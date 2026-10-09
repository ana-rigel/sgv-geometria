#!/usr/bin/env python3
"""SGV M7 — expanded paired HDR50 shape dynamics, strictly exploratory."""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import fit_sf1,simulate_sf1,flow_coordinates
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.m5_validacao_conjunta_sf1 import fit_volume,PREFIX,WINDOW,STEP
from experiments.m6_acoplamento_residual_hdr import (
    simulate_coupled,shape_signature,VARIANTS)
from experiments.m4_sf1_memoria_sazonalidade import ablated_path,BURN
from experiments.m2_nao_convexidade_tensao import morphology
from experiments.precisao_formas_3d import split_historical
from experiments.m3_precisao_nao_convexidade import circular_blocks

SEED=20261009
ORIGINS=6
SIMS=4
BOOT_REPS=12
BLOCKS={'1m':15,'1h':12}
GRID_BASE=35
GRID_REFINE=49
MEASURES=('delta_D','D_b','convex_deficit_b')
NAMES=('sf1','m5_independent','m6_coupled')


def same_flow(a,b,window):
    aa=flow_coordinates(a)[['z','iota']].to_numpy(float)[-window:]
    bb=flow_coordinates(b)[['z','iota']].to_numpy(float)[-window:]
    return bool(np.allclose(aa,bb,rtol=0,atol=1e-10))


def real_precision(frame,window,seed,block=15,reps=BOOT_REPS):
    """Frozen anchor, separately resampled A/B. Descriptive, not calibrated CI."""
    x=flow_coordinates(frame)[['z','iota','nu']].to_numpy(float)[-window:]
    a,b=split_historical(x)
    rng=np.random.default_rng(seed)
    valid=[]
    for j in range(reps):
        a0=circular_blocks(a,rng,block)
        b0=circular_blocks(b,rng,block)
        A=morphology(a0,'mixture',.5,GRID_BASE,seed+10+2*j)
        B=morphology(b0,'mixture',.5,GRID_BASE,seed+11+2*j)
        if A['valid'] and B['valid']:
            valid.append(B['negative_intensity']-A['negative_intensity'])
    return {'n_total':reps,'n_valid':len(valid),'block':block,
            'delta_D_bootstrap_p10_p50_p90':[
                float(t) for t in np.quantile(valid,[.1,.5,.9])
            ] if len(valid)>=max(6,reps//2) else None,
            'interpretation':'Diagnostic refit distribution; NOT confidence interval'}


def refine_real(frame,window,seed):
    x=flow_coordinates(frame)[['z','iota','nu']].to_numpy(float)[-window:]
    a,b=split_historical(x)
    output={}
    for n in (GRID_BASE,GRID_REFINE):
        A=morphology(a,'mixture',.5,n,seed)
        B=morphology(b,'mixture',.5,n,seed+1)
        if A['valid'] and B['valid']:
            output[str(n)]={
                'valid':True,
                'D_b':B['negative_intensity'],
                'delta_D':B['negative_intensity']-A['negative_intensity'],
                'C_b':B['convex_hull_deficit']}
        else:
            output[str(n)]={'valid':False,
                'reason':A.get('reason') or B.get('reason')}
    if all(output[str(n)]['valid'] for n in (GRID_BASE,GRID_REFINE)):
        output['difference_abs_D_b']=abs(
            output[str(GRID_BASE)]['D_b']-output[str(GRID_REFINE)]['D_b'])
        output['difference_abs_delta_D']=abs(
            output[str(GRID_BASE)]['delta_D']-
            output[str(GRID_REFINE)]['delta_D'])
    return output


def single_origin(prefix,window,step,seed,precision=False,reps=SIMS):
    ts=np.r_[prefix.timestamp.to_numpy(np.int64),
             window.timestamp.to_numpy(np.int64)]
    if len(prefix)!=len(prefix) or not np.all(np.diff(ts)==step):
        raise ValueError('Discontinuous origin')
    model=fit_sf1(prefix)
    if not model.garch.get('converged',False):
        raise ValueError('SF1 calibration did not converge')
    fit=fit_volume(prefix,'both',step)
    complete=pd.concat([prefix,window],ignore_index=True)
    observed=shape_signature(complete,len(window),seed)
    if not observed['valid']:raise ValueError('Real geometry invalid: '+observed['reason'])
    simulations={k:[] for k in NAMES}
    for j in range(reps):
        base=simulate_sf1(model,len(window)+BURN,
                          seed=seed+103*j,step_ms=step)
        base['timestamp']=int(prefix.timestamp.iloc[-1])+(
            np.arange(len(base))+1-BURN)*step
        m5=ablated_path(base,prefix,fit,step,
                         seed=seed+10000+103*j)
        m6,_=simulate_coupled(base,prefix,model,fit,step,
                              seed=seed+10000+103*j)
        for name,frame in zip(NAMES,(base,m5,m6)):
            if not same_flow(base,frame,len(window)):
                raise AssertionError('Price or iota changed')
            simulated=shape_signature(frame,len(window),seed+30000+1000*j)
            simulations[name].append(simulated)
    errors={}
    for name,shapes in simulations.items():
        ok=[s for s in shapes if s['valid']]
        errors[name]={
            'n_valid':len(ok),'n_total':len(shapes),
            'errors':{k:float(abs(np.median([s[k] for s in ok])-observed[k]))
                      for k in MEASURES} if len(ok)>=max(2,reps//2) else None,
            'median_simulated':{k:float(np.median([s[k] for s in ok]))
                                for k in MEASURES} if ok else None}
    result={
        'asof_ms':int(window.timestamp.iloc[-1]+step),
        'observed':{k:float(observed[k]) for k in MEASURES},
        'models':errors,
        'all_paths_paired':True,
        'precision':None,'refinement':None}
    if precision:
        result['precision']=real_precision(
            complete,len(window),seed+90000,BLOCKS['1m'] if step==60000
            else BLOCKS['1h'])
        result['refinement']=refine_real(complete,len(window),seed)
    return result


def median_or_none(items):
    return float(np.median(items)) if items else None


def paired_summary(results):
    out={'n_windows':len(results),'models':{},'paired':{}}
    for name in NAMES:
        all_ok=[r['models'][name]['errors'] for r in results
                if r['models'][name]['errors'] is not None]
        out['models'][name]={
            'windows_valid':len(all_ok),
            'median_abs_error':{
                m:median_or_none([x[m] for x in all_ok])
                for m in MEASURES}}
    for rival in ('sf1','m5_independent'):
        comparable=[r for r in results if
            r['models']['m6_coupled']['errors'] is not None and
            r['models'][rival]['errors'] is not None]
        out['paired']['m6_vs_'+rival]={
            'n_paired':len(comparable),
            'quality_gate':len(comparable)>=max(4,len(results)*2//3),
            'metrics':{k:{
                'm6_better_count':sum(
                    r['models']['m6_coupled']['errors'][k] <
                    r['models'][rival]['errors'][k] for r in comparable),
                'median_error_difference_m6_minus_rival':median_or_none([
                    r['models']['m6_coupled']['errors'][k]-
                    r['models'][rival]['errors'][k] for r in comparable])
            } for k in MEASURES}}
    return out


def calibrate():
    from sgvgeo.flow import default_sf1
    base=simulate_sf1(default_sf1(),7300,seed=111,step_ms=60000)
    p=base.iloc[:5000].copy()
    w=base.iloc[5000:6500].copy()
    # Verify the logic with one fixed origin and one matched set of synthetic draws.
    out=single_origin(p,w,60000,SEED,reps=2)
    assert out['all_paths_paired']
    assert all(out['models'][k]['n_total']==2 for k in NAMES)
    return {'status':'M7_SYNTHETIC_CALIBRATION',
            'model_valid_counts':{k:out['models'][k]['n_valid'] for k in NAMES},
            'paired_control':True,'data_kind':'synthetic_only'}


def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('No exploratory files')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    pre=PREFIX[interval];window=WINDOW[interval];step=STEP[interval]
    ts=df.timestamp.to_numpy(np.int64)
    candidates=[i for i in range(pre,len(df)-window+1,window)
                if np.all(np.diff(ts[i-pre:i+window])==step)]
    if not candidates:raise RuntimeError('No contiguous candidate windows')
    indices=np.linspace(0,len(candidates)-1,
                         min(ORIGINS,len(candidates)),dtype=int)
    precision_indices={0,len(indices)-1}
    rows=[];failures=[]
    for j,index in enumerate(indices):
        origin=candidates[int(index)]
        try:
            r=single_origin(df.iloc[origin-pre:origin].copy(),
                           df.iloc[origin:origin+window].copy(),
                           step,SEED+j*1000,precision=j in precision_indices)
            rows.append(r)
        except (ValueError,AssertionError,np.linalg.LinAlgError,RuntimeError) as ex:
            failures.append({'origin':int(origin),'reason':str(ex)})
    if not rows:raise RuntimeError(f'All origins invalid: {failures}')
    out=ROOT/'reports'/f'SGV_M7_{interval}_errors.csv'
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf8') as f:
        wr=csv.DictWriter(f,fieldnames=[
            'asof_ms','model','metric','real','median_simulated',
            'abs_error','n_valid','n_total'])
        wr.writeheader()
        for r in rows:
            for model,record in r['models'].items():
                for metric in MEASURES:
                    wr.writerow({'asof_ms':r['asof_ms'],'model':model,
                        'metric':metric,'real':r['observed'][metric],
                        'median_simulated':(record['median_simulated'] or {}).get(metric),
                        'abs_error':(record['errors'] or {}).get(metric),
                        'n_valid':record['n_valid'],'n_total':record['n_total']})
    return {
       'status':'M7_BTC_EXPLORATORY','interval':interval,
       'n_candidate_origins':len(candidates),'n_selected':len(indices),
       'n_valid_origins':len(rows),'n_failed_origins':len(failures),
       'failures':failures,'n_simulations_per_origin':SIMS,
       'no_confirmatory_data_used':True,
       'summary':paired_summary(rows),
       'diagnostics':[
           {'asof_ms':r['asof_ms'],
            'bootstrap':r['precision'],'grid':r['refinement']}
           for r in rows if r['precision'] is not None],
       'limits':['Origin-level comparisons; 4 synthetic draws per model',
                 'Two 12-replicate block diagnostics per timeframe are not calibrated CIs',
                 'No regime-adequate/null adequacy demonstrated',
                 'No claim of causal deformation, predictive alpha or stress']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--interval',choices=('synthetic','1m','1h'),required=True)
    a=p.parse_args()
    data=calibrate() if a.interval=='synthetic' else real(a.interval)
    path=ROOT/'reports'/f'SGV_M7_{a.interval}.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(data,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
