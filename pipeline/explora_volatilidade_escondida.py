"""Exploração: a volatilidade é a dimensão escondida do espaço 3D? Previsão: PREDICAO_volatilidade_escondida.md.

    python pipeline/explora_volatilidade_escondida.py --periodo fumaca   # maio; não imprime estatísticas
    python pipeline/explora_volatilidade_escondida.py --periodo junjul
    python pipeline/explora_volatilidade_escondida.py --periodo agoset
    python pipeline/explora_volatilidade_escondida.py --combinar          # aplica a regra (etapas A e B) aos dois períodos

Indexação: ε_{t+1} = |s_{t+1}|² / (σ̂_t² · m2*(x_t)), s_{t+1} = x_{t+1} − x_t. σ̂_t usa retornos até r_t (inclusive), que é
anterior ao passo t → t+1. O oráculo dos sintéticos para esse passo é a volatilidade que gerou r_{t+1}.
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
import explora_geometria_residual as GR  # noqa: E402

E = GR.E
K = 200
SEEDS_G = [3026, 3027, 3028, 3029, 3030]
SEEDS_S = [2026, 2027, 2028]
CAUSAIS = ["c60", "ew10", "ew30", "har"]


def gerar(kl, ts, i0, seed, gauss):
    """Mesma construção de GR.sintetica (gauss=False) e de sintetica_gauss (gauss=True); devolve também o oráculo s_t."""
    rng = np.random.default_rng(seed); lc = np.log(kl.close.values.astype(float)); r = np.diff(lc, prepend=lc[0]); rs = r.copy()
    orc = np.full(len(r), np.nan)
    for idx in GR.semanas(ts, str(ts.iloc[i0].date()), str((ts.iloc[-1] + pd.Timedelta(minutes=1)))):
        idx = idx[idx >= i0]
        if len(idx) < 100: continue
        x = r[idx]; A = np.column_stack([np.ones(len(x) - 1), x[:-1]]); a, phi = np.linalg.lstsq(A, x[1:], rcond=None)[0]
        e = np.r_[0.0, x[1:] - (a + phi * x[:-1])]
        s = np.sqrt(pd.Series(e ** 2).rolling(61, center=True, min_periods=10).mean().to_numpy())
        s = np.where(np.isfinite(s) & (s > 0), s, np.nanmedian(s))
        if gauss:
            us = rng.standard_normal(len(x))
        else:
            u = e / s; u[0] = 0.0; us = rng.permutation(u)
        y = np.empty(len(x)); y[0] = x[0]
        for t in range(1, len(x)): y[t] = a + phi * y[t - 1] + s[t] * us[t]
        rs[idx] = y; orc[idx] = s
    c = np.exp(lc[0] + np.cumsum(np.r_[0.0, rs[1:]]))
    out = kl.copy(); out["close"] = c; out["open"] = np.r_[c[0], c[:-1]]
    up = np.log(kl.high.values / kl.close.values); dn = np.log(kl.close.values / kl.low.values)
    out["high"] = c * np.exp(np.maximum(up, 0)); out["low"] = c * np.exp(-np.maximum(dn, 0))
    return out, orc


def estimativas(kl, orc=None):
    r = pd.Series(np.diff(np.log(kl.close.values.astype(float)), prepend=np.nan)); r2 = r ** 2
    est = {"c60": r.rolling(60, min_periods=30).std().to_numpy(),
           "ew10": np.sqrt(r2.ewm(alpha=0.1, adjust=False).mean().to_numpy()),
           "ew30": np.sqrt(r2.ewm(alpha=0.033, adjust=False).mean().to_numpy()),
           "har": np.sqrt((r2.rolling(10, min_periods=5).mean() + r2.rolling(60, min_periods=30).mean()
                           + r2.rolling(240, min_periods=120).mean()).to_numpy() / 3)}
    if orc is not None:
        est["oraculo"] = np.r_[orc[1:], np.nan]          # vol que gerou r_{t+1}, alinhada em t
    return {k: np.where(np.isfinite(v) & (v > 0), v, np.nan) for k, v in est.items()}


def memoria(G, sig, wk, rng):
    a, b = [], []
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        X = G[tr[:-1]]; S2 = ((G[tr[1:]] - G[tr[:-1]]) ** 2).sum(1) / sig[tr[:-1]] ** 2
        ok = np.isfinite(X).all(1) & np.isfinite(S2); X, S2 = X[ok], S2[ok]
        Xe = G[te[:-1]]; Se = ((G[te[1:]] - G[te[:-1]]) ** 2).sum(1); se = sig[te[:-1]]
        oke = np.isfinite(Xe).all(1) & np.isfinite(Se) & np.isfinite(se)
        m2 = np.full(len(Xe), np.nan)
        if oke.any():
            d, idx = cKDTree(X).query(Xe[oke], k=K)
            rk = np.maximum(d[:, -1], 1e-12); w = np.clip(1 - (d / rk[:, None]) ** 3, 0, None) ** 3
            m2[oke] = (w * S2[idx]).sum(1) / w.sum(1)
        eps = Se / (se ** 2 * m2)
        fin = np.isfinite(eps); cs = np.r_[0, np.cumsum(fin)]
        cand = np.arange(10, len(eps)); cand = cand[fin[cand] & ((cs[cand] - cs[cand - 10]) == 10)]
        pick = rng.choice(cand, min(5000, len(cand)), replace=False)
        a.append(eps[pick]); b.append(np.array([eps[i - 10:i].mean() for i in pick]))
    return float(spearmanr(np.concatenate(a), np.concatenate(b)).correlation)


def medir(kl, ts, may, wk, orc=None):
    G = GR.regua(E.coords_orig(kl), may); est = estimativas(kl, orc)
    out = {"sem_vol": memoria(G, np.ones(len(G)), wk, np.random.default_rng(20261020))}
    for nome, sig in est.items():
        out[nome] = memoria(G, sig, wk, np.random.default_rng(20261020))
    return out


def combinar():
    R = {p: json.loads((ROOT / "resultados" / f"volatilidade_escondida_{p}.json").read_text()) for p in ("junjul", "agoset")}
    red = lambda m, k: 1 - m[k] / m["sem_vol"]  # noqa: E731
    A = {}
    for p, r in R.items():
        Gs = [r["series"][f"G_{s}"] for s in SEEDS_G]
        A[p] = {"red_oraculo_G": float(np.mean([red(m, "oraculo") for m in Gs])), **{f"red_{c}_G": float(np.mean([red(m, c) for m in Gs])) for c in CAUSAIS}}
    valida = all(A[p]["red_oraculo_G"] >= 0.7 for p in R)
    escolhida = max(CAUSAIS, key=lambda c: sum(A[p][f"red_{c}_G"] for p in R))
    res = {"etapa_A": A, "validacao_passa": valida, "estimativa_escolhida": escolhida}
    if not valida:
        res["veredito"] = "INCONCLUSIVO (o método não remove a memória nem com a volatilidade verdadeira)"
    else:
        cl = {}
        for p, r in R.items():
            mr = r["series"]["real"][escolhida]; mg = [r["series"][f"G_{s}"][escolhida] for s in SEEDS_G]
            cl[p] = {"M_real": mr, "M_G": mg, "classe": "fechado" if mr <= max(mg) else "sobra além da volatilidade"}
        res["etapa_B"] = cl
        cls = {v["classe"] for v in cl.values()}
        res["veredito"] = ("FECHADO: a volatilidade é a dimensão escondida" if cls == {"fechado"} else
                           "SOBRA memória além da volatilidade" if cls == {"sobra além da volatilidade"} else "NÃO ESTÁVEL")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    (ROOT / "resultados" / "volatilidade_escondida_veredito.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS)); ap.add_argument("--combinar", action="store_true")
    ap.add_argument("--dados", default=str(ROOT / "dados")); a = ap.parse_args()
    if a.combinar:
        return combinar()
    meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    if a.periodo == "fumaca":
        may = (ts < pd.Timestamp("2026-05-03", tz="UTC")).to_numpy()
    i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    res = {"real": medir(kl, ts, may, wk)}; print("  real: ok", flush=True)
    for s in SEEDS_G:
        k_, o = gerar(kl, ts, i0, s, True); res[f"G_{s}"] = medir(k_, ts, may, wk, o); print(f"  G_{s}: ok", flush=True)
    for s in SEEDS_S:
        k_, o = gerar(kl, ts, i0, s, False); res[f"S_{s}"] = medir(k_, ts, may, wk, o); print(f"  S_{s}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    print(f"\n== volatilidade escondida [{a.periodo}]  (M = memória da surpresa; menor = mais markoviano)")
    for nome, m in res.items():
        print(f"  {nome:7s} " + "  ".join(f"{k} {v:+.3f}" for k, v in m.items()), flush=True)
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"volatilidade_escondida_{a.periodo}.json").write_text(json.dumps({"periodo": a.periodo, "series": res}, ensure_ascii=False))


if __name__ == "__main__":
    main()
