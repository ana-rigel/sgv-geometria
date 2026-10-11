#!/usr/bin/env python3
"""M20c: fail-closed aggregation of all 400 independently seeded trials."""
import argparse
import json
import math
from pathlib import Path
from scipy.stats import binomtest

SCENARIOS=("null","gaussian_var","hidden_plus","hidden_minus",
           "volatility_memory")
METRICS=("conditional_sw2","rff_hsic","joint_mmd",
         "linear_lag","quadratic_lag","marginal_shift")
N=80


def wilson(k,n):
    z=1.95996398454
    p=k/n
    den=1+z*z/n
    ctr=(p+z*z/(2*n))/den
    rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [round(max(0.,ctr-rad),4),round(min(1.,ctr+rad),4)]


def load(dir_path):
    base=Path(dir_path)
    rows=[]
    for sid,name in enumerate(SCENARIOS):
        f=base/f"shard_{sid}.json"
        if not f.is_file():
            raise FileNotFoundError(str(f))
        data=json.loads(f.read_text())
        if (data["mode"]!="full" or data["seed"]!=20261011
                or data["references_per_trial"]!=19
                or data["prefix_length"]!=800 or data["future_length"]!=500
                or data["trials_per_scenario"]!=N
                or data["scenarios"]!=[name]
                or list(data["metrics"])!=list(METRICS)):
            raise ValueError("Shard metadata mismatch: "+str(f))
        rr=data["records"]
        if len(rr)!=N or {r["trial"] for r in rr}!=set(range(N)):
            raise ValueError("Missing/duplicated trial in "+str(f))
        for r in rr:
            if r["scenario"]!=name or set(r["alarms"])!=set(METRICS):
                raise ValueError("Invalid scenario/metrics")
            if any(type(v) is not bool for v in r["alarms"].values()):
                raise ValueError("Invalid alarm value")
        rows.extend(rr)
    return rows


def summarize(rows):
    groups={name:sorted((r for r in rows if r["scenario"]==name),
                        key=lambda r:r["trial"]) for name in SCENARIOS}
    rates={}
    for name,arr in groups.items():
        rates[name]={}
        for m in METRICS:
            k=sum(r["alarms"][m] for r in arr)
            rates[name][m]={
                "alarms":k,"n":N,"rate":round(k/N,4),"wilson95":wilson(k,N)}
    def rate(s,m):return rates[s][m]["rate"]
    mcnemar={}
    for name in ("hidden_plus","hidden_minus"):
        a=[r["alarms"]["conditional_sw2"] for r in groups[name]]
        b=[r["alarms"]["rff_hsic"] for r in groups[name]]
        only_a=sum(x and not y for x,y in zip(a,b))
        only_b=sum(y and not x for x,y in zip(a,b))
        n_disc=only_a+only_b
        p=binomtest(only_a,n_disc,0.5,alternative="greater").pvalue if n_disc else 1.0
        mcnemar[name]={"only_conditional":only_a,"only_hsic":only_b,
                       "n_discordant":n_disc,"p_one_sided_exact":round(float(p),8),
                       "delta_pct_points":round(100*(sum(a)-sum(b))/N,2)}
    calibration=all(rate(g,m)<=.125 for g in ("null","gaussian_var")
                    for m in ("conditional_sw2","rff_hsic"))
    power=all(max(rate(g,"conditional_sw2"),rate(g,"rff_hsic"))>=.35
              for g in ("hidden_plus","hidden_minus"))
    geometry=all(
        mcnemar[g]["delta_pct_points"]>=10 and
        mcnemar[g]["p_one_sided_exact"]<.025
        for g in ("hidden_plus","hidden_minus"))
    controls=all(rate(g,m)<=.15 for g in ("hidden_plus","hidden_minus")
                 for m in ("linear_lag","quadratic_lag"))
    return {
        "experiment":"SGV-M20c synthetic prefix-only fitted VAR; 19 references",
        "trials_per_scenario":N,
        "number_scenarios":len(SCENARIOS),"metrics":METRICS,
        "rates":rates,"mcnemar":mcnemar,
        "gates":{
            "G0_calibration_operational":calibration,
            "G1_either_detector_power":power,
            "G2_geometry_advantage":geometry,
            "G3_moment_controls_blind":controls,
        },
        "interpretation":{
            "G2":("If false, no evidence of geometric advantage over HSIC"),
            "control":"Model parameters fitted only to prefix; Monte Carlo rank under composite null is not automatically exact.",
            "external_validity":"No BTC, no streaming, no trading, no causal identification.",
            "multiplicity":"Other metric comparisons are exploratory.",
        },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shards",default="reports/m20c/_download")
    p.add_argument("--out",default="reports/m20c/analise.json")
    a=p.parse_args()
    result=summarize(load(a.shards))
    target=Path(a.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("GATES",result["gates"])
    print("MCNEMAR",result["mcnemar"])
    for g,values in result["rates"].items():
        print(g,[(k,v["alarms"],v["n"]) for k,v in values.items()])
    print("G2_GEOMETRY_ADVANTAGE",result["gates"]["G2_geometry_advantage"])


if __name__=="__main__":
    main()
