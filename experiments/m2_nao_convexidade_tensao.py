#!/usr/bin/env python3
"""SGV-M2: nonconvexity of fitted HDRs versus separately calibrated discrepancy.

The shape of a density is not an intrinsic Fisher manifold or causal market force.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from experiments.isosuperficies_morfometria import (
    make_grid,density_values,hdr_thresholds,extract_mesh,describe_mesh,
    curvatures,implicit_curvatures,SEED)
from experiments.precisao_formas_3d import split_historical
from experiments.persistencia_dependencia import checked_exploratory_month
from sgvgeo.flow import flow_coordinates
from sgvgeo.data import load_binance_klines

W={'1m':1500,'1h':1008}
STEP={'1m':60000,'1h':3600000}
B={'1m':15,'1h':12}
ALPHAS=(.25,.5,.75)
MAX_WINDOWS=10

def morphology(sample,model='mixture',alpha=.5,n=35,seed=SEED):
    pts,spacing=make_grid(n)
    density,params=density_values(sample,pts,model,seed,with_model=True)
    field=density.reshape(n,n,n)
    threshold,coverage=hdr_thresholds(field,spacing)
    mesh,trunc=extract_mesh(field,threshold[alpha]['tau'],spacing)
    prop=describe_mesh(mesh,truncated=trunc,coverage=coverage,implicit_model=params)
    if not prop['quality_pass']:
        return {'valid':False,'reason':prop['invalid_reason']}
    K,H=implicit_curvatures(mesh.vertices,params)
    _,_,areas=curvatures(mesh.vertices,mesh.faces)
    r=(3*prop['volume']/(4*np.pi))**(1/3)
    neg=np.maximum(0.,-K*r*r)
    hull_volume=float(mesh.convex_hull.volume)
    if hull_volume<=0: return {'valid':False,'reason':'invalid_hull'}
    ratio=float(prop['volume']/hull_volume)
    if not (0<ratio<=1.05):return {'valid':False,'reason':'invalid_ratio'}
    return {'valid':True,
            'negative_intensity':float(np.average(neg,weights=areas)),
            'area_K_negative':float(areas[K<0].sum()/areas.sum()),
            'area_Kr2_lt_minus_01':float(areas[K*r*r<-.1].sum()/areas.sum()),
            'convex_hull_deficit':float(max(0.,1-ratio))}

def fit_conditional(previous):
    x=np.asarray(previous,float)
    if x.ndim!=2 or x.shape[1]!=3 or len(x)<100 or not np.isfinite(x).all():
        raise ValueError('Invalid prior-only calibration')
    A=np.column_stack([np.ones(len(x)),x[:,1],x[:,2]])
    beta=np.linalg.solve(A.T@A+np.diag([0,1e-5,1e-5]),A.T@x[:,0])
    sigma=float(np.std(x[:,0]-A@beta,ddof=3))
    if sigma<1e-10:raise ValueError('Degenerate residual')
    return beta,sigma

def conditional_rmse(x,beta,sigma):
    A=np.column_stack([np.ones(len(x)),x[:,1],x[:,2]])
    return float(np.sqrt(np.mean(((x[:,0]-A@beta)/sigma)**2)))

def measure_window(x,seed=SEED,levels=ALPHAS,n=35):
    x=np.asarray(x,float)
    cut=int(.3*len(x))
    beta,sd=fit_conditional(x[:cut])
    rem=x[cut:]
    mid=len(rem)//2
    t0=conditional_rmse(rem[:mid],beta,sd)
    t1=conditional_rmse(rem[mid:],beta,sd)
    a,b=split_historical(x)
    out={'tension_a':t0,'tension_b':t1,'delta_tension':t1-t0}
    for kind in ('gaussian','mixture'):
        for alpha in levels:
            key=f'{kind}_{int(alpha*100)}'
            A=morphology(a,kind,alpha,n,seed)
            B=morphology(b,kind,alpha,n,seed+1)
            valid=A['valid'] and B['valid']
            out[key+'_valid']=valid
            if valid:
                for metric in ('negative_intensity','area_Kr2_lt_minus_01',
                               'convex_hull_deficit'):
                    out[key+'_'+metric+'_a']=A[metric]
                    out[key+'_'+metric+'_b']=B[metric]
                    out[key+'_'+metric+'_delta']=B[metric]-A[metric]
            else:
                out[key+'_reason']=str(A.get('reason') or B.get('reason'))
    return out

def moving_block(rng,x,length):
    n=len(x)
    starts=rng.integers(n,size=(n+length-1)//length)
    ids=(starts[:,None]+np.arange(length)[None,:])%n
    return x[ids.ravel()[:n]]

def bootstrap_shape(x,seed=SEED,block=15,reps=8):
    a,b=split_historical(x)
    base_a=morphology(a,seed=seed)
    base_b=morphology(b,seed=seed+1)
    if not(base_a['valid'] and base_b['valid']):
        return {'status':'invalid_original'}
    rng=np.random.default_rng(seed)
    values=[]
    for j in range(reps):
        aa=morphology(moving_block(rng,a,block),seed=seed+100+2*j)
        bb=morphology(moving_block(rng,b,block),seed=seed+101+2*j)
        if aa['valid'] and bb['valid']:
            values.append(bb['negative_intensity']-aa['negative_intensity'])
    if len(values)<max(3,reps//2):
        return {'status':'insufficient_resamples','valid':len(values)}
    return {'status':'descriptive_only',
            'observed_delta':base_b['negative_intensity']-base_a['negative_intensity'],
            'bootstrap_p10_p50_p90':[float(v) for v in np.quantile(values,[.1,.5,.9])],
            'valid_resamples':len(values)}

def association(rows):
    good=[r for r in rows if r.get('mixture_50_valid')]
    if len(good)<5:return {'status':'insufficient_pairs','n':len(good)}
    X=np.array([r['mixture_50_negative_intensity_delta'] for r in good])
    Y=np.array([r['delta_tension'] for r in good])
    if np.std(X)<1e-12 or np.std(Y)<1e-12:
        return {'status':'degenerate_variation','n':len(good)}
    return {'status':'exploratory','n':len(good),'spearman':float(spearmanr(X,Y).statistic),
            'warning':'Not causal or confirmatory; no significance claim.'}

def synthetic():
    rng=np.random.default_rng(62)
    x=rng.normal(size=(1500,3))
    y=x.copy()
    y[1000:,0]+=1.0*np.sign(y[1000:,1])
    base=measure_window(x,levels=(.5,))
    modified=measure_window(y,levels=(.5,))
    return {'status':'M2_SYNTHETIC',
            'gaussian_intensity_a':base.get('gaussian_50_negative_intensity_a'),
            'gaussian_intensity_b':base.get('gaussian_50_negative_intensity_b'),
            'future_change_detected':base['delta_tension']!=modified['delta_tension'],
            'bootstrap':bootstrap_shape(x,reps=5)}

def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('No exploration klines')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    v=flow_coordinates(df)[['z','iota','nu']].to_numpy(float)
    time=df.timestamp.to_numpy(np.int64)
    win=W[interval]
    samples=[]
    for end in range(win,len(v)+1,win):
        x=v[end-win:end]
        times=time[end-win:end]
        if np.isfinite(x).all() and np.all(np.diff(times)==STEP[interval]):
            samples.append((end,int(times[-1]+STEP[interval]),x))
    if not samples:raise RuntimeError('No continuous exploratory windows')
    chosen=np.linspace(0,len(samples)-1,min(MAX_WINDOWS,len(samples)),dtype=int)
    rows=[]
    for j,k in enumerate(chosen):
        end,asof,x=samples[int(k)]
        result=measure_window(x,seed=SEED+end)
        result['asof_ms']=asof
        result['window_end_index']=int(end)
        if j in (0,len(chosen)-1):
            result['bootstrap_HDR50']=bootstrap_shape(x,seed=SEED+end,
                                    block=B[interval],reps=8)
        rows.append(result)
    out=ROOT/'reports'/f'SGV_M2_{interval}_janelas.csv'
    out.parent.mkdir(exist_ok=True,parents=True)
    names=list(dict.fromkeys(key for r in rows for key in r))
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=names)
        w.writeheader()
        for r in rows:
            w.writerow({k:json.dumps(v) if isinstance(v,dict) else v for k,v in r.items()})
    metrics={}
    for model in ('gaussian','mixture'):
        for a in (25,50,75):
            key=f'{model}_{a}'
            ok=[r for r in rows if r.get(key+'_valid')]
            metrics[key]={
              'n_valid':len(ok),
              'median_negative_intensity':float(np.median(
                  [(r[key+'_negative_intensity_a']+r[key+'_negative_intensity_b'])/2
                   for r in ok])) if ok else None,
              'median_convex_hull_deficit':float(np.median(
                  [(r[key+'_convex_hull_deficit_a']+r[key+'_convex_hull_deficit_b'])/2
                   for r in ok])) if ok else None}
    return {'status':'M2_BTC_EXPLORATORY','interval':interval,'windows':len(rows),
            'eligible_windows':len(samples),'reserved_periods_used':False,
            'metrics':metrics,'association':association(rows),
            'limits':['Conditional discrepancy is not verified market stress.',
                      '8 bootstrap resamples for two windows are engineering diagnostics.',
                      'No prior adjustment for heteroskedasticity/regime/seasonality.',
                      'Model and coordinate dependent; no new law or trading claim.']}
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--interval',choices=('synthetic','1m','1h'),required=True)
    a=p.parse_args()
    report=synthetic() if a.interval=='synthetic' else real(a.interval)
    out=ROOT/'reports'/f'SGV_M2_{a.interval}.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
