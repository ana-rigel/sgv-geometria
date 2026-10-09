#!/usr/bin/env python3
"""SGV-M11 — deterministic triangle-surface distance, block-time diagnostics."""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments.precisao_formas_3d import split_historical
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m9_registro_simetrico_3d import shell,normalized_mesh_points,initial_rotations,icp_fit
from experiments.m5_validacao_conjunta_sf1 import WINDOW,STEP
SEED=20261009
N_WINDOWS=6
QUADS=(256,512)
GRID=35
REPS=12
BLOCK={'1m':15,'1h':12}

def normalize_mesh(mesh):
    m=mesh.copy();m.fix_normals()
    if not m.is_watertight:raise ValueError('Open mesh')
    vol=abs(float(m.volume))
    if vol<1e-12 or not np.isfinite(vol):raise ValueError('Degenerate volume')
    radius=(3*vol/(4*np.pi))**(1/3)
    m.apply_translation(-np.asarray(m.center_mass,float))
    m.apply_scale(1/radius)
    return m

def area_quadrature(mesh,n):
    triangles=np.asarray(mesh.triangles,float)
    weights=np.asarray(mesh.area_faces,float)
    if not np.isfinite(weights).all() or weights.sum()<=0:
        raise ValueError('Invalid areas')
    goals=(np.arange(n)+.5)*weights.sum()/n
    idx=np.searchsorted(np.cumsum(weights),goals)
    return triangles[idx].mean(axis=1)

class NearestTriangle:
    """Exact closest-face query with provably conservative centroid-radius bound."""
    def __init__(self,mesh):
        self.faces=np.asarray(mesh.triangles,float)
        self.centres=self.faces.mean(axis=1)
        self.radii=np.linalg.norm(
            self.faces-self.centres[:,None,:],axis=2).max(axis=1)
        self.global_radius=float(self.radii.max())
        self.tree=cKDTree(self.centres)

    def distances(self,points):
        ans=[]
        for p in np.asarray(points,float):
            _,j=self.tree.query(p)
            cp=trimesh.triangles.closest_point(
                self.faces[int(j)][None],p[None])[0]
            upper=float(np.linalg.norm(cp-p))
            indexes=np.asarray(self.tree.query_ball_point(
                p,upper+self.global_radius+1e-10),dtype=int)
            if len(indexes):
                bound=np.linalg.norm(self.centres[indexes]-p,axis=1)-self.radii[indexes]
                indexes=indexes[bound<=upper+1e-10]
            if len(indexes):
                closest=trimesh.triangles.closest_point(
                    self.faces[indexes],np.broadcast_to(p,(len(indexes),3)))
                upper=min(upper,float(np.linalg.norm(closest-p,axis=1).min()))
            ans.append(upper)
        return np.asarray(ans)

def direct_distance(a,b,n):
    A=area_quadrature(a,n);B=area_quadrature(b,n)
    ab=float(NearestTriangle(b).distances(A).mean())
    ba=float(NearestTriangle(a).distances(B).mean())
    return {'symmetric':(ab+ba)/2,'a_to_b':ab,'b_to_a':ba}

def measure_meshes(a,b,seed):
    a=normalize_mesh(a);b=normalize_mesh(b)
    sample_a=normalized_mesh_points(a,360,seed)
    sample_b=normalized_mesh_points(b,360,seed+1)
    rotation,_=icp_fit(sample_a,sample_b,initial_rotations(a,b))
    T=np.eye(4);T[:3,:3]=rotation.T
    b.apply_transform(T)
    q={str(n):direct_distance(a,b,n) for n in QUADS}
    return {'valid':True,'distance_256':q['256']['symmetric'],
            'distance_512':q['512']['symmetric'],
            'directed_ab':q['512']['a_to_b'],
            'directed_ba':q['512']['b_to_a'],
            'relative_256_512_gap':abs(
              q['256']['symmetric']-q['512']['symmetric'])/
              max(.01,q['512']['symmetric'])}

def measure_samples(a,b,seed,n=GRID):
    try:
        return measure_meshes(shell(a,seed,n),shell(b,seed+1,n),seed+2)
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
        return {'valid':False,'reason':str(e)}

def pooled_null(a,b,seed,block,reps=REPS):
    rng=np.random.default_rng(seed)
    pooled=np.vstack((a,b));v=[]
    for j in range(reps):
        x=circular_blocks(pooled,rng,block)[:len(a)]
        y=circular_blocks(pooled,rng,block)[:len(b)]
        out=measure_samples(x,y,seed+100+3*j)
        if out['valid']:v.append(out['distance_512'])
    return {'n_requested':reps,'n_valid':len(v),
            'quantiles':([float(z) for z in np.quantile(v,[.1,.5,.9])]
               if len(v)>=reps//2 else None),
            'caution':'Pooled null assumes stationary halves; not a calibrated market null'}

def refit(a,b,seed,block,reps=REPS):
    rng=np.random.default_rng(seed);v=[]
    for j in range(reps):
        x=circular_blocks(a,rng,block)
        y=circular_blocks(b,rng,block)
        m=measure_samples(x,y,seed+300+3*j)
        if m['valid']:v.append(m['distance_512'])
    return {'n_requested':reps,'n_valid':len(v),
            'quantiles':([float(z) for z in np.quantile(v,[.1,.5,.9])]
              if len(v)>=reps//2 else None)}

def synthetic():
    from experiments.isosuperficies_morfometria import analytic_field,extract_mesh
    f,t,dx=analytic_field('sphere',61)
    sphere,tr=extract_mesh(f,t,dx)
    if tr:raise ValueError('Sphere truncated')
    a=normalize_mesh(sphere)
    identical=direct_distance(a,a,256)
    if identical['symmetric']>1e-8:
        raise AssertionError('Same triangle mesh distance must be zero')
    b=sphere.copy();b.apply_translation([.25,-.3,.2]);b.apply_scale(1.1)
    equivalent=measure_meshes(sphere,b,seed=SEED)
    distorted=b.copy();distorted.apply_scale([1.4,.72,1.])
    changed=measure_meshes(sphere,distorted,seed=SEED)
    if changed['distance_512']<=equivalent['distance_512']+.005:
        raise AssertionError('Deformation does not exceed rigid control')
    return {'status':'M11_SYNTHETIC','identical_mesh':identical,
            'equivalent':equivalent,'deformed':changed}

def real(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('Only exploratory archives permitted')
    for path in paths:checked_exploratory_month(path.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    xyz=flow_coordinates(df)[['z','iota','nu']].to_numpy(float)
    t=df.timestamp.to_numpy(np.int64);w=WINDOW[interval];step=STEP[interval]
    elig=[end for end in range(w,len(xyz)+1,w) if
          np.isfinite(xyz[end-w:end]).all() and
          np.all(np.diff(t[end-w:end])==step)]
    if not elig:raise RuntimeError('No valid contiguous windows')
    ids=np.linspace(0,len(elig)-1,min(N_WINDOWS,len(elig)),dtype=int)
    audit={0,len(ids)-1}
    rows=[];failures=[]
    for j,k in enumerate(ids):
        end=elig[int(k)]
        a,b=split_historical(xyz[end-w:end])
        out=measure_samples(a,b,SEED+end)
        if not out['valid']:
            failures.append({'end_index':end,'reason':out['reason']});continue
        result={'end_ms':int(t[end-1]+step),'observed':out}
        if j in audit:
            result['grid49']=measure_samples(a,b,SEED+end,n=49)
            result['pooled_null']=pooled_null(a,b,SEED+end+10000,BLOCK[interval])
            result['separate_refit']=refit(a,b,SEED+end+20000,BLOCK[interval])
            q=result['pooled_null']['quantiles']
            result['above_simplified_null_q90']=(out['distance_512']>q[2]
                                                 if q else None)
        rows.append(result)
    if not rows:raise RuntimeError('No successful meshes')
    audit_rows=[r for r in rows if 'pooled_null' in r]
    summary={'n_valid':len(rows),
      'median_distance_256':float(np.median([r['observed']['distance_256'] for r in rows])),
      'median_distance_512':float(np.median([r['observed']['distance_512'] for r in rows])),
      'median_relative_gap':float(np.median([r['observed']['relative_256_512_gap'] for r in rows])),
      'n_null_audits':len(audit_rows),
      'n_above_simplified_null_q90':sum(r['above_simplified_null_q90'] is True for r in audit_rows),
      'n_refit_valid':sum(r['separate_refit']['n_valid'] for r in audit_rows)}
    file=ROOT/'reports'/f'SGV_M11_{interval}_distances.csv'
    file.parent.mkdir(parents=True,exist_ok=True)
    with file.open('w',newline='',encoding='utf8') as f:
        cw=csv.DictWriter(f,fieldnames=['end_ms','distance_256','distance_512',
                      'relative_gap','null_q90','above_null_q90'])
        cw.writeheader()
        for row in rows:
            q=row.get('pooled_null',{}).get('quantiles')
            cw.writerow({'end_ms':row['end_ms'],
              'distance_256':row['observed']['distance_256'],
              'distance_512':row['observed']['distance_512'],
              'relative_gap':row['observed']['relative_256_512_gap'],
              'null_q90':q[2] if q else None,
              'above_null_q90':row.get('above_simplified_null_q90')})
    return {'status':'M11_EXPLORATORY','interval':interval,
        'n_eligible':len(elig),'n_selected':len(ids),'n_valid':len(rows),
        'failures':failures,'summary':summary,'audits':audit_rows,
        'confirmatory_read':False,
        'limits':['Finite deterministic quadrature, closest triangle exact per point',
                  'Pooled null not regime-preserving or calibrated',
                  'No claimed market stress or trading signal']}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--interval',required=True,choices=('synthetic','1m','1h'))
    a=p.parse_args()
    result=synthetic() if a.interval=='synthetic' else real(a.interval)
    f=ROOT/'reports'/f'SGV_M11_{a.interval}.json'
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
