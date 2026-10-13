"""M34 conditional geometric dynamics: B0/B0+/B-GEO, causal market block scoring.

ENGINEERING/EXPLORATORY ONLY. Uses M11-I GMM2 HDR50 instrument through
sgv_m11i.instrument compatibility API. No future features / no reserved data.
"""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import skew
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED=20261013
N_NODES=20
GEO_WINDOW=1050
BLOCK_STEP=1500
HORIZON=240
C_FIXED=.1
COLUMN_NAMES=('timestamp','open','high','low','close','volume','close_time',
              'quote_volume','trades','taker_buy','taker_buy_quote','ignore')
BTC_MONTHS=('05','06','07')

def past_features(X,nodes,timestamps):
    X=np.asarray(X,float);nodes=np.asarray(nodes,int)
    if len(X)!=len(nodes) or len(X)!=len(timestamps):raise ValueError('length mismatch')
    if not np.isfinite(X).all():raise ValueError('nonfinite')
    one=np.eye(N_NODES)[nodes]
    delta=np.vstack([np.zeros((1,3)),np.diff(X,axis=0)])
    z=pd.Series(X[:,0]);nu=pd.Series(X[:,2])
    absz=z.abs().rolling(60,min_periods=1).mean().to_numpy()
    nmean=nu.rolling(60,min_periods=1).mean().to_numpy()
    zstd=z.rolling(60,min_periods=2).std().fillna(0).to_numpy()
    rmean=z.rolling(60,min_periods=1).mean().to_numpy()
    utc=pd.to_datetime(timestamps,unit='ms',utc=True)
    minutes=utc.hour.to_numpy()*60+utc.minute.to_numpy()
    weekday=utc.dayofweek.to_numpy()
    cyc=np.column_stack([np.sin(2*np.pi*minutes/1440),np.cos(2*np.pi*minutes/1440),
                         np.sin(2*np.pi*weekday/7),np.cos(2*np.pi*weekday/7)])
    lag=np.vstack([X[0],X[:-1]])
    return np.column_stack((one,X,delta,absz,nmean,zstd,rmean,cyc,lag))

def conventional_signature(A,B):
    A=np.asarray(A,float);B=np.asarray(B,float)
    m=B.mean(axis=0)-A.mean(axis=0)
    ratio=np.log((B.var(axis=0)+1e-6)/(A.var(axis=0)+1e-6))
    cv=(np.cov(B,rowvar=False)-np.cov(A,rowvar=False))[np.triu_indices(3)]
    asym=np.nan_to_num(skew(B,axis=0,bias=False)-skew(A,axis=0,bias=False))
    return np.concatenate((m,ratio,cv,asym))

def geometry_signature(A,B,seed=SEED,grid=35):
    from sgv_m11i.instrument import build_shell,signature
    shA=build_shell(A,seed=seed,n=grid)
    shB=build_shell(B,seed=seed+1,n=grid)
    return signature(shA,shB,seed+2)

def geometry_vector(s):
    ang=s.get('theta_deg')
    x=list(s['delta_center'])+[s['delta_log_volume'],
        0. if ang is None else ang/180.,s.get('distance_512'),
        s.get('delta_D'),float(ang is None)]
    if any(z is None or not np.isfinite(z) for z in x):
        raise ValueError('invalid non-orientation geometric component')
    return np.asarray(x,float)

def fit_and_score(episodes,train_frac=.6,valid_frac=.2):
    if len(episodes)<5:raise ValueError('at least five episodes')
    n=len(episodes);ntr=int(n*train_frac);nva=int(n*valid_frac)
    if min(ntr,nva,n-ntr-nva)<1:raise ValueError('bad split')
    groups={'train':episodes[:ntr],
            'validation':episodes[ntr:ntr+nva],
            'test':episodes[ntr+nva:]}
    makers={
        'B0':lambda e:e['X_base'],
        'B0plus':lambda e:np.column_stack((e['X_base'],
          np.broadcast_to(e['conventional'],(len(e['y']),len(e['conventional']))))),
        'B_GEO':lambda e:np.column_stack((e['X_base'],
          np.broadcast_to(e['conventional'],(len(e['y']),len(e['conventional']))),
          np.broadcast_to(e['geometry'],(len(e['y']),len(e['geometry'])))))
    }
    scored={};means={}
    for name,maker in makers.items():
        Xtr=np.concatenate([maker(e) for e in groups['train']])
        ytr=np.concatenate([e['y'] for e in groups['train']])
        model=Pipeline([('scaler',StandardScaler()),
          ('model',LogisticRegression(C=C_FIXED,max_iter=350,tol=1e-4))])
        model.fit(Xtr,ytr)
        bysplit={}
        for split in ('train','validation','test'):
            rows=[]
            for ep in groups[split]:
                proba=model.predict_proba(maker(ep))
                classes={int(c):i for i,c in enumerate(model.named_steps['model'].classes_)}
                probs=np.array([proba[i,classes[int(y)]] if int(y) in classes else 1e-12
                    for i,y in enumerate(ep['y'])])
                rows.append({'episode':int(ep['episode']),'n':int(len(ep['y'])),
                             'log_loss':float(-np.mean(np.log(np.maximum(probs,1e-12))))})
            bysplit[split]=rows
        scored[name]=bysplit
        means[name]={sp:float(np.average([x['log_loss'] for x in rows],
                  weights=[x['n'] for x in rows])) for sp,rows in bysplit.items()}
    a=means
    return {'n_episodes':n,'splits':{k:[int(e['episode']) for e in v] for k,v in groups.items()},
            'losses':means,'per_episode':scored,'fixed_C':C_FIXED,
            'test_is_confirmatory':False,'test_differences_nats':{
              'B0_minus_B_GEO':a['B0']['test']-a['B_GEO']['test'],
              'B0plus_minus_B_GEO':a['B0plus']['test']-a['B_GEO']['test'],
              'B0_minus_B0plus':a['B0']['test']-a['B0plus']['test']}}

def load_approved_btc(folder):
    folder=Path(folder);digest={}
    for line in (folder/'SHA256SUMS').read_text().splitlines():
        if line.strip():
            sha,name=line.strip().split(maxsplit=1)
            digest[name.lstrip('*')]=sha
    parts=[]
    for month in BTC_MONTHS:
        filename=f'BTCUSDT-1m-2026-{month}.zip'
        if filename not in digest:raise ValueError('missing sha '+filename)
        binary=(folder/filename).read_bytes()
        if hashlib.sha256(binary).hexdigest()!=digest[filename]:
            raise ValueError('checksum mismatch '+filename)
        with zipfile.ZipFile(folder/filename) as z:
            inner=next(n for n in z.namelist() if n.endswith('.csv'))
            f=pd.read_csv(z.open(inner),header=None,names=COLUMN_NAMES,
                          usecols=['timestamp','close','volume','taker_buy'])
        f['timestamp']=pd.to_numeric(f.timestamp).astype('int64')
        if f.timestamp.iloc[0]>10**14:f.timestamp//=1000
        parts.append(f)
    data=pd.concat(parts,ignore_index=True)
    ts=data.timestamp.to_numpy('int64')
    if not np.all(np.diff(ts)==60000):raise ValueError('gaps or duplicated minutes')
    if ts[0]<1777593600000 or ts[-1]>=1785542400000:
        raise ValueError('unapproved months')
    return data

def make_real_episodes(raw,timestamps,n_episodes=24,grid=35,horizon=HORIZON):
    from sgv_m11i.instrument import gaussianize
    raw=np.asarray(raw,float);timestamps=np.asarray(timestamps,np.int64)
    june=int(pd.Timestamp('2026-06-01',tz='UTC').timestamp()*1000)
    valid=np.isfinite(raw).all(axis=1);may=(timestamps<june)&valid
    anchor=raw[may]
    if len(anchor)<1500:raise ValueError('short May calibration')
    X=np.full_like(raw,np.nan);X[valid]=gaussianize(anchor,raw[valid])
    mu=X[may].mean(0);sd=X[may].std(0);sd[sd==0]=1
    km=KMeans(n_clusters=N_NODES,random_state=SEED,n_init=10)
    km.fit((X[may]-mu)/sd)
    cent=km.cluster_centers_;safe=X.copy();safe[~valid]=0
    dist=np.sum((((safe-mu)/sd)[:,None,:]-cent[None,:,:])**2,axis=2)
    nodes=np.argmin(dist,axis=1)
    base=past_features(safe,nodes,timestamps)
    first=np.flatnonzero(timestamps>=june)[0]
    episodes=[];fails=[]
    for j in range(n_episodes):
        t=first+j*BLOCK_STEP;start=t-GEO_WINDOW+1
        if start<0 or t+horizon>=len(X):break
        if not valid[start:t+horizon+1].all():
            fails.append({'episode':j,'reason':'nonfinite'});continue
        points=X[start:t+1];A=points[:GEO_WINDOW//2];B=points[GEO_WINDOW//2:]
        conventional=conventional_signature(A,B)
        try:
            s=geometry_signature(A,B,seed=SEED+3*j,grid=grid)
            G=geometry_vector(s)
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as ex:
            fails.append({'episode':j,'reason':str(ex)});continue
        episodes.append({'episode':j,'X_base':base[t:t+horizon],
          'conventional':conventional,'geometry':G,'y':nodes[t+1:t+horizon+1],
          'timestamp':int(timestamps[t]),'geometry_details':s})
    return episodes,fails

def run_btc(folder,n_episodes=24,grid=35):
    from sgv_m11i.instrument import flow_coordinates
    f=load_approved_btc(folder)
    eps,fails=make_real_episodes(flow_coordinates(f),f.timestamp.to_numpy(),n_episodes,grid)
    if len(eps)<5:raise ValueError('too few valid episodes: '+str(fails))
    result=fit_and_score(eps)
    result.update({'source':'May–July 2026 BTC explorative checksum-verified',
       'n_requested':n_episodes,'n_valid':len(eps),'invalid':fails,
       'grid':grid,'n_test_blocks':len(result['splits']['test']),
       'frame':'May calibrated frozen normal scores',
       'geometry_backend':'repository M11-I historical integration'})
    return result

def json_ready(obj):
    if isinstance(obj,dict):return {k:json_ready(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):return [json_ready(v) for v in obj]
    if isinstance(obj,np.ndarray):return obj.tolist()
    if isinstance(obj,(np.integer,np.floating)):return obj.item()
    return obj
