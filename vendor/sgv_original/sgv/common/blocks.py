"""Blocos causais (C2, C5).

A série é dividida em blocos de ``REFIT_EVERY`` barras, ancorados na primeira
linha. Cada bloco é avaliado com parâmetros (KDE, escala, quantis) estimados
somente nas barras ``[start - window, start - 1]``. Como os blocos dependem só
da posição absoluta da linha, o resultado de uma linha não muda quando novas
linhas são acrescentadas no fim (invariância de prefixo).

No modo legado ("global") existe um único bloco cujo ajuste usa todas as
linhas, o que reproduz o comportamento dos scripts originais.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True)
class Block:
    start: int        # primeira linha avaliada
    stop: int         # uma depois da última linha avaliada
    fit_start: int    # primeira linha usada no ajuste
    fit_stop: int     # uma depois da última linha usada no ajuste

    @property
    def size(self) -> int:
        return self.stop - self.start


def make_blocks(n: int, refit_every: int, window: int, global_mode: bool) -> list[Block]:
    if n <= 0:
        return []
    if global_mode:
        return [Block(0, n, 0, n)]
    refit_every = max(1, int(refit_every))
    blocks: list[Block] = []
    for start in range(0, n, refit_every):
        stop = min(n, start + refit_every)
        blocks.append(Block(start, stop, max(0, start - int(window)), start))
    return blocks


def block_of_rows(blocks: Sequence[Block], n: int) -> np.ndarray:
    """Índice do bloco de cada linha."""
    out = np.empty(n, dtype=int)
    for bi, b in enumerate(blocks):
        out[b.start:b.stop] = bi
    return out


def block_reduce(
    values: np.ndarray,
    blocks: Sequence[Block],
    fn: Callable[[np.ndarray], float | Sequence[float]],
    min_periods: int,
    n_out: int = 1,
) -> np.ndarray:
    """Aplica ``fn`` à janela de ajuste de cada bloco e expande por linha.

    Valores não finitos da janela são descartados antes de ``fn``. Blocos com
    menos de ``min_periods`` valores finitos recebem NaN.
    """
    values = np.asarray(values, dtype=float)
    n = len(values)
    out = np.full((n, n_out), np.nan, dtype=float)
    for b in blocks:
        w = values[b.fit_start:b.fit_stop]
        w = w[np.isfinite(w)]
        if len(w) < max(1, int(min_periods)):
            continue
        res = np.atleast_1d(np.asarray(fn(w), dtype=float))
        out[b.start:b.stop, :] = res[None, :n_out]
    return out[:, 0] if n_out == 1 else out


def quantile_blocks(blocks: Sequence[Block], window: int, min_periods: int) -> list[Block]:
    """Mesmos blocos, com janela de ajuste trocada para a janela de quantis."""
    out = []
    for b in blocks:
        if b.fit_stop == b.stop and b.fit_start == 0 and b.start == 0:
            out.append(b)  # bloco global (legado)
        else:
            out.append(Block(b.start, b.stop, max(0, b.start - int(window)), b.start))
    return out


def causal_or_global_blocks(n: int, cfg, legacy_global: bool, kind: str = "quantile") -> list[Block]:
    """Atalho: blocos para quantis/z (``kind='quantile'``), KDE (``'fit'``) ou mapa (``'map'``)."""
    c = cfg.causal
    if kind == "fit":
        window = c.W_FIT
    elif kind == "map":
        window = c.W_MAP
    else:
        window = c.W_QUANTILE
    return make_blocks(n, c.REFIT_EVERY, window, legacy_global)


def min_periods_for(cfg, legacy_global: bool, kind: str = "quantile") -> int:
    if legacy_global:
        return 1
    c = cfg.causal
    return {"fit": c.MIN_FIT, "map": c.MIN_MAP}.get(kind, c.MIN_QUANTILE)
