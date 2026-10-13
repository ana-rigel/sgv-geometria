"""Dicionario geometrico — dados (exploratorio, BTC 1m mai-jul/2026 ja gasto).
Para as mesmas origens amostradas do M34 (1 a cada 2 h): medidas geometricas (do M34),
momentos detalhados nas metades gaussianizadas A/B e observaveis BRUTOS de mercado nas mesmas metades,
mais o que acontece nas 6 h seguintes (so descritivo, para gerar hipoteses)."""
import sys,numpy as np,pandas as pd;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scipy.stats import kurtosis,rankdata,norm
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments import m31g1_engenharia as g
from experiments.precisao_formas_3d import split_historical
W=1500;NA=450;HALF=525;P0=2*norm.cdf(.3)-1
G=pd.read_csv(ROOT/'reports'/'m34'/'amostra_features.csv')
f=load_binance_klines(g.EXPLO,with_flow=True);co=flow_coordinates(f)
X=co[['z','iota','nu']].to_numpy(float);r=co['r'].to_numpy(float);iota=co['iota'].to_numpy(float)
vol=f.volume.to_numpy(float);px=np.log(f.close.to_numpy(float));ts=f.timestamp.to_numpy(np.int64);pos={int(t):k for k,t in enumerate(ts)}
def waist(u):
    hv=u[:,2]>=np.quantile(u[:,2],.6);s=u[hv,0]+u[hv,1];s=(s-s.mean())/s.std();return float(np.mean(np.abs(s)<.3)/P0)
def cone(u):
    lo=u[:,2]<=np.quantile(u[:,2],1/3);hi=u[:,2]>=np.quantile(u[:,2],2/3);return float(u[hi,0].std()/u[lo,0].std())
rows=[]
for _,row in G.iterrows():
    i=pos[int(row.origin_ts)];w=X[i-W+1:i+1];a,b=split_historical(w)
    A=slice(i-W+1+NA,i-W+1+NA+HALF);B=slice(i-W+1+NA+HALF,i+1)
    d={'origin_ts':int(row.origin_ts)}
    for j,c in enumerate(('z','i','n')):
        d[f'dmu_{c}']=float(b[:,j].mean()-a[:,j].mean());d[f'dlsd_{c}']=float(np.log(b[:,j].std()/a[:,j].std()))
        d[f'dkurt_{c}']=float(kurtosis(b[:,j])-kurtosis(a[:,j]))
    ca,cb=np.corrcoef(a,rowvar=False),np.corrcoef(b,rowvar=False)
    d.update({'dcor_zi':float(cb[0,1]-ca[0,1]),'dcor_zn':float(cb[0,2]-ca[0,2]),'dcor_in':float(cb[1,2]-ca[1,2]),
              'dlogdet':float(np.linalg.slogdet(np.cov(b,rowvar=False))[1]-np.linalg.slogdet(np.cov(a,rowvar=False))[1]),
              'waist_A':waist(a),'waist_B':waist(b),'cone_A':cone(a),'cone_B':cone(b),'cor_zi_B':float(cb[0,1])})
    # observaveis brutos (sem gaussianizar)
    d.update({'mk_lrv':float(np.log((r[B]**2).sum()/(r[A]**2).sum())),            # volatilidade realizada B/A
              'mk_lvol':float(np.log(vol[B].mean()/vol[A].mean())),               # volume medio B/A
              'mk_net_iota_A':float(iota[A].mean()),'mk_net_iota_B':float(iota[B].mean()),   # saldo de agressao
              'mk_lsd_iota':float(np.log(iota[B].std()/iota[A].std())),           # heterogeneidade do fluxo
              'mk_lsd_lvol':float(np.log(np.log(vol[B]).std()/np.log(vol[A]).std())),  # irregularidade do volume
              'mk_ret_B':float(px[B.stop-1]-px[B.start-1]),'mk_ret_A':float(px[A.stop-1]-px[A.start-1]),
              'mk_cor_ri_A':float(np.corrcoef(r[A],iota[A])[0,1]),'mk_cor_ri_B':float(np.corrcoef(r[B],iota[B])[0,1]),
              'mk_lrv_B_abs':float(np.log((r[B]**2).sum()))})
    if i+360<len(r):d.update({'fw_lrv6h':float(np.log((r[i+1:i+361]**2).sum()/(r[B][-360:]**2).sum())),
                              'fw_lvol6h':float(np.log(vol[i+1:i+361].mean()/vol[B][-360:].mean())),'fw_ret6h':float(px[i+360]-px[i])})
    rows.append(d)
D=G.merge(pd.DataFrame(rows),on='origin_ts');D.to_csv(ROOT/'reports'/'dicionario'/'dados.csv',index=False);print(D.shape,D.motivo.isna().mean())
