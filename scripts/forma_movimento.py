"""A forma se desfaz e se remonta? (exploratorio, sem modelo)
Janelas moveis de 6 h (360 min, passo 60) no 1m mai-jul/2026; em cada janela, copula local (postos -> normal)
e duas medidas de forma:
  cintura = massa central da diagonal compra/venda (|z+i| padronizado < 0,3) entre os 40% de minutos de maior volume,
            relativa a normal (1 = eliptico; <1 = cintura; >1 = pico)
  cone    = dp(z) no terco de volume alto / dp(z) no terco baixo
Nulo: as mesmas medidas em janelas montadas com minutos SORTEADOS do periodo inteiro (mesma forma media,
sem ordem no tempo). Se a forma realmente se desfaz e se remonta, a variacao entre janelas reais supera a do nulo
e a serie de forma tem persistencia (autocorrelacao) entre janelas."""
import sys,json,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scipy.stats import rankdata,norm
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
W,STEP=360,60;P0=2*norm.cdf(.3)-1
def cop(x):return norm.ppf(np.column_stack([rankdata(x[:,j])/(len(x)+1) for j in range(3)]))
def shape(x):
    u=cop(x);z,i,v=u.T;hv=v>=np.quantile(v,.6);s=z[hv]+i[hv];s=(s-s.mean())/s.std()
    lo=v<=np.quantile(v,1/3);hi=v>=np.quantile(v,2/3)
    return np.mean(np.abs(s)<.3)/P0, z[hi].std()/z[lo].std()
df=load_binance_klines(sorted((ROOT/'data').glob('BTCUSDT-1m-*.zip')),with_flow=True)
X=flow_coordinates(df)[['z','iota','nu']].to_numpy(float);X=X[np.isfinite(X).all(1)]
obs=np.array([shape(X[s:s+W]) for s in range(0,len(X)-W,STEP)])
rng=np.random.default_rng(11);Xs=X[rng.permutation(len(X))]   # mesma serie, ordem no tempo destruida; mesmas janelas moveis (mesma sobreposicao)
nul=np.array([shape(Xs[s:s+W]) for s in range(0,len(Xs)-W,STEP)])
def ac(a,l):a=a-a.mean();return float(a[:-l]@a[l:]/(a@a))
res={}
for j,name in enumerate(('cintura','cone')):
    o,n=obs[:,j],nul[:,j]
    res[name]={'n_janelas':len(o),'mediana_real':float(np.median(o)),'mediana_nulo':float(np.median(n)),
               'dp_real':float(o.std()),'dp_nulo':float(n.std()),'razao_dp':float(o.std()/n.std()),
               'p10_p90_real':np.round(np.quantile(o,[.1,.9]),2).tolist(),'p10_p90_nulo':np.round(np.quantile(n,[.1,.9]),2).tolist(),
               'autocorr_1h':ac(o,1),'autocorr_6h':ac(o,6),'autocorr_24h':ac(o,24),'autocorr_nulo_1h':ac(n,1),'autocorr_nulo_6h':ac(n,6),'autocorr_nulo_24h':ac(n,24)}
    print(name,json.dumps(res[name],ensure_ascii=False))
c=obs[:,0];thr=np.quantile(nul[:,0],[.05,.95])
res['cintura']['frac_real_com_cintura_forte']=float(np.mean(c<thr[0]));res['cintura']['frac_real_com_pico_forte']=float(np.mean(c>thr[1]))
runs=[];cur=0
for f in (c<thr[0]):
    if f:cur+=1
    elif cur:runs.append(cur);cur=0
res['cintura']['duracao_media_episodios_cintura_h']=float(np.mean(runs)) if runs else None
runs=[];cur=0
for f in (nul[:,0]<thr[0]):
    if f:cur+=1
    elif cur:runs.append(cur);cur=0
res['cintura']['duracao_media_episodios_nulo_h']=float(np.mean(runs)) if runs else None
res['cintura']['frac_nulo_com_cintura_forte']=float(np.mean(nul[:,0]<thr[0]))
print('nulo: duração média dos episódios',res['cintura']['duracao_media_episodios_nulo_h'],'fração',res['cintura']['frac_nulo_com_cintura_forte']);print('cintura forte (abaixo do p5 do nulo):',round(res['cintura']['frac_real_com_cintura_forte'],3),'| pico forte (acima do p95):',round(res['cintura']['frac_real_com_pico_forte'],3),'| duração média dos episódios (h, passo 1h):',res['cintura']['duracao_media_episodios_cintura_h'])
np.save(ROOT/'reports'/'forma'/'movimento_series.npy',obs)
(ROOT/'reports'/'forma'/'movimento_forma.json').write_text(json.dumps(res,indent=1,ensure_ascii=False))
