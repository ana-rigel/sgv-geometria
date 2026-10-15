"""Poder do H-FORMA-D-01 por simulação (não julga nada): reamostra 28 dias dos pares de resíduos de jun–jul, atenua o sinal e aplica a permutação dentro do dia."""
import sys, json, numpy as np, pandas as pd
sys.argv = ["x", "--periodo", "exploracao"]
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import confirmatorio_forma as CF
from scipy.stats import rankdata
P = CF.PERIODOS["exploracao"]; kl = CF.carregar(P["meses"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); wk = CF.semanas(ts, P["treino0"], P["inicio"], P["fim"])
hour_d = pd.get_dummies(pd.Series(np.asarray(ts.dt.hour)), drop_first=True).astype(float).to_numpy()
rng = np.random.default_rng(7); out = {}
for sp in ("flow", "orig"):
    raw = CF.COORDS[sp](kl); ok = np.isfinite(raw).all(1); anchor = raw[may & ok]
    G = np.full_like(raw, np.nan); g = np.isfinite(raw).all(1); G[g] = CF.gaussianize(anchor, raw[g])
    xr, yr, d = CF.analisar(G, kl, ts, wk, "real", hour_d, sp)["forma"]["pares"]
    days = np.unique(d); grp = {k: np.where(d == k)[0] for k in days}
    zx = (xr - xr.mean()) / xr.std()
    res = {}
    for shrink in (0.0, 0.4, 0.65):
        f = 1 - shrink; hits05 = hits025 = 0; R = 300
        for rep in range(R):
            pick = rng.choice(days, 28, replace=True); idx = np.concatenate([grp[k] for k in pick])
            lab = np.concatenate([[i] * len(grp[k]) for i, k in enumerate(pick)])
            x = f * zx[idx] + np.sqrt(1 - f * f) * zx[rng.permutation(len(zx))[:len(idx)]]
            rx = rankdata(x); ry = rankdata(yr[idx]); rx = (rx - rx.mean()) / rx.std(); ry = (ry - ry.mean()) / ry.std()
            obs = (rx * ry).mean(); gi = [np.where(lab == i)[0] for i in range(28)]
            cnt = 0
            for b in range(500):
                yp = ry.copy()
                for gg in gi: yp[gg] = ry[gg][rng.permutation(len(gg))]
                cnt += (rx * yp).mean() >= obs
            p = (cnt + 1) / 501; hits05 += p <= .05; hits025 += p <= .025
        res[f"encolhe_{int(shrink * 100)}"] = {"poder_p<=0,025": round(hits025 / R, 2), "poder_p<=0,05": round(hits05 / R, 2)}
        print(sp, shrink, res[f"encolhe_{int(shrink * 100)}"], flush=True)
    out[sp] = res
json.dump(out, open(CF.ROOT / "referencia" / "H-FORMA-D-01_poder.json", "w"), indent=1, ensure_ascii=False)
