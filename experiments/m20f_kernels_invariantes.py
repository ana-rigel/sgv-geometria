#!/usr/bin/env python3
"""M20f: exactly rotation-invariant Gaussian-RBF HSIC and distance covariance.
Only synthetic data. Per trial: bandwidth learned on training/validation
prefix, Gaussian VAR fitted on prefix, 19 future null references.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from experiments.m20c_acoplamento_condicional import fit_var, simulate_var, rff_hsic
from experiments.m20d_ablacao_fatorial import make_truth
from experiments.m20e_direcao_adaptativa import DIRECTIONS,select_from_prefix

SEED=20261011
SCENARIOS=("null","gaussian_var","hidden_plus","hidden_minus","volatility_memory")
METHODS=("rbf_hsic_selected","rbf_hsic_fixed","distance_covariance",
         "rff3d_hsic","prefix_direction_hsic",
         "scan_direction_hsic","oracle_direction_hsic")
PREFIX=800
FUTURE=1800
LENGTHS=(500,1800)
N_PAIRS=(192,320)
N_REF=19
TRIALS=64
FACTORS=(.5,1.,2.)


def pairs(path,n):
    count=N_PAIRS[LENGTHS.index(n)]
    ids=np.linspace(0,n-2,count,dtype=int)
    if len(np.unique(ids))!=count:
        raise ValueError("Duplicate sampled indices")
    return path[ids],path[ids+1]


def distance_squared(x):
    xx=np.einsum("ij,ij->i",x,x)
    z=np.maximum(xx[:,None]+xx[None,:]-2*(x@x.T),0.)
    np.fill_diagonal(z,0.)
    return z


def distance_cross_squared(x,y):
    a=np.einsum("ij,ij->i",x,x)
    b=np.einsum("ij,ij->i",y,y)
    return np.maximum(a[:,None]+b[None,:]-2*(x@y.T),0.)


def center(a):
    return a-a.mean(axis=0,keepdims=True)-a.mean(axis=1,keepdims=True)+a.mean()


def hsic_from_d2(dx,dy,sigma):
    if sigma<=0:
        raise ValueError("bandwidth must be positive")
    k=np.exp(-dx/(2*sigma*sigma))
    l=np.exp(-dy/(2*sigma*sigma))
    k=center(k)
    l=center(l)
    return max(0.,float(np.mean(k*l)))


def distance_covariance_from_d2(dx,dy):
    a=center(np.sqrt(dx))
    b=center(np.sqrt(dy))
    return max(0.,float(np.mean(a*b)))


def directional_pair_hsic(x,y,directions=DIRECTIONS):
    """Same finite 1D Fourier-HSIC over paired x_t,y_t (not fake adjacency)."""
    a=x@directions.T
    b=y@directions.T
    f=np.array([1.,2.,3.])
    xa=np.stack((np.sin(a[:,:,None]*f),
                 np.cos(a[:,:,None]*f)),axis=3).reshape(len(a),len(directions),6)
    yb=np.stack((np.sin(b[:,:,None]*f),
                 np.cos(b[:,:,None]*f)),axis=3).reshape(len(b),len(directions),6)
    xa-=xa.mean(axis=0,keepdims=True)
    yb-=yb.mean(axis=0,keepdims=True)
    cross=np.einsum("tdi,tdj->dij",xa,yb,optimize=True)/len(x)
    return np.einsum("dij,dij->d",cross,cross,optimize=True)


def bandwidth_from_prefix(prefix):
    """train[0:400] -> median sigma0; validate[400:800] -> multiplier."""
    train=prefix[:400]
    ids=np.linspace(0,len(train)-1,120,dtype=int)
    dis=np.sqrt(distance_squared(train[ids]))
    vals=dis[np.triu_indices(len(ids),1)]
    vals=vals[vals>1e-12]
    sigma0=max(1e-6,float(np.median(vals))) if len(vals) else 1e-6
    val=prefix[400:]
    x,y=pairs_from_validation(val)
    dx,dy=distance_squared(x),distance_squared(y)
    vals=[hsic_from_d2(dx,dy,sigma0*fac) for fac in FACTORS]
    arg=int(np.argmax(vals))
    return sigma0, sigma0*FACTORS[arg], arg,vals


def pairs_from_validation(val):
    ids=np.linspace(0,len(val)-2,192,dtype=int)
    return val[ids],val[ids+1]


def score_pairs(x,y,sigma0,sigma_selected,direction_index,oracle):
    dx,dy=distance_squared(x),distance_squared(y)
    h=directional_pair_hsic(x,y)
    xo=x@oracle
    yo=y@oracle
    hoo=directional_pair_hsic(xo[:,None],yo[:,None],np.array([[1.]]))[0]
    return {
        "rbf_hsic_selected":hsic_from_d2(dx,dy,sigma_selected),
        "rbf_hsic_fixed":hsic_from_d2(dx,dy,sigma0),
        "distance_covariance":distance_covariance_from_d2(dx,dy),
        "rff3d_hsic":rff_hsic(x,y),
        "prefix_direction_hsic":float(h[direction_index]),
        "scan_direction_hsic":float(h.max()),
        "oracle_direction_hsic":float(hoo),
    }


def scores(path,sigma0,sigma_selected,direction_index,oracle):
    results={}
    for n in LENGTHS:
        x,y=pairs(path,n)
        results[str(n)]=score_pairs(x,y,sigma0,sigma_selected,direction_index,oracle)
    return results


def one_trial(sid,trial,seed=SEED,n_refs=N_REF):
    truth_rng=np.random.default_rng(np.random.SeedSequence([seed,sid,trial,0]))
    trajectory,oracle=make_truth(PREFIX+FUTURE,sid,truth_rng)
    prefix,future=trajectory[:PREFIX],trajectory[PREFIX:]
    sigma0,sigma,bandidx,vscores=bandwidth_from_prefix(prefix)
    diridx,direction,dirscore=select_from_prefix(prefix)
    observed=scores(future,sigma0,sigma,diridx,oracle)
    maxima={str(n):{m:-float("inf") for m in METHODS} for n in LENGTHS}
    fitted=fit_var(prefix)
    null_rng=np.random.default_rng(np.random.SeedSequence([seed,sid,trial,1]))
    for _ in range(n_refs):
        ref=simulate_var(prefix[-1],fitted,FUTURE,null_rng)
        rv=scores(ref,sigma0,sigma,diridx,oracle)
        for n in LENGTHS:
            key=str(n)
            for method in METHODS:
                maxima[key][method]=max(maxima[key][method],rv[key][method])
    alarm={str(n):{method:bool(observed[str(n)][method]>maxima[str(n)][method])
                   for method in METHODS} for n in LENGTHS}
    return {
        "scenario":SCENARIOS[sid],"trial":trial,
        "sigma0":round(sigma0,9),"sigma_selected":round(sigma,9),
        "bandwidth_index":bandidx,"prefix_validation_scores":[round(s,10) for s in vscores],
        "direction_index":diridx,"oracle_cosine_abs":round(float(abs(direction@oracle)),8),
        "alarms":alarm,
        "observed":{k:{m:round(v,11) for m,v in vals.items()}
                    for k,vals in observed.items()},
        "null_max":{k:{m:round(v,11) for m,v in vals.items()}
                    for k,vals in maxima.items()},
    }


def run(mode,sid=None,outdir="reports/m20f"):
    if mode=="pilot":
        ids=range(5); n=2; seed=SEED+1
        dest=Path(outdir)/"piloto.json"
    elif mode=="full" and sid in range(5):
        ids=[sid]; n=TRIALS; seed=SEED
        dest=Path(outdir)/f"shard_{sid}.json"
    else:
        raise ValueError("full requires --scenario 0..4")
    rows=[one_trial(s,t,seed=seed) for s in ids for t in range(n)]
    result={
        "study":"M20f rotation invariant kernel synthetic only",
        "mode":mode,"seed":seed,"scenario_ids":list(ids),
        "scenarios":[SCENARIOS[i] for i in ids],
        "trials_per_scenario":n,"prefix":PREFIX,"future_long":FUTURE,
        "future_short":LENGTHS[0],"references":N_REF,
        "pair_counts":dict(zip(map(str,LENGTHS),N_PAIRS)),
        "methods":list(METHODS),"records":rows,
    }
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    summary={}
    for s in ids:
        name=SCENARIOS[s]
        group=[r for r in rows if r["scenario"]==name]
        summary[name]={
            "n":len(group),"selected_bandwidths":[sum(r["bandwidth_index"]==i for r in group) for i in range(3)],
            "short":{m:sum(int(r["alarms"]["500"][m]) for r in group) for m in METHODS},
            "long":{m:sum(int(r["alarms"]["1800"][m]) for r in group) for m in METHODS},
        }
    print(json.dumps({"mode":mode,"summary":summary},ensure_ascii=False))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("pilot","full"),default="full")
    p.add_argument("--scenario",type=int)
    p.add_argument("--outdir",default="reports/m20f")
    a=p.parse_args()
    run(a.mode,a.scenario,a.outdir)
