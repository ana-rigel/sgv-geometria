import sys,numpy as np,pandas as pd;from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiments.m25_vol_multiescala as m
from experiments.m16_trio_btc_exploratorio import load
from experiments.m12_nulos_regimes_temporais import PREFIX
from experiments.m21b_dependencia_btc import copula
from sgvgeo.flow import flow_coordinates
names=['z','i','v']
def ent(x,l):
    u=np.abs(copula(x));a=u[:-l]-u[:-l].mean(0);b=u[l:]-u[l:].mean(0);return (a.T@b/len(a))   # 3x3: row=time t, col=time t+l
df,st=load('1m');pre=PREFIX['1m']
ext={1:np.zeros((3,3))};n=0
for k in range(2,84,8):
    i=st[k];prefix=df.iloc[i-pre:i];fut=df.iloc[i:i+1500]
    obs=flow_coordinates(pd.concat([prefix,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-1500:]
    try:s,_=m.build(prefix.copy(),k)
    except Exception as e:continue
    refs=[s['HARLMFV'](np.random.default_rng(100*k+j),1500) for j in range(39)];n+=1
    for l in (1,):
        o=ent(obs,l);R=np.array([ent(r,l) for r in refs])
        ext[l]+=((R>=o).sum(0)<=1)*1.0-((R<=o).sum(0)<=1)*1.0   # +1 obs above all, -1 below all
for l,E in ext.items():
    print(f'lag {l}: fraction of origins where entry is outside refs (two-sided, nominal ~10%) [row=t, col=t+lag]')
    print(pd.DataFrame(E/n,index=['|'+a+'|_t' for a in names],columns=['|'+a+'|_t+l' for a in names]).round(2).to_string())
print('origins',n)
