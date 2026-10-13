"""Poder do M32 por GANHO PLANTADO (engenharia, BTC mai-jul ja gasto; nenhuma variavel real da casca usada).
Variavel plantada f_t = kappa * e_t/sd(e) + ruido AR(1) unitario, com e_t = erro de previsao do B1 em t
(carrega informacao do alvo por construcao). kappa=0 mede o tamanho do teste.
Criterio do M32: p<0,05 com HAC de 1 dia E de 1 semana, e skill >= 0,5%."""
import sys,json,math,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scipy.stats import norm
from experiments import m31g1_engenharia as g
from experiments import m32_casca as m
from experiments.m31g0_features_causais import qlike_deviance
from sgvgeo.data import load_binance_klines
d,_=g.build(load_binance_klines(g.EXPLO,with_flow=True));rv=d.rv_future_15.to_numpy(float)
v1=m.rolling_forecasts(d,m.B1);ok=np.isfinite(v1)
e=np.where(ok,np.log(rv)-np.log(np.where(ok,v1,1.)),0.);e=e/e[ok].std()
dev1=qlike_deviance(v1[ok],rv[ok]);phi=.51**(1/24);res=[]
for kappa in (0.,.04,.06,.08,.12):
    for rep in range(10):
        rng=np.random.default_rng(100*rep+7);eps=rng.standard_normal(len(d));eta=np.empty(len(d));eta[0]=eps[0]
        for k in range(1,len(d)):eta[k]=phi*eta[k-1]+math.sqrt(1-phi*phi)*eps[k]
        dd=d.copy();dd['planted']=kappa*e+eta
        v2=m.rolling_forecasts(dd,m.B1+('planted',));mk=ok&np.isfinite(v2)
        dif=qlike_deviance(v2[mk],rv[mk])-qlike_deviance(v1[mk],rv[mk]);m0=qlike_deviance(v1[mk],rv[mk]).mean()
        p1=float(norm.cdf(dif.mean()/g.hac_se(dif,96)));pw=float(norm.cdf(dif.mean()/g.hac_se(dif,672)));sk=float(-dif.mean()/m0)
        res.append({'kappa':kappa,'rep':rep,'skill':sk,'p_hac_1d':p1,'p_hac_1sem':pw,'passa':bool(p1<.05 and pw<.05 and sk>=.005)})
    r=[x for x in res if x['kappa']==kappa]
    print({'kappa':kappa,'skill_medio':round(float(np.mean([x['skill'] for x in r]))*100,3),'taxa_passa':float(np.mean([x['passa'] for x in r])),
           'taxa_p1d':float(np.mean([x['p_hac_1d']<.05 for x in r])),'taxa_p1sem':float(np.mean([x['p_hac_1sem']<.05 for x in r]))},flush=True)
Path(ROOT/'reports'/'m32').mkdir(parents=True,exist_ok=True)
(ROOT/'reports'/'m32'/'poder_plantado.json').write_text(json.dumps(res,indent=1))
