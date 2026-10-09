#!/usr/bin/env python3
"""M12 causal temporal nulls: stationary blocks, SF1-M5, regime-clock blocks.

A control experiment, not a test of trading, market stress or causal physics.
All parameters and block catalogs are trained on the closed historical prefix.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import fit_sf1,simulate_sf1,flow_coordinates
from sgvgeo.data import load_binance_klines
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.m5_validacao_conjunta_sf1 import fit_volume,WINDOW,STEP
from experiments.m4_sf1_memoria_sazonalidade import ablated_path,BURN
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m11_distancia_superficie_nulos import measure_samples
from experiments.auditoria_adequacao_sf1 import acf,safe_corr

SEED=20261009
PREFIX={'1m':5000,'1h':3500}
ORIGINS=4
REPS=6
SHORT={'1m':15,'1h':12}
LONG={'1m':60,'1h':36}
MODELS=('N0_stationary','N1_SF1_M5','N2_regime_short','N3_regime_long')
KEYS=('nu_acf1','nu_acf10','abs_z_acf1','nu_std','rho_iota_nu','hour_profile_rmse')


def clock_bin(timestamp_ms):
    return ((np.asarray(timestamp_ms,dtype=np.int64)%(24*3600000))//
            (6*3600000)).astype(int)


def temporal_metrics(x,t):
    x=np.asarray(x,float)
    if not np.isfinite(x).all() or x.ndim!=2 or x.shape[1]!=3:
        raise ValueError('Nonfinite trivariate scores')
    nu=x[:,2];z=x[:,0];iota=x[:,1]
    bins=clock_bin(t)
    out={'nu_acf1':acf(nu,1),'nu_acf10':acf(nu,10),
         'abs_z_acf1':acf(np.abs(z),1),
         'nu_std':float(nu.std(ddof=1)),
         'rho_iota_nu':safe_corr(iota,nu)}
    # The profile is an array; error must be computed using observed profile.
    profile=[float(nu[bins==b].mean()) if np.any(bins==b) else None
             for b in range(4)]
    out['hour_profile']=profile
    return out


def score_metrics(sim,actual):
    result={}
    for k in KEYS[:-1]:
        result[k]=abs(sim[k]-actual[k])
    pairs=[(s,o) for s,o in zip(sim['hour_profile'],actual['hour_profile'])
           if s is not None and o is not None]
    result['hour_profile_rmse']=float(np.sqrt(np.mean([(s-o)**2
                                      for s,o in pairs]))) if len(pairs)==4 else None
    return result


def state_catalog(x,clock,block):
    """State depends ONLY on trailing activity and |z| in prefix."""
    x=np.asarray(x,float)
    clock=np.asarray(clock,dtype=np.int64)
    if len(x)!=len(clock) or block>=len(x)//4:
        raise ValueError('Insufficient calibration history')
    window=max(6,min(24,block))
    p=np.abs(x[:,0])+.5*np.maximum(x[:,2],0)
    trailing=np.convolve(p,np.ones(window)/window,'full')[:len(x)]
    # Account for causal warm-up: first block is not eligible.
    valid=np.arange(window,len(x)-block+1)
    median=float(np.median(trailing[valid]))
    states=(trailing>median).astype(int)
    starts=valid
    entry=states[starts]
    bins=clock_bin(clock[starts])
    if not np.all(np.diff(clock)>0):
        raise ValueError('Historical timestamps not strictly ascending')
    # Markov transitions over historical block-start states.
    hop=np.arange(window,len(x)-block,block)
    transitions=np.ones((2,2),float) # Laplace smoothing
    for previous,next_ in zip(states[hop[:-1]],states[hop[1:]]):
        transitions[int(previous),int(next_)]+=1
    transitions/=transitions.sum(axis=1,keepdims=True)
    return {'x':x,'times':clock,'states':states,'start':starts,
            'entry_states':entry,'bins':bins,'transitions':transitions,
            'block':block,'median_score':median,'window':window}


def stationary_path(past,n,seed,block):
    rng=np.random.default_rng(seed)
    return circular_blocks(past,rng,block)[:n]


def regime_clock_path(catalog,times,seed):
    """Synchronous trivariate historical blocks; state-transition memory.

    Clock candidates from EXACT six-hour bins when available. Fallback to
    same regime is reported and never silently claims calendar fidelity.
    """
    rng=np.random.default_rng(seed)
    n=len(times)
    block=catalog['block']
    out=np.empty((n,3),float)
    fallback=0;matched=0
    # Choose initial state from empirical distribution of the catalog.
    state=int(rng.choice([0,1],p=np.bincount(
        catalog['entry_states'],minlength=2)/len(catalog['entry_states'])))
    states=[]
    cursor=0
    while cursor<n:
        slot=int(clock_bin([times[cursor]])[0])
        candidates=np.flatnonzero(
            (catalog['entry_states']==state)&(catalog['bins']==slot))
        if not len(candidates):
            fallback+=1
            candidates=np.flatnonzero(catalog['entry_states']==state)
        else:matched+=1
        if not len(candidates):raise ValueError('Empty state block catalog')
        origin=int(catalog['start'][int(rng.choice(candidates))])
        take=min(block,n-cursor)
        out[cursor:cursor+take]=catalog['x'][origin:origin+take]
        states.append(state)
        cursor+=take
        state=int(rng.choice([0,1],p=catalog['transitions'][state]))
    return out,{'clock_matched_blocks':matched,'fallback_blocks':fallback,
                'n_blocks':len(states),
                'state_switch_fraction':float(np.mean(np.diff(states)!=0))
                if len(states)>1 else 0.,
                'state_one_fraction':float(np.mean(states))}


def fitted_catalog(prefix,interval):
    t=prefix.timestamp.to_numpy(np.int64)
    coordinates=flow_coordinates(prefix)[['z','iota','nu']].to_numpy(float)
    valid=np.isfinite(coordinates).all(axis=1)
    start=int(np.flatnonzero(valid)[0]) if valid.any() else len(valid)
    if start>len(valid)-2000 or not valid[start:].all():
        raise ValueError('Prefix contains invalid internal coordinates')
    return (coordinates[start:],t[start:])


def null_paths(prefix,interval,seed,reps=REPS):
    """Fit all models ONLY to prefix; return a callable generator and specs."""
    step=STEP[interval];window=WINDOW[interval]
    xyz,t=fitted_catalog(prefix,interval)
    if not np.all(np.diff(t)==step):
        raise ValueError('Calibration prefix has gaps')
    future_t=int(prefix.timestamp.iloc[-1])+np.arange(1,window+1)*step
    short=SHORT[interval];long=LONG[interval]
    catalog_s=state_catalog(xyz,t,short)
    catalog_l=state_catalog(xyz,t,long)
    sf1=fit_sf1(prefix)
    if not sf1.garch.get('converged',False):
        raise ValueError('GARCH fit did not converge')
    vol=fit_volume(prefix,'both',step)
    def draw(model,repeat):
        s=seed+repeat*107+MODELS.index(model)*100003
        if model=='N0_stationary':
            return stationary_path(xyz,window,s,short),{'kind':'stationary'}
        if model=='N1_SF1_M5':
            base=simulate_sf1(sf1,window+BURN,seed=s,step_ms=step)
            modified=ablated_path(base,prefix,vol,step,seed=s+1)
            # Do not construct post-window geometry from the burn-in prefix.
            simulated=flow_coordinates(modified)[['z','iota','nu']].to_numpy(float)[-window:]
            return simulated,{'kind':'garch_volume_memory_calendar'}
        cat=catalog_s if model=='N2_regime_short' else catalog_l
        return regime_clock_path(cat,future_t,s)
    return draw,{'prefix_used':len(prefix),'coordinate_prefix_used':len(xyz),
                 'catalogue_short':len(catalog_s['start']),
                 'catalogue_long':len(catalog_l['start']),
                 'state_transition_short':catalog_s['transitions'].tolist(),
                 'state_transition_long':catalog_l['transitions'].tolist()},future_t


def evaluate(prefix,future,interval,seed,reps=REPS):
    if len(future)!=WINDOW[interval] or len(prefix)!=PREFIX[interval]:
        raise ValueError('Unexpected calibration/evaluation lengths')
    clock=np.r_[prefix.timestamp.to_numpy(np.int64),
                future.timestamp.to_numpy(np.int64)]
    if not np.all(np.diff(clock)==STEP[interval]):
        raise ValueError('Gap in origin')
    actual=flow_coordinates(__import__('pandas').concat(
        [prefix,future],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-len(future):]
    if not np.isfinite(actual).all():raise ValueError('Unusable observed coordinates')
    actual_m=temporal_metrics(actual,future.timestamp.to_numpy(np.int64))
    # Independent distribution fitting for measurement; no holdout as calibration.
    from experiments.precisao_formas_3d import split_historical
    aa,bb=split_historical(actual)
    observed=measure_samples(aa,bb,seed+5000)
    if not observed['valid']:raise ValueError('Observed HDR invalid')
    draw,parameters,times=null_paths(prefix,interval,seed,reps)
    models={}
    for model in MODELS:
        shapes=[];met=[];diagnostics=[];invalid=0
        for rep in range(reps):
            sample,info=draw(model,rep)
            if not np.isfinite(sample).all():
                invalid+=1;continue
            m=temporal_metrics(sample,times)
            met.append(score_metrics(m,actual_m))
            a,b=split_historical(sample)
            d=measure_samples(a,b,seed+50000+rep*19)
            if d['valid']:
                shapes.append(d['distance_512'])
            else:invalid+=1
            diagnostics.append(info)
        if not shapes:models[model]={'n_valid':0,'n_failed':reps,'metrics':None};continue
        n_valid=len(shapes)
        errs={k:[v[k] for v in met if v[k] is not None] for k in KEYS}
        models[model]={'n_valid':n_valid,'n_requested':reps,
            'n_failed':invalid,'distance_median':float(np.median(shapes)),
            'distance_q10_q50_q90':[float(v) for v in np.quantile(shapes,[.1,.5,.9])]
                if n_valid>=4 else None,
            'actual_above_q90':bool(observed['distance_512']>np.quantile(shapes,.9))
                if n_valid>=4 else None,
            'median_abs_error':{k:float(np.median(v)) if v else None
                                for k,v in errs.items()},
            'calendar_exact_match_rate':float(sum(z.get('clock_matched_blocks',0)
                                                for z in diagnostics)/
                                           max(1,sum(z.get('n_blocks',0)
                                                for z in diagnostics)))
              if model.startswith('N2') or model.startswith('N3') else None,
            'calendar_fallback_blocks':int(sum(z.get('fallback_blocks',0)
                                              for z in diagnostics)),
            'median_state_switch':float(np.median([
                z['state_switch_fraction'] for z in diagnostics
                if 'state_switch_fraction' in z]))
                if model.startswith('N2') or model.startswith('N3') else None}
    return {'asof_ms':int(future.timestamp.iloc[-1]+STEP[interval]),
            'actual_distance_512':float(observed['distance_512']),
            'actual_distance_256':float(observed['distance_256']),
            'actual_temporal_metrics':actual_m,'fit':parameters,'models':models}


def aggregate(rows):
    out={'n_origins':len(rows),'models':{}}
    for model in MODELS:
        rs=[r['models'][model] for r in rows if r['models'][model].get('n_valid',0)>=4]
        out['models'][model]={
            'n_usable_origins':len(rs),
            'n_above_q90':int(sum(r['actual_above_q90'] is True for r in rs)),
            'median_simulated_distance':float(np.median([
                r['distance_median'] for r in rs])) if rs else None,
            'adequacy_median_abs_error':{
                k:float(np.median([r['median_abs_error'][k] for r in rs]))
                if rs else None for k in KEYS}}
    return out


def calibration():
    rng=np.random.default_rng(319)
    n=5000
    state=np.empty(n,dtype=int);state[0]=0
    for i in range(1,n):
        state[i]=state[i-1] if rng.random()<.96 else 1-state[i-1]
    x=rng.normal(size=(n,3))
    x[:,0]*=(1+1.5*state)
    x[:,1]=np.tanh(.8*x[:,0]+rng.normal(size=n))
    x[:,2]=.75*state+.35*np.abs(x[:,0])+rng.normal(size=n)*.2
    times=np.arange(n,dtype=np.int64)*60000
    cat=state_catalog(x,times,60)
    assert cat['transitions'][0,0]>.5 and cat['transitions'][1,1]>.5
    output,log=regime_clock_path(cat,times[-1500:]+60000*1500,seed=99)
    assert np.isfinite(output).all() and log['n_blocks']>=20
    assert 0<=log['clock_matched_blocks']<=log['n_blocks']
    original=stationary_path(x,400,120,15)
    rerun=stationary_path(x,400,120,15)
    np.testing.assert_array_equal(original,rerun)
    return {'status':'M12_CALIBRATION',
            'states_empirical_transition':cat['transitions'].tolist(),
            'regime_simulation':log,
            'chronology_reused_past_only':True,
            'warning':'Synthetic persistence is an engineering control'}


def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('No approved exploratory archives')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    pre=PREFIX[interval];w=WINDOW[interval];step=STEP[interval]
    t=df.timestamp.to_numpy(np.int64)
    starts=[i for i in range(pre,len(df)-w+1,w) if
            np.all(np.diff(t[i-pre:i+w])==step)]
    if not starts:raise RuntimeError('No contiguous origins')
    chosen=np.linspace(0,len(starts)-1,min(ORIGINS,len(starts)),dtype=int)
    rows=[];fail=[]
    for j,k in enumerate(chosen):
        i=starts[int(k)]
        try:
            rows.append(evaluate(df.iloc[i-pre:i].copy(),
                                 df.iloc[i:i+w].copy(),
                                 interval,SEED+j*1000))
        except (ValueError,RuntimeError,AssertionError,np.linalg.LinAlgError) as e:
            fail.append({'origin':int(i),'error':str(e)})
    if not rows:raise RuntimeError('All sampled origins failed: '+str(fail))
    path=ROOT/'reports'/f'SGV_M12_{interval}_metrics.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=['asof_ms','model','actual_distance',
                      'sim_distance_median','above_q90','valid_draws',
                      'nu_acf1_error','nu_acf10_error','nu_std_error'])
        writer.writeheader()
        for row in rows:
            for model,r in row['models'].items():
                e=r.get('median_abs_error') or {}
                writer.writerow({'asof_ms':row['asof_ms'],'model':model,
                    'actual_distance':row['actual_distance_512'],
                    'sim_distance_median':r.get('distance_median'),
                    'above_q90':r.get('actual_above_q90'),
                    'valid_draws':r.get('n_valid'),
                    'nu_acf1_error':e.get('nu_acf1'),
                    'nu_acf10_error':e.get('nu_acf10'),
                    'nu_std_error':e.get('nu_std')})
    return {'status':'M12_EXPLORATORY','interval':interval,
            'n_eligible':len(starts),'n_selected':len(chosen),
            'n_valid_origins':len(rows),'failures':fail,
            'summary':aggregate(rows),'origins':rows,
            'confirmatory_opened':False,
            'warnings':['Six null draws per origin insufficient for calibrated q90',
                        'Regime-clock block models heuristic, not verified faithful',
                        'Four origins not independent market validation',
                        'No physical law, causal information or market stress interpretation']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--interval',required=True,choices=('synthetic','1m','1h'))
    a=p.parse_args()
    r=calibration() if a.interval=='synthetic' else real(a.interval)
    file=ROOT/'reports'/f'SGV_M12_{a.interval}.json'
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(r,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
