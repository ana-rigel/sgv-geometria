#!/usr/bin/env python3
"""SGV-M13: known-generator Monte Carlo rank calibration, followed by BTC diagnostics.

A valid Monte Carlo rank from exchangeable KNOWN-GENERATOR trajectories is not a
calibrated p-value for a null estimated from a BTC prefix. No trading/stress claim.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from experiments.m12_nulos_regimes_temporais import (
    PREFIX,MODELS,null_paths,temporal_metrics,score_metrics)
from experiments.m11_distancia_superficie_nulos import measure_samples
from experiments.precisao_formas_3d import split_historical
from experiments.persistencia_dependencia import checked_exploratory_month
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments.m5_validacao_conjunta_sf1 import WINDOW,STEP

SEED=20261009
REFS=19
TRIALS=6
ORIGINS=3
REAL_REFS=19
SYN_WINDOW=1500
GENERATORS=('gaussian_var','markov_regimes')
TAIL_KEYS=('nu_q95','nu_q05','joint_upper_tail')
META_KEYS=('nu_acf1','nu_acf10','abs_z_acf1','nu_std','rho_iota_nu','hour_profile_rmse')


def mc_rank(observed,reference,min_reference=REFS):
    """Finite-sample conservative upper-tail Monte Carlo rank under exchangeability."""
    vals=np.asarray(reference,float)
    if vals.ndim!=1 or len(vals)<min_reference or not np.isfinite(vals).all():
        raise ValueError('Insufficient finite exchangeable reference draws')
    if not np.isfinite(observed):
        raise ValueError('Invalid observed geometric distance')
    return float((1+np.count_nonzero(vals>=observed))/(1+len(vals)))


def wilson(successes,n,z=1.959963984540054):
    if n<1: return None
    phat=successes/n;den=1+z*z/n
    mid=(phat+z*z/(2*n))/den
    rad=z*np.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/den
    return [float(max(0.,mid-rad)),float(min(1.,mid+rad))]


def known_generator(kind,seed,n=SYN_WINDOW):
    """Stationary generator draws independent across seed; parameters never fit."""
    if kind not in GENERATORS:raise ValueError(kind)
    rng=np.random.default_rng(seed)
    total=n+360
    eps=rng.multivariate_normal([0.,0.,0.],[
      [1.,.38,.22],[.38,1.,.28],[.22,.28,1.]],size=total)
    states=np.zeros(total,dtype=int)
    if kind=='markov_regimes':
        states[0]=int(rng.integers(2))
        for t in range(1,total):
            states[t]=states[t-1] if rng.random()<.982 else 1-states[t-1]
    x=np.empty((total,3),float)
    x[0]=eps[0]
    for t in range(1,total):
        s=states[t]
        x[t,0]=.18*x[t-1,0]+(1+.28*s)*eps[t,0]+.12*s
        x[t,1]=.22*x[t-1,1]+.38*x[t,0]+.45*eps[t,1]-.13*s
        x[t,2]=.69*x[t-1,2]+(.38+.16*s)*eps[t,2]+.17*s
    return x[-n:]


def geom_distance(x,seed):
    x=np.asarray(x,float)
    if len(x)<1000 or x.shape[1:]!=(3,) or not np.isfinite(x).all():
        return {'valid':False,'reason':'invalid_3d_window'}
    a,b=split_historical(x)
    return measure_samples(a,b,seed)


def synthetic_rank_sanity(trials=1000,seed=SEED):
    rng=np.random.default_rng(seed)
    values=[]
    for _ in range(trials):
        group=rng.normal(size=REFS+1)
        values.append(mc_rank(group[0],group[1:]))
    hits=int(np.count_nonzero(np.array(values)<=.05))
    return {'n':trials,'reference_draws':REFS,'alarms_at_005':hits,
            'frequency':hits/trials,'wilson95':wilson(hits,trials),
            'scope':'Scalar rank-code validation only, not geometric calibration'}


def synthetic_geometry(trials=TRIALS):
    output={}
    for model_id,kind in enumerate(GENERATORS):
        records=[]
        for t in range(trials):
            scores=[];invalid=[]
            for j in range(REFS+1):
                x=known_generator(kind,SEED+model_id*100000+t*1000+j)
                # Same metric and estimator on observation and each reference.
                y=geom_distance(x,SEED+200000+model_id*100000+t*1000+j)
                if y['valid']:
                    scores.append(float(y['distance_512']))
                else:
                    invalid.append({'index':j,'reason':y.get('reason')})
            if invalid:
                records.append({'trial':t,'status':'invalid_geometry',
                                'n_valid':len(scores),'failed':invalid})
                continue
            p=mc_rank(scores[0],scores[1:])
            records.append({'trial':t,'status':'exchangeable_generator',
                            'observed_distance':scores[0],
                            'reference_q10_q50_q90':[float(v) for v in
                              np.quantile(scores[1:],[.1,.5,.9])],
                            'rank_mc_p':p,'alarm_at_005':bool(p<=.05),
                            'n_references':REFS})
        eligible=[r for r in records if r['status']=='exchangeable_generator']
        hits=sum(r['alarm_at_005'] for r in eligible)
        output[kind]={'n_requested_trials':trials,
                      'n_valid_trials':len(eligible),
                      'n_alarm_005':hits,
                      'alarm_fraction':hits/len(eligible) if eligible else None,
                      'wilson95':wilson(hits,len(eligible)),
                      'trials':records,
                      'interpretation':'Known-generator exchangeability only; few trials.'}
    return {'status':'M13_KNOWN_GENERATORS',
            'rank_sanity':synthetic_rank_sanity(),
            'n_references_per_trial':REFS,'generators':output,
            'scope':['Synthetic oracle validity does not transfer to fitted market nulls',
                     'Geometric GMM2/M11 estimator refit on every synthetic draw',
                     'No confirmatory market data opened']}


def joint_tail_metrics(x):
    x=np.asarray(x,float)
    z,io,nu=x.T
    qz=np.quantile(np.abs(z),.9);qi=np.quantile(np.abs(io),.9)
    qv=np.quantile(nu,.9)
    return {'nu_q95':float(np.quantile(nu,.95)),
            'nu_q05':float(np.quantile(nu,.05)),
            'joint_upper_tail':float(np.mean(
                (np.abs(z)>qz)&(np.abs(io)>qi)&(nu>qv)))}


def extended_adequacy(observed,simulated,times):
    from experiments.m12_nulos_regimes_temporais import KEYS
    m0=temporal_metrics(observed,times)
    m1=temporal_metrics(simulated,times)
    temporal=score_metrics(m1,m0)
    t0=joint_tail_metrics(observed)
    t1=joint_tail_metrics(simulated)
    return {**temporal,**{k:abs(t0[k]-t1[k]) for k in TAIL_KEYS}}


def evaluate_market(prefix,future,interval,seed,reps=REAL_REFS):
    pre=PREFIX[interval];window=WINDOW[interval];step=STEP[interval]
    if len(prefix)!=pre or len(future)!=window:
        raise ValueError('Unapproved window sizing')
    combined=pd.concat([prefix,future],ignore_index=True)
    timestamps=combined.timestamp.to_numpy(np.int64)
    if not np.all(np.diff(timestamps)==step):raise ValueError('Noncontiguous market origin')
    actual=flow_coordinates(combined)[['z','iota','nu']].to_numpy(float)[-window:]
    if not np.isfinite(actual).all():raise ValueError('Invalid observed coordinates')
    observation=geom_distance(actual,seed+50000)
    if not observation['valid']:raise ValueError('Invalid real geometry: '+str(observation))
    draw,fit,times=null_paths(prefix,interval,seed,reps)
    result={'asof_ms':int(future.timestamp.iloc[-1]+step),
            'observed_surface_distance':float(observation['distance_512']),
            'models':{},'n_references_requested':reps}
    for name in MODELS:
        distances=[];errors=[];failures=[]
        for j in range(reps):
            try:
                sim,info=draw(name,j)
                d=geom_distance(sim,seed+100000+j*101+MODELS.index(name)*1000000)
                if not d['valid']:
                    failures.append({'draw':j,'cause':d.get('reason')})
                    continue
                distances.append(float(d['distance_512']))
                errors.append(extended_adequacy(actual,sim,times))
            except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
                failures.append({'draw':j,'cause':str(e)})
        complete=len(distances)==reps and len(errors)==reps
        model={'n_valid':len(distances),'n_failed':len(failures),
               'invalid_reasons':failures,
               'descriptive_rank':mc_rank(observation['distance_512'],distances)
                   if complete and reps>=REFS else None,
               'reference_q10_q50_q90':[
                   float(v) for v in np.quantile(distances,[.1,.5,.9])
               ] if complete else None,
               'median_temporal_errors':{key:float(np.median(
                   [e[key] for e in errors if e.get(key) is not None]))
                   if any(e.get(key) is not None for e in errors) else None
                   for key in (*META_KEYS,*TAIL_KEYS)} if errors else None,
               'note':'Rank is uncalibrated after market-prefix estimation'}
        result['models'][name]=model
    return result


def aggregate_market(rows):
    models={}
    for name in MODELS:
        r=[x['models'][name] for x in rows if
           x['models'][name]['descriptive_rank'] is not None]
        ranks=[x['descriptive_rank'] for x in r]
        models[name]={'complete_origins':len(r),
                      'rank_le_005_descriptive':sum(p<=.05 for p in ranks),
                      'ranks':ranks,
                      'median_temporal_abs_error':{k:float(np.median(
                          [x['median_temporal_errors'][k] for x in r
                           if x['median_temporal_errors'][k] is not None]))
                          if any(x['median_temporal_errors'][k] is not None
                                 for x in r) else None
                          for k in (*META_KEYS,*TAIL_KEYS)}}
    return {'n_valid_origins':len(rows),'models':models,
            'warning':'Not a calibrated market hypothesis test: fitted nulls, four families and 19 reps.'}


def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('Exploratory data missing')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    pre=PREFIX[interval];win=WINDOW[interval];step=STEP[interval]
    ts=df.timestamp.to_numpy(np.int64)
    starts=[i for i in range(pre,len(df)-win+1,win)
            if np.all(np.diff(ts[i-pre:i+win])==step)]
    if not starts:raise RuntimeError('No complete exploratory origins')
    chosen=np.linspace(0,len(starts)-1,min(ORIGINS,len(starts)),dtype=int)
    results=[];fails=[]
    for j,k in enumerate(chosen):
        i=starts[int(k)]
        try:
            results.append(evaluate_market(df.iloc[i-pre:i].copy(),
                                           df.iloc[i:i+win].copy(),
                                           interval,SEED+1000*j))
        except (RuntimeError,ValueError,AssertionError,np.linalg.LinAlgError) as e:
            fails.append({'origin_index':int(i),'error':str(e)})
    if not results:raise RuntimeError('No valid M13 origins')
    target=ROOT/'reports'/f'SGV_M13_{interval}_ranks.csv'
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=['asof_ms','model','observed',
                                       'rank_uncalibrated','valid_draws',
                                       'reference_q10','reference_q50','reference_q90'])
        w.writeheader()
        for r in results:
            for name,obj in r['models'].items():
                q=obj['reference_q10_q50_q90'] or [None]*3
                w.writerow({'asof_ms':r['asof_ms'],'model':name,
                    'observed':r['observed_surface_distance'],
                    'rank_uncalibrated':obj['descriptive_rank'],
                    'valid_draws':obj['n_valid'],
                    'reference_q10':q[0],'reference_q50':q[1],'reference_q90':q[2]})
    return {'status':'M13_REAL_EXPLORATORY','interval':interval,
            'n_eligible':len(starts),'n_selected':len(chosen),
            'origins':results,'failures':fails,
            'summary':aggregate_market(results),'no_confirmatory_opened':True,
            'warnings':['Only 19 refs per fitted market null; no calibrated p-values',
                        'Three origins cannot establish a false alarm rate for BTC',
                        'Generated nulls use prefix only; rank validity needs true generative model',
                        'No market stress, physics or causal law established']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--interval',required=True,choices=('synthetic','1m','1h'))
    a=p.parse_args()
    out=synthetic_geometry() if a.interval=='synthetic' else real(a.interval)
    dest=ROOT/'reports'/f'SGV_M13_{a.interval}.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
