"""C3 — KDE gaussiana com derivadas analíticas.

Para uma KDE gaussiana isotrópica de bandwidth h, com u_s = (x - x_s)/h² e
pesos w_s ∝ exp(-|x - x_s|² / 2h²), o potencial φ = -log ρ satisfaz:

    ∇φ      = E_w[u]                     = (x - E_w[s]) / h²
    ∇²φ     = I/h² - Cov_w[u]            = I/h² - Cov_w[s] / h⁴
    ∂³φ_ijk = E_w[(u-ū)_i (u-ū)_j (u-ū)_k] = -κ₃,w[s]_ijk / h⁶

onde κ₃,w[s] é o terceiro momento central ponderado das amostras. Essas são
exatamente as grandezas que os scripts originais aproximam com grade +
np.gradient + interpolação.

Os momentos são calculados como produtos de matrizes (pesos × potências das
amostras), o que usa BLAS. As amostras são centradas na própria média antes,
para limitar o cancelamento numérico nos momentos centrais.

A regressão de Nadaraya–Watson m(x) = Σ w_s y_s / Σ w_s usada no campo de λ
tem gradiente ∇m = Cov_w[s, y] / h².
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class KDEResult:
    log_rho: np.ndarray                 # (N,)
    grad_phi: np.ndarray | None = None  # (N, d)
    hess_phi: np.ndarray | None = None  # (N, d, d)
    phi3: np.ndarray | None = None      # (N, d, d, d)
    nw_value: np.ndarray | None = None  # (N,)
    nw_grad: np.ndarray | None = None   # (N, d)

    @property
    def phi(self) -> np.ndarray:
        return -self.log_rho


# Pontos a mais de FAR_LIMIT bandwidths da média das amostras (barras de crash,
# em que E_norm padronizado chega a 10³–10⁴) usam a rota direta centrada no
# próprio ponto: os momentos brutos centrados na média perderiam precisão.
FAR_LIMIT = 200.0


def _kde_direct(P: np.ndarray, S: np.ndarray, h: float, order: int, y: np.ndarray | None) -> dict:
    """Rota direta (duas passagens sobre x - s_m). Mais lenta, exata em qualquer ponto."""
    N, d = P.shape
    M = S.shape[0]
    h2 = h * h
    out = {"log_rho": np.full(N, np.nan), "grad": np.full((N, d), np.nan), "hess": np.full((N, d, d), np.nan),
           "phi3": np.full((N, d, d, d), np.nan), "nw_v": np.full(N, np.nan), "nw_g": np.full((N, d), np.nan)}
    log_norm = np.log(M) + 0.5 * d * np.log(2.0 * np.pi * h2)
    for i in range(N):
        diff = P[i][None, :] - S                     # (M, d)
        a = -0.5 * np.einsum("md,md->m", diff, diff) / h2
        amax = a.max()
        w = np.exp(a - amax)
        S0 = w.sum()
        out["log_rho"][i] = np.log(S0) + amax - log_norm
        u = diff / h2
        ubar = (w @ u) / S0
        cu = u - ubar
        out["grad"][i] = ubar
        if order >= 2:
            out["hess"][i] = np.eye(d) / h2 - (cu.T * w) @ cu / S0
        if order >= 3:
            out["phi3"][i] = np.einsum("m,mi,mj,mk->ijk", w, cu, cu, cu) / S0
        if y is not None:
            m = (w @ y) / S0
            out["nw_v"][i] = m
            out["nw_g"][i] = -((w * (y - m)) @ cu) / S0
    return out


def kde_eval(
    points: np.ndarray,
    samples: np.ndarray,
    h: float,
    order: int = 2,
    nw_values: np.ndarray | None = None,
    chunk: int | None = None,
) -> KDEResult:
    """Avalia log ρ e derivadas de φ = -log ρ nos pontos.

    order: 0 só log ρ; 1 + gradiente; 2 + Hessiana; 3 + terceira derivada.
    nw_values: se dado, calcula também a regressão de Nadaraya–Watson desses
    valores e seu gradiente.
    """
    P = np.atleast_2d(np.asarray(points, dtype=float))
    S = np.atleast_2d(np.asarray(samples, dtype=float))
    N, d = P.shape
    M = S.shape[0]
    h = float(h)
    h2 = h * h

    log_rho = np.full(N, np.nan)
    grad = np.full((N, d), np.nan) if order >= 1 else None
    hess = np.full((N, d, d), np.nan) if order >= 2 else None
    phi3 = np.full((N, d, d, d), np.nan) if order >= 3 else None
    nw_v = np.full(N, np.nan) if nw_values is not None else None
    nw_g = np.full((N, d), np.nan) if nw_values is not None else None
    if M == 0 or N == 0:
        return KDEResult(log_rho, grad, hess, phi3, nw_v, nw_g)

    # centra as amostras (e os pontos) na média das amostras: não muda nada,
    # mas reduz o cancelamento nos momentos centrais
    c0 = S.mean(axis=0)
    Sc = S - c0
    Pc = P - c0

    # matriz de "features" das amostras: [1, s, s⊗s, s⊗s⊗s, y, y·s]
    blocks = [np.ones((M, 1))]
    if order >= 1 or nw_values is not None:
        blocks.append(Sc)
    if order >= 2 or nw_values is not None:
        blocks.append((Sc[:, :, None] * Sc[:, None, :]).reshape(M, d * d))
    if order >= 3:
        blocks.append((Sc[:, :, None, None] * Sc[:, None, :, None] * Sc[:, None, None, :]).reshape(M, d ** 3))
    y = None
    if nw_values is not None:
        y = np.asarray(nw_values, dtype=float)
        blocks.append(y[:, None])
        blocks.append(Sc * y[:, None])
    F = np.hstack(blocks)                          # (M, K)
    K = F.shape[1]
    s_sq = np.einsum("md,md->m", Sc, Sc)

    log_norm = np.log(M) + 0.5 * d * np.log(2.0 * np.pi * h2)
    C = chunk or int(max(1, min(4096, 4e6 // max(1, M))))
    finite_pt = np.isfinite(Pc).all(axis=1)
    eye = np.eye(d)

    far = finite_pt & (np.abs(np.where(finite_pt[:, None], Pc, 0.0)).max(axis=1) / h > FAR_LIMIT)
    if far.any():
        fidx = np.where(far)[0]
        r = _kde_direct(P[fidx], S, h, order, None if nw_values is None else np.asarray(nw_values, float))
        log_rho[fidx] = r["log_rho"]
        if order >= 1:
            grad[fidx] = r["grad"]
        if order >= 2:
            hess[fidx] = r["hess"]
        if order >= 3:
            phi3[fidx] = r["phi3"]
        if nw_values is not None:
            nw_v[fidx] = r["nw_v"]
            nw_g[fidx] = r["nw_g"]
        finite_pt = finite_pt & ~far

    for s0 in range(0, N, C):
        s1 = min(N, s0 + C)
        idx = np.arange(s0, s1)[finite_pt[s0:s1]]
        if len(idx) == 0:
            continue
        x = Pc[idx]
        d2 = np.einsum("cd,cd->c", x, x)[:, None] + s_sq[None, :] - 2.0 * (x @ Sc.T)
        a = -0.5 * np.maximum(d2, 0.0) / h2
        amax = a.max(axis=1, keepdims=True)
        w = np.exp(a - amax)
        mom = (w @ F)                                 # (c, K)
        S0 = mom[:, 0]
        log_rho[idx] = np.log(S0) + amax[:, 0] - log_norm
        if K == 1:
            continue
        mom = mom / S0[:, None]
        pos = 1
        mean = mom[:, pos:pos + d]                    # E_w[s]
        pos += d
        if order >= 1:
            grad[idx] = (x - mean) / h2
        if order >= 2 or y is not None:
            m2 = mom[:, pos:pos + d * d].reshape(-1, d, d)
            pos += d * d
            cov = m2 - mean[:, :, None] * mean[:, None, :]
            if order >= 2:
                hess[idx] = eye[None] / h2 - cov / (h2 * h2)
        if order >= 3:
            m3 = mom[:, pos:pos + d ** 3].reshape(-1, d, d, d)
            pos += d ** 3
            mu = mean
            # terceiro momento central: E[s³] - 3 sym(E[s²] μ) + 2 μ³
            k3 = (m3
                  - np.einsum("cij,ck->cijk", m2, mu)
                  - np.einsum("cik,cj->cijk", m2, mu)
                  - np.einsum("cjk,ci->cijk", m2, mu)
                  + 2.0 * mu[:, :, None, None] * mu[:, None, :, None] * mu[:, None, None, :])
            phi3[idx] = -k3 / (h2 ** 3)
        if y is not None:
            ym = mom[:, pos]
            ys = mom[:, pos + 1:pos + 1 + d]
            nw_v[idx] = ym
            nw_g[idx] = (ys - mean * ym[:, None]) / h2

    return KDEResult(log_rho, grad, hess, phi3, nw_v, nw_g)


def gaussian_density(points: np.ndarray, samples: np.ndarray, h: float) -> np.ndarray:
    """Densidade KDE gaussiana (mesma normalização do sklearn)."""
    return np.exp(kde_eval(points, samples, h, order=0).log_rho)
