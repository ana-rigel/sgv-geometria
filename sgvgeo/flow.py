"""Reformulação C2: coordenadas preço–fluxo, nulo "GARCH + lei de impacto" e sintéticos.

Especificação em PREREGISTRO_C2.md (registrado antes de qualquer cálculo em dado real).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import T0_MS, fit_garch_t


# ---------------------------------------------------------------------------
# Coordenadas C2
# ---------------------------------------------------------------------------
def c2_coordinates(ohlcv: pd.DataFrame) -> pd.DataFrame:
    """x1 = r (retorno log com sinal), x2 = ι (desequilíbrio agressor), x3 = ℓ (log volume)."""
    close = pd.to_numeric(ohlcv["close"])
    vol = pd.to_numeric(ohlcv["volume"]).astype(float)
    taker = pd.to_numeric(ohlcv["taker_buy_base"]).astype(float)
    r = np.log(close).diff()
    iota = pd.Series(np.where(vol > 0, 2.0 * taker / vol.where(vol > 0, 1.0) - 1.0, 0.0), index=ohlcv.index)
    ell = np.log(vol.clip(lower=1e-12))
    out = pd.DataFrame({"r": r, "iota": iota.clip(-1, 1), "ell": ell})
    # v e a para os controles de volatilidade de D5 (mesma definição de C1)
    v = close.pct_change()
    out["v"], out["a"] = v, v.diff()
    if "timestamp" in ohlcv:
        out.insert(0, "timestamp", ohlcv["timestamp"].values)
    return out


C2_COLS = ("r", "iota", "ell")


# ---------------------------------------------------------------------------
# GARCH com σ explícito
# ---------------------------------------------------------------------------
def garch_paths(n: int, omega: float, alpha: float, beta: float, nu: float, seed: int):
    rng = np.random.default_rng(seed)
    scale = np.sqrt((nu - 2.0) / nu)
    s2 = omega / max(1e-12, 1.0 - alpha - beta)
    r, sig = np.empty(n), np.empty(n)
    prev = 0.0
    for t in range(n):
        s2 = omega + alpha * prev * prev + beta * s2
        sig[t] = np.sqrt(s2)
        prev = sig[t] * rng.standard_t(nu) * scale
        r[t] = prev
    return r, sig


def garch_filter(r: np.ndarray, p: dict) -> np.ndarray:
    r = np.asarray(r, float)
    s2 = np.empty(len(r))
    s2[0] = np.var(r)
    for t in range(1, len(r)):
        s2[t] = p["omega"] + p["alpha"] * r[t - 1] ** 2 + p["beta"] * s2[t - 1]
    return np.sqrt(s2)


def _ohlcv(r, iota, ell, ts, p0=60_000.0, seed=0):
    rng = np.random.default_rng(seed)
    close = p0 * np.exp(np.cumsum(r))
    open_ = np.r_[p0, close[:-1]]
    wick = np.abs(rng.normal(0, 1, len(r))) * np.abs(r).mean() * 0.5
    vol = np.exp(ell)
    return pd.DataFrame({
        "timestamp": ts, "datetime": pd.to_datetime(ts, unit="ms", utc=True).astype(str),
        "open": open_, "high": np.maximum(open_, close) * (1 + wick),
        "low": np.minimum(open_, close) * (1 - wick), "close": close,
        "volume": vol, "taker_buy_base": (np.clip(iota, -1, 1) + 1.0) / 2.0 * vol,
    })


# ---------------------------------------------------------------------------
# Sintéticos de calibração (seção 7 do pré-registro)
# ---------------------------------------------------------------------------
def synthetic_flow(n: int = 6000, seed: int = 0, planted: bool = False) -> pd.DataFrame:
    """(a) planted=False: sem geometria própria (lei de impacto estacionária).
    (b) planted=True: regime oculto de Markov (permanência 0,998, independente da
        volatilidade) troca a curva de impacto (1,4·z / 0,2·z) e acopla ℓ a ι."""
    rng = np.random.default_rng(seed + 1000)
    r, sig = garch_paths(n, 1e-8, 0.08, 0.90, 4.0, seed)
    z = r / sig
    u, w = rng.normal(size=n), rng.normal(size=n)
    if planted:
        s = np.empty(n, int)
        s[0] = 0
        flips = rng.random(n) > 0.998
        for t in range(1, n):
            s[t] = 1 - s[t - 1] if flips[t] else s[t - 1]
        kappa = np.where(s == 0, 1.4, 0.2)
    else:
        s = np.zeros(n, int)
        kappa = np.full(n, 0.8)
    iota = np.tanh(kappa * z + 0.6 * u)
    ell = 2.0 + np.log(sig / np.median(sig)) + 0.35 * np.abs(z) + 0.4 * w
    if planted:
        ell = ell + 0.5 * iota * (s == 1)
    ts = T0_MS + 60_000 * np.arange(n)
    df = _ohlcv(r, iota, ell, ts, seed=seed)
    df["regime_oculto"] = s
    return df


# ---------------------------------------------------------------------------
# Nulo "GARCH + lei de impacto estacionária" (seção 4 do pré-registro)
# ---------------------------------------------------------------------------
class ImpactNull:
    """Ajustado num segmento real; gera réplicas com preço GARCH-t e fluxo sorteado
    das barras reais da mesma célula (faixa de z × faixa de log σ × bloco de 4 h)."""

    MIN_CELL = 5

    def __init__(self, ohlcv: pd.DataFrame):
        c = c2_coordinates(ohlcv)
        r = c["r"].fillna(0.0).to_numpy()
        self.params = fit_garch_t(r)
        sig = garch_filter(r - r.mean(), self.params)
        z = (r - r.mean()) / sig
        self.z_edges = np.quantile(z, np.linspace(0, 1, 11)[1:-1])
        self.s_edges = np.quantile(np.log(sig), [1 / 3, 2 / 3])
        self.ts = ohlcv["timestamp"].to_numpy()
        hours = pd.to_datetime(self.ts, unit="ms", utc=True).hour.to_numpy()
        self.hblk = hours // 4
        self.p0 = float(ohlcv["close"].iloc[0])
        self.mu = r.mean()
        self.flow = c[["iota", "ell"]].to_numpy()
        zb = np.digitize(z, self.z_edges)
        sb = np.digitize(np.log(sig), self.s_edges)
        self.cells_full, self.cells_zs, self.cells_z = {}, {}, {}
        for i, (a, b, h) in enumerate(zip(zb, sb, self.hblk)):
            if i == 0 or not np.all(np.isfinite(self.flow[i])):
                continue
            self.cells_full.setdefault((a, b, h), []).append(i)
            self.cells_zs.setdefault((a, b), []).append(i)
            self.cells_z.setdefault(a, []).append(i)

    def _pool(self, a, b, h):
        for pool in (self.cells_full.get((a, b, h)), self.cells_zs.get((a, b)), self.cells_z.get(a)):
            if pool is not None and len(pool) >= self.MIN_CELL:
                return pool
        return self.cells_z.get(a) or [1]

    def sample(self, seed: int) -> pd.DataFrame:
        p = self.params
        n = len(self.ts)
        r, sig = garch_paths(n, p["omega"], p["alpha"], p["beta"], p["nu"], seed)
        zb = np.digitize(r / sig, self.z_edges)
        sb = np.digitize(np.log(sig), self.s_edges)
        rng = np.random.default_rng(seed + 7)
        idx = np.array([rng.choice(self._pool(a, b, h)) for a, b, h in zip(zb, sb, self.hblk)])
        iota, ell = self.flow[idx, 0], self.flow[idx, 1]
        return _ohlcv(r + self.mu, iota, ell, self.ts, p0=self.p0, seed=seed)
