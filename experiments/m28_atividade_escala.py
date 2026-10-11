#!/usr/bin/env python3
"""SGV-M28: activity governs scale (protocol reports/PROTOCOLO_SGV_M28_20261011.md).

HXACT = M27's HXLOC (6 local segments, blocks of 500, local FHS) with each
coordinate's variance multiplied by an activity factor
    g_j,t = exp(gamma_j (nu_{t-1} - nubar)) / kappa_j      (kappa_j = segment mean)
where nu_{t-1} is the FULL previous volume coordinate (slow real block included).
gamma_j: QML per segment after the M26 cross variance (two stages), |gamma|<=2.
Nulls: HXACT, HXLOC (M27), BL. Primary + mechanism on ODD origins (even origins
were used by the exploratory diagnostic).
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.signal import lfilter
from scipy.stats import binomtest
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
from experiments.m18_acoplamento_dinamico import LONG_BLOCK
from experiments.m21_posto_conservador import conservative_rank
from experiments.m23_modelo_minimo import slow_layer,full_stats,STATS
from experiments.m24_har_fhs import har_features
from experiments.m26_resiliencia_cruzada import cross_design,_unpack,HFLOOR
from experiments import m27_nao_estacionariedade as m27

BASE_SEED=2026101128
REFS=39
INTERVAL='1m'
K=m27.K
BLOCK=m27.BLOCK
BURN_B=m27.BURN_B
GMAX=2.
NULLS=('HXACT','HXLOC','BL')
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
PER_SHARD=2
TARGET=('hsic_5','hsic_30')
ALPHA_PRIMARY=.05/len(TARGET)
ALPHA_EQUIV=.05/len(STATS)
ALREADY_OK=tuple(s for s in STATS if s not in TARGET)


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


# ------------------------------------------------------------ activity factor
def fit_gamma(r,h,nprev):
    nc=nprev-nprev.mean()
    def nll(g):
        e=np.exp(g*nc);hh=h*e/e.mean()
        return float(np.sum(np.log(hh)+r*r/hh))
    res=minimize_scalar(nll,bounds=(-GMAX,GMAX),method='bounded',options={'xatol':1e-4})
    return float(res.x)


def fit_segment_act(xs,t,F,lo,hi,nu_full):
    par,diag=m27.fit_segment(xs,t,F,lo,hi)
    m=(t>=lo)&(t<hi);tt=t[m]
    e=xs[tt]-(par['c']+F[m][:,1:4]@par['A1'].T+F[m][:,4:7]@par['A15'].T+F[m][:,7:10]@par['A60'].T)
    R=e/par['sd'];R2=R**2;H=np.empty_like(R)
    for j in range(3):
        cc,a,b=_unpack(np.r_[par['C'][j],par['Aown'][j],par['Bv'][j]],j);w=1-cc.sum()-a.sum()-b
        H[:,j]=np.maximum(lfilter([1.],[1.,-b],w+cross_design(R2,j)@np.r_[cc,a]),HFLOOR)
    nprev=nu_full[tt-1];nbar=float(nprev.mean())
    gam=np.array([fit_gamma(R[:,j],H[:,j],nprev) for j in range(3)])
    kap=np.array([float(np.mean(np.exp(gam[j]*(nprev-nbar)))) for j in range(3)])
    G=np.exp(np.outer(nprev-nbar,gam))/kap
    Z=R/np.sqrt(H*G);Z=(Z-Z.mean(0))/Z.std(0)
    par=dict(par);par.update({'Z':Z,'gamma':gam,'nbar':nbar,'kappa':kap})
    diag=dict(diag);diag.update({'gamma_z':float(gam[0]),'gamma_iota':float(gam[1]),'gamma_nu':float(gam[2])})
    return par,diag


def sim_act(p,rng,nsteps,dseq):
    """Like m27.sim_single but the variance sees the full previous volume (slow block inside the loop)."""
    c,A1,A15,A60,sd=p['c'],p['A1'],p['A15'],p['A60'],p['sd']
    C,Aown,Bv,W,Z=p['C'],p['Aown'],p['Bv'],p['W'],p['Z']
    gam,nbar,kap=p['gamma'],p['nbar'],p['kappa']
    mu=np.linalg.solve(np.eye(3)-A1-A15-A60,c)
    buf=np.tile(mu,(60,1));s15=mu*15;s60=mu*60;pos=0
    ub=np.ones((240,3));q15=np.full(3,15.);q60=np.full(3,60.);q240=np.full(3,240.);up=0
    h=np.ones(3);r2prev=np.ones(3);out=np.empty((nsteps,3));nuprev=mu[2]+dseq[0]
    draws=Z[rng.integers(0,len(Z),size=nsteps)]
    for k in range(nsteps):
        h=np.maximum(W+C@r2prev+Aown[:,0]*q15/15+Aown[:,1]*q60/60+Aown[:,2]*q240/240+Bv*h,HFLOOR)
        g=np.exp(gam*(nuprev-nbar))/kap
        r=np.sqrt(h*g)*draws[k];r2=r*r
        o15=ub[(up-15)%240].copy();o60=ub[(up-60)%240].copy();o240=ub[up].copy()
        ub[up]=r2;up=(up+1)%240;q15+=r2-o15;q60+=r2-o60;q240+=r2-o240;r2prev=r2
        last=buf[(pos-1)%60]
        xk=c+A1@last+A15@(s15/15)+A60@(s60/60)+sd*r
        old60=buf[pos].copy();old15=buf[(pos-15)%60].copy()
        buf[pos]=xk;pos=(pos+1)%60;s60+=xk-old60;s15+=xk-old15
        out[k]=xk;out[k,2]+=dseq[k];nuprev=out[k,2]
    return out


def fit_local_act(x,seed):
    xs,ss,slow=slow_layer(x,seed)
    d=np.zeros(len(xs))
    for s in (0,1):d[slow==s]=ss[slow==s]-ss[slow==s].mean()
    nu_full=xs[:,2].copy()
    xs[:,2]-=d
    t,F=har_features(xs);L=len(xs)
    segs=np.array_split(np.arange(L),K)
    pars=[];diags=[]
    for g in segs:
        p,dg=fit_segment_act(xs,t,F,int(g[0]),int(g[-1])+1,nu_full);pars.append(p);diags.append(dg)
    bounds=[(int(g[0]),int(g[-1])+1) for g in segs]

    def sample(rng,n):
        out=[]
        for _ in range((n+BLOCK-1)//BLOCK):
            gi=int(rng.integers(0,K));lo,hi=bounds[gi]
            p0=int(rng.integers(lo,hi))
            dseq=d[(p0-BURN_B+np.arange(BURN_B+BLOCK))%L]
            out.append(sim_act(pars[gi],rng,BURN_B+BLOCK,dseq)[-BLOCK:])
        return np.vstack(out)[:n]
    return sample,{'segments':diags}


def build(prefix_df,seed):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ok=np.isfinite(pre).all(axis=1)
    raw=pre[int(np.flatnonzero(ok)[0]):]
    if len(raw)<2000 or not np.isfinite(raw).all():raise ValueError('Prefix coordinates invalid')
    ns=gaussianize_three(raw,raw)
    s={};diag={}
    s['HXACT'],diag['HXACT']=fit_local_act(ns,seed+50)
    s['HXLOC'],_=m27.fit_local(ns,seed+50)
    s['BL']=lambda rng,n:circular_blocks(raw,rng,LONG_BLOCK[INTERVAL])[:n]
    seg=diag['HXACT']['segments']
    diag['gamma_median']={k:float(np.median([q[f'gamma_{k}'] for q in seg])) for k in ('z','iota','nu')}
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


# ------------------------------------------------------------ aggregation
def _cells(val):
    cells={}
    for m in NULLS:
        for s in STATS:
            al=[r['models'][m][s]['alarm'] for r in val if r['models'][m][s]['p_rank'] is not None]
            k=int(sum(al));n=len(al)
            cells[f'{m}|{s}']={'alarms':k,'n':n,'rate':k/n if n else None,'wilson95':wilson(k,n),
                               'elevated':bool(n and wilson(k,n)[0]>CORRECT_FAMILY_LEVEL)}
    return cells


def _pair(val,a,b,s):
    xa=[];xb=[]
    for r in val:
        pa=r['models'][a][s];pb=r['models'][b][s]
        if pa['p_rank'] is not None and pb['p_rank'] is not None:xa.append(pa['alarm']);xb.append(pb['alarm'])
    return mcnemar_exact(xa,xb)


def _verdict(val,cells):
    worse={s:_pair(val,'HXACT','BL',s) for s in STATS}
    for v in worse.values():v['significant']=bool(v['p_one_sided']<ALPHA_EQUIV)
    full=all(not cells[f'HXACT|{s}']['elevated'] for s in STATS)
    equiv=all(not v['significant'] for v in worse.values())
    return worse,('ADEQUACAO PLENA (nenhuma estatistica elevada)' if full else
                  'EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)' if equiv else 'NAO FECHA A LACUNA')


def aggregate(rows,n_expected):
    if sorted(r['origin'] for r in rows)!=list(range(n_expected)):raise ValueError('Missing or duplicate origins')
    val=[r for r in rows if r.get('status')=='valid']
    odd=[r for r in val if r['origin']%2==1]
    cells=_cells(val);cells_odd=_cells(odd)
    primary={s:_pair(odd,'HXLOC','HXACT',s) for s in TARGET}
    for v in primary.values():v['significant']=bool(v['p_one_sided']<ALPHA_PRIMARY)
    mech={}
    for key,sign in (('iota','negative'),('z','positive')):
        g=np.array([r['fit_diagnostics']['gamma_median'][key] for r in odd])
        k=int(np.sum(g<0)) if sign=='negative' else int(np.sum(g>0))
        p=float(binomtest(k,len(g),.5,alternative='greater').pvalue)
        mech[f'gamma_{key}']={'predicted':sign,'median':float(np.median(g)),'q25':float(np.quantile(g,.25)),'q75':float(np.quantile(g,.75)),
                              'k_in_predicted_direction':k,'n':len(g),'sign_p':p,'supported':bool(p<.05)}
    gnu=np.array([r['fit_diagnostics']['gamma_median']['nu'] for r in odd])
    mech['gamma_nu_descriptive']={'median':float(np.median(gnu)),'frac_positive':float(np.mean(gnu>0))}
    worse,verdict=_verdict(val,cells)
    worse_odd,verdict_odd=_verdict(odd,cells_odd)
    alerts={}
    for s in ALREADY_OK:
        a=_pair(val,'HXACT','HXLOC',s);b=_pair(val,'HXLOC','HXACT',s)
        p2=min(1.,2*min(a['p_one_sided'],b['p_one_sided']))
        alerts[s]={'only_HXACT':a['x_only'],'only_HXLOC':a['y_only'],'p_two_sided':p2,
                   'HXACT_worse':bool(p2<ALPHA_EQUIV and a['x_only']>a['y_only'])}
    return {'n_valid':len(val),'n_odd':len(odd),'status':{s:sum(1 for r in rows if r.get('status')==s) for s in {r.get('status') for r in rows}},
            'cells':cells,'cells_odd':cells_odd,'primary_odd_vs_HXLOC':primary,'mechanism_odd':mech,
            'HXACT_worse_than_BL':worse,'verdict':verdict,'HXACT_worse_than_BL_odd':worse_odd,'verdict_odd':verdict_odd,
            'not_worse_alerts':alerts}


def report(a):
    pct=lambda x:'—' if x is None else f'{100*x:.0f}%'
    L=['# SGV-M28 — A atividade governa a escala (resultados)','',
       f"Origens válidas: {a['n_valid']} ({a['status']}); ímpares (teste): {a['n_odd']}. Agregado por `experiments/m28_atividade_escala.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M28_20261011.md`.",'',
       '**Todas as origens:**','','| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:L.append(f'| {m} | '+' | '.join(pct(a['cells'][f'{m}|{s}']['rate']) for s in STATS)+' |')
    L+=['','**Só ímpares (teste):**','','| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:L.append(f'| {m} | '+' | '.join(pct(a['cells_odd'][f'{m}|{s}']['rate']) for s in STATS)+' |')
    L+=['','**Mecanismo (ímpares, teste do sinal unilateral):**','']
    for k,v in a['mechanism_odd'].items():L.append(f'- {k}: '+json.dumps(v,ensure_ascii=False))
    L+=['','**Primário (ímpares, HXLOC → HXACT, McNemar unilateral, α=0,025):**','']
    for s,v in a['primary_odd_vs_HXLOC'].items():
        L.append(f"- {s}: só HXLOC {v['x_only']}, só HXACT {v['y_only']}, p={v['p_one_sided']:.2g} → {'significativo' if v['significant'] else 'n.s.'}")
    L+=['','**HXACT pior que BL? (84 origens, α=0,05/12):**','']
    for s,v in a['HXACT_worse_than_BL'].items():
        L.append(f"- {s}: só HXACT {v['x_only']}, só BL {v['y_only']}, p={v['p_one_sided']:.2g}{' **(pior)**' if v['significant'] else ''}")
    L+=['',f"**Veredito pré-registrado (84): {a['verdict']}**",f"Veredito só nas ímpares: {a['verdict_odd']}",'',
        '**Não piorar (HXACT × HXLOC, bilateral, α=0,05/12):**','']
    for s,v in a['not_worse_alerts'].items():
        L.append(f"- {s}: só HXACT {v['only_HXACT']}, só HXLOC {v['only_HXLOC']}, p={v['p_two_sided']:.2g}{' **ALERTA**' if v['HXACT_worse'] else ''}")
    return '\n'.join(L)


def write(obj,name):
    p=ROOT/'reports'/'m28'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n');return p


def run_shard(shard):
    df,starts=load(INTERVAL)
    ks=range(shard*PER_SHARD,min(len(starts),(shard+1)*PER_SHARD))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],k) for k in ks]
    write({'status':'M28_SHARD','shard':shard,'n_origins_total':len(starts),'origins':rows},f'shard_{shard:02d}.json')
    print(json.dumps({'shard':shard,'n':len(rows)}))


def run_pilot():
    df,starts=load(INTERVAL)
    r=run_origin(df,starts[0],0,refs=2)
    bad=[] if r.get('status')=='valid' else [r.get('status'),r.get('error')]
    if not bad:
        for m,v in r['models'].items():
            for s in STATS:
                if s!='m11' and any(x is None for x in v['references'][s]):bad.append((m,s))
    write({'status':'M28_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad}))
    if bad:raise RuntimeError('Pilot failed')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('pilot','shard','aggregate'),required=True)
    ap.add_argument('--shard',type=int);ap.add_argument('--shards-dir',default=str(ROOT/'reports'/'m28'/'_dl'))
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    elif a.mode=='shard':run_shard(a.shard)
    else:
        n=EXPECTED_ORIGINS[INTERVAL];rows=[]
        for s in range((n+PER_SHARD-1)//PER_SHARD):
            d=json.loads((Path(a.shards_dir)/f'shard_{s:02d}.json').read_text())
            if d.get('shard')!=s or d.get('n_origins_total')!=n:raise ValueError('bad shard')
            rows+=d['origins']
        agg=aggregate(rows,n);write(agg,'SGV_M28_AGREGADO.json')
        md=report(agg);(ROOT/'reports'/'m28'/'SGV_M28_RESULTADOS.md').write_text(md+'\n');print(md)


if __name__=='__main__':main()
