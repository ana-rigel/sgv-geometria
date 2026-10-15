"""Exploração (BTC jun–jul): reconstrói a validação da feature de caudas das cascas contra a cauda real dos retornos.
Reproduz o desenho do pacote (cascas_btc.py orig_raw + mercado_classes.py) e mede Δlog(q99,9/mediana de |r|), cujo script não veio.
"""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

REPO = Path("/home/claude/sgv-geometria"); PKG = Path("/home/claude/nav_mercado/x/navegador_sgv")
sys.path.insert(0, str(REPO / "pipeline")); sys.path.insert(0, str(PKG / "u03"))
import confirmatorio_cauda as cc                      # carregar, coords, regua (mesmas definições)
import u031_casca
from u031_casca import build_shell, hdr_mesh
u031_casca.OUTER_EXTENT = 10.0; u031_casca.OUTER_GRID = 61
OUT = Path("/home/claude/rtt/real/out_cascas"); OUT.mkdir(exist_ok=True)

kl = cc.carregar("BTCUSDT", ["2026-05", "2026-06", "2026-07"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
raw = cc.coords(kl); G, med, esc = cc.regua(raw, may)
lr = np.diff(np.log(kl.close.values.astype(float)), prepend=np.nan)
i_jun = int(np.argmax(~may)); N = len(G); W, SNAP = 1500, 240
recs = []; t0 = time.time()
for k, s in enumerate(range(i_jun, N, SNAP)):
    X = G[s - W:s]; X = X[np.isfinite(X).all(1)]; r = np.abs(lr[s - W:s]); r = r[np.isfinite(r)]
    z = (X - X.mean(0)) / X.std(0)
    rec = {"k": k, "t": s, "time": str(ts.iloc[s - 1])[:16], "valid": False,
           "kurt": ((z ** 4).mean(0) - 3).tolist(), "q999": float(np.quantile(r, .999)), "q99": float(np.quantile(r, .99)),
           "med": float(np.median(r)), "max": float(r.max())}
    try:
        if len(X) < 0.95 * W: raise ValueError("janela incompleta")
        inner = build_shell(X, seed=20261009, n=25)
        outer, cov = hdr_mesh(inner.params, .95)
        rec.update(valid=True, v50=float(abs(inner.mesh.volume)), v95=float(abs(outer.volume)))
    except Exception as e:
        rec["reason"] = str(e)[:60]
    recs.append(rec)
    if k % 60 == 0: print(f"[{time.time()-t0:4.0f}s] {k} {rec['time']} {rec['valid']}", flush=True)
json.dump(recs, open(OUT / "mapas_btc.json", "w"))
S = [r for r in recs if r["valid"]]; print("válidos", len(S), "/", len(recs))

def feat(a, b): return np.log(b["v95"] / a["v95"]) / 3 - np.log(b["v50"] / a["v50"]) / 3
def ref(a, b, q="q999"): return np.log((b[q] / b["med"]) / (a[q] / a["med"]))
byk = {r["k"]: i for i, r in enumerate(S)}
adj = [(byk[k], byk[k + 7]) for k in byk if k + 7 in byk]
rng = np.random.default_rng(3); far = []
while len(far) < 400:
    i, j = sorted(rng.choice(len(S), 2, replace=False))
    if S[j]["k"] - S[i]["k"] >= 18: far.append((i, j))
for nome, P in [("lag7", adj), ("nulo", far), ("todos (como no pacote)", adj + far)]:
    f = [feat(S[i], S[j]) for i, j in P]
    dk = [np.log((S[j]["kurt"][0] + 3) / (S[i]["kurt"][0] + 3)) for i, j in P]
    print(f"{nome:24s} n={len(P):3d}  ρ(caudas, Δlog curt E) {spearmanr(f, dk)[0]:+.3f}  "
          f"ρ(caudas, Δlog q99,9/med) {spearmanr(f, [ref(S[i], S[j]) for i, j in P])[0]:+.3f}  "
          f"q99/med {spearmanr(f, [ref(S[i], S[j], 'q99') for i, j in P])[0]:+.3f}  "
          f"max {spearmanr(f, [np.log(S[j]['max'] / S[i]['max']) for i, j in P])[0]:+.3f}")
