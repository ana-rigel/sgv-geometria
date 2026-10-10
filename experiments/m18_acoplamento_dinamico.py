#!/usr/bin/env python3
"""SGV-M18: is the residual (after M17's two-scale Markov) dynamic COUPLING
between (z, iota, nu), or LONG-RANGE temporal dependence?

2x2 factorial on top of M17's best family (two-scale Markov, "MS"):

                        coupling static        coupling dynamic (DCC)
  no long-range memory  MS                     MSDCC
  long-range memory     MSLM                   MSDCCLM

* DCC: inside every (slow, fast) state the emissions are whitened by the
  state's own covariance; the whitened innovations get a DCC(1,1) correlation
  R_t (Q_t=(1-a-b)I + a e e' + b Q_{t-1}), with (a,b) fitted by quasi-ML on the
  prefix. a=b=0 recovers MS exactly.
* LM: nu is split into a slow continuous part d_t (trailing mean minus its
  slow-regime mean) and the rest; the model is fitted on the rest, and each
  simulated window receives a contiguous block of the REAL prefix's slow
  regime sequence and d_t -- so any long-range dependence of the activity
  level (up to the prefix span) is kept, not modelled.
* References: BL (circular blocks of real prefix rows, L=500 on 1m, 168 on 1h)
  and N3 (M12), descriptive only.

Same origins, rulers, 39 references and alarm rule as M16/M17.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates
from experiments.precisao_formas_3d import gaussianize_three
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m5_validacao_conjunta_sf1 import WINDOW
from experiments.m12_nulos_regimes_temporais import PREFIX,null_paths
from experiments.m13_calibracao_alarmes_regimes import mc_rank,wilson
from experiments.m15_forma_persistencia_comparadores import all_stats,mcnemar_exact,STATS
from experiments.m16_trio_btc_exploratorio import load,EXPECTED_ORIGINS,CORRECT_FAMILY_LEVEL
from experiments.m17_tipo_de_memoria import fit_hmm,runs,SMOOTH,BURN

BASE_SEED=2026101018
REFS=39
INTERVALS=('1m','1h')
INTERVAL_ID={'1m':1,'1h':2}
PER_SHARD={'1m':2,'1h':3}
NULLS=('MS','MSDCC','MSLM','MSDCCLM','BL','N3')
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
LONG_BLOCK={'1m':500,'1h':168}
CONTRASTS=[  # (name, a, b, ruler): one-sided McNemar, H1 = a alarms more than b
    ('D1_acoplamento_frcov','MS','MSDCC','fr_cov'),
    ('D1_acoplamento_energy','MS','MSDCC','energy'),
    ('D2_memoria_longa_frcov','MS','MSLM','fr_cov'),
    ('D2_memoria_longa_energy','MS','MSLM','energy'),
]
ALPHA_CONTRAST=.05/len(CONTRASTS)


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


def n_shards(n,interval):return (n+PER_SHARD[interval]-1)//PER_SHARD[interval]


# ------------------------------------------------------------------- DCC
def _norm(Q):
    d=1/np.sqrt(np.diag(Q));return Q*d[:,None]*d[None,:]


def dcc_nll(params,e):
    a,b=params
    if a<0 or b<0 or a+b>=.999:return 1e12
    Q=np.eye(3);nll=0.
    for t in range(1,len(e)):
        Q=(1-a-b)*np.eye(3)+a*np.outer(e[t-1],e[t-1])+b*Q
        R=_norm(Q)
        sign,ld=np.linalg.slogdet(R)
        if sign<=0:return 1e12
        nll+=.5*(ld+e[t]@np.linalg.solve(R,e[t])-e[t]@e[t])
    return float(nll)


def fit_dcc(e):
    """Quasi-ML DCC(1,1) on whitened innovations; returns (a,b,gain in nll vs static)."""
    e=np.asarray(e,float)
    best=None
    for x0 in ((.02,.90),(.05,.80),(.01,.97)):
        r=minimize(dcc_nll,x0,args=(e,),method='Nelder-Mead',
                   options={'xatol':1e-3,'fatol':1e-2,'maxiter':120})
        if best is None or r.fun<best.fun:best=r
    a,b=[float(v) for v in best.x]
    if a<0 or b<0 or a+b>=.999:a,b=0.,0.
    return a,b,float(dcc_nll((0.,0.),e)-best.fun)


def dcc_innovations(rng,n,a,b):
    out=np.empty((n,3));Q=np.eye(3);prev=np.zeros(3)
    for t in range(n):
        Q=(1-a-b)*np.eye(3)+a*np.outer(prev,prev)+b*Q
        R=_norm(Q)
        prev=np.linalg.cholesky(R)@rng.standard_normal(3)
        out[t]=prev
    return out


# --------------------------------------------------------------- 2-scale
def two_scale_plus(x,interval,seed,dcc=False,lm=False):
    """M17 two-scale Markov, optionally with DCC coupling and/or real slow block (LM)."""
    w=SMOOTH[interval]
    sm=np.convolve(x[:,2],np.ones(w)/w,'full')[:len(x)]
    keep=np.arange(len(x))>=w-1
    xs=x[keep].copy();ss=sm[keep]
    slow_h,_=fit_hmm(ss.reshape(-1,1),2,seed)
    order=np.argsort(slow_h.means_.ravel())
    slow=np.argsort(order)[slow_h.predict(ss.reshape(-1,1))]
    d=np.zeros(len(xs))
    if lm:
        for s in (0,1):d[slow==s]=ss[slow==s]-ss[slow==s].mean()
        xs[:,2]-=d
    P=np.ones((2,2))
    for u,v in zip(slow[:-1],slow[1:]):P[u,v]+=1
    P/=P.sum(axis=1,keepdims=True)
    occ=np.bincount(slow,minlength=2)/len(slow)
    fast={};chol={};means={};fstate={};diag={'slow_self_transition':[float(P[0,0]),float(P[1,1])]}
    for s in (0,1):
        rows=xs[slow==s]
        if len(rows)<300:raise ValueError(f'slow regime {s} has <300 rows')
        fast[s],diag[f'fast{s}']=fit_hmm(rows,2,seed+101*(s+1))
        chol[s]=[np.linalg.cholesky(c) for c in fast[s].covars_]
        means[s]=fast[s].means_
        fstate[s]=fast[s].predict(rows)
    a=b=0.
    if dcc:
        e=np.empty_like(xs);idx={0:0,1:0}
        fs=np.empty(len(xs),int)
        for s in (0,1):fs[slow==s]=fstate[s]
        for t in range(len(xs)):
            s=slow[t];f=fs[t]
            e[t]=np.linalg.solve(chol[s][f],xs[t]-means[s][f])
        a,b,gain=fit_dcc(e)
        diag['dcc']={'a':a,'b':b,'nll_gain_vs_static':gain}

    def fast_states(rng,s,dlen):
        h=fast[s]
        st=np.empty(dlen,int);c=int(rng.choice(2,p=h.startprob_))
        for t in range(dlen):
            st[t]=c;c=int(rng.choice(2,p=h.transmat_[c]))
        return st

    def emit(rng,slow_seq):
        n=len(slow_seq);out=np.empty((n,3))
        eps=dcc_innovations(rng,n,a,b) if dcc else rng.standard_normal((n,3))
        lab,ln=runs(np.asarray(slow_seq));t=0
        for s,dl in zip(lab,ln):
            s=int(s);fs_=fast_states(rng,s,int(dl))
            for f in (0,1):
                m=np.flatnonzero(fs_==f)+t
                if len(m):out[m]=means[s][f]+eps[m]@chol[s][f].T
            t+=dl
        return out

    def sample(rng,n):
        if lm:
            total=n
            start=int(rng.integers(0,len(slow)))
            idx=(start+np.arange(total))%len(slow)
            seq=slow[idx];y=emit(rng,seq);y[:,2]+=d[idx]
            return y
        total=n+BURN;seq=np.empty(total,int);s=int(rng.choice(2,p=occ))
        for t in range(total):
            seq[t]=s;s=int(rng.choice(2,p=P[s]))
        return emit(rng,seq)[-n:]
    return sample,diag


def build_nulls(prefix_df,interval,seed):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ok=np.isfinite(pre).all(axis=1)
    first=int(np.flatnonzero(ok)[0]) if ok.any() else len(ok)
    if len(ok)-first<2000 or not ok[first:].all():raise ValueError('Prefix coordinates invalid')
    raw=pre[first:];ns=gaussianize_three(raw,raw)
    samplers={};diag={}
    for name,dcc,lm,k in (('MS',False,False,1),('MSDCC',True,False,2),('MSLM',False,True,3),('MSDCCLM',True,True,4)):
        samplers[name],diag[name]=two_scale_plus(ns,interval,seed+50,dcc=dcc,lm=lm)
    L=LONG_BLOCK[interval]
    samplers['BL']=lambda rng,n:circular_blocks(raw,rng,L)[:n]
    draw,_,_=null_paths(prefix_df,interval,seed+99)
    samplers['N3']=lambda rng,n,draw=draw:draw('N3_regime_long',int(rng.integers(0,10**6)))[0]
    return samplers,diag


# ------------------------------------------------------------------ origin
def run_origin(df,start,interval,k,refs=REFS,stats_fn=all_stats):
    pre=PREFIX[interval];w=WINDOW[interval]
    prefix=df.iloc[start-pre:start].copy();future=df.iloc[start:start+w].copy()
    actual=flow_coordinates(pd.concat([prefix,future],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-w:]
    item={'interval':interval,'origin':int(k),'window_start_ms':int(future.timestamp.iloc[0]),
          'window_end_ms':int(future.timestamp.iloc[-1]),'fit_uses_prefix_only':True,'models':{}}
    if not np.isfinite(actual).all():item['status']='invalid_observed_coordinates';return item
    obs=stats_fn(actual,seed_int(INTERVAL_ID[interval],k,1));item['observed']=obs
    try:
        samplers,diag=build_nulls(prefix,interval,seed_int(INTERVAL_ID[interval],k,2))
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
        item['status']='fit_failed';item['error']=str(e);return item
    item['status']='valid';item['fit_diagnostics']=diag
    for name in NULLS:
        ref={s:[] for s in STATS};fails=[]
        for j in range(refs):
            try:
                rng=np.random.default_rng(seed_int(INTERVAL_ID[interval],k,3,NULL_ID[name],j))
                sim=samplers[name](rng,w)
                if sim.shape!=(w,3) or not np.isfinite(sim).all():raise ValueError('bad simulated window')
                r=stats_fn(sim,seed_int(INTERVAL_ID[interval],k,4,NULL_ID[name],j))
            except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
                r={s:None for s in STATS};fails.append({'ref':j,'error':str(e)})
            for s in STATS:ref[s].append(r[s])
        rec={'references':ref,'failures':fails}
        for s in STATS:
            vals=ref[s]
            if obs[s] is None or any(v is None for v in vals):
                rec[s]={'valid':False,'n_ref_valid':int(sum(v is not None for v in vals))};continue
            p=mc_rank(obs[s],vals,min_reference=refs)
            rec[s]={'valid':True,'p_rank':p,'rank_position':int(round(p*(refs+1))),'alarm':bool(p<=.05)}
        item['models'][name]=rec
    return item


# --------------------------------------------------------------- aggregate
def cell(rows,iv,model,stat):
    ok=[r['models'][model][stat] for r in rows if r['interval']==iv and r.get('status')=='valid'
        and r['models'].get(model,{}).get(stat,{}).get('valid')]
    n=len(ok);al=sum(o['alarm'] for o in ok)
    return {'n_valid':n,'alarms':int(al),'alarm_rate':al/n if n else None,'wilson95':wilson(al,n),
            'mean_pit':float(np.mean([o['p_rank'] for o in ok])) if n else None}


def paired(rows,iv,a,b,stat):
    xa=[];xb=[]
    for r in rows:
        if r['interval']!=iv or r.get('status')!='valid':continue
        ma=r['models'][a].get(stat,{});mb=r['models'][b].get(stat,{})
        if ma.get('valid') and mb.get('valid'):xa.append(ma['alarm']);xb.append(mb['alarm'])
    return mcnemar_exact(xa,xb)


def aggregate(rows,expected):
    for iv,n in expected.items():
        ids=sorted(r['origin'] for r in rows if r['interval']==iv)
        if ids!=list(range(n)):raise ValueError(f'Missing or duplicate origins for {iv}')
    out={'cells':{},'closes_gap':{},'contrasts':{},'status':{},'diagnostics':{}}
    for iv in expected:
        out['status'][iv]={s:sum(1 for r in rows if r['interval']==iv and r.get('status')==s)
                           for s in {r.get('status') for r in rows if r['interval']==iv}}
        for m in NULLS:
            cs={s:cell(rows,iv,m,s) for s in STATS}
            for s in STATS:out['cells'][f'{iv}|{m}|{s}']=cs[s]
            out['closes_gap'][f'{iv}|{m}']=all(c['wilson95'] is not None and c['wilson95'][0]<=CORRECT_FAMILY_LEVEL
                                               for c in cs.values())
        for name,a,b,st in CONTRASTS:
            r=paired(rows,iv,a,b,st);r.update({'a':a,'b':b,'ruler':st,'alpha':ALPHA_CONTRAST,
                                               'significant':bool(r['p_one_sided']<ALPHA_CONTRAST)})
            out['contrasts'][f'{iv}|{name}']=r
        val=[r for r in rows if r['interval']==iv and r.get('status')=='valid']
        q=lambda v:[float(x) for x in np.quantile(v,[.25,.5,.75])] if v else None
        out['diagnostics'][iv]={
            'dcc_a_quartiles':q([r['fit_diagnostics']['MSDCC']['dcc']['a'] for r in val]),
            'dcc_b_quartiles':q([r['fit_diagnostics']['MSDCC']['dcc']['b'] for r in val]),
            'dcc_nll_gain_quartiles':q([r['fit_diagnostics']['MSDCC']['dcc']['nll_gain_vs_static'] for r in val]),
            'dcc_gain_gt_3_fraction':float(np.mean([r['fit_diagnostics']['MSDCC']['dcc']['nll_gain_vs_static']>3 for r in val])) if val else None}
    return out


# ---------------------------------------------------------------------- I/O
def write(obj,name):
    p=ROOT/'reports'/'m18'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n');return p


def run_pilot():
    bad=[]
    for iv in INTERVALS:
        df,starts=load(iv)
        r=run_origin(df,starts[0],iv,0,refs=2)
        if r.get('status')!='valid':bad.append((iv,r.get('status'),r.get('error')));continue
        for m,v in r['models'].items():
            for s in STATS:
                if any(x is None for x in v['references'][s]):bad.append((iv,m,s,v['failures'][:1]))
    write({'status':'M18_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad},default=str))
    if bad:raise RuntimeError('Pilot failed')


def run_shard(iv,shard):
    df,starts=load(iv);per=PER_SHARD[iv]
    ks=range(shard*per,min(len(starts),(shard+1)*per))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],iv,k) for k in ks]
    write({'status':'M18_SHARD','interval':iv,'shard':shard,'n_origins_total':len(starts),
           'confirmatory_opened':False,'origins':rows},f'shard_{iv}_{shard:03d}.json')
    print(json.dumps({'interval':iv,'shard':shard,'n':len(rows)}))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('pilot','shard'),required=True)
    ap.add_argument('--interval',choices=INTERVALS);ap.add_argument('--shard',type=int)
    a=ap.parse_args()
    run_pilot() if a.mode=='pilot' else run_shard(a.interval,a.shard)


if __name__=='__main__':main()
