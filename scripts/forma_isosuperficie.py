"""Investigacao descritiva da forma das cascas HDR50 (exploratorio, sem inferencia).
Mesmas janelas e mesmo metodo do M1 (6 janelas equiespacadas; ancora 30% + metades A/B;
GMM2; curvatura gaussiana ANALITICA da densidade ajustada)."""
import sys,json,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from experiments import isosuperficies_morfometria as iso
from experiments.precisao_formas_3d import split_historical
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
N=49
def windows(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    df=load_binance_klines(paths,with_flow=True);x=flow_coordinates(df)[['z','iota','nu']].to_numpy(float)
    ts=df.timestamp.to_numpy(np.int64);w=iso.WINDOW[interval];c=[]
    for end in range(w,len(x)+1,w):
        xx=x[end-w:end];tt=ts[end-w:end]
        if np.isfinite(xx).all() and np.all(np.diff(tt)==iso.STEP[interval]):c.append((end,int(tt[0]),xx))
    sel=np.linspace(0,len(c)-1,min(iso.MAX_WINDOWS,len(c)),dtype=int)
    return [c[i] for i in sel]
def shell(sample,kind,seed):
    pts,dx=iso.make_grid(N);d,par=iso.density_values(sample,pts,kind,seed,with_model=True)
    field=d.reshape(N,N,N);th,_=iso.hdr_thresholds(field,dx);tau=th[.5]['tau']
    mesh,trunc=iso.extract_mesh(field,tau,dx);K,H=iso.implicit_curvatures(np.asarray(mesh.vertices),par)
    return mesh,K,par,field,tau,dx
def cond_spread(s):
    nu=s[:,2];q=np.quantile(nu,[1/3,2/3]);out=[]
    for lo,hi,lab in ((-9,q[0],'baixo'),(q[0],q[1],'medio'),(q[1],9,'alto')):
        m=(nu>lo)&(nu<=hi);out.append({'nu':lab,'sd_z':float(s[m,0].std()),'sd_iota':float(s[m,1].std()),'corr_z_iota':float(np.corrcoef(s[m,0],s[m,1])[0,1])})
    return out
def main():
  res={}
  for interval in ('1m','1h'):
      rows=[]
      for end,t0,xx in windows(interval):
          a,b=split_historical(xx)
          mesh,K,par,_,_,_=shell(a,'mixture',iso.SEED+end)
          area=np.zeros(len(mesh.vertices));np.add.at(area,mesh.faces.ravel(),np.repeat(mesh.area_faces/3,3))
          v=np.asarray(mesh.vertices);neg=K<0
          comp=[{'peso':float(w),'media':np.round(m,2).tolist(),'dp':np.round(np.sqrt(np.diag(np.linalg.inv(p))),2).tolist(),
                 'corr_z_iota':float(np.linalg.inv(p)[0,1]/np.sqrt(np.linalg.inv(p)[0,0]*np.linalg.inv(p)[1,1]))} for w,m,p in zip(par['weights'],par['means'],par['precisions'])]
          rows.append({'inicio_ms':t0,'area_sela':float(area[neg].sum()/area.sum()),
                       'sela_centro_medio':np.round((v[neg]*area[neg,None]).sum(0)/area[neg].sum(),2).tolist() if neg.any() else None,
                       'componentes':comp,'espalhamento_por_volume_A':cond_spread(a)})
      res[interval]=rows
      print('=====',interval)
      for r in rows:
          print(f"area sela {r['area_sela']:.3f} centro sela {r['sela_centro_medio']}")
          for c in r['componentes']:print('   comp',c)
          print('   ',[(e['nu'],round(e['sd_z'],2),round(e['sd_iota'],2),round(e['corr_z_iota'],2)) for e in r['espalhamento_por_volume_A']])
  (ROOT/'reports'/'forma'/'investigacao_forma.json').write_text(json.dumps(res,indent=1))

if __name__=='__main__':main()
