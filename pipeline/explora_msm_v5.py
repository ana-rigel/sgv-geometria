"""MSM v5: volume na equação de observação, r = σ̄ (v/v̄)^δ (ΠM)^½ ε, k = 1…4. Previsão: PREDICAO_msm_v5_volume_observacao.md.
v3:
Original v2: Previsão: PREDICAO_msm.md + PREDICAO_msm_v2.md (escala da t corrigida).

    python pipeline/explora_msm.py --periodo fumaca|junjul|agoset
"""
import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import t as student

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402
import explora_volatilidade_multiescala as MS  # noqa: E402

E = GR.E
KS = [1, 2, 3, 4]
VALID = {"S2": (2, 8026), "S3": (3, 8027)}; PARAMS_VALID = dict(m0=1.4, b=25.0, gk=0.5, nu=4.0)   # Emenda 2: escalas separadas (~2 min, ~50 min, ~21 h)


def estrutura(k, m0, b, gk):
    gam = 1 - (1 - gk) ** (float(b) ** (np.arange(1, k + 1, dtype=float) - k))
    combos = np.array(list(itertools.product([0, 1], repeat=k))); Ms = np.array([m0, 2 - m0])
    fator = np.sqrt(np.prod(Ms[combos], axis=1)); n = 2 ** k; P = np.ones((n, n))
    for i in range(k):
        same = combos[:, i][:, None] == combos[:, i][None, :]; P *= np.where(same, 1 - gam[i] / 2, gam[i] / 2)
    return gam, fator, P


def loglik(theta, r, k, lv):
    m0, b, gk, nu, delta = theta
    if not (1.01 < m0 < 1.95 and 1.01 < b < 50 and 1e-3 < gk < 0.999 and 2.3 < nu < 50 and 0.0 <= delta <= 1.0): return 1e18
    esc = np.exp(delta * lv); rr = r / esc; sig = float(np.std(rr))          # v5: volume na observação; σ̄ perfilado na série escalada
    gam, fator, P = estrutura(k, m0, b, gk); vol = sig * fator * np.sqrt((nu - 2) / nu)
    dens = student.pdf(rr[:, None] / vol[None, :], nu) / vol[None, :]
    p = np.full(len(vol), 1 / len(vol)); ll = 0.0
    for t in range(len(r)):
        w = (p @ P) * dens[t]; s = w.sum()
        if s <= 0: return 1e18
        ll += np.log(s); p = w / s
    return -(ll - delta * float(np.sum(lv)))   # jacobiano


def ajustar(r, k, lv):
    best = None; best_deg = None
    for x0 in ([1.4, 3.0, 0.5, 4.0, 0.5], [1.6, 5.0, 0.2, 3.0, 0.3], [1.25, 2.0, 0.8, 6.0, 0.7]):
        res = minimize(loglik, x0, args=(r, k, lv), method="Nelder-Mead", options={"maxfev": 400, "xatol": 1e-3, "fatol": 0.5})
        degen = (res.x[0] > 1.95 - 0.005 * 0.94) or (res.x[3] < 2.3 + 0.005 * 47.7)
        if degen:
            print(f"    (k={k}: solução degenerada: {np.round(res.x, 3)})", flush=True)
            if best_deg is None or res.fun < best_deg.fun: best_deg = res
            continue
        if best is None or res.fun < best.fun: best = res
    degenerado = best is None
    if degenerado: best = best_deg; print(f"    (k={k}: só soluções degeneradas; guardada com marca)", flush=True)
    m0, b, gk, nu, delta = best.x; gam = estrutura(k, m0, b, gk)[0]; n = len(r); npar = 5
    return {"k": k, "nll": float(best.fun), "bic": float(2 * best.fun + npar * np.log(n)), "m0": float(m0), "b": float(b), "gamma_k": float(gk), "nu": float(nu), "delta": float(delta),
            "escalas_min": [float(1 / g) for g in gam], "degenerado": bool(degenerado)}


def gerar(k, seed, n, sig, m0, b, gk, nu, lv=None, delta=0.5):
    rng = np.random.default_rng(seed); gam = 1 - (1 - gk) ** (float(b) ** (np.arange(1, k + 1, dtype=float) - k))
    M = rng.choice([m0, 2 - m0], size=k); r = np.empty(n)
    for t in range(n):
        sw = rng.random(k) < gam; M = np.where(sw, rng.choice([m0, 2 - m0], size=k), M)
        r[t] = sig * np.sqrt(np.prod(M)) * rng.standard_t(nu) / np.sqrt(nu / (nu - 2))
    return r * np.exp(delta * lv) if lv is not None else r


def selecionar(r, nome, lv):
    fits = [ajustar(r, k, lv) for k in KS]; ks = int(min(fits, key=lambda f: f["bic"])["k"])
    print(f"  {nome}: k* = {ks} | BIC " + " ".join(f"k{f['k']} {f['bic']:.0f}" for f in fits) + " | δ " + " ".join(f"{f['delta']:.2f}" for f in fits), flush=True)
    return {"k_star": ks, "ajustes": fits}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-05-03" if a.periodo == "fumaca" else "2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may))
    idx = np.concatenate(GR.semanas(ts, ini, fim)); lc = np.log(kl.close.values.astype(float)); r = np.diff(lc[idx])
    v = kl.volume.values.astype(float)[idx][1:]; vbar = float(np.mean(v)); v = np.maximum(v, 0.01 * vbar); lv = np.log(v / vbar)
    ok = np.isfinite(r); r, lv = r[ok], lv[ok]
    if a.periodo == "fumaca": r, lv = r[:5000], lv[:5000]
    sig = float(np.std(r / np.exp(0.5 * lv))); out = {"periodo": a.periodo, "n": int(len(r)), "modelo": "volume na observação"}
    for nome, (k, seed) in VALID.items():
        out[nome] = selecionar(gerar(k, seed, len(r), sig, lv=lv, delta=0.5, **PARAMS_VALID), f"validação {nome} (k gerador {k}, δ 0,5)", lv); out[nome]["k_gerador"] = k
    out["real"] = selecionar(r, "real", lv)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    def dhat(n_): return out[n_]["ajustes"][out[n_]["k_star"] - 1]["delta"]
    valido = all(out[n]["k_star"] == out[n]["k_gerador"] and abs(dhat(n) - 0.5) <= 0.1 for n in VALID); ks = out["real"]["k_star"]; dr = dhat("real")
    if out["real"]["ajustes"][ks - 1]["degenerado"]: valido = False   # Emenda 1: k* degenerado → INCONCLUSIVO
    cls = "INCONCLUSIVO" if not valido else ("volume irrelevante" if dr <= 0.2 else ("volume absorve a escada rápida" if ks <= 2 else ("absorve em parte" if ks == 3 else "hierarquia própria")))
    out.update(validacao=valido, classe=cls)
    best = out["real"]["ajustes"][ks - 1]
    print(f"\n== MSM [{a.periodo}] validação {valido}; real k* = {ks} → {cls}")
    print(f"  real k*: m0 {best['m0']:.3f} b {best['b']:.2f} γ_k {best['gamma_k']:.3f} ν {best['nu']:.2f} δ {best['delta']:.3f} · escalas (min): {[round(e, 1) for e in best['escalas_min']]}")
    print("  ΔBIC real (k→k+1):", [round(out["real"]["ajustes"][i]["bic"] - out["real"]["ajustes"][i + 1]["bic"], 1) for i in range(3)], "| δ̂ validação:", [round(dhat(n), 3) for n in VALID])
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"msm_v5_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
