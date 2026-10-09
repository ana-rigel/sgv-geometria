"""Reformulação R1: coordenadas de fluxo de ordens e nulo SF1 (fatos estilizados).

Especificação: PREREGISTRO_R1.md. Este arquivo é uma RECONSTRUÇÃO (09/10/2026): a
versão original, nunca commitada, foi sobrescrita por engano pela execução paralela
da C2 (retirada). Interface e especificação são as mesmas; a calibração foi refeita
com este código.

Coordenadas (todas conhecidas no fechamento da barra t):
  z  = r_t / σ_t, σ = desvio-padrão dos retornos das 60 barras ANTERIORES
  ι  = 2·taker_buy/volume − 1                 (desequilíbrio do fluxo agressor)
  ν  = log volume_t − mediana do log volume nas 1500 barras ANTERIORES (atividade relativa)

Nulo SF1, ajustado ao próprio segmento:
  retornos   GARCH(1,1)-t
  ι* = a0 + a1·z + a2·ι*₋₁ + e1,  ι = tanh(ι*)
  ℓ  = b0 + b1·ℓ₋₁ + b2·|z| + b3·z + e2         (ℓ = log volume)
  (e1, e2) sorteados em par dos resíduos do ajuste
Alternativa de calibração ("interaction"): a inclinação do impacto depende da
atividade, a1 → a1 + interaction·ν̃ (ν̃ = ℓ padronizado), estrutura fora do SF1.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .data import T0_MS, fit_garch_t

SIGMA_WINDOW = 60
NU_WINDOW, NU_MIN = 1500, 300
CLIP = 0.999


def flow_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    close = pd.to_numeric(df["close"]).astype(float)
    vol = pd.to_numeric(df["volume"]).astype(float)
    buy = pd.to_numeric(df["taker_buy"]).astype(float)
    r = np.log(close).diff()
    sigma = r.shift(1).rolling(SIGMA_WINDOW, min_periods=SIGMA_WINDOW // 2).std()
    z = r / sigma
    iota = pd.Series(np.where(vol > 0, 2.0 * buy / vol.where(vol > 0, 1.0) - 1.0, 0.0),
                     index=df.index).clip(-1, 1)
    ell = np.log(vol.clip(lower=1e-12))
    nu = ell - ell.shift(1).rolling(NU_WINDOW, min_periods=NU_MIN).median()
    out = pd.DataFrame({"r": r, "z": z, "iota": iota, "nu": nu, "ell": ell})
    if "timestamp" in df:
        out.insert(0, "timestamp", df["timestamp"].values)
    return out


# ---------------------------------------------------------------------------
@dataclass
class SF1:
    garch: dict
    a: np.ndarray                      # a0, a1, a2
    b: np.ndarray                      # b0, b1, b2, b3
    resid: np.ndarray | None = None    # pares (e1, e2) do ajuste, para sorteio conjunto
    e_sd: tuple = (0.5, 0.4)           # usados só quando não há resíduos (modelo padrão)
    e_corr: float = 0.2
    meta: dict = field(default_factory=dict)


def default_sf1() -> SF1:
    """Parâmetros plausíveis para BTC 1m (escala dos ajustes da Fase 1)."""
    return SF1(garch={"omega": 1e-8, "alpha": 0.08, "beta": 0.90, "nu": 4.0},
               a=np.array([0.0, 0.35, 0.15]), b=np.array([0.3, 0.8, 0.35, 0.0]))


def _garch_paths(n, g, rng):
    scale = np.sqrt((g["nu"] - 2.0) / g["nu"])
    s2 = g["omega"] / max(1e-12, 1.0 - g["alpha"] - g["beta"])
    r, sig = np.empty(n), np.empty(n)
    prev = 0.0
    for t in range(n):
        s2 = g["omega"] + g["alpha"] * prev * prev + g["beta"] * s2
        sig[t] = np.sqrt(s2)
        prev = sig[t] * rng.standard_t(g["nu"]) * scale
        r[t] = prev
    return r, sig


def _garch_filter(r, g):
    s2 = np.empty(len(r))
    s2[0] = np.var(r)
    for t in range(1, len(r)):
        s2[t] = g["omega"] + g["alpha"] * r[t - 1] ** 2 + g["beta"] * s2[t - 1]
    return np.sqrt(s2)


def simulate_sf1(m: SF1, n: int, seed: int = 0, interaction: float = 0.0,
                 p0: float = 60_000.0, step_ms: int = 60_000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    r, sig = _garch_paths(n, m.garch, rng)
    z = r / sig
    if m.resid is not None and len(m.resid):
        E = m.resid[rng.integers(0, len(m.resid), n)]
    else:
        s1, s2 = m.e_sd
        cov = [[s1 * s1, m.e_corr * s1 * s2], [m.e_corr * s1 * s2, s2 * s2]]
        E = rng.multivariate_normal([0.0, 0.0], cov, n)
    b0, b1, b2, b3 = m.b
    ell = np.empty(n)
    prev = b0 / max(1e-6, 1.0 - b1)
    for t in range(n):
        prev = b0 + b1 * prev + b2 * abs(z[t]) + b3 * z[t] + E[t, 1]
        ell[t] = prev
    nu_t = (ell - ell.mean()) / (ell.std() + 1e-12)
    a0, a1, a2 = m.a
    istar = np.empty(n)
    prev = 0.0
    for t in range(n):
        prev = a0 + (a1 + interaction * nu_t[t]) * z[t] + a2 * prev + E[t, 0]
        istar[t] = prev
    iota = np.tanh(istar)
    close = p0 * np.exp(np.cumsum(r))
    open_ = np.r_[p0, close[:-1]]
    wick = np.abs(rng.normal(0, 1, n)) * np.abs(r).mean() * 0.5
    volume = np.exp(ell)
    ts = T0_MS + step_ms * np.arange(n)
    return pd.DataFrame({
        "timestamp": ts, "datetime": pd.to_datetime(ts, unit="ms", utc=True).astype(str),
        "open": open_, "high": np.maximum(open_, close) * (1 + wick),
        "low": np.minimum(open_, close) * (1 - wick), "close": close,
        "volume": volume, "taker_buy": (iota + 1.0) / 2.0 * volume,
        "trades": np.maximum(1, np.round(volume * 10)).astype(int),
    })


def fit_sf1(df: pd.DataFrame) -> SF1:
    """Ajusta o SF1 a um segmento (real ou sintético): GARCH-t por MV, depois as duas
    regressões por mínimos quadrados, guardando os pares de resíduos."""
    close = pd.to_numeric(df["close"]).astype(float).to_numpy()
    vol = pd.to_numeric(df["volume"]).astype(float).to_numpy()
    buy = pd.to_numeric(df["taker_buy"]).astype(float).to_numpy()
    r = np.diff(np.log(close))
    mu = r.mean()
    g = fit_garch_t(r - mu)
    z = (r - mu) / _garch_filter(r - mu, g)
    iota = np.where(vol > 0, 2 * buy / np.where(vol > 0, vol, 1) - 1, 0)[1:]
    istar = np.arctanh(np.clip(iota, -CLIP, CLIP))
    ell = np.log(np.clip(vol, 1e-12, None))[1:]
    # ι*_t ~ 1 + z_t + ι*_{t−1}
    X1 = np.column_stack([np.ones(len(z) - 1), z[1:], istar[:-1]])
    y1 = istar[1:]
    a, *_ = np.linalg.lstsq(X1, y1, rcond=None)
    # ℓ_t ~ 1 + ℓ_{t−1} + |z_t| + z_t
    X2 = np.column_stack([np.ones(len(z) - 1), ell[:-1], np.abs(z[1:]), z[1:]])
    y2 = ell[1:]
    b, *_ = np.linalg.lstsq(X2, y2, rcond=None)
    resid = np.column_stack([y1 - X1 @ a, y2 - X2 @ b])
    return SF1(garch=g, a=a, b=b, resid=resid, meta={"mu": float(mu), "n": int(len(r))})
