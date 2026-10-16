"""SGV D01 — memory of market return direction beyond 3D and volatility.

PRE-REGISTERED at reports/D01_PROTOCOLO_PRE_REGISTRO_20261015.md;
time-index erratum reports/D01_ERRATA_INDEXACAO_PRECODIGO_20261015.md.
No Oct/Nov. Synthetic tests use independent path IDs, not financial holdouts.
Three arms: B0 short returns+vol; B1=B0+SGV 3D; B2=B1+long sign lags.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import lfilter
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'pipeline'))
SYN_N=7000
SYN_BURN=500
SYN_ANCHOR=800
SYN_START=950
TRAIN_IDS=tuple(range(12))
VAL_IDS=tuple(range(12,16))
TEST_IDS=tuple(range(16,24))
LONG_LAGS=(5,10,20,40,60)
FEATURE_NAMES=(
    'sign0','sign1','sign2','sign3',
    'stdret0','stdret1','stdret2','stdret3',
    'log_ew10','log_ew60','log_ew240',
    'E_norm','jerk','memory_flux',
    'sign5','sign10','sign20','sign40','sign60'
)
ARMS={'B0':11,'B1':14,'B2':19}
BOOT_SEED=202610156
BOOT_N=2000

def rng_for(path_id:int,role:str):
    h=hashlib.sha256(f'D01|20261015|{path_id}|{role}'.encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8],'big'))

def ar_path(rng,rho,var,n):
    z=rng.standard_normal(n+SYN_BURN)*np.sqrt(var*(1-rho*rho))
    initial=rng.normal(scale=np.sqrt(var))
    h=lfilter([1],[1,-rho],z)
    h+=(rho**np.arange(1,len(h)+1))*initial
    return h[SYN_BURN:]

def synthetic_pair(i:int):
    if i not in range(24):
        raise ValueError('invalid synthetic path ID')
    rg=rng_for(i,'vol-and-magnitude')
    hs=ar_path(rg,.999,.3,SYN_N)
    hf=ar_path(rg,.90,.2,SYN_N)
    sigma=.0007*np.exp(.5*(hs+hf-.5))
    a=np.abs(rg.standard_normal(SYN_N))
    null=np.where(rng_for(i,'null-sign').random(SYN_N)<.5,-1.,1.)
    r2=rng_for(i,'direction-sign')
    directed=np.empty(SYN_N,float)
    directed[:21]=np.where(r2.random(21)<.5,-1.,1.)
    same=r2.random(SYN_N-21)<.82
    for k in range(21,SYN_N):
        directed[k]=directed[k-21] if same[k-21] else -directed[k-21]
    rn=sigma*a*null
    rd=sigma*a*directed
    if not np.array_equal(rn**2,rd**2):
        raise RuntimeError('paired magnitudes not exactly equal')
    return {'vol':sigma,'h_slow':hs,'h_fast':hf,'null':rn,'direction':rd}

def synthetic_coords(r):
    close=np.exp(np.cumsum(r))
    m=pd.Series(close).ewm(alpha=.05,adjust=False).mean().to_numpy()
    raw=(close-m)/np.abs(m)
    anch=raw[:SYN_ANCHOR]
    med=np.median(anch); scale=np.quantile(np.abs(anch-med),.995)/3
    if scale<=1e-12: raise ValueError('bad synthetic E_norm')
    en=(raw-med)/scale
    ret=np.r_[0.,np.expm1(r[1:])]
    jerk=np.r_[np.nan,np.nan,ret[2:]-2*ret[1:-1]+ret[:-2]]
    flux=np.r_[np.nan,np.diff(pd.Series(en).ewm(alpha=.05,adjust=False).mean().to_numpy())]
    return np.column_stack([en,jerk,flux])

def feature_matrix(r,coords,start=0,stop=None):
    """At t all features measurable at or before t; outcome sign(r[t+1])."""
    r=np.asarray(r,float)
    coords=np.asarray(coords,float)
    if len(r)!=len(coords):
        raise ValueError('r/coords misaligned')
    ew={}
    for window in (10,60,240):
        ew[window]=np.sqrt(pd.Series(r*r).ewm(alpha=2/(window+1),adjust=False).mean().to_numpy())
    t=np.arange(max(61,start),len(r)-1 if stop is None else min(len(r)-1,stop))
    signs=np.sign(r)
    parts=[signs[t-k] for k in range(4)]
    parts += [r[t-k] / np.maximum(ew[10][t-k],1e-12) for k in range(4)]
    parts += [np.log(np.maximum(ew[k][t],1e-12)) for k in (10,60,240)]
    parts += [coords[t,i] for i in range(3)]
    parts += [signs[t-k] for k in LONG_LAGS]
    X=np.column_stack(parts)
    y=np.where(r[t+1]>0,1,np.where(r[t+1]<0,0,-1))
    ok=np.isfinite(X).all(1)&(y>=0)
    return t[ok],X[ok],y[ok]

def fit(x,y):
    ss=StandardScaler()
    z=ss.fit_transform(x)
    lr=LogisticRegression(C=.1,max_iter=500,solver='lbfgs')
    lr.fit(z,y)
    if not np.array_equal(lr.classes_,[0,1]):
        raise ValueError('invalid label support')
    return {'mean':ss.mean_.tolist(),'scale':ss.scale_.tolist(),
            'coefs':lr.coef_[0].tolist(),'intercept':float(lr.intercept_[0])}

def predict(fitobj,x):
    x=(x-np.asarray(fitobj['mean']))/np.asarray(fitobj['scale'])
    z=x@np.asarray(fitobj['coefs'])+fitobj['intercept']
    p=np.empty(len(z))
    pos=z>=0
    p[pos]=1/(1+np.exp(-z[pos]))
    v=np.exp(z[~pos]);p[~pos]=v/(1+v)
    return np.clip(p,1e-14,1-1e-14)

def loss_values(y,p):
    return -(y*np.log(p)+(1-y)*np.log1p(-p))

def all_synthetic(ids):
    out={'null':[],'direction':[]}
    for i in ids:
        pair=synthetic_pair(i)
        for k in ('null','direction'):
            r=pair[k];coords=synthetic_coords(r)
            _,x,y=feature_matrix(r,coords,start=SYN_START)
            out[k].append((i,x,y))
    return out

def train_synthetic():
    samples=all_synthetic(TRAIN_IDS)
    fitted={}
    for kind,rows in samples.items():
        X=np.concatenate([row[1] for row in rows])
        y=np.concatenate([row[2] for row in rows])
        fitted[kind]={arm:fit(X[:,:nf],y) for arm,nf in ARMS.items()}
    return fitted

def audit_samples(samples,models):
    out={}
    for kind,rows in samples.items():
        path_metrics=[]
        for i,x,y in rows:
            vl={arm:predict(models[kind][arm],x[:,:nf]) for arm,nf in ARMS.items()}
            ll={arm:loss_values(y,p) for arm,p in vl.items()}
            path_metrics.append({'id':i,'n':len(y),
                'loss':{a:float(v.mean()) for a,v in ll.items()},
                'D_hist':float((ll['B1']-ll['B2']).mean()),
                'D_geom':float((ll['B0']-ll['B1']).mean())})
        out[kind]=path_metrics
    return out

def summarize_synthetic(out,heldout=False):
    ret={}
    for kind,arr in out.items():
        delta=np.asarray([z['D_hist'] for z in arr])
        rand=np.random.default_rng(BOOT_SEED)
        inds=rand.integers(0,len(arr),size=(BOOT_N,len(arr)))
        ci=np.quantile(delta[inds].mean(1),[.025,.975])
        ret[kind]={'n_paths':len(arr),'D_hist':float(delta.mean()),'D_geom':float(np.mean([z['D_geom'] for z in arr])),
                   'D_hist_ci95':ci.tolist(),'path_details':arr}
    if heldout:
        gates={'positive_detected':bool(ret['direction']['D_hist']>=.05 and ret['direction']['D_hist_ci95'][0]>0),
               'negative_specificity':bool(abs(ret['null']['D_hist'])<=.015),
               'paired_energy_identical':True}
        ret['gates']=gates
        ret['status']='PASS_SYNTHETIC_INSTRUMENT' if all(gates.values()) else 'FAIL_SYNTHETIC_INSTRUMENT'
    return ret

def read_market_data(months,data_dir):
    import explora_geometria_residual as GR
    df=GR.E.carregar(months,Path(data_dir))
    ts=pd.to_datetime(df.timestamp,unit='ms',utc=True)
    if ts.iloc[-1]>=pd.Timestamp('2026-10-01',tz='UTC'):
        raise RuntimeError('October, November or later are forbidden')
    raw=GR.E.coords_orig(df)
    may=(ts < pd.Timestamp('2026-06-01',tz='UTC')).to_numpy()
    coords=GR.regua(raw,may)
    r=np.diff(np.log(df.close.to_numpy(float)),prepend=np.nan)
    t,x,y=feature_matrix(r,coords)
    return df,ts,t,x,y

def market_training(data_dir):
    _,ts,t,x,y=read_market_data(['2026-05','2026-06','2026-07'],data_dir)
    yy=ts.iloc[t+1]
    mask=((yy>=pd.Timestamp('2026-06-01',tz='UTC'))&
          (yy<pd.Timestamp('2026-08-01',tz='UTC'))).to_numpy()
    xx=x[mask];ys=y[mask]
    if len(ys)<30000: raise ValueError('bad market training size')
    digest=hashlib.sha256(np.ascontiguousarray(
        np.column_stack([xx,ys])).tobytes()).hexdigest()
    models={a:fit(xx[:,:n],ys) for a,n in ARMS.items()}
    return {'models':models,'train_n':len(ys),'train_sha256':digest,
            'train_target_positive_share':float(ys.mean())}

def write_json(path,doc):
    dest=Path(path)
    dest.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(doc,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    dest.write_bytes(data)
    return hashlib.sha256(data).hexdigest()

def train(data_dir,out):
    synthetic_models=train_synthetic()
    development=audit_samples(all_synthetic(VAL_IDS),synthetic_models)
    mm=market_training(data_dir)
    frozen={'protocol':'SGV-D01-v1','synthetic_train':list(TRAIN_IDS),
            'synthetic_val':list(VAL_IDS),'synthetic_heldout':list(TEST_IDS),
            'synthetic_models':synthetic_models,
            'validation_descriptive':summarize_synthetic(development),
            'market':mm,'market_training_months':['2026-06','2026-07'],
            'only_training_may_anchor':True,'market_eval':['2026-08','2026-09'],
            'november_touched':False,'arm_features':dict(ARMS),'feature_names':list(FEATURE_NAMES)}
    digest=write_json(out,frozen)
    print(json.dumps({'stage':'TRAIN_FROZEN','sha256':digest,
        'market_n':mm['train_n'],
        'validation':{k:{s:v for s,v in val.items() if s!='path_details'}
                      for k,val in frozen['validation_descriptive'].items()}},ensure_ascii=False))

def load_frozen(path,expected):
    f=Path(path)
    digest=hashlib.sha256(f.read_bytes()).hexdigest()
    if not expected or digest!=expected: raise RuntimeError('sha256 of frozen models MUST match')
    doc=json.loads(f.read_text())
    if doc['synthetic_train']!=list(TRAIN_IDS) or doc['synthetic_heldout']!=list(TEST_IDS):
        raise RuntimeError('partitions differ')
    if doc['arm_features']!=ARMS or doc['feature_names']!=list(FEATURE_NAMES):
        raise RuntimeError('frozen design mismatch')
    return doc,digest

def test_synthetic(frozen,digest,out):
    if Path(out).exists(): raise RuntimeError('synthetic test already exists: sealed')
    # heldout paths are generated only here, after freeze
    result=summarize_synthetic(audit_samples(all_synthetic(TEST_IDS),frozen['synthetic_models']),True)
    data={'status':result['status'],'frozen_sha256':digest,'results':result,
          'energy_exact_by_construction':True,'market_data_read_here':False}
    write_json(out,data)
    print(json.dumps({'stage':'SYN_TEST','status':result['status'],
        'gates':result['gates'],'D_hist_null':result['null']['D_hist'],
        'D_hist_direction':result['direction']['D_hist'],
        'ci_direction':result['direction']['D_hist_ci95']}))
    return all(result['gates'].values())

def test_market(data_dir,frozen,digest,out):
    if Path(out).exists(): raise RuntimeError('market exploratory result already exists')
    _,ts,t,x,y=read_market_data(['2026-05','2026-06','2026-07','2026-08','2026-09'],data_dir)
    yy=ts.iloc[t+1]
    trainmask=((yy>=pd.Timestamp('2026-06-01',tz='UTC'))&
               (yy<pd.Timestamp('2026-08-01',tz='UTC'))).to_numpy()
    xx=x[trainmask];ys=y[trainmask]
    digest_train=hashlib.sha256(np.ascontiguousarray(
        np.column_stack([xx,ys])).tobytes()).hexdigest()
    if len(ys)!=frozen['market']['train_n'] or digest_train!=frozen['market']['train_sha256']:
        raise RuntimeError('training features mismatch after additional months: stop')
    start=pd.Timestamp('2026-08-01',tz='UTC')
    finish=pd.Timestamp('2026-10-01',tz='UTC')
    testmask=((yy>=start)&(yy<finish)).to_numpy()
    te=t[testmask];X=x[testmask];Y=y[testmask]
    if len(Y)<40000:raise RuntimeError('market evaluation unusually small')
    p={arm:predict(frozen['market']['models'][arm],X[:,:nf])
       for arm,nf in ARMS.items()}
    losses={arm:loss_values(Y,pr) for arm,pr in p.items()}
    pred_times=ts.iloc[te+1]
    weeks=((pred_times-start).dt.total_seconds()//(7*86400)).astype(int).to_numpy()
    details=[]
    for wk in sorted(set(weeks)):
        mask=weeks==wk
        if mask.sum()<1440:continue
        loss={a:float(losses[a][mask].mean()) for a in ARMS}
        details.append({'week':int(wk),'start':str(pred_times.iloc[np.where(mask)[0][0]]),
                        'n':int(mask.sum()),'loss':loss,
                        'D_geom':float((losses['B0'][mask]-losses['B1'][mask]).mean()),
                        'D_hist':float((losses['B1'][mask]-losses['B2'][mask]).mean()),
                        'accuracy':{a:float(np.mean((p[a][mask]>=.5)==Y[mask])) for a in ARMS}})
    if not details:raise RuntimeError('no evaluation weeks')
    weights=np.array([z['n'] for z in details],float)
    rng=np.random.default_rng(BOOT_SEED)
    ind=rng.integers(0,len(details),size=(BOOT_N,len(details)))
    stats={}
    for key in ('D_geom','D_hist'):
        values=np.array([z[key] for z in details],float)
        mean=float(np.average(values,weights=weights))
        boot=np.sum(values[ind]*weights[ind],axis=1)/np.sum(weights[ind],axis=1)
        stats[key]={'mean':mean,'ci95':np.quantile(boot,[.025,.975]).tolist(),
                    'positive_descriptive':bool(mean>0 and np.quantile(boot,.025)>0)}
    for arm in ARMS:
        stats['mean_logloss_'+arm]=float(losses[arm].mean())
        stats['accuracy_'+arm]=float(np.mean((p[arm]>=.5)==Y))
    ret={'status':'EXPLORATORY_ALREADY_EXAMINED_MONTHS',
         'frozen_sha256':digest,'train_revalidated_sha256':digest_train,
         'period':'2026-08-01..2026-09-30 UTC',
         'n_test':int(len(Y)),'n_weeks':len(details),'target_positive_share':float(Y.mean()),
         'results':stats,'weekly':details,'november_touched':False,'october_touched':False}
    write_json(out,ret)
    print(json.dumps({'stage':'MARKET_EXPLORATORY','status':ret['status'],'n':len(Y),
                      'weeks':len(details),'D_hist':stats['D_hist'],'D_geom':stats['D_geom'],
                      'loss':{a:stats['mean_logloss_'+a] for a in ARMS}},ensure_ascii=False))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage',choices=('train','synthetic','market'),required=True)
    ap.add_argument('--dados',default=str(ROOT/'dados'))
    ap.add_argument('--freeze',required=True)
    ap.add_argument('--freeze-sha',default='')
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    if a.stage=='train':
        train(a.dados,a.freeze);return
    frozen,digest=load_frozen(a.freeze,a.freeze_sha)
    if a.stage=='synthetic':
        if not test_synthetic(frozen,digest,a.out):sys.exit(2)
    else:test_market(a.dados,frozen,digest,a.out)

if __name__=='__main__':
    main()
