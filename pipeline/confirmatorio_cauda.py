"""H-CAUDA-01 — campo de agitação nos extremos (régua de caudas) antecipa a amplitude. Código congelado.

    python pipeline/confirmatorio_cauda.py --paridade-btc          # BTC jun–jul, deve dar ≈ +0,125
    python pipeline/confirmatorio_cauda.py --simbolo XRPUSDT       # julgamento: XRP jun–set/2026

Definições em PREREGISTRO_H-CAUDA-01.md.
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "sgv_original"))
from sgv.config import SGVConfig  # noqa: E402
from sgv.input_builder import build_btc_90d_input_sgv  # noqa: E402

K, P, B_PERM, SEED_PERM, SEED_NULL = 200, 4, 5000, 20261014, 2026
BAND = (3.0, 5.0)
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trades", "taker_buy", "taker_buy_quote", "ignore"]


def sha_esperado(nome):
    chk = ROOT / "dados" / (nome + ".CHECKSUM")
    if chk.exists():
        return chk.read_text().split()[0]
    for linha in (ROOT / "dados" / "SHA256SUMS").read_text().splitlines():
        if linha.strip() and linha.split()[1].lstrip("*") == nome:
            return linha.split()[0]
    sys.exit(f"Sem SHA-256 publicado para {nome}")


def carregar(simbolo, meses):
    partes = []
    for m in meses:
        nome = f"{simbolo}-1m-{m}.zip"; caminho = ROOT / "dados" / nome
        if not caminho.exists():
            sys.exit(f"Falta dados/{nome}")
        if hashlib.sha256(caminho.read_bytes()).hexdigest() != sha_esperado(nome):
            sys.exit(f"SHA-256 não confere: {nome}")
        with zipfile.ZipFile(caminho) as z:
            df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS)
        if not str(df.open_time.iloc[0]).isdigit():
            df = df.iloc[1:].astype({c: float for c in COLS[1:6]}).astype({"open_time": "int64"})
        if df.open_time.iloc[0] > 1e14:
            df["open_time"] //= 1000
        partes.append(df); print(f"{nome}: SHA-256 conferido", flush=True)
    df = pd.concat(partes, ignore_index=True)
    df["timestamp"] = df.open_time.astype("int64")
    if (np.diff(df.timestamp.values) != 60000).any():
        sys.exit("Série com buracos ou duplicatas")
    return df[["timestamp", "open", "high", "low", "close", "volume"]].reset_index(drop=True)


def coords(df):
    raw = pd.DataFrame({"timestamp": df["timestamp"].to_numpy(),
                        "datetime": pd.to_datetime(df["timestamp"], unit="ms", utc=True).astype(str).to_numpy()})
    for c in ("open", "high", "low", "close", "volume"):
        raw[c] = pd.to_numeric(df[c]).to_numpy()
    inp = build_btc_90d_input_sgv(raw, SGVConfig()); assert len(inp) == len(df)
    e = inp["E_norm"]; mf = e.ewm(alpha=0.05, adjust=False).mean().diff()
    return np.column_stack((e.to_numpy(), inp["jerk"].to_numpy(), mf.to_numpy()))


def regua(raw, may):
    ok = np.isfinite(raw).all(1); anc = raw[may & ok]
    med = np.median(anc, 0); esc = np.quantile(np.abs(anc - med), 0.995, axis=0) / 3.0
    G = np.full_like(raw, np.nan); G[ok] = (raw[ok] - med) / esc
    return G, med, esc


def campo_ll(Xtr, Str, P0):
    d, idx = cKDTree(Xtr).query(P0, k=K)
    rk = np.maximum(d[:, -1], 1e-12)
    w = np.clip(1 - (d / rk[:, None]) ** 3, 0, None) ** 3
    sw = w.sum(1); ess = sw ** 2 / np.maximum((w ** 2).sum(1), 1e-300)
    Z = np.concatenate([np.ones((len(P0), K, 1)), Xtr[idx] - P0[:, None, :]], axis=2)
    ZtW = Z * w[:, :, None]
    beta = np.linalg.solve(np.einsum("nki,nkj->nij", ZtW, Z) + 1e-9 * np.eye(P), np.einsum("nki,nkj->nij", ZtW, Str[idx]))
    R = Str[idx] - np.einsum("nki,nij->nkj", Z, beta)
    D = np.einsum("nk,nkj->n", w, R ** 2) / sw / np.maximum(1 - P / ess, 0.05)
    return np.log(np.maximum(D, 1e-12)), -3 * np.log(rk)


def semanas(ts, inicio, fim, min_dias=5):
    out = []; s = pd.Timestamp(inicio, tz="UTC"); fim = pd.Timestamp(fim, tz="UTC")
    while s < fim:
        e = min(s + pd.Timedelta(days=7), fim)
        if e - s >= pd.Timedelta(days=min_dias) or min_dias == 0:
            out.append(np.where((ts >= s).to_numpy() & (ts < e).to_numpy())[0])
        s = e
    return out


def janelas(G, kl, ts, wk, julgadas):
    close, high, low, vol = (kl[c].values.astype(float) for c in ("close", "high", "low", "volume"))
    lc, hi, lo = np.log(close), np.log(high), np.log(low); n = len(lc)
    y = np.full(n, np.nan)
    for t in range(n - 5): y[t] = np.log(hi[t + 1:t + 6].max() - lo[t + 1:t + 6].min() + 1e-12)
    r = pd.Series(np.diff(lc, prepend=np.nan)); lv = pd.Series(np.log(vol))
    hour = pd.get_dummies(pd.Series(np.asarray(ts.dt.hour)), drop_first=True).astype(float).to_numpy()
    C = np.column_stack([np.ones(n)] + [np.log(r.rolling(w).std() + 1e-9) for w in (10, 30, 60)] +
                        [np.log(r.rolling(1440, min_periods=720).std() + 1e-9), np.log(r.rolling(10080, min_periods=2880).std() + 1e-9),
                         r.rolling(5).sum(), r.rolling(30).sum(), lv.rolling(10).mean(), lv.rolling(60).mean(), hour])
    I, LD, LR, IA = [], [], [], []
    for k in julgadas:
        tr, te = wk[k - 1], wk[k]
        X = G[tr[:-1]]; S = G[tr[1:]] - G[tr[:-1]]; ok = np.isfinite(X).all(1) & np.isfinite(S).all(1)
        P0 = G[te]; okp = np.isfinite(P0).all(1); idx = te[okp]; P0 = P0[okp]
        ext = np.abs(P0).max(1); m = (ext >= BAND[0]) & (ext < BAND[1])
        if not m.any(): continue
        ld, lr = campo_ll(X[ok], S[ok], P0[m]); I.append(idx[m]); LD.append(ld); LR.append(lr)
    I, LD, LR = map(np.concatenate, (I, LD, LR))
    blk = kl.timestamp.values[I] // 300_000; first = np.r_[True, blk[1:] != blk[:-1]]
    def montar(sel):
        i = I[sel]; Cm = np.column_stack([C[i], LR[sel]]); yy = y[i]; ok = np.isfinite(yy) & np.isfinite(Cm).all(1)
        xr = stats.rankdata(LD[sel][ok]); yr = stats.rankdata(yy[ok]); A = Cm[ok]
        xr = xr - A @ np.linalg.lstsq(A, xr, rcond=None)[0]; yr = yr - A @ np.linalg.lstsq(A, yr, rcond=None)[0]
        return xr, yr, i[ok]
    return montar(first), montar(np.ones(len(I), bool)), int(len(I))


def p_perm(xr, yr, dias, rng):
    obs = stats.spearmanr(xr, yr)[0]; grupos = [np.where(dias == d)[0] for d in np.unique(dias)]
    cnt = 0
    for _ in range(B_PERM):
        yp = yr.copy()
        for g in grupos: yp[g] = yr[rng.permutation(g)]
        cnt += stats.spearmanr(xr, yp)[0] >= obs
    return float(obs), float((cnt + 1) / (B_PERM + 1))


def nula(kl, ts, i0):
    rng = np.random.default_rng(SEED_NULL); day = ts.dt.floor("D").to_numpy(); r0 = np.log(kl.close.values)
    lr = np.diff(r0, prepend=r0[0]); hi = np.log(kl.high.values) - r0; lo = r0 - np.log(kl.low.values); perm = np.arange(len(kl))
    for d_ in np.unique(day[i0:]):
        s = np.where(day == d_)[0]; s = s[s >= i0]; perm[s] = rng.permutation(s)
    c2 = np.exp(r0[0] + np.cumsum(lr[perm])); lv = np.log(kl.volume.values.astype(float))
    return pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": c2 * np.exp(hi[perm]), "low": c2 * np.exp(-lo[perm]),
                         "close": c2, "volume": np.exp(lv[perm])})


def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--paridade-btc", action="store_true"); g.add_argument("--simbolo")
    a = ap.parse_args()
    if a.paridade_btc:
        sym, meses, fim, min_dias = "BTCUSDT", ["2026-05", "2026-06", "2026-07"], "2026-08-01", 0
    else:
        sym, meses, fim, min_dias = a.simbolo, ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"], "2026-10-01", 5
    kl = carregar(sym, meses); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may))
    wk = semanas(ts, "2026-06-01", fim, min_dias)
    julgadas = range(1, len(wk) - 1) if a.paridade_btc else range(1, len(wk))   # paridade: mesmas semanas da exploração
    raw = coords(kl); G, med, esc = regua(raw, may)
    (xr, yr, ii), (xa, ya, _), n_band = janelas(G, kl, ts, wk, julgadas)
    dias = ts.dt.floor("D").to_numpy()[ii]
    rho, p = p_perm(xr, yr, dias, np.random.default_rng(SEED_PERM))
    res = {"hipotese": "H-CAUDA-01", "simbolo": sym, "modo": "paridade" if a.paridade_btc else "julgamento",
           "regua": {"mediana_maio": med.tolist(), "escala": esc.tolist()},
           "semanas_julgadas": [str(ts.iloc[wk[k][0]].date()) for k in julgadas],
           "minutos_na_faixa": n_band, "janelas": int(len(xr)), "rho_parcial": rho, "p_permutacao_dia": p,
           "rho_todos_minutos_da_faixa": float(stats.spearmanr(xa, ya)[0])}
    q = pd.qcut(xr, 5, labels=False); res["quintis"] = pd.Series(yr / len(yr) * 100).groupby(q).mean().round(2).tolist()
    mes = ts.dt.strftime("%Y-%m").to_numpy()[ii]; res["rho_por_mes"] = {m: float(stats.spearmanr(xr[mes == m], yr[mes == m])[0]) for m in np.unique(mes)}
    G2, _, _ = regua(coords(nula(kl, ts, i0)), may); kn = nula(kl, ts, i0)
    (xn, yn, _), _, _ = janelas(G2, kn, ts, wk, julgadas)
    res["nula_pipeline"] = {"janelas": int(len(xn)), "rho_parcial": float(stats.spearmanr(xn, yn)[0])}
    if not a.paridade_btc:
        valido = len(xr) >= 600
        res["valido"] = valido
        res["veredito"] = ("INCONCLUSIVO" if not valido else "CONFIRMADA" if (p < 0.05 and rho >= 0.05) else "NÃO CONFIRMADA")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    out = ROOT / "resultados" / f"H-CAUDA-01_{sym}_{res['modo']}.json"; out.parent.mkdir(exist_ok=True)
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
