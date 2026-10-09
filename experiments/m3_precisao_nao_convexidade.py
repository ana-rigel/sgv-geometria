#!/usr/bin/env python3
"""SGV-M3: numerical and sampling reliability of extrinsic HDR nonconvexity.

NO claim of stress, market physics or causal flow. Frozen prefix rank map.
Only approved BTC exploration files. Exact density Hessian from GMM2 M1.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
from scipy.stats import multivariate_t
from experiments.m2_nao_convexidade_tensao import morphology
from experiments.precisao_formas_3d import split_historical
from experiments.persistencia_dependencia import checked_exploratory_month
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates

ROOT=Path(__file__).resolve().parents[1]
W={'1m':1500,'1h':1008}
STEP={'1m':60000,'1h':3600000}
SEED=20261009
LEVELS=(.25,.5,.75)
GRID=(25,35,49)
N_ALL=20
N_AUDIT=3
REPS=29
BLOCKS={'1m':(8,20),'1h':(6,16)}
METRICS=('negative_intensity','convex_hull_deficit','area_Kr2_lt_minus_01')


def finite_or_none(v):
    return float(v) if v is not None and np.isfinite(v) else None


def picture(sample,*,level=.5,n=35,seed=SEED):
    return morphology(sample,model='mixture',alpha=level,n=n,seed=seed)


def circular_blocks(sample,rng,block):
    x=np.asarray(sample,float)
    if block<1 or block>len(x): raise ValueError("Invalid block length")
    count=(len(x)+block-1)//block
    starts=rng.integers(0,len(x),size=count)
    index=(starts[:,None]+np.arange(block)[None,:])%len(x)
    return x[index.ravel()[:len(x)]]


def baseline_null(sample,rng,kind):
    x=np.asarray(sample,float)
    mu=x.mean(axis=0)
    cov=np.cov(x,rowvar=False)
    cov+=np.eye(3)*1e-6
    if kind=='gauss':
        return rng.multivariate_normal(mu,cov,size=len(x))
    if kind=='t5':
        df=5.
        scatter=cov*(df-2)/df
        return multivariate_t.rvs(loc=mu,shape=scatter,df=df,
                                  size=len(x),random_state=rng)
    raise ValueError(kind)


def compact(p):
    if not p['valid']:return {'valid':False,'reason':p.get('reason')}
    return {'valid':True,**{k:float(p[k]) for k in METRICS}}


def initial_summary(x,seed):
    a,b=split_historical(x)
    result={}
    for side,sample in (('a',a),('b',b)):
        for level in LEVELS:
            key=f'{side}_HDR{int(level*100)}'
            result[key]=compact(picture(sample,level=level,seed=seed+(side=='b')))
    return result


def numerical_check(x,seed):
    a,b=split_historical(x)
    rows={}
    for name,sample in (('a',a),('b',b)):
        for alpha in LEVELS:
            k=f'{name}_HDR{int(alpha*100)}'
            rows[k]={}
            for n in GRID:
                rows[k][str(n)]=compact(picture(sample,level=alpha,n=n,seed=seed+(name=='b')))
            if all(rows[k][str(n)]['valid'] for n in GRID):
                lo,hi=(rows[k]['25']['negative_intensity'],
                       rows[k]['49']['negative_intensity'])
                ref=rows[k]['49']['negative_intensity']
                rows[k]['relative_D_25_49']=float(abs(lo-hi)/max(.02,abs(ref)))
                rows[k]['absolute_D_25_49']=float(abs(lo-hi))
                rows[k]['absolute_C_25_49']=float(abs(
                    rows[k]['25']['convex_hull_deficit']-
                    rows[k]['49']['convex_hull_deficit']))
    return rows


def resample_audit(x,seed,block_sizes,reps=REPS):
    a,b=split_historical(x)
    rng=np.random.default_rng(seed)
    orig_a=picture(a,seed=seed)
    orig_b=picture(b,seed=seed+1)
    if not(orig_a['valid'] and orig_b['valid']):
        return {'status':'invalid_original'}
    observed=orig_b['negative_intensity']-orig_a['negative_intensity']
    result={'status':'diagnostic_only','observed_delta_D':float(observed),
            'block_bootstrap':{},'convex_null':{}}
    for block in block_sizes:
        valid=[]
        for j in range(reps):
            sa=circular_blocks(a,rng,block)
            sb=circular_blocks(b,rng,block)
            ma=picture(sa,seed=seed+10000+j*2)
            mb=picture(sb,seed=seed+10001+j*2)
            if ma['valid'] and mb['valid']:
                valid.append(mb['negative_intensity']-ma['negative_intensity'])
        result['block_bootstrap'][str(block)]={
            'n_valid':len(valid),
            'q10_q50_q90':([float(v) for v in np.quantile(valid,[.1,.5,.9])]
                          if len(valid)>=max(10,reps//2) else None),
            'note':'Distribution of refit deltas, not a calibrated CI for true state change'}
    for kind in ('gauss','t5'):
        null_values=[]
        for j in range(reps):
            sim=baseline_null(b,rng,kind)
            p=picture(sim,seed=seed+20000+j)
            if p['valid']:null_values.append(p['negative_intensity'])
        result['convex_null'][kind]={
            'n_valid':len(null_values),
            'median':float(np.median(null_values)) if null_values else None,
            'q90':float(np.quantile(null_values,.9)) if null_values else None,
            'obs_b_D':float(orig_b['negative_intensity']),
            'obs_above_q90':bool(
                orig_b['negative_intensity']>np.quantile(null_values,.9)
            ) if len(null_values)>=max(10,reps//2) else None,
            'warning':'Parametric independent observations; not a market time-series null'}
    return result


def simulate_case(kind,seed=SEED,n=1500):
    rng=np.random.default_rng(seed)
    if kind=='gaussian':
        x=rng.normal(size=(n,3))
        x[:,1]=.55*x[:,0]+np.sqrt(1-.55**2)*x[:,1]
        return x
    if kind=='t5':
        return multivariate_t.rvs(loc=np.zeros(3),shape=np.eye(3)*.6,
                                  df=5,size=n,random_state=rng)
    if kind=='persistent_mixture':
        x=rng.normal(size=(n,3))
        state=np.where(rng.random(n)<.5,1.,-1.)
        x[:,1]=state*.82*x[:,0]+np.sqrt(1-.82**2)*x[:,1]
        return x
    raise ValueError(kind)


def synth():
    cases={}
    for i,kind in enumerate(('gaussian','t5','persistent_mixture')):
        xx=simulate_case(kind,seed=SEED+i)
        # Calibration is engineering power/sensitivity check, not proof.
        cases[kind]={'baseline':initial_summary(xx,seed=SEED+i),
                     'resolution':numerical_check(xx,seed=SEED+i)}
    return {'status':'M3_SYNTHETIC_CALIBRATION','cases':cases,
            'n_trials_per_case':1,
            'warning':'Small control set, no inference of power or error rates'}


def summary(rows,details):
    result={'n_windows':len(rows)}
    for alpha in LEVELS:
        k=f'HDR{int(alpha*100)}'
        x=[r['b_'+k]['negative_intensity']
           for r in rows if r['b_'+k]['valid']]
        result[k]={
            'n_valid':len(x),
            'median_D':float(np.median(x)) if x else None,
            'median_C':float(np.median([
                r['b_'+k]['convex_hull_deficit']
                for r in rows if r['b_'+k]['valid']])) if x else None}
    resolution=[]
    audits=[]
    for item in details:
        if 'resolution' in item:
            for name,group in item['resolution'].items():
                if 'absolute_D_25_49' in group:
                    resolution.append(group['absolute_D_25_49'])
        audits.append(item.get('bootstrap',{}))
    result['n_windows_audited']=len(details)
    result['numerical_D_25_49_abs_median']=float(np.median(resolution)) if resolution else None
    result['n_grid_diagnostics_valid']=len(resolution)
    for kind in ('gauss','t5'):
        nulls=[a['convex_null'][kind]['obs_above_q90'] for a in audits
               if a.get('status')=='diagnostic_only'
               and a['convex_null'][kind]['obs_above_q90'] is not None]
        result[f'n_obs_above_{kind}_null_q90']=sum(nulls)
        result[f'n_{kind}_null_comparisons']=len(nulls)
    return result


def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('Exploration klines absent')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    xx=flow_coordinates(df)[['z','iota','nu']].to_numpy(float)
    time=df.timestamp.to_numpy(np.int64)
    w=W[interval]
    windows=[]
    for end in range(w,len(xx)+1,w):
        sample=xx[end-w:end]; ts=time[end-w:end]
        if np.isfinite(sample).all() and np.all(np.diff(ts)==STEP[interval]):
            windows.append((end,int(ts[-1]+STEP[interval]),sample))
    if not windows:raise RuntimeError('No valid contiguous windows')
    chosen=np.linspace(0,len(windows)-1,min(N_ALL,len(windows)),dtype=int)
    auditidx=set(np.linspace(0,len(chosen)-1,min(N_AUDIT,len(chosen)),dtype=int))
    output=[]
    details=[]
    for j,i in enumerate(chosen):
        end,asof,x=windows[int(i)]
        result=initial_summary(x,seed=SEED+end)
        result['index']=int(i)
        result['asof_ms']=asof
        output.append(result)
        if j in auditidx:
            details.append({
                'index':int(i),'asof_ms':asof,
                'resolution':numerical_check(x,seed=SEED+end),
                'bootstrap':resample_audit(
                    x,SEED+end,block_sizes=BLOCKS[interval])})
    file=ROOT/'reports'/f'SGV_M3_{interval}_windows.csv'
    file.parent.mkdir(parents=True,exist_ok=True)
    with file.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=('asof_ms','index','side','alpha','valid',
                              'negative_intensity','convex_hull_deficit',
                              'area_Kr2_lt_minus_01','reason'))
        writer.writeheader()
        for r in output:
            for side in ('a','b'):
                for alpha in LEVELS:
                    p=r[f'{side}_HDR{int(alpha*100)}']
                    writer.writerow({
                        'asof_ms':r['asof_ms'],'index':r['index'],
                        'side':side,'alpha':alpha,'valid':p['valid'],
                        'negative_intensity':p.get('negative_intensity'),
                        'convex_hull_deficit':p.get('convex_hull_deficit'),
                        'area_Kr2_lt_minus_01':p.get('area_Kr2_lt_minus_01'),
                        'reason':p.get('reason')})
    return {'status':'M3_BTC_EXPLORATION','interval':interval,
            'n_eligible':len(windows),'no_confirmatory_data_used':True,
            'grid_resolutions':list(GRID),'bootstrap_reps':REPS,
            'audit':details,'results':summary(output,details),
            'warnings':['Exploratory diagnostics, no calibrated null p-values',
                'Independent Gaussian/t5 simulations miss time dependence',
                'GMM2 fitted to Gaussian can still exhibit sample nonconvexity',
                'Shape is extrinsic and coordinate-dependent, not financial stress']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--interval',required=True,choices=('synthetic','1m','1h'))
    args=p.parse_args()
    r=synth() if args.interval=='synthetic' else real(args.interval)
    target=ROOT/'reports'/f'SGV_M3_{args.interval}.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(r,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
