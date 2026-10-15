import sys, numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, "/home/claude/sgv-geometria/pipeline"); sys.path.insert(0, "/home/claude/nav_mercado/x/navegador_sgv/u03")
import confirmatorio_cauda as cc, u031_casca
from u031_casca import build_shell, hdr_mesh
u031_casca.OUTER_EXTENT = 10.0; u031_casca.OUTER_GRID = 61
kl = cc.carregar("BTCUSDT", ["2026-05", "2026-06", "2026-07"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); G, _, _ = cc.regua(cc.coords(kl), may)
lr = np.diff(np.log(kl.close.values.astype(float)), prepend=np.nan); i0 = int(np.argmax(~may)); W = 1500; N = len(G)
def mapa(s, seed=20261009):
    X = G[s:s + W]; r = np.abs(lr[s:s + W])
    m = {"q": np.quantile(r, .999) / np.median(r)}
    try:
        inner = build_shell(X, seed=seed, n=25); outer, _ = hdr_mesh(inner.params, .95)
        m.update(v50=abs(inner.mesh.volume), v95=abs(outer.volume))
    except Exception as e: m["erro"] = str(e)[:40]
    return m
starts = [i0 + k * 28 * 60 for k in range(200) if i0 + k * 28 * 60 + W <= N]
M = [mapa(s) for s in starts]; print("janelas", len(M), "válidas", sum("v50" in m for m in M))
F, R, F95, F50 = [], [], [], []
for a, b in zip(M[0::2], M[1::2]):
    if "v50" in a and "v50" in b:
        f50 = np.log(b["v50"] / a["v50"]) / 3; f95 = np.log(b["v95"] / a["v95"]) / 3
        F.append(f95 - f50); F95.append(f95); F50.append(f50); R.append(np.log(b["q"] / a["q"]))
print("pares", len(F), "ρ caudas", round(spearmanr(F, R)[0], 3), "ρ só v95", round(spearmanr(F95, R)[0], 3), "ρ só v50", round(spearmanr(F50, R)[0], 3))
# confiabilidade da feature: 5 sementes
rel = []
for a_s, b_s in list(zip(starts[0::2], starts[1::2]))[:10]:
    v = []
    for sd in range(5):
        a, b = mapa(a_s, 20261009 + sd), mapa(b_s, 20261009 + sd)
        if "v50" in a and "v50" in b: v.append(np.log(b["v95"] / a["v95"]) / 3 - np.log(b["v50"] / a["v50"]) / 3)
    rel.append(v)
w = np.mean([np.var(v) for v in rel if len(v) > 1]); tot = np.var(F); print("var entre sementes", round(w, 5), "var total", round(tot, 5), "confiabilidade", round(1 - w / tot, 3))
