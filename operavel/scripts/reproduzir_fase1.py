#!/usr/bin/env python3
"""Reproduz os números congelados da Fase 1 com o pacote reconstruído e calcula
a faixa do portão G2.3 do pré-registro da Fase 2.

Referências (relatório da Fase 1, 06–07/08/2026):
  tendência-ETH 4h : +22,2%/ano, Sharpe 1,53, maxDD 17,5%, Sharpe>=0,8 em 6/7 anos
  portfólio 50/25/25 com circuit breaker: +17,0%/ano, Sharpe 2,32, maxDD 8,8%;
                     2025 +8,2%; 2026 (até jul) −0,3%
Tolerância de reprodução (fixada antes de rodar): retorno anual ±1,0 p.p.,
Sharpe ±0,10, maxDD ±1,0 p.p. — diferenças de fonte de dados (spot vs futuros,
fuso, meses re-baixados) podem explicar desvios pequenos e ficam registradas.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sgv_operavel.backtest import circuit_breaker, combine, gate_report, metrics  # noqa: E402
from sgv_operavel.config import DEFAULT as CFG  # noqa: E402
from sgv_operavel.data import load_ohlcv, resample  # noqa: E402
from sgv_operavel.features import BARS_PER_YEAR  # noqa: E402
from sgv_operavel.sleeves import carry, trend  # noqa: E402

REF = {"trend_eth": {"ret_anual": 0.222, "sharpe": 1.53, "max_dd": 0.175, "anos": 6},
       "portfolio": {"ret_anual": 0.170, "sharpe": 2.32, "max_dd": 0.088,
                     "ano_2025": 0.082, "ano_2026": -0.003}}
TOL = {"ret_anual": 0.010, "sharpe": 0.10, "max_dd": 0.010}


def klines(sym):
    files = sorted(glob.glob(str(ROOT / "data" / sym / "klines" / "*.csv")))
    df = pd.concat([load_ohlcv(f) for f in files]).sort_index()
    return df[~df.index.duplicated(keep="last")]


def funding(sym):
    files = sorted(glob.glob(str(ROOT / "data" / sym / "funding" / "*.csv")))
    tmp = ROOT / "data" / f"{sym}_funding_all.csv"
    fd = pd.concat([pd.read_csv(f) for f in files])
    fd = fd.sort_values("calc_time").drop_duplicates("calc_time")
    fd.to_csv(tmp, index=False)
    return carry.load_funding(tmp), len(files)


def ok(val, ref, key):
    return abs(val - ref) <= TOL[key]


def main():
    out = {"pacote": "sgv_operavel v1.0 + correções de 06/08 (reconstruído em 09/10/2026)"}
    eth = klines("ETHUSDT")
    out["dados"] = {"eth_1h_barras": len(eth), "inicio": str(eth.index[0]), "fim": str(eth.index[-1])}
    bt = trend.backtest(resample(eth, "4h"), CFG)
    g = gate_report(bt["net"], None, CFG, BARS_PER_YEAR["4h"])
    o = g["overall"]
    out["trend_eth"] = {"aprovado": g["aprovado"], "ret_anual": o["ret_anual"], "sharpe": o["sharpe"],
                        "max_dd": o["max_dd"], "anos_sharpe_0_8": g["anos_aprovados"],
                        "n_anos": len(g["por_ano"]),
                        "confere": all(ok(o[k], REF["trend_eth"][k], k) for k in TOL)}
    rets = {}
    for sym in ("BTCUSDT", "ETHUSDT"):
        f, nmeses = funding(sym)
        b = carry.backtest(f, CFG)
        gc = gate_report(b["net"], None, CFG, 365 * 24 / CFG.carry.funding_period_hours)
        rets[sym] = b["net"]
        out[f"carry_{sym}"] = {"aprovado": gc["aprovado"], "periodos": len(f), "meses": nmeses,
                               "ret_anual": gc["overall"]["ret_anual"], "sharpe": gc["overall"]["sharpe"],
                               "max_dd": gc["overall"]["max_dd"],
                               "tempo_em_posicao": float(b["in_pos"].mean())}
    port = combine({"trend_eth": bt["net"], "carry_btc": rets["BTCUSDT"], "carry_eth": rets["ETHUSDT"]},
                   {"trend_eth": 0.5, "carry_btc": 0.25, "carry_eth": 0.25})
    pcb = circuit_breaker(port, CFG.risk.circuit_breaker_dd)
    days = (port.index[-1] - port.index[0]).days
    ann = float((1 + pcb).prod()) ** (365.25 / days) - 1
    m = metrics(pcb, len(pcb) / (days / 365.25))
    por_ano = {int(y): float((1 + s).prod() - 1) for y, s in pcb.groupby(pcb.index.year)}
    out["portfolio"] = {"ret_anual": ann, "sharpe": m["sharpe"], "max_dd": m["max_dd"], "dias": days,
                        "por_ano": por_ano,
                        "confere": ok(ann, REF["portfolio"]["ret_anual"], "ret_anual")
                        and ok(m["sharpe"], REF["portfolio"]["sharpe"], "sharpe")
                        and ok(m["max_dd"], REF["portfolio"]["max_dd"], "max_dd")}

    # Faixa do G2.3: janelas móveis de 12 semanas (84 dias corridos) do portfólio
    daily = (1 + pcb).groupby(pcb.index.normalize()).prod() - 1
    daily = daily.asfreq("D", fill_value=0.0)
    w12 = (1 + daily).rolling(84).apply(np.prod, raw=True).dropna() - 1
    def band(s):
        return {"p5": float(s.quantile(0.05)), "p50": float(s.quantile(0.50)),
                "p95": float(s.quantile(0.95)), "n_janelas": int(len(s))}
    out["faixa_G2_3"] = {"regra": "6,6 anos inteiros (decide o portão)", **band(w12),
                         "descritivo_desde_2024": band(w12[w12.index >= "2024-01-01"])}
    out["reproducao_confere"] = bool(out["trend_eth"]["confere"] and out["portfolio"]["confere"])
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "fase1_reproducao.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
