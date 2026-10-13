"""6.1 — Binning único para mapa de força e alinhamento."""
from __future__ import annotations

import numpy as np


def quantile_edges(values: np.ndarray, n_cells: int, q_low: float, q_high: float, eps: float = 1e-12) -> np.ndarray:
    """Bordas por quantis robustos (q_low–q_high ± 10%), como nos outros scripts."""
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return np.linspace(-1.0, 1.0, n_cells + 1)
    lo, hi = np.quantile(v, [q_low, q_high])
    span = max(hi - lo, eps)
    return np.linspace(lo - 0.10 * span, hi + 0.10 * span, n_cells + 1)


def minmax_edges(values: np.ndarray, n_cells: int) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return np.linspace(-1.0, 1.0, n_cells + 1)
    return np.linspace(v.min(), v.max(), n_cells + 1)


def centers(edges: np.ndarray) -> np.ndarray:
    return 0.5 * (edges[:-1] + edges[1:])


def bin_index(values: np.ndarray, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Índice da célula (0..n_cells-1) e flag de fora da grade.

    Pontos fora da grade vão para a célula da borda. NaN recebe índice -1.
    """
    v = np.asarray(values, dtype=float)
    n_cells = len(edges) - 1
    idx = np.digitize(v, edges[1:-1], right=False)
    out = (v < edges[0]) | (v > edges[-1])
    idx = np.clip(idx, 0, n_cells - 1)
    idx = np.where(np.isfinite(v), idx, -1)
    return idx.astype(int), out & np.isfinite(v)


# ---------------------------------------------------------------- legado
def legacy_grid_points(values: np.ndarray, size: int) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return np.linspace(-1, 1, size)
    return np.linspace(v.min(), v.max(), size)


def legacy_searchsorted_index(grid: np.ndarray, v: np.ndarray) -> np.ndarray:
    idx = np.searchsorted(grid, v)
    return np.clip(idx, 0, len(grid) - 1)


def legacy_nearest_index(sorted_vals: np.ndarray, v: float) -> int:
    idx = np.searchsorted(sorted_vals, v)
    if idx <= 0:
        return 0
    if idx >= len(sorted_vals):
        return len(sorted_vals) - 1
    left = sorted_vals[idx - 1]
    right = sorted_vals[idx]
    if abs(v - left) <= abs(v - right):
        return idx - 1
    return idx


def legacy_nearest_index_vec(sorted_vals: np.ndarray, v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    idx = np.searchsorted(sorted_vals, v)
    n = len(sorted_vals)
    left_i = np.clip(idx - 1, 0, n - 1)
    right_i = np.clip(idx, 0, n - 1)
    left = sorted_vals[left_i]
    right = sorted_vals[right_i]
    choose_left = np.abs(v - left) <= np.abs(v - right)
    res = np.where(choose_left, left_i, right_i)
    res = np.where(idx <= 0, 0, res)
    res = np.where(idx >= n, n - 1, res)
    return res.astype(int)
