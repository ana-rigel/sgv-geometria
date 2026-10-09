"""Sleeve A — Tendência (time-series momentum, 4h/1d).

Núcleo do portfólio. Long quando momentum de lookback é positivo E preço está
acima da média móvel; flat caso contrário. Sizing por vol-alvo. Sinal na barra
t, execução na abertura de t+1 (sem lookahead).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import Config
from ..features import BARS_PER_YEAR, realized_vol_annual


def signal(df: pd.DataFrame, cfg: Config) -> pd.Series:
    """Posição-alvo em [0, max_position] por barra (fração do capital)."""
    t = cfg.trend
    mom = df["close"].pct_change(t.lookback_bars)
    ma = df["close"].rolling(t.ma_bars, min_periods=t.ma_bars).mean()
    raw = ((mom > 0) & (df["close"] > ma)).astype(float)
    if t.allow_short:
        raw = raw - ((mom < 0) & (df["close"] < ma)).astype(float)

    vol = realized_vol_annual(df["close"], t.vol_span, BARS_PER_YEAR[t.timeframe])
    scale = (cfg.risk.target_vol_annual / vol).clip(upper=cfg.risk.max_position)
    return (raw * scale).fillna(0.0).rename("pos_trend")


def backtest(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Retornos da sleeve com custos. Posição decidida em t aplica ao retorno t+1."""
    pos = signal(df, cfg)
    ret_next = df["open"].shift(-1).pct_change().shift(-0)  # placeholder, ver abaixo
    # retorno da barra t+1 medido open(t+1)->open(t+2): captura exatamente o
    # período em que a posição decidida em t esteve ativa.
    o = df["open"]
    ret_fwd = (o.shift(-2) / o.shift(-1) - 1.0)
    gross = pos * ret_fwd
    turnover = pos.diff().abs().fillna(pos.abs())
    costs = turnover * cfg.costs.round_trip / 2  # custo por lado a cada mudança
    out = pd.DataFrame({"pos": pos, "gross": gross, "cost": costs})
    out["net"] = out["gross"] - out["cost"]
    return out.dropna(subset=["net"])
