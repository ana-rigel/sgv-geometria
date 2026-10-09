#!/usr/bin/env python3
"""SGV-M4: SF1 adequacy, volume-memory and seasonal ablations.

Causal prefix fit, same SF1 simulated return/flow paths across all variants.
This is descriptive calibration, not an intrinsic-geometry or trading claim.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import fit_sf1,simulate_sf1,flow_coordinates
from experiments.auditoria_adequacao_sf1 import diagnostics
from experiments.persistencia_dependencia import checked_exploratory_month

PREFIX={"1m":5000,"1h":2000}
WINDOW={"1m":1500,"1h":1008}
STEP={"1m":60000,"1h":3600000}
ORIGINS=4
SIMS=4
BURN=1700
SEED=20261009
LAGS=(1,2,5,10)
KEYS=("nu_acf1","nu_acf10","nu_std","iota_acf1","rho_z_iota","rho_abs_z_nu","abs_z_acf1")


def season(ts):
    t=np.asarray(ts,np.int64)
    day=(t%(86400_000))/86400_000
    return np.column_stack([np.sin(2*np.pi*day),np.cos(2*np.pi*day)])


def regress_volume(frame,variant,step):
    """Fit only prefix. Ridge standardized slopes with stabilised AR lag weights."""
    if variant not in ("memory","season","both"):
        raise ValueError("Unknown ablation")
    ell=np.log(np.maximum(frame.volume.to_numpy(float),1e-12))
    z=flow_coordinates(frame)["z"].to_numpy(float)
    timestamps=frame.timestamp.to_numpy(np.int64)
    usable=np.arange(max(LAGS)+1,len(frame))
    usable=usable[np.isfinite(z[usable])]
    if len(usable)<1500:raise ValueError("Too little clean prefix")
    needs_season=variant in ("season","both")
    if needs_season:
        if timestamps[-1]-timestamps[0] < 3*86400_000 or len(frame)<3000:
            raise ValueError("Insufficient complete day cycles for season")
    ls=(1,) if variant=="season" else LAGS
    mat=np.column_stack(
        [*[ell[usable-lag] for lag in ls],np.abs(z[usable]),z[usable],
         *([season(timestamps[usable])[:,k] for k in range(2)] if needs_season else [])]
    )
    center=mat.mean(0)
    sd=mat.std(0)
    sd=np.maximum(sd,1e-6)
    X=(mat-center)/sd
    y=ell[usable]
    ym=y.mean()
    beta=np.linalg.solve(X.T@X+np.eye(X.shape[1])*2.,X.T@(y-ym))
    raw=beta/sd
    lag_coef=raw[:len(ls)]
    norm=np.sum(np.abs(lag_coef))
    if norm>.97:
        raw[:len(ls)]*=.97/norm
    # recompute intercept/residual after enforcing lag stability
    intercept=float(np.mean(y-mat@raw))
    residual=y-intercept-mat@raw
    # centered residuals; preserve observed innovation distribution
    residual-=residual.mean()
    return {"variant":variant,"lags":ls,"coef":raw,
            "intercept":intercept,"residual":residual,
            "season":needs_season,
            "lag_norm":float(np.sum(np.abs(raw[:len(ls)])))}


def ablated_path(sf1path,prefix,fit,step,seed):
    """Price and taker_buy copied unchanged. Only reconstructed volume differs."""
    rng=np.random.default_rng(seed)
    df=sf1path.copy()
    x=flow_coordinates(df)
    z=x["z"].to_numpy(dtype=float,copy=True)
    z[~np.isfinite(z)]=0.
    ts=(int(prefix.timestamp.iloc[-1])+np.arange(1-BURN,len(df)+1-BURN)*step)
    df["timestamp"]=ts
    prev=list(np.log(np.maximum(prefix.volume.to_numpy(float)[-10:],1e-12)))
    eps=fit["residual"][rng.integers(0,len(fit["residual"]),len(df))]
    coeff=fit["coef"]
    out=np.empty(len(df))
    for j in range(len(df)):
        features=[*[prev[-lag] for lag in fit["lags"]],
                  abs(z[j]),z[j]]
        if fit["season"]:
            features.extend(season([ts[j]])[0].tolist())
        ell=fit["intercept"]+np.dot(coeff,features)+eps[j]
        if not np.isfinite(ell) or abs(ell)>80:
            raise ValueError("Unstable extended volume path")
        out[j]=ell
        prev.append(float(ell))
    volume=np.exp(out)
    original_iota=(2*df.taker_buy.to_numpy(float) /
                   df.volume.to_numpy(float)-1)
    df["volume"]=volume
    df["taker_buy"]=(original_iota+1)/2*volume
    return df


def compare_one(prefix,window,step,seed,sims=SIMS):
    sf1=fit_sf1(prefix)
    if not sf1.garch.get("converged",False):
        raise ValueError("SF1 GARCH fit not converged")
    y=flow_coordinates(__import__("pandas").concat([prefix,window],ignore_index=True))
    obs=diagnostics(y[["z","iota","nu"]].to_numpy(float)[-len(window):])
    fits={}
    failures={}
    for v in ("memory","season","both"):
        try:
            fits[v]=regress_volume(prefix,v,step)
        except ValueError as ex:
            failures[v]=str(ex)
    paths={key:[] for key in ("sf1",*fits)}
    price_flow_checked=True
    for j in range(sims):
        base=simulate_sf1(sf1,len(window)+BURN,seed=seed+j*103,step_ms=step)
        base["timestamp"]=(int(prefix.timestamp.iloc[-1])+
                           np.arange(1-BURN,len(base)+1-BURN)*step)
        original=flow_coordinates(base)[["z","iota","nu"]].to_numpy(float)[-len(window):]
        paths["sf1"].append(diagnostics(original))
        for v,fit in fits.items():
            new=ablated_path(base,prefix,fit,step,seed=seed+10000+j*103)
            mod=flow_coordinates(new)[["z","iota","nu"]].to_numpy(float)[-len(window):]
            if not (np.allclose(original[:,0],mod[:,0],atol=1e-10,rtol=0) and
                    np.allclose(original[:,1],mod[:,1],atol=1e-10,rtol=0)):
                price_flow_checked=False
                raise AssertionError("Price or aggressive-flow path changed!")
            paths[v].append(diagnostics(mod))
    metrics={}
    for name,series in paths.items():
        metrics[name]={}
        for k in KEYS:
            med=float(np.median([p[k] for p in series]))
            metrics[name][k]={"observed":float(obs[k]),"sim_median":med,
                               "abs_error":float(abs(obs[k]-med))}
    return {"asof_ms":int(window.timestamp.iloc[-1]+step),
            "n_sim":sims,"price_flow_invariant":price_flow_checked,
            "model_coefficients":{k:{"lag_norm":v["lag_norm"],
                        "lags":list(v["lags"]),"season":v["season"]}
                        for k,v in fits.items()},
            "unavailable":failures,"metrics":metrics}


def summarize(rows):
    variants=("sf1","memory","season","both")
    output={"n_origins":len(rows),"variants":{}}
    for v in variants:
        selected=[r for r in rows if v in r["metrics"]]
        if not selected:
            output["variants"][v]={"n":0,"status":"unavailable"}
            continue
        a={"n":len(selected)}
        for key in KEYS:
            a[key+"_median_abs_error"]=float(np.median(
                [r["metrics"][v][key]["abs_error"] for r in selected]))
            a[key+"_median_sim"]=float(np.median(
                [r["metrics"][v][key]["sim_median"] for r in selected]))
            a[key+"_median_real"]=float(np.median(
                [r["metrics"][v][key]["observed"] for r in selected]))
        output["variants"][v]=a
    return output


def synthetic():
    from sgvgeo.flow import default_sf1
    a=simulate_sf1(default_sf1(),7800,seed=123)
    prefix=a.iloc[:5000]
    fits=[regress_volume(prefix,v,60000) for v in ("memory","season","both")]
    b=simulate_sf1(default_sf1(),3000,seed=124)
    out={}
    for i,f in enumerate(fits):
        changed=ablated_path(b,prefix,f,60000,seed=125)
        out[f["variant"]]={"original_close_unchanged":bool(np.array_equal(
            changed.close.to_numpy(),b.close.to_numpy())),
            "iota_unchanged":bool(np.allclose(
                (2*changed.taker_buy/changed.volume-1).to_numpy(),
                (2*b.taker_buy/b.volume-1).to_numpy())),
            "positive_volume":bool((changed.volume>0).all())}
    return {"status":"M4_CALIBRACAO","variants":out,
            "warning":"Engineering test; not market improvement evidence"}


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths:raise FileNotFoundError("Exploration files not found")
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    w=WINDOW[interval];pre=PREFIX[interval];step=STEP[interval]
    starts=list(range(pre,len(df)-w+1,w))
    starts=[i for i in starts if np.all(np.diff(
        df.timestamp.to_numpy(np.int64)[i-pre:i+w])==step)]
    if not starts:raise RuntimeError("No contiguous sample")
    selected=np.linspace(0,len(starts)-1,min(ORIGINS,len(starts)),dtype=int)
    rows=[]
    failures=[]
    for j,k in enumerate(selected):
        start=starts[int(k)]
        try:
            rows.append(compare_one(df.iloc[start-pre:start].copy(),
                                    df.iloc[start:start+w].copy(),
                                    step,SEED+j*100))
        except (ValueError,AssertionError,np.linalg.LinAlgError) as ex:
            failures.append({"start":start,"error":str(ex)})
    if not rows:raise RuntimeError("No valid GARCH/volume model")
    filename=ROOT/"reports"/f"SGV_M4_{interval}_comparison.csv"
    filename.parent.mkdir(parents=True,exist_ok=True)
    with filename.open("w",newline="",encoding="utf8") as f:
        cw=csv.DictWriter(f,fieldnames=["asof_ms","variant","metric",
                        "observed","sim_median","abs_error"])
        cw.writeheader()
        for row in rows:
            for name,metrics in row["metrics"].items():
                for key,vals in metrics.items():
                    cw.writerow({"asof_ms":row["asof_ms"],"variant":name,
                                 "metric":key,**vals})
    return {"status":"M4_BTC_EXPLORATORY","interval":interval,
            "n_valid":len(rows),"n_failed":len(failures),"failed":failures,
            "n_eligible_candidates":len(starts),
            "no_confirmatory_used":True,
            "same_price_and_flow_paths":all(r["price_flow_invariant"] for r in rows),
            "results":summarize(rows),"unavailable":{
                str(r["asof_ms"]):r["unavailable"] for r in rows if r["unavailable"]},
            "limits":["Four simulations/origin; exploratory medians only",
                      "Model variants alter volume only, and baseline unchanged",
                      "Seasonal estimation needs >=3 day cycles",
                      "Volume lags and clock can still miss regime shifts",
                      "Improved SF1 fit does not imply intrinsic geometry or market stress"]}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--interval",required=True,choices=("synthetic","1m","1h"))
    args=parser.parse_args()
    result=synthetic() if args.interval=="synthetic" else real(args.interval)
    dest=ROOT/"reports"/f"SGV_M4_{args.interval}.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
