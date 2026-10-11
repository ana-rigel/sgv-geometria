#!/usr/bin/env python3
"""SGV-M20b: matched Gaussian marginals + all-lag linear autocovariances,
yet distinct higher-order transition copulas. Synthetic only.

Run: python experiments/m20b_dependencia_ordem_superior.py --mode full
Fixed preregistered thresholds, no parameter search or BTC data access.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261011
ETA = 0.43
C = 2.0 * math.exp(-1.5)
RHO = 0.7
FULL_N = 1800
FULL_CAL = 280
FULL_EVAL = 200
PRIMARY = "fourier_hsic"
STATS = ("fourier_hsic", "lag_cov", "lag_abs", "lag_square", "lag_sign",
         "lag_hermite3", "oracle_h", "static_mean", "static_var")


def h(x):
    return np.sin(2.0 * x) - C * np.sin(x)


def theoretical_checks():
    """Gauss-Hermite integration verifies low-order orthogonality."""
    pts, wgts = np.polynomial.hermite.hermgauss(100)
    x, w = pts * math.sqrt(2.0), wgts / math.sqrt(math.pi)
    hx = h(x)
    integrals = {
        "E_h": float(np.dot(w, hx)),
        "E_xh": float(np.dot(w, x * hx)),
        "E_x2h": float(np.dot(w, x*x*hx)),
        "E_absh": float(np.dot(w, np.abs(x)*hx)),
        "E_h2": float(np.dot(w, hx*hx)),
    }
    lower_bound = 1.0 - abs(ETA)*(1+C)**2
    return {"integrals":integrals,"transition_lower_bound":lower_bound,
            "pass": lower_bound > 0.0 and
                    all(abs(integrals[k]) < 1e-10
                        for k in ("E_h", "E_xh", "E_x2h", "E_absh"))}


def gen_hidden(n: int, eta: float, rng: np.random.Generator):
    """Sample exact rank-one Markov kernel via rejection from N(0,1).

    For current x, proposal y~phi. Envelope = 1+|eta*h(x)|*(1+C).
    Since kernel factor = 1+eta*h(x)*h(y), accept with ratio
    factor/envelope. Initialization x0~phi is EXACTLY stationary.
    """
    x = np.empty(n, dtype=float)
    x[0] = rng.standard_normal()
    for t in range(1, n):
        hx = float(h(x[t-1]))
        envelope = 1.0 + abs(eta*hx)*(1.0+C)
        while True:
            proposal = rng.standard_normal()
            acceptance = (1.0 + eta*hx*float(h(proposal)))/envelope
            if rng.random() < acceptance:
                x[t] = proposal
                break
    return x


def generate(n: int, kind: str, rng: np.random.Generator):
    x = rng.standard_normal((n, 3))
    if kind == "null":
        return x
    if kind in ("hidden_plus", "hidden_minus"):
        eta = ETA if kind == "hidden_plus" else -ETA
        x[:, 0] = gen_hidden(n, eta, rng)
    elif kind == "volatility_memory":
        z = np.empty(n, dtype=float)
        z[0] = rng.standard_normal()
        eps = rng.standard_normal(n)
        for t in range(1, n):
            z[t] = RHO*z[t-1] + math.sqrt(1-RHO*RHO)*eps[t]
        signs = 2*rng.integers(0,2,size=n)-1
        x[:,0] = signs*z
    else:
        raise ValueError("Unknown scenario: "+kind)
    return x


def cov1(a, b):
    return float(np.mean((a-a.mean())*(b-b.mean())))


def features(x):
    return np.stack([f(k*x) for k in (1,2,3)
                     for f in (np.sin,np.cos)], axis=1)


def scores(x: np.ndarray):
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 100:
        raise ValueError("Need >=100 3D observations")
    u = x[:, 0]
    a, b = u[:-1], u[1:]
    fa, fb = features(a), features(b)
    fa -= fa.mean(axis=0)
    fb -= fb.mean(axis=0)
    m = len(a)
    cross = (fa.T @ fb)/m
    mid = len(u)//2
    herm = lambda z: z*z*z-3.0*z
    out = {
        "fourier_hsic":float(np.sum(cross*cross)),
        "lag_cov":abs(cov1(a,b)),
        "lag_abs":abs(cov1(np.abs(a),np.abs(b))),
        "lag_square":abs(cov1(a*a,b*b)),
        "lag_sign":abs(cov1(np.sign(a),np.sign(b))),
        "lag_hermite3":abs(cov1(herm(a),herm(b))),
        "oracle_h":abs(cov1(h(a),h(b))),
        "static_mean":abs(float(np.mean(u[:mid])-np.mean(u[mid:]))),
        "static_var":abs(float(np.var(u[:mid])-np.var(u[mid:]))),
    }
    if not all(np.isfinite(v) for v in out.values()):
        raise FloatingPointError("Non-finite statistic")
    return out


def wilson(k: int, n: int):
    z = 1.95996398454
    p = k/n
    denom = 1+z*z/n
    ctr = (p+z*z/(2*n))/denom
    rad = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return [round(max(0,ctr-rad),4),round(min(1,ctr+rad),4)]


def experiment(mode="full"):
    pilot = mode == "pilot"
    n = 450 if pilot else FULL_N
    n_cal = 16 if pilot else FULL_CAL
    n_eval = 16 if pilot else FULL_EVAL
    rng = np.random.default_rng(SEED + (1 if pilot else 0))
    checks = theoretical_checks()
    if not checks["pass"]:
        raise RuntimeError("Failed mathematical stationarity gate")
    calibration = [scores(generate(n, "null", rng)) for _ in range(n_cal)]
    thresholds = {s:float(np.quantile([r[s] for r in calibration],
                                     .95, method="higher")) for s in STATS}
    groups = {}
    for name in ("null", "hidden_plus", "hidden_minus", "volatility_memory"):
        vals = [scores(generate(n, name, rng)) for _ in range(n_eval)]
        groups[name]={}
        for s in STATS:
            k = sum(int(v[s]>thresholds[s]) for v in vals)
            groups[name][s] = {
                "n":n_eval,"alarms":k,"rate":round(k/n_eval,4),
                "wilson95":wilson(k,n_eval),
                "mean":round(float(np.mean([v[s] for v in vals])),7),
            }
    rate = lambda g,s: groups[g][s]["rate"]
    gates = {
        "G1_analytic_kernel_valid":checks["pass"],
        "G2_primary_fpr_le_10pct":rate("null",PRIMARY)<=.10,
        "G3_positive_hidden_power_ge_80pct":rate("hidden_plus",PRIMARY)>=.80,
        "G3_negative_hidden_power_ge_80pct":rate("hidden_minus",PRIMARY)>=.80,
        "G4_linear_abs_square_controls_blind":all(
            rate(g,s)<=.15
            for g in ("hidden_plus","hidden_minus")
            for s in ("lag_cov","lag_abs","lag_square")),
        "G5_volatility_memory_lag_abs_power_ge_75pct":
            rate("volatility_memory","lag_abs")>=.75,
        "G6_oracle_power_ge_80pct":min(
            rate("hidden_plus","oracle_h"),
            rate("hidden_minus","oracle_h"))>=.80,
    }
    result={
        "protocol":"SGV-M20b higher-order coupling, preregistered synthetic only",
        "mode":mode,"seed":SEED+(1 if pilot else 0),
        "n_per_series":n,"n_null_calibration":n_cal,
        "n_per_evaluation_group":n_eval,
        "eta":ETA,"rho_volatility":RHO,"h_coefficient_c":C,
        "math_checks":checks,"thresholds_95pct":thresholds,
        "groups":groups,"gates":gates,"all_gates_pass":all(gates.values()),
        "interpretation":"Fourier feature HSIC is conventional nonlinear dependence; no novel geometry, no BTC, no claims of identification of unrestricted processes.",
        "error_control":"One-sided per-statistic calibration only. Multi-statistic exploratory comparisons lack familywise correction. Independent series are units.",
    }
    name="piloto.json" if pilot else "resultados_sinteticos.json"
    target=ROOT/"reports"/"m20b"/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"mode":mode,"gates":gates,"all_gates_pass":result["all_gates_pass"],
                      "summary":{g:{s:round(r["rate"]*100,2) for s,r in stats.items()}
                                 for g,stats in groups.items()}},ensure_ascii=False))
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("pilot","full"),default="full")
    experiment(parser.parse_args().mode)
