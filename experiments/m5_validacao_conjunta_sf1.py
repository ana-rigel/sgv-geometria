#!/usr/bin/env python3
"""M5: paired SF1 volume-memory/calendar comparison, observational only."""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates,fit_sf1,simulate_sf1
from sgvgeo.data import load_binance_klines
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.auditoria_adequacao_sf1 import diagnostics
from experiments.m4_sf1_memoria_sazonalidade import (
    season,ablated_path,LAGS,BURN,KEYS as M4_KEYS)
PREFIX={'1m':5000,'1h':2000}
WINDOW={'1m':1500,'1h':1008}
STEP={'1m':60000,'1h':3600000}
ORIGINS=8
SIMS=8
SEED=20261009
VOL_KEYS=('nu_acf1','nu_acf10','nu_std','rho_abs_z_nu')
CONTROL_KEYS=('iota_acf1','rho_z_iota','abs_z_acf1')
OTHER_KEYS=('rho_iota_nu',)
SCALE={'nu_acf1':.15,'nu_acf10':.15,'nu_std':.25,
       'rho_abs_z_nu':.15}
VARIANTS=('sf1','memory','season','both')


def fit_volume(prefix,variant,step):
    """Past-only volume AR + calendar; 1h allowed when >=3 actual day cycles."""
    if variant not in ('memory','season','both'):raise ValueError(variant)
    ts=prefix.timestamp.to_numpy(np.int64)
    if not np.all(np.diff(ts)==step):raise ValueError('Gap in prefix')
    ell=np.log(np.maximum(prefix.volume.to_numpy(dtype=float),1e-12))
    z=flow_coordinates(prefix)['z'].to_numpy(dtype=float,copy=True)
    min_lag=max(LAGS)
    idx=np.arange(min_lag+1,len(prefix))
    idx=idx[np.isfinite(z[idx])]
    if len(idx)<1500:raise ValueError('Insufficient clean prefix')
    has_season=variant in ('season','both')
    if has_season and ts[-1]-ts[0] < 3*86400000:
        raise ValueError('Need at least three complete daily cycles')
    lags=(1,) if variant=='season' else LAGS
    cols=[ell[idx-l] for l in lags]+[np.abs(z[idx]),z[idx]]
    if has_season:
        s=season(ts[idx])
        cols.extend([s[:,0],s[:,1]])
    A=np.column_stack(cols)
    mean=A.mean(axis=0)
    sd=np.maximum(A.std(axis=0),1e-6)
    standardized=(A-mean)/sd
    y=ell[idx]
    reg=np.linalg.solve(standardized.T@standardized+
                        np.eye(A.shape[1])*2.,
                        standardized.T@(y-y.mean()))
    coef=reg/sd
    lag_norm=np.abs(coef[:len(lags)]).sum()
    if lag_norm>.97:coef[:len(lags)]*=.97/lag_norm
    intercept=float(np.mean(y-A@coef))
    eps=y-intercept-A@coef
    eps-=eps.mean()
    return {'variant':variant,'lags':lags,'coef':coef,'intercept':intercept,
            'residual':eps,'season':has_season,
            'lag_norm':float(np.abs(coef[:len(lags)]).sum()),
            'effective_n':int(len(idx)),'days':float((ts[-1]-ts[0])/86400000)}


def full_metrics(matrix):
    metrics=diagnostics(matrix)
    return {key:metrics[key] for key in (*VOL_KEYS,*CONTROL_KEYS,*OTHER_KEYS)}


def joint_loss(metrics,reference):
    return float(np.mean([abs(metrics[k]-reference[k])/SCALE[k]
                          for k in VOL_KEYS]))


def evaluate(prefix,window,step,seed,n_sim=SIMS):
    if len(prefix)<2000 or len(window)<900:raise ValueError('Short segment')
    joined=pd.concat([prefix,window],ignore_index=True)
    if not np.all(np.diff(joined.timestamp.to_numpy(np.int64))==step):
        raise ValueError('Discontinuous time')
    observed=full_metrics(flow_coordinates(joined)[['z','iota','nu']]
                          .to_numpy(float)[-len(window):])
    sf1=fit_sf1(prefix)
    if not sf1.garch.get('converged',False):
        raise ValueError('GARCH-t did not converge')
    fit={}
    unavailable={}
    for v in VARIANTS[1:]:
        try:fit[v]=fit_volume(prefix,v,step)
        except (ValueError,np.linalg.LinAlgError) as e:unavailable[v]=str(e)
    outcomes={v:[] for v in ('sf1',*fit)}
    for rep in range(n_sim):
        base=simulate_sf1(sf1,len(window)+BURN,
                          seed=seed+rep*103,step_ms=step)
        base['timestamp']=(int(prefix.timestamp.iloc[-1])+
                           (np.arange(len(base))+1-BURN)*step)
        x=flow_coordinates(base)[['z','iota','nu']].to_numpy(float)[-len(window):]
        outcomes['sf1'].append(full_metrics(x))
        for variant,trained in fit.items():
            replacement=ablated_path(base,prefix,trained,step,
                                     seed=seed+100000+rep*103)
            y=flow_coordinates(replacement)[['z','iota','nu']].to_numpy(float)[-len(window):]
            if not np.allclose(x[:,:2],y[:,:2],atol=1e-10,rtol=0):
                raise AssertionError('Price or flow changed')
            outcomes[variant].append(full_metrics(y))
    scores={}
    for name,draws in outcomes.items():
        median={k:float(np.median([v[k] for v in draws]))
                for k in observed}
        scores[name]={
            'metrics':{k:{'observed':float(observed[k]),
                          'sim_median':median[k],
                          'abs_error':float(abs(observed[k]-median[k]))}
                       for k in observed},
            'joint_loss':joint_loss(median,observed)}
    return {'asof_ms':int(window.timestamp.iloc[-1]+step),
            'simulations':n_sim,'metrics':scores,
            'unavailable':unavailable,
            'fit_info':{k:{'lag_norm':f['lag_norm'],'days':f['days']}
                         for k,f in fit.items()},
            'price_flow_invariance':True}


def aggregate(results):
    data={}
    for v in VARIANTS:
        subset=[r for r in results if v in r['metrics']]
        if not subset:
            data[v]={'status':'unavailable','n':0}
            continue
        row={'n':len(subset),
             'median_joint_loss':float(np.median(
                 [x['metrics'][v]['joint_loss'] for x in subset]))}
        for k in (*VOL_KEYS,*CONTROL_KEYS,*OTHER_KEYS):
            row[k+'_median_abs_error']=float(np.median(
                [x['metrics'][v]['metrics'][k]['abs_error'] for x in subset]))
            row[k+'_median_real']=float(np.median(
                [x['metrics'][v]['metrics'][k]['observed'] for x in subset]))
            row[k+'_median_sim']=float(np.median(
                [x['metrics'][v]['metrics'][k]['sim_median'] for x in subset]))
        if v!='sf1':
            paired=[x for x in subset if 'sf1' in x['metrics']]
            row['improved_origins']=int(sum(
                x['metrics'][v]['joint_loss']<x['metrics']['sf1']['joint_loss']
                for x in paired))
            row['median_joint_loss_delta_vs_sf1']=float(np.median([
                x['metrics'][v]['joint_loss']-x['metrics']['sf1']['joint_loss']
                for x in paired]))
            row['acf1_error_increase_vs_sf1']=float(
                row['nu_acf1_median_abs_error']-
                data['sf1']['nu_acf1_median_abs_error'])
            row['passes_gate']=bool(
                row['median_joint_loss_delta_vs_sf1']<0 and
                row['acf1_error_increase_vs_sf1']<=.04)
        data[v]=row
    candidates=[v for v in VARIANTS[1:] if data[v].get('passes_gate',False)]
    winner=min(candidates,key=lambda k:data[k]['median_joint_loss']) if candidates else None
    return {'n_origins':len(results),'models':data,
            'eligible_best_under_protocol':winner,
            'warning':'Exploratory multi-metric diagnostic, not statistical selection certainty'}


def calibrate():
    from sgvgeo.flow import default_sf1
    generated=simulate_sf1(default_sf1(),4500,seed=13,step_ms=3600000)
    prefix=generated.iloc[:2000].copy()
    a=fit_volume(prefix,'season',3600000)
    b=fit_volume(prefix,'both',3600000)
    changed=generated.copy()
    changed.loc[2000:,'volume']*=50
    c=fit_volume(changed.iloc[:2000], 'season',3600000)
    assert np.array_equal(a['coef'],c['coef'])
    assert a['effective_n']>=1500 and b['season']
    return {'status':'M5_CALIBRATION','hourly_season_available':True,
            'past_only_invariance':True,'season_fit_n':a['effective_n']}


def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('No exploration months')
    for path in paths:checked_exploratory_month(path.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    pre=PREFIX[interval];w=WINDOW[interval];step=STEP[interval]
    ts=df.timestamp.to_numpy(np.int64)
    starts=[x for x in range(pre,len(df)-w+1,w)
            if np.all(np.diff(ts[x-pre:x+w])==step)]
    if not starts:raise RuntimeError('No contiguous origins')
    indexes=np.linspace(0,len(starts)-1,min(ORIGINS,len(starts)),dtype=int)
    results=[]
    skips=[]
    for j,k in enumerate(indexes):
        origin=starts[int(k)]
        try:
            results.append(evaluate(df.iloc[origin-pre:origin].copy(),
                                    df.iloc[origin:origin+w].copy(),
                                    step,SEED+j*1000))
        except (ValueError,AssertionError,np.linalg.LinAlgError) as e:
            skips.append({'origin':origin,'error':str(e)})
    if not results:raise RuntimeError('All sampled origins failed')
    path=ROOT/'reports'/f'SGV_M5_{interval}_comparison.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf8') as f:
        wr=csv.DictWriter(f,fieldnames=['asof_ms','variant','metric',
                         'observed','sim_median','abs_error','joint_loss'])
        wr.writeheader()
        for r in results:
            for name,info in r['metrics'].items():
                for k,v in info['metrics'].items():
                    wr.writerow({'asof_ms':r['asof_ms'],'variant':name,
                                 'metric':k,**v,'joint_loss':info['joint_loss']})
    return {'status':'M5_EXPLORATORY_REPLAY','interval':interval,
            'n_eligible_origins':len(starts),
            'n_sampled':len(indexes),'n_valid':len(results),
            'n_failures':len(skips),'failures':skips,
            'no_confirmatory_data':True,
            'n_simulations_per_origin':SIMS,
            'all_price_flow_invariant':all(r['price_flow_invariance'] for r in results),
            'summary':aggregate(results),'missing_variants':{
                str(r['asof_ms']):r['unavailable'] for r in results if r['unavailable']},
            'limitations':['Only eight simulations per fit, exploratory',
             'Seasonality corrects only a first 24h harmonic',
             'Extended innovations do not preserve original volume-flow residual coupling',
             'No structural causal claims, no market-stress proof']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--interval',required=True,choices=('synthetic','1m','1h'))
    args=parser.parse_args()
    result=calibrate() if args.interval=='synthetic' else real(args.interval)
    dest=ROOT/'reports'/f'SGV_M5_{args.interval}.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
