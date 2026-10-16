"""SGV AMB01: ambiental vs interno, controle fatorial com treino congelado.

Protocolo: reports/AMB01_PROTOCOLO_20261015.md
ESTE SCRIPT NUNCA LÊ OUTUBRO OU NOVEMBRO. Teste sintético é aberto uma vez,
após a publicação dos modelos em resultados/amb01_modelos_congelados.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import lfilter
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from pipeline import sgv_d01_direcao as D01

ROOT=Path(__file__).resolve().parents[1]
KINDS=('N','E','I','EI')
TRAIN_IDS=tuple(range(0,8))
VAL_IDS=tuple(range(8,12))
TEST_IDS=tuple(range(12,20))
N=5000
BURN=500
SYN_START=950
ENV_LAGS=(1,5,15,30,60,120)
INNER_LAGS=(5,10,20,40,60)
ARMS={'A0':16,'AE':28,'AI':21,'AEI':33}
C=0.2
BOOT_N=2000
BOOT_SEED=202610157

def rng_for(path_id,role):
    seed=int.from_bytes(hashlib.sha256(f'AMB01|20261015|{path_id}|{role}'.encode()).digest()[:8],'big')
    return np.random.default_rng(seed)

def ar_path(rng,rho,var,total):
    z=rng.normal(size=total+BURN)*np.sqrt(var*(1-rho*rho))
    init=rng.normal(scale=np.sqrt(var))
    return (lfilter([1.],[1.,-rho],z)+init*rho**np.arange(1,len(z)+1))[BURN:]

def sigmoid(v):
    v=np.asarray(v,float)
    return 1/(1+np.exp(-np.clip(v,-40,40)))

def synthetic_path(path_id:int):
    if path_id not in range(20): raise ValueError('unknown ID')
    rg=rng_for(path_id,'common-vol')
    slow=ar_path(rg,.999,.3,N)
    fast=ar_path(rg,.9,.2,N)
    mag=np.abs(rg.standard_normal(N))
    sigma=.0007*np.exp(.5*(slow+fast-.5))
    result={}
    for kind in KINDS:
        rng=rng_for(path_id,'environment-'+kind)
        # AR environmental channel or white environmental baseline.
        Z=(ar_path(rng,.985,1,N) if kind in ('E','EI') else rng.standard_normal(N))
        env_obs=np.column_stack([Z+2*rng.standard_normal(N),np.tanh((Z+2*rng.standard_normal(N))/2)])
        sign_rng=rng_for(path_id,'sign-'+kind)
        uniform=sign_rng.random(N)
        s=np.zeros(N,float)
        s[0]=1. if uniform[0]<.5 else -1.
        for k in range(1,N):
            if kind=='N':
                p=.5
            elif kind=='E':
                p=float(sigmoid(1.8*Z[k-1]))
            elif kind=='I':
                p=.5 if k<21 else (.82 if s[k-21]>0 else .18)
            else:
                p=float(sigmoid(1.8*Z[k-1]+(1.5*s[k-21] if k>=21 else 0.)))
            s[k]=1. if uniform[k]<p else -1.
        returns=sigma*mag*s
        result[kind]={'r':returns,'env':env_obs,'coords':D01.synthetic_coords(returns),
                      'sign':s}
    first=result['N']['r']**2
    if any(not np.array_equal(first,result[k]['r']**2) for k in KINDS):
        raise RuntimeError('Squared returns differ between paired synthetic conditions')
    return result

def feature_matrix(r,coords,env,start=0,stop=None):
    """Feature A0, AE, AI, AEI produced from the exact same aligned rows.

    Only present/past coordinates/environment/returns at index t; label r[t+1].
    """
    r=np.asarray(r,float)
    env=np.asarray(env,float)
    if env.shape!=(len(r),2):
        raise ValueError('ambient features shape unexpected')
    t,x,y=D01.feature_matrix(r,coords,start=max(121,start),stop=stop)
    # D01: cols [0:11] = short-return and vol; [11:14] = SGV; [14:19] = internal long
    # A0: first 14 + current environment two; AE: + 12 environmental lags
    # AI: A0 + 5 internal long; AEI: both.
    core=np.column_stack([x[:,:14],env[t,:]])
    history=np.column_stack([env[t-lag,j] for lag in ENV_LAGS for j in (0,1)])
    long_sign=x[:,14:]
    out=np.column_stack([core,history,long_sign])
    if out.shape[1]!=33:
        raise RuntimeError(f'unexpected AMB01 feature count {out.shape}')
    good=np.isfinite(out).all(axis=1)
    return t[good],out[good],y[good]

def arm_matrix(X,arm):
    if arm=='A0':return X[:,:16]
    if arm=='AE':return X[:,:28]
    if arm=='AI':return np.column_stack([X[:,:16],X[:,28:]])
    if arm=='AEI':return X
    raise ValueError(f'unknown arm {arm}')

def fit_model(X,y):
    scaler=StandardScaler()
    Xt=scaler.fit_transform(X)
    clf=LogisticRegression(C=C,solver='lbfgs',max_iter=1500)
    clf.fit(Xt,y)
    if not np.array_equal(clf.classes_,[0,1]):raise RuntimeError('one class')
    return {'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist(),
            'coef':clf.coef_[0].tolist(),'bias':float(clf.intercept_[0]),'C':C}

def predict(model,X):
    means=np.asarray(model['mean']); stds=np.asarray(model['scale'])
    z=((X-means)/stds)@np.asarray(model['coef'])+model['bias']
    y=np.empty(len(z));pos=z>=0
    y[pos]=1/(1+np.exp(-z[pos]))
    ez=np.exp(z[~pos]); y[~pos]=ez/(1+ez)
    return np.clip(y,1e-14,1-1e-14)

def losses(y,p):
    return -(y*np.log(p)+(1-y)*np.log1p(-p))

def data_for_ids(ids):
    out={kind:[] for kind in KINDS}
    for i in ids:
        p=synthetic_path(i)
        for kind in KINDS:
            q=p[kind]
            t,x,y=feature_matrix(q['r'],q['coords'],q['env'],start=SYN_START)
            out[kind].append((i,x,y))
    return out

def train_synthetic():
    samples=data_for_ids(TRAIN_IDS)
    models={}
    for k,rows in samples.items():
        X=np.concatenate([r[1] for r in rows]);y=np.concatenate([r[2] for r in rows])
        models[k]={arm:fit_model(arm_matrix(X,arm),y) for arm in ARMS}
    return models

def diffs(losses_):
    ll=losses_
    return {
        'D_E':float(np.mean(ll['A0']-ll['AE'])),
        'D_I':float(np.mean(ll['A0']-ll['AI'])),
        'D_I_given_E':float(np.mean(ll['AE']-ll['AEI'])),
        'D_E_given_I':float(np.mean(ll['AI']-ll['AEI']))}

def evaluate_synthetic_samples(ids,models):
    paths=data_for_ids(ids)
    result={}
    for k,rows in paths.items():
        per=[]
        for path_id,X,y in rows:
            ll={arm:losses(y,predict(models[k][arm],arm_matrix(X,arm))) for arm in ARMS}
            per.append({'id':path_id,'n':len(y),'logloss':{a:float(x.mean()) for a,x in ll.items()},
                        'diff':diffs(ll)})
        result[k]=per
    return result

def boot_by_units(rows,key,weights=False):
    vals=np.array([r['diff'][key] for r in rows],float)
    w=np.array([r['n'] for r in rows],float) if weights else np.ones(len(rows))
    rg=np.random.default_rng(BOOT_SEED)
    ind=rg.integers(0,len(rows),size=(BOOT_N,len(rows)))
    means=np.sum(vals[ind]*w[ind],axis=1)/np.sum(w[ind],axis=1)
    ci=np.quantile(means,[.025,.975])
    return {'mean':float(np.average(vals,weights=w)),'ci95':ci.tolist()}

def summarize_synthetic(eval_,holdout=False):
    result={}
    for kind,rows in eval_.items():
        result[kind]={'n_paths':len(rows),'loss':{a:float(np.mean([r['logloss'][a] for r in rows])) for a in ARMS},
                      'metrics':{key:boot_by_units(rows,key) for key in ('D_E','D_I','D_I_given_E','D_E_given_I')},
                      'paths':rows}
    if holdout:
        n=result['N']['metrics'];e=result['E']['metrics'];i=result['I']['metrics']
        gates={
            'ambient_positive_E':bool(e['D_E']['mean']>=.005 and e['D_E']['ci95'][0]>0),
            'internal_positive_I':bool(i['D_I_given_E']['mean']>=.04 and i['D_I_given_E']['ci95'][0]>0),
            'specificity_N':bool(abs(n['D_E']['mean'])<=.005 and abs(n['D_I_given_E']['mean'])<=.005),
            'ambient_specificity_I':bool(abs(i['D_E']['mean'])<=.005),
            'paired_energy_exact':True
        }
        result['gates']=gates
        result['status']='PASS_SYNTHETIC_AMB01' if all(gates.values()) else 'FAIL_SYNTHETIC_AMB01'
    return result

def market_data(months,dados):
    # Source of official SGV 3D as in D01, plus volume and aggressive flow.
    import explora_geometria_residual as GR
    df=GR.E.carregar(months,Path(dados))
    ts=pd.to_datetime(df.timestamp,unit='ms',utc=True)
    if ts.iloc[-1]>=pd.Timestamp('2026-10-01',tz='UTC'):
        raise RuntimeError('Oct/Nov market input forbidden')
    raw=GR.E.coords_orig(df)
    may=(ts < pd.Timestamp('2026-06-01',tz='UTC')).to_numpy()
    xyz=GR.regua(raw,may)
    r=np.diff(np.log(df.close.to_numpy(float)),prepend=np.nan)
    vol=df.volume.to_numpy(float)
    buy=df.taker_buy.to_numpy(float)
    if np.any(vol<0) or np.any(buy<0) or np.any(buy>vol+1e-4):
        raise ValueError('invalid volume/taker buy')
    env=np.column_stack((np.log1p(vol),2*buy/np.maximum(vol,1e-12)-1))
    if not np.isfinite(env).all():raise ValueError('environment NaNs')
    t,X,y=feature_matrix(r,xyz,env)
    return ts,t,X,y

def market_train(dados):
    ts,t,X,y=market_data(['2026-05','2026-06','2026-07'],dados)
    labeltime=ts.iloc[t+1]
    selection=((labeltime>=pd.Timestamp('2026-06-01',tz='UTC')) &
               (labeltime<pd.Timestamp('2026-08-01',tz='UTC'))).to_numpy()
    xx=X[selection];yy=y[selection]
    if len(yy)<30000:raise ValueError('missing training')
    digest=hashlib.sha256(np.ascontiguousarray(np.column_stack((xx,yy))).tobytes()).hexdigest()
    models={a:fit_model(arm_matrix(xx,a),yy) for a in ARMS}
    return {'models':models,'n':int(len(yy)),
            'positive_share':float(np.mean(yy)),'train_sha256':digest}

def save(path,doc):
    f=Path(path);f.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(doc,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
    f.write_bytes(data)
    return hashlib.sha256(data).hexdigest()

def train(dados,freeze):
    sm=train_synthetic()
    val=evaluate_synthetic_samples(VAL_IDS,sm)
    mm=market_train(dados)
    frozen={'kind':'AMB01_freeze_v1','synthetic_train_ids':list(TRAIN_IDS),
            'synthetic_validation_ids':list(VAL_IDS),
            'synthetic_sealed_ids':list(TEST_IDS),
            'models_synthetic':sm,'validation_descriptive':summarize_synthetic(val),
            'market_train':mm,'market_training_months':['2026-06','2026-07'],
            'market_evaluation_months':['2026-08','2026-09'],
            'features':{'core':16,'amb_history':12,'internal_history':5},
            'config':{'C':C,'env_lags':list(ENV_LAGS),'internal_lags':list(INNER_LAGS),'bootstrap':BOOT_N},
            'November_touched':False}
    digest=save(freeze,frozen)
    print(json.dumps({'stage':'TRAIN_FREEZE','sha256':digest,'market_train_n':mm['n'],
       'validation':{kind:{key:v for key,v in dat.items() if key!='paths'} for kind,dat in frozen['validation_descriptive'].items()}},ensure_ascii=False),flush=True)

def load_freeze(path,expected):
    f=Path(path)
    digest=hashlib.sha256(f.read_bytes()).hexdigest()
    if not expected or digest!=expected:raise ValueError('freeze SHA256 mismatch')
    d=json.loads(f.read_text())
    if d['synthetic_train_ids']!=list(TRAIN_IDS) or d['synthetic_sealed_ids']!=list(TEST_IDS):
        raise ValueError('wrong synthetic split')
    if d['config']!={'C':C,'env_lags':list(ENV_LAGS),'internal_lags':list(INNER_LAGS),'bootstrap':BOOT_N}:
        raise ValueError('changed settings')
    return d,digest

def synthetic_final(frozen,digest,out):
    if Path(out).exists(): raise RuntimeError('heldout consumed')
    evaluation=evaluate_synthetic_samples(TEST_IDS,frozen['models_synthetic'])
    summ=summarize_synthetic(evaluation,True)
    result={'status':summ['status'],'models_sha256':digest,'test_opened_once':True,
            'synthetics':summ,'market_data_used':False}
    save(out,result)
    print(json.dumps({'stage':'SYNTHETIC_FINAL','status':summ['status'],'gates':summ['gates'],
       'effects':{k:{m:x['mean'] for m,x in v['metrics'].items()} for k,v in summ.items() if k in KINDS}},
       ensure_ascii=False),flush=True)
    return summ['status']=='PASS_SYNTHETIC_AMB01'

def market_final(dados,frozen,digest,out):
    if Path(out).exists():raise RuntimeError('market previously evaluated')
    ts,t,X,y=market_data(['2026-05','2026-06','2026-07','2026-08','2026-09'],dados)
    lt=ts.iloc[t+1]
    training=((lt>=pd.Timestamp('2026-06-01',tz='UTC')) &
              (lt<pd.Timestamp('2026-08-01',tz='UTC'))).to_numpy()
    xx=X[training];yy=y[training]
    hd=hashlib.sha256(np.ascontiguousarray(np.column_stack((xx,yy))).tobytes()).hexdigest()
    if hd!=frozen['market_train']['train_sha256'] or len(yy)!=frozen['market_train']['n']:
        raise RuntimeError('Training prefix not identical after extension; stop.')
    te=((lt>=pd.Timestamp('2026-08-01',tz='UTC')) &
        (lt<pd.Timestamp('2026-10-01',tz='UTC'))).to_numpy()
    Xt=X[te];yt=y[te];times=lt[te]
    if len(yt)<40000:raise RuntimeError('too few holdout observations')
    pred={a:predict(frozen['market_train']['models'][a],arm_matrix(Xt,a)) for a in ARMS}
    lv={a:losses(yt,pred[a]) for a in ARMS}
    weekly=((times-pd.Timestamp('2026-08-01',tz='UTC')).dt.total_seconds()//(7*86400)).astype(int).to_numpy()
    per=[]
    for week in np.unique(weekly):
        mask=weekly==week
        if mask.sum()<1440: continue
        los={a:lv[a][mask] for a in ARMS}
        per.append({'week':int(week),'n':int(mask.sum()),'first_time_utc':str(times.iloc[np.flatnonzero(mask)[0]]),
                    'logloss':{a:float(v.mean()) for a,v in los.items()},
                    'accuracy':{a:float(np.mean((pred[a][mask]>=.5)==yt[mask])) for a in ARMS},
                    'diff':diffs(los)})
    if not per:raise RuntimeError('no weeks')
    result={'status':'BTC_AGO_SET_EXPLORATORY_SPENT','market_months':['2026-08','2026-09'],
            'market_test_n':len(yt),'market_train_hash_verified':hd,
            'zero_ret_fraction':float(1-len(yt)/np.sum(te)),
            'positive_share':float(yt.mean()),'n_weeks':len(per),
            'metrics':{k:boot_by_units(per,k,True) for k in ('D_E','D_I','D_I_given_E','D_E_given_I')},
            'loss':{a:float(lv[a].mean()) for a in ARMS},
            'accuracy':{a:float(np.mean((pred[a]>=.5)==yt)) for a in ARMS},
            'weekly':per,'model_sha256':digest,
            'november_touched':False,'october_touched':False}
    save(out,result)
    print(json.dumps({'stage':'MARKET_FINAL','status':result['status'],
         'n':result['market_test_n'],'metrics':result['metrics']},ensure_ascii=False),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage',choices=('train','synthetic','market'),required=True)
    ap.add_argument('--dados',default=str(ROOT/'dados'))
    ap.add_argument('--freeze',required=True)
    ap.add_argument('--freeze-sha',default='')
    ap.add_argument('--out',required=True)
    arg=ap.parse_args()
    if arg.stage=='train':return train(arg.dados,arg.freeze)
    model,dig=load_freeze(arg.freeze,arg.freeze_sha)
    if arg.stage=='synthetic':
        if not synthetic_final(model,dig,arg.out):raise SystemExit(2)
    else:market_final(arg.dados,model,dig,arg.out)

if __name__=='__main__':main()
