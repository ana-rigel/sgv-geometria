"""Sleeve B — Evento de ruptura de atividade (o DNA do SGV, migrado para 15m/1h).

Trade: no início de um evento de ruptura EM CLUSTER (T2), em regime de
volatilidade, entra na direção do momentum na abertura da barra seguinte;
sai por stop (avaliado no fechamento de cada barra) ou por tempo (hold_bars).

Tudo aqui foi validado na auditoria de 08/2026; o que não validou não existe
neste arquivo. Uma posição por vez. Sem lookahead: decisão em t, fill em
open(t+1).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import Config
from ..features import burst_event, momentum_sign, vol_regime


def entries(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Tabela de candidatos: index = barra do sinal, colunas dir/cluster."""
    c = cfg.collapse
    ev = burst_event(df, c)
    mom = momentum_sign(df, c.momentum_bars)
    reg = vol_regime(df)

    mask = reg & (mom != 0)
    mask &= ev["t2_start"] if c.only_cluster else ev["event_start"]
    if c.block_hours_utc:
        mask &= ~df.index.hour.isin(c.block_hours_utc)

    out = pd.DataFrame({"dir": mom[mask]}, index=df.index[mask])
    out["cluster"] = ev.loc[out.index, "cluster"]
    return out


def backtest(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Simula trade a trade. Devolve DataFrame de trades com retornos líquidos."""
    c = cfg.collapse
    cand = entries(df, cfg)
    o, cl = df["open"].values, df["close"].values
    pos_of = {ts: i for i, ts in enumerate(df.index)}

    trades, busy_until = [], -1
    for ts, row in cand.iterrows():
        i = pos_of[ts]
        entry_i = i + 1                      # fill na abertura da barra seguinte
        if entry_i <= busy_until or entry_i + c.hold_bars + 1 >= len(df):
            continue
        d, e = float(row["dir"]), o[entry_i]
        exit_i, motivo = entry_i + c.hold_bars, "TIME"
        for k in range(entry_i, entry_i + c.hold_bars):
            if d * (cl[k] / e - 1.0) <= c.stop_ret:
                exit_i, motivo = k + 1, "STOP"   # sai na abertura seguinte ao gatilho
                break
        exit_px = o[exit_i]
        gross = d * (exit_px / e - 1.0)
        net = gross - cfg.costs.round_trip
        trades.append({
            "signal_time": ts, "entry_time": df.index[entry_i],
            "exit_time": df.index[exit_i], "dir": d, "motivo": motivo,
            "gross": gross, "net": net,
        })
        busy_until = exit_i
    return pd.DataFrame(trades)


def returns_series(trades: pd.DataFrame, index: pd.DatetimeIndex, risk_frac: float) -> pd.Series:
    """Converte trades em série de retornos do capital da sleeve.

    Cada trade arrisca `risk_frac` do capital até o stop: exposição =
    risk_frac / |stop|. Mantém risco por trade constante (Plano §4 Fase 3).
    """
    ser = pd.Series(0.0, index=index)
    if trades.empty:
        return ser
    for _, t in trades.iterrows():
        ser.loc[t["exit_time"]] += t["net"]
    return ser
