"""SGV-C01 engineering: independent A/B draws and fixed GMM3 estimation.

Never accesses BTC or protected classification test data. All features use the
SAME fitted A/B densities, except energy distance uses those observed draws.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import warnings
import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.mixture import GaussianMixture
from experiments.c01_oraculo_hdr_fisher import (
    GMM3, known_pair, fr_covariance, fr_ambient_mc, delta_entropy_mc,
    energy_distance, hdr_pair, common_bounds,
)

BASE_SEED = 20261014
N_PER_ARM = 750
REG_COVAR = 1e-4
N_INIT = 3
MAX_ITER = 300
TOL = 1e-4
ALLOWED_SPLITS = frozenset(('calibration', 'training', 'validation'))
CASES = tuple(f'T{i}' for i in range(7))


def seed_for(split: str, case: str, replicate: int, purpose: str) -> int:
    """SHA-256 stable namespace seeds; sealed test split is not accessible."""
    if split not in ALLOWED_SPLITS:
        raise ValueError('C01 sealed test partition unavailable during engineering')
    if case not in CASES or replicate < 0 or not isinstance(purpose, str) or not purpose:
        raise ValueError('invalid case, replicate or seed namespace')
    msg = f'C01|{BASE_SEED}|{split}|{case}|{replicate}|{purpose}'.encode('utf-8')
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], 'big')


def sample_sha256(samples: np.ndarray) -> str:
    x = np.ascontiguousarray(np.asarray(samples, dtype='<f8'))
    return hashlib.sha256(x.tobytes(order='C')).hexdigest()


@dataclass(frozen=True)
class ObservedPair:
    case: str
    replicate: int
    split: str
    a: np.ndarray
    b: np.ndarray
    a_sha256: str
    b_sha256: str
    design_seed: int
    a_seed: int
    b_seed: int


def independent_pair(case: str, replicate: int, *, split: str = 'calibration',
                     n: int = N_PER_ARM, nuisance: bool = True) -> ObservedPair:
    if n != N_PER_ARM:
        raise ValueError(f'fixed instrument sample size n={N_PER_ARM} per arm')
    sn = seed_for(split, case, replicate, 'nuisance')
    sa = seed_for(split, case, replicate, 'observed_A')
    sb = seed_for(split, case, replicate, 'observed_B')
    if len({sn, sa, sb}) != 3:
        raise RuntimeError('seed collision')
    p, q = known_pair(case, nuisance_seed=sn if nuisance else None)
    a = p.sample(n, np.random.default_rng(sa))
    b = q.sample(n, np.random.default_rng(sb))
    ha, hb = sample_sha256(a), sample_sha256(b)
    if ha == hb or np.shares_memory(a, b):
        raise RuntimeError('A/B samples must be independent')
    a.setflags(write=False)
    b.setflags(write=False)
    return ObservedPair(case, replicate, split, a, b, ha, hb, sn, sa, sb)


@dataclass(frozen=True)
class EstimatedGMM:
    model: GMM3
    converged: bool
    lower_bound: float
    iterations: int
    min_weight: float
    max_condition_number: float
    warnings: tuple[str, ...]


def estimate_gmm(samples: np.ndarray, *, seed: int) -> EstimatedGMM:
    x = np.asarray(samples, dtype=float)
    if x.shape != (N_PER_ARM, 3) or not np.isfinite(x).all():
        raise ValueError('expected 750 finite observed 3-D vectors')
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always', ConvergenceWarning)
        fit = GaussianMixture(
            n_components=3, covariance_type='full', n_init=N_INIT,
            reg_covar=REG_COVAR, max_iter=MAX_ITER, tol=TOL,
            random_state=int(seed % (2**32 - 1)), init_params='kmeans'
        ).fit(x)
    model = GMM3(fit.weights_, fit.means_, fit.covariances_)
    minw = float(model.weights.min())
    cond = float(max(np.linalg.cond(c) for c in model.covs))
    if not fit.converged_ or minw < 1e-3 or cond > 1e8:
        raise ValueError(f'invalid GMM fit: converged={fit.converged_}, weight={minw}, cond={cond}')
    return EstimatedGMM(model, bool(fit.converged_), float(fit.lower_bound_),
                        int(fit.n_iter_), minw, cond,
                        tuple(str(w.message) for w in caught))


def estimate_pair(pair: ObservedPair) -> tuple[EstimatedGMM, EstimatedGMM]:
    fa = estimate_gmm(pair.a, seed=seed_for(pair.split, pair.case, pair.replicate, 'fit_A'))
    fb = estimate_gmm(pair.b, seed=seed_for(pair.split, pair.case, pair.replicate, 'fit_B'))
    return fa, fb


def baseline_features(pair: ObservedPair, fa: EstimatedGMM, fb: EstimatedGMM,
                      *, n_mc: int = 8000) -> dict[str, float]:
    p, q = fa.model, fb.model
    ma, ca = p.moments()
    mb, cb = q.moments()
    dm, dc = mb - ma, cb - ca
    out = {f'delta_mu_{i}': float(v) for i, v in enumerate(dm)}
    out.update({f'delta_cov_{i}{j}': float(dc[i, j]) for i in range(3) for j in range(i, 3)})
    out['logdet_cov_delta'] = float(np.linalg.slogdet(cb)[1] - np.linalg.slogdet(ca)[1])
    dh, dh_se = delta_entropy_mc(
        p, q, n=n_mc, seed=seed_for(pair.split, pair.case, pair.replicate, 'entropy'))
    out['entropy_delta'] = dh
    out['fr_cov'] = fr_covariance(p, q)
    fr = fr_ambient_mc(p, q, n=n_mc,
                       seed=seed_for(pair.split, pair.case, pair.replicate, 'fr_ambient'))
    out['fr_ambient'] = float(fr['fr_ambient'])
    out['energy'] = energy_distance(pair.a, pair.b)
    return out | {'_num_entropy_delta_se': dh_se, '_num_affinity_se': fr['affinity_se']}


def hdr_features(pair: ObservedPair, fa: EstimatedGMM, fb: EstimatedGMM,
                 *, grid_n: int = 35, cutoff_n: int = 8000,
                 cover_n: int = 8000) -> dict[str, float]:
    """HDR50/95 shape descriptors: paired common-world-grid, no registration."""
    out = {}
    for alpha, label in ((.50, 'hdr50'), (.95, 'hdr95')):
        measured = hdr_pair(
            fa.model, fb.model, alpha=alpha,
            seed=seed_for(pair.split, pair.case, pair.replicate, label) % (2**63),
            grid_n=grid_n, cutoff_n=cutoff_n, cover_n=cover_n,
        )
        out[f'{label}_center_distance'] = measured['center_distance']
        out[f'{label}_log_volume_ratio'] = measured['log_volume_ratio']
        out[f'{label}_log_area_ratio'] = measured['log_area_ratio']
        out[f'{label}_delta_components'] = float(measured['delta_components'])
        lo, hi = common_bounds(fa.model, fb.model)
        axes = [np.linspace(lo[j], hi[j], grid_n) for j in range(3)]
        xyz = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1).reshape(-1, 3)
        mask_a = fa.model.logpdf(xyz) >= measured['A']['log_threshold']
        mask_b = fb.model.logpdf(xyz) >= measured['B']['log_threshold']
        union = int(np.count_nonzero(mask_a | mask_b))
        if union == 0 or min(np.count_nonzero(mask_a), np.count_nonzero(mask_b)) < 4:
            raise ValueError('insufficient HDR voxels for shape comparison')
        out[f'{label}_voxel_iou_loss'] = float(
            1 - np.count_nonzero(mask_a & mask_b) / union)
        points_a, points_b = xyz[mask_a], xyz[mask_b]
        cov_a = np.cov(points_a, rowvar=False, bias=True)
        cov_b = np.cov(points_b, rowvar=False, bias=True)
        cov_a /= np.trace(cov_a)
        cov_b /= np.trace(cov_b)
        out[f'{label}_shape_tensor_diff'] = float(np.linalg.norm(cov_b-cov_a, ord='fro'))
        out[f'_num_{label}_coverage_error_a'] = float(measured['A']['coverage_error'])
        out[f'_num_{label}_coverage_error_b'] = float(measured['B']['coverage_error'])
    return out


def pilot_record(case: str, replicate: int, *, n_mc: int = 8000,
                 hdr_grid: int = 35) -> dict:
    pair = independent_pair(case, replicate, split='calibration')
    fa, fb = estimate_pair(pair)
    baseline = baseline_features(pair, fa, fb, n_mc=n_mc)
    hdr = hdr_features(pair, fa, fb, grid_n=hdr_grid,
                       cutoff_n=n_mc, cover_n=n_mc)
    return {
        'status': 'ENGINEERING_ONLY', 'case': case, 'replicate': replicate,
        'split': pair.split, 'n_per_arm': N_PER_ARM,
        'samples_sha256': {'A': pair.a_sha256, 'B': pair.b_sha256},
        'seeds': {'nuisance': pair.design_seed,
                  'sample_A': pair.a_seed, 'sample_B': pair.b_seed},
        'fit': {side: {
            'converged': obj.converged, 'iterations': obj.iterations,
            'min_weight': obj.min_weight, 'max_condition_number': obj.max_condition_number,
            'warnings': list(obj.warnings)
        } for side, obj in (('A', fa), ('B', fb))},
        'baseline': {k: v for k, v in baseline.items() if not k.startswith('_num_')},
        'hdr': {k: v for k, v in hdr.items() if not k.startswith('_num_')},
        'numerical_diagnostics': {k: v for block in (baseline, hdr)
                                  for k, v in block.items() if k.startswith('_num_')},
    }
