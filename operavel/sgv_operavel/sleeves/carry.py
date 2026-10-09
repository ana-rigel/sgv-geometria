"""Sleeve C — Carry de funding delta-neutro (spot long + perp short).

Sem previsão: colhe o funding quando ele está alto. Requer série de funding
rates (CSV com colunas timestamp, funding_rate por período de 8h). Sem a
série, a sleeve fica inativa e o backtest reporta isso explicitamente.

Retorno modelado = funding recebido - custos de montagem/desmontagem
(4 pernas: compra spot, venda perp, e o inverso na saída). Risco residual
(basis, liquidação da perna perp) tratado na Fase 2 com margem >= 3x.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import Config


def load_funding(path: str | Path) -> pd.Series:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    tcol = next(c for c in df.columns if "time" in c or "date" in c)
    rcol = next(c for c in df.columns if "rate" in c and "interval" not in c)
    ts = pd.to_numeric(df[tcol], errors="coerce")
    idx = (pd.to_datetime(ts, unit="ms", utc=True) if ts.notna().all()
           else pd.to_datetime(df[tcol], utc=True))
    return pd.Series(pd.to_numeric(df[rcol], errors="coerce").values, index=idx).sort_index().dropna()


def backtest(funding: pd.Series, cfg: Config) -> pd.DataFrame:
    """Estado por período de funding: dentro/fora + retorno líquido."""
    c = cfg.carry
    per_year = 365 * 24 / c.funding_period_hours
    ann = funding * per_year

    in_pos, rows = False, []
    setup_cost = cfg.costs.round_trip * 2  # 4 pernas ao montar+desmontar
    for ts, f in funding.items():
        a = ann.loc[ts]
        ret, event = 0.0, ""
        if not in_pos and a > c.min_annualized:
            in_pos, event, ret = True, "ENTER", -setup_cost / 2
        elif in_pos and a <= c.exit_annualized:
            in_pos, event, ret = False, "EXIT", -setup_cost / 2
        if in_pos and event != "ENTER":
            ret += f  # short do perp recebe o funding positivo
        rows.append({"time": ts, "funding": f, "annualized": a,
                     "in_pos": in_pos, "event": event, "net": ret})
    return pd.DataFrame(rows).set_index("time")
