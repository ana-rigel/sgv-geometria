"""Correções de referência, independentes do SGV Operável original.

Somente auditoria. Nenhuma função aqui substitui o sistema principal.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def strict_annual_gate(net: pd.Series, bars_per_year: float, min_years: int = 4,
                       min_coverage: float = 0.95, min_sharpe: float = 0.8) -> dict:
    """Aprova somente >=4 anos civis completos com Sharpe >=0.8 por ano.

    Não reduz automaticamente o requisito quando existem poucos anos.
    """
    if not isinstance(net.index, pd.DatetimeIndex):
        raise TypeError("É necessário DatetimeIndex")
    if not (0 < min_coverage <= 1):
        raise ValueError("min_coverage deve estar em (0,1]")
    if bars_per_year <= 0 or min_years < 1:
        raise ValueError("Parâmetros anuais inválidos")
    per_year = {}
    for year, group in net.dropna().groupby(net.dropna().index.year):
        # Controla apenas anos com cobertura de amostras adequada.
        expected = bars_per_year * (366 if pd.Timestamp(year=year,month=12,day=31).dayofyear==366 else 365) / 365
        full = len(group) >= min_coverage * expected
        sd = float(group.std())
        sharpe = float(group.mean()/sd * np.sqrt(bars_per_year)) if sd > 0 else 0.0
        per_year[int(year)] = {"n":int(len(group)), "completo":bool(full),
                               "sharpe":sharpe, "passa":bool(full and sharpe >= min_sharpe)}
    count = sum(x["passa"] for x in per_year.values())
    full_count = sum(x["completo"] for x in per_year.values())
    return {"aprovado":bool(count >= min_years), "anos_completos":full_count,
            "anos_aprovados":count, "exigidos":min_years, "por_ano":per_year}


def risk_sized_returns(trades: pd.DataFrame, index: pd.DatetimeIndex,
                       risk_fraction: float, stop_fraction: float,
                       max_exposure: float = 1.0) -> pd.Series:
    """Retorno sobre capital considerando tamanho nocional por orçamento de stop.

    Trata net como retorno por unidade de notional. Não modela MTM antes da saída,
    gaps, slippage variável, liquidação ou ociosidade; serve para testar sizing.
    """
    if not 0 < risk_fraction <= 1 or not 0 < stop_fraction <= 1:
        raise ValueError("Frações inválidas")
    if max_exposure <= 0:
        raise ValueError("Exposição máxima inválida")
    unit = min(max_exposure, risk_fraction / stop_fraction)
    out = pd.Series(0.0, index=index, name="capital_return_at_exit")
    for _, row in trades.iterrows():
        ts = row["exit_time"]
        if ts not in out.index:
            raise ValueError(f"Saída fora do calendário: {ts}")
        out.loc[ts] += unit * float(row["net"])
    return out
