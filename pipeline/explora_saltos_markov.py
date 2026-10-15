"""Exploração: (1) o campo é difusão ou saltos (Pawula, curtose condicional)? (2) Markov em 3D ou 4D (volatilidade escondida)?

Previsão e critérios: PREDICAO_saltos_markov.md (registrada antes deste código).

    python pipeline/explora_saltos_markov.py --periodo fumaca   # maio; só confere que roda, não imprime estatísticas
    python pipeline/explora_saltos_markov.py --periodo junjul
    python pipeline/explora_saltos_markov.py --periodo agoset
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402  (E, regua, semanas, sintetica, PERIODOS)

E = GR.E
K = 200
SEEDS_S = [2026, 2027, 2028]
SEEDS_G = [3026, 3027, 3028]
REGIOES = {"nucleo": (0, 1), "meio": (1, 3), "extremos": (3, 10)}
EIXOS = ["E_norm", "jerk", "memory_flux"]


def sintetica_gauss(kl, ts, i0, seed):
    """Como GR.sintetica, mas com choques gaussianos N(0,1): difusão pura com volatilidade estocástica."""
    rng = np.random.default_rng(seed); lc = np.log(kl.close.values.astype(float)); r = np.diff(lc, prepend=lc[0]); rs = r.copy()
    for idx in GR.semanas(ts, str(ts.iloc[i0].date()), str((ts.iloc[-1] + pd.Timedelta(minutes=1)))):
        idx = idx[idx >= i0]
        if len(idx) < 100: continue
        x = r[idx]; A = np.column_stack([np.ones(len(x) - 1), x[:-1]]); a, phi = np.linalg.lstsq(A, x[1:], rcond=None)[0]
        e = np.r_[0.0, x[1:] - (a + phi * x[:-1])]
        s = np.sqrt(pd.Series(e ** 2).rolling(61, center=True, min_periods=10).mean().to_numpy())
        s = np.where(np.isfinite(s) & (s > 0), s, np.nanmedian(s))
        us = rng.standard_normal(len(x))
        y = np.empty(len(x)); y[0] = x[0]
        for t in range(1, len(x)): y[t] = a + phi * y[t - 1] + s[t] * us[t]
        rs[idx] = y
    c = np.exp(lc[0] + np.cumsum(np.r_[0.0, rs[1:]]))
    out = kl.copy(); out["close"] = c; out["open"] = np.r_[c[0], c[:-1]]
    up = np.log(kl.high.values / kl.close.values); dn = np.log(kl.close.values / kl.low.values)
    out["high"] = c * np.exp(np.maximum(up, 0)); out["low"] = c * np.exp(-np.maximum(dn, 0))
    return out


def vol_causal(kl, may):
    """log do desvio dos retornos de 1 min nos 60 min anteriores a t (causal), na régua de caudas com âncora em maio."""
    lr = pd.Series(np.diff(np.log(kl.close.values.astype(float)), prepend=np.nan))
    v = np.log(lr.rolling(60, min_periods=30).std().shift(1).to_numpy() + 1e-12)
    ok = np.isfinite(v) & may; med = np.median(v[ok]); esc = np.quantile(np.abs(v[ok] - med), 0.995) / 3.0
    return (v - med) / esc


def tricubo(d):
    rk = np.maximum(d[:, -1], 1e-12)
    return np.clip(1 - (d / rk[:, None]) ** 3, 0, None) ** 3


def teste1(G, wk):
    rng = np.random.default_rng(20261019); kap, ext = [], []
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        X = G[tr[:-1]]; S = G[tr[1:]] - G[tr[:-1]]; ok = np.isfinite(X).all(1) & np.isfinite(S).all(1); X, S = X[ok], S[ok]
        P0 = G[te]; P0 = P0[np.isfinite(P0).all(1)]; e = np.abs(P0).max(1)
        core = np.where(e < 1)[0]; sel = np.r_[rng.choice(core, min(3000, len(core)), replace=False), np.where(e >= 1)[0]]
        d, idx = cKDTree(X).query(P0[sel], k=K); w = tricubo(d); sw = w.sum(1)
        m2 = np.einsum("nk,nkj->nj", w, S[idx] ** 2) / sw[:, None]; m4 = np.einsum("nk,nkj->nj", w, S[idx] ** 4) / sw[:, None]
        kap.append(m4 / np.maximum(m2 ** 2, 1e-300) - 3); ext.append(e[sel])
    kap, ext = np.vstack(kap), np.concatenate(ext)
    return {reg: {eixo: (float(np.median(kap[(ext >= lo) & (ext < hi), j])) if ((ext >= lo) & (ext < hi)).any() else None)
                  for j, eixo in enumerate(EIXOS)} | {"n": int(((ext >= lo) & (ext < hi)).sum())} for reg, (lo, hi) in REGIOES.items()}


def memoria(Z, wk, rng):
    """M = Spearman(ε_{t+1}, média ε_{t−9..t}); ε_t = |s_t|² / m2(x_{t−1}) com m2 do campo da semana anterior."""
    a, b = [], []
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        X = Z[tr[:-1]]; S2 = ((Z[tr[1:], :3] - Z[tr[:-1], :3]) ** 2).sum(1)
        ok = np.isfinite(X).all(1) & np.isfinite(S2); X, S2 = X[ok], S2[ok]
        Xe = Z[te[:-1]]; Se = ((Z[te[1:], :3] - Z[te[:-1], :3]) ** 2).sum(1)   # ε para o passo te[i] → te[i+1]
        oke = np.isfinite(Xe).all(1) & np.isfinite(Se)
        m2 = np.full(len(Xe), np.nan)
        if oke.any():
            d, idx = cKDTree(X).query(Xe[oke], k=K); w = tricubo(d); m2[oke] = (w * S2[idx]).sum(1) / w.sum(1)
        eps = Se / m2
        cand = np.arange(10, len(eps))
        cand = cand[np.isfinite(eps[cand]) & np.array([np.isfinite(eps[i - 10:i]).all() for i in cand])]
        pick = rng.choice(cand, min(5000, len(cand)), replace=False)
        a.append(eps[pick]); b.append(np.array([eps[i - 10:i].mean() for i in pick]))
    return float(spearmanr(np.concatenate(a), np.concatenate(b)).correlation)


def teste2(G, v, wk):
    m3 = memoria(G, wk, np.random.default_rng(20261020)); m4 = memoria(np.column_stack([G, v]), wk, np.random.default_rng(20261020))
    return {"M_3D": m3, "M_4D": m4, "Red": float(1 - m4 / m3) if m3 != 0 else None}


def medir(kl, ts, may, wk):
    G = GR.regua(E.coords_orig(kl), may)
    return {"T1": teste1(G, wk), "T2": teste2(G, vol_causal(kl, may), wk)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    if a.periodo == "fumaca":
        may = (ts < pd.Timestamp("2026-05-03", tz="UTC")).to_numpy()
    i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    series = {"real": kl, **{f"S_{s}": GR.sintetica(kl, ts, i0, s) for s in SEEDS_S}, **{f"G_{s}": sintetica_gauss(kl, ts, i0, s) for s in SEEDS_G}}
    res = {}
    for nome, k_ in series.items():
        res[nome] = medir(k_, ts, may, wk); print(f"  {nome}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    clas = {}
    for reg in REGIOES:
        r = res["real"]["T1"][reg]["E_norm"]; g = [res[f"G_{s}"]["T1"][reg]["E_norm"] for s in SEEDS_G]; s_ = [res[f"S_{s}"]["T1"][reg]["E_norm"] for s in SEEDS_S]
        if r is None: clas[reg] = "sem dados"; continue
        if r > max(g):
            clas[reg] = "saltos, reproduzidos pelas caudas dos choques" if r <= max(s_) else "saltos além das caudas dos choques"
        else:
            clas[reg] = "difusão adequada"
    t2 = res["real"]["T2"]
    clas2 = ("não é a volatilidade" if (t2["Red"] is None or t2["Red"] < 0.5) else
             ("a volatilidade é a dimensão que falta" if t2["M_4D"] < 0.05 else "ajuda, mas falta mais"))
    out = {"periodo": a.periodo, "series": res, "classificacao_T1_E_norm": clas, "classificacao_T2": clas2}
    print(f"\n== saltos × difusão e Markov [{a.periodo}]")
    for nome in series:
        t1 = res[nome]["T1"]; t2_ = res[nome]["T2"]
        print(f"  {nome:7s} κ_E núcleo {t1['nucleo']['E_norm']:6.2f} meio {t1['meio']['E_norm']:6.2f} extremos {t1['extremos']['E_norm']:6.2f}"
              f"  | κ_jerk ext {t1['extremos']['jerk']:6.2f} κ_mf ext {t1['extremos']['memory_flux']:6.2f}"
              f"  | M_3D {t2_['M_3D']:+.3f} M_4D {t2_['M_4D']:+.3f} Red {t2_['Red']:+.2f}")
    print("  T1 (E_norm):", clas); print("  T2:", clas2)
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"saltos_markov_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
