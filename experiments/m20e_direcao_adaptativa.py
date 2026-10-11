#!/usr/bin/env python3
"""SGV M20e: infer nonlinear-dependence direction on a causal prefix only.
Synthetic trials; no BTC access. A deliberately conventional HSIC selection.

Each trial: one observed path, fixed prefix, 19 *shared* fitted-VAR
reference futures; 500 and 1800 evaluation windows nested in same future.
The 32-direction in-window scan is calibrated with the same scan on refs.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from experiments.m20c_acoplamento_condicional import fit_var, simulate_var, rff_hsic
from experiments.m20d_ablacao_fatorial import make_truth, projected_stats

SEED=20261011
SCENARIOS=("null","gaussian_var","hidden_plus","hidden_minus","volatility_memory")
METHODS=("adaptive_hsic","fixed_hsic","scan_hsic",
         "rff3d_hsic","adaptive_cqw2","oracle_hsic")
PREFIX=800
SHORT=500
LONG=1800
REFERENCES=19
TRIALS=64
LENS=(SHORT,LONG)


def candidate_directions():
    """Fixed, not tuned. 3 axes + 29 Fibonacci-sphere directions."""
    arr=[np.eye(3)[i].copy() for i in range(3)]
    n=29
    golden=np.pi*(3.-np.sqrt(5.))
    for j in range(n):
        z=1.0-2.0*(j+.5)/n
        radius=np.sqrt(max(0.,1-z*z))
        a=j*golden
        v=np.array([radius*np.cos(a),radius*np.sin(a),z])
        # Canonical sign; HSIC itself does not depend on flipping sign.
        if v[np.argmax(np.abs(v))]<0:
            v=-v
        arr.append(v)
    x=np.array(arr)
    x/=np.linalg.norm(x,axis=1,keepdims=True)
    assert x.shape==(32,3)
    return x


DIRECTIONS=candidate_directions()


def directional_hsic(x, directions=DIRECTIONS):
    """Efficient finite Fourier-HSIC at every candidate direction.

    Equivalent to the 1D Fourier cross-covariance of the M20b instrument.
    Returns one scalar per direction; no true hidden direction involved.
    """
    if x.ndim!=2 or x.shape[1]!=3 or len(x)<100:
        raise ValueError("Expected >=100 observations of dimension three")
    u=x@directions.T
    a,b=u[:-1],u[1:]
    freqs=np.array([1.,2.,3.])
    sa=np.sin(a[:,:,None]*freqs)
    ca=np.cos(a[:,:,None]*freqs)
    sb=np.sin(b[:,:,None]*freqs)
    cb=np.cos(b[:,:,None]*freqs)
    fa=np.stack((sa,ca),axis=3).reshape(len(a),len(directions),6)
    fb=np.stack((sb,cb),axis=3).reshape(len(a),len(directions),6)
    fa-=fa.mean(axis=0,keepdims=True)
    fb-=fb.mean(axis=0,keepdims=True)
    cross=np.einsum("tdi,tdj->dij",fa,fb,optimize=True)/len(a)
    return np.einsum("dij,dij->d",cross,cross,optimize=True)


def select_from_prefix(prefix):
    scores=directional_hsic(prefix)
    i=int(np.argmax(scores))
    return i,DIRECTIONS[i].copy(),float(scores[i])


def evaluate(future, direction_index, oracle_direction):
    """No information from prefix enters scores except frozen index."""
    out={}
    for n in LENS:
        x=future[:n]
        hs=directional_hsic(x)
        selected=projected_stats(x@DIRECTIONS[direction_index])
        oracle=projected_stats(x@oracle_direction)
        out[str(n)]={
            "adaptive_hsic":float(hs[direction_index]),
            "fixed_hsic":float(hs[0]),
            "scan_hsic":float(hs.max()),
            "rff3d_hsic":rff_hsic(x[:-1],x[1:]),
            "adaptive_cqw2":selected["cqw2_1d"],
            "oracle_hsic":oracle["hsic_1d"]}
    return out


def run_trial(sid,trial,seed=SEED,n_refs=REFERENCES):
    truth_rng=np.random.default_rng(np.random.SeedSequence([seed,sid,trial,0]))
    trajectory,oracle=make_truth(PREFIX+LONG,sid,truth_rng)
    prefix,observed=trajectory[:PREFIX],trajectory[PREFIX:]
    direction_idx,selected,prefix_score=select_from_prefix(prefix)
    oracle_similarity=float(abs(selected@oracle))
    fitted=fit_var(prefix)
    values=evaluate(observed,direction_idx,oracle)
    maxima={str(n):{m:-float("inf") for m in METHODS} for n in LENS}
    null_rng=np.random.default_rng(np.random.SeedSequence([seed,sid,trial,1]))
    for _ in range(n_refs):
        ref=simulate_var(prefix[-1],fitted,LONG,null_rng)
        null_scores=evaluate(ref,direction_idx,oracle)
        for n in LENS:
            for met in METHODS:
                maxima[str(n)][met]=max(maxima[str(n)][met],null_scores[str(n)][met])
    alarm={str(n):{m:bool(values[str(n)][m]>maxima[str(n)][m])
                   for m in METHODS} for n in LENS}
    return {
        "scenario":SCENARIOS[sid],"trial":trial,
        "selected_direction_index":direction_idx,
        "oracle_cosine_abs":round(oracle_similarity,8),
        "prefix_hsic_selection_score":round(prefix_score,9),
        "alarms":alarm,
        "observed":{k:{m:round(v,10) for m,v in vals.items()}
                    for k,vals in values.items()},
        "null_max":{k:{m:round(v,10) for m,v in vals.items()}
                    for k,vals in maxima.items()},
    }


def run(mode="full",sid=None,outdir="reports/m20e"):
    if mode=="pilot":
        ids=range(5)
        count=2
        seed=SEED+1
        dest=Path(outdir)/"pilot.json"
    elif mode=="full" and sid in range(5):
        ids=[sid]
        count=TRIALS
        seed=SEED
        dest=Path(outdir)/f"shard_{sid}.json"
    else:
        raise ValueError("full requires --scenario 0..4")
    records=[run_trial(s,t,seed) for s in ids for t in range(count)]
    result={
        "study":"M20e prefix-only directional recovery (synthetic)",
        "mode":mode,"seed":seed,"scenarios":[SCENARIOS[i] for i in ids],
        "scenario_ids":list(ids),"trials_per_scenario":count,
        "prefix":PREFIX,"future_short":SHORT,"future_long":LONG,
        "references":REFERENCES,"n_directions":len(DIRECTIONS),
        "methods":list(METHODS),"records":records,
    }
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    summary={}
    for s in ids:
        name=SCENARIOS[s]
        group=[r for r in records if r["scenario"]==name]
        summary[name]={
            "n":len(group),
            "direction_recovery_80pct":sum(x["oracle_cosine_abs"]>=.8 for x in group),
            "alarms_short":{m:sum(int(x["alarms"][str(SHORT)][m]) for x in group)
                            for m in METHODS},
            "alarms_long":{m:sum(int(x["alarms"][str(LONG)][m]) for x in group)
                           for m in METHODS},
        }
    print(json.dumps({"mode":mode,"summary":summary},ensure_ascii=False))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("pilot","full"),default="full")
    p.add_argument("--scenario",type=int)
    p.add_argument("--outdir",default="reports/m20e")
    a=p.parse_args()
    run(a.mode,a.scenario,a.outdir)
