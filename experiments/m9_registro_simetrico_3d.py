#!/usr/bin/env python3
"""SGV M9: quotient rotation of inertia axes + held-out free rigid registration.

The rotation of a registered shell is NOT an identified physical spin.
Only pre-cutoff BTC exploratory archives permitted.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
import trimesh
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import fit_sf1,simulate_sf1,flow_coordinates
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.m5_validacao_conjunta_sf1 import fit_volume,PREFIX,WINDOW,STEP
from experiments.m6_acoplamento_residual_hdr import simulate_coupled
from experiments.m4_sf1_memoria_sazonalidade import ablated_path,BURN
from experiments.precisao_formas_3d import split_historical
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.isosuperficies_morfometria import (
    make_grid,density_values,hdr_thresholds,extract_mesh,describe_mesh,
    principal_axes,analytic_field)
SEED=20261009
N_ORIGINS=6
N_SIM=3
N_BOOT=8
TRAIN_POINTS=360
TEST_POINTS=360
GRID=35
GRID_CHECK=49
METRICS=('translation_norm','volume_log_change',
         'axis_angle_deg','heldout_deformation')
MODELS=('sf1','m5','m6')


def angle_deg(R):
    return float(np.rad2deg(np.arccos(np.clip((np.trace(R)-1)/2.,-1.,1.))))


def quotient_axis_angle(a,b,gap=.07):
    """Angular distance in SO(3)/D2, not directional eigenvector rotation."""
    qa,ga=principal_axes(a)
    qb,gb=principal_axes(b)
    if qa is None or qb is None or ga<gap or gb<gap:
        return None,{'axis_identifiable':False,'gap_a':float(ga),'gap_b':float(gb)}
    flips=((1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1))
    angles=[angle_deg(qb@np.diag(signs)@qa.T) for signs in flips]
    return float(min(angles)),{'axis_identifiable':True,
                               'gap_a':float(ga),'gap_b':float(gb)}


def normalized_mesh_points(mesh,n,seed):
    if not mesh.is_watertight:raise ValueError('Mesh not watertight')
    m=mesh.copy();m.fix_normals()
    vol=abs(float(m.volume))
    if vol<=1e-10:raise ValueError('Degenerate shell volume')
    radius=(3*vol/(4*np.pi))**(1/3)
    points,_=trimesh.sample.sample_surface(m,n,seed=seed)
    return (points-np.asarray(m.center_mass,float))/radius


def heldout_chamfer(A,B):
    da=cKDTree(B).query(A,k=1)[0]
    db=cKDTree(A).query(B,k=1)[0]
    return float(.5*(da.mean()+db.mean()))


def kabsch(source,target):
    X=source-source.mean(axis=0)
    Y=target-target.mean(axis=0)
    u,_,vt=np.linalg.svd(X.T@Y)
    fix=np.eye(3);fix[-1,-1]=np.linalg.det(u@vt)
    return u@fix@vt


def initial_rotations(ma,mb):
    ans=[np.eye(3)]
    for axis in np.eye(3):
        for deg in (90,180,270):
            ans.append(Rotation.from_rotvec(axis*np.deg2rad(deg)).as_matrix())
    qa,_=principal_axes(ma)
    qb,_=principal_axes(mb)
    if qa is not None and qb is not None:
        for signs in ((1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)):
            ans.append(qb@np.diag(signs)@qa.T)
    return ans


def icp_fit(A,B,starts,iterations=14):
    tree=cKDTree(A)
    best=None
    for start in starts:
        R=np.asarray(start,float).copy()
        last=np.inf
        for i in range(iterations):
            transformed=B@R
            ids=tree.query(transformed,k=1)[1]
            delta=kabsch(transformed,A[ids])
            R=R@delta
            score=heldout_chamfer(A,B@R)
            if abs(last-score)<1e-6:break
            last=score
        score=heldout_chamfer(A,B@R)
        if best is None or score<best[0]:
            best=(score,R.copy())
    return best[1],float(best[0])


def compare_meshes(ma,mb,seed=SEED,train=TRAIN_POINTS,test=TEST_POINTS):
    """Optimization is on train shell samples; scoring independent test samples."""
    if not ma.is_watertight or not mb.is_watertight:
        return {'valid':False,'reason':'open_mesh'}
    aa=ma.copy();bb=mb.copy()
    aa.fix_normals();bb.fix_normals()
    va=abs(float(aa.volume));vb=abs(float(bb.volume))
    if min(va,vb)<1e-10:
        return {'valid':False,'reason':'degenerate_volume'}
    centroid_a=np.asarray(aa.center_mass,float)
    centroid_b=np.asarray(bb.center_mass,float)
    angle,axis=quotient_axis_angle(aa,bb)
    Atr=normalized_mesh_points(aa,train,seed)
    Btr=normalized_mesh_points(bb,train,seed+1)
    R,training_error=icp_fit(Atr,Btr,initial_rotations(aa,bb))
    Ate=normalized_mesh_points(aa,test,seed+2)
    Bte=normalized_mesh_points(bb,test,seed+3)
    heldout=heldout_chamfer(Ate,Bte@R)
    if not np.isfinite(heldout):
        return {'valid':False,'reason':'nonfinite_deformation'}
    return {'valid':True,
            'translation_vector':[float(x) for x in centroid_b-centroid_a],
            'translation_norm':float(np.linalg.norm(centroid_b-centroid_a)),
            'volume_log_change':float(np.log(vb/va)),
            'axis_angle_deg':angle,
            'heldout_deformation':heldout,
            'training_deformation':training_error,
            'axis_identifiable':axis['axis_identifiable'],
            'gap_a':axis['gap_a'],'gap_b':axis['gap_b']}


def shell(sample,seed,n=GRID):
    pts,dx=make_grid(n)
    density=density_values(sample,pts,'mixture',seed)
    field=density.reshape((n,n,n))
    levels,coverage=hdr_thresholds(field,dx)
    mesh,truncated=extract_mesh(field,levels[.5]['tau'],dx)
    props=describe_mesh(mesh,truncated=truncated,coverage=coverage)
    if not props['quality_pass']:
        raise ValueError('Quality gate: '+str(props['invalid_reason']))
    return mesh


def measure_pair(a,b,seed=SEED,n=GRID):
    try:
        ma=shell(a,seed,n);mb=shell(b,seed+1,n)
        return compare_meshes(ma,mb,seed+2)
    except (ValueError,np.linalg.LinAlgError,RuntimeError) as exc:
        return {'valid':False,'reason':str(exc)}


def measure_frame(frame,window,seed,n=GRID):
    x=flow_coordinates(frame)[['z','iota','nu']].to_numpy(float)[-window:]
    if not np.isfinite(x).all():
        return {'valid':False,'reason':'nonfinite_coordinates'}
    a,b=split_historical(x)
    return measure_pair(a,b,seed,n)


def bootstrap(frame,window,seed,block,reps=N_BOOT):
    x=flow_coordinates(frame)[['z','iota','nu']].to_numpy(float)[-window:]
    a,b=split_historical(x)
    rng=np.random.default_rng(seed)
    draws={k:[] for k in METRICS}
    invalid=0
    for j in range(reps):
        aa=circular_blocks(a,rng,block)
        bb=circular_blocks(b,rng,block)
        d=measure_pair(aa,bb,seed+400+j)
        if not d['valid']:
            invalid+=1;continue
        for key in METRICS:
            if d[key] is not None:
                draws[key].append(float(d[key]))
    ax=draws['axis_angle_deg']
    valid_ratio=len(ax)/max(1,reps-invalid)
    width=float(np.quantile(ax,.9)-np.quantile(ax,.1)) if len(ax)>=4 else None
    rotation_stable=bool(len(ax)>=6 and valid_ratio>=.75
                         and width is not None and width<=45)
    return {'n_replicates':reps,'n_invalid_meshes':invalid,
            'n_axis_identifiable':len(ax),
            'rotation_stable':rotation_stable,
            'angle_greater_90_fraction':(
                float(np.mean(np.asarray(ax)>90)) if ax else None),
            'angle_q90_minus_q10':width,
            'q10_q50_q90':{
                k:[float(v) for v in np.quantile(vals,[.1,.5,.9])]
                  if len(vals)>=4 else None
                for k,vals in draws.items()},
            'warning':'Descriptive bootstrap quantiles, not calibrated coverage'}


def trial(prefix,window,step,seed,n_sim=N_SIM,check=False):
    ts=np.r_[prefix.timestamp.to_numpy(np.int64),
             window.timestamp.to_numpy(np.int64)]
    if not np.all(np.diff(ts)==step):
        raise ValueError('Discontinuous origin')
    fitted=fit_sf1(prefix)
    if not fitted.garch.get('converged',False):
        raise ValueError('SF1 fit did not converge')
    volume=fit_volume(prefix,'both',step)
    combined=pd.concat([prefix,window],ignore_index=True)
    obs=measure_frame(combined,len(window),seed)
    if not obs['valid']:
        raise ValueError('Observed mesh invalid: '+obs.get('reason',''))
    sims={k:[] for k in MODELS}
    for j in range(n_sim):
        sf1=simulate_sf1(fitted,len(window)+BURN,
                         seed=seed+103*j,step_ms=step)
        sf1['timestamp']=int(prefix.timestamp.iloc[-1])+(
            np.arange(len(sf1))+1-BURN)*step
        m5=ablated_path(sf1,prefix,volume,step,seed+10000+j*103)
        m6,_=simulate_coupled(sf1,prefix,fitted,volume,step,seed+10000+j*103)
        reference=flow_coordinates(sf1)[['z','iota']].to_numpy(float)[-len(window):]
        for name,frame in zip(MODELS,(sf1,m5,m6)):
            observed=flow_coordinates(frame)[['z','iota']].to_numpy(float)[-len(window):]
            if not np.allclose(reference,observed,rtol=0,atol=1e-10):
                raise AssertionError('Simulated price/flow path drift')
            sims[name].append(measure_frame(frame,len(window),seed+7000+j))
    models={}
    for name,draws in sims.items():
        valid=[v for v in draws if v['valid']]
        model={'n_total':len(draws),'n_valid':len(valid),
               'n_axis_identifiable':sum(d['axis_angle_deg'] is not None
                                         for d in valid),
               'median':{},'abs_error':{}}
        for k in METRICS:
            sample=[float(v[k]) for v in valid if v[k] is not None]
            value=(float(np.median(sample)) if len(sample)>=max(2,(n_sim+1)//2)
                   else None)
            model['median'][k]=value
            model['abs_error'][k]=(float(abs(value-obs[k]))
                if value is not None and obs[k] is not None else None)
        models[name]=model
    outcome={'asof_ms':int(window.timestamp.iloc[-1]+step),
             'observed':obs,'models':models,'bootstrap':None,'grid':None}
    if check:
        outcome['bootstrap']=bootstrap(combined,len(window),seed+99000,
                                      15 if step==60000 else 12)
        outcome['grid']={
            str(n):measure_frame(combined,len(window),seed,n)
            for n in (GRID,GRID_CHECK)}
    return outcome


def aggregate(rows):
    summary={'n_origins':len(rows),'models':{},'paired_m6_vs_m5':{}}
    for name in MODELS:
        summary['models'][name]={}
        for key in METRICS:
            values=[r['models'][name]['abs_error'][key] for r in rows
                    if r['models'][name]['abs_error'][key] is not None]
            summary['models'][name][key]={
                'n_valid':len(values),
                'median_abs_error':float(np.median(values)) if values else None}
    for key in METRICS:
        paired=[r for r in rows if
                r['models']['m5']['abs_error'][key] is not None and
                r['models']['m6']['abs_error'][key] is not None]
        diffs=[r['models']['m6']['abs_error'][key]-
               r['models']['m5']['abs_error'][key] for r in paired]
        summary['paired_m6_vs_m5'][key]={
            'n_paired':len(diffs),'comparison_gate':len(diffs)>=4,
            'm6_better':int(sum(x<0 for x in diffs)),
            'median_difference':float(np.median(diffs)) if diffs else None}
    return summary


def calibrate():
    f,t,dx=analytic_field('sphere',61)
    sp,tr=extract_mesh(f,t,dx)
    if tr:raise ValueError('Unexpected sphere truncation')
    shifted=sp.copy();shifted.apply_translation([.4,-.3,.2])
    sphere=compare_meshes(sp,shifted,seed=65)
    if sphere['axis_identifiable']:
        raise AssertionError('Sphere orientation falsely identifiable')
    if abs(sphere['translation_norm']-np.sqrt(.29))>.01:
        raise AssertionError('Sphere translation mismatch')
    a=sp.copy();b=sp.copy()
    a.apply_scale([1.5,1.,.65])
    b.apply_scale([1.5,1.,.65])
    b.apply_transform(Rotation.from_euler('z',25,degrees=True).as_matrix()
                      if False else np.eye(4))
    # Known rigid rotation with center fixed
    m=np.eye(4);m[:3,:3]=Rotation.from_euler('z',25,degrees=True).as_matrix()
    b.apply_transform(m)
    b.apply_scale(1.1)
    aligned=compare_meshes(a,b,seed=73)
    if aligned['axis_angle_deg'] is None or not 15<aligned['axis_angle_deg']<35:
        raise AssertionError('Ellipsoid quotient rotation not recovered')
    if abs(aligned['volume_log_change']-3*np.log(1.1))>.03:
        raise AssertionError('Ellipsoid volume change mismatch')
    deformed=b.copy()
    deformed.apply_scale([1.18,.78,1.])
    residual=compare_meshes(a,deformed,seed=73)
    return {'status':'M9_CALIBRATION',
            'sphere_translation_norm':sphere['translation_norm'],
            'sphere_axis_rotation':sphere['axis_angle_deg'],
            'sphere_deformation_holdout':sphere['heldout_deformation'],
            'ellipsoid_axis_angle':aligned['axis_angle_deg'],
            'ellipsoid_holdout_deformation':aligned['heldout_deformation'],
            'ellipsoid_deformed_holdout':residual['heldout_deformation'],
            'known_expansion_log_volume':aligned['volume_log_change']}


def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('Exploratory BTC archives unavailable')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    pre=PREFIX[interval];w=WINDOW[interval];step=STEP[interval]
    time=df.timestamp.to_numpy(np.int64)
    candidates=[i for i in range(pre,len(df)-w+1,w)
                if np.all(np.diff(time[i-pre:i+w])==step)]
    if not candidates:raise ValueError('No contiguous origins')
    chosen=np.linspace(0,len(candidates)-1,
                       min(N_ORIGINS,len(candidates)),dtype=int)
    audit={0,len(chosen)-1}
    rows=[];errors=[]
    for j,index in enumerate(chosen):
        position=candidates[int(index)]
        try:
            rows.append(trial(df.iloc[position-pre:position].copy(),
                              df.iloc[position:position+w].copy(),
                              step,SEED+j*1000,check=j in audit))
        except (ValueError,RuntimeError,AssertionError,np.linalg.LinAlgError) as e:
            errors.append({'origin':int(position),'reason':str(e)})
    if not rows:raise RuntimeError('All M9 origins failed: '+str(errors))
    target=ROOT/'reports'/f'SGV_M9_{interval}_metrics.csv'
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=[
            'asof_ms','model','metric','actual','sim_median',
            'abs_error','n_valid','n_axes'])
        writer.writeheader()
        for row in rows:
            for model,record in row['models'].items():
                for key in METRICS:
                    writer.writerow({
                        'asof_ms':row['asof_ms'],'model':model,'metric':key,
                        'actual':row['observed'][key],
                        'sim_median':record['median'][key],
                        'abs_error':record['abs_error'][key],
                        'n_valid':record['n_valid'],
                        'n_axes':record['n_axis_identifiable']})
    return {'status':'M9_EXPLORATORY','timeframe':interval,
            'eligible_origins':len(candidates),'selected_origins':len(chosen),
            'valid_origins':len(rows),'failures':errors,
            'no_confirmatory_data':True,'summary':aggregate(rows),
            'audit':[{'asof_ms':r['asof_ms'],'observed':r['observed'],
                      'bootstrap':r['bootstrap'],'grid':r['grid']}
                     for r in rows if r['bootstrap'] is not None],
            'limitations':['Rotation of axes is a quotient measurement, not material spin',
                           'Heldout deformation is estimated from surface samples',
                           'Multistart ICP may still have local minima',
                           'Eight block replicates and three sims are engineering diagnostics',
                           'No market stress or predictive claim']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--interval',choices=('synthetic','1m','1h'),required=True)
    a=parser.parse_args()
    result=calibrate() if a.interval=='synthetic' else real(a.interval)
    file=ROOT/'reports'/f'SGV_M9_{a.interval}.json'
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
