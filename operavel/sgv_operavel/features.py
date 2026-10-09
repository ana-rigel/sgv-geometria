"""Features consolidadas — apenas o que sobreviveu à auditoria de 08/2026.

O que entrou e por quê:
  * burst_event : sucessor observável do "vácuo" OIT. Engenharia reversa
    (06/08/2026) mostrou que OIT-baixo = vol curta/vol longa ALTA — o evento é
    uma ruptura de atividade, não uma secagem. Medido diretamente aqui.
  * cluster (T2)              : evento repetido — único amplificador com AUC OOS.
  * momentum                  : único sinal direcional que validou.
  * vol_regime                : filtro de regime (vol acima da mediana móvel).

O que ficou de fora e por quê: sigma, iit, psi, einstein e demais métricas
contínuas — AUC out-of-fold 0.517 nos 336 trades; correlações candle-level
nulas. Ver README §Auditoria.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import CollapseConfig


def burst_event(df: pd.DataFrame, cfg: CollapseConfig) -> pd.DataFrame:
    """Evento de RUPTURA DE ATIVIDADE — o núcleo observável do "vácuo" legado.

    Nota de consolidação (06/08/2026): engenharia reversa sobre o bar log 15m
    mostrou que OIT-baixo é reproduzido por vol_ratio ALTO (AUC 0.725) — o
    evento legado chamado de "vácuo" era, observacionalmente, um burst de
    volatilidade curta relativa. O detector direto é mais forte que o proxy:
    |fwd4| = 0.326%% vs 0.238%% (p=2e-11) contra 0.311%% vs 0.241%% do OIT.

    Devolve: vol_ratio, thr, event, event_start, cluster.
    """
    out = pd.DataFrame(index=df.index)
    ret = df["close"].pct_change()
    vol_s = ret.ewm(span=cfg.span_short, min_periods=cfg.span_short).std()
    vol_l = ret.ewm(span=cfg.span_long, min_periods=cfg.span_long).std()
    out["vol_ratio"] = vol_s / vol_l
    out["thr"] = out["vol_ratio"].rolling(cfg.quantile_window, min_periods=cfg.quantile_window // 2).quantile(cfg.quantile)
    out["event"] = out["vol_ratio"] > out["thr"]
    out["event_start"] = out["event"] & ~out["event"].shift(1, fill_value=False)
    # T2 = barra de evento com outro evento nas `cluster_bars` anteriores
    # (semântica do Doc v5 §5.2: "segundo vácuo no cluster" — inclui a
    # confirmação dentro do próprio run). t2_start = primeira barra T2 do
    # cluster: é o gatilho de entrada da Sleeve B.
    prev_ev = out["event"].shift(1, fill_value=False)
    had_recent = prev_ev.rolling(cfg.cluster_bars, min_periods=1).max().astype(bool)
    out["t2"] = out["event"] & had_recent
    out["t2_start"] = out["t2"] & ~out["t2"].shift(1, fill_value=False)
    out["cluster"] = out["t2_start"]  # alias usado pela sleeve
    return out


def momentum_sign(df: pd.DataFrame, bars: int) -> pd.Series:
    """Direção = sinal do retorno acumulado em `bars` barras."""
    return np.sign(df["close"].pct_change(bars)).fillna(0.0).rename("mom_sign")


def vol_regime(df: pd.DataFrame, span: int = 96, med_window: int = 2000) -> pd.Series:
    """Regime de volatilidade: True quando vol EWMA > mediana móvel longa.

    Origem: Doc v5 §3.3 — o edge do colapso vive em regimes com energia.
    """
    ret = df["close"].pct_change()
    vol = ret.ewm(span=span, min_periods=span).std()
    med = vol.rolling(med_window, min_periods=med_window // 4).median()
    return (vol > med).rename("vol_regime")


def realized_vol_annual(close: pd.Series, span: int, bars_per_year: float) -> pd.Series:
    """Volatilidade anualizada (para vol targeting da Sleeve A)."""
    return close.pct_change().ewm(span=span, min_periods=span).std() * np.sqrt(bars_per_year)


BARS_PER_YEAR = {"15min": 35040.0, "1h": 8760.0, "4h": 2190.0, "1d": 365.0}
