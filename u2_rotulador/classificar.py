"""SGV-U2 — classifica o mecanismo com três painéis (M11-I, convencional, combinado) + sensibilidade (M11-I com ΔD contínuo).

    python u2_rotulador/classificar.py

Validação deixando uma família inteira de fora; floresta aleatória (principal) e logística multinomial (segunda).
IC 95% por bootstrap das réplicas (família, rep), 2.000 reamostras. Saída: resultados/U2_resultado.json e .md
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
CLASSES = ["nenhum", "translacao", "escala", "rotacao", "bimodal", "curvatura", "caudas"]
df = pd.read_csv(ROOT / "resultados" / "variaveis.csv")

# --- variáveis M11-I (como registrado): θ nulo → 0 + indicador; inválida → 0 + indicador
m = pd.DataFrame(index=df.index)
valid = df.m_valid.astype(str).str.lower().eq("true")
m["m_invalida"] = (~valid).astype(float)
m["m_theta_nao_ident"] = df.m_theta_deg.isna().astype(float)
for k in ("translation_norm", "delta_log_volume", "theta_deg", "distance_512"):
    m["m_" + k] = df["m_" + k].fillna(0.0).where(valid, 0.0)
m["m_dD_bin"] = (df.m_delta_D.fillna(0.0) > 0.01).astype(float).where(valid, 0.0)
m_cont = m.drop(columns="m_dD_bin").assign(m_delta_D=df.m_delta_D.fillna(0.0).where(valid, 0.0))
c = df[[col for col in df.columns if col.startswith("c_")]]
PAINEIS = {"M11-I": m, "convencional": c, "combinado": pd.concat([m, c], axis=1), "M11-I (ΔD contínuo)": m_cont}
y = df.classe.to_numpy(); fam = df.familia.to_numpy(); unid = (df.familia + "_" + df.rep.astype(str)).to_numpy()


def modelos():
    return {"floresta": RandomForestClassifier(n_estimators=500, random_state=0, n_jobs=2),
            "logistica": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, C=1.0))}


pred = {}
for mod in ("floresta", "logistica"):
    for nome, X in PAINEIS.items():
        p = np.empty(len(y), dtype=object)
        for f in np.unique(fam):
            te = fam == f; clf = modelos()[mod].fit(X[~te], y[~te]); p[te] = clf.predict(X[te])
        pred[(mod, nome)] = p


def recalls(yt, yp):
    return np.array([np.mean(yp[yt == k] == k) for k in CLASSES])


rng = np.random.default_rng(0); unidades = np.unique(unid); grupos = {u: np.where(unid == u)[0] for u in unidades}
res = {"n": int(len(y)), "taxa_invalidas_m11": {k: float(1 - valid[y == k].mean()) for k in CLASSES},
       "theta_nao_identificavel": {k: float(df.m_theta_deg[y == k].isna().mean()) for k in CLASSES}, "modelos": {}}
B = 2000; boot_idx = [np.concatenate([grupos[u] for u in rng.choice(unidades, len(unidades))]) for _ in range(B)]
linhas_md = []
for mod in ("floresta", "logistica"):
    R = {}
    for nome in PAINEIS:
        yp = pred[(mod, nome)]
        R[nome] = {"recall": dict(zip(CLASSES, recalls(y, yp).round(4).tolist())), "f1_macro": float(f1_score(y, yp, average="macro")),
                   "acuracia": float(np.mean(yp == y)), "confusao": confusion_matrix(y, yp, labels=CLASSES).tolist(),
                   "por_familia_testada": {f: float(np.mean(yp[fam == f] == y[fam == f])) for f in np.unique(fam)}}
    # diferenças M11-I − convencional e combinado − convencional, com IC
    for a_, b_ in (("M11-I", "convencional"), ("combinado", "convencional"), ("M11-I (ΔD contínuo)", "convencional")):
        ya, yb = pred[(mod, a_)], pred[(mod, b_)]
        d = np.array([recalls(y[ix], ya[ix]) - recalls(y[ix], yb[ix]) for ix in boot_idx])
        df1 = np.array([f1_score(y[ix], ya[ix], average="macro") - f1_score(y[ix], yb[ix], average="macro") for ix in boot_idx])
        obs = recalls(y, ya) - recalls(y, yb)
        R[f"{a_} − {b_}"] = {"recall": {k: {"dif": round(float(obs[i]), 4), "ic95": [round(float(q), 4) for q in np.quantile(d[:, i], [0.025, 0.975])]} for i, k in enumerate(CLASSES)},
                              "f1_macro": {"dif": round(R[a_]["f1_macro"] - R[b_]["f1_macro"], 4), "ic95": [round(float(q), 4) for q in np.quantile(df1, [0.025, 0.975])]}}
    res["modelos"][mod] = R
    linhas_md.append(f"\n### {mod}\n\n| Classe | M11-I | convencional | combinado | M11-I − conv (IC 95%) |\n|---|---|---|---|---|")
    for i, k in enumerate(CLASSES):
        dd = R["M11-I − convencional"]["recall"][k]
        linhas_md.append(f"| {k} | {R['M11-I']['recall'][k]:.2f} | {R['convencional']['recall'][k]:.2f} | {R['combinado']['recall'][k]:.2f} | {dd['dif']:+.2f} ({dd['ic95'][0]:+.2f}; {dd['ic95'][1]:+.2f}) |")
    f = R["M11-I − convencional"]["f1_macro"]; g = R["combinado − convencional"]["f1_macro"]
    linhas_md.append(f"| **F1 macro** | {R['M11-I']['f1_macro']:.3f} | {R['convencional']['f1_macro']:.3f} | {R['combinado']['f1_macro']:.3f} | {f['dif']:+.3f} ({f['ic95'][0]:+.3f}; {f['ic95'][1]:+.3f}) |")
    linhas_md.append(f"\nCombinado − convencional, F1 macro: {g['dif']:+.3f} ({g['ic95'][0]:+.3f}; {g['ic95'][1]:+.3f}). "
                     f"M11-I com ΔD contínuo: F1 {R['M11-I (ΔD contínuo)']['f1_macro']:.3f}.")
    for nome in ("M11-I", "convencional"):
        linhas_md.append(f"\nConfusão {nome} (linhas = verdade, colunas = previsto, ordem {', '.join(CLASSES)}):\n\n```\n" +
                         "\n".join(f"{k:11s} " + " ".join(f"{v:3d}" for v in row) for k, row in zip(CLASSES, R[nome]["confusao"])) + "\n```")
json.dump(res, open(ROOT / "resultados" / "U2_resultado.json", "w"), indent=1, ensure_ascii=False)
txt = "\n".join(linhas_md); (ROOT / "resultados" / "U2_tabelas.md").write_text(txt); print(txt)
print("\ninválidas M11:", res["taxa_invalidas_m11"]); print("θ não identificável:", res["theta_nao_identificavel"])
