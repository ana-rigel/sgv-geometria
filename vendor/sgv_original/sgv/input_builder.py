"""Arquivo 0 — monta o input do SGV a partir das barras OHLCV de 1 minuto.

Reescrita de ``build_btc_90d_input_sgv_refactored.py``. Fórmulas mantidas:

- E_raw = (close - EMA_0,05(close)) / |EMA|  e  E_norm = z robusto de E_raw
- velocity = ret_1m, acceleration = Δvelocity, jerk = Δacceleration
- lambda_dynamic = 1 / (desvio-padrão dos retornos nas últimas 30 barras + 1e-6)
  ("rigidez": volatilidade local baixa → rigidez alta)

Mudanças, cada uma atrás de uma flag:

- ``LEGACY_GLOBAL_QUANTILES``: o original calcula a mediana e o MAD do z de
  E_norm no período inteiro (olha o futuro). No modo novo, os parâmetros vêm
  da janela causal de cada bloco.
- ``LEGACY_ZERO_FILL``: o original preenche NaN com 0. No aquecimento isso
  vira λ = 0 nas primeiras barras, ou seja, "rigidez zero", e
  jerk/λ = |jerk| / 1e-9 ≈ 10⁶. Também zera os retornos futuros da cauda.
  No modo novo esses valores ficam NaN e ``input_valid`` marca as linhas.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .common.blocks import causal_or_global_blocks, min_periods_for
from .common.stats import robust_z_singularity
from .common.validity import add_meta
from .config import DEFAULT_CONFIG, SGVConfig

PRICE_COL = "close"
MEMORY_ALPHA = 0.05
LAMBDA_WINDOW = 30
LAMBDA_MIN = 1e-6
ROBUST_EPS = 1e-9
EPS = 1e-9

OUT_COLS = ["timestamp", "datetime", "open", "high", "low", "close", "volume", "ret_1m",
            "ret_fwd_1m", "ret_fwd_3m", "ret_fwd_5m", "memory_close", "memory_flux", "velocity",
            "acceleration", "jerk", "E_raw", "E_norm", "lambda_dynamic"]


def build_lambda_dynamic(ret_1m: pd.Series, window: int = LAMBDA_WINDOW) -> pd.Series:
    ret_1m = pd.to_numeric(ret_1m, errors="coerce")
    local_vol = ret_1m.rolling(window=window, min_periods=max(5, window // 3)).std()
    return 1.0 / (local_vol.abs() + LAMBDA_MIN)


def build_btc_90d_input_sgv(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    L = cfg.legacy
    df = df.copy()
    required = ["timestamp", "datetime", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando no raw dataset: {missing}")
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["timestamp", "close"]).sort_values("timestamp").reset_index(drop=True)
    close = df[PRICE_COL]
    n = len(df)

    df["ret_1m"] = close.pct_change(1)
    df["ret_fwd_1m"] = close.shift(-1) / (close + EPS) - 1.0
    df["ret_fwd_3m"] = close.shift(-3) / (close + EPS) - 1.0
    df["ret_fwd_5m"] = close.shift(-5) / (close + EPS) - 1.0
    df["memory_close"] = close.ewm(alpha=MEMORY_ALPHA, adjust=False).mean()
    df["memory_flux"] = df["memory_close"].diff()
    df["velocity"] = df["ret_1m"]
    df["acceleration"] = df["velocity"].diff()
    df["jerk"] = df["acceleration"].diff()
    df["E_raw"] = (df["close"] - df["memory_close"]) / (df["memory_close"].abs() + ROBUST_EPS)

    blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_QUANTILES)
    min_p = min_periods_for(cfg, L.LEGACY_GLOBAL_QUANTILES)
    df["E_norm"] = robust_z_singularity(df["E_raw"].to_numpy(float), blocks, min_p, ROBUST_EPS)
    df["lambda_dynamic"] = build_lambda_dynamic(df["ret_1m"], LAMBDA_WINDOW)

    out = df[OUT_COLS].copy()
    numeric_cols = out.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["input_valid"] = out[numeric_cols].notna().all(axis=1).astype(int)
    if L.LEGACY_ZERO_FILL:
        out[numeric_cols] = out[numeric_cols].fillna(0.0)
    out = out.reset_index(drop=True)
    lam = out["lambda_dynamic"]
    add_meta(out, "input_builder", {
        "lambda_warmup_rows": int(lam.isna().sum() if not L.LEGACY_ZERO_FILL else (lam == 0).sum()),
        "lambda_p01_p50_p99": [float(x) for x in np.nanpercentile(lam[lam > 0], [1, 50, 99])] if (lam > 0).any() else None,
        "input_valid_share": float(out["input_valid"].mean()) if n else None,
    })
    return out
