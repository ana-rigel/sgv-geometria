"""Volatilidade multiescala: o real cabe num sintético com escala lenta real × escala rápida calibrada?
Previsão: PREDICAO_volatilidade_multiescala.md. Medida idêntica à 2ª rodada (explora_volatilidade_escondida_v2.py).

    python pipeline/explora_volatilidade_multiescala.py --periodo fumaca|junjul|agoset
    python pipeline/explora_volatilidade_multiescala.py --combinar
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402
import explora_volatilidade_escondida as V  # noqa: E402
import explora_volatilidade_escondida_v2 as V2  # noqa: E402

E = GR.E
SEEDS_M = [4026, 4027, 4028, 4029, 4030]
PRIMARIA = "ew10"


def calibrar(u):
    y = np.log(u[1:] ** 2 + 1e-12); y = y - y.mean(); vy = y.var()
    ks = np.arange(1, 21); ac = np.array([np.mean(y[:-k] * y[k:]) / vy for k in ks])
    ok = ac > 0
    if ok.sum() < 3:
        return 0.0, 0.0
    b, a = np.polyfit(ks[ok], np.log(ac[ok]), 1)
    phi = float(np.clip(np.exp(b), 0.0, 0.995)); c = float(np.exp(a))
    return phi, float(np.clip(c * vy / 4, 0.0, 2.0))


def gerar_m(kl, ts, i0, seed):
    rng = np.random.default_rng(seed); lc = np.log(kl.close.values.astype(float)); r = np.diff(lc, prepend=lc[0]); rs = r.copy()
    orc = np.full(len(r), np.nan); params = []
    for idx in GR.semanas(ts, str(ts.iloc[i0].date()), str((ts.iloc[-1] + pd.Timedelta(minutes=1)))):
        idx = idx[idx >= i0]
        if len(idx) < 100: continue
        x = r[idx]; A = np.column_stack([np.ones(len(x) - 1), x[:-1]]); a, phi = np.linalg.lstsq(A, x[1:], rcond=None)[0]
        e = np.r_[0.0, x[1:] - (a + phi * x[:-1])]
        s = np.sqrt(pd.Series(e ** 2).rolling(61, center=True, min_periods=10).mean().to_numpy())
        s = np.where(np.isfinite(s) & (s > 0), s, np.nanmedian(s))
        ph, vh = calibrar(e / s); params.append({"inicio": str(ts.iloc[idx[0]].date()), "phi_h": ph, "var_h": vh})
        h = np.empty(len(x)); h[0] = rng.normal(0, np.sqrt(vh)); eta = rng.normal(0, np.sqrt(vh * (1 - ph ** 2)), len(x))
        for t in range(1, len(x)): h[t] = ph * h[t - 1] + eta[t]
        f = np.exp(h - vh); z = rng.standard_normal(len(x))
        y = np.empty(len(x)); y[0] = x[0]
        for t in range(1, len(x)): y[t] = a + phi * y[t - 1] + s[t] * f[t] * z[t]
        rs[idx] = y; orc[idx] = s * f
    c = np.exp(lc[0] + np.cumsum(np.r_[0.0, rs[1:]]))
    out = kl.copy(); out["close"] = c; out["open"] = np.r_[c[0], c[:-1]]
    up = np.log(kl.high.values / kl.close.values); dn = np.log(kl.close.values / kl.low.values)
    out["high"] = c * np.exp(np.maximum(up, 0)); out["low"] = c * np.exp(-np.maximum(dn, 0))
    return out, orc, params


def combinar():
    R = {p: json.loads((ROOT / "resultados" / f"volatilidade_multiescala_{p}.json").read_text()) for p in ("junjul", "agoset")}
    red = lambda m, k: 1 - m[k] / m["sem_vol"]  # noqa: E731
    val = {p: float(np.mean([red(r["series"][f"M_{s}"], "oraculo") for s in SEEDS_M])) for p, r in R.items()}
    res = {"red_oraculo_M": val, "validacao_passa": all(v >= 0.7 for v in val.values())}
    if not res["validacao_passa"]:
        res["veredito"] = "INCONCLUSIVO"
    else:
        tab = {}
        for est in ["ew10", "c60", "ew30", "har"]:
            tab[est] = {}
            for p, r in R.items():
                mr = r["series"]["real"][est]; mm = [r["series"][f"M_{s}"][est] for s in SEEDS_M]
                tab[est][p] = {"M_real": mr, "M_M": [min(mm), max(mm)], "classe": "fechado" if mr <= max(mm) else "sobra"}
        res["comparacoes"] = tab
        cls = {tab[PRIMARIA][p]["classe"] for p in R}
        res["veredito"] = ("FECHADO: volatilidade multiescala" if cls == {"fechado"} else
                           "SOBRA além da volatilidade multiescala" if cls == {"sobra"} else "NÃO ESTÁVEL")
        todas = {tab[e][p]["classe"] for e in tab for p in R}
        res["robusto"] = len(todas) == 1
    print(json.dumps(res, ensure_ascii=False, indent=1))
    (ROOT / "resultados" / "volatilidade_multiescala_veredito.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


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
    res = {"real": V2.medir(kl, ts, may, wk)}; print("  real: ok", flush=True); params = {}
    for s in SEEDS_M:
        k_, o, p = gerar_m(kl, ts, i0, s); res[f"M_{s}"] = V2.medir(k_, ts, may, wk, o); params[f"M_{s}"] = p; print(f"  M_{s}: ok", flush=True)
    for s in V.SEEDS_G:
        k_, o = V.gerar(kl, ts, i0, s, True); res[f"G_{s}"] = V2.medir(k_, ts, may, wk, o); print(f"  G_{s}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    print(f"\n== volatilidade multiescala [{a.periodo}]  (M = memória da surpresa do retorno; menor = mais markoviano)")
    for nome, m in res.items():
        print(f"  {nome:7s} " + "  ".join(f"{k} {v:+.3f}" for k, v in m.items()), flush=True)
    pr = params[f"M_{SEEDS_M[0]}"]
    print("  calibração por semana (φ_h, Var h):", [(round(x["phi_h"], 3), round(x["var_h"], 3)) for x in pr])
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"volatilidade_multiescala_{a.periodo}.json").write_text(
        json.dumps({"periodo": a.periodo, "series": res, "calibracao": params}, ensure_ascii=False))


if __name__ == "__main__":
    main()
