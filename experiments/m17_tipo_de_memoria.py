#!/usr/bin/env python3
"""SGV-M17: what kind of memory does BTC have? Markov (1 vs several time
scales), semi-Markov (regimes that age), or calendar clocks?

Same exploratory origins, 39 references and three rulers as M16. Seven nulls,
all fitted ONLY on each origin's prefix coordinates:

  H2, H4         plain Gaussian HMM, 2/4 states, full covariance (Markov; EM picks
                 the time scales -- in development it picked only fast ones)
  MS             TWO-SCALE Markov: a slow 2-state activity regime decoded from a
                 trailing mean of nu (60 bars on 1m, 24 on 1h) with geometric
                 durations, and inside each slow regime its own fast 2-state HMM
  MSSM           same, but slow-regime durations bootstrapped from the prefix's
                 decoded runs (regimes that age: semi-Markov at the slow scale)
  MSR, MSSMR     MS / MSSM fitted on de-seasonalized nu, with the prefix clock
                 profile re-added at the future timestamps (+ calendar clock:
                 hour-of-day on 1m, hour-of-week on 1h)
  N3             M12 regime-clock long blocks (anchor from M16)

HMM nulls live in prefix normal-score space; the measurement re-gaussianizes
every window by ranks (split_historical), so per-marginal monotone maps do not
matter -- dependence and dynamics do.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates
from experiments.precisao_formas_3d import gaussianize_three
from experiments.m5_validacao_conjunta_sf1 import WINDOW,STEP
from experiments.m12_nulos_regimes_temporais import PREFIX,null_paths
from experiments.m13_calibracao_alarmes_regimes import mc_rank,wilson
from experiments.m15_forma_persistencia_comparadores import all_stats,mcnemar_exact,STATS
from experiments.m16_trio_btc_exploratorio import load,EXPECTED_ORIGINS,CORRECT_FAMILY_LEVEL

BASE_SEED=2026101017
REFS=39
INTERVALS=('1m','1h')
INTERVAL_ID={'1m':1,'1h':2}
PER_SHARD={'1m':2,'1h':3}
NULLS=('H2','H4','MS','MSSM','MSR','MSSMR','N3')
SMOOTH={'1m':60,'1h':24}
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
BURN=500
CONTRASTS=[  # (name, a, b): one-sided, energy ruler, H1 = a alarms more than b
    ('C1_escala_lenta','H4','MS'),
    ('C2_envelhecimento','MS','MSSM'),
    ('C3a_relogio_MS','MS','MSR'),
    ('C3b_relogio_MSSM','MSSM','MSSMR'),
    ('C4_mais_estados','H2','H4'),
]
ALPHA_CONTRAST=.05/len(CONTRASTS)


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


def n_shards(n,interval):return (n+PER_SHARD[interval]-1)//PER_SHARD[interval]


# ------------------------------------------------------------------ clocks
def clock_bin(ts_ms,interval):
    h=np.asarray(ts_ms,dtype=np.int64)//3600000
    return (h%24).astype(int) if interval=='1m' else (h%168).astype(int)


def clock_profile(nu,ts,interval):
    nb=24 if interval=='1m' else 168
    b=clock_bin(ts,interval)
    cnt=np.bincount(b,minlength=nb)
    if cnt.min()==0:raise ValueError('Clock bin without prefix data')
    return np.bincount(b,weights=nu,minlength=nb)/cnt


# --------------------------------------------------------------- HMM nulls
def fit_hmm(x,k,seed,restarts=3):
    from hmmlearn.hmm import GaussianHMM
    best=None;bs=-np.inf;conv=False
    for r in range(restarts):
        try:
            h=GaussianHMM(n_components=k,covariance_type='full',n_iter=200,tol=1e-3,
                          min_covar=1e-3,random_state=int(seed+17*r))
            h.fit(x);s=float(h.score(x))
            if not np.isfinite(s) or not np.isfinite(h.transmat_).all():continue
            if any(min(np.linalg.eigvalsh(c))<=1e-7 for c in h.covars_):continue
            if s>bs:best,bs,conv=h,s,bool(h.monitor_.converged)
        except (ValueError,np.linalg.LinAlgError):continue
    if best is None:raise ValueError(f'HMM{k} failed on every restart')
    ev=np.sort(np.abs(np.linalg.eigvals(best.transmat_)))[::-1][1:]
    scales=[float(-1/np.log(v)) if 0<v<1 else None for v in ev]
    return best,{'k':k,'loglik':bs,'converged':conv,'time_scales_bars':scales,
                 'self_transition':[float(v) for v in np.diag(best.transmat_)]}


def hmm_sampler(h):
    def sample(rng,n):
        x,_=h.sample(n_samples=n+BURN,random_state=int(rng.integers(0,2**31-1)))
        return np.asarray(x[-n:],float)
    return sample


def runs(states):
    change=np.flatnonzero(np.diff(states)!=0)+1
    st=np.r_[0,change];en=np.r_[change,len(states)]
    return states[st],en-st


def two_scale(x,interval,seed):
    """Slow 2-state activity regime (from trailing mean of nu) x fast 2-state HMM per regime."""
    from hmmlearn.hmm import GaussianHMM
    w=SMOOTH[interval]
    sm=np.convolve(x[:,2],np.ones(w)/w,'full')[:len(x)]
    sm[:w-1]=np.nan
    keep=np.isfinite(sm);xs=x[keep];ss=sm[keep].reshape(-1,1)
    slow_h,_=fit_hmm(ss,2,seed)
    slow=slow_h.predict(ss)
    order=np.argsort(slow_h.means_.ravel());slow=np.argsort(order)[slow]   # 0 = calm, 1 = active
    labels,lens=runs(slow)
    inner=slice(1,len(labels)-1)
    pools={s:lens[inner][labels[inner]==s] for s in (0,1)}
    for s in (0,1):
        if len(pools[s])<3:raise ValueError(f'slow regime {s} has <3 complete runs')
    P=np.ones((2,2))
    for a,b in zip(slow[:-1],slow[1:]):P[a,b]+=1
    P/=P.sum(axis=1,keepdims=True)
    fast={};fdiag={}
    for s in (0,1):
        rows=xs[slow==s]
        if len(rows)<300:raise ValueError(f'slow regime {s} has <300 rows')
        fast[s],fdiag[str(s)]=fit_hmm(rows,2,seed+101*(s+1))
    occ=np.bincount(slow,minlength=2)/len(slow)
    def fill(rng,seq):
        out=np.empty((len(seq),3));lab,ln=runs(np.asarray(seq));t=0
        for s,d in zip(lab,ln):
            y,_=fast[int(s)].sample(n_samples=int(d),random_state=int(rng.integers(0,2**31-1)))
            out[t:t+d]=y;t+=d
        return out
    def markov(rng,n):
        total=n+BURN;seq=np.empty(total,int);s=int(rng.choice(2,p=occ))
        for t in range(total):
            seq[t]=s;s=int(rng.choice(2,p=P[s]))
        return fill(rng,seq)[-n:]
    def semi(rng,n):
        total=n+BURN;seq=[];s=int(rng.choice(2,p=occ))
        while len(seq)<total:
            seq+= [s]*int(rng.choice(pools[s]));s=1-s
        return fill(rng,np.array(seq[:total]))[-n:]
    dur={}
    for s in (0,1):
        L=pools[s].astype(float);m=L.mean();p=1/m;top=int(L.max())
        g=1-(1-p)**np.arange(1,top+1)
        e=np.searchsorted(np.sort(L),np.arange(1,top+1),side='right')/len(L)
        dur[str(s)]={'n_runs':int(len(L)),'mean_bars':float(m),'cv':float(L.std()/m),
                     'ks_vs_geometric':float(np.max(np.abs(e-g)))}
    return markov,semi,{'slow_self_transition':[float(P[0,0]),float(P[1,1])],
                        'slow_durations':dur,'fast':fdiag}


def build_nulls(prefix_df,interval,future_ts,seed):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ts=prefix_df.timestamp.to_numpy(np.int64)
    ok=np.isfinite(pre).all(axis=1)
    first=int(np.flatnonzero(ok)[0]) if ok.any() else len(ok)
    if len(ok)-first<2000 or not ok[first:].all():raise ValueError('Prefix coordinates invalid')
    raw=pre[first:];ts=ts[first:]
    ns=gaussianize_three(raw,raw)
    prof=clock_profile(ns[:,2],ts,interval)
    des=ns.copy();des[:,2]-=prof[clock_bin(ts,interval)]
    fut_clock=prof[clock_bin(future_ts,interval)]
    samplers={};diag={}
    for k in (2,4):
        h,d=fit_hmm(ns,k,seed+k);samplers[f'H{k}']=hmm_sampler(h);diag[f'H{k}']=d
    samplers['MS'],samplers['MSSM'],diag['MS']=two_scale(ns,interval,seed+50)
    msr,mssmr,diag['MSR']=two_scale(des,interval,seed+60)
    def with_clock(f):
        def s(rng,n):
            x=f(rng,n).copy();x[:,2]+=fut_clock[:n];return x
        return s
    samplers['MSR']=with_clock(msr);samplers['MSSMR']=with_clock(mssmr)
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
        samplers,diag=build_nulls(prefix,interval,future.timestamp.to_numpy(np.int64),
                                  seed_int(INTERVAL_ID[interval],k,2))
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
def cell(rows,interval,model,stat):
    ok=[r['models'][model][stat] for r in rows if r['interval']==interval and r.get('status')=='valid'
        and r['models'].get(model,{}).get(stat,{}).get('valid')]
    n=len(ok);al=sum(o['alarm'] for o in ok)
    return {'n_valid':n,'alarms':int(al),'alarm_rate':al/n if n else None,'wilson95':wilson(al,n),
            'mean_pit':float(np.mean([o['p_rank'] for o in ok])) if n else None}


def paired(rows,interval,a,b,stat='energy'):
    xa=[];xb=[]
    for r in rows:
        if r['interval']!=interval or r.get('status')!='valid':continue
        ma=r['models'][a].get(stat,{});mb=r['models'][b].get(stat,{})
        if ma.get('valid') and mb.get('valid'):xa.append(ma['alarm']);xb.append(mb['alarm'])
    return mcnemar_exact(xa,xb)


def closes_gap(cells):
    """M16 rule 'sem evidencia': every ruler's Wilson lower bound <= 7%."""
    return all(c['wilson95'] is not None and c['wilson95'][0]<=CORRECT_FAMILY_LEVEL for c in cells.values())


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
            out['closes_gap'][f'{iv}|{m}']=closes_gap(cs)
        for name,a,b in CONTRASTS:
            r=paired(rows,iv,a,b);r.update({'a':a,'b':b,'alpha':ALPHA_CONTRAST,
                                            'significant':bool(r['p_one_sided']<ALPHA_CONTRAST)})
            out['contrasts'][f'{iv}|{name}']=r
        val=[r for r in rows if r['interval']==iv and r.get('status')=='valid']
        sc=[x for r in val for x in r['fit_diagnostics']['H4']['time_scales_bars'] if x]
        du=[d for r in val for d in r['fit_diagnostics']['MS']['slow_durations'].values()]
        q=lambda v:[float(x) for x in np.quantile(v,[.25,.5,.75])] if v else None
        out['diagnostics'][iv]={'H4_time_scales_bars_quartiles':q(sc),
                                'slow_regime_mean_duration_bars_quartiles':q([d['mean_bars'] for d in du]),
                                'slow_duration_cv_quartiles':q([d['cv'] for d in du]),
                                'slow_ks_vs_geometric_quartiles':q([d['ks_vs_geometric'] for d in du]),
                                'H_converged_fraction':{f'H{k}':float(np.mean([r['fit_diagnostics'][f'H{k}']['converged'] for r in val]))
                                                        for k in (2,4)} if val else None}
    return out


# ---------------------------------------------------------------------- I/O
def write(obj,name):
    p=ROOT/'reports'/'m17'/name;p.parent.mkdir(parents=True,exist_ok=True)
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
    write({'status':'M17_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad},default=str))
    if bad:raise RuntimeError('Pilot failed')


def run_shard(iv,shard):
    df,starts=load(iv);per=PER_SHARD[iv]
    ks=range(shard*per,min(len(starts),(shard+1)*per))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],iv,k) for k in ks]
    write({'status':'M17_SHARD','interval':iv,'shard':shard,'n_origins_total':len(starts),
           'confirmatory_opened':False,'origins':rows},f'shard_{iv}_{shard:03d}.json')
    print(json.dumps({'interval':iv,'shard':shard,'n':len(rows)}))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('pilot','shard'),required=True)
    ap.add_argument('--interval',choices=INTERVALS);ap.add_argument('--shard',type=int)
    a=ap.parse_args()
    run_pilot() if a.mode=='pilot' else run_shard(a.interval,a.shard)


if __name__=='__main__':main()
