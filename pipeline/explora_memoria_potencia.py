"""Memória da volatilidade: lei de potência ou soma de exponenciais? Sintético E2 com escala lenta ajustada.
Previsão: PREDICAO_memoria_potencia.md.

    python pipeline/explora_memoria_potencia.py --periodo fumaca|junjul|agoset
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402
import explora_volatilidade_multiescala as MS  # noqa: E402
import confirmatorio_tempo as T  # noqa: E402  (retornos, perfil_dia, acf, LAGS)

E = GR.E
SEEDS_E2 = [5026, 5027, 5028, 5029, 5030]
LAGS_V2 = T.LAGS + [2048, 2880, 4096, 5760, 7200]        # v2: até 5 dias
PERIODOS_V2 = {**GR.PERIODOS, "junset": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"], "2026-06-01", "2026-10-01")}


def gerar_e2(kl, ts, i0, seed):
    """Como gerar_m, mas a escala lenta é um AR(1) AJUSTADO ao log do caminho suavizado, e simulado de novo."""
    rng = np.random.default_rng(seed); lc = np.log(kl.close.values.astype(float)); r = np.diff(lc, prepend=lc[0]); rs = r.copy(); params = []
    for idx in GR.semanas(ts, str(ts.iloc[i0].date()), str((ts.iloc[-1] + pd.Timedelta(minutes=1)))):
        idx = idx[idx >= i0]
        if len(idx) < 100: continue
        x = r[idx]; A = np.column_stack([np.ones(len(x) - 1), x[:-1]]); a, phi = np.linalg.lstsq(A, x[1:], rcond=None)[0]
        e = np.r_[0.0, x[1:] - (a + phi * x[:-1])]
        s = np.sqrt(pd.Series(e ** 2).rolling(61, center=True, min_periods=10).mean().to_numpy())
        s = np.where(np.isfinite(s) & (s > 0), s, np.nanmedian(s))
        # escala lenta ajustada: AR(1) em log s
        ell = np.log(s); B = np.column_stack([np.ones(len(ell) - 1), ell[:-1]]); c, phl = np.linalg.lstsq(B, ell[1:], rcond=None)[0]
        phl = float(np.clip(phl, 0.0, 0.9999)); veta = float(np.var(ell[1:] - (c + phl * ell[:-1])))
        ls = np.empty(len(x)); ls[0] = ell[0]; eta = rng.normal(0, np.sqrt(veta), len(x))
        for t in range(1, len(x)): ls[t] = c + phl * ls[t - 1] + eta[t]
        s_star = np.exp(ls)
        # escala rápida calibrada como no M
        ph, vh = MS.calibrar(e / s); params.append({"inicio": str(ts.iloc[idx[0]].date()), "phi_l": phl, "var_eta": veta, "tau_l": float(1 / (1 - phl)) if phl < 1 else None, "phi_h": ph, "var_h": vh})
        h = np.empty(len(x)); h[0] = rng.normal(0, np.sqrt(vh)); eta2 = rng.normal(0, np.sqrt(vh * (1 - ph ** 2)), len(x))
        for t in range(1, len(x)): h[t] = ph * h[t - 1] + eta2[t]
        f = np.exp(h - vh); z = rng.standard_normal(len(x))
        y = np.empty(len(x)); y[0] = x[0]
        for t in range(1, len(x)): y[t] = a + phi * y[t - 1] + s_star[t] * f[t] * z[t]
        rs[idx] = y
    cfe = np.exp(lc[0] + np.cumsum(np.r_[0.0, rs[1:]]))
    out = kl.copy(); out["close"] = cfe; out["open"] = np.r_[cfe[0], cfe[:-1]]
    up = np.log(kl.high.values / kl.close.values); dn = np.log(kl.close.values / kl.low.values)
    out["high"] = cfe * np.exp(np.maximum(up, 0)); out["low"] = cfe * np.exp(-np.maximum(dn, 0))
    return out, params


def dois_exp(tau, A, t1, B, t2):
    return np.log(np.maximum(A * np.exp(-tau / t1) + B * np.exp(-tau / t2), 1e-12))


def ajustar_formas(rho, lags=None):
    tau = np.array(lags or T.LAGS, float); ok = np.isfinite(rho) & (rho > 0); n = int(ok.sum()); out = {"n_pos": n}
    if n < 6: return out
    y = np.log(rho[ok]); t = tau[ok]
    def aic(sqr, k): return float(n * np.log(max(sqr, 1e-300) / n) + 2 * k)
    b1, a1 = np.polyfit(np.log(t), y, 1); sqr = float(np.sum((y - (a1 + b1 * np.log(t))) ** 2))
    out.update(beta=float(-b1), r2_pot=float(1 - sqr / np.sum((y - y.mean()) ** 2)), aic_pot=aic(sqr, 2))
    b2, a2 = np.polyfit(t, y, 1); sqr = float(np.sum((y - (a2 + b2 * t)) ** 2))
    out.update(theta=float(-1 / b2) if b2 < 0 else None, r2_exp=float(1 - sqr / np.sum((y - y.mean()) ** 2)), aic_exp=aic(sqr, 2))
    out["delta_r2"] = out["r2_pot"] - out["r2_exp"]
    best = None
    for t1, t2 in ((3, 300), (10, 1000), (30, 3000), (5, 100)):
        try:
            p, _ = curve_fit(dois_exp, t, y, p0=[rho[ok][0] / 2, t1, rho[ok][0] / 2, t2], bounds=([0, 1, 0, 1], [1, 1e4, 1, 1e4]), maxfev=20000)
            s = float(np.sum((y - dois_exp(t, *p)) ** 2))
            if best is None or s < best[0]: best = (s, p)
        except Exception:
            continue
    if best:
        s, p = best; th = sorted([p[1], p[3]])
        out.update(theta1=float(th[0]), theta2=float(th[1]), aic_2exp=aic(s, 4), r2_2exp=float(1 - s / np.sum((y - y.mean()) ** 2)))
        out["d_aic"] = out["aic_pot"] - out["aic_2exp"]   # negativo = potência melhor
    return out


def classe(f):
    if "aic_2exp" not in f: return "sem ajuste"
    if f["aic_pot"] < f["aic_2exp"] - 2 and 0.1 <= f["beta"] <= 0.6: return "potência"
    if f["aic_2exp"] < f["aic_pot"] - 2: return "duas exponenciais"
    return "indistinguível"


def medir(kl, ts, may, wk, s_dia, lags=None):
    lags = lags or T.LAGS; a = np.abs(T.retornos(kl)) / s_dia; blk = [np.concatenate(wk)]
    rho = T.acf(a, blk, lags); f = ajustar_formas(rho, lags); f["rho"] = [None if not np.isfinite(v) else float(v) for v in rho]; f["classe"] = classe(f)
    if len(lags) > 21:   # v2: ΔAIC em função do atraso máximo (1, 2, 3, 5 dias)
        f["d_aic_por_corte"] = {}
        for corte in (1440, 2880, 4320, 7200):
            m = [i for i, L in enumerate(lags) if L <= corte]; g = ajustar_formas(rho[m], [lags[i] for i in m])
            f["d_aic_por_corte"][str(corte)] = g.get("d_aic")
    return f


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS_V2), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    ap.add_argument("--v2", action="store_true", help="grade até 5 dias (PREDICAO_memoria_potencia_v2.md)")
    a = ap.parse_args(); meses, ini, fim = PERIODOS_V2[a.periodo]; lags = LAGS_V2 if a.v2 else None; tag = "_v2" if a.v2 else ""
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-05-03" if a.periodo == "fumaca" else "2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    s_dia = T.perfil_dia(T.retornos(kl), ts, may)
    res = {"real": medir(kl, ts, may, wk, s_dia, lags)}; print("  real: ok", flush=True); params = {}
    for s in SEEDS_E2:
        k_, p = gerar_e2(kl, ts, i0, s); res[f"E2_{s}"] = medir(k_, ts, may, wk, s_dia, lags); params[f"E2_{s}"] = p; print(f"  E2_{s}: ok", flush=True)
    for s in MS.SEEDS_M:
        k_, _, _ = MS.gerar_m(kl, ts, i0, s); res[f"M_{s}"] = medir(k_, ts, may, wk, s_dia, lags); print(f"  M_{s}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    e2 = [res[f"E2_{s}"] for s in SEEDS_E2]; real = res["real"]
    valid = sum(f["classe"] in ("duas exponenciais", "indistinguível") for f in e2) >= 4
    rr = np.array([v if v is not None else np.nan for v in real["rho"]]); re2 = np.array([[v if v is not None else np.nan for v in f["rho"]] for f in e2])
    LG = lags or T.LAGS; fora = [LG[i] for i in range(len(LG)) if np.isfinite(rr[i]) and (rr[i] > np.nanmax(re2[:, i]) or rr[i] < np.nanmin(re2[:, i]))]
    d = [f["delta_r2"] for f in e2 if "delta_r2" in f]
    cls_env = "acima" if real["delta_r2"] > max(d) else ("dentro" if real["delta_r2"] >= min(d) else "abaixo")
    out = {"periodo": a.periodo, "series": res, "parametros_E2": params, "validacao_E2": valid, "classe_real": real["classe"] if valid else "INCONCLUSIVO",
           "delta_r2_vs_E2": cls_env, "descola_em": fora[0] if fora else None}
    print(f"\n== memória em lei de potência{tag} [{a.periodo}]")
    for nome, f in res.items():
        print(f"  {nome:8s} β {f.get('beta', float('nan')):.3f} θ {f.get('theta') or float('nan'):8.1f} θ1/θ2 {f.get('theta1', float('nan')):7.1f}/{f.get('theta2', float('nan')):8.1f} "
              f"AIC pot {f.get('aic_pot', float('nan')):7.1f} exp {f.get('aic_exp', float('nan')):7.1f} 2exp {f.get('aic_2exp', float('nan')):7.1f} ΔR² {f.get('delta_r2', float('nan')):+.3f} → {f['classe']}", flush=True)
    pr = params[f"E2_{SEEDS_E2[0]}"]; print("  E2 por semana (φ_ℓ, τ_ℓ min, Var η):", [(round(x["phi_l"], 4), round(x["tau_l"] or 0, 0), round(x["var_eta"], 5)) for x in pr])
    if lags: print("  ρ real nos atrasos longos:", [(L, round(v, 3)) for L, v in zip(LG[21:], real["rho"][21:]) if v is not None], "| ΔAIC por corte:", real.get("d_aic_por_corte"))
    print(f"  validação E2: {valid}; classe real: {out['classe_real']}; ΔR² real vs E2: {cls_env}; descola em: {out['descola_em']} min")
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"memoria_potencia{tag}_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
