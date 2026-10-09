"""Dados: sintéticos, substitutos e klines reais.

Regra do projeto: nenhum diagnóstico de existência/forma da geometria usa retorno
futuro. Os geradores aqui produzem apenas OHLCV.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

T0_MS = 1_756_684_800_000  # 2025-09-01 00:00 UTC (só rótulo de tempo para dados sintéticos)


# ---------------------------------------------------------------------------
# Sintético: GARCH(1,1) com choques t de Student (escala típica do BTC 1m:
# desvio incondicional ≈ 0,07% por minuto, α=0,08, β=0,90, ν=4)
# ---------------------------------------------------------------------------
def garch_t_returns(n: int, omega: float = 1e-8, alpha: float = 0.08, beta: float = 0.90,
                    nu: float = 4.0, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    scale = np.sqrt((nu - 2.0) / nu)  # variância unitária do choque t
    s2 = omega / max(1e-12, 1.0 - alpha - beta)
    r = np.empty(n)
    prev = 0.0
    for t in range(n):
        s2 = omega + alpha * prev * prev + beta * s2
        prev = np.sqrt(s2) * rng.standard_t(nu) * scale
        r[t] = prev
    return r


def ohlcv_from_returns(r: np.ndarray, p0: float = 60_000.0, seed: int = 1,
                       t0_ms: int = T0_MS, step_ms: int = 60_000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = len(r)
    close = p0 * np.exp(np.cumsum(r))
    open_ = np.r_[p0, close[:-1]]
    wick = np.abs(rng.normal(0.0, 1.0, n)) * np.abs(r).mean() * 0.5
    high = np.maximum(open_, close) * (1.0 + wick)
    low = np.minimum(open_, close) * (1.0 - wick)
    ts = t0_ms + step_ms * np.arange(n)
    vol = rng.gamma(2.0, 5.0, n) * (1.0 + 50.0 * np.abs(r) / (np.abs(r).mean() + 1e-12))
    return pd.DataFrame({
        "timestamp": ts,
        "datetime": pd.to_datetime(ts, unit="ms", utc=True).astype(str),
        "open": open_, "high": high, "low": low, "close": close, "volume": vol,
    })


def synthetic_btc_1m(n: int = 6000, seed: int = 0) -> pd.DataFrame:
    return ohlcv_from_returns(garch_t_returns(n, seed=seed), seed=seed + 1)


# ---------------------------------------------------------------------------
# Substitutos (hipótese nula) para o teste de existência
# ---------------------------------------------------------------------------
def surrogate_shuffle(r: np.ndarray, seed: int = 0) -> np.ndarray:
    """Destrói toda estrutura temporal; preserva a distribuição marginal."""
    return np.random.default_rng(seed).permutation(r)


def surrogate_iaaft(r: np.ndarray, n_iter: int = 100, seed: int = 0) -> np.ndarray:
    """IAAFT: preserva espectro (autocorrelação linear) e distribuição marginal;
    destrói estrutura não linear (inclusive boa parte do agrupamento de volatilidade)."""
    rng = np.random.default_rng(seed)
    sorted_r = np.sort(r)
    amp = np.abs(np.fft.rfft(r))
    x = rng.permutation(r)
    for _ in range(n_iter):
        phases = np.angle(np.fft.rfft(x))
        x = np.fft.irfft(amp * np.exp(1j * phases), n=len(r))
        x = sorted_r[np.argsort(np.argsort(x))]
    return x


def _garch_t_negloglik(params: np.ndarray, r: np.ndarray) -> float:
    omega, alpha, beta, nu = params
    if omega <= 0 or alpha < 0 or beta < 0 or alpha + beta >= 0.9999 or nu <= 2.05:
        return 1e12
    n = len(r)
    s2 = np.empty(n)
    s2[0] = r.var()
    for t in range(1, n):
        s2[t] = omega + alpha * r[t - 1] ** 2 + beta * s2[t - 1]
    scale = np.sqrt(s2 * (nu - 2.0) / nu)
    return -np.sum(stats.t.logpdf(r / scale, nu) - np.log(scale))


def fit_garch_t(r: np.ndarray) -> dict:
    """MLE simples de GARCH(1,1)-t (sem dependências extras)."""
    r = np.asarray(r, float) - np.mean(r)
    v = r.var()
    x0 = np.array([v * 0.02, 0.08, 0.90, 5.0])
    res = optimize.minimize(_garch_t_negloglik, x0, args=(r,), method="Nelder-Mead",
                            options={"maxiter": 4000, "xatol": 1e-10, "fatol": 1e-6})
    omega, alpha, beta, nu = res.x
    return {"omega": omega, "alpha": alpha, "beta": beta, "nu": nu, "converged": bool(res.success)}


def surrogate_garch(r: np.ndarray, seed: int = 0, params: dict | None = None) -> np.ndarray:
    """Substituto mais exigente: série nova de um GARCH-t ajustado aos dados.
    Preserva agrupamento de volatilidade e caudas; não preserva nada além disso."""
    p = params or fit_garch_t(r)
    return garch_t_returns(len(r), p["omega"], p["alpha"], p["beta"], p["nu"], seed=seed)


# ---------------------------------------------------------------------------
# Klines reais da Binance (formato data.binance.vision ou CSV já tratado)
# ---------------------------------------------------------------------------
KLINE_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
              "quote_volume", "trades", "taker_base", "taker_quote", "ignore"]


def _read_kline_frame(buf) -> pd.DataFrame:
    df = pd.read_csv(buf, header=None)
    if isinstance(df.iloc[0, 0], str) and not str(df.iloc[0, 0]).isdigit():
        df = df.iloc[1:].reset_index(drop=True)  # arquivo com cabeçalho
    df = df.iloc[:, :12]
    df.columns = KLINE_COLS[: df.shape[1]]
    return df


def load_binance_klines(paths, with_flow: bool = False) -> pd.DataFrame:
    """Lê um ou vários .zip/.csv de klines da Binance e devolve OHLCV no formato do SGV.

    with_flow=True acrescenta `trades` (nº de negócios) e `taker_buy` (volume base
    comprado por ordens agressoras), usados pelas coordenadas de fluxo (R1).

    Trata timestamps em milissegundos e em microssegundos (a Binance passou a
    usar microssegundos nos dumps de spot a partir de 2025)."""
    if isinstance(paths, (str, Path)):
        paths = [paths]
    frames = []
    for p in sorted(Path(x) for x in paths):
        if p.suffix == ".zip":
            with zipfile.ZipFile(p) as z:
                for name in z.namelist():
                    if name.endswith(".csv"):
                        frames.append(_read_kline_frame(io.BytesIO(z.read(name))))
        else:
            frames.append(_read_kline_frame(p))
    df = pd.concat(frames, ignore_index=True)
    ot = pd.to_numeric(df["open_time"], errors="coerce").astype("int64")
    ot = np.where(ot > 10**14, ot // 1000, ot)  # µs -> ms
    out = pd.DataFrame({
        "timestamp": ot,
        "open": pd.to_numeric(df["open"]), "high": pd.to_numeric(df["high"]),
        "low": pd.to_numeric(df["low"]), "close": pd.to_numeric(df["close"]),
        "volume": pd.to_numeric(df["volume"]),
    })
    if "taker_base" in df:  # fluxo agressor (usado pela reformulação C2)
        out["taker_buy_base"] = pd.to_numeric(df["taker_base"]).values
        out["trades"] = pd.to_numeric(df["trades"]).values
    if with_flow:
        out["trades"] = pd.to_numeric(df["trades"], errors="coerce")
        out["taker_buy"] = pd.to_numeric(df["taker_base"], errors="coerce")
    out = out.drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    out.insert(1, "datetime", pd.to_datetime(out["timestamp"], unit="ms", utc=True).astype(str))
    return out
