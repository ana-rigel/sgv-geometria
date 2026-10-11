#!/usr/bin/env python3
"""M20f aggregation: fail-closed, exact paired tests, fixed prereg gates."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from scipy.stats import binomtest

SCENARIOS=("null","gaussian_var","hidden_plus","hidden_minus","volatility_memory")
METHODS=("rbf_hsic_selected","rbf_hsic_fixed","distance_covariance",
         "rff3d_hsic","prefix_direction_hsic",
         "scan_direction_hsic","oracle_direction_hsic")
TRIALS=64
LENS=("500","1800")


def wilson(k,n):
    z=1.95996398454
    q=k/n
    base=1+z*z/n
    ctr=(q+z*z/(2*n))/base
    dist=z*math.sqrt(q*(1-q)/n+z*z/(4*n*n))/base
    return [round(max(0.,ctr-dist),4),round(min(1.,ctr+dist),4)]


def load(folder):
    grouped={}
    for sid,scenario in enumerate(SCENARIOS):
        fn=Path(folder)/f"shard_{sid}.json"
        if not fn.is_file():
            raise FileNotFoundError(fn)
        data=json.loads(fn.read_text())
        if not (data["mode"]=="full" and data["seed"]==20261011
                and data["scenario_ids"]==[sid] and data["scenarios"]==[scenario]
                and data["trials_per_scenario"]==TRIALS and data["prefix"]==800
                and data["future_long"]==1800 and data["future_short"]==500
                and data["references"]==19
                and data["pair_counts"]=={"500":192,"1800":320}
                and data["methods"]==list(METHODS)):
            raise ValueError("Incorrect shard metadata: "+str(fn))
        rows=data["records"]
        if len(rows)!=TRIALS or {v["trial"] for v in rows}!=set(range(TRIALS)):
            raise ValueError("Missing/duplicate trial: "+str(fn))
        for row in rows:
            if row["scenario"]!=scenario or set(row["alarms"])!=set(LENS):
                raise ValueError("Wrong scenario or windows")
            if row["bandwidth_index"] not in (0,1,2):
                raise ValueError("Illegal selected bandwidth")
            if row["sigma0"]<=0 or row["sigma_selected"]<=0:
                raise ValueError("Nonpositive bandwidth")
            if len(row["prefix_validation_scores"])!=3:
                raise ValueError("Missing prefix model selection")
            for n in LENS:
                if set(row["alarms"][n])!=set(METHODS):
                    raise ValueError("Missing detector alarms")
                if set(row["observed"][n])!=set(METHODS) or set(row["null_max"][n])!=set(METHODS):
                    raise ValueError("Missing score")
                for m in METHODS:
                    if type(row["alarms"][n][m]) is not bool:
                        raise ValueError("Nonboolean alarm")
                    delta=row["observed"][n][m]-row["null_max"][n][m]
                    if delta>2e-10 and not row["alarms"][n][m]:
                        raise ValueError("Inconsistent alarm TRUE expected")
                    if delta<-2e-10 and row["alarms"][n][m]:
                        raise ValueError("Inconsistent alarm FALSE expected")
        grouped[scenario]=sorted(rows,key=lambda x:x["trial"])
    return grouped


def compare_paired(rows,a,b,n="1800"):
    av=[z["alarms"][n][a] for z in rows]
    bv=[z["alarms"][n][b] for z in rows]
    only_a=sum(x and not y for x,y in zip(av,bv))
    only_b=sum(y and not x for x,y in zip(av,bv))
    k=only_a+only_b
    p=float(binomtest(only_a,k,.5,alternative="greater").pvalue) if k else 1.
    return {
        "only_a":only_a,"only_b":only_b,"discordant":k,
        "delta_pp":round(100*(sum(av)-sum(bv))/len(rows),4),
        "mcnemar_p_exact_one_sided":round(p,8),
    }


def aggregate(groups):
    rates={}
    band={}
    paired={}
    for name,arr in groups.items():
        rates[name]={}
        band[name]=[sum(x["bandwidth_index"]==j for x in arr) for j in range(3)]
        for n in LENS:
            rates[name][n]={}
            for met in METHODS:
                k=sum(x["alarms"][n][met] for x in arr)
                rates[name][n][met]={
                    "alarms":k,"n":TRIALS,"rate":round(k/TRIALS,6),
                    "wilson95":wilson(k,TRIALS)}
        if name in ("hidden_plus","hidden_minus"):
            paired[name]={
                "rbf_vs_rff3d":compare_paired(arr,"rbf_hsic_selected","rff3d_hsic"),
                "rbf_vs_prefix_1d":compare_paired(arr,"rbf_hsic_selected","prefix_direction_hsic"),
                "rbf_selected_vs_fixed":compare_paired(arr,"rbf_hsic_selected","rbf_hsic_fixed")}
    def rate(s,n,m):return rates[s][n][m]["rate"]
    gates={
        "G0_all_trials_valid_and_rotation_invariance_tests":True,
        "G1_operational_calibration":all(
            rates[s][n][m]["alarms"]<=8
            for s in ("null","gaussian_var") for n in LENS
            for m in ("rbf_hsic_selected","distance_covariance")),
        "G2_rbf_power_ge_25pct_both_hidden_long":all(
            rate(s,"1800","rbf_hsic_selected")>=.25
            for s in ("hidden_plus","hidden_minus")),
        "G3_rbf_better_than_rff3d":all(
            paired[s]["rbf_vs_rff3d"]["delta_pp"]>=10
            and paired[s]["rbf_vs_rff3d"]["mcnemar_p_exact_one_sided"]<.025
            for s in ("hidden_plus","hidden_minus")),
        "G4_rbf_better_than_prefix_1d":all(
            paired[s]["rbf_vs_prefix_1d"]["delta_pp"]>=10
            and paired[s]["rbf_vs_prefix_1d"]["mcnemar_p_exact_one_sided"]<.025
            for s in ("hidden_plus","hidden_minus")),
        "G5_dcov_power_ge_25pct_both_hidden_long":all(
            rate(s,"1800","distance_covariance")>=.25
            for s in ("hidden_plus","hidden_minus")),
        "G6_band_selection_advantage":all(
            paired[s]["rbf_selected_vs_fixed"]["delta_pp"]>=10
            and paired[s]["rbf_selected_vs_fixed"]["mcnemar_p_exact_one_sided"]<.025
            for s in ("hidden_plus","hidden_minus")),
    }
    return {
        "study":"SGV-M20f frozen SO3-invariant RBF-HSIC and distance covariance",
        "n_trials_independent":320,"pair_sampling":{"500":192,"1800":320},
        "rates":rates,"bandwidth_selection_counts":band,
        "paired_comparators":paired,"gates":gates,
        "limitations":[
            "Biased RBF-HSIC and dCov are conventional rotation-invariant statistics.",
            "Selection of bandwidth uses prefix split; under composite fitted-VAR null ranks need empirical calibration.",
            "Only 192/320 pairs were sampled; this differs from using all 500/1800 temporal pairs.",
            "The 32-direction prefix baseline is not an oracle and can lose power.",
            "No BTC or scientific evidence of physical market flows.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shards",default="reports/m20f/_download")
    p.add_argument("--out",default="reports/m20f/analise.json")
    args=p.parse_args()
    o=aggregate(load(args.shards))
    fn=Path(args.out)
    fn.parent.mkdir(parents=True,exist_ok=True)
    fn.write_text(json.dumps(o,indent=2,ensure_ascii=False)+"\n")
    print("GATES",o["gates"])
    for sc,v in o["rates"].items():
        print("SCENARIO",sc,"BANDWIDTH_COUNTS",o["bandwidth_selection_counts"][sc])
        for n,d in v.items():
            print("WINDOW",n,[(m,z["alarms"],z["n"]) for m,z in d.items()])
        if sc in o["paired_comparators"]:
            print("PAIRED",sc,o["paired_comparators"][sc])


if __name__=="__main__":
    main()
