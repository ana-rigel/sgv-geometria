#!/usr/bin/env python3
"""SGV-M20d: 2x2x2 paired factorial ablation; SYNTHETIC ONLY.

Compare direction oracle vs blind projection, n=500 vs 1800, and true
Gaussian null vs prefix-fitted VAR. Each unit is an independent trial;
the observed path is identical across its eight cells. This does NOT
establish new geometry or provide a BTC indicator.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
from experiments.m20b_dependencia_ordem_superior import generate as generate_m20b
from experiments.m20c_acoplamento_condicional import random_rotation, fit_var, simulate_var, rff_hsic

ROOT=Path(__file__).resolve().parents[1]
SEED=20261011
SCENARIOS=("null","gaussian_var","hidden_plus","hidden_minus","volatility_memory")
PREFIX=800
LONG=1800
SHORT=500
R=19
TRIALS=64
METHODS=("hsic_1d","cqw2_1d","lag_1d")
LENS=(SHORT,LONG)
DIRECTIONS=("known","blind")
NULLS=("known","fitted")
QLEVELS=(.1,.25,.5,.75,.9)


def make_truth(n, sid, rng):
    name=SCENARIOS[sid]
    if name=="gaussian_var":
        a=.38
        raw=np.empty((n,3),float)
        raw[0]=rng.standard_normal(3)
        eps=rng.standard_normal((n,3))*math.sqrt(1-a*a)
        for t in range(1,n):
            raw[t]=a*raw[t-1]+eps[t]
    else:
        name_m20={"null":"null","hidden_plus":"hidden_plus",
                  "hidden_minus":"hidden_minus",
                  "volatility_memory":"volatility_memory"}[name]
        raw=generate_m20b(n,name_m20,rng)
    q=random_rotation(rng)
    # raw latent row (u,v,w) -> observed coordinates raw @ Q.T.
    # Its first latent direction is the FIRST COLUMN of Q (oracle).
    return raw@q.T, q[:,0]


def known_model(sid):
    a=.38 if SCENARIOS[sid]=="gaussian_var" else 0.0
    return np.zeros(3),np.eye(3)*a,np.eye(3)*math.sqrt(1-a*a)


def projected_stats(seq):
    """1D distribution coupling statistics, each with fixed definitions."""
    a,b=seq[:-1],seq[1:]
    # identical features to M20b for the 1D projected test
    fa=np.stack([fn(k*a) for k in (1,2,3)
                 for fn in (np.sin,np.cos)],axis=1)
    fb=np.stack([fn(k*b) for k in (1,2,3)
                 for fn in (np.sin,np.cos)],axis=1)
    fa-=fa.mean(axis=0)
    fb-=fb.mean(axis=0)
    c=fa.T@fb/len(a)
    s=np.quantile(a,[1/3,2/3])
    unconditional=np.quantile(b,QLEVELS)
    cqw=0.0
    for mask in (a<=s[0],(a>s[0])&(a<=s[1]),a>s[1]):
        if mask.sum()<20:
            raise ValueError("Too-small tertile")
        cqw+=float(np.mean((np.quantile(b[mask],QLEVELS)-unconditional)**2))
    lag=float(abs(np.mean((a-a.mean())*(b-b.mean()))))
    out={"hsic_1d":float(np.sum(c*c)),
         "cqw2_1d":cqw/3.0,
         "lag_1d":lag}
    if not all(np.isfinite(x) and x>=0 for x in out.values()):
        raise FloatingPointError("bad 1D score")
    return out


def cell_key(direction,n,null):
    return f"{direction}_n{n}_{null}"


def one_trial(sid,trial,seed=SEED,n_refs=R,prefix_length=PREFIX):
    if n_refs<1:
        raise ValueError("No null references")
    obsrng=np.random.default_rng(np.random.SeedSequence(
        [seed,sid,trial,0]))
    path,direction=make_truth(prefix_length+LONG,sid,obsrng)
    prefix=path[:prefix_length]
    future=path[prefix_length:]
    # Same observed trajectory across ALL factor cells.
    proj={"known":direction,"blind":np.array([1.0,0.,0.])}
    obs={}
    for label,d in proj.items():
        u=future@d
        for n in LENS:
            obs[(label,n)]=projected_stats(u[:n])
    obs_3d={n:rff_hsic(future[:n-1],future[1:n]) for n in LENS}
    params={"known":known_model(sid),
            "fitted":fit_var(prefix)}
    maxima={(label,n,null,m):-math.inf
            for label in DIRECTIONS for n in LENS for null in NULLS
            for m in METHODS}
    maxima3d={(n,null):-math.inf for n in LENS for null in NULLS}
    for j,null in enumerate(NULLS):
        rg=np.random.default_rng(np.random.SeedSequence(
            [seed,sid,trial,1+j]))
        for _ in range(n_refs):
            simulated=simulate_var(prefix[-1],params[null],LONG,rg)
            for n in LENS:
                score_3d=rff_hsic(simulated[:n-1],simulated[1:n])
                maxima3d[(n,null)]=max(maxima3d[(n,null)],score_3d)
            for label,d in proj.items():
                u=simulated@d
                for n in LENS:
                    ss=projected_stats(u[:n])
                    for metric in METHODS:
                        k=(label,n,null,metric)
                        maxima[k]=max(maxima[k],ss[metric])
    alarms={}
    values={}
    for label in DIRECTIONS:
        for n in LENS:
            for null in NULLS:
                ck=cell_key(label,n,null)
                alarms[ck]={m:bool(obs[(label,n)][m]>maxima[(label,n,null,m)])
                            for m in METHODS}
                values[ck]={m:round(float(obs[(label,n)][m]),8) for m in METHODS}
    blind3d={f"n{n}_{null}":bool(obs_3d[n]>maxima3d[(n,null)])
             for n in LENS for null in NULLS}
    return {"scenario":SCENARIOS[sid],"trial":trial,
            "alarms":alarms,"blind_rff3d":blind3d,
            "oracle_direction":direction.round(10).tolist(),
            "observed_scores":values,
            "observed_rff3d":{str(n):round(float(obs_3d[n]),8) for n in LENS}}


def run(mode,sid=None,outdir="reports/m20d"):
    pilot=mode=="pilot"
    if pilot:
        scenarios=range(len(SCENARIOS))
        count=2
        seed=SEED+1
        out=Path(outdir)/"piloto_engenharia.json"
    else:
        if sid not in range(len(SCENARIOS)):
            raise ValueError("full requires --scenario 0..4")
        scenarios=(sid,)
        count=TRIALS
        seed=SEED
        out=Path(outdir)/f"shard_{sid}.json"
    records=[]
    for scenario in scenarios:
        for trial in range(count):
            records.append(one_trial(scenario,trial,seed))
    payload={
        "mode":mode,"seed":seed,"prefix":PREFIX,
        "future_short":SHORT,"future_long":LONG,"references":R,
        "trials_per_scenario":count,
        "scenario_ids":list(scenarios),"scenarios":[SCENARIOS[x] for x in scenarios],
        "metrics":list(METHODS),
        "records":records}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"mode":mode,"scenarios":payload["scenarios"],
                      "records":len(records),
                      "n_alarm_summary":{
                        s:sum(int(row["alarms"][cell_key("known",LONG,"known")]["hsic_1d"])
                              for row in records if row["scenario"]==s)
                        for s in payload["scenarios"]}},ensure_ascii=False))
    return payload


if __name__=="__main__":
    pa=argparse.ArgumentParser()
    pa.add_argument("--mode",choices=("pilot","full"),default="full")
    pa.add_argument("--scenario",type=int)
    pa.add_argument("--outdir",default="reports/m20d")
    args=pa.parse_args()
    run(args.mode,args.scenario,args.outdir)
