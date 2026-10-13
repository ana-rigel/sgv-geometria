"""Arquivo 8 — valor esperado condicional ao score de transição do terreno.

Reescrita de ``sgv_build_expected_value_90d_refactored.py``. Definição
mantida: média do retorno futuro nas barras com sinal ativo dentro das 200
anteriores, ponderada pela frequência do sinal. Itens 8.1–8.6.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .common.blocks import causal_or_global_blocks, min_periods_for
from .common.stats import quantile_threshold
from .common.validity import add_meta, assign_columns
from .config import DEFAULT_CONFIG, SGVConfig


def _csum(x: np.ndarray) -> np.ndarray:
    return np.concatenate([[0.0], np.cumsum(x)])


def rolling_expected_value(signal: np.ndarray, returns: np.ndarray, window: int, horizon: int,
                           legacy_window: bool, min_signals: int) -> dict[str, np.ndarray]:
    """EV na barra i com sinais nas barras j de [max(0, i-window), fim].

    fim = i-1 no original (8.1: vaza retorno não realizado quando horizon > 1);
    fim = i-horizon no modo novo (j + horizon <= i).
    Retorna média, contagem de sinais, número de retornos usados e erro-padrão.
    """
    sig = np.asarray(signal, dtype=float)
    ret = np.asarray(returns, dtype=float)
    n = len(sig)
    active = np.nan_to_num(sig, nan=0.0) > 0
    use = active & np.isfinite(ret)
    r0 = np.where(use, ret, 0.0)
    C_sig, C_n, C_s, C_s2 = _csum(active.astype(float)), _csum(use.astype(float)), _csum(r0), _csum(r0 ** 2)
    i = np.arange(n)
    start = np.maximum(0, i - window)
    end = i if legacy_window else np.maximum(i - horizon + 1, 0)
    end = np.maximum(end, start)
    count_sig = C_sig[end] - C_sig[start]
    n_ret = C_n[end] - C_n[start]
    s = C_s[end] - C_s[start]
    s2 = C_s2[end] - C_s2[start]
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = s / n_ret
        var = (s2 - n_ret * mean ** 2) / (n_ret - 1)
        se = np.sqrt(np.maximum(var, 0.0)) / np.sqrt(n_ret)
    enough = count_sig >= min_signals
    return {"ev": np.where(enough, mean, np.nan), "count": count_sig, "n": n_ret,
            "se": np.where(enough & (n_ret > 1), se, np.nan)}


def compute_probabilities(signal: np.ndarray, signal_defined: np.ndarray, window: int) -> np.ndarray:
    sig = np.nan_to_num(np.asarray(signal, dtype=float), nan=0.0) > 0
    defined = np.asarray(signal_defined, dtype=bool)
    n = len(sig)
    C_a, C_d = _csum((sig & defined).astype(float)), _csum(defined.astype(float))
    i = np.arange(n)
    start = np.maximum(0, i - window)
    k = C_d[i] - C_d[start]
    with np.errstate(invalid="ignore", divide="ignore"):
        p = (C_a[i] - C_a[start]) / k
    return np.where(k >= 10, p, np.nan)


def build_expected_value_90d(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c, L = cfg.expected_value, cfg.legacy
    df = df.copy().replace([np.inf, -np.inf], np.nan)
    missing = [col for col in ("terrain_transition_score", "close") if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando: {missing}")
    score = pd.to_numeric(df["terrain_transition_score"], errors="coerce").replace([np.inf, -np.inf], np.nan)
    close = pd.to_numeric(df["close"], errors="coerce").replace([np.inf, -np.inf], np.nan)
    n = len(df)

    cols: dict[str, Any] = {"terrain_transition_score": score.to_numpy()}
    fwd = {}
    for h in c.HORIZONS:
        fwd[h] = (close.shift(-h) / (close + c.EPS) - 1.0).to_numpy()   # 8.5: cauda fica NaN
        cols[f"ret_fwd_{h}"] = fwd[h]

    q_blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_QUANTILES)
    q_min = min_periods_for(cfg, L.LEGACY_GLOBAL_QUANTILES)
    s = score.to_numpy()
    q_high = quantile_threshold(s, q_blocks, c.Q_HIGH, q_min)
    q_low = quantile_threshold(s, q_blocks, c.Q_LOW, q_min)
    with np.errstate(invalid="ignore"):
        sig_long = (s >= q_high).astype(int)
        sig_short = (s <= q_low).astype(int)
    defined = np.isfinite(q_high) & np.isfinite(q_low)
    if L.LEGACY_GLOBAL_QUANTILES:
        defined = np.ones(n, dtype=bool)
    cols["signal_long"], cols["signal_short"] = sig_long, sig_short

    legacy_win = L.LEGACY_EV_WINDOW
    evs: dict[str, dict] = {}
    for h in c.HORIZONS:
        evs[f"long_{h}"] = rolling_expected_value(sig_long, fwd[h], c.WINDOW, h, legacy_win, c.MIN_SIGNALS)
        evs[f"short_{h}"] = rolling_expected_value(sig_short, -fwd[h], c.WINDOW, h, legacy_win, c.MIN_SIGNALS)
    for side in ("long", "short"):
        for h in c.HORIZONS:
            ev = evs[f"{side}_{h}"]["ev"]
            cols[f"ev_{side}_{h}"] = np.nan_to_num(ev, nan=0.0) if L.LEGACY_ZERO_FILL else ev

    prob_long = compute_probabilities(sig_long, defined, c.WINDOW)
    prob_short = compute_probabilities(sig_short, defined, c.WINDOW)
    if L.LEGACY_ZERO_FILL:
        prob_long, prob_short = np.nan_to_num(prob_long, nan=0.0), np.nan_to_num(prob_short, nan=0.0)
    cols["prob_long"], cols["prob_short"] = prob_long, prob_short
    cols["expected_value_score"] = prob_long * cols["ev_long_1"] + prob_short * cols["ev_short_1"]

    # 8.4 / 8.6
    cols["ev_valid"] = np.isfinite(cols["expected_value_score"]).astype(int)
    for side in ("long", "short"):
        cols[f"ev_{side}_1_n"] = evs[f"{side}_1"]["n"]
        cols[f"ev_{side}_1_se"] = evs[f"{side}_1"]["se"]

    out = assign_columns(df, cols)
    if L.LEGACY_ZERO_FILL:
        num = out.select_dtypes(include=[np.number]).columns
        out[num] = out[num].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    add_meta(out, "expected_value", {
        "ev_valid_share": float(np.mean(cols["ev_valid"])) if n else None,
        "median_signals_long": float(np.nanmedian(evs["long_1"]["n"])) if n else None,
        "median_se_long_1": float(np.nanmedian(evs["long_1"]["se"])) if np.isfinite(evs["long_1"]["se"]).any() else None,
    })
    return out
