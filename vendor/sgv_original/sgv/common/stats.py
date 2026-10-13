"""C5 — Quantis, z-scores e winsorização causais por bloco.

Cada função recebe a lista de blocos; com o bloco global (legado) o resultado é
o mesmo das funções originais aplicadas ao período inteiro.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from .blocks import Block, block_reduce


def quantile_threshold(values, blocks: Sequence[Block], q: float, min_periods: int) -> np.ndarray:
    return block_reduce(values, blocks, lambda w: float(np.quantile(w, q)), min_periods)


def winsorize(values, blocks: Sequence[Block], q_low: float, q_high: float, min_periods: int) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    b = block_reduce(v, blocks, lambda w: np.quantile(w, [q_low, q_high]), min_periods, n_out=2)
    return np.clip(v, b[:, 0], b[:, 1])


# --- z robusto do terreno (0,6745 (x - med) / MAD; zero se MAD < 1e-12)
def _terrain_z_params(w: np.ndarray) -> tuple[float, float]:
    med = float(np.median(w))
    mad = float(np.median(np.abs(w - med)))
    return med, mad


def robust_z_terrain(values, blocks: Sequence[Block], min_periods: int) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    p = block_reduce(v, blocks, _terrain_z_params, min_periods, n_out=2)
    med, mad = p[:, 0], p[:, 1]
    with np.errstate(invalid="ignore", divide="ignore"):
        z = 0.6745 * (v - med) / mad
    z = np.where(np.isfinite(mad) & (mad < 1e-12), 0.0, z)
    return z


# --- z robusto da singularidade (1,4826 MAD; senão desvio; senão 1)
def _sing_z_params(w: np.ndarray, eps: float) -> tuple[float, float]:
    med = float(np.median(w))
    mad = float(np.median(np.abs(w - med)))
    scale = 1.4826 * mad if mad > 0 else float(np.std(w))
    if not np.isfinite(scale) or scale < eps:
        scale = 1.0
    return med, scale


def robust_z_singularity(values, blocks: Sequence[Block], min_periods: int, eps: float) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    p = block_reduce(v, blocks, lambda w: _sing_z_params(w, eps), min_periods, n_out=2)
    return (v - p[:, 0]) / p[:, 1]


def minmax_robust(values, blocks: Sequence[Block], min_periods: int, eps: float) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    p = block_reduce(v, blocks, lambda w: np.quantile(w, [0.05, 0.95]), min_periods, n_out=2)
    q05, q95 = p[:, 0], p[:, 1]
    denom = q95 - q05
    out = (v - q05) / np.where(np.abs(denom) < eps, np.nan, denom)
    out = np.clip(out, 0.0, 1.0)
    # no original, denominador degenerado devolve 0 para a série inteira
    out = np.where(np.isfinite(denom) & (np.abs(denom) < eps), 0.0, out)
    return out
