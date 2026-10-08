"""Coordenadas de estado da camada geométrica, como o legado as define, e escalas causais.

Definições do legado (reproduzidas aqui sem os vazamentos):
  v      = retorno de 1 barra (pct_change)
  a      = Δv
  jerk   = Δa  (terceira diferença do preço relativo)
  E_geo  = v² + a²            (o "E_norm" que o ramo geométrico usa — sobrescreve o do input)
  mem_e  = EMA(E_geo, α=0.05)
  m_flux = Δ mem_e            (o "memory_flux" da camada 3D)
  λ      = 1 / (desvio-padrão móvel de v em 30 barras, mín. 10) — "lambda_dynamic"

Toda escala aqui usa apenas barras ANTERIORES à barra avaliada.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

ALPHA_MEM = 0.05
LAMBDA_WINDOW = 30
LAMBDA_MIN = 10


def legacy_coordinates(ohlcv: pd.DataFrame) -> pd.DataFrame:
    close = pd.to_numeric(ohlcv["close"], errors="coerce")
    v = close.pct_change()
    a = v.diff()
    jerk = a.diff()
    E = v ** 2 + a ** 2
    mem = E.ewm(alpha=ALPHA_MEM, adjust=False).mean()
    mflux = mem.diff()
    lam = 1.0 / (v.rolling(LAMBDA_WINDOW, min_periods=LAMBDA_MIN).std() + 1e-6)
    out = pd.DataFrame({"v": v, "a": a, "jerk": jerk, "E": E, "mem_e": mem,
                        "m_flux": mflux, "lam": lam})
    if "timestamp" in ohlcv:
        out.insert(0, "timestamp", ohlcv["timestamp"].values)
    return out


def realized_vol(ohlcv: pd.DataFrame, windows=(10, 30, 60)) -> pd.DataFrame:
    """Volatilidade realizada PASSADA (inclui a barra corrente, nunca a seguinte)."""
    r = np.log(pd.to_numeric(ohlcv["close"])).diff()
    return pd.DataFrame({f"logvol_{w}": np.log(r.rolling(w, min_periods=w // 2).std() + 1e-12)
                         for w in windows})


def causal_robust_z(x: pd.Series, window: int = 1500, min_periods: int = 300) -> pd.Series:
    """z = (x − mediana) / (1,4826·MAD), mediana e MAD das `window` barras ANTERIORES."""
    past = x.shift(1)
    med = past.rolling(window, min_periods=min_periods).median()
    mad = (past - med).abs().rolling(window, min_periods=min_periods).median()
    return (x - med) / (1.4826 * mad + 1e-300)


def causal_rank_gauss(x: pd.Series, window: int = 1500, min_periods: int = 300) -> pd.Series:
    """Posto da barra entre as `window` anteriores, levado à normal padrão."""
    vals = x.to_numpy(float)
    out = np.full(len(vals), np.nan)
    for t in range(len(vals)):
        lo = max(0, t - window)
        past = vals[lo:t]
        past = past[np.isfinite(past)]
        if len(past) < min_periods or not np.isfinite(vals[t]):
            continue
        rank = (np.sum(past < vals[t]) + 0.5 * np.sum(past == vals[t]) + 0.5) / (len(past) + 1.0)
        out[t] = norm.ppf(rank)
    return pd.Series(out, index=x.index)


def scale_coordinates(coords: pd.DataFrame, cols=("E", "jerk", "m_flux"), how: str = "robust_z",
                      window: int = 1500, min_periods: int = 300) -> pd.DataFrame:
    f = {"robust_z": causal_robust_z, "rank_gauss": causal_rank_gauss}[how]
    return pd.DataFrame({c: f(coords[c], window, min_periods) for c in cols})


def scott_bandwidth(n: int, d: int) -> float:
    """Regra de Scott para dados padronizados: h = n^(−1/(d+4))."""
    return float(n ** (-1.0 / (d + 4)))
