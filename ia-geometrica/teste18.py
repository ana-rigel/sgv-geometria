"""Teste 18 (a régua sobre outro observador). Predição: PREDICAO_teste18_regua_sobre_outro.md."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import lfilter, csd, welch
from scipy.optimize import brentq
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste18_regua_sobre_outro.md").exists(), "sem predição, sem teste"
N, SEEDS, NPER = 200000, range(1000, 1100), 8192


# ---- os observadores Ω: (nome, função que produz y limpo, ganho analítico |H(f)|², ruído na saída)
def ema(lam): return lambda x: lfilter([lam], [1, -(1 - lam)], x, axis=0)
def g2_ema(lam): return lambda f: lam ** 2 / (1 - 2 * (1 - lam) * np.cos(2 * np.pi * f) + (1 - lam) ** 2)
def mm(W): return lambda x: lfilter(np.ones(W) / W, [1.0], x, axis=0)
def g2_mm(W): return lambda f: np.where(f > 0, (np.sin(np.pi * f * W) / (W * np.sin(np.pi * f) + 1e-18)) ** 2, 1.0)
OMEGAS = {"ema_0.3": (ema(0.3), g2_ema(0.3), 0.0), "ema_0.03": (ema(0.03), g2_ema(0.03), 0.0), "ema_0.003": (ema(0.003), g2_ema(0.003), 0.0),
          "cascata_0.03": (lambda x: ema(0.03)(ema(0.03)(x)), lambda f: g2_ema(0.03)(f) ** 2, 0.0), "media_movel_50": (mm(50), g2_mm(50), 0.0),
          "ema_0.03_ruido_0.2": (ema(0.03), g2_ema(0.03), 0.2)}
MUNDOS = {"escada-3": lambda s: V.mundo_escada(N, s, [7, 70, 700]), "deriva": lambda s: V.mundo_deriva(N, s, 0.9)}


def fc_verdade(g2):
    return brentq(lambda f: g2(f) - 0.5, 1e-6, 0.5 - 1e-6)


def regua(x, y):
    """Ĥ = S_yx / S_xx por Welch (soma das coordenadas); corte estimado, cegueira estimada, cobertura."""
    Sxx = 0; Syx = 0; Syy = 0
    for d in range(x.shape[1]):
        f, pxx = welch(x[:, d], nperseg=NPER, window="hann"); _, pyx = csd(y[:, d], x[:, d], nperseg=NPER, window="hann"); _, pyy = welch(y[:, d], nperseg=NPER, window="hann")
        Sxx = Sxx + pxx; Syx = Syx + pyx; Syy = Syy + pyy
    H2 = np.minimum(np.abs(Syx) ** 2 / np.maximum(Sxx, 1e-18) ** 2, 1.0); coh = np.abs(Syx) ** 2 / np.maximum(Sxx * Syy, 1e-18)
    m = f > 0; cruz = np.where(H2[m] < 0.5)[0]; fc = float(f[m][cruz[0]]) if len(cruz) else float("nan")
    beta = float((Sxx[m] * (1 - H2[m])).sum() / Sxx[m].sum()); cob = float(Sxx[m][coh[m] >= 0.5].sum() / Sxx[m].sum())
    return fc, beta, cob


def main():
    out = {}; fcs = {k: fc_verdade(g2) for k, (_, g2, _) in OMEGAS.items()}
    for mnome, gen in MUNDOS.items():
        out[mnome] = {}
        for onome, (fun, g2, sig) in OMEGAS.items():
            acerta, erros, cobs, fcs_est = 0, [], [], []
            for s in SEEDS:
                x = gen(s); rng = np.random.default_rng(s + 99); y_limpo = fun(x); y = y_limpo + (rng.normal(0, sig, x.shape) if sig else 0)
                fc_est, beta_est, cob = regua(x, y); beta = float(np.mean(np.sum((x - y_limpo) ** 2, axis=1)) / np.mean(np.sum((x - x.mean(0)) ** 2, axis=1)))
                ok = bool(np.isfinite(fc_est) and abs(fc_est / fcs[onome] - 1) <= 0.3); acerta += ok; erros.append(abs(beta_est - beta)); cobs.append(cob); fcs_est.append(fc_est)
            out[mnome][onome] = {"fc_verdade": fcs[onome], "fc_est_mediano": float(np.nanmedian(fcs_est)), "acerta_fc": acerta, "erro_beta_mediano": float(np.median(erros)), "cobertura_mediana": float(np.median(cobs))}
            print(f"  {mnome} / {onome}: f_c {fcs[onome]:.2e} est {np.nanmedian(fcs_est):.2e} | acerta {acerta}/100 | |β̂−β| mediano {np.median(erros):.3f} | cobertura {np.median(cobs):.2f}", flush=True)
    a = all(out["escada-3"][o]["acerta_fc"] >= 80 for o in OMEGAS); b = all(out["escada-3"][o]["erro_beta_mediano"] <= 0.05 for o in OMEGAS)
    out["criterio"] = {"a_corte": bool(a), "b_cegueira": bool(b), "passa": bool(a and b)}
    print(f"\n== teste 18: (a) corte {a} (b) cegueira {b} → {'PASSA' if a and b else 'REPROVA'}")
    (ROOT / "resultados_teste18.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
