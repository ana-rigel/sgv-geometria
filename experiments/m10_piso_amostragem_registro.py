#!/usr/bin/env python3
"""SGV-M10 — finite point-sampling floor of free 3D HDR-shell registration.

This is a measurement precision study, NOT a proof of geometric, causal or
financial novelty. The strict BTC exploration allowlist is never widened.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.precisao_formas_3d import split_historical
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m9_registro_simetrico_3d import (
    shell,compare_meshes,quotient_axis_angle)
from experiments.m5_validacao_conjunta_sf1 import WINDOW,STEP

SEED=20261009
N_WINDOWS=6
N_AUDIT=3
DENSITIES=(180,360,720)
MAIN_N=360
N_REPS=6
BOOT_REPS=16
BOOT_REG_REPS=3
GRID=35
GRID_REFINE=49
BLOCK={'1m':15,'1h':12}
METRICS=('heldout_deformation','axis_angle_deg')


def shape_meshes(x,seed,n=GRID):
    x=np.asarray(x,float)
    a,b=split_historical(x)
    if not np.isfinite(x).all():raise ValueError('Nonfinite flow coordinates')
    return shell(a,seed,n),shell(b,seed+1,n)


def six_seed_scores(ma,mb,seed,n=MAIN_N,reps=N_REPS):
    """Samples SAME meshes independently: null floor and observed pair."""
    if reps<4:raise ValueError('At least four seeds required for quantile floor')
    cross=[];self_a=[];self_b=[]
    for j in range(reps):
        s=seed+j*47
        x=compare_meshes(ma,mb,seed=s,train=n,test=n)
        a=compare_meshes(ma,ma,seed=s+10000,train=n,test=n)
        b=compare_meshes(mb,mb,seed=s+20000,train=n,test=n)
        if not (x['valid'] and a['valid'] and b['valid']):
            raise ValueError('Registration failed on fixed meshes')
        cross.append(x['heldout_deformation'])
        self_a.append(a['heldout_deformation'])
        self_b.append(b['heldout_deformation'])
    floor=max(float(np.quantile(self_a,.9)),float(np.quantile(self_b,.9)))
    median_cross=float(np.median(cross))
    return {'n_points_each_set':n,'n_seed_repeats':reps,
            'observed_median':median_cross,
            'cross_q10_q50_q90':[float(v) for v in np.quantile(cross,[.1,.5,.9])],
            'null_a_q10_q50_q90':[float(v) for v in np.quantile(self_a,[.1,.5,.9])],
            'null_b_q10_q50_q90':[float(v) for v in np.quantile(self_b,[.1,.5,.9])],
            'floor_max_self_q90':floor,
            'excess_over_floor':float(max(0,median_cross-floor)),
            'exceeds_sampling_floor':bool(median_cross>floor),
            'warning':'Empirical threshold, no calibrated false-positive probability'}


def known_shape_controls(seed=SEED,n=360,reps=6):
    from experiments.isosuperficies_morfometria import analytic_field,extract_mesh
    from scipy.spatial.transform import Rotation
    f,t,dx=analytic_field('sphere',61)
    ball,truncated=extract_mesh(f,t,dx)
    if truncated:raise ValueError('Synthetic sphere truncated')
    transformed=ball.copy()
    matrix=np.eye(4)
    matrix[:3,:3]=Rotation.from_euler('xyz',[20,35,-15],degrees=True).as_matrix()
    transformed.apply_transform(matrix)
    transformed.apply_translation([.4,-.3,.2])
    transformed.apply_scale(1.1)
    distorted=transformed.copy()
    distorted.apply_scale([1.35,.77,1.0])
    equivalence=six_seed_scores(ball,transformed,seed,n,reps)
    deformed=six_seed_scores(ball,distorted,seed+500,n,reps)
    return {'rigid_equivalent':equivalence,'truly_deformed':deformed,
            'deformed_excess_not_smaller_than_rigid':
            deformed['excess_over_floor']>=equivalence['excess_over_floor']}


def small_floor(ma,mb,seed,n=MAIN_N,reps=BOOT_REG_REPS):
    """Reduced-score bootstrap floor; diagnostic only, not same as main 6 draws."""
    cross=[];sa=[];sb=[]
    for j in range(reps):
        s=seed+j*59
        x=compare_meshes(ma,mb,seed=s,train=n,test=n)
        a=compare_meshes(ma,ma,seed=s+10000,train=n,test=n)
        b=compare_meshes(mb,mb,seed=s+20000,train=n,test=n)
        if not(x['valid'] and a['valid'] and b['valid']):
            return None
        cross.append(x['heldout_deformation'])
        sa.append(a['heldout_deformation'])
        sb.append(b['heldout_deformation'])
    floor=max(np.quantile(sa,.9),np.quantile(sb,.9))
    ang,_=quotient_axis_angle(ma,mb)
    return {'excess':float(max(0,np.median(cross)-floor)),
            'deformation':float(np.median(cross)),
            'axis_angle_deg':ang}


def bootstrap_temporal(x,seed,block,reps=BOOT_REPS):
    """Resample future halves ONLY; fitted anchor coordinates stay fixed."""
    a,b=split_historical(x)
    rng=np.random.default_rng(seed)
    data={'excess':[],'deformation':[],'axis_angle_deg':[]}
    invalid=0
    for j in range(reps):
        aa=circular_blocks(a,rng,block)
        bb=circular_blocks(b,rng,block)
        try:
            ma=shell(aa,seed+4000+2*j,GRID)
            mb=shell(bb,seed+4001+2*j,GRID)
            value=small_floor(ma,mb,seed+30000+j*500)
            if value is None:
                invalid+=1;continue
        except (ValueError,RuntimeError,np.linalg.LinAlgError):
            invalid+=1;continue
        for key in data:
            if value[key] is not None:data[key].append(value[key])
    return {'n_requested':reps,'n_rejected':invalid,
            'axis_identifiable':len(data['axis_angle_deg']),
            'q10_q50_q90':{
                k:([float(v) for v in np.quantile(items,[.1,.5,.9])]
                    if len(items)>=max(6,reps//2) else None)
                for k,items in data.items()},
            'warning':'Refit bootstrap describes sensitivity, not true-state CI'}


def one_window(x,seed,detail=False,block=15):
    ma,mb=shape_meshes(x,seed,GRID)
    baseline=six_seed_scores(ma,mb,seed+100)
    ang,meta=quotient_axis_angle(ma,mb)
    result={'main_360':baseline,
            'axis_angle_deg':ang,'axis_identifiable':meta['axis_identifiable'],
            'spectral_gaps':[meta['gap_a'],meta['gap_b']]}
    if detail:
        result['by_point_count']={
            str(n):(baseline if n==MAIN_N else
                    six_seed_scores(ma,mb,seed+150+n,n=n))
            for n in DENSITIES}
        result['refined_49'] = six_seed_scores(
            *shape_meshes(x,seed,GRID_REFINE),seed=seed+100,
            n=MAIN_N)
        result['temporal_bootstrap']=bootstrap_temporal(
            x,seed+70000,block)
    return result


def summarise(rows):
    basic=[r['measurement']['main_360'] for r in rows]
    audits=[r['measurement'] for r in rows if 'by_point_count' in r['measurement']]
    return {'n_windows':len(rows),
            'n_detected_above_floor':sum(r['exceeds_sampling_floor'] for r in basic),
            'median_observed_chamfer':float(np.median([
                r['observed_median'] for r in basic])),
            'median_local_floor':float(np.median([
                r['floor_max_self_q90'] for r in basic])),
            'median_floor_excess':float(np.median([
                r['excess_over_floor'] for r in basic])),
            'audit_windows':len(audits),
            'grid_35_to_49_abs_delta_excess_median':
                float(np.median([
                    abs(r['main_360']['excess_over_floor']-
                        r['refined_49']['excess_over_floor'])
                    for r in audits])) if audits else None,
            'point_counts':{
                str(n):{'median_self_floor':float(np.median([
                    r['by_point_count'][str(n)]['floor_max_self_q90']
                    for r in audits]))} for n in DENSITIES
                } if audits else {}}


def synthetic():
    controls={}
    for n in DENSITIES:
        controls[str(n)]=known_shape_controls(seed=SEED+n,n=n,reps=N_REPS)
    # Within each mesh, sampling floor should tend to decrease with density.
    floors=[controls[str(n)]['rigid_equivalent']['floor_max_self_q90']
            for n in DENSITIES]
    if not floors[-1]<floors[0]:
        raise AssertionError('Sampling floor did not decrease for known sphere')
    return {'status':'M10_CALIBRATION','point_counts':list(DENSITIES),
            'synthetic':controls,'floor_decreased_180_to_720':True}


def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('Missing exploration klines')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    coords=flow_coordinates(df)[['z','iota','nu']].to_numpy(float)
    w=WINDOW[interval];step=STEP[interval]
    t=df.timestamp.to_numpy(np.int64)
    candidates=[end for end in range(w,len(coords)+1,w)
                if np.isfinite(coords[end-w:end]).all() and
                np.all(np.diff(t[end-w:end])==step)]
    if not candidates:raise RuntimeError('No complete windows')
    picked=np.linspace(0,len(candidates)-1,min(N_WINDOWS,len(candidates)),dtype=int)
    chosen_details={0,len(picked)//2,len(picked)-1}
    rows=[];failures=[]
    for j,k in enumerate(picked):
        end=candidates[int(k)]
        try:
            m=one_window(coords[end-w:end],SEED+end,
                         detail=j in chosen_details,block=BLOCK[interval])
            rows.append({'end_ms':int(t[end-1]+step),
                         'window_end_index':int(end),'measurement':m})
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
            failures.append({'end_index':int(end),'reason':str(e)})
    if not rows:raise RuntimeError('All real windows invalid')
    file=ROOT/'reports'/f'SGV_M10_{interval}_floors.csv'
    file.parent.mkdir(parents=True,exist_ok=True)
    with file.open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=[
            'end_ms','n_points','cross_median','null_floor',
            'excess','exceeds_floor','detail','bootstrap_rejected'])
        writer.writeheader()
        for r in rows:
            o=r['measurement']
            for n,s in (o.get('by_point_count') or {'360':o['main_360']}).items():
                writer.writerow({
                    'end_ms':r['end_ms'],'n_points':n,
                    'cross_median':s['observed_median'],
                    'null_floor':s['floor_max_self_q90'],
                    'excess':s['excess_over_floor'],
                    'exceeds_floor':s['exceeds_sampling_floor'],
                    'detail':'by_point_count' in o,
                    'bootstrap_rejected':o.get('temporal_bootstrap',{}).get('n_rejected')})
    return {'status':'M10_EXPLORATORY','timeframe':interval,
            'n_eligible':len(candidates),'n_selected':len(picked),
            'n_valid':len(rows),'failed':failures,
            'summary':summarise(rows),
            'audit':[
                {'end_ms':r['end_ms'],**r['measurement']}
                for r in rows if 'by_point_count' in r['measurement']],
            'confirmatory_used':False,
            'limitations':['Floor conditional on mesh and sampled points',
                           'Six seeds do not calibrate a false positive rate',
                           'Block refits are not confidence intervals',
                           'No SF1/M5/M6 ranking and no stress/causal claim']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--interval',required=True,choices=('synthetic','1m','1h'))
    a=p.parse_args()
    report=synthetic() if a.interval=='synthetic' else real(a.interval)
    file=ROOT/'reports'/f'SGV_M10_{a.interval}.json'
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':main()
