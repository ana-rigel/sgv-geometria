"""Portfólio, métricas, walk-forward anual e gates pré-registrados (Plano §4)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import Config
from .features import BARS_PER_YEAR


# --------------------------- métricas ---------------------------

def metrics(net: pd.Series, bars_per_year: float) -> dict:
    net = net.dropna()
    if net.empty or net.abs().sum() == 0:
        return {"n_bars": len(net), "ret_total": 0.0, "sharpe": 0.0,
                "max_dd": 0.0, "ret_anual": 0.0}
    eq = (1 + net).cumprod()
    dd = 1 - eq / eq.cummax()
    mu, sd = net.mean(), net.std()
    years = len(net) / bars_per_year
    return {
        "n_bars": len(net),
        "ret_total": float(eq.iloc[-1] - 1),
        "ret_anual": float(eq.iloc[-1] ** (1 / max(years, 1e-9)) - 1),
        "sharpe": float(mu / sd * np.sqrt(bars_per_year)) if sd > 0 else 0.0,
        "max_dd": float(dd.max()),
    }


def trade_metrics(trades: pd.DataFrame, cost: float) -> dict:
    if trades.empty:
        return {"n": 0, "wr": 0.0, "edge_medio": 0.0, "edge_cost_ratio": 0.0}
    net = trades["net"]
    return {
        "n": len(trades),
        "wr": float((net > 0).mean()),
        "edge_medio": float(net.mean()),
        "edge_cost_ratio": float((trades["gross"].mean()) / cost) if cost > 0 else np.inf,
    }


# --------------------------- portfólio ---------------------------

def combine(sleeve_returns: dict[str, pd.Series], weights: dict[str, float]) -> pd.Series:
    """Combina séries de retorno das sleeves nos pesos dados (rebalance implícito por barra)."""
    idx = None
    for s in sleeve_returns.values():
        idx = s.index if idx is None else idx.union(s.index)
    total = pd.Series(0.0, index=idx.sort_values())
    for name, ser in sleeve_returns.items():
        total = total.add(ser.reindex(total.index).fillna(0.0) * weights.get(name, 0.0), fill_value=0.0)
    return total.rename("portfolio")


def circuit_breaker(net: pd.Series, dd_limit: float) -> pd.Series:
    """Aplica o circuit breaker do plano: DD > limite -> zera até novo pico.

    Conservador: uma vez disparado, fica fora até a revisão (aqui modelada
    como retorno ao pico anterior da série bruta).
    """
    eq, out, peak, active = 1.0, [], 1.0, True
    raw_eq, raw_peak = 1.0, 1.0
    for r in net.fillna(0.0):
        raw_eq *= (1 + r)
        raw_peak = max(raw_peak, raw_eq)
        if active:
            eq *= (1 + r)
            peak = max(peak, eq)
            if 1 - eq / peak >= dd_limit:
                active = False
        else:
            if raw_eq >= raw_peak:  # sistema bruto recuperou o pico -> religar
                active, peak = True, eq
        out.append(eq)
    eq_ser = pd.Series(out, index=net.index)
    return eq_ser.pct_change().fillna(eq_ser.iloc[0] - 1)


# --------------------------- walk-forward + gates ---------------------------

def yearly_split(net: pd.Series) -> dict[int, pd.Series]:
    return {y: g for y, g in net.groupby(net.index.year) if len(g) > 50}


def gate_report(net: pd.Series, trades: pd.DataFrame | None, cfg: Config,
                bars_per_year: float) -> dict:
    """Avalia os critérios pré-registrados do Plano §4 Fase 1. NÃO EDITAR
    critérios após ver resultados — mudanças exigem novo pré-registro."""
    g = cfg.gates
    years = yearly_split(net)
    per_year = {y: metrics(s, bars_per_year) for y, s in years.items()}
    n_pass = sum(1 for m in per_year.values() if m["sharpe"] >= g.min_sharpe_oos)

    overall = metrics(net, bars_per_year)
    q = net.groupby([net.index.year, net.index.quarter]).sum()
    total = q.sum()
    max_q_share = float((q.max() / total)) if total > 0 else 1.0

    checks = {
        f"sharpe>= {g.min_sharpe_oos} em >= {g.min_years_pass} anos": n_pass >= min(g.min_years_pass, len(per_year)),
        f"max_dd <= {g.max_drawdown:.0%}": overall["max_dd"] <= g.max_drawdown,
        f"nenhum trimestre > {g.max_single_quarter_share:.0%} do retorno": (total <= 0) or (max_q_share <= g.max_single_quarter_share),
    }
    if trades is not None:
        tm = trade_metrics(trades, cfg.costs.round_trip)
        checks[f"edge/custo >= {g.min_edge_cost_ratio}x"] = tm["edge_cost_ratio"] >= g.min_edge_cost_ratio
    verdict = all(checks.values())
    return {"aprovado": verdict, "checks": checks, "overall": overall,
            "por_ano": per_year, "anos_aprovados": n_pass,
            "trades": trade_metrics(trades, cfg.costs.round_trip) if trades is not None else None}
