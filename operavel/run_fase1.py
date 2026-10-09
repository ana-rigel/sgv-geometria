#!/usr/bin/env python3
"""Fase 1 — backtest multi-regime das três sleeves + gates pré-registrados.

Uso:
    python run_fase1.py --klines caminho/klines_1m_ou_15m/  [--funding funding.csv]

Aceita um CSV único ou um diretório de dumps mensais da Binance Vision.
Reporta integridade dos dados, resultado por sleeve, gates e portfólio.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from sgv_operavel.backtest import circuit_breaker, combine, gate_report, metrics, trade_metrics
from sgv_operavel.config import DEFAULT as CFG
from sgv_operavel.data import integrity_report, load_dir, load_ohlcv, resample
from sgv_operavel.features import BARS_PER_YEAR
from sgv_operavel.sleeves import carry, collapse, trend

WEIGHTS = {"trend": 0.50, "collapse": 0.30, "carry": 0.20}  # Plano §3


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--klines", required=True, help="CSV ou diretório de klines (menor TF disponível)")
    ap.add_argument("--funding", default=None, help="CSV de funding rates (opcional)")
    ap.add_argument("--out", default="fase1_report.json")
    args = ap.parse_args()

    p = Path(args.klines)
    base = load_dir(p) if p.is_dir() else load_ohlcv(p)
    print("== Integridade (base) ==")
    print(json.dumps(integrity_report(base, "15min"), indent=2, ensure_ascii=False))

    tf_b = CFG.collapse.timeframe
    tf_a = CFG.trend.timeframe
    df_b = resample(base, tf_b)
    df_a = resample(base, tf_a)

    # ---- Sleeve B: colapso ----
    tr_b = collapse.backtest(df_b, CFG)
    ret_b = collapse.returns_series(tr_b, df_b.index, CFG.risk.risk_per_trade)
    print("\n== Sleeve B (colapso", tf_b, ") ==")
    print(trade_metrics(tr_b, CFG.costs.round_trip))
    gate_b = gate_report(ret_b, tr_b, CFG, BARS_PER_YEAR[tf_b])

    # ---- Sleeve A: tendência ----
    bt_a = trend.backtest(df_a, CFG)
    ret_a = bt_a["net"]
    print("\n== Sleeve A (tendência", tf_a, ") ==")
    print(metrics(ret_a, BARS_PER_YEAR[tf_a]))
    gate_a = gate_report(ret_a, None, CFG, BARS_PER_YEAR[tf_a])

    # ---- Sleeve C: carry ----
    gate_c, ret_c = None, None
    if args.funding:
        f = carry.load_funding(args.funding)
        bt_c = carry.backtest(f, CFG)
        ret_c = bt_c["net"]
        print("\n== Sleeve C (carry) ==")
        print(metrics(ret_c, 365 * 24 / CFG.carry.funding_period_hours))
        gate_c = gate_report(ret_c, None, CFG, 365 * 24 / CFG.carry.funding_period_hours)
    else:
        print("\n== Sleeve C: INATIVA (sem série de funding) ==")

    # ---- Portfólio ----
    sleeves = {"trend": ret_a, "collapse": ret_b}
    if ret_c is not None:
        sleeves["carry"] = ret_c
    port = combine(sleeves, WEIGHTS)
    port_cb = circuit_breaker(port, CFG.risk.circuit_breaker_dd)
    print("\n== Portfólio (com circuit breaker) ==")
    # aproximação: usa a maior frequência presente
    print(metrics(port_cb, BARS_PER_YEAR[tf_b]))

    report = {
        "gates": {"trend": gate_a, "collapse": gate_b, "carry": gate_c},
        "portfolio": metrics(port_cb, BARS_PER_YEAR[tf_b]),
        "config_hash": str(CFG),
    }
    Path(args.out).write_text(json.dumps(report, indent=2, default=str, ensure_ascii=False))
    print(f"\nRelatório salvo em {args.out}")
    for name, g in report["gates"].items():
        if g:
            print(f"GATE {name}: {'APROVADO' if g['aprovado'] else 'REPROVADO'} — {g['checks']}")


if __name__ == "__main__":
    main()
