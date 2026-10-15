"""RB-01, análise PÓS-HOC (escrita depois de ver F0–F3; não muda o veredito dos portões).

Motivo: o G5 registrado exige Spearman(f̂, f) >= 0,80, mas 5 dos 8 casos têm f verdadeira = 0
(transformações afins não mudam a razão V95/V50). Com esses empates o teto do ρ é ~0,87 mesmo
com estimativa perfeita. Aqui se reportam medidas sem esse defeito, marcadas como pós-hoc:
  - teto do ρ dado o desenho e ρ/teto;
  - viés e dispersão de f̂ nos pares nulos (leitura espúria de caudas);
  - AUC caudas5% contra nulo (menor dose detectável) e ρ só nos três níveis de caudas.
"""
from __future__ import annotations

import json

import numpy as np
from scipy.stats import rankdata, spearmanr

from regua.analise_rb01 import DIR, auc, feat
from regua.rb01 import FAMILIES
from regua.run_rb01 import CANDS


def rho_teto(f_true):
    r_true = rankdata(f_true)
    return float(np.corrcoef(r_true, np.arange(1, len(f_true) + 1)[np.argsort(np.argsort(f_true, kind="stable"))])[0, 1])


def main():
    out = {}
    for fam in FAMILIES:
        p = DIR / f"rb01_{fam}.json"
        if not p.exists():
            continue
        r = json.loads(p.read_text())
        tr = r["truth"]
        out[fam] = {}
        for c in CANDS:
            rows = []
            for x in r["pairs"]:
                a, b = x["cand"][c]["A"], x["cand"][c]["B"]
                if a["ok"] and b["ok"]:
                    # afins: f teórica = 0 exato (o valor de Monte Carlo ~±0,005 é só ruído da verdade)
                    ftv = 0.0 if not x["case"].startswith("caudas") else feat(tr["A"], tr[x["case"]])["f"]
                    rows.append({"case": x["case"], "f": feat(a, b)["f"], "f_true": ftv})
            if len(rows) < 10:
                out[fam][c] = None
                continue
            ft = np.array([q["f_true"] for q in rows]); fh = np.array([q["f"] for q in rows])
            teto = rho_teto(ft)
            rho = float(spearmanr(fh, ft)[0])
            nul = [q["f"] for q in rows if q["case"] == "nulo"]
            c5 = [q["f"] for q in rows if q["case"] == "caudas05"]
            tails = [q for q in rows if q["case"].startswith("caudas")]
            rho_t = float(spearmanr([q["f"] for q in tails], [q["f_true"] for q in tails])[0]) if len(tails) > 5 else float("nan")
            out[fam][c] = {"rho": rho, "teto": teto, "rho_sobre_teto": rho / teto,
                           "nulo_media": float(np.mean(nul)) if nul else float("nan"),
                           "nulo_sd": float(np.std(nul, ddof=1)) if len(nul) > 1 else float("nan"),
                           "f_verdadeira_caudas05": float(feat(tr["A"], tr["caudas05"])["f"]),
                           "auc_caudas05_vs_nulo": auc(c5, nul), "rho_so_caudas": rho_t}
    (DIR / "posthoc_rb01.json").write_text(json.dumps(out, indent=1))
    for fam, v in out.items():
        print("==", fam)
        for c, m in v.items():
            if m is None:
                print(f"  {c}: poucos pares válidos"); continue
            print(f"  {c}: ρ={m['rho']:.2f} teto={m['teto']:.2f} ρ/teto={m['rho_sobre_teto']:.2f} | nulo f̂={m['nulo_media']:+.3f}±{m['nulo_sd']:.3f} "
                  f"(f caudas5%={m['f_verdadeira_caudas05']:.3f}) | AUC 5%×nulo={m['auc_caudas05_vs_nulo']:.2f} | ρ só caudas={m['rho_so_caudas']:.2f}")


if __name__ == "__main__":
    main()
