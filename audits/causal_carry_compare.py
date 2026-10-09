#!/usr/bin/env python3
"""Auditoria causal do funding. Não modifica o SGV Operável original.

Premissa: funding_rate observado com timestamp de liquidação só fica conhecido
após esse pagamento. A posição que estava aberta ANTES do timestamp recebe
ou paga o funding dessa liquidação. A decisão com base na taxa observada muda
a posição apenas para a próxima liquidação.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from operavel.sgv_operavel.config import DEFAULT as CFG
from operavel.sgv_operavel.sleeves import carry


def causal_carry_backtest(funding: pd.Series, cfg=CFG) -> pd.DataFrame:
    """Modelo de fluxo de caixa pós-liquidação (não inclui basis/MTM/margem)."""
    funding = funding.sort_index()
    if funding.index.has_duplicates:
        raise ValueError("Funding tem timestamps duplicados; normalizar antes")
    in_position = False
    rows = []
    setup_cost = cfg.costs.round_trip * 2  # quatro pernas, ida+volta
    ann_factor = 365 * 24 / cfg.carry.funding_period_hours
    for ts, f in funding.items():
        f = float(f)
        before = in_position
        # Obrigação no settlement: paga/recebe se já estava posicionado.
        payment = f if before else 0.0
        annualized = f * ann_factor
        after = before
        if not before and annualized > cfg.carry.min_annualized:
            after = True
        elif before and annualized <= cfg.carry.exit_annualized:
            after = False
        cost = setup_cost / 2 if after != before else 0.0
        rows.append({"time": ts, "funding": f, "position_before": before,
                     "position_after": after, "cashflow_funding": payment,
                     "cost": cost, "net": payment - cost,
                     "event": "ENTER" if not before and after else
                              ("EXIT" if before and not after else "")})
        in_position = after
    return pd.DataFrame(rows).set_index("time")


def read_monthly_csv(directory: Path) -> pd.Series:
    paths = sorted(directory.glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"Sem CSVs de funding em {directory}")
    dfs = []
    for path in paths:
        df = pd.read_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]
        tcol = next((c for c in df if "time" in c or "date" in c), None)
        rcol = next((c for c in df if "rate" in c and "interval" not in c), None)
        if tcol is None or rcol is None:
            raise ValueError(f"Colunas não reconhecidas em {path}")
        raw = pd.to_numeric(df[tcol], errors="coerce")
        if raw.notna().all():
            stamps = pd.to_datetime(raw, unit="ms", utc=True)
        else:
            stamps = pd.to_datetime(df[tcol], utc=True)
        dfs.append(pd.DataFrame({"ts": stamps, "rate": pd.to_numeric(df[rcol], errors="coerce")}))
    merged = pd.concat(dfs, ignore_index=True).dropna(subset=["ts","rate"])
    merged = merged.sort_values("ts").drop_duplicates("ts", keep="last")
    return pd.Series(merged["rate"].to_numpy(float), index=pd.DatetimeIndex(merged["ts"]), name="funding")


def summarize(funding: pd.Series, legacy: pd.DataFrame, causal: pd.DataFrame) -> dict:
    if not legacy.index.equals(causal.index):
        raise ValueError("Calendários diferentes")
    exposure = causal["position_before"].to_numpy(bool)
    stopped = (causal["event"] == "EXIT").to_numpy(bool)
    omitted = float(funding.to_numpy()[stopped].sum())
    first = funding.index[0]
    last = funding.index[-1]
    duration = (last-first).total_seconds()/86400
    return {
        "status": "AUDITORIA_CASHFLOW_SEM_MTM_BASIS_MARGEM",
        "periodo": [str(first),str(last)], "dias":duration,"n_pagamentos":len(funding),
        "n_saidas":int(stopped.sum()),"fracao_exposta_antes":float(exposure.mean()),
        "soma_taxas_em_saida_ignoradas_no_legado":omitted,
        "net_legacy_soma":float(legacy["net"].sum()),
        "net_causal_soma":float(causal["net"].sum()),
        "legacy_menos_causal":float(legacy["net"].sum()-causal["net"].sum()),
        "net_legacy_composto":float(np.prod(1+legacy["net"].to_numpy())-1),
        "net_causal_composto":float(np.prod(1+causal["net"].to_numpy())-1),
        "observacao":"Fluxos por unidade nocional; NÃO simulam P&L spot/perp, basis, liquidação, capital imobilizado ou custos reais de hedge."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--funding-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, default=ROOT/"audits"/"carry_cashflow_auditoria.json")
    a = p.parse_args()
    funding = read_monthly_csv(a.funding_dir)
    legacy = carry.backtest(funding, CFG)
    causal = causal_carry_backtest(funding, CFG)
    report = summarize(funding, legacy, causal)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__ == "__main__":
    main()
