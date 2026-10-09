#!/usr/bin/env python3
"""Exploratory Fisher–Rao trajectory diagnostic. Never accesses confirmatory periods.

Run: python experiments/fisher_rao_trajectory.py --interval 1h
Requires numpy; local exploration ZIPs under data/.
This is a diagnostic, NOT a preregistered confirmatory test.
"""
import argparse
import csv
import json
import re
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CUTOFF = {"1m": "2026-08", "1h": "2025-01"}
START = {"1m": "2026-05", "1h": "2020-01"}
END = {"1m": "2026-07", "1h": "2024-12"}


def read_exploration(interval):
    paths = sorted((ROOT / "data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths:
        raise FileNotFoundError("No exploration ZIPs in data/. Run scripts/baixar_klines.py first.")
    timestamps, high, low, close = [], [], [], []
    for path in paths:
        match = re.fullmatch(rf"BTCUSDT-{interval}-(\d{{4}}-\d{{2}})\.zip", path.name)
        if not match or not (START[interval] <= match.group(1) <= END[interval]):
            raise ValueError(f"Unexpected/out-of-range file: {path.name}")
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if not name.endswith(".csv"):
                    continue
                with archive.open(name) as stream:
                    import io
                    for row in csv.reader(io.TextIOWrapper(stream)):
                        try:
                            ts = int(row[0])
                            h, l, c = float(row[2]), float(row[3]), float(row[4])
                        except (ValueError, IndexError):
                            continue
                        if ts > 10**14:  # Binance microseconds
                            ts //= 1000
                        timestamps.append(ts)
                        high.append(h)
                        low.append(l)
                        close.append(c)
    ts = np.asarray(timestamps, dtype=np.int64)
    order = np.argsort(ts)
    ts, high, low, close = ts[order], np.asarray(high)[order], np.asarray(low)[order], np.asarray(close)[order]
    if len(ts) < 2000 or np.any(np.diff(ts) <= 0):
        raise ValueError("Too few bars or duplicate timestamps")
    from datetime import datetime, timezone
    last_month = datetime.fromtimestamp(int(ts[-1])/1000, timezone.utc).strftime("%Y-%m")
    if last_month >= CUTOFF[interval]:
        raise ValueError("Confirmatory period detected; aborting")
    return ts, high, low, close, [p.name for p in paths]


def rolling_mean_std(x, window):
    # causal estimates: value at index t uses returns up to t
    n = len(x)
    a = np.full(n, np.nan)
    b = np.full(n, np.nan)
    cs = np.r_[0., np.cumsum(x)]
    cs2 = np.r_[0., np.cumsum(x*x)]
    mu = (cs[window:] - cs[:-window]) / window
    var = (cs2[window:] - cs2[:-window]) / window - mu*mu
    a[window-1:] = mu
    b[window-1:] = np.sqrt(np.maximum(var, 1e-14))
    return a, b


def curvature(mu, sig):
    """Fisher metric ds²=(dmu²+2 dsigma²)/sigma²; derivatives in bar time.
    Christoffel: Gamma^mu_mu,sigma=-1/sigma;
    Gamma^sigma_mu,mu=1/(2sigma); Gamma^sigma_sigma,sigma=-1/sigma.
    """
    u, v = np.gradient(mu), np.gradient(sig)
    du, dv = np.gradient(u), np.gradient(v)
    ax = du - 2*u*v/sig
    ay = dv + u*u/(2*sig) - v*v/sig
    speed2 = (u*u + 2*v*v)/(sig*sig)
    aa = (ax*ax + 2*ay*ay)/(sig*sig)
    ua = (u*ax + 2*v*ay)/(sig*sig)
    k2 = aa / np.maximum(speed2, 1e-22)**2 - ua**2 / np.maximum(speed2, 1e-22)**3
    return np.sqrt(np.maximum(k2, 0.))


def fit_predict(train_x, train_y, test_x, ridge=10.):
    m = train_x.mean(axis=0)
    s = train_x.std(axis=0)
    s[s < 1e-10] = 1.
    a = np.column_stack([np.ones(len(train_x)), (train_x-m)/s])
    b = np.column_stack([np.ones(len(test_x)), (test_x-m)/s])
    penalty = np.eye(a.shape[1])*ridge
    penalty[0, 0] = 0
    coef = np.linalg.solve(a.T@a + penalty, a.T@train_y)
    return b@coef


def evaluate(x, y, folds=5, embargo=8):
    n = len(y)
    start = n//2
    bounds = np.linspace(start, n, folds+1, dtype=int)
    predictions = np.full(n, np.nan)
    for left, right in zip(bounds[:-1], bounds[1:]):
        train_end = left-embargo
        if train_end < 300:
            raise ValueError("Insufficient training observations")
        predictions[left:right] = fit_predict(x[:train_end], y[:train_end], x[left:right])
    ok = np.isfinite(predictions)
    return float(np.mean((y[ok]-predictions[ok])**2)), predictions, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", choices=["1m","1h"], required=True)
    ap.add_argument("--window", type=int, default=1500)
    ap.add_argument("--max-rows", type=int, default=18000)
    args = ap.parse_args()
    if args.window < 50 or args.max_rows < 3000:
        raise ValueError("Invalid window/max-rows")
    ts, hi, lo, close, files = read_exploration(args.interval)
    # Take a contiguous exploration tail; no train/test overlap at evaluation boundaries.
    if len(close) > args.max_rows:
        ts, hi, lo, close = [a[-args.max_rows:] for a in (ts,hi,lo,close)]
    step_ms = 60000 if args.interval=="1m" else 3600000
    valid_step = np.r_[False, np.diff(ts)==step_ms]
    ret = np.r_[np.nan, np.diff(np.log(close))]
    ret[~valid_step] = np.nan
    # Segment after last gap, avoiding interpolating across missing bars.
    gaps = np.flatnonzero(~valid_step)
    last_gap = int(gaps[-1]) if len(gaps) else 0
    if last_gap > 0:
        ts, hi, lo, close, ret = [a[last_gap:] for a in (ts,hi,lo,close,ret)]
    ret[0] = 0.
    if len(ret) < max(3500, args.window*2):
        raise ValueError("Insufficient contiguous exploration bars")
    mu, sig = rolling_mean_std(ret, args.window)
    # Central differences use t+1; shift curvature by 2 to enforce causality.
    # At prediction origin t, k[t] uses parameter states at most t-1.
    start = args.window+5
    kraw = curvature(mu[start-3:], sig[start-3:])
    k = np.full(len(ret), np.nan)
    k[start:] = kraw[1:-2] if len(kraw[1:-2])==len(ret)-start else np.nan
    # More transparent causal implementation: compute k at t-2 from central derivatives.
    k = np.full(len(ret), np.nan)
    k[start:] = kraw[:-3]
    horizon = 5 if args.interval=="1m" else 4
    # Future log range of highs/lows; target known only after t+h.
    target = np.full(len(ret), np.nan)
    for t in range(start, len(ret)-horizon):
        target[t] = np.log(np.max(hi[t+1:t+horizon+1])/np.min(lo[t+1:t+horizon+1]))
    # Features are all causal and known by close of bar t.
    lag = np.column_stack([np.roll(ret, j) for j in (0,1,2,3,4)])
    vol = np.column_stack([sig, np.roll(sig, 1), np.roll(sig, 2)])
    vol_der = np.column_stack([np.gradient(sig), np.gradient(np.gradient(sig)),
                               np.gradient(mu), np.gradient(np.gradient(mu))])
    # gradient at t would use t+1: lag all derivative features two bars.
    vol_der = np.roll(vol_der, 2, axis=0)
    base = np.column_stack([lag, vol])
    expanded = np.column_stack([base, vol_der])
    fisher = np.column_stack([expanded, np.log1p(k)])
    valid = np.isfinite(target) & np.all(np.isfinite(fisher), axis=1)
    valid[:start+5] = False
    if valid.sum() < 2500:
        raise ValueError("Not enough usable rows")
    y = target[valid]
    xlist = [base[valid], expanded[valid], fisher[valid]]
    results = {}
    for name, x in zip(("baseline","derivatives","fisher"),xlist):
        mse, pred, mask = evaluate(x, y, embargo=horizon+4)
        results[name] = mse
    results["fisher_vs_derivatives_relative_mse_gain"] = (
        (results["derivatives"]-results["fisher"])/results["derivatives"])
    results["fisher_vs_baseline_relative_mse_gain"] = (
        (results["baseline"]-results["fisher"])/results["baseline"])
    report = {"status":"EXPLORATORY_ONLY", "interval":args.interval,
              "source_files":files, "rows":int(valid.sum()), "window":args.window,
              "horizon":horizon, "model":"Gaussian Fisher-Rao geodesic curvature",
              "note":"No GARCH fit or conditional-information significance test; baseline uses realized rolling volatility.",
              "results":results}
    out = ROOT/"reports"/f"FISHER_RAO_EXPLORATORIO_{args.interval}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__=="__main__":
    main()
