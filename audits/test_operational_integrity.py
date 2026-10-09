"""Testes sintéticos de regressão da auditoria SGV (sem dados financeiros reservados)."""
import numpy as np
import pandas as pd

from audits.causal_carry_compare import causal_carry_backtest
from audits.operational_controls import risk_sized_returns, strict_annual_gate
from operavel.sgv_operavel.config import DEFAULT as CFG
from operavel.sgv_operavel.sleeves import carry, collapse
from operavel.sgv_operavel.backtest import gate_report


def test_funding_pago_antes_da_decisao_de_saida():
    dates = pd.date_range("2024-01-01", periods=3, freq="8h", tz="UTC")
    f = pd.Series([0.001, -0.0002, 0.001], index=dates)
    old = carry.backtest(f, CFG)
    fixed = causal_carry_backtest(f, CFG)
    assert bool(fixed.loc[dates[1], "position_before"])
    assert fixed.loc[dates[1], "event"] == "EXIT"
    assert np.isclose(fixed.loc[dates[1], "cashflow_funding"], -0.0002)
    assert np.isclose(old["net"].sum() - fixed["net"].sum(), 0.0002)


def test_funding_sem_conhecimento_do_proximo_periodo():
    dates = pd.date_range("2024-01-01", periods=4, freq="8h", tz="UTC")
    a = pd.Series([0.0002, 0.0003, -0.0002, 0.0001], index=dates)
    b = a.copy()
    b.iloc[3] = -0.02
    ca = causal_carry_backtest(a)
    cb = causal_carry_backtest(b)
    assert np.array_equal(ca["net"].iloc[:3].to_numpy(), cb["net"].iloc[:3].to_numpy())


def test_legado_ignora_risk_frac_e_referencia_respeita():
    dates = pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC")
    trades = pd.DataFrame({"exit_time":[dates[2]], "net":[0.01]})
    # Defeito comprovado no legado: a entrada risk_frac não altera a saída.
    legacy_small = collapse.returns_series(trades, dates, risk_frac=0.001)
    legacy_big = collapse.returns_series(trades, dates, risk_frac=0.005)
    assert legacy_small.equals(legacy_big)
    fixed_small = risk_sized_returns(trades, dates, 0.001, 0.012)
    fixed_big = risk_sized_returns(trades, dates, 0.005, 0.012)
    assert np.isclose(fixed_big.sum(), 5 * fixed_small.sum())


def test_gate_antigo_aprova_dois_anos_mas_minimo_quatro_nao():
    idx = pd.date_range("2020-01-01", "2021-12-31", freq="D", tz="UTC")
    returns = pd.Series(0.001 + 0.0002 * (np.arange(len(idx))%2), index=idx)
    # Com o min(4,len(per_year)) do legado, o gate antigo aceita só dois anos.
    old = gate_report(returns, None, CFG, bars_per_year=365)
    assert old["aprovado"] is True
    strict = strict_annual_gate(returns, bars_per_year=365, min_years=4)
    assert strict["anos_completos"] == 2
    assert strict["aprovado"] is False


def test_gate_quatro_anos_incluindo_ano_parcial():
    idx = pd.date_range("2020-01-01", "2023-07-01", freq="D", tz="UTC")
    returns = pd.Series(0.001 + 0.0002 * (np.arange(len(idx))%2), index=idx)
    stricter = strict_annual_gate(returns, bars_per_year=365, min_years=4)
    assert stricter["anos_completos"] == 3
    assert stricter["aprovado"] is False
