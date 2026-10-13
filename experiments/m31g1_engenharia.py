#!/usr/bin/env python3
"""SGV M31-G1 — ENGENHARIA (sem teste de hipotese, sem dado reservado).

O que este modulo faz:
  1. Variaveis de forma ORIGINAIS (copula local da janela de 6 h), copiadas de
     scripts/forma_movimento.py @ e1e86b1 e scripts/hdom_teste.py @ 1a86847:
        cone    = sd(u_z | u_nu >= q2/3) / sd(u_z | u_nu <= q1/3)
        cintura = mean(|s| < 0,3)/0,2358, s = (u_z+u_iota)/sqrt2 nos 40% de maior u_nu (padronizado)
  2. Baseline forte B0 (HAR-X sazonal com HARQ, amplitude de Parkinson, semivariancia,
     indicadores de quarto de hora, harmonicos da hora do dia, dia da semana, volume, |iota|).
  3. Controle de atribuicao B0+ = B0 + elasticidade movel volatilidade-volume (6 h) e interacao com nu_t.
  4. Regra de lacunas: a serie e dividida em segmentos continuos; nenhuma janela, defasagem
     ou alvo atravessa uma lacuna; cada segmento reaquece do zero.
  5. Poder: variaveis PLACEBO (ruido AR(1) com a persistencia do cone) contra B0 em dados ja gastos,
     para medir o erro-padrao HAC da diferenca de QLIKE e o efeito minimo detectavel —
     SEM calcular o desempenho de B1, B1+ ou B0+ (nada sobre a hipotese).
"""
from __future__ import annotations
import argparse,json,math,sys,time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata,norm
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates
from sgvgeo.data import load_binance_klines
from experiments.m31g0_features_causais import target_rv_forward,qlike_deviance,synthetic_klines

MIN=60_000
W=360                 # janela da forma (6 h), como no original
NU_HISTORY=1500       # mediana do volume em flow_coordinates
RVS=(15,60,240,1440)
STEP=15;H=15
TRAIN=1344            # 14 dias de origens de 15 min (escolhido so com B0 e placebos, ver grade_placebo.json)
RIDGE=100.0;EPS=1e-14     # idem
WARM=NU_HISTORY+max(W,max(RVS))+1
P0=2*norm.cdf(.3)-1
EXPLO=tuple(ROOT/'data'/f'BTCUSDT-1m-2026-{m}.zip' for m in ('05','06','07'))

SEASON=(['q15_1','q15_2','q15_3']+[f'{f}_hod{k}' for k in (1,2,3) for f in ('sin','cos')]
        +[f'weekday_{d}' for d in range(6)])
B0=tuple([f'log_rv_{w}' for w in RVS]+['harq_60','harq_x_rv15','log_pk_15','log_pk_60','down_share_60',
         'log_vol_15','log_vol_60','nu','abs_iota_15']+SEASON)
ELAST=('elast','elast_x_nu')
SHAPE=('cone_log','cintura','cone_log_x_nu')
SHELL=('saddle_frac',)
MODELS={'B0':B0,'B0plus':B0+ELAST,'B1':B0+SHAPE,'B1plus':B0+ELAST+SHAPE,'B2':B0+ELAST+SHAPE+SHELL}
SHELL_GRID=35;SHELL_SEED=20261012


# ---------------------------------------------------------------- forma (original)
def cop(x):
    """Copula local: postos -> normal, por coluna (identico a forma_movimento/hdom_teste)."""
    return norm.ppf(np.column_stack([rankdata(x[:,j])/(len(x)+1) for j in range(x.shape[1])]))


def shape_original(z,iota,nu):
    """(cone, cintura) exatamente como scripts/forma_movimento.py::shape @ e1e86b1."""
    u=cop(np.column_stack([z,iota,nu]));uz,ui,uv=u.T
    hv=uv>=np.quantile(uv,.6);s=uz[hv]+ui[hv];s=(s-s.mean())/s.std()
    lo=uv<=np.quantile(uv,1/3);hi=uv>=np.quantile(uv,2/3)
    return float(uz[hi].std()/uz[lo].std()),float(np.mean(np.abs(s)<.3)/P0)


def shell_saddle(z,iota,nu,grid=SHELL_GRID,seed=SHELL_SEED):
    """Variavel NATIVA da casca: fracao da area da HDR50 (GMM2 na copula local da janela)
    com curvatura gaussiana analitica K<0 (mesmo instrumento do M1). None se a malha nao for
    fechada, estiver truncada ou nao cobrir massa suficiente."""
    from experiments import isosuperficies_morfometria as iso
    u=cop(np.column_stack([z,iota,nu]))
    pts,dx=iso.make_grid(grid);dens,par=iso.density_values(u,pts,'mixture',seed,with_model=True)
    f=dens.reshape(grid,grid,grid);th,cov=iso.hdr_thresholds(f,dx)
    mesh,trunc=iso.extract_mesh(f,th[.5]['tau'],dx)
    top=iso.mesh_topology(np.asarray(mesh.vertices),np.asarray(mesh.faces))
    if trunc or not top['closed_edges'] or cov<iso.MIN_COVERAGE:return None
    K,_=iso.implicit_curvatures(np.asarray(mesh.vertices),par)
    area=np.zeros(len(mesh.vertices));np.add.at(area,np.asarray(mesh.faces).ravel(),np.repeat(mesh.area_faces/3,3))
    return float(area[K<0].sum()/area.sum())


def elasticity(z,nu):
    """B0+: inclinacao OLS de |z| em nu na janela, dividida pela media de |z| (semi-elasticidade)."""
    a=np.abs(z);c=nu-nu.mean();den=float(c@c)
    if den<=1e-12 or a.mean()<=1e-12:return None
    return float((c@(a-a.mean()))/den/a.mean())


# ---------------------------------------------------------------- segmentos e variaveis
def segments(ts):
    """Indices [ini,fim) de trechos continuos de 1 min."""
    br=np.flatnonzero(np.diff(ts)!=MIN)+1
    edges=np.r_[0,br,len(ts)]
    return [(int(a),int(b)) for a,b in zip(edges[:-1],edges[1:])]


def _roll(x,w):
    c=np.r_[0.,np.cumsum(np.where(np.isfinite(x),x,0.))]
    out=np.full(len(x),np.nan);out[w-1:]=c[w:]-c[:-w];return out


def segment_rows(seg,with_shell=False):
    """Linhas de origem dentro de UM segmento continuo (nenhuma informacao de fora dele)."""
    seg=seg.reset_index(drop=True);n=len(seg)
    if n<WARM+H+2:return []
    co=flow_coordinates(seg);r=co['r'].to_numpy(float);z=co['z'].to_numpy(float)
    iota=co['iota'].to_numpy(float);nu=co['nu'].to_numpy(float)
    ts=seg.timestamp.to_numpy(np.int64);vol=seg.volume.to_numpy(float)
    hl=np.log(seg.high.to_numpy(float)/seg.low.to_numpy(float));pk=hl*hl/(4*math.log(2))
    r2=r*r;r4=r2*r2;neg=np.where(r<0,r2,0.)
    rv={w:_roll(r2,w) for w in RVS};rq60=_roll(r4,60)*60/3;pk15=_roll(pk,15);pk60=_roll(pk,60)
    dn60=_roll(neg,60);v15=_roll(vol,15)/15;v60=_roll(vol,60)/60;ai15=_roll(np.abs(iota),15)/15
    fut=target_rv_forward(r,H);rows=[]
    for i in np.flatnonzero(((ts//MIN)%STEP==0)&(np.arange(n)>=WARM)&(np.arange(n)<n-H)):
        zw,iw,vw=z[i-W+1:i+1],iota[i-W+1:i+1],nu[i-W+1:i+1]
        if not(np.isfinite(zw).all() and np.isfinite(iw).all() and np.isfinite(vw).all()):continue
        if not(np.isfinite(rv[1440][i]) and rv[15][i]>0 and rq60[i]>0 and pk15[i]>0 and np.isfinite(fut[i]) and fut[i]>0):continue
        cone,cint=shape_original(zw,iw,vw);el=elasticity(zw,vw)
        if el is None or not np.isfinite(cone) or cone<=0:continue
        sad=None
        if with_shell:
            try:sad=shell_saddle(zw,iw,vw)
            except (ValueError,np.linalg.LinAlgError,RuntimeError):sad=None
        t=pd.Timestamp(int(ts[i]),unit='ms',tz='UTC');qh=t.minute//15;hod=t.hour+t.minute/60
        row={'origin_ts':int(ts[i]),'rv_future_15':float(fut[i]),
             **{f'log_rv_{w}':float(np.log(rv[w][i])) for w in RVS},
             'harq_60':float(.5*np.log(rq60[i])-np.log(rv[60][i])),
             'log_pk_15':float(np.log(pk15[i])),'log_pk_60':float(np.log(pk60[i])),
             'down_share_60':float(dn60[i]/rv[60][i]),'log_vol_15':float(np.log(v15[i])),'log_vol_60':float(np.log(v60[i])),
             'nu':float(nu[i]),'abs_iota_15':float(ai15[i]),
             **{f'q15_{k}':float(qh==k) for k in (1,2,3)},
             **{f'{f}_hod{k}':float(fn(2*np.pi*k*hod/24)) for k in (1,2,3) for f,fn in (('sin',np.sin),('cos',np.cos))},
             **{f'weekday_{d}':float(t.dayofweek==d) for d in range(6)},
             'elast':el,'elast_x_nu':el*float(nu[i]),
             'cone_log':float(np.log(cone)),'cintura':cint,'cone_log_x_nu':float(np.log(cone))*float(nu[i]),
             'saddle_frac':np.nan if sad is None else sad}
        row['harq_x_rv15']=row['harq_60']*row['log_rv_15']
        rows.append(row)
    return rows


def build(frame,with_shell=False):
    frame=frame.sort_values('timestamp').reset_index(drop=True)
    ts=frame.timestamp.to_numpy(np.int64);rows=[];segs=segments(ts)
    for a,b in segs:rows+=segment_rows(frame.iloc[a:b],with_shell=with_shell)
    d=pd.DataFrame(rows)
    if d.empty:raise ValueError('sem origens validas')
    d=d.sort_values('origin_ts').reset_index(drop=True)
    d['label_matures_ts']=d.origin_ts+H*MIN
    return d,{'n_segmentos':len(segs),'maior_segmento_min':int(max(b-a for a,b in segs))}


# ---------------------------------------------------------------- previsao movel
def rolling_forecasts(d,cols,train=TRAIN):
    """Para cada origem: ridge em log(RV) com os `train` rotulos ja maturados; smearing."""
    X=d[list(cols)].to_numpy(float);y=np.log(np.maximum(d.rv_future_15.to_numpy(float),EPS))
    ts=d.origin_ts.to_numpy(np.int64);mat=d.label_matures_ts.to_numpy(np.int64)
    out=np.full(len(d),np.nan)
    for k in range(len(d)):
        j=np.searchsorted(mat,ts[k],side='right')   # rotulos com maturacao <= origem atual
        if j<train:continue
        sl=slice(j-train,j);Xt=X[sl];mu=Xt.mean(0);sd=Xt.std(0);sd=np.where(sd>1e-10,sd,1.)
        Z=np.column_stack([np.ones(train),(Xt-mu)/sd]);pen=np.diag([0.]+[RIDGE]*X.shape[1])
        beta=np.linalg.solve(Z.T@Z+pen,Z.T@y[sl]);res=y[sl]-Z@beta
        sm=float(np.mean(np.exp(np.clip(res,-30,15))))
        out[k]=float(np.exp(np.clip(np.r_[1.,(X[k]-mu)/sd]@beta,-30,15))*sm)
    return out


def hac_se(x,lag):
    x=np.asarray(x,float)-np.mean(x);n=len(x);g0=x@x/n;s=g0
    for l in range(1,lag+1):s+=2*(1-l/(lag+1))*(x[l:]@x[:-l])/n
    return math.sqrt(max(s,0.)/n)


def placebo_power(d,seeds=20,phi=.51**(1/24),lag=96):
    """Variaveis placebo (3 AR(1) independentes, persistencia do cone) somadas ao B0.
    Sob H0 verdadeira por construcao: mede tamanho do teste e erro-padrao HAC de mean(dev_placebo - dev_B0)."""
    v0=rolling_forecasts(d,B0);ok=np.isfinite(v0);rv=d.rv_future_15.to_numpy(float)
    dev0=qlike_deviance(v0[ok],rv[ok]);stats=[];ses=[];deltas=[]
    for s in range(seeds):
        rng=np.random.default_rng(1000+s);e=rng.standard_normal((len(d),3));p=np.empty_like(e);p[0]=e[0]
        for k in range(1,len(d)):p[k]=phi*p[k-1]+math.sqrt(1-phi*phi)*e[k]
        dd=d.copy();names=('placebo_a','placebo_b','placebo_c')
        for j,nm in enumerate(names):dd[nm]=p[:,j]
        v1=rolling_forecasts(dd,B0+names);dif=qlike_deviance(v1[ok],rv[ok])-dev0
        se=hac_se(dif,lag);ses.append(se);deltas.append(float(dif.mean()));stats.append(float(dif.mean()/se))
    m0=float(dev0.mean());se=float(np.median(ses));n=int(ok.sum())
    def mde(n_test,power=.8):return float((norm.ppf(.95)+norm.ppf(power))*se*math.sqrt(n/n_test)/m0)
    return {'n_origens_avaliadas':n,'dev_media_B0':m0,'se_hac_mediano':se,
            'placebo_dm_stats':[round(x,3) for x in stats],'placebo_frac_rejeita_5pct_unilateral':float(np.mean(np.array(stats)<-norm.ppf(.95))),
            'placebo_delta_medio':[round(x,6) for x in deltas],
            'mde_skill_80pct':{'mesmo_n':mde(n),'3_meses_~8600':mde(8600),'4_meses_~11500':mde(11500)},
            'poder_por_skill_3meses':{f'{s:.1%}':float(norm.cdf(s*m0/(se*math.sqrt(n/8600))-norm.ppf(.95))) for s in (.005,.01,.02,.03)}}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('synthetic','exploratory'),required=True)
    ap.add_argument('--seeds',type=int,default=20);ap.add_argument('--out',default=str(ROOT/'reports'/'m31g1'))
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    if a.mode=='synthetic':frame=synthetic_klines(n=40_000)
    else:
        if not all(p.exists() for p in EXPLO):raise FileNotFoundError('so BTC 1m mai-jul/2026')
        frame=load_binance_klines(EXPLO,with_flow=True)
        ts=frame.timestamp.to_numpy(np.int64)
        if not(pd.Timestamp('2026-05-01',tz='UTC').value//10**6<=ts[0] and ts[-1]<pd.Timestamp('2026-08-01',tz='UTC').value//10**6):
            raise SystemExit('dados fora do periodo exploratorio autorizado')
    t0=time.perf_counter();d,seginfo=build(frame);tf=time.perf_counter()-t0
    sanity={}
    for name,cols in MODELS.items():
        v=rolling_forecasts(d.tail(TRAIN+40).reset_index(drop=True),cols)   # so sanidade numerica, 40 previsoes
        sanity[name]={'n_previsoes_finitas':int(np.isfinite(v).sum()),'todas_positivas':bool(np.all(v[np.isfinite(v)]>0))}
    t1=time.perf_counter();pw=placebo_power(d,seeds=a.seeds);tp=time.perf_counter()-t1
    res={'estudo':'M31-G1 ENGENHARIA — sem desempenho de B0+, B1 ou B1+; sem dado reservado',
         'fonte':'sintetico' if a.mode=='synthetic' else 'BTCUSDT 1m mai-jul/2026 (ja explorado)',
         'n_candles':len(frame),**seginfo,'n_origens':len(d),'tempo_features_s':round(tf,2),'tempo_poder_s':round(tp,1),
         'variaveis':{k:list(v) for k,v in MODELS.items()},'sanidade':sanity,
         'resumo_forma':{c:{q:round(float(d[c].quantile(q)),3) for q in (.05,.5,.95)} for c in ('cone_log','cintura','elast')},
         'corr_cone_elast':round(float(np.corrcoef(d.cone_log,d.elast)[0,1]),3),
         'poder_placebo':pw}
    (out/f'm31g1_{a.mode}.json').write_text(json.dumps(res,indent=1,ensure_ascii=False))
    print(json.dumps({k:v for k,v in res.items() if k!='variaveis'},indent=1,ensure_ascii=False))


if __name__=='__main__':main()
