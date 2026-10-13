"""Funções numéricas compartilhadas (sigmoide, EMA, log1p seguro) e C6 (safe_ratio)."""
from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np
import pandas as pd

from .blocks import Block, block_reduce


def sigmoid(x) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    x_arr = np.clip(x_arr, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-x_arr))


def ema(series: pd.Series, alpha: float) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    return series.ewm(alpha=alpha, adjust=False).mean()


def safe_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def log1p_safe(x, max_log: float) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    arr = np.where(np.isnan(arr), np.nan, np.maximum(arr, 0.0))
    out = np.log1p(arr)
    return np.clip(out, 0.0, max_log)


def to_float(value: Any) -> float:
    """Conversão rápida para float (10.6): NaN quando não numérico."""
    if value is None:
        return math.nan
    try:
        v = float(value)
    except (TypeError, ValueError):
        return math.nan
    return v if math.isfinite(v) else (math.nan if math.isnan(v) else v)


def safe_ratio(
    num,
    den,
    *,
    legacy_abs_eps: bool,
    eps: float,
    blocks: Sequence[Block],
    min_periods: int,
    q: float,
    legacy_fill_zero: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """C6 — num / |den| com piso relativo.

    Modo novo: piso = quantil ``q`` de |den| na janela causal do bloco (nunca
    menor que ``eps``). Retorna (razão, flag de piso aplicado). Sem piso
    disponível (aquecimento) a razão é NaN.

    Modo legado: num / (|den| + eps), com NaN preenchido por 0 como no
    original.
    """
    num = np.asarray(num, dtype=float)
    den_abs = np.abs(np.asarray(den, dtype=float))
    if legacy_abs_eps:
        if legacy_fill_zero:
            num = np.nan_to_num(num, nan=0.0)
            den_abs = np.nan_to_num(den_abs, nan=0.0)
        return num / (den_abs + eps), np.zeros(len(num), dtype=int)

    floor = block_reduce(den_abs, blocks, lambda w: float(np.quantile(w, q)), min_periods)
    floor = np.where(np.isfinite(floor), np.maximum(floor, eps), np.nan)
    eff = np.maximum(den_abs, floor)
    floored = (den_abs < floor).astype(int)
    ratio = num / eff
    ratio = np.where(np.isfinite(floor), ratio, np.nan)
    return ratio, floored
