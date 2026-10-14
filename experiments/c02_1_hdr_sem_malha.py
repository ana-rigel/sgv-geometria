"""SGV-C02.1: HDR descriptors without grid, voxels or mesh (HDR12-ML).

Protocol: reports/PROTOCOLO_SGV_C02_1_EMENDA_HDR_SEM_MALHA_20261014.md (registered
before this code). Regions are the same as C01: R_alpha(p) = {x : log p(x) >= tau},
tau = (1-alpha) quantile of log p over samples of p. Lebesgue integrals use
importance sampling with the fitted density itself; inside R_alpha the weight
1/p is bounded by 1/tau, so the estimators have finite variance. Only
`w2_hdr` uses the observed A/B draws (ranked by the fitted density), like
`energy` in the C01 base block. Synthetic use only; no market data.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

from experiments.c01_oraculo_hdr_fisher import GMM3

ALPHAS = (0.50, 0.95)
N_CUT = 32_000
N_COVER = 32_000
N_VOL = 32_000
N_JAC = 32_000
N_CROSS = 32_000
COVERAGE_TOL = 0.015
MIN_ESS = 2_000
FEATURES = ('center_distance', 'log_volume_ratio', 'jaccard_loss',
            'shape_tensor_diff', 'w2_hdr', 'cross_mass_shift')


def feature_names(include_w2: bool = True) -> tuple[str, ...]:
    return tuple(f'hdr{int(a * 100)}_{f}' for a in ALPHAS for f in FEATURES
                 if include_w2 or f != 'w2_hdr')


def subseed(base: int, purpose: str) -> int:
    """Stable SHA-256 seed per purpose (same style as C01/C02 namespaces)."""
    if not isinstance(purpose, str) or not purpose:
        raise ValueError('purpose required')
    msg = f'C02.1|{int(base)}|{purpose}'.encode('utf-8')
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], 'big')


def _rng(base: int, purpose: str) -> np.random.Generator:
    return np.random.default_rng(subseed(base, purpose))


@dataclass(frozen=True)
class Region:
    alpha: float
    log_tau: float
    coverage: float
    volume: float
    centroid: np.ndarray
    shape: np.ndarray        # trace-normalised covariance of the uniform measure on R
    ess: float


def region(p: GMM3, alpha: float, *, seed: int, scale: int = 1) -> Region:
    """Threshold, held-out coverage and uniform-measure statistics of R_alpha(p)."""
    if not 0 < alpha < 1:
        raise ValueError('alpha must be in (0, 1)')
    tag = f'{alpha:.2f}'
    cut = p.sample(N_CUT * scale, _rng(seed, f'cut|{tag}'))
    log_tau = float(np.quantile(p.logpdf(cut), 1.0 - alpha))
    held = p.sample(N_COVER * scale, _rng(seed, f'cover|{tag}'))
    coverage = float(np.mean(p.logpdf(held) >= log_tau))
    x = p.sample(N_VOL * scale, _rng(seed, f'vol|{tag}'))
    lp = p.logpdf(x)
    inside = lp >= log_tau
    if inside.sum() < 10:
        raise ValueError('HDR region empty under sampling: fail closed')
    w = np.zeros(len(x))
    w[inside] = np.exp(-lp[inside])            # 1/p, bounded by 1/tau inside R
    volume = float(w.mean())
    wi = w[inside]
    ess = float(wi.sum() ** 2 / np.sum(wi ** 2))
    xi = x[inside]
    centroid = (wi[:, None] * xi).sum(0) / wi.sum()
    d = xi - centroid
    cov = (wi[:, None, None] * np.einsum('ni,nj->nij', d, d)).sum(0) / wi.sum()
    return Region(alpha, log_tau, coverage, volume, centroid, cov / np.trace(cov), ess)


def jaccard_loss(p: GMM3, q: GMM3, ra: Region, rb: Region, *, seed: int, scale: int = 1) -> float:
    """1 - V(R_A ∩ R_B)/V(R_A ∪ R_B), deterministic-mixture importance sampling."""
    half = N_JAC * scale // 2
    tag = f'{ra.alpha:.2f}'
    x = np.vstack((p.sample(half, _rng(seed, f'jacA|{tag}')), q.sample(half, _rng(seed, f'jacB|{tag}'))))
    lp, lq = p.logpdf(x), q.logpdf(x)
    lm = np.logaddexp(lp, lq) - np.log(2.0)
    in_a, in_b = lp >= ra.log_tau, lq >= rb.log_tau
    w = np.exp(-lm)
    union = float(np.mean((in_a | in_b) * w))
    if union <= 0:
        raise ValueError('empty HDR union: fail closed')
    return float(1.0 - np.mean((in_a & in_b) * w) / union)


def cross_mass_shift(p: GMM3, q: GMM3, ra: Region, rb: Region, *, seed: int, scale: int = 1) -> float:
    """½(|Q(R_A) − α| + |P(R_B) − α|): mass each density puts in the other's HDR."""
    tag = f'{ra.alpha:.2f}'
    xq = q.sample(N_CROSS * scale, _rng(seed, f'crossQ|{tag}'))
    xp = p.sample(N_CROSS * scale, _rng(seed, f'crossP|{tag}'))
    q_in_a = float(np.mean(p.logpdf(xq) >= ra.log_tau))
    p_in_b = float(np.mean(q.logpdf(xp) >= rb.log_tau))
    return 0.5 * (abs(q_in_a - ra.alpha) + abs(p_in_b - rb.alpha))


def w2_hdr(a_obs: np.ndarray, b_obs: np.ndarray, p: GMM3, q: GMM3, alpha: float) -> float:
    """Exact W2^2 between the observations inside each arm's own sample HDR.

    Each arm keeps its floor(alpha·n) observations of highest fitted density;
    both are expressed in the frame whitened by A's sample mean and covariance.
    No Monte Carlo: deterministic given the fits.
    """
    a = np.asarray(a_obs, float)
    b = np.asarray(b_obs, float)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 3:
        raise ValueError('A and B observations must both have shape (n, 3)')
    k = int(np.floor(alpha * len(a)))
    if k < 10:
        raise ValueError('too few observations inside the sample HDR')
    ka = a[np.argsort(-p.logpdf(a), kind='stable')[:k]]
    kb = b[np.argsort(-q.logpdf(b), kind='stable')[:k]]
    mu = a.mean(0)
    li = np.linalg.inv(np.linalg.cholesky(np.cov(a, rowvar=False))).T
    cost = cdist((ka - mu) @ li, (kb - mu) @ li, 'sqeuclidean')
    r, c = linear_sum_assignment(cost)
    return float(cost[r, c].mean())


def hdr12_ml(a_obs: np.ndarray, b_obs: np.ndarray, p: GMM3, q: GMM3, *, seed: int,
             scale: int = 1) -> dict[str, float]:
    """HDR12-ML block plus `_num_*` diagnostics; raises on any fail-closed condition."""
    if scale not in (1, 2):
        raise ValueError('scale is 1 (production budget) or 2 (precision gate)')
    out: dict[str, float] = {}
    _, cov_a = p.moments()
    s_a = float(np.sqrt(np.trace(cov_a) / 3))
    for alpha in ALPHAS:
        lab = f'hdr{int(alpha * 100)}'
        ra = region(p, alpha, seed=subseed(seed, f'A|{alpha}'), scale=scale)
        rb = region(q, alpha, seed=subseed(seed, f'B|{alpha}'), scale=scale)
        out[f'{lab}_center_distance'] = float(np.linalg.norm(rb.centroid - ra.centroid))
        out[f'{lab}_log_volume_ratio'] = float(np.log(rb.volume) - np.log(ra.volume))
        out[f'{lab}_jaccard_loss'] = jaccard_loss(p, q, ra, rb, seed=subseed(seed, f'J|{alpha}'), scale=scale)
        out[f'{lab}_shape_tensor_diff'] = float(np.linalg.norm(rb.shape - ra.shape, ord='fro'))
        out[f'{lab}_w2_hdr'] = w2_hdr(a_obs, b_obs, p, q, alpha)
        out[f'{lab}_cross_mass_shift'] = cross_mass_shift(p, q, ra, rb, seed=subseed(seed, f'X|{alpha}'), scale=scale)
        out[f'_num_{lab}_coverage_error_a'] = ra.coverage - alpha
        out[f'_num_{lab}_coverage_error_b'] = rb.coverage - alpha
        out[f'_num_{lab}_ess_a'] = ra.ess
        out[f'_num_{lab}_ess_b'] = rb.ess
    out['_num_scale_a'] = s_a
    return out


def precision_checks(run1: dict[str, float], run2: dict[str, float]) -> list[str]:
    """Return the list of failed checks of the C02.1 precision gate (empty = pass)."""
    fails: list[str] = []
    s_a = run1['_num_scale_a']
    for alpha in ALPHAS:
        lab = f'hdr{int(alpha * 100)}'
        for run, tag in ((run1, 'r1'), (run2, 'r2')):
            for side in ('a', 'b'):
                if abs(run[f'_num_{lab}_coverage_error_{side}']) > COVERAGE_TOL:
                    fails.append(f'{lab}:{tag}:coverage_{side}')
                if run[f'_num_{lab}_ess_{side}'] < MIN_ESS:
                    fails.append(f'{lab}:{tag}:ess_{side}')
        d = lambda f: abs(run1[f'{lab}_{f}'] - run2[f'{lab}_{f}'])  # noqa: E731
        if d('log_volume_ratio') > 0.05:
            fails.append(f'{lab}:log_volume_ratio')
        if d('center_distance') > 0.10 * max(run1[f'{lab}_center_distance'], 0.10 * s_a):
            fails.append(f'{lab}:center_distance')
        if d('jaccard_loss') > 0.02:
            fails.append(f'{lab}:jaccard_loss')
        if d('shape_tensor_diff') > 0.02:
            fails.append(f'{lab}:shape_tensor_diff')
        if d('cross_mass_shift') > 0.01:
            fails.append(f'{lab}:cross_mass_shift')
        if not np.isfinite(run1[f'{lab}_w2_hdr']) or run1[f'{lab}_w2_hdr'] != run2[f'{lab}_w2_hdr']:
            fails.append(f'{lab}:w2_hdr')
    return fails


# ---------------------------------------------------------------------------
# C02.1a (errata registrada em reports/PROTOCOLO_SGV_C02_1A_ERRATA_20261014.md)
# ---------------------------------------------------------------------------
UNIFORM_FEATURES = ('center_distance', 'log_volume_ratio', 'shape_tensor_diff')
N_BOOT = 5
MIN_RELIABILITY = 0.5


def envelope_core(x: np.ndarray) -> float:
    """log(q95/q50) of Mahalanobis radii in the sample's OWN mean/covariance (linear, no ranks)."""
    x = np.asarray(x, float)
    li = np.linalg.inv(np.linalg.cholesky(np.cov(x, rowvar=False))).T
    r = np.linalg.norm((x - x.mean(0)) @ li, axis=1)
    return float(np.log(np.quantile(r, 0.95) / np.quantile(r, 0.50)))


def envelope_core_delta(a_obs: np.ndarray, b_obs: np.ndarray) -> float:
    return envelope_core(b_obs) - envelope_core(a_obs)


def reliability(main: np.ndarray, boot: np.ndarray) -> float:
    """1 − mean within-pair refit variance / between-pair variance (one family, one feature).

    main: (n_pairs,) values from the main fit; boot: (n_pairs, N_BOOT) refit values.
    """
    main = np.asarray(main, float)
    boot = np.asarray(boot, float)
    total = np.var(main, ddof=1)
    noise = np.mean(np.var(boot, axis=1, ddof=1))
    return float(1.0 - noise / total) if total > 0 else float('-inf')


def precision_checks_a(run1: dict[str, float], run2: dict[str, float], retained: set[str]) -> list[str]:
    """C02.1a precision gate on the retained features (empty list = pass)."""
    fails: list[str] = []
    s_a = run1['_num_scale_a']
    for alpha in ALPHAS:
        lab = f'hdr{int(alpha * 100)}'
        uses_uniform = any(f'{lab}_{f}' in retained for f in UNIFORM_FEATURES)
        for run, tag in ((run1, 'r1'), (run2, 'r2')):
            for side in ('a', 'b'):
                if abs(run[f'_num_{lab}_coverage_error_{side}']) > COVERAGE_TOL:
                    fails.append(f'{lab}:{tag}:coverage_{side}')
                if uses_uniform and run[f'_num_{lab}_ess_{side}'] < MIN_ESS:
                    fails.append(f'{lab}:{tag}:ess_{side}')
        d = lambda f: abs(run1[f'{lab}_{f}'] - run2[f'{lab}_{f}'])  # noqa: E731
        lim = {'log_volume_ratio': float(np.log(1.10)),
               'center_distance': max(0.10 * run1[f'{lab}_center_distance'], 0.05 * s_a),
               'jaccard_loss': 0.02, 'shape_tensor_diff': 0.02, 'cross_mass_shift': 0.01}
        for f, tol in lim.items():
            if f'{lab}_{f}' in retained and d(f) > tol:
                fails.append(f'{lab}:{f}')
        k = f'{lab}_w2_hdr'
        if k in retained and (not np.isfinite(run1[k]) or run1[k] != run2[k]):
            fails.append(f'{lab}:w2_hdr')
    return fails
