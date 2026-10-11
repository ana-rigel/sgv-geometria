#!/usr/bin/env python3
"""M20c: conditional sliced quantile transport vs classical nonlinear
dependence tests under prefix-fitted VAR nulls. Synthetic ONLY.

Five independent scenario shards, 80 independent trials each.
Every trial fits a Gaussian VAR(1) on prefix ONLY and compares a future
window to 19 futures from that fitted null. No data from BTC is loaded.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from experiments.m20b_dependencia_ordem_superior import generate as gen_m20b

SEED = 20261011
SCENARIOS = ("null", "gaussian_var", "hidden_plus", "hidden_minus",
             "volatility_memory")
METRICS = ("conditional_sw2", "rff_hsic", "joint_mmd",
           "linear_lag", "quadratic_lag", "marginal_shift")
MAIN_PREFIX = 800
MAIN_FUTURE = 500
MAIN_N_REF = 19
MAIN_TRIALS = 80

_rngproj = np.random.default_rng(271828)
PROJECTIONS = np.concatenate(
    (np.eye(3), _rngproj.normal(size=(3,3))), axis=0)
PROJECTIONS /= np.linalg.norm(PROJECTIONS, axis=1, keepdims=True)
RFF_DIR = np.random.default_rng(104729).normal(size=(8,3))
JOINT_DIR = np.random.default_rng(161803).normal(size=(12,6))
QUANTILE_LEVELS = (0.1,0.25,0.5,0.75,0.9)


def random_rotation(rng):
    raw = rng.standard_normal((3,3))
    q, r = np.linalg.qr(raw)
    q = q @ np.diag(np.where(np.diag(r) >= 0, 1.0, -1.0))
    if np.linalg.det(q) < 0:
        q[:, -1] *= -1
    return q


def generate_series(n, scenario, rng):
    if scenario == "null":
        return rng.standard_normal((n, 3))
    if scenario == "gaussian_var":
        rho = 0.38
        x = np.empty((n,3), dtype=float)
        x[0] = rng.standard_normal(3)
        eps = math.sqrt(1-rho*rho)*rng.standard_normal((n,3))
        for t in range(1,n):
            x[t] = rho*x[t-1] + eps[t]
        return x
    kind = {
        "hidden_plus":"hidden_plus", "hidden_minus":"hidden_minus",
        "volatility_memory":"volatility_memory"}[scenario]
    raw = gen_m20b(n,kind,rng)
    return raw @ random_rotation(rng)


def fit_var(prefix):
    """OLS ridge on observed prefix only, with positive definite covariance."""
    if len(prefix) < 20 or prefix.shape[1] != 3:
        raise ValueError("Need (>=20,3) prefix")
    X = np.column_stack((np.ones(len(prefix)-1),prefix[:-1]))
    Y = prefix[1:]
    penalty = np.diag([0.,1e-4,1e-4,1e-4])
    B = np.linalg.solve(X.T@X+penalty,X.T@Y)
    residual = Y-X@B
    cov = residual.T @ residual / len(residual)
    cov = (cov+cov.T)*0.5 + np.eye(3)*1e-6
    return B[0],B[1:],np.linalg.cholesky(cov)


def simulate_var(last, params, n, rng):
    intercept,A,chol = params
    x = np.empty((n,3),dtype=float)
    cur = last.copy()
    noise = rng.standard_normal((n,3)) @ chol.T
    for i in range(n):
        cur = intercept+cur@A+noise[i]
        x[i] = cur
    return x


def conditional_sw2(pairs_x,pairs_y):
    """Average squared quantile displacements in six fixed projections.
    Conditional distributions are in terciles of each antecedent projection.
    This is a discretized conditional sliced-W2-inspired statistic, not exact OT.
    """
    xp = pairs_x @ PROJECTIONS.T
    yp = pairs_y @ PROJECTIONS.T
    unconditional = np.quantile(yp,QUANTILE_LEVELS,axis=0)
    value = 0.0
    for j in range(6):
        splits = np.quantile(xp[:,j],(1/3,2/3))
        groups = (xp[:,j] <= splits[0],
                  (xp[:,j] > splits[0]) & (xp[:,j] <= splits[1]),
                  xp[:,j] > splits[1])
        for idx in groups:
            if int(idx.sum()) < 5:
                raise ValueError("Too-small conditioning tercile")
            conditional = np.quantile(yp[idx],QUANTILE_LEVELS,axis=0)
            value += float(np.mean((conditional-unconditional)**2))
    return value / 18.0


def rff_hsic(x,y):
    a=x@RFF_DIR.T
    b=y@RFF_DIR.T
    f=np.concatenate((np.sin(a),np.cos(a)),axis=1)
    g=np.concatenate((np.sin(b),np.cos(b)),axis=1)
    f-=f.mean(axis=0)
    g-=g.mean(axis=0)
    cross=f.T@g/len(x)
    return float(np.sum(cross*cross))


def joint_mmd(x,y):
    u=x@JOINT_DIR[:,:3].T
    v=y@JOINT_DIR[:,3:].T
    # Compare characteristic embedding E exp(i*(aX+bY)) against
    # E exp(i*aX) * E exp(i*bY). No random permutations or look-ahead.
    joint=np.mean(np.exp(1j*(u+v)),axis=0)
    independent=(np.mean(np.exp(1j*u),axis=0)
                 * np.mean(np.exp(1j*v),axis=0))
    return float(np.mean(np.abs(joint-independent)**2))


def scores(window):
    if window.ndim != 2 or window.shape[1] != 3 or len(window)<100:
        raise ValueError("Window must be (n>=100,3)")
    x,y=window[:-1],window[1:]
    xc=x-x.mean(axis=0)
    yc=y-y.mean(axis=0)
    lag=xc.T@yc/len(x)
    qx=x*x
    qy=y*y
    quad=((qx-qx.mean(axis=0)).T@(qy-qy.mean(axis=0)))/len(x)
    n=len(window)//2
    diff_mean=window[:n].mean(axis=0)-window[n:].mean(axis=0)
    ca=np.cov(window[:n],rowvar=False,bias=True)
    cb=np.cov(window[n:],rowvar=False,bias=True)
    out={
        "conditional_sw2":conditional_sw2(x,y),
        "rff_hsic":rff_hsic(x,y),
        "joint_mmd":joint_mmd(x,y),
        "linear_lag":float(np.linalg.norm(lag)),
        "quadratic_lag":float(np.linalg.norm(quad)),
        "marginal_shift":float(np.sqrt(np.sum(diff_mean*diff_mean)
                                       + np.sum((ca-cb)**2))),
    }
    if not all(np.isfinite(v) and v>=0 for v in out.values()):
        raise FloatingPointError("Nonfinite or negative metric")
    return out


def one_trial(sid,trial,prefix_length=MAIN_PREFIX,
              future_length=MAIN_FUTURE,n_refs=MAIN_N_REF,
              independent_seed=SEED):
    rng=np.random.default_rng(np.random.SeedSequence(
        [independent_seed,int(sid),int(trial)]))
    scenario=SCENARIOS[sid]
    truth=generate_series(prefix_length+future_length,scenario,rng)
    prefix=truth[:prefix_length]
    future=truth[prefix_length:]
    params=fit_var(prefix)
    observed=scores(future)
    maxima={s:-float("inf") for s in METRICS}
    refs={s:[] for s in METRICS}
    for _ in range(n_refs):
        simulated=simulate_var(prefix[-1],params,future_length,rng)
        sim=scores(simulated)
        for s in METRICS:
            maxima[s]=max(maxima[s],sim[s])
            refs[s].append(sim[s])
    if not all(len(refs[s])==n_refs for s in METRICS):
        raise RuntimeError("Incomplete reference panel")
    alarms={s:bool(observed[s]>maxima[s]) for s in METRICS}
    return {
        "scenario":scenario,"trial":trial,
        "alarms":alarms,
        "observed":{s:round(float(observed[s]),10) for s in METRICS},
        "reference_max":{s:round(float(maxima[s]),10) for s in METRICS},
    }


def run(mode,scenario=None,outdir="reports/m20c"):
    pilot=mode=="pilot"
    if pilot:
        scenarios=range(5)
        nt=3
        n_prefix,n_future,n_refs=400,300,19
        seed=SEED+1
        output=Path(outdir)/"piloto_engenharia.json"
    else:
        if scenario is None or scenario not in range(5):
            raise ValueError("Full run requires --scenario 0..4")
        scenarios=(scenario,)
        nt=MAIN_TRIALS
        n_prefix,n_future,n_refs=MAIN_PREFIX,MAIN_FUTURE,MAIN_N_REF
        seed=SEED
        output=Path(outdir)/f"shard_{scenario}.json"
    trials=[]
    for sid in scenarios:
        for trial in range(nt):
            trials.append(one_trial(sid,trial,n_prefix,n_future,n_refs,seed))
    data={
        "mode":mode,"seed":seed,
        "prefix_length":n_prefix,"future_length":n_future,
        "references_per_trial":n_refs,"trials_per_scenario":nt,
        "scenarios":([SCENARIOS[i] for i in scenarios]),
        "metrics":METRICS,"records":trials,
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"mode":mode,"scenarios":data["scenarios"],
                      "trial_count":len(trials),
                      "alarms_by_scenario":{
                        name:{s:sum(1 for r in trials if r["scenario"]==name
                                    and r["alarms"][s]) for s in METRICS}
                        for name in data["scenarios"]}},ensure_ascii=False))
    return data


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("pilot","full"),default="full")
    p.add_argument("--scenario",type=int)
    p.add_argument("--outdir",default="reports/m20c")
    a=p.parse_args()
    run(a.mode,a.scenario,a.outdir)
