"""MSM v3: dessazonalizado por variância diária (âncora maio), k = 1…5, sem M. Previsão: PREDICAO_msm_v3.md.
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
KS = [1, 2, 3, 4, 5]
VALID = {"S2": (2, 8026), "S3": (3, 8027)}; PARAMS_VALID = dict(m0=1.4, b=25.0, gk=0.5, nu=4.0)   # Emenda 2: escalas separadas (~2 min, ~50 min, ~21 h)


def estrutura(k, m0, b, gk):
    gam = 1 - (1 - gk) ** (float(b) ** (np.arange(1, k + 1, dtype=float) - k))
    combos = np.array(list(itertools.product([0, 1], repeat=k))); Ms = np.array([m0, 2 - m0])
    fator = np.sqrt(np.prod(Ms[combos], axis=1)); n = 2 ** k; P = np.ones((n, n))
    for i in range(k):
        same = combos[:, i][:, None] == combos[:, i][None, :]; P *= np.where(same, 1 - gam[i] / 2, gam[i] / 2)
    return gam, fator, P


def loglik(theta, r, k, sig):
    m0, b, gk, nu = theta
    if not (1.01 < m0 < 1.95 and 1.01 < b < 50 and 1e-3 < gk < 0.999 and 2.3 < nu < 50): return 1e18   # v3 Emenda 1
    gam, fator, P = estrutura(k, m0, b, gk); vol = sig * fator * np.sqrt((nu - 2) / nu)   # v2: t padronizada (variância 1)
    dens = student.pdf(r[:, None] / vol[None, :], nu) / vol[None, :]
    p = np.full(len(vol), 1 / len(vol)); ll = 0.0
    for t in range(len(r)):
        w = (p @ P) * dens[t]; s = w.sum()
        if s <= 0: return 1e18
        ll += np.log(s); p = w / s
    return -ll


def ajustar(r, k):
    sig = float(np.std(r)); best = None; LIM = [(1.01, 1.95), (1.01, 50), (1e-3, 0.999), (2.3, 50)]
    for x0 in ([1.4, 3.0, 0.5, 4.0], [1.6, 5.0, 0.2, 3.0], [1.25, 2.0, 0.8, 6.0]):
        res = minimize(loglik, x0, args=(r, k, sig), method="Nelder-Mead", options={"maxfev": 300, "xatol": 1e-3, "fatol": 0.5})
        degen = any(abs(v - lo) < 0.005 * (hi - lo) or abs(v - hi) < 0.005 * (hi - lo) for v, (lo, hi) in zip(res.x, LIM))
        if degen: print(f"    (k={k}: solução degenerada descartada: {np.round(res.x, 3)})", flush=True); continue
        if best is None or res.fun < best.fun: best = res
    if best is None: raise RuntimeError(f"k={k}: só soluções degeneradas")
    m0, b, gk, nu = best.x; gam = estrutura(k, m0, b, gk)[0]; n = len(r); npar = 4
    return {"k": k, "nll": float(best.fun), "bic": float(2 * best.fun + npar * np.log(n)), "m0": float(m0), "b": float(b), "gamma_k": float(gk), "nu": float(nu),
            "escalas_min": [float(1 / g) for g in gam], "sigma": sig}


def gerar(k, seed, n, sig, m0, b, gk, nu):
    rng = np.random.default_rng(seed); gam = 1 - (1 - gk) ** (float(b) ** (np.arange(1, k + 1, dtype=float) - k))
    M = rng.choice([m0, 2 - m0], size=k); r = np.empty(n)
    for t in range(n):
        sw = rng.random(k) < gam; M = np.where(sw, rng.choice([m0, 2 - m0], size=k), M)
        r[t] = sig * np.sqrt(np.prod(M)) * rng.standard_t(nu) / np.sqrt(nu / (nu - 2))
    return r


def selecionar(r, nome):
    fits = [ajustar(r, k) for k in KS]; ks = int(min(fits, key=lambda f: f["bic"])["k"])
    print(f"  {nome}: k* = {ks} | BIC " + " ".join(f"k{f['k']} {f['bic']:.0f}" for f in fits), flush=True)
    return {"k_star": ks, "ajustes": fits}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-05-03" if a.periodo == "fumaca" else "2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may))
    lc = np.log(kl.close.values.astype(float)); r_all = np.diff(lc, prepend=np.nan)
    h = (ts.dt.hour * 60 + ts.dt.minute).to_numpy(); s = np.full(1440, np.nan)
    for hh in range(1440):
        sel = may & (h == hh) & np.isfinite(r_all)
        if sel.any(): s[hh] = np.sqrt(np.mean(r_all[sel] ** 2))
    s = np.where(np.isfinite(s), s, np.nanmedian(s)); ker = np.ones(31) / 31
    s = np.real(np.fft.ifft(np.fft.fft(s) * np.fft.fft(np.roll(np.r_[ker, np.zeros(1440 - 31)], -15))))   # média móvel circular de 31 min
    idx = np.concatenate(GR.semanas(ts, ini, fim)); r = (r_all / s[h])[idx]; r = r[np.isfinite(r)]
    if a.periodo == "fumaca": r = r[:5000]
    sig = float(np.std(r)); out = {"periodo": a.periodo, "n": int(len(r))}
    for nome, (k, seed) in VALID.items():
        out[nome] = selecionar(gerar(k, seed, len(r), sig, **PARAMS_VALID), f"validação {nome} (k gerador {k})"); out[nome]["k_gerador"] = k
    out["real"] = selecionar(r, "real")
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    valido = all(out[n]["k_star"] == out[n]["k_gerador"] for n in VALID); ks = out["real"]["k_star"]
    cls = "INCONCLUSIVO" if not valido else ("escada fica de pé" if ks >= 4 else ("cai para três" if ks == 3 else "menos que três"))
    out.update(validacao=valido, classe=cls)
    best = out["real"]["ajustes"][ks - 1]
    print(f"\n== MSM [{a.periodo}] validação {valido}; real k* = {ks} → {cls}")
    print(f"  real k*: m0 {best['m0']:.3f} b {best['b']:.2f} γ_k {best['gamma_k']:.3f} ν {best['nu']:.2f} · escalas (min): {[round(e, 1) for e in best['escalas_min']]}")
    print("  ΔBIC real (k→k+1):", [round(out["real"]["ajustes"][i]["bic"] - out["real"]["ajustes"][i + 1]["bic"], 1) for i in range(4)])
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"msm_v3_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
