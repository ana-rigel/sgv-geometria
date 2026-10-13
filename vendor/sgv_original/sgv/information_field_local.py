"""Arquivo 1 — densidade informacional local (versão simples).

Reescrita de ``sgv_build_information_field_geometry_90d_refactored.py``.
Essência mantida: cinemática a partir do preço, densidade KDE do ponto atual
nas 200 barras anteriores (que o excluem) e suas derivadas no tempo.

Itens implementados: 1.1–1.6.

O nome da função e do arquivo de saída mudou para não colidir com a versão
canônica (arquivo 2): ``build_information_field_local_90d`` grava
``sgv_information_field_local_90d.csv``. O nome antigo continua como alias.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from .common.scaling import MAD_TO_SIGMA
from .common.validity import add_meta, assign_columns
from .config import DEFAULT_CONFIG, SGVConfig

OUTPUT_NAME = "sgv_information_field_local_90d.csv"


def compute_base_features(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    df = df.copy()
    if "close" not in df.columns:
        if cfg.info_local.KINEMATICS_SOURCE == "input" and not cfg.legacy.LEGACY_OVERWRITE_KINEMATICS \
                and {"E_norm", "jerk"} <= set(df.columns):
            return df
        raise ValueError("Coluna 'close' necessária (ou use KINEMATICS_SOURCE='input' com E_norm e jerk).")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    ret = df["close"].pct_change()
    velocity = ret
    acceleration = velocity.diff()
    jerk = acceleration.diff()
    e_norm = velocity ** 2 + acceleration ** 2

    cols = {"ret": ret, "velocity": velocity, "acceleration": acceleration,
            "E_norm_px": e_norm, "jerk_px": jerk}
    overwrite = cfg.legacy.LEGACY_OVERWRITE_KINEMATICS
    if overwrite or "E_norm" not in df.columns:
        cols["E_norm"] = e_norm
    if overwrite or "jerk" not in df.columns:
        cols["jerk"] = jerk
    return assign_columns(df, cols)


def _local_density(X: np.ndarray, window: int, bandwidth: float, unscaled: bool,
                   chunk: int = 2048) -> tuple[np.ndarray, np.ndarray]:
    """Densidade de cada ponto na janela [i-window, i) com amostras válidas.

    Retorna (densidade, válido). Regras do original: janela com menos de
    max(10, window//5) linhas, menos de 10 amostras válidas ou ponto inválido →
    inválido.
    """
    n = len(X)
    pad = np.full((window, 2), np.nan)
    Xp = np.vstack([pad, X])
    windows = sliding_window_view(Xp, (window, 2))[:, 0]   # (n+1, window, 2)
    dens = np.full(n, np.nan)
    rows_in_window = np.minimum(np.arange(n), window)
    min_rows = max(10, window // 5)
    h2 = bandwidth * bandwidth
    norm = 2.0 * np.pi * h2

    for s0 in range(0, n, chunk):
        s1 = min(n, s0 + chunk)
        W = windows[s0:s1]                                   # (c, window, 2)
        P = X[s0:s1]                                         # (c, 2)
        valid_s = np.isfinite(W).all(axis=2)                 # (c, window)
        cnt = valid_s.sum(axis=1)
        ok = (rows_in_window[s0:s1] >= min_rows) & (cnt >= 10) & np.isfinite(P).all(axis=1)
        if not ok.any():
            continue
        Wm = np.where(valid_s[..., None], W, np.nan)
        if unscaled:
            Ws, Ps = Wm, P
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                med = np.nanmedian(Wm, axis=1)                       # (c, 2)
                mad = np.nanmedian(np.abs(Wm - med[:, None, :]), axis=1)
                sd = np.nanstd(Wm, axis=1)
            scale = MAD_TO_SIGMA * mad
            scale = np.where(np.isfinite(scale) & (scale > 0), scale, sd)
            scale = np.where(np.isfinite(scale) & (scale > 0), scale, 1.0)
            Ws = (Wm - med[:, None, :]) / scale[:, None, :]
            Ps = (P - med) / scale
        d2 = ((Ps[:, None, :] - Ws) ** 2).sum(axis=2)        # (c, window)
        k = np.where(valid_s, np.exp(-0.5 * d2 / h2), 0.0)
        with np.errstate(invalid="ignore", divide="ignore"):
            rho = k.sum(axis=1) / cnt / norm
        dens[s0:s1] = np.where(ok, rho, np.nan)
    return dens, np.isfinite(dens)


def build_information_field_local_90d(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c, L = cfg.info_local, cfg.legacy
    df = df.copy().replace([np.inf, -np.inf], np.nan)
    df = compute_base_features(df, cfg)

    if L.LEGACY_OVERWRITE_KINEMATICS or c.KINEMATICS_SOURCE == "close":
        e_col, j_col = ("E_norm", "jerk") if L.LEGACY_OVERWRITE_KINEMATICS else ("E_norm_px", "jerk_px")
    else:
        e_col, j_col = "E_norm", "jerk"
    X = np.column_stack([
        pd.to_numeric(df[e_col], errors="coerce").to_numpy(float),
        pd.to_numeric(df[j_col], errors="coerce").to_numpy(float),
    ])
    dens, valid = _local_density(X, c.WINDOW, c.BANDWIDTH, unscaled=L.LEGACY_UNSCALED_KDE)

    if L.LEGACY_ZERO_FILL:
        dens_series = pd.Series(np.where(valid, dens, 0.0), index=df.index)
    else:
        dens_series = pd.Series(dens, index=df.index)
    grad = dens_series.diff()
    acc = grad.diff()
    if L.LEGACY_ZERO_FILL:
        grad, acc = grad.fillna(0.0), acc.fillna(0.0)

    out = assign_columns(df, {
        "information_density": dens_series.to_numpy(),
        "information_gradient": grad.to_numpy(),
        "information_acceleration": acc.to_numpy(),
        "info_density_valid": valid.astype(int),
        "info_density_source": f"{e_col},{j_col}",
    })
    add_meta(out, "information_field_local", {
        "valid_share": float(valid.mean()) if len(valid) else None,
        "density_std": float(np.nanstd(dens)) if valid.any() else None,
    })
    return out


def build_information_field_geometry_90d(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    """Alias do nome antigo (1.4)."""
    warnings.warn(
        "build_information_field_geometry_90d (versão simples) foi renomeada para "
        "build_information_field_local_90d; a versão canônica com esse nome está em "
        "sgv.information_field.",
        DeprecationWarning,
        stacklevel=2,
    )
    return build_information_field_local_90d(df, cfg)
