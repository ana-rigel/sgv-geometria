"""A forma tem direcao? (exploratorio, 1m mai-jul/2026, ja usado; NAO e teste confirmatorio)
Janelas de 6 h SEM sobreposicao. Em cada janela (copula local):
  A  = dominancia dos lobulos = media de s=(z+iota)/sqrt2 entre os 40% de minutos de maior volume
       (>0: lobulo comprador mais pesado; <0: vendedor)
  cintura, cone como em forma_movimento.py
Alvo: retorno logaritmico do preco nos 15/60/240 min APOS o fim da janela.
Medidas: Spearman(A, retorno futuro); acerto do sinal; o mesmo so nas janelas com cintura forte e cone aberto."""
import sys,json,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scipy.stats import rankdata,norm,spearmanr,binomtest
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
W=360;P0=2*norm.cdf(.3)-1
df=load_binance_klines(sorted((ROOT/'data').glob('BTCUSDT-1m-*.zip')),with_flow=True)
F=flow_coordinates(df)[['z','iota','nu']].to_numpy(float);ok=np.isfinite(F).all(1);idx=np.flatnonzero(ok)
logp=np.log(df.close.to_numpy(float))
def cop(x):return norm.ppf(np.column_stack([rankdata(x[:,j])/(len(x)+1) for j in range(3)]))
rows=[]
for s in range(0,len(idx)-W-240,W):
    rr=idx[s:s+W]
    if rr[-1]-rr[0]!=W-1:continue
    u=cop(F[rr]);z,i,v=u.T;hv=v>=np.quantile(v,.6);sd=(z+i)/np.sqrt(2)
    A=float(sd[hv].mean());ss=(sd[hv]-sd[hv].mean())/sd[hv].std();cint=float(np.mean(np.abs(ss)<.3)/P0)
    lo=v<=np.quantile(v,1/3);hi=v>=np.quantile(v,2/3);cone=float(z[hi].std()/z[lo].std())
    e=rr[-1];fw={h:float(logp[e+h]-logp[e]) for h in (15,60,240)}
    rows.append(dict(A=A,cintura=cint,cone=cone,**{f'r{h}':fw[h] for h in fw}))
import pandas as pd;d=pd.DataFrame(rows)
mov=json.loads((ROOT/'reports'/'forma'/'movimento_forma.json').read_text())
cut_c=mov['cintura']['p10_p90_nulo'][0];cut_k=mov['cone']['p10_p90_nulo'][1]
cond=(d.cintura<cut_c)&(d.cone>cut_k)
out={'n_janelas':len(d),'n_cintura_e_cone':int(cond.sum())}
for h in (15,60,240):
    r=d[f'r{h}'];rho,p=spearmanr(d.A,r);hit=int(np.sum(np.sign(d.A)==np.sign(r)))
    rc=r[cond];Ac=d.A[cond];hitc=int(np.sum(np.sign(Ac)==np.sign(rc)))
    out[f'{h}min']={'spearman':round(float(rho),3),'p':round(float(p),3),'acerto_sinal':round(hit/len(d),3),'p_acerto':round(binomtest(hit,len(d),.5).pvalue,3),
                    'cond_spearman':round(float(spearmanr(Ac,rc)[0]),3) if cond.sum()>5 else None,'cond_acerto':round(hitc/max(1,cond.sum()),3),
                    'cond_p_acerto':round(binomtest(hitc,int(cond.sum()),.5).pvalue,3) if cond.sum() else None}
print(json.dumps(out,indent=1,ensure_ascii=False))
(ROOT/'reports'/'forma'/'dominancia_direcao.json').write_text(json.dumps(out,indent=1,ensure_ascii=False))
