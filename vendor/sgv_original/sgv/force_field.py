"""Arquivo 6 — mapa de força no plano (E_norm, jerk).

Reescrita de ``sgv_build_force_field_90d_refactored.py``. O campo continua
sendo a média de (ΔE, Δjerk) por célula da grade, e ``force_magnitude`` a
média das magnitudes por célula. Itens 6.1–6.8.

O construtor de mapa (:func:`build_map`) é compartilhado com o alinhamento
(arquivo 7), que monta um mapa causal por bloco.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .common.binning import bin_index, centers, legacy_grid_points, legacy_nearest_index_vec, quantile_edges, minmax_edges
from .common.blocks import causal_or_global_blocks, min_periods_for
from .common.scaling import fit_robust_scale
from .common.validity import add_meta
from .config import DEFAULT_CONFIG, SGVConfig


@dataclass
class ForceMap:
    legacy_binning: bool
    e_axis: np.ndarray        # legado: pontos da grade; novo: bordas
    j_axis: np.ndarray
    sum_x: np.ndarray         # (nE, nJ)
    sum_y: np.ndarray
    sum_m: np.ndarray
    sum_x2: np.ndarray
    sum_y2: np.ndarray
    count: np.ndarray         # amostras com força finita
    rows: np.ndarray          # amostras atribuídas (inclusive força NaN)
    scale_x: float
    scale_y: float
    min_cell_n: int

    # ------------------------------------------------------------ células
    @property
    def shape(self) -> tuple[int, int]:
        return self.sum_x.shape

    def cell_values(self) -> tuple[np.ndarray, np.ndarray]:
        if self.legacy_binning:
            return self.e_axis, self.j_axis
        return centers(self.e_axis), centers(self.j_axis)

    def means(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        with np.errstate(invalid="ignore", divide="ignore"):
            fx = self.sum_x / self.count
            fy = self.sum_y / self.count
            fm = self.sum_m / self.count
        bad = self.count < max(1, self.min_cell_n)
        fx, fy, fm = (np.where(bad, np.nan, a) for a in (fx, fy, fm))
        return fx, fy, fm

    # ------------------------------------------------------------ binning
    def agg_index(self, e: np.ndarray, j: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Célula em que um ponto é agregado (e flag de fora da grade)."""
        if self.legacy_binning:
            ie = np.clip(np.searchsorted(self.e_axis, e), 0, len(self.e_axis) - 1)
            ij = np.clip(np.searchsorted(self.j_axis, j), 0, len(self.j_axis) - 1)
            return ie, ij, np.zeros(len(e), dtype=bool)
        ie, oe = bin_index(e, self.e_axis)
        ij, oj = bin_index(j, self.j_axis)
        return ie, ij, oe | oj

    def lookup_index(self, e: np.ndarray, j: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Célula consultada para um ponto (6.1: a mesma da agregação no modo novo)."""
        if not self.legacy_binning:
            ie, ij, _ = self.agg_index(e, j)
            return ie, ij
        # legado: vizinho mais próximo entre os valores presentes no mapa
        present = self.rows > 0
        e_idx = np.where(present.any(axis=1))[0]
        j_idx = np.where(present.any(axis=0))[0]
        if len(e_idx) == 0 or len(j_idx) == 0:
            return np.full(len(e), -1), np.full(len(j), -1)
        ie = e_idx[legacy_nearest_index_vec(self.e_axis[e_idx], e)]
        ij = j_idx[legacy_nearest_index_vec(self.j_axis[j_idx], j)]
        return ie, ij


def compute_forces(e: np.ndarray, j: np.ndarray, mode: str) -> tuple[np.ndarray, np.ndarray]:
    E, J = pd.Series(e), pd.Series(j)
    if mode == "departure":
        return (E.shift(-1) - E).to_numpy(), (J.shift(-1) - J).to_numpy()
    return E.diff().to_numpy(), J.diff().to_numpy()


def build_map(e, j, fx, fy, cfg: SGVConfig) -> ForceMap:
    c, L = cfg.force_field, cfg.legacy
    e = np.asarray(e, float)
    j = np.asarray(j, float)
    fx = np.asarray(fx, float)
    fy = np.asarray(fy, float)
    ok_pos = np.isfinite(e) & np.isfinite(j)
    e, j, fx, fy = e[ok_pos], j[ok_pos], fx[ok_pos], fy[ok_pos]

    if L.LEGACY_UNSCALED_FORCE:
        sx = sy = 1.0
    else:
        sc = fit_robust_scale(np.column_stack([fx, fy]))
        sx, sy = float(sc.scale[0]), float(sc.scale[1])
    fx_s, fy_s = fx / sx, fy / sy
    fm_s = np.sqrt(fx_s ** 2 + fy_s ** 2)

    if L.LEGACY_BINNING:
        if L.LEGACY_MINMAX_GRID:
            e_axis, j_axis = legacy_grid_points(e, c.GRID_SIZE), legacy_grid_points(j, c.GRID_SIZE)
        else:
            e_axis = centers(quantile_edges(e, c.GRID_SIZE, c.Q_LOW, c.Q_HIGH))
            j_axis = centers(quantile_edges(j, c.GRID_SIZE, c.Q_LOW, c.Q_HIGH))
        shape = (len(e_axis), len(j_axis))
    else:
        if L.LEGACY_MINMAX_GRID:
            e_axis, j_axis = minmax_edges(e, c.GRID_SIZE), minmax_edges(j, c.GRID_SIZE)
        else:
            e_axis = quantile_edges(e, c.GRID_SIZE, c.Q_LOW, c.Q_HIGH)
            j_axis = quantile_edges(j, c.GRID_SIZE, c.Q_LOW, c.Q_HIGH)
        shape = (len(e_axis) - 1, len(j_axis) - 1)

    fm_obj = ForceMap(L.LEGACY_BINNING, e_axis, j_axis, *(np.zeros(shape) for _ in range(5)),
                      np.zeros(shape), np.zeros(shape), sx, sy,
                      1 if L.LEGACY_NO_MIN_CELL else c.MIN_CELL_N)
    ie, ij, _ = fm_obj.agg_index(e, j)
    flat = ie * shape[1] + ij
    size = shape[0] * shape[1]
    fin = np.isfinite(fx_s) & np.isfinite(fy_s)
    fm_obj.rows[:] = np.bincount(flat, minlength=size).reshape(shape)
    fm_obj.count[:] = np.bincount(flat[fin], minlength=size).reshape(shape)
    fm_obj.sum_x[:] = np.bincount(flat[fin], weights=fx_s[fin], minlength=size).reshape(shape)
    fm_obj.sum_y[:] = np.bincount(flat[fin], weights=fy_s[fin], minlength=size).reshape(shape)
    fm_obj.sum_m[:] = np.bincount(flat[fin], weights=fm_s[fin], minlength=size).reshape(shape)
    fm_obj.sum_x2[:] = np.bincount(flat[fin], weights=fx_s[fin] ** 2, minlength=size).reshape(shape)
    fm_obj.sum_y2[:] = np.bincount(flat[fin], weights=fy_s[fin] ** 2, minlength=size).reshape(shape)
    return fm_obj


def map_to_frame(fmap: ForceMap, cfg: SGVConfig) -> pd.DataFrame:
    """Tabela de células presentes, no formato do script original (+ colunas novas)."""
    ev, jv = fmap.cell_values()
    fx, fy, fm = fmap.means()
    present = fmap.rows > 0
    ie, ij = np.nonzero(present)
    order = np.lexsort((jv[ij], ev[ie]))           # ordenado por E e depois jerk (como o groupby)
    ie, ij = ie[order], ij[order]
    with np.errstate(invalid="ignore", divide="ignore"):
        var_x = fmap.sum_x2 / fmap.count - (fmap.sum_x / fmap.count) ** 2
        var_y = fmap.sum_y2 / fmap.count - (fmap.sum_y / fmap.count) ** 2
    out = pd.DataFrame({
        "E": ev[ie], "jerk": jv[ij],
        "force_x": fx[ie, ij], "force_y": fy[ie, ij], "force_magnitude": fm[ie, ij],
        "n_obs": fmap.count[ie, ij].astype(int),
        "force_x_std": np.sqrt(np.maximum(var_x[ie, ij], 0.0)),
        "force_y_std": np.sqrt(np.maximum(var_y[ie, ij], 0.0)),
    })
    out.attrs["force_scale"] = (fmap.scale_x, fmap.scale_y)
    return out


def build_force_field_90d(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    """Mapa de força atual.

    Modo legado (``LEGACY_GLOBAL_MAP``): um mapa com o período inteiro, como o
    original. Modo novo: o mapa causal que seria usado na próxima barra (janela
    das últimas ``W_MAP`` barras). O alinhamento monta seus próprios mapas por
    bloco; este arquivo serve para inspeção e para o live.
    """
    c, L = cfg.force_field, cfg.legacy
    df = df.copy().replace([np.inf, -np.inf], np.nan)
    for col in ("E_norm", "jerk"):
        if col not in df.columns:
            raise ValueError(f"Colunas faltando: {[col]}")
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["E_norm", "jerk"]).reset_index(drop=True)
    if len(df) < 10:
        raise ValueError("Dados insuficientes para force field.")
    e = df["E_norm"].to_numpy(float)
    j = df["jerk"].to_numpy(float)
    fx, fy = compute_forces(e, j, c.FORCE_MODE)
    if L.LEGACY_GLOBAL_MAP:
        rows = slice(0, len(df))
    else:
        rows = slice(max(0, len(df) - cfg.causal.W_MAP), len(df))
    fmap = build_map(e[rows], j[rows], fx[rows], fy[rows], cfg)
    out = map_to_frame(fmap, cfg)
    if out.empty:
        raise ValueError("Falha ao construir grid de força.")
    if L.LEGACY_ZERO_FILL:
        for col in ("force_x", "force_y", "force_magnitude"):
            out[col] = out[col].fillna(0.0)
        out = out[["E", "jerk", "force_x", "force_y", "force_magnitude", "n_obs", "force_x_std", "force_y_std"]]
    add_meta(out, "force_field", {
        "cells_present": int(len(out)),
        "cells_below_min_n": int((out["n_obs"] < fmap.min_cell_n).sum()),
        "force_scale": [fmap.scale_x, fmap.scale_y],
        "window_rows": int(rows.stop - rows.start),
    })
    return out
