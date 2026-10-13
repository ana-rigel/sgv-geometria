"""C1 — Padronização robusta de escala.

x_tilde = (x - mediana) / (1,4826 * MAD), com mediana e MAD estimadas na mesma
janela usada para ajustar a KDE. No modo legado (``LEGACY_UNSCALED_KDE``) a
transformação é a identidade.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

MAD_TO_SIGMA = 1.4826


@dataclass(frozen=True)
class RobustScale:
    med: np.ndarray    # (d,)
    scale: np.ndarray  # (d,)

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (np.asarray(X, dtype=float) - self.med) / self.scale

    def scale_delta(self, dX: np.ndarray) -> np.ndarray:
        """Diferenças (velocidades, desvios) só são divididas pela escala."""
        return np.asarray(dX, dtype=float) / self.scale

    @classmethod
    def identity(cls, d: int) -> "RobustScale":
        return cls(np.zeros(d), np.ones(d))


def fit_robust_scale(X: np.ndarray) -> RobustScale:
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    d = X.shape[1]
    med = np.zeros(d)
    scale = np.ones(d)
    for k in range(d):
        col = X[:, k]
        col = col[np.isfinite(col)]
        if len(col) == 0:
            continue
        m = float(np.median(col))
        mad = float(np.median(np.abs(col - m)))
        s = MAD_TO_SIGMA * mad
        if not np.isfinite(s) or s <= 0:
            s = float(np.std(col))
        if not np.isfinite(s) or s <= 0:
            s = 1.0
        med[k] = m
        scale[k] = s
    return RobustScale(med, scale)


def scaler_for(X_fit: np.ndarray, unscaled: bool) -> RobustScale:
    d = 1 if np.asarray(X_fit).ndim == 1 else np.asarray(X_fit).shape[1]
    if unscaled:
        return RobustScale.identity(d)
    return fit_robust_scale(X_fit)
