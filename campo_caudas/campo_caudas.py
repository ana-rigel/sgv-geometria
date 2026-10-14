"""Campo de agitação D(x) do espaço ORIGINAL na régua de caudas (orig_raw) — exploratório, jun–jul/2026.

Não é o H-DIF-01 (congelado, régua gaussianizada). Outubro não é tocado.

Régua (definição da Ana, cascas_btc.py, espaço orig_raw), por coordenada, âncora maio/2026:
    med = mediana de maio;  esc = quantil 99,5 % de |x − med| em maio / 3;  G = (x − med) / esc   (linear)
Coordenadas brutas: E_norm e jerk de build_btc_90d_input_sgv (SGVConfig padrão, sgv_original ac6b986);
memory_flux = E_norm.ewm(alpha=0.05, adjust=False).mean().diff().

Estimadores de D (trD = traço), campo da semana k−1 avaliado nos próprios minutos da semana k:
  NW-h   Nadaraya–Watson gaussiano de banda fixa h = 0,45 (o do relatório do campo)          [referência]
  kNN-LC banda adaptativa: k = 200 vizinhos, núcleo tricúbico no raio do 200.º vizinho, constante local
  kNN-LL idem, LOCALMENTE LINEAR: s_i ≈ m + B(x_i − x0); D = covariância ponderada dos resíduos      [ajuste 1]
         × correção de amostra pequena: D / (1 − p/ESS), p = 4, ESS = (Σw)²/Σw²                     [ajuste 2]
Densidade local (para controle): log ρ ∝ −3·log(raio do k-ésimo vizinho).
Nula de pipeline: retornos, sombras, agressão e volume permutados dentro de cada dia (semente 2026),
mesmas fórmulas e a MESMA régua com âncora de maio (maio intocado).
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree

os.environ["SGV_SPACE"] = "orig"
sys.argv = ["x"]
full = open("/home/claude/rtt/real/nulls_space.py").read()
ns = {"__name__": "cc"}; exec(full.split("res = {}")[0], ns)
kl, ts, i_jun, coords = ns["kl"], ns["ts"], ns["i_jun"], ns["coords"]
K, H, P = 200, 0.45, 4
MAY = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
weeks = []
s0 = pd.Timestamp("2026-06-01", tz="UTC")
while s0 < pd.Timestamp("2026-08-01", tz="UTC"):
    e0 = min(s0 + pd.Timedelta(days=7), pd.Timestamp("2026-08-01", tz="UTC"))
    weeks.append(np.where((ts >= s0).to_numpy() & (ts < e0).to_numpy())[0]); s0 = e0
hour_d = pd.get_dummies(pd.Series(np.asarray(ts.dt.hour)), drop_first=True).astype(float).to_numpy()
BINS = [0, 1, 2, 3, 5, 10, np.inf]; BIN_NAMES = ["<1", "1–2", "2–3", "3–5", "5–10", "≥10"]


def regua(raw):
    ok = np.isfinite(raw).all(1); anc = raw[MAY & ok]
    med = np.median(anc, 0); esc = np.quantile(np.abs(anc - med), 0.995, axis=0) / 3.0
    G = np.full_like(raw, np.nan); G[ok] = (raw[ok] - med) / esc
    return G, med, esc


def campo(Xtr, Str, P0):
    """D por três estimadores e log-densidade kNN nos pontos P0, com os dados (Xtr → Str) da semana anterior."""
    tree = cKDTree(Xtr); d, idx = tree.query(P0, k=K)
    rk = np.maximum(d[:, -1], 1e-12)
    out = {"logrho": -3 * np.log(rk), "rk": rk}
    w = np.clip(1 - (d / rk[:, None]) ** 3, 0, None) ** 3                  # tricúbico
    sw = w.sum(1); ess = sw ** 2 / np.maximum((w ** 2).sum(1), 1e-300)
    Sn = Str[idx]                                                           # (n, K, 3)
    mu = np.einsum("nk,nkj->nj", w, Sn) / sw[:, None]
    out["lc"] = np.einsum("nk,nkj->n", w, (Sn - mu[:, None, :]) ** 2) / sw
    # localmente linear: regressão ponderada de s em [1, x − x0]
    Z = np.concatenate([np.ones((len(P0), K, 1)), Xtr[idx] - P0[:, None, :]], axis=2)   # (n, K, 4)
    ZtW = Z * w[:, :, None]
    A = np.einsum("nki,nkj->nij", ZtW, Z) + 1e-9 * np.eye(P)
    b = np.einsum("nki,nkj->nij", ZtW, Sn)
    beta = np.linalg.solve(A, b)                                            # (n, 4, 3)
    R = Sn - np.einsum("nki,nij->nkj", Z, beta)
    Dfull = np.einsum("nk,nki,nkj->nij", w, R, R) / sw[:, None, None]
    corr = 1.0 / np.maximum(1 - P / ess, 0.05)
    out["ll"] = np.trace(Dfull, axis1=1, axis2=2) * corr
    ev = np.linalg.eigvalsh(Dfull); out["aniso"] = ev[:, 2] / np.maximum(ev[:, 1], 1e-300)   # máx/médio
    out["degen"] = ev[:, 0] / np.maximum(ev[:, 2], 1e-300)                                  # mín/máx
    out["ess"] = ess
    # Nadaraya–Watson de banda fixa (referência), em lotes
    nw = np.zeros(len(P0))
    S2 = (Str ** 2).sum(1)
    for a in range(0, len(P0), 1500):
        Q = P0[a:a + 1500]; d2 = (Q ** 2).sum(1)[:, None] + (Xtr ** 2).sum(1)[None, :] - 2 * Q @ Xtr.T
        W = np.exp(-0.5 * np.maximum(d2, 0) / H ** 2); n = np.maximum(W.sum(1), 1e-300)
        m = (W @ Str) / n[:, None]; nw[a:a + 1500] = (W @ S2) / n - (m ** 2).sum(1)
    out["nw"] = nw
    return out


def alvos(close, high, low, vol):
    lc, hi, lo = np.log(close), np.log(high), np.log(low); n = len(lc)
    rng5 = np.full(n, np.nan)
    for t in range(n - 5): rng5[t] = hi[t + 1:t + 6].max() - lo[t + 1:t + 6].min()
    r = pd.Series(np.diff(lc, prepend=np.nan)); lv = pd.Series(np.log(vol))
    C = np.column_stack([np.ones(n)] + [np.log(r.rolling(w).std() + 1e-9) for w in (10, 30, 60)] +
                        [np.log(r.rolling(1440, min_periods=720).std() + 1e-9), np.log(r.rolling(10080, min_periods=2880).std() + 1e-9),
                         r.rolling(5).sum(), r.rolling(30).sum(), lv.rolling(10).mean(), lv.rolling(60).mean(), hour_d])
    return np.log(rng5 + 1e-9), C


def rho_parcial(x, y, C):
    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(C).all(1)
    if ok.sum() < 100: return np.nan
    xr = stats.rankdata(x[ok]); yr = stats.rankdata(y[ok]); A = C[ok]
    xr = xr - A @ np.linalg.lstsq(A, xr, rcond=None)[0]; yr = yr - A @ np.linalg.lstsq(A, yr, rcond=None)[0]
    return float(stats.spearmanr(xr, yr)[0])


def analisar(G, close, high, low, vol, label):
    y, C = alvos(close, high, low, vol)
    rec = {k: [] for k in ("idx", "ext", "nw", "lc", "ll", "llnext", "aniso", "degen", "ess", "logrho")}
    for k in range(1, len(weeks) - 1):
        tr, te, nx = weeks[k - 1], weeks[k], weeks[k + 1]
        def pares(sel):
            X = G[sel[:-1]]; S = G[sel[1:]] - G[sel[:-1]]; ok = np.isfinite(X).all(1) & np.isfinite(S).all(1); return X[ok], S[ok]
        Xp, Sp = pares(tr); Xn, Sn_ = pares(nx)
        P0 = G[te]; okp = np.isfinite(P0).all(1); idx = te[okp]; P0 = P0[okp]
        a = campo(Xp, Sp, P0); b = campo(Xn, Sn_, P0)
        rec["idx"].append(idx); rec["ext"].append(np.abs(P0).max(1))
        for c in ("nw", "lc", "ll", "aniso", "degen", "ess", "logrho"): rec[c].append(a[c])
        rec["llnext"].append(b["ll"])
    R = {k: np.concatenate(v) for k, v in rec.items()}
    out = {"label": label, "n": int(len(R["idx"])), "faixas": {}}
    for lo_, hi_, nm in zip(BINS[:-1], BINS[1:], BIN_NAMES):
        m = (R["ext"] >= lo_) & (R["ext"] < hi_)
        if m.sum() < 30:
            out["faixas"][nm] = {"n": int(m.sum())}; continue
        lnw, llc, lll = (np.log(np.maximum(R[c][m], 1e-12)) for c in ("nw", "lc", "ll"))
        f = {"n": int(m.sum()), "frac": float(m.mean()),
             "D_mediana": {"nw": float(np.exp(np.median(lnw))), "lc": float(np.exp(np.median(llc))), "ll": float(np.exp(np.median(lll)))},
             "anisotropia_max_medio_mediana": float(np.median(R["aniso"][m])), "frac_direcao_degenerada": float(np.mean(R["degen"][m] < 1e-3)), "ess_mediano": float(np.median(R["ess"][m])),
             "persistencia_logD_ll": float(stats.spearmanr(lll, np.log(np.maximum(R["llnext"][m], 1e-12)))[0])}
        i = R["idx"][m]; s5 = np.arange(len(i)) % 5 == 0
        if s5.sum() >= 100:
            Cm = np.column_stack([C[i][s5], R["logrho"][m][s5]])
            f["rho_parcial_Range5"] = {c: rho_parcial(np.log(np.maximum(R[c][m][s5], 1e-12)), y[i][s5], Cm) for c in ("nw", "ll")}
        out["faixas"][nm] = f
    print(json.dumps(out, ensure_ascii=False), flush=True)
    return out


raw = coords(kl)
G, med, esc = regua(raw)
h = hashlib.sha256(np.ascontiguousarray(np.round(raw[np.isfinite(raw).all(1)], 12)).tobytes()).hexdigest()
ok = np.isfinite(G).all(1) & ~MAY
info = {"regua": {"mediana_maio": med.tolist(), "escala": esc.tolist()}, "sha256_coord_brutas_arred12": h,
        "jun_jul": {"curtose_regua": [float(pd.Series(G[ok, j]).kurt()) for j in range(3)], "max_abs": np.abs(G[ok]).max(0).tolist(),
                    "frac_fora_cubo_2": float(np.mean(np.abs(G[ok]).max(1) > 2)), "frac_alem_3": float(np.mean(np.abs(G[ok]).max(1) > 3))}}
print(json.dumps(info, ensure_ascii=False), flush=True)
res = {"info": info, "real": analisar(G, kl.close.values, kl.high.values, kl.low.values, kl.volume.values.astype(float), "real")}
rng = np.random.default_rng(2026); day = ts.dt.floor("D").to_numpy(); r0 = np.log(kl.close.values); lr = np.diff(r0, prepend=r0[0])
hi = np.log(kl.high.values) - r0; lo = r0 - np.log(kl.low.values); perm = np.arange(len(kl))
for d_ in np.unique(day[i_jun:]):
    s = np.where(day == d_)[0]; s = s[s >= i_jun]; perm[s] = rng.permutation(s)
c2 = np.exp(r0[0] + np.cumsum(lr[perm])); h2 = c2 * np.exp(hi[perm]); l2 = c2 * np.exp(-lo[perm]); lv = np.log(kl.volume.values.astype(float))
df2 = pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": h2, "low": l2, "close": c2, "volume": np.exp(lv[perm]),
                    "taker_buy": (kl.taker_buy.values / kl.volume.values)[perm] * np.exp(lv[perm])})
G2, _, _ = regua(coords(df2))
res["pipeline"] = analisar(G2, c2, h2, l2, np.exp(lv[perm]), "pipeline")
json.dump(res, open("/home/claude/rtt/real/campo_caudas.json", "w"), indent=1, ensure_ascii=False)
