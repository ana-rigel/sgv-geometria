"""SGV-C01 phase I: analytic 3-D Gaussian-mixture oracle and HDR instrumentation.

No market inputs. Fisher-Rao here is AMBIENT (square-root embedding), not
an intrinsic geodesic constrained to the Gaussian-mixture submanifold.
All samples are synthetic, and the classification holdout is not accessed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import numpy as np
from scipy.special import logsumexp
from scipy.spatial.distance import cdist
from scipy.stats import multivariate_normal


@dataclass(frozen=True)
class GMM3:
    weights: np.ndarray
    means: np.ndarray
    covs: np.ndarray

    def __post_init__(self):
        w = np.asarray(self.weights, dtype=float)
        m = np.asarray(self.means, dtype=float)
        c = np.asarray(self.covs, dtype=float)
        if w.ndim != 1 or len(w) < 1 or m.shape != (len(w), 3) or c.shape != (len(w), 3, 3):
            raise ValueError('invalid three-dimensional Gaussian mixture shapes')
        if not all(np.isfinite(z).all() for z in (w, m, c)):
            raise ValueError('non-finite parameters')
        if np.any(w <= 0) or not np.isclose(np.sum(w), 1, rtol=0, atol=1e-12):
            raise ValueError('strictly positive weights must sum to one')
        if not np.allclose(c, np.swapaxes(c, 1, 2), atol=1e-12):
            raise ValueError('covariances must be symmetric')
        if np.any(np.linalg.eigvalsh(c) <= 1e-10):
            raise ValueError('covariances must be positive definite')
        for k, value in [('weights', w), ('means', m), ('covs', c)]:
            value = np.array(value, copy=True)
            value.setflags(write=False)
            object.__setattr__(self, k, value)

    def logpdf(self, points: np.ndarray) -> np.ndarray:
        x = np.asarray(points, dtype=float)
        if x.ndim != 2 or x.shape[-1] != 3:
            raise ValueError('points must have shape (n, 3)')
        terms = [np.log(w) + np.atleast_1d(multivariate_normal.logpdf(x, mean=mu, cov=cov))
                 for w, mu, cov in zip(self.weights, self.means, self.covs)]
        return logsumexp(np.stack(terms, axis=0), axis=0)

    def sample(self, count: int, rng: np.random.Generator) -> np.ndarray:
        if count < 1:
            raise ValueError('sample count must be positive')
        ids = rng.choice(len(self.weights), size=count, p=self.weights)
        out = np.empty((count, 3))
        for k, (mu, cov) in enumerate(zip(self.means, self.covs)):
            idx = np.flatnonzero(ids == k)
            if len(idx):
                out[idx] = rng.multivariate_normal(mu, cov, size=len(idx))
        return out

    def moments(self) -> tuple[np.ndarray, np.ndarray]:
        mu = self.weights @ self.means
        dif = self.means - mu
        cov = np.einsum('k,kij->ij', self.weights, self.covs)
        cov += np.einsum('k,ki,kj->ij', self.weights, dif, dif)
        return mu, cov

    def affine(self, matrix: np.ndarray, shift: np.ndarray | Sequence[float] = (0., 0., 0.)) -> 'GMM3':
        a = np.asarray(matrix, dtype=float)
        b = np.asarray(shift, dtype=float)
        if a.shape != (3, 3) or b.shape != (3,) or abs(np.linalg.det(a)) < 1e-9:
            raise ValueError('invertible 3x3 affine map required')
        return GMM3(self.weights, self.means @ a.T + b,
                    np.einsum('ij,kjl,ml->kim', a, self.covs, a))


def base_model(axis: int = 0, amplitude: float = .85) -> GMM3:
    if axis not in (0, 1, 2) or not 0 < amplitude < 1:
        raise ValueError('invalid axis or amplitude')
    e = np.eye(3)[axis]
    component_cov = np.eye(3) - amplitude**2 * np.outer(e, e)
    return GMM3(np.array([.5, .5]), np.array([amplitude*e, -amplitude*e]),
                np.array([component_cov, component_cov]))


def known_pair(kind: str, nuisance_seed: int | None = None) -> tuple[GMM3, GMM3]:
    """Engineering generator only; NOT a sealed inference/test sampler."""
    p = base_model()
    if kind == 'T0':
        q = base_model()
    elif kind == 'T1':
        q = p.affine(np.eye(3), (0., .65, 0.))
    elif kind == 'T2':
        q = p.affine(1.25 * np.eye(3))
    elif kind == 'T3':
        q = p.affine(np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]]))
    elif kind == 'T4':
        q = p.affine(np.array([[1., .55, 0.], [0., 1., 0.], [0., 0., 1.]]))
    elif kind == 'T5':
        q = GMM3(np.array([.8, .2]), p.means, p.covs)
    elif kind == 'T6':
        q = GMM3(np.array([.475, .475, .05]),
                 np.concatenate((p.means, np.array([[2.8, 0., 0.]]))),
                 np.concatenate((p.covs, np.array([.35**2 * np.eye(3)]))))
    else:
        raise ValueError('unknown case label')
    if nuisance_seed is not None:
        rng = np.random.default_rng(nuisance_seed)
        u = rng.normal(size=(3, 3))
        rot, r = np.linalg.qr(u)
        rot = rot @ np.diag(np.sign(np.diag(r)))
        if np.linalg.det(rot) < 0:
            rot[:, 0] *= -1
        transform = rot * rng.uniform(.9, 1.1)
        shift = rng.uniform(-.25, .25, size=3)
        p, q = p.affine(transform, shift), q.affine(transform, shift)
    return p, q


def entropy_mc(p: GMM3, *, n: int, seed: int) -> tuple[float, float]:
    x = p.sample(n, np.random.default_rng(seed))
    z = -p.logpdf(x)
    return float(np.mean(z)), float(np.std(z, ddof=1) / np.sqrt(n))


def delta_entropy_mc(p: GMM3, q: GMM3, *, n: int, seed: int) -> tuple[float, float]:
    a, ea = entropy_mc(p, n=n, seed=seed)
    b, eb = entropy_mc(q, n=n, seed=seed+1)
    return b-a, float(np.hypot(ea, eb))


def fr_covariance(p: GMM3, q: GMM3) -> float:
    """Fisher distance of centered GAUSSIAN SURROGATES, covariances only."""
    _, sa = p.moments()
    _, sb = q.moments()
    inv_chol = np.linalg.solve(np.linalg.cholesky(sa), np.eye(3))
    lam = np.linalg.eigvalsh(inv_chol @ sb @ inv_chol.T)
    return float(np.sqrt(.5 * np.sum(np.log(lam)**2)))


def fr_ambient_mc(p: GMM3, q: GMM3, *, n: int, seed: int) -> dict:
    """Ambient Fisher-Rao 2 arccos affinity, stratified importance MC.

    The error of d near affinity=1 is nonlinear; return error of affinity,
    not an invalid symmetric SE of d. Purely numerical bounds apply.
    """
    if n < 4 or n % 2:
        raise ValueError('even n >= 4 required')
    rng = np.random.default_rng(seed)
    x = np.vstack((p.sample(n//2, rng), q.sample(n//2, rng)))
    lp, lq = p.logpdf(x), q.logpdf(x)
    weights = np.exp(.5*(lp+lq) - np.logaddexp(lp, lq) + np.log(2.))
    # Two independent strata, not n iid mixture draws; variance is within-strata.
    left, right = weights[:n//2], weights[n//2:]
    affinity = float((left.mean()+right.mean())/2)
    se = float(np.sqrt((left.var(ddof=1)+right.var(ddof=1))/(2*n)))
    if affinity > 1.0 + 1e-10 or affinity < -1e-10:
        raise ValueError('affinity outside [0, 1] beyond floating precision')
    return {'affinity': affinity, 'affinity_se': se,
            'fr_ambient': float(2 * np.arccos(np.clip(affinity, 0, 1))),
            'n': n, 'convention': '2 arccos affinity; ambient density sphere'}


def energy_distance(x: np.ndarray, y: np.ndarray) -> float:
    """V-statistic energy distance, same convention as M15, not squared metric."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if x.ndim != 2 or x.shape[1] != 3 or y.ndim != 2 or y.shape[1] != 3:
        raise ValueError('X and Y must have shape (n,3)')
    return float(2*cdist(x, y).mean() - cdist(x, x).mean() - cdist(y, y).mean())


def common_bounds(p: GMM3, q: GMM3, *, sigmas: float = 5.) -> tuple[np.ndarray, np.ndarray]:
    lo, hi = [], []
    for z in (p, q):
        s = np.sqrt(np.diagonal(z.covs, axis1=1, axis2=2))
        lo.append(np.min(z.means - sigmas*s, axis=0))
        hi.append(np.max(z.means + sigmas*s, axis=0))
    return np.minimum.reduce(lo), np.maximum.reduce(hi)


def hdr_measure(p: GMM3, *, alpha: float, seed: int, grid_n: int = 35,
                cutoff_n: int = 16000, cover_n: int = 16000,
                bounds: tuple[np.ndarray, np.ndarray] | None = None) -> dict:
    """MC cutoff + independent coverage; marching-cubes closed shell geometry.

    Does NOT establish model-parameter uncertainty or inferential null validity.
    """
    from skimage.measure import marching_cubes
    import trimesh
    if not 0 < alpha < 1 or grid_n < 16 or cutoff_n < 20 or cover_n < 20:
        raise ValueError('invalid HDR settings')
    if bounds is None:
        bounds = common_bounds(p, p)
    lo, hi = [np.asarray(v, dtype=float) for v in bounds]
    if lo.shape != (3,) or hi.shape != (3,) or np.any(hi <= lo):
        raise ValueError('invalid coordinate bounds')
    calib = p.sample(cutoff_n, np.random.default_rng(seed))
    threshold_log = float(np.quantile(p.logpdf(calib), 1.0-alpha))
    heldout = p.sample(cover_n, np.random.default_rng(seed+1))
    covered = float(np.mean(p.logpdf(heldout) >= threshold_log))
    axes = [np.linspace(lo[i], hi[i], grid_n) for i in range(3)]
    xyz = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1).reshape(-1, 3)
    field = p.logpdf(xyz).reshape((grid_n,)*3)
    mask = field >= threshold_log
    touches = bool(any(np.any(np.take(mask, j, axis=i)) for i in range(3) for j in (0, grid_n-1)))
    if not np.any(mask) or np.all(mask) or touches:
        raise ValueError('HDR mesh absent or domain-truncated: fail closed')
    step = (hi-lo)/(grid_n-1)
    verts, faces, _, _ = marching_cubes(field, level=threshold_log, spacing=tuple(step))
    verts += lo
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    if not mesh.is_watertight:
        raise ValueError('HDR triangulation not watertight')
    volume = float(abs(mesh.volume))
    if not np.isfinite(volume) or volume <= 0:
        raise ValueError('invalid HDR volume')
    components = trimesh.graph.connected_components(mesh.face_adjacency, nodes=np.arange(len(faces)))
    return {'alpha': alpha, 'log_threshold': threshold_log, 'coverage': covered,
            'coverage_error': covered-alpha, 'grid_n': grid_n,
            'volume': volume, 'area': float(mesh.area),
            'center': mesh.center_mass.tolist(), 'components': len(components),
            'n_faces': int(len(faces)), 'is_watertight': bool(mesh.is_watertight),
            'touches_boundary': touches, 'bounds': [lo.tolist(), hi.tolist()]}


def hdr_pair(p: GMM3, q: GMM3, *, alpha: float, seed: int, grid_n: int = 35,
             cutoff_n: int = 16000, cover_n: int = 16000) -> dict:
    domain = common_bounds(p, q)
    a = hdr_measure(p, alpha=alpha, seed=seed, grid_n=grid_n,
                    cutoff_n=cutoff_n, cover_n=cover_n, bounds=domain)
    b = hdr_measure(q, alpha=alpha, seed=seed+1000, grid_n=grid_n,
                    cutoff_n=cutoff_n, cover_n=cover_n, bounds=domain)
    return {'A': a, 'B': b, 'center_distance': float(np.linalg.norm(np.array(b['center'])-a['center'])),
            'log_volume_ratio': float(np.log(b['volume']/a['volume'])),
            'log_area_ratio': float(np.log(b['area']/a['area'])),
            'delta_components': b['components'] - a['components']}
