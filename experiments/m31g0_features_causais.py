#!/usr/bin/env python3
"""SGV M31-G0 ENGINEERING ONLY — causal pseudo-geometry features & strong HAR-X.

No holdout, no scientific preregistration, no confirmatory backtest.
Cone/waist here are explicitly PROXIES pending original code/commit of M31-G.
Run --mode exploratory only on BTCUSDT spot 1m May--July 2026 zips.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from sgvgeo.flow import flow_coordinates
from sgvgeo.data import load_binance_klines, ohlcv_from_returns

MINUTES = 60_000
SEED = 20261012
RVS = (15, 60, 240, 1440)
GEOM_WINDOW = 360
NU_HISTORY = 1500
ORIGIN_STEP = 15
FUTURE_HORIZON = 15
REG_TRAIN = 672  # exactly 7 days x 96 origins/day
RIDGE = 1.0
EPS = 1e-12
MIN_TAIL_GROUP = 60
WAIST_CUTOFF = 0.1
EXPLORATORY_FILES = tuple(
    ROOT / "data" / f"BTCUSDT-1m-2026-{m}.zip" for m in ("05", "06", "07")
)

B0_FEATURES = tuple(
    [f"log_rv_past_{m}" for m in RVS]
    + ["log_volmean_15", "log_volmean_60", "abs_iota",
       "nu", "sin_minute_hour", "cos_minute_hour",
       "sin_minute_day", "cos_minute_day"]
    + [f"weekday_{d}" for d in range(6)]
)
G_FEATURES = ("cone_log_proxy", "waist_proxy", "cone_log_x_nu_proxy")
B1_FEATURES = B0_FEATURES + G_FEATURES


def validate_klines(df: pd.DataFrame, *, require_btc_2026: bool = False):
    needed = {"timestamp", "close", "volume", "taker_buy"}
    missing = needed.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    ts = np.asarray(df["timestamp"], dtype=np.int64)
    if len(ts) < NU_HISTORY + GEOM_WINDOW + FUTURE_HORIZON + 10:
        raise ValueError("Insufficient 1m candles for complete causal windows")
    if np.any(np.diff(ts) != MINUTES):
        raise ValueError("Gap/duplicate/non-1m candles; refuse to bridge")
    price = np.asarray(df["close"], dtype=float)
    vol = np.asarray(df["volume"], dtype=float)
    buy = np.asarray(df["taker_buy"], dtype=float)
    if not (np.isfinite(price).all() and np.isfinite(vol).all()
            and np.isfinite(buy).all()):
        raise ValueError("Nonfinite OHLCV")
    if np.any(price <= 0) or np.any(vol <= 0):
        raise ValueError("Nonpositive close/volume")
    if np.any(buy < -1e-10) or np.any(buy - vol > 1e-7):
        raise ValueError("Taker base buys outside 0..volume")
    if require_btc_2026:
        start = pd.Timestamp("2026-05-01", tz="UTC").value // 1_000_000
        end = pd.Timestamp("2026-08-01", tz="UTC").value // 1_000_000
        if not (start <= ts[0] and ts[-1] < end):
            raise ValueError("Data outside authorized May--July 2026 BTC period")
    return True


def synthetic_klines(n=3400, seed=SEED):
    """Deterministic synthetic 1m prices, flow and volume; no real BTC."""
    rng = np.random.default_rng(seed)
    z = rng.standard_t(6, size=n) * 0.0007
    frame = ohlcv_from_returns(
        z, p0=50_000., seed=seed + 1,
        t0_ms=int(pd.Timestamp("2026-05-01", tz="UTC").value // 1_000_000),
    )
    # Nontrivial taker imbalance, no dependence on future features.
    base = frame["volume"].to_numpy(float)
    frame["taker_buy"] = base * np.clip(
        0.5 + 0.25 * rng.standard_normal(n), 0., 1.
    )
    return frame


def cone_waist_proxy(z_window, iota_window, nu_window):
    """Causal 6h split: upper/lower nu terciles; no fitted GMM surface.

    CONE = SD(z|upper third nu)/SD(z|lower third nu)
    WAIST = P(|iota|<=0.1|upper third nu)
    Both are exploratory CONDITIONAL STATISTICS, not intrinsic geometry.
    """
    a = np.asarray(z_window, dtype=float)
    b = np.asarray(iota_window, dtype=float)
    c = np.asarray(nu_window, dtype=float)
    if (a.shape != (GEOM_WINDOW,) or b.shape != (GEOM_WINDOW,)
            or c.shape != (GEOM_WINDOW,)):
        return None
    if not (np.isfinite(a).all() and np.isfinite(b).all()
            and np.isfinite(c).all()):
        return None
    qlo, qhi = np.quantile(c, (1 / 3, 2 / 3))
    lo, hi = c <= qlo, c >= qhi
    if min(int(lo.sum()), int(hi.sum())) < MIN_TAIL_GROUP:
        return None
    sd_lo, sd_hi = float(a[lo].std(ddof=1)), float(a[hi].std(ddof=1))
    if sd_lo <= 1e-12 or sd_hi <= 1e-12:
        return None
    cone = sd_hi / sd_lo
    waist = float(np.mean(np.abs(b[hi]) <= WAIST_CUTOFF))
    return float(np.log(cone)), waist


def target_rv_forward(r, horizon=FUTURE_HORIZON):
    """At t: sum(r[t+1:t+1+h]^2). Last h values are unavailable/NaN."""
    v = np.asarray(r, dtype=float)
    sq = v * v
    out = np.full(len(v), np.nan, dtype=float)
    if horizon < 1 or len(v) <= horizon:
        return out
    # Padded cumulative sum; only finite array series used in valid rows.
    clean = np.where(np.isfinite(sq), sq, 0.)
    c = np.r_[0., np.cumsum(clean)]
    out[:-horizon] = c[horizon + 1:] - c[1:-horizon]
    return out


def qlike_deviance(vhat, rv):
    """Unitless QLIKE divergence; no zero targets allowed."""
    vhat, rv = np.asarray(vhat, float), np.asarray(rv, float)
    if np.any(vhat <= 0) or np.any(rv <= 0):
        raise ValueError("QLIKE deviance requires strictly positive arguments")
    ratio = rv / vhat
    return ratio - np.log(ratio) - 1.


def build_rows(frame: pd.DataFrame, *, require_btc_2026=False):
    """All feature values at origin i use closed bars <= i.

    Future target is included solely for training once its maturity
    `origin_i + 15 <= current_i` has been verified in forecast_at().
    """
    validate_klines(frame, require_btc_2026=require_btc_2026)
    ts = np.asarray(frame["timestamp"], dtype=np.int64)
    coords = flow_coordinates(frame)
    r = coords["r"].to_numpy(float)
    z = coords["z"].to_numpy(float)
    iota = coords["iota"].to_numpy(float)
    nu = coords["nu"].to_numpy(float)
    vol = np.asarray(frame["volume"], float)
    rv_past = {
        w: pd.Series(r * r).rolling(w, min_periods=w).sum().to_numpy()
        for w in RVS
    }
    logvol = {
        w: np.log(pd.Series(vol).rolling(w, min_periods=w).mean().to_numpy())
        for w in (15, 60)
    }
    rv_future = target_rv_forward(r)
    rows = []
    first = NU_HISTORY + GEOM_WINDOW + 1
    indices = np.flatnonzero(((ts // MINUTES) % ORIGIN_STEP == 0)
                             & (np.arange(len(ts)) >= first))
    for i in indices:
        arr = (z[i-GEOM_WINDOW+1:i+1],
               iota[i-GEOM_WINDOW+1:i+1],
               nu[i-GEOM_WINDOW+1:i+1])
        g = cone_waist_proxy(*arr)
        if g is None:
            continue
        if (not np.isfinite(rv_past[1440][i])
                or not np.isfinite(logvol[60][i])
                or not np.isfinite(iota[i]) or not np.isfinite(nu[i])):
            continue
        t = pd.Timestamp(int(ts[i]), unit="ms", tz="UTC")
        minute = int(t.minute)
        minute_of_day = int(t.hour) * 60 + minute
        d = int(t.dayofweek)
        row = {
            "origin_i":int(i),
            "origin_ts":int(ts[i]),
            "label_matures_i":int(i + FUTURE_HORIZON),
            "label_matures_ts":int(ts[i] + FUTURE_HORIZON * MINUTES),
            "rv_future_15":float(rv_future[i]),
            "log_volmean_15":float(logvol[15][i]),
            "log_volmean_60":float(logvol[60][i]),
            "abs_iota":float(abs(iota[i])),
            "nu":float(nu[i]),
            "sin_minute_hour":float(np.sin(2*np.pi*minute/60)),
            "cos_minute_hour":float(np.cos(2*np.pi*minute/60)),
            "sin_minute_day":float(np.sin(2*np.pi*minute_of_day/1440)),
            "cos_minute_day":float(np.cos(2*np.pi*minute_of_day/1440)),
            "cone_log_proxy":g[0],
            "waist_proxy":g[1],
            "cone_log_x_nu_proxy":float(g[0] * nu[i]),
        }
        row.update({f"log_rv_past_{w}":
                    float(np.log(max(rv_past[w][i], EPS)))
                    for w in RVS})
        row.update({f"weekday_{j}":float(d == j) for j in range(6)})
        rows.append(row)
    data = pd.DataFrame(rows)
    if data.empty:
        raise ValueError("No valid causal feature rows")
    return data


def _ridge_fit(train:pd.DataFrame, target:pd.Series, columns):
    x = train[list(columns)].to_numpy(float)
    y = np.log(np.maximum(target.to_numpy(float), EPS))
    mu=x.mean(axis=0)
    sd=x.std(axis=0)
    sd=np.where(sd>1e-10,sd,1.)
    xn = (x-mu)/sd
    X = np.column_stack((np.ones(len(xn)),xn))
    penalty = np.diag([0.] + [RIDGE]*xn.shape[1])
    beta = np.linalg.solve(X.T@X+penalty,X.T@y)
    residual = y-X@beta
    smear = float(np.mean(np.exp(np.clip(residual,-30.,15.))))
    if not np.isfinite(smear) or smear<=0:
        raise FloatingPointError("Invalid smearing factor")
    return beta,mu,sd,smear


def forecast_at(data:pd.DataFrame, origin_i:int,columns, *, train_count=REG_TRAIN):
    """The only eligible labels ended no later than origin_i.

    Uses original index for temporal eligibility, independent of whether
    the data table contains future rows/labels or later modifications.
    """
    current=data.loc[data["origin_i"]==origin_i]
    if len(current)!=1:
        raise ValueError("Origin absent or duplicated")
    mature=data.loc[
        (data["label_matures_i"]<=origin_i)
        & np.isfinite(data["rv_future_15"])
        & (data["rv_future_15"]>=0)
    ].sort_values("origin_i")
    if len(mature)<train_count:
        raise ValueError("Insufficient strictly matured training labels")
    train=mature.tail(train_count)
    if int(train["label_matures_i"].max())>origin_i:
        raise AssertionError("Label leakage")
    beta,mu,sd,smear=_ridge_fit(train,train["rv_future_15"],columns)
    current_x=current[list(columns)].to_numpy(float)
    linear=float(np.r_[1.,(current_x[0]-mu)/sd]@beta)
    point = float(np.exp(np.clip(linear,-30.,15.))*smear)
    if not np.isfinite(point) or point<=0:
        raise FloatingPointError("Invalid predicted RV")
    return {
        "rv_hat":point,
        "n_train":len(train),
        "train_first_i":int(train["origin_i"].min()),
        "train_last_i":int(train["origin_i"].max()),
        "last_matured_label_i":int(train["label_matures_i"].max()),
        "train_smearing":smear,
    }


def engineering_report(df, *, synthetic=False, probes=32):
    tic=time.perf_counter()
    data=build_rows(df,require_btc_2026=not synthetic)
    feature_seconds=time.perf_counter()-tic
    irows=data["origin_i"].to_numpy(np.int64)
    # Preselect evenly spread, deterministic probes with sufficient mature labels.
    eligible=[int(i) for i in irows
              if int(np.sum(data["label_matures_i"].to_numpy()<=i))>=REG_TRAIN]
    if not eligible:
        raise ValueError("Insufficient history to fit fixed 7-day rolling baseline")
    ids=np.linspace(0,len(eligible)-1,min(probes,len(eligible)),dtype=int)
    chosen=[eligible[j] for j in ids]
    preds=[]
    fit_start=time.perf_counter()
    for i in chosen:
        p0=forecast_at(data,i,B0_FEATURES)
        p1=forecast_at(data,i,B1_FEATURES)
        preds.append({
            "origin_i":i,"origin_ts":int(data.loc[data["origin_i"]==i,"origin_ts"].iloc[0]),
            "baseline_rv_hat":round(p0["rv_hat"],12),
            "proxy_plus_rv_hat":round(p1["rv_hat"],12),
            "training_n":p0["n_train"],
            "last_matured_label_i":p0["last_matured_label_i"],
        })
    fit_seconds=time.perf_counter()-fit_start
    def summary(x):
        q=np.quantile(np.asarray(x,float),[0,.05,.5,.95,1])
        return {k:round(float(y),6) for k,y in zip(("min","p05","median","p95","max"),q)}
    result={
        "study":"M31-G0 ENGINEERING ONLY: causal 6h conditional proxies",
        "not_confirmatory":True,"source":"SYNTHETIC" if synthetic else "BTCUSDT spot 1m May--July 2026 (already explored)",
        "raw_rows":len(df),"causal_origin_rows":len(data),
        "origin_count_total_candidates":int(np.sum((np.asarray(df["timestamp"])//MINUTES)%ORIGIN_STEP==0)),
        "valid_causal_coverage_fraction":round(len(data)/max(1,int(np.sum((np.asarray(df["timestamp"])//MINUTES)%ORIGIN_STEP==0))),6),
        "first_origin_utc":pd.to_datetime(data["origin_ts"].iloc[0],unit="ms",utc=True).isoformat(),
        "last_origin_utc":pd.to_datetime(data["origin_ts"].iloc[-1],unit="ms",utc=True).isoformat(),
        "features_b0":list(B0_FEATURES),"features_proxy":list(G_FEATURES),
        "n_train_fixed":REG_TRAIN,"n_probe_forecasts":len(preds),
        "cone_log_proxy_summary":summary(data["cone_log_proxy"]),
        "waist_proxy_summary":summary(data["waist_proxy"]),
        "n_invalid_label_tail":int(data["rv_future_15"].isna().sum()),
        "time_feature_seconds":round(feature_seconds,4),
        "time_probe_fit_seconds":round(fit_seconds,4),
        "probe_predictions":preds,
        "deliberately_omitted":"No QLIKE performance comparison, p-values, or external/holdout data were evaluated.",
        "limitations":[
            "These features are conditional summary proxies, NOT the cone/waist of the other collaborator.",
            "The 6h proxy depends on historical 1500-min volume normalization.",
            "B0 is a prototyping HAR-X seasonal baseline, NOT validated as the strongest baseline.",
            "Forecasts are merely technical sanity checks. No performance or advantage claim.",
        ],
    }
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("synthetic","exploratory"),default="synthetic")
    p.add_argument("--out",default="reports/m31g0/engenharia.json")
    p.add_argument("--probes",type=int,default=32)
    a=p.parse_args()
    if a.mode=="synthetic":
        frame=synthetic_klines(n=17_000)
    else:
        if not all(f.exists() for f in EXPLORATORY_FILES):
            raise FileNotFoundError("Only authorized BTC 1m May--July zips are accepted")
        frame=load_binance_klines(EXPLORATORY_FILES,with_flow=True)
    result=engineering_report(frame,synthetic=a.mode=="synthetic",probes=a.probes)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    summary={k:v for k,v in result.items() if k not in ("probe_predictions","features_b0","features_proxy")}
    print(json.dumps(summary,ensure_ascii=False))
    return result


if __name__=="__main__":
    main()
