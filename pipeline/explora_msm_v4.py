"""MSM v4: relógio de volume (barras de volume igual), k = 1…5, sem M. Previsão: PREDICAO_msm_v4_tempo_volume.md.
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
    if not (1 < m0 < 2 and 1.01 < b < 50 and 1e-3 < gk < 0.999 and 2.1 < nu < 50): return 1e18
    gam, fator, P = estrutura(k, m0, b, gk); vol = sig * fator * np.sqrt((nu - 2) / nu)   # v2: t padronizada (variância 1)
    dens = student.pdf(r[:, None] / vol[None, :], nu) / vol[None, :]
    p = np.full(len(vol), 1 / len(vol)); ll = 0.0
    for t in range(len(r)):
        w = (p @ P) * dens[t]; s = w.sum()
        if s <= 0: return 1e18
        ll += np.log(s); p = w / s
    return -ll


def ajustar(r, k):
    sig = float(np.std(r)); best = None
    for x0 in ([1.4, 3.0, 0.5, 4.0], [1.6, 5.0, 0.2, 3.0]):
        res = minimize(loglik, x0, args=(r, k, sig), method="Nelder-Mead", options={"maxfev": 300, "xatol": 1e-3, "fatol": 0.5})
        if best is None or res.fun < best.fun: best = res
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
    idx = np.concatenate(GR.semanas(ts, ini, fim)); close = kl.close.values.astype(float)[idx]; vol = kl.volume.values.astype(float)[idx]
    vstar = 2.0 * float(np.mean(vol)); acc = 0.0; fins = []
    for i, v in enumerate(vol):
        acc += v
        if acc >= vstar: fins.append(i); acc = 0.0
    fins = np.array(fins); lc = np.log(close[fins]); r = np.diff(lc); r = r[np.isfinite(r)]
    dur = np.diff(np.r_[-1, fins]); frac1 = float(np.mean(dur == 1)); dur_media = float(np.mean(dur))
    print(f"  barras de volume: {len(fins)} (V* = {vstar:.1f}; duração média {dur_media:.2f} min; fração de 1 min {frac1:.2f})", flush=True)
    if a.periodo == "fumaca": r = r[:5000]
    sig = float(np.std(r)); out = {"periodo": a.periodo, "n": int(len(r)), "relogio": "volume", "v_star": vstar, "duracao_media_min": dur_media, "fracao_1min": frac1}
    for nome, (k, seed) in VALID.items():
        out[nome] = selecionar(gerar(k, seed, len(r), sig, **PARAMS_VALID), f"validação {nome} (k gerador {k})"); out[nome]["k_gerador"] = k
    out["real"] = selecionar(r, "real")
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    valido = all(out[n]["k_star"] == out[n]["k_gerador"] for n in VALID); ks = out["real"]["k_star"]
    cls = "INCONCLUSIVO" if not valido else ("escada intacta" if ks >= 4 else "relógio de volume encolhe a escada")
    out.update(validacao=valido, classe=cls)
    best = out["real"]["ajustes"][ks - 1]
    print(f"\n== MSM [{a.periodo}] validação {valido}; real k* = {ks} → {cls}")
    print(f"  real k*: m0 {best['m0']:.3f} b {best['b']:.2f} γ_k {best['gamma_k']:.3f} ν {best['nu']:.2f} · escalas (barras): {[round(e, 1) for e in best['escalas_min']]}")
    print("  ΔBIC real (k→k+1):", [round(out["real"]["ajustes"][i]["bic"] - out["real"]["ajustes"][i + 1]["bic"], 1) for i in range(4)])
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"msm_v4_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
