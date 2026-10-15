"""SGV saltos × memoria V2: controles sinteticos de mecanismos conhecidos.

Executar somente DEPOIS de registrar PREDICAO_saltos_markov_V2.md.
Nao acessa dados financeiros, nem importacoes do pipeline SGV.
Teste A: escalonamento do momento 4, nao curtose em uma escala.
Teste B: correlacao de agitacao com historia usando volatilidade verdadeira e proxy causal.
Nenhum dos dois prova por si so Markov, Pawula ou saltos de mercado.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
from scipy.signal import lfilter
from scipy.stats import spearmanr
import scipy

SEED = 20261015
DT0 = 0.125
DURATION = 2048
N_PATHS_A = 32
SCALES = (0.125, 0.25, 0.5, 1.0)
LAMBDA = 0.3
JUMP_SD = 0.8
N_PATHS_B = 24
N_B = 12000
BURN = 1000
PHI = 0.2
RHO = 0.995
TAU = 1.0
B = 1000
THEORY_JUMP_M4_PER_DT = LAMBDA * 3.0 * JUMP_SD**4


def generate_a(seed: int):
    """Brownian increments paired with compound-Poisson increments."""
    rng = np.random.default_rng(seed)
    n = int(round(DURATION / DT0))
    t = np.arange(n) * DT0
    sigma2 = .25 * (1 + .5 * np.sin(2 * np.pi * t / 83)**2)
    brownian = np.sqrt(sigma2 * DT0) * rng.standard_normal(n)
    counts = rng.poisson(LAMBDA * DT0, size=n)
    js = np.zeros(n)
    total = int(counts.sum())
    if total:
        js = np.bincount(np.repeat(np.arange(n), counts),
                         weights=rng.normal(0, JUMP_SD, total),
                         minlength=n).astype(float)
    return brownian, brownian + js, total


def m4_dt(increments: np.ndarray) -> np.ndarray:
    values = []
    for h in SCALES:
        stride = int(round(h / DT0))
        if not np.isclose(stride * DT0, h):
            raise ValueError("scale is not divisible by dt0")
        dx = increments.reshape(-1, stride).sum(axis=1)
        values.append(float(np.mean(dx**4) / h))
    return np.array(values)


def intercept(y: np.ndarray) -> np.ndarray:
    """OLS intercept for shape (4,) or (n,4). Exploratory finite-scale proxy."""
    t = np.asarray(SCALES)
    X = np.column_stack([np.ones(len(t)), t])
    weights = np.linalg.pinv(X)[0]
    return np.asarray(y) @ weights


def ci_bootstrap(samples: np.ndarray, seed: int, nboot: int = B) -> list[float]:
    """Bootstrap only whole independent trajectories, never adjacent steps."""
    vals = np.asarray(samples, float)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(vals), size=(nboot, len(vals)))
    means = vals[indices].mean(axis=1)
    return np.quantile(means, [0.025, 0.975]).tolist()


def run_a() -> dict:
    diff, jump, counts = [], [], []
    for i in range(N_PATHS_A):
        a, c, n = generate_a(SEED * 100 + i)
        diff.append(m4_dt(a))
        jump.append(m4_dt(c))
        counts.append(n)
    diff, jump = np.asarray(diff), np.asarray(jump)
    intercept_diff = intercept(diff)
    intercept_jump = intercept(jump)
    ci_d = ci_bootstrap(intercept_diff, 202610151)
    ci_j = ci_bootstrap(intercept_jump, 202610151)
    d, j = float(intercept_diff.mean()), float(intercept_jump.mean())
    gates = {
        "continuous_near_zero": abs(d) < 0.06 and ci_d[0] <= 0 <= ci_d[1],
        "jump_positive": j > 0.15 and ci_j[0] > 0.10,
        "jump_close_to_theory": abs(j - THEORY_JUMP_M4_PER_DT) < 0.15,
    }
    return {
        "n_paths": N_PATHS_A, "n_steps_per_path": int(DURATION / DT0),
        "base_dt": DT0, "scales": list(SCALES),
        "continuous_m4_per_dt": diff.mean(axis=0).tolist(),
        "jump_m4_per_dt": jump.mean(axis=0).tolist(),
        "continuous_intercept": d, "continuous_ci95": ci_d,
        "jump_intercept": j, "jump_ci95": ci_j,
        "theoretical_jump_limit": THEORY_JUMP_M4_PER_DT,
        "count_total_jumps": int(sum(counts)),
        "gates": {k: bool(v) for k, v in gates.items()},
    }


def generate_b(seed: int, latent: bool) -> dict:
    """Known AR(1) stochastic-volatility state with oracle h_t."""
    rng = np.random.default_rng(seed)
    n = N_B + BURN
    eta = rng.standard_normal(n)
    eps = rng.standard_normal(n)
    h = np.zeros(n + 1)
    h[0] = rng.normal(0, TAU) if latent else 0.
    if latent:
        for t in range(n):
            h[t + 1] = RHO * h[t] + TAU * np.sqrt(1 - RHO**2) * eta[t]
    r = np.exp(h[:n] / 2) * eps
    x = lfilter([1.], [1., -PHI], r)
    # same t indexing: r[t] is the change x[t+1]-phi*x[t].
    return {"resid": r[BURN:], "h": h[BURN:n], "x": x[BURN:]}


def past_mean(values: np.ndarray, n: int) -> np.ndarray:
    """At index t, mean strictly of values[t-n:t]. Never include t or future."""
    x = np.asarray(values, float)
    cs = np.concatenate(([0.], np.cumsum(x)))
    out = np.full(len(x), np.nan)
    out[n:] = (cs[n:-1] - cs[:-n-1]) / n
    return out


def memory_correlation(values: np.ndarray) -> float:
    past10 = past_mean(values, 10)
    ok = np.isfinite(values) & np.isfinite(past10)
    if ok.sum() < 100:
        raise ValueError("too few memory observations")
    return float(spearmanr(values[ok], past10[ok]).correlation)


def evaluate_b(d: dict) -> dict:
    r, h = d["resid"], d["h"]
    e2 = r**2
    unconditional = np.exp((TAU**2) / 2) if np.any(h != 0) else 1.0
    sem = e2 / unconditional
    proxy_var = past_mean(e2, 60)
    proxy = e2 / np.maximum(proxy_var, 1e-10)
    oracle = e2 / np.exp(h)
    # Common indices; proxy requires 60 lagged values, all require 10 preceding.
    start = 70
    out = {
        "M_sem": memory_correlation(sem[start:]),
        "M_proxy": memory_correlation(proxy[start:]),
        "M_oracle": memory_correlation(oracle[start:]),
    }
    return out


def run_b() -> dict:
    groups = {"latent": [], "homoscedastic": []}
    for kind, latent in (("latent", True), ("homoscedastic", False)):
        for i in range(N_PATHS_B):
            d = generate_b(SEED * 200 + i, latent)
            groups[kind].append(evaluate_b(d))
    summary = {}
    for name, items in groups.items():
        detail = {}
        for j, key in enumerate(("M_sem", "M_proxy", "M_oracle")):
            v = np.array([x[key] for x in items])
            detail[key] = {
                "mean": float(v.mean()),
                "ci95": ci_bootstrap(v, 202610152 + j),
                "path_values": v.tolist(),
            }
        summary[name] = detail

    lat, homo = summary["latent"], summary["homoscedastic"]
    def has_zero(rec): return rec["ci95"][0] <= 0 <= rec["ci95"][1]
    gates = {
        "latent_memory_detected": lat["M_sem"]["mean"] > 0.20 and lat["M_sem"]["ci95"][0] > 0.10,
        "oracle_removes_known_memory": abs(lat["M_oracle"]["mean"]) < 0.05 and has_zero(lat["M_oracle"]),
        "causal_proxy_reduces_memory": lat["M_proxy"]["mean"] < lat["M_sem"]["mean"],
        "homoscedastic_control_zero": abs(homo["M_sem"]["mean"]) < 0.05 and has_zero(homo["M_sem"]),
        "homoscedastic_oracle_zero": abs(homo["M_oracle"]["mean"]) < 0.05 and has_zero(homo["M_oracle"]),
    }
    return {"n_paths": N_PATHS_B, "steps_per_path_after_burn": N_B,
            "rho": RHO, "tau": TAU, "phi": PHI,
            "groups": summary, "gates": {k: bool(v) for k, v in gates.items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    a, b = run_a(), run_b()
    gates = {**{"A_" + k: v for k, v in a["gates"].items()},
             **{"B_" + k: v for k, v in b["gates"].items()}}
    result = {"study": "saltos-markov-V2", "status": "VALIDATED_SYNTHETIC_CONTROLS" if all(gates.values())
              else "INCONCLUSIVE_INSTRUMENT", "market_data_used": False, "original_v1_unchanged": True,
              "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
              "A": a, "B": b, "gates": gates}
    payload = (json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(payload)
    print(json.dumps({"status": result["status"], "gates": gates,
                      "A": {"continuous": a["continuous_intercept"], "jump": a["jump_intercept"]},
                      "B_latent": {k: round(v["mean"], 4) for k, v in b["groups"]["latent"].items()},
                      "json_sha256": hashlib.sha256(payload).hexdigest()}, ensure_ascii=False))
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
