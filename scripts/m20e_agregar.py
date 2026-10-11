#!/usr/bin/env python3
"""M20e aggregation: fail-closed, paired comparisons and fixed protocol gates."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from scipy.stats import binomtest

SCENARIOS=("null","gaussian_var","hidden_plus","hidden_minus","volatility_memory")
METHODS=("adaptive_hsic","fixed_hsic","scan_hsic",
         "rff3d_hsic","adaptive_cqw2","oracle_hsic")
N=64
LENS=("500","1800")


def wilson(k,n):
    z=1.95996398454
    p=k/n
    den=1+z*z/n
    ctr=(p+z*z/(2*n))/den
    rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [round(max(0.,ctr-rad),4),round(min(1.,ctr+rad),4)]


def load(folder):
    result={}
    for sid,scenario in enumerate(SCENARIOS):
        path=Path(folder)/f"shard_{sid}.json"
        if not path.is_file():
            raise FileNotFoundError("Required shard missing: "+str(path))
        data=json.loads(path.read_text())
        expected=(data["mode"]=="full" and data["seed"]==20261011
                  and data["scenario_ids"]==[sid]
                  and data["scenarios"]==[scenario]
                  and data["trials_per_scenario"]==N
                  and data["prefix"]==800
                  and data["future_short"]==500
                  and data["future_long"]==1800
                  and data["references"]==19
                  and data["n_directions"]==32
                  and data["methods"]==list(METHODS))
        if not expected:
            raise ValueError("Unexpected metadata: "+str(path))
        rows=data["records"]
        if len(rows)!=N or {r["trial"] for r in rows}!=set(range(N)):
            raise ValueError("Incomplete or duplicate trials: "+str(path))
        for row in rows:
            if row["scenario"]!=scenario or set(row["alarms"])!=set(LENS):
                raise ValueError("Scenario/windows mismatched: "+str(path))
            if not (0<=row["oracle_cosine_abs"]<=1.00000001):
                raise ValueError("Invalid cosine")
            if row["selected_direction_index"] not in range(32):
                raise ValueError("Invalid direction index")
            if set(row["observed"])!=set(LENS) or set(row["null_max"])!=set(LENS):
                raise ValueError("Missing recorded diagnostic values")
            for n in LENS:
                if set(row["alarms"][n])!=set(METHODS):
                    raise ValueError("Missing method")
                if set(row["observed"][n])!=set(METHODS):
                    raise ValueError("Missing observed metric")
                if set(row["null_max"][n])!=set(METHODS):
                    raise ValueError("Missing null threshold")
                for m in METHODS:
                    v=row["alarms"][n][m]
                    if type(v) is not bool:
                        raise ValueError("Nonboolean alarm")
                    # Rounded diagnostic values; allow numerical ties within rounding.
                    diff=row["observed"][n][m]-row["null_max"][n][m]
                    if diff>2e-10 and not v:
                        raise ValueError("Alarm mismatches statistic")
                    if diff< -2e-10 and v:
                        raise ValueError("Alarm mismatches statistic")
        result[scenario]=sorted(rows,key=lambda r:r["trial"])
    return result


def mcnemar(rows,method_a,method_b,window="500"):
    a=[r["alarms"][window][method_a] for r in rows]
    b=[r["alarms"][window][method_b] for r in rows]
    only_a=sum(x and not y for x,y in zip(a,b))
    only_b=sum(y and not x for x,y in zip(a,b))
    d=only_a+only_b
    p=float(binomtest(only_a,d,.5,alternative="greater").pvalue) if d else 1.0
    return {"only_a":only_a,"only_b":only_b,"discordant":d,
            "p_one_sided_exact":round(p,8),
            "delta_pp":round(100*(sum(a)-sum(b))/len(rows),4)}


def summarize(groups):
    rates={}
    cosine={}
    paired={}
    for scenario,rows in groups.items():
        rates[scenario]={}
        direction_count=sum(r["oracle_cosine_abs"]>=.8 for r in rows)
        cosine[scenario]={
            "hit80":direction_count,"n":N,"rate":round(direction_count/N,6),
            "wilson95":wilson(direction_count,N),
            "mean_abs_cosine":round(sum(r["oracle_cosine_abs"] for r in rows)/N,6)}
        for n in LENS:
            rates[scenario][n]={}
            for metric in METHODS:
                k=sum(r["alarms"][n][metric] for r in rows)
                rates[scenario][n][metric]={
                    "alarms":k,"n":N,"rate":round(k/N,6),"wilson95":wilson(k,N)}
        if scenario in ("hidden_plus","hidden_minus"):
            paired[scenario]={
                "adaptive_vs_fixed":mcnemar(rows,"adaptive_hsic","fixed_hsic"),
                "adaptive_vs_scan":mcnemar(rows,"adaptive_hsic","scan_hsic"),
                "geometry_vs_adaptive":mcnemar(rows,"adaptive_cqw2","adaptive_hsic")}
    def rate(s,n,m):return rates[s][n][m]["rate"]
    gates={
        "G0_integrity_all_trials_and_tests":True,
        "G1_calibration_on_both_nulls":all(
            rate(s,n,m)<=.125
            for s in ("null","gaussian_var") for n in LENS
            for m in ("adaptive_hsic","scan_hsic")),
        "G2_prefix_direction_recovery_80pct_at_least_60pct":all(
            cosine[s]["rate"]>=.60 for s in ("hidden_plus","hidden_minus")),
        "G3_adaptive_short_power_at_least_35pct":all(
            rate(s,"500","adaptive_hsic")>=.35
            for s in ("hidden_plus","hidden_minus")),
        "G4_adaptive_beats_fixed_10pp_paired_p_lt_025":all(
            paired[s]["adaptive_vs_fixed"]["delta_pp"]>=10
            and paired[s]["adaptive_vs_fixed"]["p_one_sided_exact"]<.025
            for s in ("hidden_plus","hidden_minus")),
        "G5_adaptive_within_10pp_of_scan":all(
            paired[s]["adaptive_vs_scan"]["delta_pp"]>=-10
            for s in ("hidden_plus","hidden_minus")),
        "G6_geometry_beats_adaptive_10pp_p_lt_025":all(
            paired[s]["geometry_vs_adaptive"]["delta_pp"]>=10
            and paired[s]["geometry_vs_adaptive"]["p_one_sided_exact"]<.025
            for s in ("hidden_plus","hidden_minus")),
    }
    return {
        "study":"SGV-M20e causal prefix direction vs blind classical baselines",
        "total_independent_trials":len(SCENARIOS)*N,
        "trials_per_scenario":N,"reference_count_per_trial":19,
        "rates":rates,"direction_recovery":cosine,
        "paired_mcnemar":paired,"gates":gates,
        "limits":[
            "R=19 produces a discrete extreme-rank alarm, no exact validity for a prefix-fitted composite null.",
            "Oracle direction is only for diagnostics and upper-bound comparison.",
            "Adaptive direction selection is conventional Fourier-HSIC, not intrinsic geometry.",
            "Future scan maximizes a statistic over 32 directions in both observed and simulated futures.",
            "No BTC, no market prediction, no claim of causal identification.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shards",default="reports/m20e/_download")
    p.add_argument("--out",default="reports/m20e/analise.json")
    args=p.parse_args()
    summary=summarize(load(args.shards))
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    print("GATES",summary["gates"])
    for scenario in SCENARIOS:
        print("SCENARIO",scenario,"RECOVERY",summary["direction_recovery"][scenario])
        for n in LENS:
            print("WINDOW",n,[(met,s["alarms"],s["n"])
                  for met,s in summary["rates"][scenario][n].items()])
        if scenario in summary["paired_mcnemar"]:
            print("PAIRED",scenario,summary["paired_mcnemar"][scenario])
    print("G6_GEOMETRY_ADVANTAGE",summary["gates"]["G6_geometry_beats_adaptive_10pp_p_lt_025"])


if __name__=="__main__":
    main()
