"""KDE gaussiano isotrópico com derivadas analíticas.

ρ(x)   = (2πh²)^(−d/2) · (1/n) Σ K(u_i),   u_i = (x − X_i)/h,   K(u) = exp(−|u|²/2)
∇ρ     = −(1/h)  · (1/n) Σ K u_i          (× constante)
∇²ρ    =  (1/h²) · (1/n) Σ K (u_i u_iᵀ − I)

Potencial de informação (surpresa):  φ = −log ρ
  ∇φ   = −∇ρ/ρ                          (menos o "escore" de localização)
  ∇²φ  = −∇²ρ/ρ + ∇ρ∇ρᵀ/ρ²              (informação observada — a métrica do legado)

Os pesos são calculados em log e normalizados pelo máximo, então a métrica
(que é razão de somas) é estável mesmo com densidades minúsculas.
"""
from __future__ import annotations

import numpy as np


class GaussianKDE:
    def __init__(self, X: np.ndarray, h: float):
        X = np.asarray(X, float)
        if X.ndim != 2:
            raise ValueError("X deve ser (n, d)")
        self.X = X[np.all(np.isfinite(X), axis=1)]
        self.n, self.d = self.X.shape
        self.h = float(h)

    # pesos normalizados w_i ∝ K(u_i) e log da soma
    def _weights(self, x: np.ndarray):
        u = (x - self.X) / self.h
        q = -0.5 * np.einsum("ij,ij->i", u, u)
        qmax = q.max()
        w = np.exp(q - qmax)
        return u, w, qmax

    def log_density(self, x: np.ndarray) -> float:
        _, w, qmax = self._weights(np.asarray(x, float))
        return (qmax + np.log(w.sum()) - np.log(self.n)
                - 0.5 * self.d * np.log(2 * np.pi * self.h ** 2))

    def phi(self, x) -> float:
        """Surpresa φ = −log ρ."""
        return -self.log_density(x)

    def grad_phi(self, x) -> np.ndarray:
        u, w, _ = self._weights(np.asarray(x, float))
        W = w.sum()
        return (w @ u) / W / self.h  # ∇φ = −∇ρ/ρ = +(Σ w u)/(h Σ w)

    def hess_phi(self, x) -> np.ndarray:
        """Informação observada H = ∇²(−log ρ) = (I − Cov_w(u)) / h²."""
        u, w, _ = self._weights(np.asarray(x, float))
        W = w.sum()
        mu = (w @ u) / W
        second = np.einsum("i,ij,ik->jk", w, u, u) / W
        cov = second - np.outer(mu, mu)
        return (np.eye(self.d) - cov) / self.h ** 2

    def score_at_samples(self, leave_one_out: bool = True) -> np.ndarray:
        """∇φ em cada amostra (usado pela métrica de Fisher local).

        Por padrão é deixe-um-fora: o kernel da própria amostra (u = 0) puxaria o
        escore para zero e subestimaria a informação."""
        X, h = self.X, self.h
        out = np.empty_like(X)
        for start in range(0, self.n, 512):
            blk = X[start:start + 512]
            U = (blk[:, None, :] - X[None, :, :]) / h          # (b, n, d)
            Q = -0.5 * np.einsum("bnd,bnd->bn", U, U)
            if leave_one_out:
                idx = np.arange(start, start + len(blk))
                Q[np.arange(len(blk)), idx] = -np.inf
            Q -= Q.max(axis=1, keepdims=True)
            W = np.exp(Q)
            out[start:start + len(blk)] = np.einsum("bn,bnd->bd", W, U) / W.sum(1, keepdims=True) / h
        return out
