"""Regularizacao separada (B0 com ridge 100; grupo novo com ridge R). So placebos e sinal plantado,
BTC mai-jul ja gasto; nenhuma variavel real de G ou E entra aqui."""
import sys,json,math,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from experiments import m31g1_engenharia as g
from experiments import m32_casca as m32
from experiments.m31g0_features_causais import qlike_deviance
from sgvgeo.data import load_binance_klines
def rolling(d,base,group,rb,rg,train=1344):
    cols=tuple(base)+tuple(group);X=d[list(cols)].to_numpy(float);rv=d.rv_future_15.to_numpy(float)
    good=np.isfinite(rv)&(rv>0);y=np.where(good,np.log(np.where(good,rv,1.)),np.nan)
    ts=d.origin_ts.to_numpy(np.int64);mat=d.label_matures_ts.to_numpy(np.int64);gi=np.flatnonzero(good);gm=mat[gi];out=np.full(len(d),np.nan)
    pen=np.diag([0.]+[rb]*len(base)+[rg]*len(group))
    for k in range(len(d)):
        j=np.searchsorted(gm,ts[k],side='right')
        if j<train:continue
        sl=gi[j-train:j];Xt=X[sl];mu=Xt.mean(0);sd=Xt.std(0);sd=np.where(sd>1e-10,sd,1.)
        Z=np.column_stack([np.ones(train),(Xt-mu)/sd]);beta=np.linalg.solve(Z.T@Z+pen,Z.T@y[sl]);res=y[sl]-Z@beta
        out[k]=float(np.exp(np.clip(np.r_[1.,(X[k]-mu)/sd]@beta,-30,15))*np.mean(np.exp(np.clip(res,-30,15))))
    return out
d,_=g.build(load_binance_klines(g.EXPLO,with_flow=True));rv=d.rv_future_15.to_numpy(float)
v0=m32.rolling_forecasts(d,g.B0);ok=np.isfinite(v0);dev0=qlike_deviance(v0[ok],rv[ok]);m0=dev0.mean()
e=np.where(ok,np.log(rv)-np.log(np.where(ok,v0,1.)),0.);e/=e[ok].std();phi=.5**(1/24);res={}
def ar(seed,k):
    r=np.random.default_rng(seed).standard_normal((len(d),k));P=np.empty_like(r);P[0]=r[0]
    for t in range(1,len(d)):P[t]=phi*P[t-1]+math.sqrt(1-phi*phi)*r[t]
    return P
names=tuple(f'g{j}' for j in range(10))
for R in (100.,1000.,3000.,10000.):
    pens=[];sk=[]
    for s in range(3):
        P=ar(700+s,10);dd=d.copy()
        for j,nm in enumerate(names):dd[nm]=P[:,j]
        v=rolling(dd,g.B0,names,100.,R);pens.append(float((qlike_deviance(v[ok],rv[ok])-dev0).mean()/m0))
        dd['g0']=.09*e+P[:,0]          # 1 variavel informativa entre 10
        v=rolling(dd,g.B0,names,100.,R);sk.append(float(-(qlike_deviance(v[ok],rv[ok])-dev0).mean()/m0))
    res[str(R)]={'penalidade_10_placebos_pct':100*float(np.mean(pens)),'skill_com_1_sinal_plantado_pct':100*float(np.mean(sk))}
    print('ridge do grupo',R,res[str(R)],flush=True)
(ROOT/'reports'/'m34'/'ridge_grupo.json').write_text(json.dumps(res,indent=1))
