#!/usr/bin/env python3
"""SGV-M19a (exploratory, descriptive): are the M18 long-block (BL) alarms on the
1m exploratory origins just volatility shocks? Reads only committed M18 shards
and exploratory klines; no confirmatory month is touched."""
import sys,json,glob,numpy as np,pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scipy.stats import spearmanr,mannwhitneyu,fisher_exact
from experiments.m16_trio_btc_exploratorio import load
from experiments.m12_nulos_regimes_temporais import PREFIX
from experiments.m5_validacao_conjunta_sf1 import WINDOW
rows=[]
for f in glob.glob(str(ROOT/'reports/m18/shards/shard_1m_*.json')): rows+=json.load(open(f))['origins']
rows=sorted(rows,key=lambda r:r['origin'])
df,starts=load('1m');pre=PREFIX['1m'];w=WINDOW['1m']
lr=np.log(df.close.to_numpy(float))
out=[]
for r in rows:
    i=starts[r['origin']]
    rp=np.diff(lr[i-pre:i]);rw=np.diff(lr[i-1:i+w])
    volr=rw.std()/rp.std()
    h=np.diff(lr[i:i+w:60]); hp=np.diff(lr[i-pre:i:60])
    maxh=np.max(np.abs(h))/hp.std()
    vol_v=np.log(df.volume.to_numpy(float)[i:i+w].mean()/df.volume.to_numpy(float)[i-pre:i].mean())
    trend=abs(lr[i+w-1]-lr[i])/rp.std()/np.sqrt(w)
    m=r['models']['BL']; al={s:(m[s]['alarm'] if m[s].get('valid') else None) for s in ('m11','fr_cov','energy')}
    n_al=sum(1 for v in al.values() if v); 
    out.append(dict(origin=r['origin'],volr=volr,maxh=maxh,volume=vol_v,trend=trend,n_alarm=n_al,**{f'a_{k}':v for k,v in al.items()},
                    pit_e=m['energy'].get('p_rank'),pit_f=m['fr_cov'].get('p_rank')))
d=pd.DataFrame(out)
print('base rates: any',(d.n_alarm>=1).mean().round(3),' >=2',(d.n_alarm>=2).mean().round(3),' all3',(d.n_alarm>=3).mean().round(3))
for c in ('volr','maxh','volume','trend'):
    rho,p=spearmanr(d[c],d.n_alarm); print(f'{c:7s} spearman vs n_alarm rho={rho:+.2f} p={p:.3f} | vs energy PIT rho={spearmanr(d[c],d.pit_e)[0]:+.2f} | vs FR PIT rho={spearmanr(d[c],d.pit_f)[0]:+.2f}')
q=d.volr.quantile([.33,.67]).values
d['vt']=np.digitize(d.volr,q)
res=d.groupby('vt').agg(n=('origin','size'),volr=('volr','median'),any_alarm=('n_alarm',lambda x:(x>=1).mean()),ge2=('n_alarm',lambda x:(x>=2).mean())).round(2)
print(res)
d.to_csv(ROOT/'reports/m19/SGV_M19a_alarmes_BL_vs_volatilidade.csv',index=False)
