#!/usr/bin/env python3
"""SGV-M6: paired volume/flow innovation control, with pilot HDR morphology.

All fits are based on the historical prefix. No claims of market causality,
physics, trading performance, or proof of Fisher-Rao intrinsic curvature.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from sgvgeo.flow import flow_coordinates, fit_sf1, simulate_sf1, default_sf1, CLIP
from sgvgeo.data import load_binance_klines
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.m5_validacao_conjunta_sf1 import (
    PREFIX,WINDOW,STEP,fit_volume,full_metrics,joint_loss)
from experiments.m4_sf1_memoria_sazonalidade import (
    ablated_path,season,BURN,LAGS)
from experiments.precisao_formas_3d import split_historical
from experiments.m2_nao_convexidade_tensao import morphology

SEED=20261009
ORIGINS=4
SIMS=6
MORPH_ORIGINS=2
MORPH_SIMS=3
BINS=16
ALL_KEYS=('nu_acf1','nu_acf10','nu_std','rho_abs_z_nu',
          'rho_iota_nu','rho_z_iota','iota_acf1','abs_z_acf1')
VARIANTS=('sf1','m5_independent','m6_coupled')


def historical_innovation_pairs(prefix,sf1,volume_fit):
    """Align SF1 flow innovations (row t-2) with M5 volume fit residuals at t."""
    coordinates=flow_coordinates(prefix)
    z=coordinates['z'].to_numpy(float)
    idx=np.arange(max(LAGS)+1,len(prefix),dtype=int)
    idx=idx[np.isfinite(z[idx])]
    e1=np.asarray(sf1.resid,float)[idx-2,0]
    e2=np.asarray(volume_fit['residual'],float)
    if e1.shape!=e2.shape or len(e1)<1500:
        raise ValueError('Residual indices could not be aligned')
    if not np.isfinite(e1).all() or not np.isfinite(e2).all():
        raise ValueError('Non-finite historical innovations')
    if e1.std()<1e-10 or e2.std()<1e-10:
        raise ValueError('Degenerate innovations')
    return e1,e2


def synthetic_flow_innovations(base,sf1):
    """Invert the exact GARCH and tanh(istar) recursions of simulate_sf1."""
    close=base.close.to_numpy(float)
    opened=base.open.to_numpy(float)
    volume=base.volume.to_numpy(float)
    buy=base.taker_buy.to_numpy(float)
    if (not np.isfinite(close).all() or not np.isfinite(opened).all()
            or np.any(close<=0) or np.any(opened<=0) or np.any(volume<=0)):
        raise ValueError('Invalid synthetic OHLCV')
    r=np.log(close/opened)
    io=2*buy/volume-1
    star=np.arctanh(np.clip(io,-CLIP,CLIP))
    a0,a1,a2=sf1.a
    g=sf1.garch
    s2=float(g['omega'])/max(1e-12,1-float(g['alpha'])-float(g['beta']))
    prev_r=0.
    prev_istar=0.
    e=np.empty(len(base))
    for k in range(len(base)):
        s2=float(g['omega'])+float(g['alpha'])*prev_r**2+float(g['beta'])*s2
        if not np.isfinite(s2) or s2<=0:raise ValueError('GARCH recursion unstable')
        z=r[k]/np.sqrt(s2)
        e[k]=star[k]-(a0+a1*z+a2*prev_istar)
        prev_r=r[k]
        prev_istar=star[k]
    if not np.isfinite(e).all():raise ValueError('Synthetic flow residual unstable')
    return e


def sample_paired_innovations(e1_test,e1_train,e2_train,seed,bins=BINS):
    """Empirical conditional draw: observed e2 given quantile bin of e1."""
    if bins<2 or bins>len(e1_train)//20:
        raise ValueError('Invalid number of conditional bins')
    rng=np.random.default_rng(seed)
    cuts=np.quantile(e1_train,np.linspace(0,1,bins+1)[1:-1])
    historical=np.searchsorted(cuts,e1_train,side='right')
    sought=np.searchsorted(cuts,e1_test,side='right')
    result=np.empty(len(e1_test))
    for k in range(bins):
        targets=np.flatnonzero(sought==k)
        if not len(targets):continue
        candidates=np.flatnonzero(historical==k)
        if not len(candidates):
            raise ValueError(f'No calibration innovations in bin {k}')
        indices=rng.choice(candidates,size=len(targets),replace=True)
        result[targets]=e2_train[indices]
    return result


def volume_path_from_innovations(base,prefix,volfit,step,innovations):
    """Only volume and absolute taker buy units change; z and iota do not."""
    if len(innovations)!=len(base):
        raise ValueError('Innovation length mismatch')
    frame=base.copy()
    x=flow_coordinates(base)['z'].to_numpy(dtype=float,copy=True)
    x[~np.isfinite(x)]=0.
    ts=int(prefix.timestamp.iloc[-1])+(np.arange(len(base))+1-BURN)*step
    frame['timestamp']=ts
    past=list(np.log(np.maximum(prefix.volume.to_numpy(float)[-10:],1e-12)))
    coeff=volfit['coef']
    levels=np.empty(len(base))
    for i in range(len(base)):
        features=[*[past[-lag] for lag in volfit['lags']],abs(x[i]),x[i]]
        if volfit['season']:
            features.extend(season([ts[i]])[0].tolist())
        ell=float(volfit['intercept']+np.dot(coeff,features)+innovations[i])
        if not np.isfinite(ell) or abs(ell)>80:
            raise ValueError('Volume path diverged')
        levels[i]=ell
        past.append(ell)
    vol=np.exp(levels)
    origio=2*base.taker_buy.to_numpy(float)/base.volume.to_numpy(float)-1.
    frame['volume']=vol
    frame['taker_buy']=(1+origio)/2*vol
    return frame


def simulate_coupled(base,prefix,sf1,volfit,step,seed):
    e1_train,e2_train=historical_innovation_pairs(prefix,sf1,volfit)
    e1_gen=synthetic_flow_innovations(base,sf1)
    e2_gen=sample_paired_innovations(e1_gen,e1_train,e2_train,seed)
    frame=volume_path_from_innovations(base,prefix,volfit,step,e2_gen)
    return frame, {
        'training_flow_volume_innovation_corr':float(np.corrcoef(e1_train,e2_train)[0,1]),
        'generated_flow_volume_innovation_corr':float(np.corrcoef(e1_gen,e2_gen)[0,1]),
        'innovations_used':int(len(e2_gen)),
        'bins':BINS}


def shape_signature(frame,window,seed):
    """HDR50 only. Defined on 30%-anchor, two later slices of closed bars."""
    x=flow_coordinates(frame)[['z','iota','nu']].to_numpy(float)[-window:]
    if not np.isfinite(x).all():
        return {'valid':False,'reason':'nonfinite_coordinates'}
    a,b=split_historical(x)
    A=morphology(a,'mixture',.5,35,seed)
    B=morphology(b,'mixture',.5,35,seed+1)
    if not A['valid'] or not B['valid']:
        return {'valid':False,'reason':str(A.get('reason') or B.get('reason'))}
    return {'valid':True,
            'D_a':A['negative_intensity'],'D_b':B['negative_intensity'],
            'delta_D':B['negative_intensity']-A['negative_intensity'],
            'convex_deficit_b':B['convex_hull_deficit']}


def diag_of(frame,window):
    obs=flow_coordinates(frame)[['z','iota','nu']].to_numpy(float)[-window:]
    if not np.isfinite(obs).all():raise ValueError('Nonfinite market coordinates')
    return full_metrics(obs)


def comparison(prefix,window,step,seed,reps=SIMS,with_morph=False):
    both=pd.concat([prefix,window],ignore_index=True)
    if not np.all(np.diff(both.timestamp.to_numpy(np.int64))==step):
        raise ValueError('Gap in prefix/evaluation')
    sf1=fit_sf1(prefix)
    if not sf1.garch.get('converged',False):
        raise ValueError('GARCH-t did not converge')
    fitted=fit_volume(prefix,'both',step)
    observed=diag_of(both,len(window))
    sim_metrics={kind:[] for kind in VARIANTS}
    coupling=[]
    shape={kind:[] for kind in ('real',*VARIANTS)}
    if with_morph:
        shape['real'].append(shape_signature(both,len(window),seed))
    for j in range(reps):
        base=simulate_sf1(sf1,len(window)+BURN,
                          seed=seed+103*j,step_ms=step)
        base['timestamp']=int(prefix.timestamp.iloc[-1])+(
            np.arange(len(base))+1-BURN)*step
        indep=ablated_path(base,prefix,fitted,step,
                          seed=seed+10000+103*j)
        coupled,record=simulate_coupled(base,prefix,sf1,fitted,step,
                                       seed=seed+10000+103*j)
        coupling.append(record)
        frames={'sf1':base,'m5_independent':indep,'m6_coupled':coupled}
        zio_ref=flow_coordinates(base)[['z','iota']].to_numpy(float)[-len(window):]
        for variant,frame in frames.items():
            zio=flow_coordinates(frame)[['z','iota']].to_numpy(float)[-len(window):]
            if not np.allclose(zio,zio_ref,atol=1e-10,rtol=0):
                raise AssertionError('Price or relative aggressive flow altered')
            sim_metrics[variant].append(diag_of(frame,len(window)))
            if with_morph and j<MORPH_SIMS:
                shape[variant].append(shape_signature(frame,len(window),seed+1000*j))
    result={'asof_ms':int(window.timestamp.iloc[-1]+step),
            'n_simulations':reps,
            'paired_innovations':coupling,
            'observed':observed,
            'metrics':{},'shape':shape if with_morph else None}
    for variant,draws in sim_metrics.items():
        med={k:float(np.median([d[k] for d in draws])) for k in ALL_KEYS}
        result['metrics'][variant]={
            'joint_loss_m5':joint_loss(med,observed),
            'abs_flow_volume_corr_error':abs(med['rho_iota_nu']-observed['rho_iota_nu']),
            'metric_errors':{k:float(abs(med[k]-observed[k])) for k in ALL_KEYS},
            'median_simulated':med}
    return result


def summarize(rows):
    result={'n_valid':len(rows),'variants':{}}
    for variant in VARIANTS:
        x=[r['metrics'][variant] for r in rows]
        out={
          'joint_loss_median':float(np.median([v['joint_loss_m5'] for v in x])),
          'flow_activity_corr_abs_error_median':float(np.median([
              v['abs_flow_volume_corr_error'] for v in x]))}
        for k in ALL_KEYS:
            out[k+'_median_abs_error']=float(np.median([
                v['metric_errors'][k] for v in x]))
        if variant=='m6_coupled':
            out['origins_improved_flow_activity_vs_m5']=int(sum(
                r['metrics']['m6_coupled']['abs_flow_volume_corr_error']<
                r['metrics']['m5_independent']['abs_flow_volume_corr_error']
                for r in rows))
            out['origins_improved_joint_loss_vs_m5']=int(sum(
                r['metrics']['m6_coupled']['joint_loss_m5']<
                r['metrics']['m5_independent']['joint_loss_m5']
                for r in rows))
        result['variants'][variant]=out
    result['mean_training_innovation_corr']=float(np.mean([
        c['training_flow_volume_innovation_corr']
        for r in rows for c in r['paired_innovations']]))
    result['mean_generated_innovation_corr']=float(np.mean([
        c['generated_flow_volume_innovation_corr']
        for r in rows for c in r['paired_innovations']]))
    morphology_audits=[]
    for r in rows:
        if r['shape'] is None:continue
        one={'asof_ms':r['asof_ms'],'real':r['shape']['real'][0]}
        for variant in VARIANTS:
            synthetic=[s for s in r['shape'][variant] if s['valid']]
            one[variant]={
                'valid':len(synthetic),'total':len(r['shape'][variant]),
                'median_D_b':float(np.median([s['D_b'] for s in synthetic]))
                   if synthetic else None,
                'median_delta_D':float(np.median([s['delta_D'] for s in synthetic]))
                   if synthetic else None,
                'median_convex_deficit_b':float(np.median([
                    s['convex_deficit_b'] for s in synthetic])) if synthetic else None}
            if synthetic and one['real']['valid']:
                one[variant]['D_b_abs_error']=abs(
                    one[variant]['median_D_b']-one['real']['D_b'])
                one[variant]['delta_D_abs_error']=abs(
                    one[variant]['median_delta_D']-one['real']['delta_D'])
        morphology_audits.append(one)
    result['morphology_HDR50_audit']=morphology_audits
    return result


def calibrate():
    # Deliberately plant strong coupled innovations and compare conditional
    # reconstruction against an independent bootstrap of the volume residual.
    planted=default_sf1()
    planted.e_corr=.85
    sample=simulate_sf1(planted,6800,seed=61)
    prefix=sample.iloc[:5000].copy()
    sf1=fit_sf1(prefix)
    fit=fit_volume(prefix,'both',60000)
    tr_e1,tr_e2=historical_innovation_pairs(prefix,sf1,fit)
    base=simulate_sf1(sf1,3600,seed=62)
    gen_e1=synthetic_flow_innovations(base,sf1)
    paired=sample_paired_innovations(gen_e1,tr_e1,tr_e2,seed=63)
    independent=tr_e2[np.random.default_rng(63).integers(len(tr_e2),size=len(gen_e1))]
    train_corr=float(np.corrcoef(tr_e1,tr_e2)[0,1])
    paired_corr=float(np.corrcoef(gen_e1,paired)[0,1])
    independent_corr=float(np.corrcoef(gen_e1,independent)[0,1])
    if abs(paired_corr-train_corr)>=abs(independent_corr-train_corr):
        raise AssertionError('Paired bootstrap did not recover planted coupling')
    frame,_=simulate_coupled(base,prefix,sf1,fit,60000,seed=63)
    assert np.array_equal(base.close.to_numpy(),frame.close.to_numpy())
    assert np.allclose(2*base.taker_buy/base.volume-1,
                       2*frame.taker_buy/frame.volume-1)
    return {'status':'M6_SYNTHETIC',
            'train_correlation':train_corr,
            'coupled_correlation':paired_corr,
            'independent_correlation':independent_corr,
            'coupling_recovery_better_than_independent':True,
            'price_and_relative_flow_unchanged':True}


def run_real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('Exploration months missing')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    pre=PREFIX[interval];win=WINDOW[interval];step=STEP[interval]
    ts=df.timestamp.to_numpy(np.int64)
    origins=[i for i in range(pre,len(df)-win+1,win)
             if np.all(np.diff(ts[i-pre:i+win])==step)]
    if not origins:raise RuntimeError('No complete windows')
    selected=np.linspace(0,len(origins)-1,min(ORIGINS,len(origins)),dtype=int)
    morphology_idx=set(np.linspace(0,len(selected)-1,
                         min(MORPH_ORIGINS,len(selected)),dtype=int))
    rows=[];failed=[]
    for j,index in enumerate(selected):
        start=origins[int(index)]
        try:
            r=comparison(df.iloc[start-pre:start].copy(),
                         df.iloc[start:start+win].copy(),step,
                         seed=SEED+j*1000,with_morph=j in morphology_idx)
            rows.append(r)
        except (AssertionError,ValueError,np.linalg.LinAlgError,RuntimeError) as e:
            failed.append({'origin':int(start),'reason':str(e)})
    if not rows:raise RuntimeError(f'All fits failed: {failed}')
    path=ROOT/'reports'/f'SGV_M6_{interval}_ablation.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['asof_ms','variant','metric','observed',
                                        'sim_median','abs_error'])
        w.writeheader()
        for r in rows:
            for v,output in r['metrics'].items():
                for k in ALL_KEYS:
                    w.writerow({'asof_ms':r['asof_ms'],'variant':v,
                                'metric':k,'observed':r['observed'][k],
                                'sim_median':output['median_simulated'][k],
                                'abs_error':output['metric_errors'][k]})
    return {'status':'M6_BTC_EXPLORATORY','interval':interval,
            'n_eligible':len(origins),'n_selected':len(selected),
            'n_valid':len(rows),'n_failure':len(failed),'failures':failed,
            'no_confirmatory_data_used':True,
            'n_simulations':SIMS,
            'n_morphology_selected':len(morphology_idx),
            'results':summarize(rows),
            'warnings':['Empirical conditional bins need larger independent calibration',
                        'Four origins and six simulations are exploratory only',
                        'M6 preserves marginal price/iota but not absolute taker buy',
                        'Morphology: HDR50 in at most two windows with three model draws',
                        'No claim of causal information flow, market stress or trading edge']}


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--interval',choices=('synthetic','1m','1h'),required=True)
    args=a.parse_args()
    out=calibrate() if args.interval=='synthetic' else run_real(args.interval)
    path=ROOT/'reports'/f'SGV_M6_{args.interval}.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
