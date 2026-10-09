#!/usr/bin/env python3
"""SGV-M15: shape versus persistence ablation, with cheap comparators.

Everything is synthetic. Each external trial draws ONE Markov-regime truth
(prefix 2000 + window 1500, the M14 generator), fits SIX candidate nulls to
the prefix only, and simulates 19 references from each. The SAME observed
window is ranked against every null, so contrasts between nulls are paired
(common observed trajectory per trial).

Three statistics are computed on the SAME split halves of every trajectory
(anchor 30%, gaussianized halves, exactly `split_historical` as in M11/M14):

* ``m11``     : the unchanged M11 HDR50 surface distance (512 quadrature);
* ``fr_cov``  : Fisher-Rao distance between the two half covariances
                (zero-mean Gaussian Fisher metric, sqrt(1/2 * sum log^2 l_i));
* ``energy``  : sample energy distance between the two halves.

A separate VAR-truth control (VAR null) checks the calibration of the two
comparators under a correctly specified Gaussian family, as M14 did for m11.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
from scipy.spatial.distance import cdist
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from experiments.m13_calibracao_alarmes_regimes import mc_rank,wilson
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m11_distancia_superficie_nulos import measure_samples
from experiments.precisao_formas_3d import split_historical
from experiments.m14_calibracao_aninhada import (
    truth_hmm,truth_var,fit_hmm,fit_var,sample_hmm,sample_var,validate_prefix,
    PREFIX,WINDOW,REFS)

BASE_SEED=2026101015
TRUTHS=('HMM','VAR')
NULLS={'HMM':('HMM','GMM_IID','VAR','B15','B60','B150'),
       'VAR':('VAR',)}
STATS=('m11','fr_cov','energy')
TRIALS=500
PER_SHARD={'HMM':5,'VAR':25}
SHARDS={k:TRIALS//v for k,v in PER_SHARD.items()}
PILOT={'HMM':2,'VAR':2}
BLOCKS={'B15':15,'B60':60,'B150':150}


def seed_int(*parts):
    """Collision-free integer seed derived from a SeedSequence path."""
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])


def rng_for(*parts):
    return np.random.default_rng(np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]]))


TRUTH_ID={'HMM':1,'VAR':2}
NULL_ID={'HMM':1,'GMM_IID':2,'VAR':3,'B15':4,'B60':5,'B150':6}


def sample_truth(truth,trial):
    if truth not in TRUTHS:raise ValueError(truth)
    rng=rng_for(TRUTH_ID[truth],trial,0)
    n=PREFIX+WINDOW
    x=truth_hmm(rng,n) if truth=='HMM' else truth_var(rng,n)
    return x[:PREFIX],x[PREFIX:]


# ---------------------------------------------------------------- nulls
def fit_gmm_iid(prefix,seed):
    """Two-component full-covariance Gaussian mixture, IID: right shape, no memory."""
    from sklearn.mixture import GaussianMixture
    x=validate_prefix(prefix)
    g=GaussianMixture(n_components=2,covariance_type='full',n_init=3,
                      max_iter=300,tol=1e-4,reg_covar=1e-4,random_state=int(seed))
    g.fit(x)
    if not g.converged_:raise ValueError('GMM_IID nonconverged')
    if min(g.weights_)<1e-3:raise ValueError('GMM_IID degenerate weight')
    if any(min(np.linalg.eigvalsh(c))<=1e-7 for c in g.covariances_):
        raise ValueError('GMM_IID degenerate covariance')
    return {'type':'gmm_iid','model':g,'weights':[float(w) for w in g.weights_]}


def sample_gmm_iid(fit,rng,n):
    g=fit['model']
    comp=rng.choice(len(g.weights_),size=n,p=g.weights_/g.weights_.sum())
    out=np.empty((n,3))
    for k in range(len(g.weights_)):
        m=comp==k
        if m.any():
            out[m]=rng.multivariate_normal(g.means_[k],g.covariances_[k],size=int(m.sum()))
    return out


def fit_null(name,prefix,seed):
    if name=='HMM':return fit_hmm(prefix,seed)
    if name=='VAR':return fit_var(prefix)
    if name=='GMM_IID':return fit_gmm_iid(prefix,seed)
    if name in BLOCKS:
        return {'type':'blocks','x':validate_prefix(prefix).copy(),'block_length':BLOCKS[name]}
    raise ValueError(name)


def sample_null(fit,rng,n):
    t=fit['type']
    if t=='hmm':return sample_hmm(fit,rng,n)
    if t=='var':return sample_var(fit,rng,n)
    if t=='gmm_iid':return sample_gmm_iid(fit,rng,n)
    if t=='blocks':return circular_blocks(fit['x'],rng,fit['block_length'])[:n]
    raise ValueError(t)


# ---------------------------------------------------------- statistics
def fisher_rao_cov(a,b):
    """Fisher-Rao distance between N(0,Sa) and N(0,Sb): sqrt(1/2 sum log^2 eig(Sa^-1 Sb))."""
    Sa=np.cov(np.asarray(a,float),rowvar=False)
    Sb=np.cov(np.asarray(b,float),rowvar=False)
    L=np.linalg.cholesky(Sa)
    Li=np.linalg.inv(L)
    lam=np.linalg.eigvalsh(Li@Sb@Li.T)
    if min(lam)<=0:raise ValueError('Nonpositive covariance eigenvalue')
    return float(np.sqrt(.5*np.sum(np.log(lam)**2)))


def energy_distance(a,b):
    """Sample energy distance 2E|X-Y|-E|X-X'|-E|Y-Y'| (V-statistic)."""
    a=np.asarray(a,float);b=np.asarray(b,float)
    return float(2*cdist(a,b).mean()-cdist(a,a).mean()-cdist(b,b).mean())


def all_stats(x,seed):
    """m11, fr_cov, energy on exactly the same gaussianized halves.

    A statistic that fails is reported as None (never replaced); the others
    are still returned.
    """
    a,b=split_historical(np.asarray(x,float))
    out={}
    d=measure_samples(a,b,int(seed))
    v=d.get('distance_512') if d.get('valid',False) else None
    out['m11']=float(v) if v is not None and np.isfinite(v) else None
    out['m11_reason']=None if out['m11'] is not None else str(d.get('reason','nonfinite'))
    try:out['fr_cov']=fisher_rao_cov(a,b)
    except (ValueError,np.linalg.LinAlgError):out['fr_cov']=None
    out['energy']=energy_distance(a,b)
    if not np.isfinite(out['energy']):out['energy']=None
    return out


# --------------------------------------------------------------- trial
def run_trial(truth,trial,stats_fn=all_stats,refs=REFS):
    if truth not in TRUTHS or trial<0:raise ValueError('Unrecognized trial')
    prefix,window=sample_truth(truth,trial)
    obs=stats_fn(window,seed_int(TRUTH_ID[truth],trial,1))
    item={'truth':truth,'trial_id':int(trial),'observed':obs,'nulls':{},
          'fit_uses_prefix_only':True}
    for name in NULLS[truth]:
        rec={'status':'valid'}
        try:
            fit=fit_null(name,prefix,seed_int(TRUTH_ID[truth],trial,2,NULL_ID[name]))
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
            item['nulls'][name]={'status':'fit_failed','error':str(e)}
            continue
        ref={s:[] for s in STATS}
        for k in range(refs):
            try:
                sim=sample_null(fit,rng_for(TRUTH_ID[truth],trial,3,NULL_ID[name],k),WINDOW)
                r=stats_fn(sim,seed_int(TRUTH_ID[truth],trial,4,NULL_ID[name],k))
            except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
                r={s:None for s in STATS};r['m11_reason']=str(e)
            for s in STATS:ref[s].append(r[s])
        rec['references']=ref
        for s in STATS:
            vals=ref[s]
            if obs[s] is None or any(v is None for v in vals):
                rec[s]={'valid':False,
                        'n_ref_valid':int(sum(v is not None for v in vals)),
                        'observed_valid':obs[s] is not None}
                continue
            rank=mc_rank(obs[s],vals,min_reference=refs)
            rec[s]={'valid':True,'p_rank':rank,
                    'rank_position':int(round(rank*(refs+1))),  # 1 = obs exceeds all refs
                    'alarm':bool(rank<=.05)}
        item['nulls'][name]=rec
    return item


# ----------------------------------------------------------- aggregate
def mcnemar_exact(x,y):
    """One-sided exact McNemar: H1 = statistic x alarms more often than y (paired)."""
    from scipy.stats import binomtest
    b=int(sum(1 for a,c in zip(x,y) if a and not c))
    c=int(sum(1 for a,c2 in zip(x,y) if c2 and not a))
    p=float(binomtest(b,b+c,.5,alternative='greater').pvalue) if b+c else 1.0
    return {'x_only':b,'y_only':c,'n_pairs':len(x),'p_one_sided':p}


def cell(rows,truth,null,stat,requested):
    vals=[r['nulls'].get(null,{}) for r in rows if r['truth']==truth]
    ok=[v[stat] for v in vals if v.get('status')=='valid' and v.get(stat,{}).get('valid')]
    n=len(ok);al=sum(o['alarm'] for o in ok)
    hist=[0]*(REFS+1)
    for o in ok:hist[o['rank_position']-1]+=1
    return {'n_requested':requested,'n_valid':n,'n_invalid':requested-n,'alarms':int(al),
            'alarm_rate':float(al/n) if n else None,'wilson95':wilson(al,n),
            'failure_bounds':[al/requested,(al+requested-n)/requested],
            'rank_histogram_pos1_is_extreme':hist}


def paired(rows,truth,a,b):
    """Pairs (null_a,stat_a) vs (null_b,stat_b) on trials valid for both."""
    xa=[];xb=[]
    for r in rows:
        if r['truth']!=truth:continue
        na=r['nulls'].get(a[0],{});nb=r['nulls'].get(b[0],{})
        if na.get('status')!='valid' or nb.get('status')!='valid':continue
        sa=na.get(a[1],{});sb=nb.get(b[1],{})
        if not(sa.get('valid') and sb.get('valid')):continue
        xa.append(sa['alarm']);xb.append(sb['alarm'])
    out=mcnemar_exact(xa,xb)
    out['rate_a']=float(np.mean(xa)) if xa else None
    out['rate_b']=float(np.mean(xb)) if xb else None
    return out


PREREGISTERED_CONTRASTS=[
    # (name, a=(null,stat), b=(null,stat), alpha)
    ('Q1_persistencia_m11',('GMM_IID','m11'),('HMM','m11'),.05),
    ('Q2_forma_m11',('VAR','m11'),('GMM_IID','m11'),.05),
    ('Q3_dose_blocos_m11',('B15','m11'),('B150','m11'),.05),
    ('Q4_m11_vs_frcov_VAR',('VAR','m11'),('VAR','fr_cov'),.0125),
    ('Q4_m11_vs_frcov_GMM_IID',('GMM_IID','m11'),('GMM_IID','fr_cov'),.0125),
    ('Q4_m11_vs_frcov_B15',('B15','m11'),('B15','fr_cov'),.0125),
    ('Q4_m11_vs_frcov_B60',('B60','m11'),('B60','fr_cov'),.0125),
    ('Q5_m11_vs_energy_VAR',('VAR','m11'),('VAR','energy'),.0125),
    ('Q5_m11_vs_energy_GMM_IID',('GMM_IID','m11'),('GMM_IID','energy'),.0125),
    ('Q5_m11_vs_energy_B15',('B15','m11'),('B15','energy'),.0125),
    ('Q5_m11_vs_energy_B60',('B60','m11'),('B60','energy'),.0125),
]


def aggregate(rows,requested=TRIALS,check=True):
    if check:
        for truth in TRUTHS:
            ids=sorted(r['trial_id'] for r in rows if r['truth']==truth)
            if ids!=list(range(requested)):
                raise ValueError(f'Missing or duplicate trial IDs for truth {truth}')
    cells={}
    for truth in TRUTHS:
        for null in NULLS[truth]:
            for stat in STATS:
                cells[f'{truth}->{null}|{stat}']=cell(rows,truth,null,stat,requested)
    contrasts={}
    for name,a,b,alpha in PREREGISTERED_CONTRASTS:
        res=paired(rows,'HMM',a,b)
        res.update({'a':list(a),'b':list(b),'alpha':alpha,
                    'significant':bool(res['p_one_sided']<alpha)})
        contrasts[name]=res
    fit_fail={f'{t}->{n}':int(sum(1 for r in rows if r['truth']==t
                                  and r['nulls'].get(n,{}).get('status')=='fit_failed'))
              for t in TRUTHS for n in NULLS[t]}
    return {'cells':cells,'contrasts':contrasts,'fit_failures':fit_fail}


# ----------------------------------------------------------------- I/O
def write(obj,name):
    p=ROOT/'reports'/'m15'/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n')
    return p


def run_pilot():
    rows=[run_trial(t,i) for t in TRUTHS for i in range(PILOT[t])]
    bad=[]
    for r in rows:
        for s in STATS:
            if r['observed'][s] is None:bad.append((r['truth'],r['trial_id'],'obs',s))
        for n,v in r['nulls'].items():
            if v.get('status')!='valid':bad.append((r['truth'],r['trial_id'],n,'fit'))
            else:
                for s in STATS:
                    if not v[s]['valid']:bad.append((r['truth'],r['trial_id'],n,s))
    write({'status':'M15_PILOT','problems':bad,'n_rows':len(rows),
           'note':'engineering gate only; alarms are not inspected'},'pilot.json')
    print(json.dumps({'status':'M15_PILOT','problems':bad}))
    if bad:raise RuntimeError('Pilot failed: full run blocked')


def run_shard(truth,shard):
    if truth not in TRUTHS or not 0<=shard<SHARDS[truth]:raise ValueError('bad shard')
    per=PER_SHARD[truth];start=shard*per
    rows=[run_trial(truth,i) for i in range(start,start+per)]
    write({'status':'M15_SHARD','truth':truth,'shard':shard,'trials':rows},
          f'shard_{truth}_{shard:03d}.json')
    print(json.dumps({'status':'M15_SHARD','truth':truth,'shard':shard,'n':len(rows)}))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('pilot','shard'),required=True)
    ap.add_argument('--truth',choices=TRUTHS)
    ap.add_argument('--shard',type=int)
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    else:
        if a.truth is None or a.shard is None:ap.error('shard needs --truth and --shard')
        run_shard(a.truth,a.shard)


if __name__=='__main__':main()
