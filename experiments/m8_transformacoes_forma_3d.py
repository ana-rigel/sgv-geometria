#!/usr/bin/env python3
"""M8: direct four-way (non-additive) HDR50 shape-motion observation."""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import fit_sf1,simulate_sf1,flow_coordinates,default_sf1
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.m5_validacao_conjunta_sf1 import fit_volume,PREFIX,WINDOW,STEP
from experiments.m6_acoplamento_residual_hdr import simulate_coupled
from experiments.m4_sf1_memoria_sazonalidade import ablated_path,BURN
from experiments.precisao_formas_3d import split_historical
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.isosuperficies_morfometria import (
    make_grid,density_values,hdr_thresholds,extract_mesh,describe_mesh,motion,
    analytic_field)

SEED=20261009
ORIGINS=6
SIMS=3
BOOTSTRAP_ORIGINS=3
BOOTSTRAP_REPS=12
GRID=35
GRID_CHECK=49
VARIANTS=('sf1','m5','m6')
SCALARS=('translation_norm','volume_log_change',
         'rotation_angle_deg','chamfer_residual_normalized')


def surface(x,n=GRID,seed=SEED):
    pts,spacing=make_grid(n)
    densities=density_values(x,pts,'mixture',seed=seed)
    field=densities.reshape((n,n,n))
    thresholds,coverage=hdr_thresholds(field,spacing)
    mesh,truncated=extract_mesh(field,thresholds[.5]['tau'],spacing)
    props=describe_mesh(mesh,truncated=truncated,coverage=coverage)
    return mesh,props


def motion_of_pairs(a,b,n=GRID,seed=SEED):
    ma,pa=surface(a,n,seed)
    mb,pb=surface(b,n,seed+1)
    if not pa['quality_pass'] or not pb['quality_pass']:
        return {'valid':False,'reason':pa.get('invalid_reason') or
                pb.get('invalid_reason')}
    try:
        mv=motion(ma,pa,mb,pb,seed=seed+2)
    except (ValueError,np.linalg.LinAlgError,RuntimeError) as e:
        return {'valid':False,'reason':'motion_failure: '+str(e)}
    if not mv['quality_pass']:
        return {'valid':False,'reason':mv.get('reason','unknown')}
    return {'valid':True,
            'translation_vector':mv['translation_vector'],
            'translation_norm':float(mv['translation_norm']),
            'volume_log_change':float(mv['volume_log_change']),
            'volume_ratio':float(mv['volume_ratio']),
            'isotropic_scale':float(mv['isotropic_scale']),
            'orientation_identifiable':bool(mv['orientation_identifiable']),
            'rotation_angle_deg':mv['rotation_angle_deg'],
            'chamfer_residual_normalized':mv['chamfer_residual_normalized'],
            'gap_a':pa['orientation_gap'],'gap_b':pb['orientation_gap']}


def signature(frame,window,seed,n=GRID):
    x=flow_coordinates(frame)[['z','iota','nu']].to_numpy(float)[-window:]
    if not np.isfinite(x).all():
        return {'valid':False,'reason':'nonfinite_coordinates'}
    a,b=split_historical(x)
    return motion_of_pairs(a,b,n,seed)


def bootstrap_observation(frame,window,seed,block,reps=BOOTSTRAP_REPS):
    x=flow_coordinates(frame)[['z','iota','nu']].to_numpy(float)[-window:]
    a,b=split_historical(x)
    rng=np.random.default_rng(seed)
    values={k:[] for k in SCALARS}
    rejected=0
    for j in range(reps):
        aa=circular_blocks(a,rng,block)
        bb=circular_blocks(b,rng,block)
        result=motion_of_pairs(aa,bb,GRID,seed+100+2*j)
        if not result['valid']:
            rejected+=1
            continue
        for key in SCALARS:
            if result[key] is not None:values[key].append(result[key])
    return {'n_total':reps,'n_rejected':rejected,
            'quantiles_descriptive':{
              k:([float(t) for t in np.quantile(v,[.1,.5,.9])]
                 if len(v)>=max(6,reps//2) else None)
              for k,v in values.items()},
            'n_identifiable':{k:len(v) for k,v in values.items()},
            'warning':'Quantiles of block-refitted shapes, not calibrated CIs'}


def check_resolution(frame,window,seed):
    return {str(n):signature(frame,window,seed,n)
            for n in (GRID,GRID_CHECK)}


def evaluate_origin(prefix,window,step,seed,reps=SIMS,bootstrap=False,
                    resolution=False):
    if not np.all(np.diff(np.r_[
        prefix.timestamp.to_numpy(np.int64),
        window.timestamp.to_numpy(np.int64)])==step):
        raise ValueError('Gap in origin')
    fitted_sf1=fit_sf1(prefix)
    if not fitted_sf1.garch.get('converged',False):
        raise ValueError('SF1 GARCH did not converge')
    volume_fit=fit_volume(prefix,'both',step)
    actual=pd.concat([prefix,window],ignore_index=True)
    observed=signature(actual,len(window),seed)
    if not observed['valid']:
        raise ValueError('Real shape invalid: '+observed.get('reason',''))
    simulated={k:[] for k in VARIANTS}
    for j in range(reps):
        base=simulate_sf1(fitted_sf1,len(window)+BURN,
                          seed=seed+103*j,step_ms=step)
        base['timestamp']=int(prefix.timestamp.iloc[-1])+(
            np.arange(len(base))+1-BURN)*step
        m5=ablated_path(base,prefix,volume_fit,step,
                        seed=seed+10000+103*j)
        m6,_=simulate_coupled(base,prefix,fitted_sf1,volume_fit,step,
                              seed=seed+10000+103*j)
        ref=flow_coordinates(base)[['z','iota']].to_numpy(float)[-len(window):]
        for model,frame in zip(VARIANTS,(base,m5,m6)):
            check=flow_coordinates(frame)[['z','iota']].to_numpy(float)[-len(window):]
            if not np.allclose(ref,check,atol=1e-10,rtol=0):
                raise AssertionError('Relative flow or returns altered')
            simulated[model].append(signature(frame,len(window),
                                              seed+20000+1000*j))
    models={}
    for model,records in simulated.items():
        valid=[r for r in records if r['valid']]
        summaries={}
        errors={}
        for k in SCALARS:
            usable=[r[k] for r in valid if r[k] is not None]
            enough=len(usable)>=max(2,(reps+1)//2)
            summaries[k]=float(np.median(usable)) if enough else None
            errors[k]=(float(abs(summaries[k]-observed[k])) if enough and
                       observed[k] is not None else None)
        models[model]={'n_valid':len(valid),'n_total':reps,
                       'n_rotatable':sum(r['rotation_angle_deg'] is not None
                                         for r in valid),
                       'median':summaries,'errors':errors}
    out={'asof_ms':int(window.timestamp.iloc[-1]+step),
         'observed':observed,'models':models,
         'bootstrap':None,'resolution':None}
    if bootstrap:
        out['bootstrap']=bootstrap_observation(actual,len(window),seed+90000,
                                               block=15 if step==60000 else 12)
    if resolution:
        out['resolution']=check_resolution(actual,len(window),seed)
    return out


def summarise(rows):
    out={'n_origins':len(rows),'models':{},'paired_m6_vs_m5':{}}
    for model in VARIANTS:
        out['models'][model]={}
        for key in SCALARS:
            errors=[r['models'][model]['errors'][key] for r in rows
                    if r['models'][model]['errors'][key] is not None]
            out['models'][model][key]={
                'n_valid':len(errors),
                'median_abs_error':float(np.median(errors)) if errors else None}
    for key in SCALARS:
        paired=[r for r in rows if
                r['models']['m6']['errors'][key] is not None and
                r['models']['m5']['errors'][key] is not None]
        difference=[r['models']['m6']['errors'][key]-
                    r['models']['m5']['errors'][key] for r in paired]
        out['paired_m6_vs_m5'][key]={
            'n_pairs':len(difference),
            'gate':len(difference)>=4,
            'm6_better':int(sum(d<0 for d in difference)),
            'median_error_delta_m6_minus_m5':
                float(np.median(difference)) if difference else None}
    return out


def calibrate():
    # Known geometry independent of fitted models.
    f,t,dx=analytic_field('sphere',n=61)
    from experiments.isosuperficies_morfometria import extract_mesh,describe_mesh
    m,tr=extract_mesh(f,t,dx)
    p=describe_mesh(m,truncated=tr,coverage=1.)
    shifted=m.copy()
    shifted.apply_translation([.4,-.3,.2])
    q=describe_mesh(shifted,coverage=1.)
    measured=motion(m,p,shifted,q,seed=SEED)
    assert measured['quality_pass']
    assert not measured['orientation_identifiable']
    assert np.allclose(measured['translation_vector'],[.4,-.3,.2],atol=.005)
    assert abs(measured['volume_log_change'])<1e-8
    # A deformation can be rejected separately without zero-filling.
    rng=np.random.default_rng(23)
    x=rng.normal(size=(600,3))
    z=motion_of_pairs(x,x,GRID,seed=44)
    assert z['valid']
    return {'status':'M8_SYNTHETIC_CALIBRATION',
            'known_sphere_shift':measured['translation_vector'],
            'sphere_rotation_unidentifiable':True,
            'same_distribution_motion_valid':True}


def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('Exploratory BTC archives absent')
    for f in paths:checked_exploratory_month(f.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    pre=PREFIX[interval];w=WINDOW[interval];step=STEP[interval]
    ts=df.timestamp.to_numpy(np.int64)
    origins=[i for i in range(pre,len(df)-w+1,w)
             if np.all(np.diff(ts[i-pre:i+w])==step)]
    if not origins:raise RuntimeError('No continuous eligible origins')
    pick=np.linspace(0,len(origins)-1,min(ORIGINS,len(origins)),dtype=int)
    boot={0,len(pick)//2,len(pick)-1}
    grid={0,len(pick)-1}
    rows=[];failures=[]
    for j,index in enumerate(pick):
        start=origins[int(index)]
        try:
            rows.append(evaluate_origin(
                df.iloc[start-pre:start].copy(),
                df.iloc[start:start+w].copy(),step,SEED+j*1000,
                bootstrap=j in boot,resolution=j in grid))
        except (ValueError,RuntimeError,AssertionError,np.linalg.LinAlgError) as ex:
            failures.append({'origin':int(start),'reason':str(ex)})
    if not rows:raise RuntimeError(f'No successful origins: {failures}')
    path=ROOT/'reports'/f'SGV_M8_{interval}_movements.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=[
          'asof_ms','model','metric','observed',
          'median_simulated','abs_error','valid_simulations'])
        writer.writeheader()
        for r in rows:
            for model in VARIANTS:
                for key in SCALARS:
                    writer.writerow({'asof_ms':r['asof_ms'],
                         'model':model,'metric':key,
                         'observed':r['observed'][key],
                         'median_simulated':r['models'][model]['median'][key],
                         'abs_error':r['models'][model]['errors'][key],
                         'valid_simulations':r['models'][model]['n_valid']})
    return {'status':'M8_BTC_EXPLORATORY','interval':interval,
            'n_candidate':len(origins),'n_selected':len(pick),
            'n_valid':len(rows),'failures':failures,
            'summary':summarise(rows),
            'audits':[{'asof_ms':r['asof_ms'],
                       'observed':r['observed'],
                       'bootstrap':r['bootstrap'],
                       'resolution':r['resolution']}
                      for r in rows if r['bootstrap'] or r['resolution']],
            'confirmed_periods_read':False,
            'warnings':['No unique additive four-motion decomposition',
                        'Small number of simulators and block replicates',
                        'Rotation undefined for near-degenerate inertia axes',
                        'Sampled Chamfer is only residual after conventional alignment',
                        'Geometrical state shape not proven to predict or cause market stress']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--interval',required=True,
                        choices=('synthetic','1m','1h'))
    args=parser.parse_args()
    out=calibrate() if args.interval=='synthetic' else real(args.interval)
    dest=ROOT/'reports'/f'SGV_M8_{args.interval}.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
