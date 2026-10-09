"""Carga e validação de dados OHLCV.

Fontes aceitas:
  1. CSVs de klines da Binance (Binance Vision / API), com ou sem cabeçalho.
  2. Qualquer CSV com colunas: timestamp/open/high/low/close/volume.

Toda série é validada (monotônica, sem duplicatas, gaps reportados) antes de
entrar no pipeline. Reamostragem sempre a partir do menor timeframe disponível.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

BINANCE_KLINE_COLS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "n_trades",
    "taker_buy_base", "taker_buy_quote", "ignore",
]

REQUIRED = ["open", "high", "low", "close", "volume"]


def load_ohlcv(path: str | Path) -> pd.DataFrame:
    """Lê um CSV de OHLCV e devolve DataFrame indexado por datetime UTC."""
    path = Path(path)
    head = pd.read_csv(path, nrows=1, header=None)
    has_header = not str(head.iloc[0, 0]).replace(".", "").replace("-", "").isdigit()

    if has_header:
        df = pd.read_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]
        tcol = next((c for c in ("timestamp", "open_time", "bar_time", "datetime", "date", "time") if c in df.columns), None)
        if tcol is None:
            raise ValueError(f"{path.name}: nenhuma coluna de tempo reconhecida")
    else:
        df = pd.read_csv(path, header=None)
        df = df.iloc[:, : len(BINANCE_KLINE_COLS)]
        df.columns = BINANCE_KLINE_COLS[: df.shape[1]]
        tcol = "open_time"

    ts = pd.to_numeric(df[tcol], errors="coerce")
    if ts.notna().all():  # epoch ms ou us (Binance usa ms; dumps 2025+ usam us)
        unit = "us" if ts.iloc[0] > 1e14 else "ms"
        idx = pd.to_datetime(ts, unit=unit, utc=True)
    else:
        idx = pd.to_datetime(df[tcol], utc=True, errors="coerce")

    out = df[[c for c in REQUIRED if c in df.columns]].apply(pd.to_numeric, errors="coerce")
    missing = [c for c in REQUIRED if c not in out.columns]
    if missing:
        raise ValueError(f"{path.name}: colunas ausentes {missing}")
    out.index = idx
    out = out[~out.index.isna()].sort_index()
    out = out[~out.index.duplicated(keep="last")].dropna(subset=["close"])
    return out


def load_dir(directory: str | Path, pattern: str = "*.csv") -> pd.DataFrame:
    """Concatena todos os CSVs de um diretório (ex.: dumps mensais da Binance Vision)."""
    files = sorted(Path(directory).glob(pattern))
    if not files:
        raise FileNotFoundError(f"nenhum CSV em {directory}")
    df = pd.concat([load_ohlcv(f) for f in files]).sort_index()
    return df[~df.index.duplicated(keep="last")]


def resample(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Reamostra OHLCV para o timeframe pedido ('15min','1h','4h','1d')."""
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    out = df.resample(timeframe, label="left", closed="left").agg(agg)
    return out.dropna(subset=["close"])


def integrity_report(df: pd.DataFrame, timeframe: str) -> dict:
    """Relatório de integridade — roda antes de qualquer backtest (Fase 0 gate)."""
    step = pd.Timedelta(timeframe)
    gaps = (df.index.to_series().diff().dropna() > step).sum()
    return {
        "inicio": str(df.index[0]),
        "fim": str(df.index[-1]),
        "barras": len(df),
        "anos": round((df.index[-1] - df.index[0]).days / 365.25, 2),
        "gaps": int(gaps),
        "nan_close": int(df["close"].isna().sum()),
    }
