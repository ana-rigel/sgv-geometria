#!/usr/bin/env python3
"""Fail-closed SGV-M20d aggregator: 5 scenarios x 64 independent trials.

All statistics, confidence intervals and paired factor effects are computed
without refitting or selecting winning factors posthoc.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

SCENARIOS=("null","gaussian_var","hidden_plus","hidden_minus","volatility_memory")
D=("known","blind")
N=(500,1800)
R=("known","fitted")
METHODS=("hsic_1d","cqw2_1d","lag_1d")
TRIALS=64


def cell(d,n,r):
    return f"{d}_n{n}_{r}"


def wilson(k,n):
    z=1.95996398454
    p=k/n
    den=1+z*z/n
    ctr=(p+z*z/(2*n))/den
    rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [round(max(0,ctr-rad),4),round(min(1,ctr+rad),4)]


def load(sharddir):
    groups={}
    for sid,name in enumerate(SCENARIOS):
        p=Path(sharddir)/f"shard_{sid}.json"
        if not p.exists():
            raise FileNotFoundError(f"Missing required shard: {p}")
        obj=json.loads(p.read_text())
        expected=(obj["mode"]=="full" and obj["seed"]==20261011
                  and obj["prefix"]==800 and obj["future_short"]==500
                  and obj["future_long"]==1800 and obj["references"]==19
                  and obj["trials_per_scenario"]==TRIALS
                  and obj["scenario_ids"]==[sid]
                  and obj["scenarios"]==[name]
                  and obj["metrics"]==list(METHODS))
        if not expected:
            raise ValueError("Metadata inconsistent in "+str(p))
        rows=obj["records"]
        if len(rows)!=TRIALS or {r["trial"] for r in rows}!=set(range(TRIALS)):
            raise ValueError("Missing/duplicate trial in "+str(p))
        target_keys={cell(d,n,r) for d in D for n in N for r in R}
        for row in rows:
            if row["scenario"]!=name or set(row["alarms"])!=target_keys:
                raise ValueError("Inconsistent factor cells")
            if set(row["observed_scores"])!=target_keys:
                raise ValueError("Incomplete observed scores")
            for d in D:
                for n in N:
                    a=row["observed_scores"][cell(d,n,"known")]
                    b=row["observed_scores"][cell(d,n,"fitted")]
                    if a!=b:
                        raise ValueError("Observed truth modified across null factor")
            for v in row["alarms"].values():
                if set(v)!=set(METHODS) or any(type(x) is not bool for x in v.values()):
                    raise ValueError("Bad metric/boolean")
            if set(row["blind_rff3d"])!={f"n{n}_{r}" for n in N for r in R}:
                raise ValueError("Incomplete blind 3D comparators")
        groups[name]=sorted(rows,key=lambda r:r["trial"])
    return groups


def paired_effects(rows,metric):
    """Unit of resampling is one TRIAL, not its eight nonindependent cells."""
    table=[]
    for row in rows:
        z={}
        a=row["alarms"]
        z["direction"]=np.mean([
            int(a[cell("known",n,r)][metric])-int(a[cell("blind",n,r)][metric])
            for n in N for r in R])
        z["sample_size"]=np.mean([
            int(a[cell(d,1800,r)][metric])-int(a[cell(d,500,r)][metric])
            for d in D for r in R])
        z["null_model"]=np.mean([
            int(a[cell(d,n,"known")][metric])-int(a[cell(d,n,"fitted")][metric])
            for d in D for n in N])
        table.append(z)
    effects={}
    arr=np.array([[z[f] for f in ("direction","sample_size","null_model")]
                  for z in table])
    rng=np.random.default_rng(314159)
    boot=np.empty((2000,3))
    for i in range(len(boot)):
        indices=rng.integers(0,len(arr),len(arr))
        boot[i]=arr[indices].mean(axis=0)
    for j,name in enumerate(("direction","sample_size","null_model")):
        effects[name]={
            "delta_pp":round(100*float(arr[:,j].mean()),3),
            "trial_bootstrap95_pp":[round(100*float(x),3)
                                    for x in np.quantile(boot[:,j],[.025,.975])],
            "paired_trial_n":len(rows)}
    return effects


def analyze(groups):
    rates={}
    effects={}
    for name,rows in groups.items():
        rates[name]={}
        for d in D:
            for n in N:
                for r in R:
                    ck=cell(d,n,r)
                    rates[name][ck]={}
                    for met in METHODS:
                        k=sum(int(x["alarms"][ck][met]) for x in rows)
                        rates[name][ck][met]={
                            "alarms":k,"n":TRIALS,
                            "rate":round(k/TRIALS,6),
                            "wilson95":wilson(k,TRIALS)}
        rates[name]["blind_rff3d"]={}
        for n in N:
            for r in R:
                k=sum(int(x["blind_rff3d"][f"n{n}_{r}"]) for x in rows)
                rates[name]["blind_rff3d"][f"n{n}_{r}"]={
                    "alarms":k,"n":TRIALS,"rate":round(k/TRIALS,6),
                    "wilson95":wilson(k,TRIALS)}
        if name in ("hidden_plus","hidden_minus"):
            effects[name]={met:paired_effects(rows,met) for met in METHODS}
    def rate(s,d,n,r,metric):
        return rates[s][cell(d,n,r)][metric]["rate"]
    null_checks={}
    for name in ("null","gaussian_var"):
        for metric in ("hsic_1d","cqw2_1d"):
            vals=[rate(name,d,n,r,metric) for d in D for n in N for r in R]
            null_checks[f"{name}/{metric}"]={
                "avg":round(float(np.mean(vals)),6),
                "max":round(float(max(vals)),6)}
    g1=all(z["avg"]<=.10 and z["max"]<=.16 for z in null_checks.values())
    g2=all(rate(s,"known",1800,"known","hsic_1d")>=.60
           for s in ("hidden_plus","hidden_minus"))
    g3=all(rate(s,"blind",500,"fitted","hsic_1d")<=.20
           for s in ("hidden_plus","hidden_minus"))
    g4=any(all(effects[s]["hsic_1d"][f]["delta_pp"]>=10
               for s in ("hidden_plus","hidden_minus"))
           for f in ("direction","sample_size","null_model"))
    geom={}
    for s in ("hidden_plus","hidden_minus"):
        rows=groups[s]
        a=[z["alarms"][cell("blind",500,"fitted")]["cqw2_1d"] for z in rows]
        b=[z["alarms"][cell("blind",500,"fitted")]["hsic_1d"] for z in rows]
        only_a=sum(v and not w for v,w in zip(a,b))
        only_b=sum(w and not v for v,w in zip(a,b))
        discord=only_a+only_b
        pv=binomtest(only_a,discord,.5,alternative="greater").pvalue if discord else 1.0
        geom[s]={
            "only_geometry":only_a,"only_hsic":only_b,"discordant":discord,
            "delta_pp":round(100*(sum(a)-sum(b))/TRIALS,4),
            "mcnemar_p_unilateral":round(float(pv),8)}
    g5=all(v["delta_pp"]>=10 and v["mcnemar_p_unilateral"]<.025
           for v in geom.values())
    return {
        "study":"SGV-M20d preregistered 2x2x2 factorial ablation",
        "n_scenarios":len(SCENARIOS),"trials_per_scenario":TRIALS,
        "total_independent_trials":len(SCENARIOS)*TRIALS,
        "factor_cells_per_trial":8,"future_lengths":[500,1800],
        "rates":rates,"paired_effects":effects,
        "null_calibration_checks":null_checks,
        "geometry_mcnemar":geom,
        "gates":{
            "G0_shards_and_paired_observation":True,
            "G1_operational_calibration":g1,
            "G2_oracle_long_power":g2,
            "G3_blind_short_fitted_lacks_power":g3,
            "G4_factor_with_at_least_10pp_both_hidden":g4,
            "G5_geometric_advantage":g5},
        "limits":[
            "Known direction and known null are oracle conditions, not deployable.",
            "Blind 1D projection is not a general rotation-invariant detector.",
            "Bootstrap resamples independent trial, not eight correlated cells.",
            "Null fitting to prefix means rank test not exactly calibrated.",
            "No BTC or trading conclusions; metrics are classical statistics."],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shards",default="reports/m20d/_download")
    p.add_argument("--out",default="reports/m20d/analise.json")
    a=p.parse_args()
    result=analyze(load(a.shards))
    target=Path(a.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("GATES",result["gates"])
    print("GEOMETRY_MC_NEMAR",result["geometry_mcnemar"])
    print("NULL_CALIBRATION",result["null_calibration_checks"])
    for sc in ("hidden_plus","hidden_minus"):
        print(sc,"HSIC_FACTOR_EFFECTS",result["paired_effects"][sc]["hsic_1d"])
        for d,n,r in (("known",1800,"known"),("blind",500,"fitted"),
                      ("known",500,"fitted"),("blind",1800,"fitted"),
                      ("blind",500,"known")):
            ck=cell(d,n,r)
            print(sc,ck,{m:result["rates"][sc][ck][m]["alarms"] for m in METHODS})
    print("G5_GEOMETRY_ADVANTAGE",result["gates"]["G5_geometric_advantage"])


if __name__=="__main__":
    main()
