"""Julgamento dos portões G1–G5 do RB-01 a partir de resultados/rb01/rb01_F*.json (regras da seção 6 do protocolo)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from regua.rb01 import FAMILIES
from regua.run_rb01 import CANDS

DIR = Path(__file__).resolve().parents[1] / "resultados" / "rb01"


def feat(wa, wb):
    d50 = wb["50"]["logV"] - wa["50"]["logV"]
    d95 = wb["95"]["logV"] - wa["95"]["logV"]
    return {"d50": d50, "d95": d95, "f": (d95 - d50) / 3}


def icc(groups):
    """ICC(1) de ANOVA a um fator, desbalanceado (grupos com >= 2 reajustes)."""
    groups = [np.asarray(g, float) for g in groups if len(g) >= 2]
    if len(groups) < 3:
        return float("nan")
    n = np.array([len(g) for g in groups]); N, a = n.sum(), len(groups)
    grand = np.concatenate(groups).mean()
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
    msb, msw = ssb / (a - 1), ssw / (N - a)
    k0 = (N - (n ** 2).sum() / N) / (a - 1)
    return float((msb - msw) / (msb + (k0 - 1) * msw))


def auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    if not len(pos) or not len(neg):
        return float("nan")
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def judge_family(res, c):
    tr = res["truth"]
    windows, pairs = [], []
    for p in res["pairs"]:
        wa, wb = p["cand"][c]["A"], p["cand"][c]["B"]
        windows += [wa, wb]
        if wa["ok"] and wb["ok"]:
            ft = feat(tr["A"], tr[p["case"]])
            pairs.append({"case": p["case"], **feat(wa, wb), "f_true": ft["f"]})
    ok = [w for w in windows if w["ok"]]
    inval = 1 - len(ok) / len(windows)
    g = {"invalidas": inval, "motivos": sorted({w["motivo"].split(":")[0] for w in windows if not w["ok"]})}
    for a, key in ((0.50, "50"), (0.95, "95")):
        ei = np.abs([w[key]["mass_int"] - a for w in ok]) if ok else np.array([np.nan])
        et = np.abs([w[key]["mass_true"] - a for w in ok]) if ok else np.array([np.nan])
        g[f"int{key}_med"], g[f"int{key}_p95"] = float(np.median(ei)), float(np.quantile(ei, .95))
        g[f"true{key}_med"] = float(np.median(et))
        g[f"true{key}_vies"] = float(np.median([w[key]["mass_true"] - a for w in ok])) if ok else float("nan")
    # G4
    grp = {}
    for r in res["refits"]:
        wa, wb = r["cand"][c]["A"], r["cand"][c]["B"]
        if wa["ok"] and wb["ok"]:
            grp.setdefault(r["case"], []).append(feat(wa, wb))
    for k in ("d50", "d95", "f"):
        g[f"icc_{k}"] = icc([[x[k] for x in v] for v in grp.values()])
    # G5
    if len(pairs) >= 10:
        g["rho_f"] = float(spearmanr([p["f"] for p in pairs], [p["f_true"] for p in pairs])[0])
    else:
        g["rho_f"] = float("nan")
    g["auc_caudas_vs_exp"] = auc([p["f"] for p in pairs if p["case"] in ("caudas10", "caudas20")],
                                 [p["f"] for p in pairs if p["case"] == "expansao"])
    gates = {
        "G1": g["int50_med"] <= .005 and g["int50_p95"] <= .01 and g["int95_med"] <= .005 and g["int95_p95"] <= .01,
        "G2": inval <= .02,
        "G3": g["true50_med"] <= .02 and g["true95_med"] <= .01,
        "G4": all(g[f"icc_{k}"] >= .80 for k in ("d50", "d95", "f")),
        "G5": g["rho_f"] >= .80 and g["auc_caudas_vs_exp"] >= .90,
    }
    return g, gates


def main():
    res = {f: json.loads((DIR / f"rb01_{f}.json").read_text()) for f in FAMILIES if (DIR / f"rb01_{f}.json").exists()}
    out = {"familias": list(res), "candidatos": {}}
    for c in CANDS:
        fams = {f: dict(zip(("medidas", "portoes"), judge_family(r, c))) for f, r in res.items()}
        aprovado = len(fams) == 6 and all(all(v["portoes"].values()) for v in fams.values())
        score = sum(v["medidas"]["true95_med"] for v in fams.values())
        out["candidatos"][c] = {"aprovado": aprovado, "soma_true95_med": score, "familias": fams}
    aprov = [c for c in CANDS if out["candidatos"][c]["aprovado"]]
    out["escolhido"] = min(aprov, key=lambda c: out["candidatos"][c]["soma_true95_med"]) if aprov else None
    # secundário: invalidez do candidato A na régua flow_raw; verdade da feature por caso
    out["flow_raw_A_invalidas"] = {f: float(np.mean([v is not None for p in r["pairs"] for v in p["flow_A_invalid"].values()]))
                                   for f, r in res.items()}
    out["f_verdadeira"] = {f: {k: feat(r["truth"]["A"], r["truth"][k])["f"] for k in r["truth"] if k != "A"}
                           for f, r in res.items()}
    (DIR / "julgamento_rb01.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for c in CANDS:
        print(f"== {c}  aprovado={out['candidatos'][c]['aprovado']}")
        for f, v in out["candidatos"][c]["familias"].items():
            m, gt = v["medidas"], v["portoes"]
            print(f"  {f} {''.join('✓' if gt[k] else '✗' for k in ('G1','G2','G3','G4','G5'))} inval={m['invalidas']:.3f} "
                  f"int={m['int50_med']:.4f}/{m['int95_med']:.4f} true={m['true50_med']:.4f}/{m['true95_med']:.4f} "
                  f"vies={m['true50_vies']:+.3f}/{m['true95_vies']:+.4f} icc={m['icc_d50']:.2f}/{m['icc_d95']:.2f}/{m['icc_f']:.2f} "
                  f"rho={m['rho_f']:.2f} auc={m['auc_caudas_vs_exp']:.2f} {m['motivos']}")
    print("escolhido:", out["escolhido"])
    print("flow_raw A inválidas:", out["flow_raw_A_invalidas"])


if __name__ == "__main__":
    main()
