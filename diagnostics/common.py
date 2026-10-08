"""Infraestrutura comum dos diagnósticos.

Fonte de dados:
  - padrão: série sintética GARCH-t tipo BTC 1m (semente fixa) — calibração;
  - real:   defina SGV_DATA com um ou mais caminhos (.zip/.csv de klines da Binance,
            separados por ':'), por exemplo
            SGV_DATA=data/BTCUSDT-1m-2026-08.zip python diagnostics/run_all.py

Regra: nenhum diagnóstico olha retorno futuro. Os dados reais continuam virgens
para o teste confirmatório.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sgvgeo.data import load_binance_klines, synthetic_btc_1m  # noqa: E402

REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)


def dataset(n: int = 6000, seed: int = 0) -> tuple[pd.DataFrame, str]:
    src = os.environ.get("SGV_DATA")
    if src:
        df = load_binance_klines(src.split(":"))
        tail = int(os.environ.get("SGV_TAIL", n))
        return df.tail(tail).reset_index(drop=True), f"real:{src} (últimas {tail} barras)"
    return synthetic_btc_1m(n, seed=seed), f"sintético GARCH(1,1)-t(4), n={n}, semente={seed}"


def tag() -> str:
    return "real" if os.environ.get("SGV_DATA") else "sintetico"


def out_path(name: str) -> Path:
    d = REPORTS / tag()
    d.mkdir(parents=True, exist_ok=True)
    return d / name


def save_json(name: str, obj: dict) -> None:
    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        return str(o)
    out_path(name).write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=conv))


class Timer:
    def __enter__(self):
        self.t = time.time()
        return self

    def __exit__(self, *a):
        self.dt = time.time() - self.t


def slog(x):
    """log com sinal: sign(x)·log1p|x| (a compressão que o legado usa)."""
    x = np.asarray(x, float)
    return np.sign(x) * np.log1p(np.abs(x))
