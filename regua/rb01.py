"""RB-01: régua bruta para cascas HDR50/HDR95 sob caudas pesadas (protocolo PROTOCOLO_REGUA_BRUTA.md).

Só sintéticos. Todas as regiões são R_a = {x : log p(x) >= log tau}; volume, centro e forma por
amostragem de importância com a própria densidade (método do C02.1), sem malha.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
from scipy import stats
from scipy.special import gammaln, logsumexp
from scipy.stats import gaussian_kde
from sklearn.mixture import GaussianMixture

D = 3
ALPHAS = (0.50, 0.95)
SEED_GMM = 20261009
N_WINDOW = 1500
N_CUT = 20_000      # amostras de p̂ para o limiar de Hyndman
N_HELD = 20_000     # amostras de p̂ para a massa interna
N_VOL = 20_000      # amostras de p̂ para volume/centro/forma
N_TRUE_EVAL = 20_000  # amostras da verdade para P_true(R̂)
N_TRUTH = 200_000   # amostras da verdade para tau/volume verdadeiros


def subseed(*parts) -> int:
    msg = "RB-01|" + "|".join(str(p) for p in parts)
    return int.from_bytes(hashlib.sha256(msg.encode()).digest()[:8], "big")


def rng(*parts) -> np.random.Generator:
    return np.random.default_rng(subseed(*parts))


# ----------------------------------------------------------------------------- densidades verdadeiras
class Dist:
    def logpdf(self, x): raise NotImplementedError
    def sample(self, n, g): raise NotImplementedError


class MVN(Dist):
    def __init__(self, mean, cov):
        self.mean, self.cov = np.asarray(mean, float), np.asarray(cov, float)
        self._d = stats.multivariate_normal(self.mean, self.cov)
    def logpdf(self, x): return self._d.logpdf(x)
    def sample(self, n, g): return g.multivariate_normal(self.mean, self.cov, n)


class MVT(Dist):
    def __init__(self, loc, shape, df):
        self.loc, self.shape, self.df = np.asarray(loc, float), np.asarray(shape, float), float(df)
        self._d = stats.multivariate_t(self.loc, self.shape, df=self.df)
        self._L = np.linalg.cholesky(self.shape)
    def logpdf(self, x): return self._d.logpdf(x)
    def sample(self, n, g):
        z = g.standard_normal((n, D)) @ self._L.T
        w = g.chisquare(self.df, n) / self.df
        return self.loc + z / np.sqrt(w)[:, None]


class IndepJSU(Dist):
    """Eixos independentes Johnson SU (assimetria + cauda pesada)."""
    def __init__(self, a, b):
        self.m = [stats.johnsonsu(ai, bi) for ai, bi in zip(a, b)]
    def logpdf(self, x): return sum(m.logpdf(x[:, j]) for j, m in enumerate(self.m))
    def sample(self, n, g): return np.column_stack([m.rvs(n, random_state=g) for m in self.m])


class Affine(Dist):
    """Y = c + M (X - c) + t."""
    def __init__(self, base, M, c, t=None):
        self.base, self.M, self.c = base, np.asarray(M, float), np.asarray(c, float)
        self.t = np.zeros(D) if t is None else np.asarray(t, float)
        self.Minv = np.linalg.inv(self.M)
        self.logdet = float(np.linalg.slogdet(self.M)[1])
    def logpdf(self, y):
        x = (y - self.c - self.t) @ self.Minv.T + self.c
        return self.base.logpdf(x) - self.logdet
    def sample(self, n, g):
        return (self.base.sample(n, g) - self.c) @ self.M.T + self.c + self.t


class Mix(Dist):
    def __init__(self, comps, w):
        self.comps, self.w = comps, np.asarray(w, float) / np.sum(w)
    def logpdf(self, x):
        return logsumexp(np.column_stack([np.log(w) + c.logpdf(x) for c, w in zip(self.comps, self.w)]), axis=1)
    def sample(self, n, g):
        k = g.choice(len(self.comps), n, p=self.w)
        out = np.empty((n, D))
        for i, c in enumerate(self.comps):
            idx = np.flatnonzero(k == i)
            if len(idx):
                out[idx] = c.sample(len(idx), g)
        return out


def rotation(axis, deg):
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    th = np.deg2rad(deg)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


R0 = rotation([1, 2, 3], 35.0)                      # eixos girados, fixos
COV0 = R0 @ np.diag([1.0, 0.55, 0.30]) @ R0.T       # autovalores distintos
FAMILIES = ("F0", "F1", "F2", "F3", "F4", "F5")
CASES = ("nulo", "translacao", "expansao", "rotacao", "anisotropia", "caudas05", "caudas10", "caudas20")


def family_base(fam: str) -> Dist:
    if fam == "F0":
        return MVN(np.zeros(3), COV0)
    if fam in ("F1", "F2", "F3"):
        nu = {"F1": 5.0, "F2": 3.5, "F3": 3.0}[fam]
        return MVT(np.zeros(3), COV0, nu)          # matriz de forma = COV0
    if fam == "F4":
        base = IndepJSU(a=[-1.0, 0.6, -0.4], b=[1.3, 1.6, 1.4])
        L = R0 @ np.diag(np.sqrt([1.0, 0.55, 0.30]))
        return Affine(base, L, np.zeros(3))
    if fam == "F5":
        u = R0[:, 0]
        return Mix([MVT(-1.2 * u, 0.5 * COV0, 4.0), MVT(1.2 * u, 0.5 * COV0, 4.0)], [0.6, 0.4])
    raise ValueError(fam)


@dataclass
class FamilySetup:
    fam: str
    A: Dist           # A já na régua orig_raw
    cases: dict       # caso -> B na régua orig_raw
    ruler: tuple      # (mediana, escala) orig_raw
    ruler_flow: tuple  # (mediana, escala) flow_raw (1,4826·MAD), relativa às unidades base


def build_family(fam: str) -> FamilySetup:
    base = family_base(fam)
    anchor = base.sample(40_000, rng(fam, "ancora"))
    med = np.median(anchor, 0)
    esc = np.quantile(np.abs(anchor - med), 0.995, axis=0) / 3.0
    mad = 1.4826 * np.median(np.abs(anchor - med), 0)
    c = anchor.mean(0)
    cov = np.cov(anchor, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    u = evecs[:, -1]                                  # eixo principal
    sd_u = float(np.sqrt(u @ cov @ u))
    B = {
        "nulo": base,
        "translacao": Affine(base, np.eye(3), c, 0.5 * sd_u * u),
        "expansao": Affine(base, 1.25 * np.eye(3), c),
        "rotacao": Affine(base, rotation(evecs[:, 0], 30.0), c),
        "anisotropia": Affine(base, np.eye(3) + 0.4 * np.outer(u, u), c),
    }
    for eps, key in ((0.05, "caudas05"), (0.10, "caudas10"), (0.20, "caudas20")):
        B[key] = Mix([base, Affine(base, 3.0 * np.eye(3), c)], [1 - eps, eps])
    to_ruler = lambda d: Affine(d, np.diag(1 / esc), med, -med)   # y = (x - med)/esc
    return FamilySetup(fam, to_ruler(base), {k: to_ruler(v) for k, v in B.items()}, (med, esc), (med, mad))


# ----------------------------------------------------------------------------- modelos candidatos
class Model:
    name = "?"
    def logpdf(self, x): raise NotImplementedError
    def sample(self, n, g): raise NotImplementedError


class GMMModel(Model):
    def __init__(self, x, k, seed=SEED_GMM):
        self.gm = GaussianMixture(n_components=k, covariance_type="full", reg_covar=1e-4,
                                  max_iter=100, n_init=2, random_state=seed).fit(x)
        self.w, self.mu, self.cov = self.gm.weights_, self.gm.means_, self.gm.covariances_
        self.L = np.linalg.cholesky(self.cov)
    def logpdf(self, x): return self.gm.score_samples(x)
    def density(self, x): return np.exp(self.logpdf(x))
    def sample(self, n, g):
        k = g.choice(len(self.w), n, p=self.w)
        z = g.standard_normal((n, D))
        return self.mu[k] + np.einsum("nij,nj->ni", self.L[k], z)


def _mvt_logpdf(x, mu, S, nu):
    L = np.linalg.cholesky(S)
    z = np.linalg.solve(L, (x - mu).T)
    delta = (z ** 2).sum(0)
    logdet = 2 * np.log(np.diag(L)).sum()
    return (gammaln((nu + D) / 2) - gammaln(nu / 2) - 0.5 * D * np.log(nu * np.pi) - 0.5 * logdet
            - 0.5 * (nu + D) * np.log1p(delta / nu)), delta


class TMixModel(Model):
    NU_GRID = (2.5, 3.0, 4.0, 6.0, 10.0, 30.0)
    def __init__(self, x, k=2, seed=SEED_GMM, max_iter=200, tol=1e-6):
        init = GaussianMixture(n_components=k, covariance_type="full", reg_covar=1e-4,
                               max_iter=100, n_init=2, random_state=seed).fit(x)
        best = None
        for nu in self.NU_GRID:
            w, mu, S = init.weights_.copy(), init.means_.copy(), init.covariances_.copy()
            prev = -np.inf
            converged = False
            for _ in range(max_iter):
                lp = np.empty((len(x), k)); dl = np.empty((len(x), k))
                for j in range(k):
                    lp[:, j], dl[:, j] = _mvt_logpdf(x, mu[j], S[j], nu)
                lp += np.log(w)
                ll = logsumexp(lp, axis=1)
                r = np.exp(lp - ll[:, None])
                tot = ll.sum()
                uu = (nu + D) / (nu + dl)
                for j in range(k):
                    rj, ruj = r[:, j], r[:, j] * uu[:, j]
                    w[j] = rj.mean()
                    mu[j] = (ruj[:, None] * x).sum(0) / ruj.sum()
                    d = x - mu[j]
                    S[j] = (ruj[:, None, None] * np.einsum("ni,nj->nij", d, d)).sum(0) / rj.sum() + 1e-4 * np.eye(D)
                if abs(tot - prev) < tol * abs(tot):
                    converged = True
                    break
                prev = tot
            if best is None or tot > best[0]:
                best = (tot, nu, w.copy(), mu.copy(), S.copy(), converged)
        _, self.nu, self.w, self.mu, self.S, self.converged = best
        self.L = np.linalg.cholesky(self.S)
    def logpdf(self, x):
        return logsumexp(np.column_stack([np.log(w) + _mvt_logpdf(x, m, S, self.nu)[0]
                                          for w, m, S in zip(self.w, self.mu, self.S)]), axis=1)
    def sample(self, n, g):
        k = g.choice(len(self.w), n, p=self.w)
        z = np.einsum("nij,nj->ni", self.L[k], g.standard_normal((n, D)))
        s = g.chisquare(self.nu, n) / self.nu
        return self.mu[k] + z / np.sqrt(s)[:, None]


class KDEModel(Model):
    def __init__(self, x):
        self.k = gaussian_kde(x.T, bw_method="scott")
    def logpdf(self, x): return self.k.logpdf(x.T)
    def sample(self, n, g): return self.k.resample(n, seed=g).T


# ----------------------------------------------------------------------------- limiares
class Invalid(Exception):
    pass


def tau_hyndman(m: Model, alpha: float, g) -> float:
    return float(np.quantile(m.logpdf(m.sample(N_CUT, g)), 1.0 - alpha))


def _grid(n, extent):
    axis = np.linspace(-extent, extent, n)
    dx = float(axis[1] - axis[0])
    pts = np.stack(np.meshgrid(axis, axis, axis, indexing="ij"), -1).reshape(-1, 3)
    return pts, dx


def tau_grid_vendor(m: GMMModel, alpha: float) -> float:
    """Reprodução fiel das regras do vendor (build_shell para 50; hdr_mesh com 61³ ±10 para 95)."""
    if alpha == 0.50:
        n, ext, lo, hi = 25, 3.5, 0.95, 1.05
    else:
        n, ext, lo, hi = 61, 10.0, 0.99, 1.01
    pts, dx = _grid(n, ext)
    field = m.density(pts)
    cover = float(field.sum() * dx ** 3)
    if not lo <= cover <= hi:
        raise Invalid(f"cobertura_{int(alpha*100)}:{cover:.4f}")
    ordered = np.sort(field)[::-1]
    frac = np.cumsum(ordered) / ordered.sum()
    i = int(np.searchsorted(frac, alpha, side="left"))
    if i + 1 >= len(ordered):
        raise Invalid("limiar_fora")
    tau = float((ordered[i] + ordered[i + 1]) / 2)
    F = field.reshape(n, n, n)
    border = np.zeros(F.shape, bool)
    for ax in range(3):
        for which in (0, -1):
            sl = [slice(None)] * 3; sl[ax] = which; border[tuple(sl)] = True
    if np.any(F[border] >= tau):
        raise Invalid(f"borda_{int(alpha*100)}")
    return float(np.log(tau))


# ----------------------------------------------------------------------------- estatísticas da região
def region_stats(m: Model, logtau: float, g) -> dict:
    held = m.sample(N_HELD, g)
    mass_int = float(np.mean(m.logpdf(held) >= logtau))
    x = m.sample(N_VOL, g)
    lp = m.logpdf(x)
    inside = lp >= logtau
    if inside.sum() < 20:
        raise Invalid("regiao_vazia")
    wi = np.exp(-lp[inside])
    vol = float(wi.sum() / len(x))
    xi = x[inside]
    cen = (wi[:, None] * xi).sum(0) / wi.sum()
    d = xi - cen
    cov = (wi[:, None, None] * np.einsum("ni,nj->nij", d, d)).sum(0) / wi.sum()
    return {"logtau": logtau, "mass_int": mass_int, "logV": float(np.log(vol)),
            "center": cen.tolist(), "shape": (cov / np.trace(cov)).ravel().tolist()}


def fit_candidate(name: str, x: np.ndarray) -> Model:
    if name in ("A", "B"):
        return GMMModel(x, 2)
    if name == "C":
        return GMMModel(x, 3)
    if name == "D":
        m = TMixModel(x, 2)
        if not m.converged:
            raise Invalid("em_sem_convergir")
        return m
    if name == "E":
        return KDEModel(x)
    raise ValueError(name)


def measure_window(name: str, x: np.ndarray, truth: Dist, true_eval: np.ndarray, g) -> dict:
    """Ajusta o candidato numa janela e mede as duas regiões. Levanta Invalid nas regras do candidato."""
    m = fit_candidate(name, x)
    lp_true_eval = m.logpdf(true_eval)
    out = {}
    for a in ALPHAS:
        logtau = tau_grid_vendor(m, a) if name == "A" else tau_hyndman(m, a, g)
        st = region_stats(m, logtau, g)
        st["mass_true"] = float(np.mean(lp_true_eval >= logtau))
        out[f"{int(a*100)}"] = st
    return out


def truth_stats(d: Dist, key) -> dict:
    g = rng("verdade", *key)
    x = d.sample(N_TRUTH, g)
    lp = d.logpdf(x)
    out = {}
    for a in ALPHAS:
        logtau = float(np.quantile(lp, 1 - a))
        inside = lp >= logtau
        wi = np.exp(-lp[inside])
        vol = float(wi.sum() / len(x))
        xi = x[inside]
        cen = (wi[:, None] * xi).sum(0) / wi.sum()
        out[f"{int(a*100)}"] = {"logV": float(np.log(vol)), "center": cen.tolist()}
    return out


def flow_ruler_vendor_valid(m: GMMModel) -> str | None:
    """Só para a régua secundária flow_raw: o candidato A seria válido?"""
    try:
        for a in ALPHAS:
            tau_grid_vendor(m, a)
        return None
    except Invalid as e:
        return str(e)
