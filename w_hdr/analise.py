"""W-HDR — análise das partes A (detecção, dose-resposta) e B (rótulo do mecanismo). Saídas em resultados/."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

ROOT = Path(__file__).resolve().parent; R = ROOT / "resultados"
CLASSES = ["nenhum", "translacao", "escala", "rotacao", "bimodal", "curvatura", "caudas"]
out = {}

# ------------------------------------------------------------------ A
A = pd.read_csv(R / "parteA.csv")
MED = {"M11-I distância": "m11_dist", "M11-I |ΔD|": "m11_absdD", "W₂ completo": "w_w2", "W₂-HDR": "w_w2hdr", "MMD²": "mmd2"}
nul = A[A.classe == "nulo"]; cal = nul[nul.rep % 2 == 0]; chk = nul[nul.rep % 2 == 1]
limiar = {n: float(np.nanquantile(cal[c], 0.95)) for n, c in MED.items()}
out["A"] = {"limiar_q95": limiar, "falso_alarme_conferencia": {n: float((chk[c].fillna(-np.inf) > limiar[n]).mean()) for n, c in MED.items()},
            "m11_invalida": {k: float(1 - A[A.classe == k].m11_valida.astype(bool).mean()) for k in A.classe.unique()}, "deteccao": {}}
alt = A[A.classe != "nulo"]
for mec in alt.classe.unique():
    for k in sorted(alt.k.unique()):
        d = alt[(alt.classe == mec) & (alt.k == k)]
        out["A"]["deteccao"][f"{mec}|{k:.2f}"] = {n: float((d[c].fillna(-np.inf) > limiar[n]).mean()) for n, c in MED.items()}
linhas = ["## Parte A — taxa de detecção (limiar q95 dos nulos de calibração; 30 alternativas por célula)\n",
          "| Mecanismo | k | " + " | ".join(MED) + " |", "|---|---|" + "---|" * len(MED)]
for key, v in out["A"]["deteccao"].items():
    mec, k = key.split("|"); linhas.append(f"| {mec} | {k} | " + " | ".join(f"{v[n]:.2f}" for n in MED) + " |")
linhas.append("\nFalso alarme nos nulos de conferência: " + ", ".join(f"{n} {v:.0%}" for n, v in out["A"]["falso_alarme_conferencia"].items()))
linhas.append("Invalidez do M11-I: " + ", ".join(f"{k} {v:.0%}" for k, v in out["A"]["m11_invalida"].items()))

# ------------------------------------------------------------------ B
u2 = pd.read_csv(ROOT.parent / "u2_rotulador" / "resultados" / "variaveis.csv")
w = pd.read_csv(R / "parteB_w.csv"); df = u2.merge(w, on=["familia", "rep", "classe"]); assert len(df) == 630
valid = df.m_valid.astype(str).str.lower().eq("true")
m = pd.DataFrame({"m_invalida": (~valid).astype(float), "m_theta_nao_ident": df.m_theta_deg.isna().astype(float)})
for k in ("translation_norm", "delta_log_volume", "theta_deg", "distance_512"):
    m["m_" + k] = df["m_" + k].fillna(0.0).where(valid, 0.0)
m["m_dD_bin"] = (df.m_delta_D.fillna(0.0) > 0.01).astype(float).where(valid, 0.0)
c = df[[x for x in df.columns if x.startswith("c_")]]; wv = df[["w_w2", "w_media", "w_bures", "w_forma", "w_w2hdr"]]
P = {"M11-I": m, "W": wv, "convencional": c, "convencional + W": pd.concat([c, wv], axis=1), "M11-I + W": pd.concat([m, wv], axis=1)}
y = df.classe.to_numpy(); fam = df.familia.to_numpy(); unid = (df.familia + "_" + df.rep.astype(str)).to_numpy()
pred = {}
for nome, X in P.items():
    p = np.empty(len(y), dtype=object)
    for f in np.unique(fam):
        te = fam == f; p[te] = RandomForestClassifier(n_estimators=500, random_state=0, n_jobs=2).fit(X[~te], y[~te]).predict(X[te])
    pred[nome] = p
rec = lambda yt, yp: np.array([np.mean(yp[yt == k] == k) for k in CLASSES])  # noqa: E731
rng = np.random.default_rng(0); us = np.unique(unid); g = {u: np.where(unid == u)[0] for u in us}
boot = [np.concatenate([g[u] for u in rng.choice(us, len(us))]) for _ in range(2000)]
out["B"] = {n: {"recall": dict(zip(CLASSES, rec(y, p).round(3).tolist())), "f1_macro": float(f1_score(y, p, average="macro"))} for n, p in pred.items()}
for a_, b_ in (("W", "M11-I"), ("W", "convencional"), ("convencional + W", "convencional"), ("M11-I + W", "W")):
    d = np.array([f1_score(y[i], pred[a_][i], average="macro") - f1_score(y[i], pred[b_][i], average="macro") for i in boot])
    dr = np.array([rec(y[i], pred[a_][i]) - rec(y[i], pred[b_][i]) for i in boot]); obs = rec(y, pred[a_]) - rec(y, pred[b_])
    out["B"][f"{a_} − {b_}"] = {"f1": round(out["B"][a_]["f1_macro"] - out["B"][b_]["f1_macro"], 4), "ic95": np.quantile(d, [0.025, 0.975]).round(4).tolist(),
                               "recall": {k: [round(float(obs[j]), 3)] + np.quantile(dr[:, j], [0.025, 0.975]).round(3).tolist() for j, k in enumerate(CLASSES)}}
linhas += ["\n## Parte B — rótulo do mecanismo (floresta, deixa uma família de fora; 630 comparações do U2)\n",
           "| Classe | " + " | ".join(P) + " |", "|---|" + "---|" * len(P)]
for k in CLASSES:
    linhas.append(f"| {k} | " + " | ".join(f"{out['B'][n]['recall'][k]:.2f}" for n in P) + " |")
linhas.append("| **F1 macro** | " + " | ".join(f"{out['B'][n]['f1_macro']:.3f}" for n in P) + " |")
for k in ("W − M11-I", "W − convencional", "convencional + W − convencional", "M11-I + W − W"):
    x = out["B"][k]; linhas.append(f"\n{k}: F1 {x['f1']:+.3f} (IC {x['ic95'][0]:+.3f}; {x['ic95'][1]:+.3f}); recall bimodal {x['recall']['bimodal']}, curvatura {x['recall']['curvatura']}, caudas {x['recall']['caudas']}")
json.dump(out, open(R / "W-HDR.json", "w"), indent=1, ensure_ascii=False)
txt = "\n".join(linhas); (R / "W-HDR_tabelas.md").write_text(txt); print(txt)
