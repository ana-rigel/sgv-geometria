"""M29 exploratory diagnostic (declared, EVEN origins' observed windows only):
is the volume->volume dependence at ~30 min a CLOCK (minute-of-hour periodicity)
or smooth persistence? No model involved.
  acf(l)      : autocorrelation of in-window rank normal scores of nu, l=1..65
  hs(l)       : 1-D HSIC nu_t -> nu_t+l, l in 25..35 and 55..65
  moh         : mean nu score by minute-of-hour (pooled over even windows)
"""
import sys,json,numpy as np,pandas as pd;from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiments.m16_trio_btc_exploratorio import load
from experiments.m12_nulos_regimes_temporais import PREFIX
from experiments.m5_validacao_conjunta_sf1 import WINDOW
from experiments.m21b_dependencia_btc import copula,hsic
from sgvgeo.flow import flow_coordinates
df,st=load('1m');pre=PREFIX['1m'];w=WINDOW['1m']
ACF=[];HS={};MOH=np.zeros(60);CNT=np.zeros(60)
for k in range(0,84,2):
    i=st[k];prefix=df.iloc[i-pre:i];fut=df.iloc[i:i+w]
    x=flow_coordinates(pd.concat([prefix,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-w:]
    u=copula(x)[:,2];u=(u-u.mean())/u.std()
    ACF.append([float(np.mean(u[:-l]*u[l:])) for l in range(1,66)])
    for l in (*range(25,36),*range(55,66)):HS.setdefault(l,[]).append(hsic(u[:-l,None],u[l:,None]))
    m=(pd.to_datetime(fut.timestamp.to_numpy(),unit='ms').minute).to_numpy()
    np.add.at(MOH,m,u);np.add.at(CNT,m,1)
A=np.array(ACF);acf=A.mean(0);moh=MOH/CNT
print('n windows',len(A))
print('ACF (mean over windows):')
for l in (1,2,5,10,14,15,16,20,29,30,31,45,59,60,61):print(f'  lag {l:2d}: {acf[l-1]:+.4f}  (frac windows where acf(l) > mean of l±1: {np.mean(A[:,l-1]>(A[:,l-2]+A[:,l])/2) if 1<l<65 else float("nan"):.2f})')
print('HSIC nu->nu median:')
for l in sorted(HS):print(f'  lag {l}: {np.median(HS[l]):.5f}')
print('minute-of-hour mean nu score (top/bottom):')
o=np.argsort(moh);print('  low ',[(int(m),round(float(moh[m]),3)) for m in o[:6]]);print('  high',[(int(m),round(float(moh[m]),3)) for m in o[-8:][::-1]])
print('  sd of minute means',round(float(moh.std()),3),' approx SE of one mean',round(float(1/np.sqrt(CNT.mean())),3))
Path('reports/m29diag').mkdir(parents=True,exist_ok=True)
Path('reports/m29diag/relogio_volume_pares.json').write_text(json.dumps({'acf_mean':acf.tolist(),'acf_all':A.tolist(),'hsic_median':{l:float(np.median(v)) for l,v in HS.items()},'moh_mean':moh.tolist(),'moh_count':CNT.tolist()},indent=1))
