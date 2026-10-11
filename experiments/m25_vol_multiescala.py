#!/usr/bin/env python3
"""SGV-M25: multi-scale volatility memory (HARCH-type) on top of the M24 model.

Variance of each whitened coordinate:
    h_t = w + a1 u_{t-1}^2 + a15 mean(u^2 over t-15..t-1) + a60 mean(.. 60) + a240 mean(.. 240) + b h_{t-1}
with w = 1 - a1 - a15 - a60 - a240 - b (unit unconditional variance), QML on the prefix.
Mean: HAR (1/15/60 min) inside two-scale regimes, real slow block (LM), filtered
historical innovations (FHS) -- exactly M24's HARLMF otherwise.
Nulls: HARLMFV (new, main), HARLMF (M24), BL. Same 12 statistics, 39 refs, conservative rank.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.signal import lfilter
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates
from experiments.precisao_formas_3d import gaussianize_three
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m5_validacao_conjunta_sf1 import WINDOW
from experiments.m12_nulos_regimes_temporais import PREFIX
from experiments.m13_calibracao_alarmes_regimes import wilson
from experiments.m15_forma_persistencia_comparadores import mcnemar_exact
from experiments.m16_trio_btc_exploratorio import load,EXPECTED_ORIGINS,CORRECT_FAMILY_LEVEL
from experiments.m17_tipo_de_memoria import BURN
from experiments.m18_acoplamento_dinamico import LONG_BLOCK
from experiments.m21_posto_conservador import conservative_rank
from experiments.m23_modelo_minimo import slow_layer,full_stats,STATS
from experiments.m24_har_fhs import har_features,companion_radius,fit_har

BASE_SEED=2026101125
REFS=39
INTERVAL='1m'
VH=(15,60,240)
NULLS=('HARLMFV','HARLMF','BL')
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
PER_SHARD=2
ALPHA_PRIMARY=.05/3
ALPHA_EQUIV=.05/len(STATS)


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


# ---------------------------------------------------------------- HARCH
def lagged_means(u2):
    """Row t: [u2_{t-1}, mean u2_{t-15..t-1}, mean .. 60, mean .. 240] (zeros-padded start with 1s)."""
    c=np.concatenate([[0.],np.cumsum(u2)]);n=len(u2);t=np.arange(n)
    out=[np.r_[1.,u2[:-1]]]
    for h in VH:
        lo=np.maximum(t-h,0);cnt=np.maximum(t-lo,1)
        m=(c[t]-c[lo])/cnt;m[0]=1.;out.append(m)
    return np.column_stack(out)


def harch_nll(p,M,u2):
    a=np.asarray(p[:4]);b=p[4]
    if np.any(a<0) or b<0 or a.sum()+b>=.999:return 1e12
    x=(1-a.sum()-b)+M@a
    h=lfilter([1.],[1.,-b],x)
    h=np.maximum(h,1e-6)
    return float(.5*np.sum(np.log(h)+u2/h))


def fit_harch(u):
    u2=np.asarray(u,float)**2;M=lagged_means(u2);best=None
    for x0 in ((.05,.05,.05,.05,.7),(.1,.1,.05,.02,.6),(.03,.03,.1,.1,.6),(.05,.0,.0,.0,.9)):
        r=minimize(harch_nll,x0,args=(M,u2),method='Nelder-Mead',options={'xatol':1e-4,'fatol':1e-3,'maxiter':800})
        if best is None or r.fun<best.fun:best=r
    p=[float(v) for v in best.x]
    if min(p)<0 or sum(p)>=.999:p=[0.,0.,0.,0.,0.]
    return p


def fit_harv(x,seed):
    """M24 HARLMF with the variance swapped for HARCH (1/15/60/240)."""
    xs,ss,slow=slow_layer(x,seed)
    d=np.zeros(len(xs))
    for s in (0,1):d[slow==s]=ss[slow==s]-ss[slow==s].mean()
    xs[:,2]-=d
    t,F=har_features(xs)
    par={};U_t=[];U=[];diag={}
    for s in (0,1):
        m=slow[t]==s
        if m.sum()<300:raise ValueError(f'regime {s}: <300 rows')
        B=np.linalg.lstsq(F[m],xs[t[m]],rcond=None)[0].T
        c,A1,A15,A60=B[:,0],B[:,1:4],B[:,4:7],B[:,7:10]
        rho=companion_radius(A1,A15,A60);shr=1.
        while rho>=.995:
            shr*=.98;rho=companion_radius(A1*shr,A15*shr,A60*shr)
        A1,A15,A60=A1*shr,A15*shr,A60*shr
        e=xs[t[m]]-(c+F[m][:,1:4]@A1.T+F[m][:,4:7]@A15.T+F[m][:,7:10]@A60.T)
        L=np.linalg.cholesky(np.cov(e,rowvar=False))
        par[s]=(c,A1,A15,A60,L);U_t.append(t[m]);U.append(np.linalg.solve(L,e.T).T)
        diag[f'regime{s}']={'companion_radius':rho,'shrink':shr}
    o=np.argsort(np.concatenate(U_t));U=np.concatenate(U)[o]
    vp=[fit_harch(U[:,j]) for j in range(3)]
    diag['harch']=[{'a1':p[0],'a15':p[1],'a60':p[2],'a240':p[3],'b':p[4]} for p in vp]
    Z=np.empty_like(U)
    for j in range(3):
        u2=U[:,j]**2;M=lagged_means(u2);a=np.array(vp[j][:4]);b=vp[j][4]
        h=np.maximum(lfilter([1.],[1.,-b],(1-a.sum()-b)+M@a),1e-6)
        Z[:,j]=U[:,j]/np.sqrt(h)
    Z=(Z-Z.mean(0))/Z.std(0)
    A=np.array([p[:4] for p in vp]);Bv=np.array([p[4] for p in vp]);W=1-A.sum(1)-Bv

    def sample(rng,n):
        total=n+BURN+240
        start=int(rng.integers(0,len(slow)));idx=(start+np.arange(total))%len(slow)
        seq=slow[idx];out=np.empty((total,3))
        c,A1,A15,A60,L=par[int(seq[0])]
        mu=np.linalg.solve(np.eye(3)-A1-A15-A60,c)
        buf=np.tile(mu,(60,1));s15=mu*15;s60=mu*60;pos=0
        ub=np.ones((240,3));q15=np.full(3,15.);q60=np.full(3,60.);q240=np.full(3,240.);up=0
        h=np.ones(3);u2prev=np.ones(3)
        draws=Z[rng.integers(0,len(Z),size=total)]
        for k in range(total):
            c,A1,A15,A60,L=par[int(seq[k])]
            h=W+A[:,0]*u2prev+A[:,1]*q15/15+A[:,2]*q60/60+A[:,3]*q240/240+Bv*h
            u=np.sqrt(h)*draws[k];u2=u*u
            o15=ub[(up-15)%240].copy();o60=ub[(up-60)%240].copy();o240=ub[up].copy()
            ub[up]=u2;up=(up+1)%240
            q15+=u2-o15;q60+=u2-o60;q240+=u2-o240;u2prev=u2
            last=buf[(pos-1)%60]
            xk=c+A1@last+A15@(s15/15)+A60@(s60/60)+L@u
            old60=buf[pos].copy();old15=buf[(pos-15)%60].copy()
            buf[pos]=xk;pos=(pos+1)%60;s60+=xk-old60;s15+=xk-old15
            out[k]=xk
        out[:,2]+=d[idx]
        return out[-n:]
    return sample,diag


def build(prefix_df,seed):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ok=np.isfinite(pre).all(axis=1)
    raw=pre[int(np.flatnonzero(ok)[0]):]
    if len(raw)<2000 or not np.isfinite(raw).all():raise ValueError('Prefix coordinates invalid')
    ns=gaussianize_three(raw,raw)
    s={};diag={}
    s['HARLMFV'],diag['HARLMFV']=fit_harv(ns,seed+50)
    s['HARLMF'],diag['HARLMF']=fit_har(ns,seed+50,fhs=True)
    s['BL']=lambda rng,n:circular_blocks(raw,rng,LONG_BLOCK[INTERVAL])[:n]
    return s,diag


def run_origin(df,start,k,refs=REFS,stats_fn=full_stats):
    pre=PREFIX[INTERVAL];w=WINDOW[INTERVAL]
    prefix=df.iloc[start-pre:start].copy();fut=df.iloc[start:start+w].copy()
    actual=flow_coordinates(pd.concat([prefix,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-w:]
    item={'origin':int(k),'window_start_ms':int(fut.timestamp.iloc[0]),'models':{}}
    if not np.isfinite(actual).all():item['status']='invalid_observed';return item
    obs=stats_fn(actual,seed_int(k,1));item['observed']=obs
    try:samplers,diag=build(prefix,seed_int(k,2))
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
        item['status']='fit_failed';item['error']=str(e);return item
    item['status']='valid';item['fit_diagnostics']=diag
    for name in NULLS:
        ref={s:[] for s in STATS}
        for j in range(refs):
            try:
                sim=samplers[name](np.random.default_rng(seed_int(k,3,NULL_ID[name],j)),w)
                if sim.shape!=(w,3) or not np.isfinite(sim).all():raise ValueError('bad window')
                r=stats_fn(sim,seed_int(k,4,NULL_ID[name],j))
            except (ValueError,RuntimeError,np.linalg.LinAlgError):
                r={s:None for s in STATS}
            for s in STATS:ref[s].append(r[s])
        rec={'references':ref}
        for s in STATS:
            p=conservative_rank(obs[s],ref[s]);rec[s]={'p_rank':p,'alarm':bool(p is not None and p<=.05)}
        item['models'][name]=rec
    return item


def aggregate(rows,n_expected):
    if sorted(r['origin'] for r in rows)!=list(range(n_expected)):raise ValueError('Missing or duplicate origins')
    val=[r for r in rows if r.get('status')=='valid']
    cells={}
    for m in NULLS:
        for s in STATS:
            al=[r['models'][m][s]['alarm'] for r in val if r['models'][m][s]['p_rank'] is not None]
            k=int(sum(al));n=len(al)
            cells[f'{m}|{s}']={'alarms':k,'n':n,'rate':k/n if n else None,'wilson95':wilson(k,n),
                               'elevated':bool(n and wilson(k,n)[0]>CORRECT_FAMILY_LEVEL)}
    def pair(a,b,s):
        xa=[];xb=[]
        for r in val:
            pa=r['models'][a][s];pb=r['models'][b][s]
            if pa['p_rank'] is not None and pb['p_rank'] is not None:xa.append(pa['alarm']);xb.append(pb['alarm'])
        return mcnemar_exact(xa,xb)
    primary={s:pair('HARLMF','HARLMFV',s) for s in ('vol_1','vol_5','vol_30')}
    for v in primary.values():v['significant']=bool(v['p_one_sided']<ALPHA_PRIMARY)
    worse={s:pair('HARLMFV','BL',s) for s in STATS}
    for v in worse.values():v['significant']=bool(v['p_one_sided']<ALPHA_EQUIV)
    full=all(not cells[f'HARLMFV|{s}']['elevated'] for s in STATS)
    equiv=all(not v['significant'] for v in worse.values())
    verdict=('ADEQUACAO PLENA (nenhuma estatistica elevada)' if full else
             'EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)' if equiv else 'NAO FECHA A LACUNA')
    med=lambda key:[float(np.median([r['fit_diagnostics']['HARLMFV']['harch'][j][key] for r in val])) for j in range(3)]
    diagq={f'harch_{k}_median_z_iota_nu':med(k) for k in ('a1','a15','a60','a240','b')}
    return {'n_valid':len(val),'status':{s:sum(1 for r in rows if r.get('status')==s) for s in {r.get('status') for r in rows}},
            'cells':cells,'primary_vs_HARLMF':primary,'HARLMFV_worse_than_BL':worse,'verdict':verdict,'diagnostics':diagq}


def report(a):
    pct=lambda x:'—' if x is None else f'{100*x:.0f}%'
    L=['# SGV-M25 — Volatilidade multiescala (resultados)','',
       f"Origens válidas: {a['n_valid']} ({a['status']}). Agregado por `experiments/m25_vol_multiescala.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M25_20261011.md`.",'',
       '| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:L.append(f'| {m} | '+' | '.join(pct(a['cells'][f'{m}|{s}']['rate']) for s in STATS)+' |')
    L+=['','**Primário (HARLMF → HARLMFV, McNemar unilateral, α=0,0167):**','']
    for s,v in a['primary_vs_HARLMF'].items():
        L.append(f"- {s}: só HARLMF {v['x_only']}, só HARLMFV {v['y_only']}, p={v['p_one_sided']:.2g} → {'melhora significativa' if v['significant'] else 'n.s.'}")
    L+=['','**HARLMFV pior que BL? (α=0,05/12):**','']
    for s,v in a['HARLMFV_worse_than_BL'].items():
        L.append(f"- {s}: só HARLMFV {v['x_only']}, só BL {v['y_only']}, p={v['p_one_sided']:.2g}{' **(pior)**' if v['significant'] else ''}")
    L+=['',f"**Veredito pré-registrado: {a['verdict']}**",'','Diagnósticos: '+json.dumps(a['diagnostics'],ensure_ascii=False)]
    return '\n'.join(L)


def write(obj,name):
    p=ROOT/'reports'/'m25'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n');return p


def run_shard(shard):
    df,starts=load(INTERVAL)
    ks=range(shard*PER_SHARD,min(len(starts),(shard+1)*PER_SHARD))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],k) for k in ks]
    write({'status':'M25_SHARD','shard':shard,'n_origins_total':len(starts),'origins':rows},f'shard_{shard:02d}.json')
    print(json.dumps({'shard':shard,'n':len(rows)}))


def run_pilot():
    df,starts=load(INTERVAL)
    r=run_origin(df,starts[0],0,refs=2)
    bad=[] if r.get('status')=='valid' else [r.get('status'),r.get('error')]
    if not bad:
        for m,v in r['models'].items():
            for s in STATS:
                if s!='m11' and any(x is None for x in v['references'][s]):bad.append((m,s))
    write({'status':'M25_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad}))
    if bad:raise RuntimeError('Pilot failed')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('pilot','shard','aggregate'),required=True)
    ap.add_argument('--shard',type=int);ap.add_argument('--shards-dir',default=str(ROOT/'reports'/'m25'/'_dl'))
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    elif a.mode=='shard':run_shard(a.shard)
    else:
        n=EXPECTED_ORIGINS[INTERVAL];rows=[]
        for s in range((n+PER_SHARD-1)//PER_SHARD):
            d=json.loads((Path(a.shards_dir)/f'shard_{s:02d}.json').read_text())
            if d.get('shard')!=s or d.get('n_origins_total')!=n:raise ValueError('bad shard')
            rows+=d['origins']
        agg=aggregate(rows,n);write(agg,'SGV_M25_AGREGADO.json')
        md=report(agg);(ROOT/'reports'/'m25'/'SGV_M25_RESULTADOS.md').write_text(md+'\n');print(md)


if __name__=='__main__':main()
