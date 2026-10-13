"""M34 engenharia (BTC 1m mai-jul/2026, ja gasto). NENHUM desempenho preditivo de G ou E.
Mede: custo, taxa de falha, distribuicoes, confiabilidade (bootstrap em blocos dentro das metades),
correlacao G x E, e penalidade de 10 placebos para escolher a regularizacao do grupo."""
import sys,json,math,time,numpy as np,pandas as pd;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments import m34_deformacoes as m
from experiments import m31g1_engenharia as g
from experiments import m32_casca as m32
from experiments.m31g0_features_causais import qlike_deviance
from experiments.precisao_formas_3d import split_historical
from experiments.m3_precisao_nao_convexidade import circular_blocks
OUT=ROOT/'reports'/'m34';OUT.mkdir(parents=True,exist_ok=True)
f=load_binance_klines(g.EXPLO,with_flow=True);co=flow_coordinates(f);X=co[['z','iota','nu']].to_numpy(float)
ts=f.timestamp.to_numpy(np.int64)
orig=[i for i in np.flatnonzero((ts//60000)%15==0) if i>=m.WINDOW+1500 and np.isfinite(X[i-m.WINDOW+1:i+1]).all()]
sub=orig[::8];rows=[];t0=time.perf_counter()
for i in sub:
    G,why,E=m.features(X[i-m.WINDOW+1:i+1]);rows.append({'origin_ts':int(ts[i]),'motivo':why,**(G or {}),**{f'E_{k}':v for k,v in E.items()}})
tg=(time.perf_counter()-t0)/len(sub);D=pd.DataFrame(rows);D.to_csv(OUT/'amostra_features.csv',index=False)
valid=D.motivo.isna();print('origens amostradas',len(D),'s/origem',round(tg,2),'validas',float(valid.mean()),D.motivo.value_counts().to_dict(),flush=True)
# confiabilidade
rng=np.random.default_rng(0);pick=np.linspace(0,len(sub)-1,40).astype(int);rel={k:[] for k in m.G_COLS+tuple('E_'+c for c in m.E_COLS)}
for p in pick:
    i=sub[p];a,b=split_historical(X[i-m.WINDOW+1:i+1]);vals={k:[] for k in rel}
    for r in range(8):
        a2=circular_blocks(a,rng,15)[:len(a)];b2=circular_blocks(b,rng,15)[:len(b)]
        try:G,_=m.geom_from_halves(a2,b2,m.SEED+r)
        except Exception:G=None
        E=m.econ_from_halves(a2,b2)
        if G:
            for k in m.G_COLS:vals[k].append(G[k])
        for k in m.E_COLS:vals['E_'+k].append(E[k])
    for k,v in vals.items():
        if len(v)>=4:rel[k].append(float(np.var(v,ddof=1)))
confi={}
for k,v in rel.items():
    col=D.loc[valid,k] if k in D else None
    tot=float(np.var(col,ddof=1)) if col is not None and len(col)>2 else np.nan
    confi[k]={'var_ruido_media':float(np.mean(v)) if v else None,'var_total':tot,'confiabilidade':float(1-np.mean(v)/tot) if v and tot>0 else None}
print('confiabilidade',{k:round(v['confiabilidade'],2) if v['confiabilidade'] is not None else None for k,v in confi.items()},flush=True)
# correlacao G x E (descritiva, sem alvo)
C=D.loc[valid,list(m.G_COLS)+['E_'+c for c in m.E_COLS]].corr().loc[list(m.G_COLS),['E_'+c for c in m.E_COLS]]
maxabs={k:float(C.loc[k].abs().max()) for k in m.G_COLS}
print('max |corr| de cada G com E',{k:round(v,2) for k,v in maxabs.items()},flush=True)
# placebo: penalidade de 10 variaveis sem informacao, para escolher ridge
d,_=g.build(f);rv=d.rv_future_15.to_numpy(float);phi=.5**(1/24);pen={}
for ridge in (100.,300.,1000.,3000.):
    v0=m32.rolling_forecasts(d,g.B0,ridge=ridge);ok=np.isfinite(v0);ok[:1344]=False;dev0=qlike_deviance(v0[ok],rv[ok]);ps=[]
    for s in range(3):
        rr=np.random.default_rng(500+s);e=rr.standard_normal((len(d),10));P=np.empty_like(e);P[0]=e[0]
        for k in range(1,len(d)):P[k]=phi*P[k-1]+math.sqrt(1-phi*phi)*e[k]
        dd=d.copy();names=tuple(f'pl{j}' for j in range(10))
        for j,nm in enumerate(names):dd[nm]=P[:,j]
        v1=m32.rolling_forecasts(dd,g.B0+names,ridge=ridge);ps.append(float((qlike_deviance(v1[ok],rv[ok])-dev0).mean()/dev0.mean()))
    pen[str(ridge)]={'dev_B0':float(dev0.mean()),'penalidade_10_placebos_pct':100*float(np.mean(ps))};print('ridge',ridge,pen[str(ridge)],flush=True)
res={'n_origens_amostradas':len(D),'s_por_origem':tg,'fracao_valida':float(valid.mean()),'motivos_falha':D.motivo.value_counts().to_dict(),
     'origens_por_trimestre_estimadas':8600,'horas_cpu_por_trimestre':tg*8600/3600,
     'resumo_G':D.loc[valid,list(m.G_COLS)].describe().round(4).to_dict(),'confiabilidade':confi,'max_abs_corr_G_com_E':maxabs,
     'corr_G_E':C.round(3).to_dict(),'placebo_ridge':pen}
(OUT/'m34_engenharia.json').write_text(json.dumps(res,indent=1,ensure_ascii=False,default=float))
