"""Dados sintéticos para testes e placebos.

``make_input`` gera barras de 1 minuto de um passeio aleatório com
volatilidade agrupada (GARCH(1,1) simples), sem nenhuma estrutura direcional.
É o "mercado nulo": num pipeline sem vazamento, EV, alinhamento e taxas de
alerta devem ficar no nível de acaso nesses dados.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def make_input(n: int = 600, seed: int = 0, scale: str = "unit", start: str = "2026-05-01") -> pd.DataFrame:
    """Barras com ``timestamp``, ``close``, ``E_norm``, ``jerk`` e ``lambda_dynamic``.

    scale="raw": E_norm e jerk calculados do preço como no arquivo 1
    (ordens de grandeza 1e-6 e 1e-3, como nos dados reais de 1m).
    scale="unit": as mesmas séries divididas pela sua escala robusta (O(1)),
    útil para exercitar a geometria nos testes de paridade.
    """
    rng = np.random.default_rng(seed)
    m = n + 3
    omega, alpha, beta = 2e-8, 0.08, 0.90
    var = omega / (1 - alpha - beta)
    r = np.empty(m)
    for t in range(m):
        z = rng.standard_t(5) / np.sqrt(5 / 3)
        r[t] = np.sqrt(var) * z
        var = omega + alpha * r[t] ** 2 + beta * var
    close = 60000.0 * np.exp(np.cumsum(r))
    ts = pd.date_range(start, periods=m, freq="1min", tz="UTC")
    df = pd.DataFrame({"timestamp": ts, "close": close})
    ret = df["close"].pct_change()
    acc = ret.diff()
    jerk = acc.diff()
    e_norm = ret ** 2 + acc ** 2
    if scale == "unit":
        e_norm = e_norm / np.nanmedian(e_norm)
        jerk = jerk / (1.4826 * np.nanmedian(np.abs(jerk - np.nanmedian(jerk))))
    lam = np.empty(m)
    a = 0.0
    for t in range(m):
        a = 0.9 * a + rng.normal(0, 0.1)
        lam[t] = 0.05 + abs(a)
    near_zero = rng.random(m) < 0.02
    lam[near_zero] = rng.uniform(0, 1e-4, near_zero.sum())
    df["E_norm"] = e_norm
    df["jerk"] = jerk
    df["lambda_dynamic"] = lam
    return df.iloc[3:].reset_index(drop=True)


def make_raw_ohlc(n: int = 2000, seed: int = 0, start: str = "2026-05-01") -> pd.DataFrame:
    """Barras OHLCV de 1 minuto no formato do ``btc_90d_1m_raw.csv`` (timestamp em ms)."""
    base = make_input(n, seed=seed, scale="raw", start=start)
    close = base["close"]
    rng = np.random.default_rng(seed + 1)
    wiggle = np.abs(rng.normal(0, 2e-4, len(close)))
    return pd.DataFrame({
        "timestamp": (base["timestamp"].astype("int64") // 10**6).to_numpy(),
        "datetime": base["timestamp"].astype(str).to_numpy(),
        "open": close.shift(1).fillna(close).to_numpy(),
        "high": (close * (1 + wiggle)).to_numpy(),
        "low": (close * (1 - wiggle)).to_numpy(),
        "close": close.to_numpy(),
        "volume": rng.gamma(2.0, 5.0, len(close)),
    })


def make_sgv_input(n: int = 2000, seed: int = 0, cfg=None) -> pd.DataFrame:
    """Input no formato real do SGV (E_norm, jerk e λ como o construtor de input os define)."""
    from .config import DEFAULT_CONFIG
    from .input_builder import build_btc_90d_input_sgv
    return build_btc_90d_input_sgv(make_raw_ohlc(n, seed=seed), cfg or DEFAULT_CONFIG)
