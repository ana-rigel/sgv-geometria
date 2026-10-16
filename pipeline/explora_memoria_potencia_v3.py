"""Memória da volatilidade v3: grade sem múltiplos de um dia, dessazonalização por diferença, E2 gerado de uma vez.
Previsão: PREDICAO_memoria_potencia_v3.md.

    python pipeline/explora_memoria_potencia_v3.py --periodo fumaca|junjul|agoset|junset
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
import explora_volatilidade_multiescala as MS  # noqa: E402
import confirmatorio_tempo as T  # noqa: E402  (retornos, acf)
import explora_memoria_potencia as P  # noqa: E402  (ajustar_formas, classe, PERIODOS_V2)

E = GR.E
LAGS3 = [1, 2, 3, 4, 6, 8, 11, 16, 23, 32, 45, 64, 91, 128, 181, 256, 362, 512, 724, 1024, 1800, 2160, 3600, 5040, 6480]
SEEDS_E3 = list(range(6026, 6036))


def media_dia(r, ts, may):
    h = (ts.dt.hour * 60 + ts.dt.minute).to_numpy(); a = np.abs(r); m = np.full(1440, np.nan)
    for k in range(1440):
        sel = may & (h == k) & np.isfinite(a)
        if sel.any(): m[k] = a[sel].mean()
    m = np.where(np.isfinite(m), m, np.nanmean(m))
    return m[h]


def gerar_e3(kl, i0, seed):
    """E2 do período inteiro: um ajuste, uma trajetória, sem re-ancorar."""
    rng = np.random.default_rng(seed); lc = np.log(kl.close.values.astype(float)); r = np.diff(lc, prepend=lc[0]); rs = r.copy()
    x = r[i0:]; A = np.column_stack([np.ones(len(x) - 1), x[:-1]]); a, phi = np.linalg.lstsq(A, x[1:], rcond=None)[0]
    e = np.r_[0.0, x[1:] - (a + phi * x[:-1])]
    s = np.sqrt(pd.Series(e ** 2).rolling(61, center=True, min_periods=10).mean().to_numpy()); s = np.where(np.isfinite(s) & (s > 0), s, np.nanmedian(s))
    ell = np.log(s); B = np.column_stack([np.ones(len(ell) - 1), ell[:-1]]); c, phl = np.linalg.lstsq(B, ell[1:], rcond=None)[0]
    phl = float(np.clip(phl, 0.0, 0.99999)); veta = float(np.var(ell[1:] - (c + phl * ell[:-1])))
    ls = np.empty(len(x)); ls[0] = ell[0]; eta = rng.normal(0, np.sqrt(veta), len(x))
    for t in range(1, len(x)): ls[t] = c + phl * ls[t - 1] + eta[t]
    ph, vh = MS.calibrar(e / s)
    h = np.empty(len(x)); h[0] = rng.normal(0, np.sqrt(vh)); eta2 = rng.normal(0, np.sqrt(vh * (1 - ph ** 2)), len(x))
    for t in range(1, len(x)): h[t] = ph * h[t - 1] + eta2[t]
    f = np.exp(h - vh); z = rng.standard_normal(len(x)); y = np.empty(len(x)); y[0] = x[0]; sst = np.exp(ls)
    for t in range(1, len(x)): y[t] = a + phi * y[t - 1] + sst[t] * f[t] * z[t]
    rs[i0:] = y
    cfe = np.exp(lc[0] + np.cumsum(np.r_[0.0, rs[1:]])); out = kl.copy(); out["close"] = cfe; out["open"] = np.r_[cfe[0], cfe[:-1]]
    up = np.log(kl.high.values / kl.close.values); dn = np.log(kl.close.values / kl.low.values)
    out["high"] = cfe * np.exp(np.maximum(up, 0)); out["low"] = cfe * np.exp(-np.maximum(dn, 0))
    return out, {"a": float(a), "phi": float(phi), "c": float(c), "phi_l": phl, "tau_l_min": float(1 / (1 - phl)), "var_eta": veta, "phi_h": float(ph), "var_h": float(vh)}


def medir(kl, wk, m_dia):
    a = np.abs(T.retornos(kl)) - m_dia; blk = [np.concatenate(wk)]
    rho = T.acf(a, blk, LAGS3); f = P.ajustar_formas(rho, LAGS3); f["rho"] = [None if not np.isfinite(v) else float(v) for v in rho]; f["classe"] = P.classe(f)
    f["d_aic_por_corte"] = {}
    for corte in (2160, 3600, 5040, 6480):
        m = [i for i, L in enumerate(LAGS3) if L <= corte]; g = P.ajustar_formas(rho[m], [LAGS3[i] for i in m]); f["d_aic_por_corte"][str(corte)] = g.get("d_aic")
    return f


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(P.PERIODOS_V2), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = P.PERIODOS_V2[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-05-03" if a.periodo == "fumaca" else "2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    m_dia = media_dia(T.retornos(kl), ts, may)
    res = {"real": medir(kl, wk, m_dia)}; print("  real: ok", flush=True); params = {}
    for s in SEEDS_E3:
        k_, p = gerar_e3(kl, i0, s); res[f"E2_{s}"] = medir(k_, wk, m_dia); params[f"E2_{s}"] = p; print(f"  E2_{s}: ok", flush=True)
    for s in MS.SEEDS_M:
        k_, _, _ = MS.gerar_m(kl, ts, i0, s); res[f"M_{s}"] = medir(k_, wk, m_dia); print(f"  M_{s}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    e2 = [res[f"E2_{s}"] for s in SEEDS_E3]; real = res["real"]
    n2 = sum(f["classe"] == "duas exponenciais" for f in e2); valid = n2 >= 8
    rr = np.array([v if v is not None else np.nan for v in real["rho"]]); re2 = np.array([[v if v is not None else np.nan for v in f["rho"]] for f in e2])
    fora = [LAGS3[i] for i in range(len(LAGS3)) if np.isfinite(rr[i]) and (rr[i] > np.nanmax(re2[:, i]) or rr[i] < np.nanmin(re2[:, i]))]
    d = [f["delta_r2"] for f in e2 if "delta_r2" in f]
    cls_env = "acima" if real["delta_r2"] > max(d) else ("dentro" if real["delta_r2"] >= min(d) else "abaixo")
    out = {"periodo": a.periodo, "series": res, "parametros_E2": params, "E2_duas_exp": n2, "validacao_E2": valid,
           "classe_real": real["classe"] if valid else "INCONCLUSIVO", "delta_r2_vs_E2": cls_env, "descola_em": fora[0] if fora else None}
    print(f"\n== memória em lei de potência v3 [{a.periodo}]")
    for nome, f in res.items():
        print(f"  {nome:8s} β {f.get('beta', float('nan')):.3f} θ {f.get('theta') or float('nan'):8.1f} θ1/θ2 {f.get('theta1', float('nan')):7.1f}/{f.get('theta2', float('nan')):8.1f} "
              f"AIC pot {f.get('aic_pot', float('nan')):7.1f} 2exp {f.get('aic_2exp', float('nan')):7.1f} ΔR² {f.get('delta_r2', float('nan')):+.3f} → {f['classe']}", flush=True)
    print("  ρ real longos:", [(L, round(v, 3)) for L, v in zip(LAGS3[20:], real["rho"][20:]) if v is not None], "| E2_6026:", [(L, round(v, 3)) for L, v in zip(LAGS3[20:], res["E2_6026"]["rho"][20:]) if v is not None])
    print("  ΔAIC real por corte:", real["d_aic_por_corte"]); print("  E2 parâmetros (6026):", {k: round(v, 5) for k, v in params["E2_6026"].items()})
    print(f"  E2 'duas exponenciais': {n2}/10; validação: {valid}; classe real: {out['classe_real']}; ΔR² vs E2: {cls_env}; descola em: {out['descola_em']} min")
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"memoria_potencia_v3_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
