"""C01 engineering-only same-distribution T0 null: estimation noise and alarm size.

No official validation/test partitions, no classification, no market data.
40 scale-only replicates, 40 threshold replicates, 40 independent diagnostics.
All namespaces use calibration replicate IDs >= 1_000_000 to avoid official IDs.
Thresholds are fixed before the diagnostic group is evaluated.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.c01_estimacao_independente import (
    N_PER_ARM, independent_pair, estimate_pair, baseline_features, hdr_features,
)

SEED_NAMESPACE = 'calibration'
REPLICATE_BASE = 1_000_000
GROUPS = {'scaling': (0, 40), 'threshold': (40, 80), 'independent_diagnostic': (80, 120)}
MC = 32000
GRID = 35
SCORING_FEATURES = (
    'hdr50_center_distance','hdr50_log_volume_ratio','hdr50_log_area_ratio',
    'hdr50_delta_components','hdr50_voxel_iou_loss','hdr50_shape_tensor_diff',
    'hdr95_center_distance','hdr95_log_volume_ratio','hdr95_log_area_ratio',
    'hdr95_delta_components','hdr95_voxel_iou_loss','hdr95_shape_tensor_diff',
)
NUMERIC_FEATURES = (
    'fr_ambient','fr_cov','energy','entropy_delta',
    'hdr50_center_distance','hdr50_voxel_iou_loss','hdr50_shape_tensor_diff',
    'hdr95_center_distance','hdr95_voxel_iou_loss','hdr95_shape_tensor_diff',
)


def anomaly(v: dict, key: str) -> float:
    z = float(v[key])
    if not np.isfinite(z):
        raise ValueError('non-finite measurement')
    if ('log_volume_ratio' in key or 'log_area_ratio' in key or
            'delta_components' in key or key == 'entropy_delta'):
        return abs(z)
    if z < -1e-12:
        raise ValueError('anomaly magnitude negative')
    return max(0., z)


def quantile(x, q):
    return float(np.quantile(np.asarray(x,dtype=float), q,method='higher'))


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:return [None, None]
    p = k/n
    mid = (p+z*z/(2*n))/(1+z*z/n)
    rad = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return [float(max(0.0, mid-rad)), float(min(1.0, mid+rad))]


def measure(rep: int) -> dict:
    pair = independent_pair('T0', REPLICATE_BASE+rep, split=SEED_NAMESPACE)
    fa, fb = estimate_pair(pair)
    base = baseline_features(pair,fa,fb,n_mc=MC)
    hdr = hdr_features(pair,fa,fb,grid_n=GRID,cutoff_n=MC,cover_n=MC)
    vals = {k:float(v) for k,v in ({**base, **hdr}).items()}
    if not all(np.isfinite(v) for v in vals.values()):
        raise ValueError('non-finite metrics')
    return {
        'replicate':rep,
        'sample_hash_A':pair.a_sha256,
        'sample_hash_B':pair.b_sha256,
        'fit_iterations':[fa.iterations,fb.iterations],
        'fit_min_weight':[fa.min_weight,fb.min_weight],
        'values':vals,
    }


def score(row: dict, scale: dict) -> float:
    return max(anomaly(row['values'],k)/scale[k] for k in SCORING_FEATURES)


def summarize(rows,feature):
    x = np.asarray([anomaly(r['values'],feature) for r in rows])
    return {'median':float(np.median(x)), 'q90':quantile(x,.9),
            'q95':quantile(x,.95),'max':float(np.max(x))}


def run() -> dict:
    rows = {}
    failures = {}
    start=time.monotonic()
    for group,(lo,hi) in GROUPS.items():
        group_rows=[]; group_fail=[]
        for rep in range(lo,hi):
            try:
                group_rows.append(measure(rep))
            except (ValueError,RuntimeError,np.linalg.LinAlgError) as exc:
                group_fail.append({'replicate':rep,'exception':type(exc).__name__, 'reason':str(exc)})
        rows[group]=group_rows
        failures[group]=group_fail
        print(f'{group}: {len(group_rows)}/{hi-lo} valid; elapsed {time.monotonic()-start:.1f}s',flush=True)

    n_expected = sum(hi-lo for lo,hi in GROUPS.values())
    n_valid = sum(len(r) for r in rows.values())
    if n_valid != n_expected:
        return {'status':'INCONCLUSIVE_FAILURES','all_valid':False,
                'total':n_expected,'valid':n_valid,'failures':failures,
                'rows':rows,'contains_market_data':False,'official_test_opened':False}

    # Group I learns scales; Group II sets the joint threshold; III never sets/tunes anything.
    scales = {}
    for key in SCORING_FEATURES:
        q75 = quantile([anomaly(r['values'],key) for r in rows['scaling']],.75)
        scales[key] = q75 if q75 > 1e-12 else 1.0
    scores_threshold = [score(r,scales) for r in rows['threshold']]
    cutoff = quantile(scores_threshold,.95)
    scores_check = [score(r,scales) for r in rows['independent_diagnostic']]
    alerts = int(sum(v > cutoff for v in scores_check))
    n_check=len(scores_check)

    # Do not reselect features/cutoff after seeing diagnostics.
    values_all=[r for group in rows.values() for r in group]
    summary = {k:summarize(values_all,k) for k in NUMERIC_FEATURES}
    n_outlier_coverage = sum(any(abs(r['values'][f'_num_{label}_coverage_error_{side}'])>.015
        for label in ('hdr50','hdr95') for side in ('a','b')) for r in values_all)
    return {
        'status':'ENGINEERING_ONLY','all_valid':True,'contains_market_data':False,
        'official_test_opened':False,'classifier_trained':False,
        'n_per_arm':N_PER_ARM,'gmm_components':3,'mc_samples_per_estimate':MC,
        'grid_n':GRID,'seed_namespace':SEED_NAMESPACE,'replicate_base':REPLICATE_BASE,
        'groups':{k:len(v) for k,v in rows.items()},
        'max_threshold_method':'q75 scaler from 40; 95th percentile max-score from separate 40; eval on fresh 40',
        'scales':scales,'threshold':cutoff,'scores_threshold':scores_threshold,
        'validation_scores':scores_check, 'validation_alerts':alerts,
        'validation_trials':n_check,'validation_alert_rate':alerts/n_check,
        'wilson_95':wilson(alerts,n_check),
        'metrics_t0_distribution':summary,
        'replicates_with_coverage_error_above_0_015':n_outlier_coverage,
        'replicate_hashes':[{**{'group':g},**{k:r[k] for k in ('replicate','sample_hash_A','sample_hash_B')}}
            for g,items in rows.items() for r in items],
        'failures':failures,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',default='reports/c01_t0_null_calibration_mc32000.json')
    args=p.parse_args()
    d=run()
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('status',d['status'],'null alerts',d.get('validation_alerts'),'/',d.get('validation_trials'),
          'Wilson',d.get('wilson_95'),flush=True)
    return 0 if d['all_valid'] else 2

if __name__=='__main__':
    sys.exit(main())
