"""SGV-ID4 -- prospective controls for volatility-only vs hidden sign memory.

Synthetic data only. Prediction recorded before code in PREDICAO_ID4_VOL_VS_DIRECAO_20261015.md.
Training and validation (trajectory IDs 0..17) are wholly separate from held-out
test (18..29). The heldout runner consumes JSON-frozen models; no fitting on test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from scipy.signal import lfilter
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

SEED = 20261015
N = 10000
BURN = 1000
ANCHOR_N = 1000
FIRST_T = 1100
TRAIN_IDS = tuple(range(12))
VALIDATION_IDS = tuple(range(12, 18))
TEST_IDS = tuple(range(18, 30))
L_RHO, F_RHO = 0.999, 0.90
L_VAR, F_VAR = 0.30, 0.20
BASE_SCALE = 0.0007
SIGN_PERSISTENCE = 0.85
BASE_NAMES = ('E_norm', 'jerk', 'memory_flux', 'h_slow', 'h_fast',
              'sign_t', 'sign_t_minus_1', 'sign_t_minus_2')
EXTRA_NAME = 'sign_t_minus_3'
BOOTSTRAPS = 2000
BOOT_SEED = 202610154


def seed_for(path_id: int, role: str) -> int:
    payload = f'ID4|{SEED}|{path_id}|{role}'.encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], 'big')


def ar_path(rng: np.random.Generator, rho: float, variance: float, total: int) -> np.ndarray:
    z = rng.standard_normal(total) * np.sqrt(variance * (1-rho*rho))
    stationary_initial = rng.normal(scale=np.sqrt(variance))
    h = lfilter([1.0], [1.0, -rho], z)
    h += (rho ** (np.arange(total) + 1)) * stationary_initial
    return h[BURN:]


def ewm(v: np.ndarray, alpha: float) -> np.ndarray:
    out = np.empty(len(v), dtype=float)
    out[0] = v[0]
    for t in range(1, len(v)):
        out[t] = alpha * v[t] + (1-alpha) * out[t-1]
    return out


def coordinates(r: np.ndarray) -> np.ndarray:
    """Essential SGV definitions, NOT a byte-identical financial pipeline."""
    close = np.exp(np.cumsum(r, dtype=float))
    remembered_price = ewm(close, .05)
    eraw = (close-remembered_price) / np.abs(remembered_price)
    anchor = eraw[:ANCHOR_N]
    med = np.median(anchor)
    spread = np.quantile(np.abs(anchor-med), .995)/3
    if not np.isfinite(spread) or spread < 1e-12:
        raise ValueError('bad E_norm anchor')
    en = (eraw-med)/spread
    simple_return = np.empty(len(r))
    simple_return[0] = 0.0
    simple_return[1:] = close[1:] / close[:-1] - 1.0
    jerk = np.empty(len(r))
    jerk[:2] = np.nan
    jerk[2:] = simple_return[2:] - 2*simple_return[1:-1] + simple_return[:-2]
    mf = np.empty(len(r))
    memory = ewm(en, .05)
    mf[0] = np.nan
    mf[1:] = np.diff(memory)
    return np.column_stack((en, jerk, mf))


def paired_path(path_id: int) -> dict:
    if not 0 <= path_id < 30:
        raise ValueError('bad path id')
    total = N+BURN
    common = np.random.default_rng(seed_for(path_id, 'shared'))
    hslow = ar_path(common, L_RHO, L_VAR, total)
    hfast = ar_path(common, F_RHO, F_VAR, total)
    magnitudes = np.abs(common.standard_normal(total)[BURN:])
    sigma = BASE_SCALE * np.exp(.5*(hslow+hfast-.5))
    sign_n = np.where(np.random.default_rng(seed_for(path_id, 'null_sign')).random(N) < .5, -1., 1.)
    rng = np.random.default_rng(seed_for(path_id, 'direction_sign'))
    sign_d = np.empty(N, dtype=float)
    sign_d[:4] = np.where(rng.random(4) < .5, -1., 1.)
    propagate = rng.random(N-4) < SIGN_PERSISTENCE
    for t in range(4,N):
        sign_d[t] = sign_d[t-4] if propagate[t-4] else -sign_d[t-4]
    r_n = sigma * magnitudes * sign_n
    r_d = sigma * magnitudes * sign_d
    energy_n = np.square(r_n/sigma)
    energy_d = np.square(r_d/sigma)
    if not np.array_equal(energy_n, energy_d):
        raise RuntimeError('energy must be byte-exactly identical in paired paths')
    if np.any(~np.isfinite(sigma)):
        raise RuntimeError('nonfinite volatility')
    out = {'path_id':path_id, 'oracle_energy':energy_n,
           'slow':hslow, 'fast':hfast, 'sigma':sigma,
           'null': {'r':r_n,'sign':sign_n,'coord':coordinates(r_n)},
           'direction': {'r':r_d,'sign':sign_d,'coord':coordinates(r_d)}}
    return out


def design_matrix(path: dict, condition: str) -> tuple[np.ndarray,np.ndarray,np.ndarray]:
    if condition not in ('null','direction'):
        raise ValueError('invalid condition')
    s = path[condition]['sign']
    xyz = path[condition]['coord']
    t = np.arange(FIRST_T,N-1)
    base = np.column_stack((
        xyz[t],path['slow'][t],path['fast'][t],
        s[t],s[t-1],s[t-2]
    ))
    extra = s[t-3,None]
    y = (s[t+1] > 0).astype(int)
    if not np.isfinite(base).all():
        raise ValueError('nonfinite features')
    return base,extra,y


def clean_energy_memory(path: dict) -> float:
    x=path['oracle_energy']
    history=np.convolve(x,np.ones(10)/10,mode='full')[:len(x)]
    # prior 10 only; no current energy included.
    prior=np.r_[np.full(10,np.nan),history[9:-1]]
    return float(spearmanr(x[10:],prior[10:]).correlation)


def fit_model(x: np.ndarray,y: np.ndarray) -> dict:
    scale = StandardScaler()
    z=scale.fit_transform(x)
    reg=LogisticRegression(C=1.0,max_iter=1000,solver='lbfgs')
    reg.fit(z,y)
    if not np.array_equal(reg.classes_,[0,1]):
        raise ValueError('invalid classification support')
    return {'mean':scale.mean_.tolist(),'scale':scale.scale_.tolist(),
            'coef':reg.coef_.reshape(-1).tolist(),'intercept':float(reg.intercept_[0]),
            'classes':[0,1], 'C':1.0,'solver':'lbfgs','max_iter':1000}


def frozen_predict(model: dict,x: np.ndarray) -> np.ndarray:
    mu = np.asarray(model['mean'])
    sc = np.asarray(model['scale'])
    beta = np.asarray(model['coef'])
    logit = ((x-mu)/sc) @ beta + model['intercept']
    out = np.empty_like(logit)
    pos=logit>=0
    out[pos]=1/(1+np.exp(-logit[pos]))
    t=np.exp(logit[~pos])
    out[~pos]=t/(1+t)
    return np.clip(out,1e-14,1-1e-14)


def logloss_per_path(y: np.ndarray,p: np.ndarray) -> float:
    return float(np.mean(-y*np.log(p)-(1-y)*np.log1p(-p)))


def construct_split(ids: tuple[int,...]) -> dict:
    result={'null':[], 'direction':[]}
    energies=[]
    for idx in ids:
        pair=paired_path(idx)
        energies.append(clean_energy_memory(pair))
        for condition in result:
            b,e,y=design_matrix(pair,condition)
            result[condition].append((b,e,y))
    return {'data':result,'energy_rho':energies,
            'sha256_pairs': [hashlib.sha256(f'ID4|{idx}|same-vol-magnitudes'.encode()).hexdigest()
                             for idx in ids]}


def fit_training() -> dict:
    tr=construct_split(TRAIN_IDS)
    frozen={}
    for condition, items in tr['data'].items():
        b = np.concatenate([p[0] for p in items])
        e = np.concatenate([p[1] for p in items])
        y = np.concatenate([p[2] for p in items])
        frozen[condition]={
            'base': fit_model(b,y),
            'base_plus_lag4':fit_model(np.hstack((b,e)),y)
        }
    return {'schema':'SGV-ID4-frozen-v1', 'study':'ID4', 'trained_on':list(TRAIN_IDS),
            'validation_ids':list(VALIDATION_IDS),'sealed_test_ids':list(TEST_IDS),
            'feature_base':list(BASE_NAMES),'feature_extra':EXTRA_NAME,
            'models':frozen, 'train_energy_rho':tr['energy_rho'],
            'note':'Synthetic controls; never train on IDs 18..29'}


def evaluate(ids: tuple[int,...],frozen:dict) -> dict:
    val=construct_split(ids)
    report={'ids':list(ids),'sha256_pairs':val['sha256_pairs'],
            'energy_rho':val['energy_rho'],'outcomes':{}}
    for condition,rows in val['data'].items():
        per=[]
        for idx,(b,e,y) in zip(ids,rows):
            p_base=frozen_predict(frozen['models'][condition]['base'],b)
            p_plus=frozen_predict(frozen['models'][condition]['base_plus_lag4'],np.hstack((b,e)))
            base_loss=logloss_per_path(y,p_base)
            plus_loss=logloss_per_path(y,p_plus)
            per.append({'id':idx,'base':base_loss,'plus':plus_loss,'delta':base_loss-plus_loss,
                        'base_accuracy':float(np.mean((p_base>=.5)==y)),
                        'plus_accuracy':float(np.mean((p_plus>=.5)==y))})
        report['outcomes'][condition]=per
    return report


def summarize_test(report:dict) -> dict:
    rng=np.random.default_rng(BOOT_SEED)
    out={}
    for condition,items in report['outcomes'].items():
        delta=np.asarray([r['delta'] for r in items])
        idx=rng.integers(0,len(items),size=(BOOTSTRAPS,len(items)))
        ci=np.quantile(delta[idx].mean(axis=1),[.025,.975])
        out[condition]={'n_paths':len(items),'delta_logloss':float(delta.mean()),
                        'ci95':ci.tolist(),
                        'mean_base_logloss':float(np.mean([r['base'] for r in items])),
                        'mean_plus_logloss':float(np.mean([r['plus'] for r in items])),
                        'mean_base_accuracy':float(np.mean([r['base_accuracy'] for r in items])),
                        'mean_plus_accuracy':float(np.mean([r['plus_accuracy'] for r in items]))}
    nonidentify = all(np.isfinite(report['energy_rho']))
    gates = {'energy_unidentifiable_by_construction':bool(nonidentify),
             'direction_sensitive':bool(out['direction']['delta_logloss']>=.05
                and out['direction']['ci95'][0]>0),
             'null_specificity':bool(abs(out['null']['delta_logloss'])<=.015)}
    return {'status':'SYNTHETIC_ID4_PASS' if all(gates.values()) else 'SYNTHETIC_ID4_FAIL',
            'gates':gates,'outcomes':out,
            'interpretation':'Directional delay identifies this planted alternative; pure energy remains identical. No BTC conclusions.'}


def write_json(path:str,data:dict) -> str:
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(data,indent=2,allow_nan=False,ensure_ascii=False)+'\n').encode()
    p.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=('train','test'),required=True)
    parser.add_argument('--freeze',required=True)
    parser.add_argument('--out',required=True)
    parser.add_argument('--freeze-sha',default=None)
    opt=parser.parse_args()
    if opt.stage=='train':
        frozen=fit_training()
        frozen['validation_descriptive']=evaluate(VALIDATION_IDS,frozen)
        print('FROZEN',write_json(opt.freeze,frozen),flush=True)
        print('VALIDATION_ONLY',len(frozen['validation_descriptive']['ids']),'paths',flush=True)
        return 0
    path=Path(opt.freeze)
    checksum=hashlib.sha256(path.read_bytes()).hexdigest()
    if not opt.freeze_sha or checksum!=opt.freeze_sha:
        raise RuntimeError('Freeze SHA-256 is required and must match exact frozen models')
    frozen=json.loads(path.read_text())
    if frozen['trained_on']!=list(TRAIN_IDS) or frozen['sealed_test_ids']!=list(TEST_IDS):
        raise RuntimeError('Unexpected training/test IDs in frozen model')
    if Path(opt.out).exists():
        raise RuntimeError('Holdout result exists, no ordinary rerun permitted')
    report=evaluate(TEST_IDS,frozen)
    summary=summarize_test(report)
    payload={'freeze_sha256':checksum,'full_report':report,'summary':summary,
             'market_data_used':False,'test_opened_once':True}
    print('TEST_RESULT',write_json(opt.out,payload),summary,flush=True)
    return 0 if summary['status']=='SYNTHETIC_ID4_PASS' else 2


if __name__=='__main__':
    sys.exit(main())
