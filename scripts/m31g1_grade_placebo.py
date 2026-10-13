"""Escolha de treino/regularizacao SO com B0 e placebos (sem informacao da hipotese).
Criterios: menor deviança media do B0 e menor penalidade dos placebos."""
import sys,json,math,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from experiments import m31g1_engenharia as m
from experiments.m31g0_features_causais import qlike_deviance
from sgvgeo.data import load_binance_klines
d,_=m.build(load_binance_klines(m.EXPLO,with_flow=True));rv=d.rv_future_15.to_numpy(float)
phi=.51**(1/24);res=[]
def placebos(seed):
    rng=np.random.default_rng(1000+seed);e=rng.standard_normal((len(d),3));p=np.empty_like(e);p[0]=e[0]
    for k in range(1,len(d)):p[k]=phi*p[k-1]+math.sqrt(1-phi*phi)*e[k]
    return p
P=[placebos(s) for s in range(5)]
for train in (672,1344,2016):
    for ridge in (1.,10.,100.):
        m.RIDGE=ridge;start=2016   # mesma amostra avaliada em todas as configuracoes
        v0=m.rolling_forecasts(d,m.B0,train=train);ok=np.isfinite(v0);ok[:start]=False
        dev0=qlike_deviance(v0[ok],rv[ok]);pen=[]
        for p in P:
            dd=d.copy();dd['pa'],dd['pb'],dd['pc']=p.T
            v1=m.rolling_forecasts(dd,m.B0+('pa','pb','pc'),train=train)
            pen.append(float((qlike_deviance(v1[ok],rv[ok])-dev0).mean()/dev0.mean()))
        r={'train':train,'ridge':ridge,'n':int(ok.sum()),'dev_B0':round(float(dev0.mean()),5),'penalidade_placebo_pct':round(100*float(np.mean(pen)),3)}
        res.append(r);print(r,flush=True)
Path(ROOT/'reports'/'m31g1').mkdir(parents=True,exist_ok=True)
(ROOT/'reports'/'m31g1'/'grade_placebo.json').write_text(json.dumps(res,indent=1))
