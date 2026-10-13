"""Arquivo 9 — sinal de edge = EV × cosseno de alinhamento.

Reescrita de ``sgv_edge_signal_90_refactored.py``. Produto, direção pelo
sinal do produto e filtros 0,25/0,50 mantidos. Itens 9.1–9.6.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .common.validity import add_meta, assign_columns
from .config import DEFAULT_CONFIG, SGVConfig

log = logging.getLogger("sgv.edge")


def _num(s) -> np.ndarray:
    return pd.to_numeric(pd.Series(s), errors="coerce").replace([np.inf, -np.inf], np.nan).to_numpy(float)


def merge_inputs(alignment_df: pd.DataFrame, ev_df: pd.DataFrame | None, cfg: SGVConfig) -> tuple[pd.DataFrame, dict]:
    """9.1 — junção explícita 1:1 por timestamp, com relatório de cobertura."""
    on = cfg.edge.JOIN_ON
    if ev_df is None:
        return alignment_df.copy(), {"merged": False}
    for name, d in (("alinhamento", alignment_df), ("EV", ev_df)):
        if on not in d.columns:
            raise ValueError(f"Entrada de {name} sem a coluna de junção '{on}'.")
        if d[on].duplicated().any():
            raise ValueError(f"Entrada de {name} tem '{on}' duplicado; a junção precisa ser 1:1.")
    a = alignment_df.copy()
    b = ev_df.copy()
    a[on] = pd.to_datetime(a[on], utc=True, errors="coerce")
    b[on] = pd.to_datetime(b[on], utc=True, errors="coerce")
    ev_cols = [col for col in ("expected_value_score", "ev_valid", "prob_long", "prob_short",
                               "ev_long_1", "ev_short_1") if col in b.columns]
    if "expected_value_score" not in ev_cols:
        raise ValueError("Entrada de EV sem 'expected_value_score'.")
    a = a.drop(columns=[col for col in ev_cols if col in a.columns])
    merged = a.merge(b[[on] + ev_cols], on=on, how="left", validate="one_to_one", indicator="_join")
    matched = (merged["_join"] == "both").to_numpy()
    merged = merged.drop(columns="_join")
    report = {
        "merged": True,
        "rows_alignment": int(len(a)), "rows_ev": int(len(b)),
        "rows_matched": int(matched.sum()),
        "coverage": float(matched.mean()) if len(merged) else 0.0,
        "rows_with_valid_ev": int(merged["expected_value_score"].notna().sum()),
    }
    if report["coverage"] < 0.95:
        log.warning("Cobertura da junção alinhamento × EV: %.1f%%", 100 * report["coverage"])
    return merged, report


def build_edge_signal_90(
    alignment_df: pd.DataFrame,
    ev_df: pd.DataFrame | None = None,
    cfg: SGVConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    c, L = cfg.edge, cfg.legacy
    df, report = merge_inputs(alignment_df, ev_df, cfg)
    df = df.replace([np.inf, -np.inf], np.nan)
    align_col = c.ALIGNMENT_COL
    missing = [col for col in ("expected_value_score", align_col) if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando: {missing}")

    ev = _num(df["expected_value_score"])
    align = _num(df[align_col])
    raw_score = ev * align
    inputs_ok = np.isfinite(ev) & np.isfinite(align)
    if "ev_valid" in df.columns and not L.LEGACY_EDGE_FILL:
        inputs_ok &= _num(df["ev_valid"]) > 0

    if L.LEGACY_EDGE_FILL:
        edge_score = np.nan_to_num(raw_score, nan=0.0)
        direction = np.select([edge_score > 0, edge_score < 0], ["LONG", "SHORT"], default="NEUTRAL")
    else:
        edge_score = np.where(inputs_ok, raw_score, np.nan)
        direction = np.select(
            [~inputs_ok, edge_score > 0, edge_score < 0],
            ["NO_EDGE", "LONG", "SHORT"], default="NEUTRAL",
        )

    with np.errstate(invalid="ignore"):
        ev_pos = ev > c.EV_THRESHOLD
        cols = {
            "expected_value_score": ev,
            align_col: align,
            "edge_score": edge_score,
            "edge_valid_long": (ev_pos & (align > c.ALIGNMENT_STRONG)).astype(int),
            "edge_valid_short": (ev_pos & (align < -c.ALIGNMENT_STRONG)).astype(int),
            "edge_strong_long": (ev_pos & (align > c.ALIGNMENT_VERY_STRONG)).astype(int),
            "edge_strong_short": (ev_pos & (align < -c.ALIGNMENT_VERY_STRONG)).astype(int),
            "edge_direction": direction,
        }
    # 9.5: de onde vem o sinal do produto
    src = np.full(len(df), "", dtype=object)
    ok = np.isfinite(ev) & np.isfinite(align)
    src[ok] = np.char.add(np.where(ev[ok] >= 0, "ev+", "ev-").astype(str),
                          np.where(align[ok] >= 0, "cos+", "cos-").astype(str))
    cols["edge_sign_source"] = src
    out = assign_columns(df, cols)

    if L.LEGACY_ZERO_FILL:
        num = out.select_dtypes(include=[np.number]).columns
        out[num] = out[num].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    add_meta(out, "edge_merge", report)
    add_meta(out, "edge_direction_shares",
             pd.Series(direction).value_counts(normalize=True).round(4).to_dict())
    return out
