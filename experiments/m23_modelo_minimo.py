#!/usr/bin/env python3
"""SGV-M23: a minimal explicit model of BTC 1m -- two-scale regimes with
autoregression (VAR(1) per slow regime) and conditional volatility (GARCH(1,1)
per whitened coordinate) -- with and without the real slow block (LM, M18).

Does it close the gap that every parametric null left open (M16-M18, M21b)?
Audited with the three rulers (M11, Fisher-Rao, energy) AND the lag-dependence
statistics of M21b (lin/vol/HSIC at lags 1, 5, 30). References: MSDCCLM (best
parametric of M18) and BL (real 8h blocks). 39 references, conservative rank.
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
from experiments.m15_forma_persistencia_comparadores import all_stats,mcnemar_exact
from experiments.m16_trio_btc_exploratorio import load,EXPECTED_ORIGINS,CORRECT_FAMILY_LEVEL
from experiments.m17_tipo_de_memoria import fit_hmm,SMOOTH,BURN
from experiments.m18_acoplamento_dinamico import two_scale_plus,LONG_BLOCK
from experiments.m21_posto_conservador import conservative_rank
from experiments.m21b_dependencia_btc import dep_stats,STATS as DEP_STATS

BASE_SEED=2026101123
REFS=39
INTERVAL='1m'
NULLS=('MSAR','MSARLM','MSDCCLM','BL')
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
RULERS=('m11','fr_cov','energy')
STATS=RULERS+DEP_STATS
PER_SHARD=2
ALPHA_PRIMARY=.05/3
ALPHA_EQUIV=.05/len(STATS)


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


# ----------------------------------------------------------------- GARCH
def garch_nll(p,u2):
    a,b=p
    if a<0 or b<0 or a+b>=.999:return 1e12
    h=lfilter([0.,a],[1.,-b],u2)+(1-a-b)/(1-b)          # unit unconditional variance
    h=np.maximum(h,1e-6)
    return float(.5*np.sum(np.log(h)+u2/h))


def fit_garch(u):
    u2=np.asarray(u,float)**2;best=None
    for x0 in ((.05,.90),(.10,.80),(.02,.97)):
        r=minimize(garch_nll,x0,args=(u2,),method='Nelder-Mead',options={'xatol':1e-4,'fatol':1e-3,'maxiter':300})
        if best is None or r.fun<best.fun:best=r
    a,b=[float(v) for v in best.x]
    if a<0 or b<0 or a+b>=.999:a,b=0.,0.
    return a,b


# ------------------------------------------------------------- the model
def slow_layer(x,seed):
    w=SMOOTH[INTERVAL]
    sm=np.convolve(x[:,2],np.ones(w)/w,'full')[:len(x)]
    keep=np.arange(len(x))>=w-1
    xs=x[keep].copy();ss=sm[keep]
    h,_=fit_hmm(ss.reshape(-1,1),2,seed)
    order=np.argsort(h.means_.ravel())
    slow=np.argsort(order)[h.predict(ss.reshape(-1,1))]
    return xs,ss,slow


def fit_msar(x,seed,lm=False):
    xs,ss,slow=slow_layer(x,seed)
    d=np.zeros(len(xs))
    if lm:
        for s in (0,1):d[slow==s]=ss[slow==s]-ss[slow==s].mean()
        xs[:,2]-=d
    P=np.ones((2,2))
    for u,v in zip(slow[:-1],slow[1:]):P[u,v]+=1
    P/=P.sum(axis=1,keepdims=True)
    occ=np.bincount(slow,minlength=2)/len(slow)
    c={};A={};L={};res_t=[];res_u=[];diag={}
    t_all=np.arange(1,len(xs))
    for s in (0,1):
        idx=t_all[(slow[1:]==s)&(slow[:-1]==s)]
        if len(idx)<300:raise ValueError(f'regime {s}: <300 within-regime pairs')
        X=np.column_stack([np.ones(len(idx)),xs[idx-1]]);Y=xs[idx]
        beta=np.linalg.lstsq(X,Y,rcond=None)[0]
        c[s]=beta[0];As=beta[1:].T
        rho=float(max(abs(np.linalg.eigvals(As))))
        if rho>=.99:As=As*(.99/rho)
        A[s]=As
        e=Y-(c[s]+xs[idx-1]@As.T)
        S=np.cov(e,rowvar=False)
        L[s]=np.linalg.cholesky(S)
        u=np.linalg.solve(L[s],e.T).T
        res_t.append(idx);res_u.append(u)
        diag[f'regime{s}']={'spectral_radius':rho,'n_pairs':int(len(idx))}
    order=np.argsort(np.concatenate(res_t));U=np.concatenate(res_u)[order]
    garch=[fit_garch(U[:,j]) for j in range(3)]
    diag['garch']=[{'alpha':a,'beta':b} for a,b in garch]
    diag['slow_self_transition']=[float(P[0,0]),float(P[1,1])]
    ga=np.array([g[0] for g in garch]);gb=np.array([g[1] for g in garch])

    def simulate(rng,seq,dblock=None):
        n=len(seq);out=np.empty((n,3))
        s0=int(seq[0]);xprev=np.linalg.solve(np.eye(3)-A[s0],c[s0])
        h=np.ones(3);uprev=np.zeros(3)
        for t in range(n):
            s=int(seq[t])
            h=(1-ga-gb)+ga*uprev**2+gb*h
            uprev=np.sqrt(h)*rng.standard_normal(3)
            xprev=c[s]+A[s]@xprev+L[s]@uprev
            out[t]=xprev
        if dblock is not None:out[:,2]+=dblock
        return out

    def sample(rng,n):
        if lm:
            start=int(rng.integers(0,len(slow)));idx=(start+np.arange(n))%len(slow)
            return simulate(rng,slow[idx],d[idx])
        total=n+BURN;seq=np.empty(total,int);s=int(rng.choice(2,p=occ))
        for t in range(total):
            seq[t]=s;s=int(rng.choice(2,p=P[s]))
        return simulate(rng,seq)[-n:]
    return sample,diag


def build(prefix_df,seed):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ok=np.isfinite(pre).all(axis=1)
    raw=pre[int(np.flatnonzero(ok)[0]):]
    if len(raw)<2000 or not np.isfinite(raw).all():raise ValueError('Prefix coordinates invalid')
    ns=gaussianize_three(raw,raw)
    s={};diag={}
    s['MSAR'],diag['MSAR']=fit_msar(ns,seed+50)
    s['MSARLM'],diag['MSARLM']=fit_msar(ns,seed+50,lm=True)
    s['MSDCCLM'],_=two_scale_plus(ns,INTERVAL,seed+50,dcc=True,lm=True)
    s['BL']=lambda rng,n:circular_blocks(raw,rng,LONG_BLOCK[INTERVAL])[:n]
    return s,diag


def full_stats(x,seed):
    r=all_stats(x,seed);d=dep_stats(x)
    return {**{k:r[k] for k in RULERS},**d}


# ------------------------------------------------------------------ origin
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
            p=conservative_rank(obs[s],ref[s])
            rec[s]={'p_rank':p,'alarm':bool(p is not None and p<=.05)}
        item['models'][name]=rec
    return item


# --------------------------------------------------------------- aggregate
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
    primary={s:pair('MSDCCLM','MSARLM',s) for s in ('lin_1','vol_1','hsic_1')}
    for v in primary.values():v['significant']=bool(v['p_one_sided']<ALPHA_PRIMARY)
    worse_than_bl={s:pair('MSARLM','BL',s) for s in STATS}
    for v in worse_than_bl.values():v['significant']=bool(v['p_one_sided']<ALPHA_EQUIV)
    lm_effect={s:pair('MSAR','MSARLM',s) for s in STATS}
    full=all(not cells[f'MSARLM|{s}']['elevated'] for s in STATS)
    equiv=all(not v['significant'] for v in worse_than_bl.values())
    verdict=('ADEQUACAO PLENA (nenhuma estatistica elevada)' if full else
             'EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)' if equiv else
             'NAO FECHA A LACUNA')
    q=lambda v:[float(x) for x in np.quantile(v,[.25,.5,.75])] if v else None
    diagq={'garch_alpha_beta_median':[[float(np.median([r['fit_diagnostics']['MSARLM']['garch'][j][k] for r in val])) for k in ('alpha','beta')] for j in range(3)],
           'var_spectral_radius_quartiles':q([r['fit_diagnostics']['MSARLM'][f'regime{s}']['spectral_radius'] for r in val for s in (0,1)])}
    return {'n_valid':len(val),'status':{s:sum(1 for r in rows if r.get('status')==s) for s in {r.get('status') for r in rows}},
            'cells':cells,'primary_improvement_vs_MSDCCLM':primary,'MSARLM_worse_than_BL':worse_than_bl,
            'lm_effect_MSAR_vs_MSARLM':lm_effect,'verdict':verdict,'diagnostics':diagq}


def report(a):
    pct=lambda x:'—' if x is None else f'{100*x:.0f}%'
    L=['# SGV-M23 — Modelo mínimo do BTC 1m (resultados)','',
       f"Origens válidas: {a['n_valid']} ({a['status']}). Agregado por `experiments/m23_modelo_minimo.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M23_20261011.md`.",'',
       '| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:L.append(f'| {m} | '+' | '.join(pct(a['cells'][f'{m}|{s}']['rate']) for s in STATS)+' |')
    L+=['','**Primário (MSDCCLM → MSARLM, McNemar unilateral, α=0,0167):**','']
    for s,v in a['primary_improvement_vs_MSDCCLM'].items():
        L.append(f"- {s}: só MSDCCLM {v['x_only']}, só MSARLM {v['y_only']}, p={v['p_one_sided']:.2g} → {'melhora significativa' if v['significant'] else 'n.s.'}")
    L+=['','**MSARLM pior que BL? (α=0,05/12 por estatística)**','']
    for s,v in a['MSARLM_worse_than_BL'].items():
        L.append(f"- {s}: só MSARLM {v['x_only']}, só BL {v['y_only']}, p={v['p_one_sided']:.2g}{' **(pior)**' if v['significant'] else ''}")
    L+=['',f"**Veredito pré-registrado: {a['verdict']}**",'','Diagnósticos: '+json.dumps(a['diagnostics'],ensure_ascii=False)]
    return '\n'.join(L)


def write(obj,name):
    p=ROOT/'reports'/'m23'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n');return p


def run_shard(shard):
    df,starts=load(INTERVAL)
    ks=range(shard*PER_SHARD,min(len(starts),(shard+1)*PER_SHARD))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],k) for k in ks]
    write({'status':'M23_SHARD','shard':shard,'n_origins_total':len(starts),'origins':rows},f'shard_{shard:02d}.json')
    print(json.dumps({'shard':shard,'n':len(rows)}))


def run_pilot():
    df,starts=load(INTERVAL)
    r=run_origin(df,starts[0],0,refs=2)
    bad=[] if r.get('status')=='valid' else [r.get('status'),r.get('error')]
    if not bad:
        for m,v in r['models'].items():
            for s in STATS:
                if s!='m11' and any(x is None for x in v['references'][s]):bad.append((m,s))
    write({'status':'M23_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad}))
    if bad:raise RuntimeError('Pilot failed')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('pilot','shard','aggregate'),required=True)
    ap.add_argument('--shard',type=int);ap.add_argument('--shards-dir',default=str(ROOT/'reports'/'m23'/'_dl'))
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    elif a.mode=='shard':run_shard(a.shard)
    else:
        n=EXPECTED_ORIGINS[INTERVAL];rows=[]
        for s in range((n+PER_SHARD-1)//PER_SHARD):
            d=json.loads((Path(a.shards_dir)/f'shard_{s:02d}.json').read_text())
            if d.get('shard')!=s or d.get('n_origins_total')!=n:raise ValueError('bad shard')
            rows+=d['origins']
        agg=aggregate(rows,n);write(agg,'SGV_M23_AGREGADO.json')
        md=report(agg);(ROOT/'reports'/'m23'/'SGV_M23_RESULTADOS.md').write_text(md+'\n');print(md)


if __name__=='__main__':main()
