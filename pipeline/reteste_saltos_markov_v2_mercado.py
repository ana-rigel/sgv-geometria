"""V2b observational RE-ANALYSIS: June–September 2026 ALREADY EXAMINED.

Finite-scale raw-return diagnostics and causal previous-week AR(1)+SV surrogates.
Separate 3D state proxy-volatility memory: NOT a Chapman–Kolmogorov test.
No October and no reserved holdout; no interpretation as confirmatory.
Protocol: PROTOCOLO_saltos_markov_V2b_mercado.md.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR
import explora_saltos_markov as V1

SCALES = (1, 2, 4, 8)
SEEDS = {"G": (3026, 3027, 3028), "S": (2026, 2027, 2028)}
TRAIN_WEEK = 7 * 24 * 60
VOL_WINDOW = 60
VOL_PROXIES = (30, 60, 120)


def sha_seed(period: str, kind: str, seed: int, week: int) -> int:
    b = f"V2b|{period}|{kind}|{seed}|{week}".encode()
    return int.from_bytes(hashlib.sha256(b).digest()[:8], "big")


def finite_scales(r: np.ndarray) -> dict:
    """Non-overlapping minute log-returns; values are finite-scale only."""
    z = np.asarray(r, float)
    if len(z) < 100 or not np.isfinite(z).all():
        raise ValueError("short or nonfinite return series")
    out = {}
    for n in SCALES:
        nn = (len(z) // n) * n
        y = z[:nn].reshape(-1, n).sum(axis=1)
        moment2, moment4 = float(np.mean(y*y)), float(np.mean(y**4))
        if moment2 <= 1e-18:
            raise ValueError("zero variance")
        out[str(n)] = {"m4_per_min": moment4 / n,
                       "excess_kurtosis": moment4 / moment2**2 - 3,
                       "n_nonoverlap": int(nn/n)}
    return out


def past_std(r: np.ndarray, width: int) -> np.ndarray:
    """For index t includes ONLY returns at indices t-width .. t-1."""
    z = pd.Series(r, dtype=float).rolling(width, min_periods=max(15, width//2)).std().shift(1)
    return z.to_numpy(dtype=float)


def calibrate_prior_week(prev_returns: np.ndarray) -> dict:
    x = np.asarray(prev_returns, float)
    if len(x) < 500 or not np.isfinite(x).all():
        raise ValueError("previous week missing or invalid")
    X = np.column_stack([np.ones(len(x)-1), x[:-1]])
    a, phi = np.linalg.lstsq(X, x[1:], rcond=None)[0]
    # Clip only stationarity limits specified in this file; report clips.
    phi = float(np.clip(phi, -.98, .98))
    e = x[1:] - (a + phi*x[:-1])
    hp = 2*np.log(np.maximum(past_std(e, VOL_WINDOW), 1e-12))
    ok = np.isfinite(hp) & np.isfinite(e)
    hvals = hp[ok]
    if len(hvals) < 100:
        raise ValueError("no causal log volatility")
    u = e[ok] / np.exp(hvals/2)
    u = (u - u.mean()) / u.std()
    if not np.isfinite(u).all() or len(u) < 100:
        raise ValueError("invalid empirical shocks")
    mu = float(np.mean(hvals))
    H = np.column_stack([np.ones(len(hvals)-1), hvals[:-1]-mu])
    intercept, rho = np.linalg.lstsq(H, hvals[1:]-mu, rcond=None)[0]
    rho = float(np.clip(rho, 0, .995))
    eta_std = float(np.std(hvals[1:] - mu - intercept - rho*(hvals[:-1]-mu), ddof=1))
    if not np.isfinite(eta_std) or eta_std <= 0:
        raise ValueError("invalid latent-volatility model")
    return {"a":float(a), "phi":phi, "h_mu":mu+float(intercept), "h_rho":rho,
            "h_sd":eta_std, "last_h":float(hvals[-1]), "last_x":float(x[-1]),
            "empirical_innovations":u}


def simulate_week(model: dict, n: int, *, kind: str, seed: int) -> np.ndarray:
    if kind not in ("G", "S"):
        raise ValueError("unknown surrogate")
    rng = np.random.default_rng(seed)
    etas = rng.standard_normal(n)
    if kind == "G":
        shocks = rng.standard_normal(n)
    else:
        shocks = rng.choice(model["empirical_innovations"], size=n, replace=True)
    h = float(model["last_h"])
    xprev = float(model["last_x"])
    z = np.empty(n, float)
    for t in range(n):
        # h_t is available before the new shock, not inferred using future returns.
        z[t] = model["a"] + model["phi"]*xprev + np.exp(h/2)*shocks[t]
        xprev = z[t]
        h = model["h_mu"] + model["h_rho"]*(h-model["h_mu"]) + model["h_sd"]*etas[t]
    if not np.isfinite(z).all():
        raise ValueError("nonfinite synthetic return")
    return z


def run_a(kl: pd.DataFrame, ts: pd.Series, period: str, weeks: list) -> dict:
    r = np.diff(np.log(kl.close.to_numpy(float)), prepend=np.nan)
    per_week = []
    for k, te in enumerate(weeks):
        if len(te) < 500:
            raise ValueError("evaluation week too short")
        start = int(te[0])
        tr = np.arange(start-TRAIN_WEEK, start)
        if tr[0] < 1 or not np.isfinite(r[tr]).all():
            raise ValueError("prior causal training week absent")
        mdl = calibrate_prior_week(r[tr])
        row = {"week":k, "start_ms":int(kl.timestamp.iloc[te[0]]),
               "real":finite_scales(r[te]), "G":{}, "S":{},
               "train_n":len(tr), "eval_n":len(te),
               "fit":{key:float(mdl[key]) for key in
                      ("a","phi","h_mu","h_rho","h_sd")}}
        for kind in ("G","S"):
            for seed in SEEDS[kind]:
                z = simulate_week(mdl, len(te), kind=kind,
                                  seed=sha_seed(period,kind,seed,k))
                row[kind][str(seed)] = finite_scales(z)
        per_week.append(row)

    stats = {}
    for axis in SCALES:
        a = str(axis)
        rs = np.array([week["real"][a]["m4_per_min"] for week in per_week])
        stats[a] = {
            "real_median_m4_per_min":float(np.median(rs)),
            "real_median_excess_kurtosis":float(np.median([
                week["real"][a]["excess_kurtosis"] for week in per_week])),
        }
        for kind in ("G","S"):
            med = [float(np.median([week[kind][str(seed)][a]["m4_per_min"]
                                     for week in per_week])) for seed in SEEDS[kind]]
            stats[a][kind+"_median_m4_per_min_reps"] = med
    return {"status":"DESCRIPTIVE_FINITE_SCALES_ONLY",
            "weeks":len(per_week),"by_scale":stats,"details":per_week}


def causal_vol_proxy(kl: pd.DataFrame, may: np.ndarray, n: int) -> np.ndarray:
    lr = np.diff(np.log(kl.close.to_numpy(float)), prepend=np.nan)
    raw = np.log(np.maximum(past_std(lr,n), 1e-12))
    valid = may & np.isfinite(raw)
    if valid.sum() < 1000:
        raise ValueError("insufficient May anchor for causal volatility proxy")
    med = float(np.median(raw[valid]))
    scale = float(np.quantile(np.abs(raw[valid]-med), .995)/3)
    if scale <= 1e-12:
        raise ValueError("degenerate May anchor")
    return (raw-med)/scale


def run_b(kl: pd.DataFrame, may: np.ndarray, weeks: list) -> dict:
    G = GR.regua(GR.E.coords_orig(kl), may)
    baseline = V1.memoria(G, weeks, np.random.default_rng(20261020))
    if not np.isfinite(baseline) or abs(baseline) < 1e-9:
        raise ValueError("invalid/near-zero 3D baseline")
    out = {"M_3D":float(baseline), "proxies":{}}
    for n in VOL_PROXIES:
        proxy = causal_vol_proxy(kl, may, n)
        val = float(V1.memoria(np.column_stack([G, proxy]),
                              weeks, np.random.default_rng(20261020)))
        out["proxies"][str(n)] = {
            "M_4D":val, "Red":float(1 - val/baseline),
        }
    return out


def run(period: str, data_dir: str) -> dict:
    if period not in ("junjul", "agoset"):
        raise ValueError("only spent/exploratory periods are allowed")
    months, start, end = GR.PERIODOS[period]
    kl = GR.E.carregar(months, Path(data_dir))
    ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    if ts.iloc[-1] >= pd.Timestamp("2026-10-01", tz="UTC"):
        raise ValueError("October or later data forbidden")
    may = (ts < pd.Timestamp("2026-06-01",tz="UTC")).to_numpy()
    weeks = GR.semanas(ts,start,end)
    if not weeks:
        raise ValueError("no evaluation weeks")
    a = run_a(kl,ts,period,weeks)
    b = run_b(kl,may,weeks)
    return {"period":period,"status":"EXPLORATORY_REANALYSIS_ONLY",
            "test_data_unseen":False,"october_accessed":False,
            "no_Pawula_or_Markov_classification":True,
            "test_A":a,"test_B":b}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--periodo",choices=("junjul","agoset"),required=True)
    p.add_argument("--dados",default=str(ROOT/"dados"))
    args = p.parse_args()
    result=run(args.periodo,args.dados)
    out=ROOT/"resultados"/f"saltos_markov_v2b_{args.periodo}.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode()
    out.write_bytes(data)
    print(json.dumps({"period":args.periodo,"status":result["status"],
                      "test_B":result["test_B"],
                      "test_A":result["test_A"]["by_scale"],
                      "sha256":hashlib.sha256(data).hexdigest()},ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
