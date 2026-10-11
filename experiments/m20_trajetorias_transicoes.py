#!/usr/bin/env python3
"""SGV-M20a: synthetic, pre-registered test of geometry of distribution paths
and transition couplings. NO BTC DATA, GMM, or future leakage.

Scientific distinction:
- p_t (distribution path): Gaussian moment proxy using W2/Bures;
- q(x_t,x_t+1) (temporal coupling): antisymmetric probability current;
- ordinary lagged covariance is an explicit comparator and can explain the current.
A path of identical marginals can conceal irreversible rotating dynamics.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261011
ALPHA = 0.65
BETA = 0.22
GAMMA = 0.65
STATS = ("endpoint_w2", "path_length", "transition_cost", "excess_cost",
         "current_abs", "lagcov_frobenius", "lagdiag_departure",
         "mean_shift", "cov_shift")


def system(beta: float = 0.0):
    """Stationary N(0,I) VAR, with same diagonal lag-one covariance for all beta.
    The xy block has nonreversible circulation if beta != 0.
    """
    a = np.array([[ALPHA, -beta, 0.0],
                  [beta, ALPHA, 0.0],
                  [0.0, 0.0, GAMMA]], dtype=float)
    q = np.eye(3) - a @ a.T
    if np.linalg.eigvalsh(q).min() <= 0:
        raise ValueError("Nonpositive innovation covariance")
    return a, q


def generate(n: int, beta: float, rng: np.random.Generator,
             drift: float = 0.0):
    """Stationary VAR started from its invariant distribution.
    Optional deterministic time-dependent translation changes p_t smoothly.
    """
    a, q = system(beta)
    x = np.empty((n, 3), dtype=float)
    state = rng.standard_normal(3)
    innovation = rng.standard_normal((n, 3)) @ np.linalg.cholesky(q).T
    for t in range(n):
        state = a @ state + innovation[t]
        x[t] = state
    if drift:
        x[:, 0] += drift * np.linspace(0.0, 1.0, n)
    return x


def covpop(x):
    centered = x - x.mean(axis=0)
    return (centered.T @ centered) / len(x)


def psd_sqrt(a):
    eig, vec = np.linalg.eigh((a + a.T) * 0.5)
    return (vec * np.sqrt(np.maximum(eig, 0.0))) @ vec.T


def gaussian_w2_sq(x, y):
    """Gaussian-moment W2^2 (Gelbrich/Bures lower bound for empirical OT).
    This is NOT the exact W2 of a non-Gaussian mixture or a flow estimator.
    """
    ma, mb = x.mean(axis=0), y.mean(axis=0)
    ca, cb = covpop(x), covpop(y)
    sca = psd_sqrt(ca)
    cross_sqrt = psd_sqrt(sca @ cb @ sca)
    val = float(np.sum((ma - mb) ** 2) + np.trace(ca + cb - 2 * cross_sqrt))
    return max(0.0, val)


def scores(x: np.ndarray, window: int = 256, step: int = 128):
    """Features computed only from observed trajectory in this trial.
    For overlapping rolling snapshots, path_length is descriptive, not iid.
    """
    n = len(x)
    if n < 2 * window or step <= 0:
        raise ValueError("Insufficient samples")
    mid = n // 2
    endpoint = float(np.sqrt(gaussian_w2_sq(x[:mid], x[mid:])))
    cuts = [x[i:i+window] for i in range(0, n-window+1, step)]
    path_length = float(sum(np.sqrt(gaussian_w2_sq(a, b))
                            for a, b in zip(cuts[:-1], cuts[1:])))
    before, after = x[:-1], x[1:]
    x0 = before - before.mean(axis=0)
    y0 = after - after.mean(axis=0)
    lag = (x0.T @ y0) / len(before)
    current = float(lag[0, 1] - lag[1, 0])
    kinetic = float(np.mean(np.sum((after-before)**2, axis=1)))
    # Each observed pair is a coupling of its empirical marginals.
    # Gaussian W2 is a lower bound to the true empirical transport cost.
    excess = float(kinetic - gaussian_w2_sq(before, after))
    return {
        "endpoint_w2": endpoint,
        "path_length": path_length,
        "transition_cost": kinetic,
        "excess_cost": excess,
        "current_abs": abs(current),
        "lagcov_frobenius": float(np.linalg.norm(lag-ALPHA*np.eye(3))),
        "lagdiag_departure": abs(float(np.trace(lag)/3-ALPHA)),
        "mean_shift": float(np.linalg.norm(x[mid:].mean(0)-x[:mid].mean(0))),
        "cov_shift": float(np.linalg.norm(covpop(x[mid:])-covpop(x[:mid]))),
        "signed_current": current,
    }


def wilson(k: int, n: int):
    if n == 0:
        return [None, None]
    z = 1.959963984540054
    p = k/n
    c = (p + z*z/(2*n)) / (1+z*z/n)
    r = z*np.sqrt((p*(1-p)+z*z/(4*n))/n)/(1+z*z/n)
    return [round(max(0.0, c-r), 4), round(min(1.0, c+r), 4)]


def _batch(count: int, n: int, beta: float, drift: float,
           rng: np.random.Generator):
    results = []
    for _ in range(count):
        results.append(scores(generate(n, beta, rng, drift)))
    return results


def run(mode="full"):
    pilot = mode == "pilot"
    n = 640 if pilot else 1200
    n_cal = 24 if pilot else 320
    n_eval = 24 if pilot else 240
    rng = np.random.default_rng(SEED + (1 if pilot else 0))
    cal = _batch(n_cal, n, 0.0, 0.0, rng)
    # These are independent of calibration; evaluation is not tuned afterward.
    groups = {
        "null": _batch(n_eval, n, 0.0, 0.0, rng),
        "rotation_positive": _batch(n_eval, n, BETA, 0.0, rng),
        "rotation_negative": _batch(n_eval, n, -BETA, 0.0, rng),
        "smooth_drift": _batch(n_eval, n, 0.0, 1.4, rng),
    }
    threshold = {s: float(np.quantile([a[s] for a in cal],
                                     0.95, method="higher"))
                 for s in STATS}
    outputs = {}
    for group, records in groups.items():
        outputs[group] = {}
        for s in STATS:
            count = sum(int(r[s] > threshold[s]) for r in records)
            outputs[group][s] = {
                "alarms": count,
                "n": len(records),
                "rate": round(count/len(records), 4),
                "wilson95": wilson(count, len(records)),
                "mean": round(float(np.mean([r[s] for r in records])), 6),
            }
        outputs[group]["signed_current_mean"] = round(
            float(np.mean([r["signed_current"] for r in records])), 6)
    fpr = outputs["null"]["current_abs"]["rate"]
    powers = [outputs[g]["current_abs"]["rate"]
              for g in ("rotation_positive", "rotation_negative")]
    static = [outputs[g]["endpoint_w2"]["rate"]
              for g in ("rotation_positive", "rotation_negative")]
    path = [outputs[g]["path_length"]["rate"]
            for g in ("rotation_positive", "rotation_negative")]
    drift_detect = outputs["smooth_drift"]["endpoint_w2"]["rate"]
    gate = {
        "E1_stationarity_algebraic": bool(np.allclose(
            system(BETA)[0] @ system(BETA)[0].T + system(BETA)[1],
            np.eye(3), atol=1e-12)),
        "E2_current_fpr_le_10pct": fpr <= 0.10,
        "E2_both_rotation_power_ge_80pct": min(powers) >= 0.80,
        "E2_static_blind_le_15pct": max(static) <= 0.15,
        "E3_smooth_drift_w2_power_ge_80pct": drift_detect >= 0.80,
    }
    result = {
        "protocol": "SGV-M20a; synthetic mechanism demonstration ONLY",
        "seed": SEED, "mode": mode,
        "n_observations": n,
        "n_null_calibration": n_cal, "n_per_evaluation_group": n_eval,
        "parameters": {"alpha": ALPHA, "beta_abs": BETA,
                       "gamma": GAMMA, "smooth_drift": 1.4},
        "one_sided_thresholds_95pct": threshold,
        "results": outputs,
        "gate": gate,
        "all_gates_pass": all(gate.values()),
        "explanation": {
            "static_W2": "Gaussian-moment proxy, not exact mixture/empirical OT",
            "current": "antisymmetric lag-one cross covariance; not novel vs ordinary lagged covariance",
            "excess": "Observed pair cost minus Gaussian marginal OT lower bound; can be blind to rotational circulation",
            "pvalues": "none; held-out empirical alarm rates with Wilson intervals",
            "multiplicity": "primary gate predeclared; other measures descriptive; no claim of familywise error control",
            "btc": "no BTC files loaded and no held-out periods touched",
        },
    }
    out = ROOT/"reports"/"m20"/("piloto.json" if pilot else "resultados_sinteticos.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("pilot","full"), default="full")
    args = ap.parse_args()
    run(args.mode)
