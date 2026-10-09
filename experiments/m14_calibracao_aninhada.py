#!/usr/bin/env python3
"""SGV-M14: nested fit-on-prefix Monte Carlo calibration of M11 HDR surface distance.

Everything is synthetic. Each external trial generates an INDEPENDENT prefix
and future under a FIXED truth, fits the candidate null ONLY to the prefix,
generates 19 paths, and re-estimates the full M11 instrument in all 20 paths.
Ranks after fitting ARE NOT exchangeable; repeated trials measure their
calibration empirically. A misspecified null's exceedance is model inadequacy.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from experiments.m13_calibracao_alarmes_regimes import mc_rank,wilson
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m11_distancia_superficie_nulos import measure_samples
from experiments.precisao_formas_3d import split_historical

SCENARIOS=('VAR_fit','HMM_fit','HMM_to_VAR','HMM_to_blocks')
SEED=20261009
PREFIX=2000
WINDOW=1500
REFS=19
SHARDS=20
PER_SHARD=25
PILOT_TRIALS=2
BLOCK=15
COV_VAR=np.array([[.62,.20,.11],[.20,.59,.07],[.11,.07,.36]])
A_VAR=np.array([[.22,.06,.02],[-.025,.22,.03],[.03,.02,.69]])
MU_VAR=np.array([0.,-.05,.1])
TRANS=np.array([[.984,.016],[.026,.974]])
MU_HMM=np.array([[0.,.10,-.55],[1.10,-.40,1.05]])
COV_HMM=np.array([
    [[.55,.11,.08],[.11,.48,.07],[.08,.07,.40]],
    [[1.10,.26,.17],[.26,.81,.13],[.17,.13,.81]]
])


def validate_prefix(x):
    x=np.asarray(x,dtype=float)
    if x.ndim!=2 or x.shape[1]!=3 or len(x)<300 or not np.isfinite(x).all():
        raise ValueError('Invalid fitted null prefix')
    return x


def stationary_prob(P):
    """Stationary two-state Markov distribution, no dependence on future window."""
    a=float(P[0,1]);b=float(P[1,0])
    if a<=0 or b<=0:raise ValueError('Non-ergodic transition matrix')
    return np.array([b/(a+b),a/(a+b)])


def truth_var(rng,n):
    """Stationary Gaussian VAR(1), fixed true parameters."""
    total=n+350
    noise=rng.multivariate_normal(np.zeros(3),COV_VAR,size=total)
    out=np.empty((total,3),float)
    out[0]=MU_VAR
    for i in range(1,total):
        out[i]=MU_VAR+A_VAR@(out[i-1]-MU_VAR)+noise[i]
    return out[350:]


def truth_hmm(rng,n):
    """Stationary Markov regimes with conditionally independent Gaussian emissions."""
    total=n+350
    state=int(rng.choice(2,p=stationary_prob(TRANS)))
    result=np.empty((total,3))
    for i in range(total):
        if i:
            state=int(rng.choice(2,p=TRANS[state]))
        result[i]=rng.multivariate_normal(MU_HMM[state],COV_HMM[state])
    return result[350:]


def sample_truth(scenario,seed,prefix=PREFIX,window=WINDOW):
    if scenario not in SCENARIOS:raise ValueError(scenario)
    rng=np.random.default_rng(seed)
    n=prefix+window
    out=truth_var(rng,n) if scenario=='VAR_fit' else truth_hmm(rng,n)
    return out[:prefix],out[prefix:]


def fit_var(prefix):
    x=validate_prefix(prefix)
    A=np.column_stack([np.ones(len(x)-1),x[:-1]])
    beta=np.linalg.lstsq(A,x[1:],rcond=None)[0]
    intercept=beta[0]
    transition=beta[1:].T
    spectral=float(max(abs(np.linalg.eigvals(transition))))
    if spectral>=.995:
        raise ValueError('VAR fit not stationary (spectral radius >= .995)')
    err=x[1:]-A@beta
    cov=np.cov(err,rowvar=False)
    if min(np.linalg.eigvalsh(cov))<=1e-8:
        raise ValueError('Nonpositive VAR innovation covariance')
    mean=np.linalg.solve(np.eye(3)-transition,intercept)
    return {'type':'var','intercept':intercept,
            'A':transition,'cov':cov,'mean':mean,
            'spectral_radius':spectral}


def sample_var(fit,rng,n):
    if n<=0:raise ValueError('Invalid sample length')
    total=n+250
    innov=rng.multivariate_normal(np.zeros(3),fit['cov'],size=total)
    out=np.empty((total,3),float)
    out[0]=fit['mean']
    for t in range(1,total):
        out[t]=fit['intercept']+fit['A']@out[t-1]+innov[t]
    return out[-n:]


def fit_hmm(prefix,seed,restarts=2):
    """Same two-state full-covariance Gaussian HMM as the Markov truth.

    Label switching is immaterial. Reject invalid likelihood/convergence.
    """
    from hmmlearn.hmm import GaussianHMM
    x=validate_prefix(prefix)
    best=None;best_score=-np.inf;problems=[]
    for r in range(restarts):
        try:
            h=GaussianHMM(n_components=2,covariance_type='full',
                          n_iter=75,tol=.01,min_covar=.001,
                          random_state=int(seed+13*r))
            h.fit(x)
            score=float(h.score(x))
            P=np.asarray(h.transmat_)
            cov=np.asarray(h.covars_)
            if (not h.monitor_.converged or not np.isfinite(score)
                or not np.isfinite(P).all()
                or not np.isfinite(cov).all()
                or any(min(np.linalg.eigvalsh(z))<=1e-7 for z in cov)
                or min(stationary_prob(P))<1e-4):
                raise ValueError('HMM nonconverged or degenerate')
            if score>best_score:best=h;best_score=score
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
            problems.append(str(e))
    if best is None:
        raise ValueError('HMM fit failed every restart: '+'; '.join(problems))
    return {'type':'hmm','model':best,
            'log_likelihood':float(best_score),
            'iterations':int(best.monitor_.iter),
            'self_transition_mean':float(np.trace(best.transmat_)/2)}


def sample_hmm(fit,rng,n):
    from hmmlearn.hmm import GaussianHMM
    h=fit['model']
    # Stationary unconditional draw after burn-in, as for fitted VAR.
    seed=int(rng.integers(0,2**31-1))
    x,_=h.sample(n_samples=n+250,random_state=seed)
    return np.asarray(x[-n:],float)


def fit_blocks(prefix):
    x=validate_prefix(prefix)
    return {'type':'blocks','x':x.copy(),'block_length':BLOCK}


def sample_blocks(fit,rng,n):
    return circular_blocks(fit['x'],rng,fit['block_length'])[:n]


def fit_null(scenario,prefix,seed):
    if scenario=='HMM_fit':
        return fit_hmm(prefix,seed)
    if scenario in ('VAR_fit','HMM_to_VAR'):
        return fit_var(prefix)
    if scenario=='HMM_to_blocks':
        return fit_blocks(prefix)
    raise ValueError(scenario)


def sample_null(fit,rng,n):
    if fit['type']=='var':return sample_var(fit,rng,n)
    if fit['type']=='hmm':return sample_hmm(fit,rng,n)
    if fit['type']=='blocks':return sample_blocks(fit,rng,n)
    raise ValueError('Unknown null')


def full_m11_distance(x,seed):
    """Exact M11 measurement path; metric never modified between scenarios."""
    a,b=split_historical(np.asarray(x,float))
    d=measure_samples(a,b,int(seed))
    if not d.get('valid',False):
        raise ValueError('M11 invalid geometry: '+str(d.get('reason')))
    result=float(d['distance_512'])
    if not np.isfinite(result):raise ValueError('Nonfinite M11 distance')
    return result


def run_trial(scenario,trial_id,metric=full_m11_distance,references=REFS):
    if scenario not in SCENARIOS or trial_id<0:raise ValueError('Unrecognized trial')
    if references<1:raise ValueError('Need reference draws')
    sid=SCENARIOS.index(scenario)
    seed=SEED+sid*100_000_000+trial_id*1987
    prefix,future=sample_truth(scenario,seed)
    item={'scenario':scenario,'trial_id':int(trial_id),
          'n_references_requested':int(references),
          'n_references_valid':0,
          'fit_uses_prefix_only':True,
          'metric':'M11_direct_triangle_HDR50_512'}
    try:
        fitted=fit_null(scenario,prefix,seed+33)
        item['fit_type']=fitted['type']
        item['fit_diagnostics']={
            k:float(v) for k,v in fitted.items()
            if k in ('spectral_radius','log_likelihood',
                     'iterations','self_transition_mean','block_length')}
        obs=float(metric(future,seed+101))
        if not np.isfinite(obs):raise ValueError('Nonfinite observed distance')
        refs=[];invalid=[]
        for k in range(references):
            try:
                # One independent reference per seed, with parameters fixed at
                # prefix-estimated fitted model; no reference re-fits the time null.
                rng=np.random.default_rng(seed+10000+97*k)
                simulated=sample_null(fitted,rng,WINDOW)
                val=float(metric(simulated,seed+25000+97*k))
                if not np.isfinite(val):raise ValueError('Nonfinite null distance')
                refs.append(val)
            except (ValueError,RuntimeError,AssertionError,
                    np.linalg.LinAlgError) as e:
                invalid.append({'reference':k,'error':str(e)})
        item['n_references_valid']=len(refs)
        if invalid:
            item.update({'status':'invalid','failure_stage':'reference_geometry',
                         'failures':invalid,'observed_distance':obs})
            return item
        rank=float(mc_rank(obs,refs,min_reference=references))
        item.update({'status':'valid','observed_distance':obs,
                     'reference_median':float(np.median(refs)),
                     'reference_q90':float(np.quantile(refs,.9)),
                     'rank_statistic_uncalibrated':rank,
                     'alarm_at_005':bool(rank<=.05)})
    except (ValueError,RuntimeError,AssertionError,
            np.linalg.LinAlgError) as e:
        item.update({'status':'invalid','failure_stage':'fit_or_observation',
                     'error':str(e)})
    return item


def aggregate(rows,requested):
    seen=[(x['scenario'],x['trial_id']) for x in rows]
    if len(set(seen))!=len(seen):raise ValueError('Duplicate external trial ID')
    if len(rows)!=requested:raise ValueError('Missing external trials')
    valid=[r for r in rows if r['status']=='valid']
    n=len(valid)
    bad=requested-n
    alarms=sum(r['alarm_at_005'] for r in valid)
    return {'n_requested':int(requested),'n_valid':int(n),
            'n_invalid':int(bad),'alarms':int(alarms),
            'alarm_rate':float(alarms/n) if n else None,
            'wilson95':wilson(alarms,n),
            'failure_bounds_unconditional':[
                float(alarms/requested),
                float((alarms+bad)/requested)],
            'nominal_level':.05,
            'warning':'HMM and VAR calibrations reflect fitting, initialization, and geometry; misspecified null alarms are model inadequacy'}


def write_result(result,filename):
    path=ROOT/'reports'/filename
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    return path


def run_pilot():
    scenarios={}
    all_valid=True
    for scenario in SCENARIOS:
        trials=[run_trial(scenario,t) for t in range(PILOT_TRIALS)]
        stats=aggregate(trials,PILOT_TRIALS)
        scenarios[scenario]={'summary':stats,'trials':trials}
        if stats['n_valid']!=PILOT_TRIALS:all_valid=False
    outcome={'status':'M14_PILOT','all_scenarios_passed':all_valid,
             'scenarios':scenarios,
             'warning':'Eight external trials are engineering validation only'}
    write_result(outcome,'SGV_M14_pilot.json')
    print(json.dumps({'status':outcome['status'],
                     'all_scenarios_passed':all_valid,
                     'stats':{k:v['summary'] for k,v in scenarios.items()}},indent=2))
    if not all_valid:raise RuntimeError('Pilot failed, 500-trial run blocked')


def run_shard(scenario,shard,per_shard=PER_SHARD):
    if shard<0 or shard>=SHARDS:raise ValueError('Invalid shard')
    start=shard*per_shard
    result=[run_trial(scenario,i) for i in range(start,start+per_shard)]
    summary=aggregate(result,per_shard)
    outcome={'status':'M14_SHARD','scenario':scenario,'shard':shard,
             'trial_start':start,'trial_end':start+per_shard-1,
             'n_references_each':REFS,'summary':summary,
             'trials':result,'true_law_constant':True,
             'no_BTC_data_accessed':True}
    file=write_result(outcome,f'SGV_M14_{scenario}_shard{shard:02d}.json')
    print(json.dumps({'status':'M14_SHARD','scenario':scenario,
                      'shard':shard,'summary':summary},indent=2))
    if summary['n_valid']==0:
        raise RuntimeError(f'No valid nested trials in shard (report at {file})')
    # Partial invalidity is reported and bounded, not silently excluded.


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('pilot','shard'),required=True)
    ap.add_argument('--scenario',choices=SCENARIOS)
    ap.add_argument('--shard',type=int)
    ap.add_argument('--per-shard',type=int,default=PER_SHARD)
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    else:
        if a.scenario is None or a.shard is None:ap.error('shard needs scenario and shard')
        run_shard(a.scenario,a.shard,a.per_shard)
if __name__=='__main__':main()
