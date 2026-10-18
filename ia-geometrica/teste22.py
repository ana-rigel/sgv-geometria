"""Teste 22 (OBS-01 etapa um: a régua sobre uma rede recorrente sintética). Predição: PREDICAO_teste22_rnn_sintetica.md."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import lfilter, csd, welch

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste22_rnn_sintetica.md").exists(), "sem predição, sem teste"
N, SEEDS, NPER, NH = 200000, range(1000, 1100), 8192, 32


def mundo(seed):
    rng = np.random.default_rng(seed); x = np.zeros(N)
    for tau in (7, 70, 700):
        phi = 1 - 1 / tau; e = rng.normal(0, 1.0, N) * np.sqrt(1 - phi ** 2); x += lfilter([1.0], [1, -phi], e)
    return x


def rede(seed):
    rng = np.random.default_rng(seed + 500); a = np.exp(rng.uniform(np.log(0.003), np.log(0.3), NH))
    W = rng.normal(0, 1, (NH, NH)); W *= 0.5 / max(abs(np.linalg.eigvals(W))); u = rng.normal(0, 1, NH); r = rng.normal(0, 1, NH) / np.sqrt(NH)
    return a, W, u, r


def rodar_rede(x, a, W, u, r, phi):
    h = np.zeros(NH); y = np.zeros(len(x)); A = (1 - a)
    for t in range(len(x)):
        h = A * h + a * phi(W @ h + u * x[t]); y[t] = r @ h
    return y


def H_verdade(a, W, u, r, f):
    out = np.zeros(len(f), dtype=complex); I = np.eye(NH)
    for k, fk in enumerate(f):
        z = np.exp(-2j * np.pi * fk); M = I - np.diag(1 - a) * z - (a[:, None] * W) * z
        out[k] = r @ np.linalg.solve(M, a * u)
    return out


def regua(x, y):
    f, Sxx = welch(x, nperseg=NPER, window="hann"); _, Syx = csd(y, x, nperseg=NPER, window="hann"); _, Syy = welch(y, nperseg=NPER, window="hann")
    m = f > 0; f, Sxx, Syx, Syy = f[m], Sxx[m], Syx[m], Syy[m]
    H = Syx / np.maximum(Sxx, 1e-18); coh = np.abs(Syx) ** 2 / np.maximum(Sxx * Syy, 1e-18)
    return f, Sxx, H, coh


def medidas(f, Sxx, H):
    Ht = H / max(abs(H[0]), 1e-12); H2 = np.minimum(np.abs(Ht) ** 2, 1.0); cruz = np.where(H2 < 0.5)[0]
    fc = float(f[cruz[0]]) if len(cruz) else float("nan")
    nu = float((Sxx * (1 - H2)).sum() / Sxx.sum()); eps = float((Sxx * np.abs(1 - Ht) ** 2).sum() / Sxx.sum()); return fc, nu, eps


VERSOES = {"linear": (lambda z: z, 1.0), "tanh_pequena": (np.tanh, 0.1), "tanh_grande": (np.tanh, 3.0)}


def main():
    acc = {v: {"ok": 0, "e_nu": [], "e_eps": [], "cob": [], "fc_v": [], "fc_e": [], "nu_e": []} for v in VERSOES}
    for s in SEEDS:
        x = mundo(s); a, W, u, r = rede(s)
        for v, (phi, esc) in VERSOES.items():
            y = rodar_rede(esc * x, a, W, u, r, phi); f, Sxx, H, coh = regua(x, y); fc_e, nu_e, eps_e = medidas(f, Sxx, H)
            Hv = H_verdade(a, W, u, r, f); fc_v, nu_v, eps_v = medidas(f, Sxx, Hv)   # verdade (linear ou linearizada)
            q = acc[v]; q["ok"] += bool(np.isfinite(fc_e) and np.isfinite(fc_v) and abs(fc_e / fc_v - 1) <= 0.3); q["e_nu"].append(abs(nu_e - nu_v)); q["e_eps"].append(abs(eps_e - eps_v))
            q["cob"].append(float(Sxx[coh >= 0.5].sum() / Sxx.sum())); q["fc_v"].append(fc_v); q["fc_e"].append(fc_e); q["nu_e"].append(nu_e)
        if (s - 1000) % 10 == 0: print(f"  s{s} ok", flush=True)
    out = {}
    for v in VERSOES:
        q = acc[v]; out[v] = {"acerta_fc": q["ok"], "erro_nu_mediano": float(np.median(q["e_nu"])), "erro_eps_mediano": float(np.median(q["e_eps"])), "cobertura_mediana": float(np.median(q["cob"])),
                              "fc_verdade_mediano": float(np.nanmedian(q["fc_v"])), "fc_est_mediano": float(np.nanmedian(q["fc_e"])), "nu_est_mediano": float(np.median(q["nu_e"])),
                              "dentro_tolerancias": int(sum(1 for i in range(len(q["e_nu"])) if q["e_nu"][i] <= 0.05 and q["e_eps"][i] <= 0.05 and np.isfinite(q["fc_e"][i]) and np.isfinite(q["fc_v"][i]) and abs(q["fc_e"][i] / q["fc_v"][i] - 1) <= 0.3))}
        print(f"  {v}: corte {q['ok']}/100 (verdade {np.nanmedian(q['fc_v']):.2e}, est {np.nanmedian(q['fc_e']):.2e}) | |ν̂−ν| {np.median(q['e_nu']):.3f} | |ε̂−ε| {np.median(q['e_eps']):.3f} | cobertura {np.median(q['cob']):.2f} | nos três em {out[v]['dentro_tolerancias']}", flush=True)
    L = out["linear"]; passa = L["acerta_fc"] >= 80 and L["erro_nu_mediano"] <= 0.05 and L["erro_eps_mediano"] <= 0.05
    out["criterio"] = {"a_corte": bool(L["acerta_fc"] >= 80), "b_nao_ver": bool(L["erro_nu_mediano"] <= 0.05), "c_errar": bool(L["erro_eps_mediano"] <= 0.05), "passa": bool(passa)}
    print(f"\n== teste 22 (rede linear): {'PASSA' if passa else 'REPROVA'}")
    (ROOT / "resultados_teste22.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
