"""C7 — validade, preenchimento final, validação de input e metadados."""
from __future__ import annotations

import json
import logging
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .. import __version__

log = logging.getLogger("sgv")


# ----------------------------------------------------------------- metadados
def meta(df: pd.DataFrame) -> dict:
    """Dicionário de metadados acumulados no DataFrame (vai para o .meta.json)."""
    m = df.attrs.get("sgv_meta")
    if m is None:
        m = {}
        df.attrs["sgv_meta"] = m
    return m


def add_meta(df: pd.DataFrame, key: str, value: Any) -> None:
    meta(df)[key] = value


def add_clip_count(df: pd.DataFrame, column: str, count: int) -> None:
    clips = meta(df).setdefault("clip_counts", {})
    clips[column] = int(clips.get(column, 0)) + int(count)


# ----------------------------------------------------------------- montagem
def assign_columns(df: pd.DataFrame, cols: dict[str, Any]) -> pd.DataFrame:
    """Insere várias colunas de uma vez (sem fragmentar o DataFrame).

    Colunas já existentes são substituídas no lugar, mantendo a ordem.
    """
    attrs = dict(df.attrs)
    existing = {k: v for k, v in cols.items() if k in df.columns}
    new = {k: v for k, v in cols.items() if k not in df.columns}
    out = df
    if existing:
        out = out.copy()
        for k, v in existing.items():
            out[k] = v
    if new:
        new_df = pd.DataFrame(new, index=df.index)
        out = pd.concat([out, new_df], axis=1)
    out.attrs.update(attrs)
    return out


# ------------------------------------------------------------- preenchimento
def finalize_for_live(df: pd.DataFrame, columns: Iterable[str] | None = None) -> pd.DataFrame:
    """Único ponto em que NaN vira 0 (C7). Conta e registra no log."""
    out = df.copy()
    cols = list(columns) if columns is not None else out.select_dtypes(include=[np.number]).columns.tolist()
    total = 0
    per_col = {}
    for c in cols:
        if c not in out.columns:
            continue
        s = pd.to_numeric(out[c], errors="coerce").replace([np.inf, -np.inf], np.nan)
        k = int(s.isna().sum())
        if k:
            per_col[c] = k
            total += k
        out[c] = s.fillna(0.0)
    if total:
        log.info("finalize_for_live: %d células preenchidas com 0 em %d colunas", total, len(per_col))
    add_meta(out, "zero_filled_cells", per_col)
    return out


def legacy_fill_zero(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    """Reproduz o zero-fill embutido dos scripts originais."""
    out = df
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out


# ------------------------------------------------------------- validação
def validate_time_index(df: pd.DataFrame, ts_col: str = "timestamp", bar_seconds: int = 60,
                        dedupe: bool = True, sort: bool = True) -> pd.DataFrame:
    """Confere a ordem e as duplicatas de timestamp e marca buracos em ``bar_gap``.

    Com ``sort``/``dedupe`` desligados só marca (``dup_timestamp``) e avisa,
    sem reordenar nem remover linhas: é o que os scripts que não ordenavam no
    original (terreno, geodésica) usam, para não mudar as linhas de saída.
    """
    if ts_col not in df.columns:
        return df
    out = df.copy()
    ts = out[ts_col]
    if not pd.api.types.is_datetime64_any_dtype(ts):
        ts_num = pd.to_numeric(ts, errors="coerce")
        if ts_num.notna().mean() > 0.8:
            sample = ts_num.dropna()
            med = sample.abs().median() if len(sample) else 0
            unit = "ns" if med >= 1e17 else "us" if med >= 1e14 else "ms" if med >= 1e11 else "s"
            ts = pd.to_datetime(ts_num, unit=unit, errors="coerce", utc=True)
        else:
            ts = pd.to_datetime(ts, errors="coerce", utc=True)
    else:
        ts = pd.to_datetime(ts, errors="coerce", utc=True)
    out[ts_col] = ts
    n0 = len(out)
    monotonic = bool(out[ts_col].is_monotonic_increasing)
    if not monotonic:
        if sort:
            out = out.sort_values(ts_col, kind="mergesort")
        else:
            log.warning("validate_time_index: timestamps fora de ordem (linhas mantidas como vieram)")
    dup = out[ts_col].duplicated(keep="last")
    if dup.any():
        if dedupe:
            log.warning("validate_time_index: %d timestamps duplicados removidos", int(dup.sum()))
            out = out[~dup]
        else:
            log.warning("validate_time_index: %d timestamps duplicados (mantidos)", int(dup.sum()))
    out = out.reset_index(drop=True)
    gaps = out[ts_col].diff().dt.total_seconds()
    out["bar_gap"] = (gaps > bar_seconds * 1.5).astype(int)
    out["dup_timestamp"] = out[ts_col].duplicated(keep=False).astype(int)
    add_meta(out, "rows_in", n0)
    add_meta(out, "bar_gaps", int(out["bar_gap"].sum()))
    add_meta(out, "timestamps_monotonic", monotonic)
    add_meta(out, "dup_timestamps", int(out["dup_timestamp"].sum()))
    return out


# ------------------------------------------------------------- escrita
def write_outputs(df: pd.DataFrame, path: str | Path, cfg, extra: dict | None = None,
                  ts_col: str = "timestamp") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    m = dict(meta(df))
    if extra:
        m.update(extra)
    info: dict[str, Any] = {
        "sgv_version": __version__,
        "written_at": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "config_hash": cfg.config_hash(),
        "legacy_flags_on": [k for k, v in cfg.to_dict()["legacy"].items() if v],
        "rows": int(len(df)),
        "nan_counts": {c: int(v) for c, v in df.isna().sum().items() if int(v) > 0},
    }
    if ts_col in df.columns and len(df):
        ts = pd.to_datetime(df[ts_col], errors="coerce", utc=True)
        info["date_range"] = [str(ts.min()), str(ts.max())]
    info.update(m)
    meta_path = path.with_name(path.name + ".meta.json")
    meta_path.write_text(json.dumps(info, indent=2, default=_json_default), encoding="utf-8")
    return path


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)
