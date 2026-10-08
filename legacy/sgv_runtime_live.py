from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

from build_btc_90d_input_sgv_refactored import build_btc_90d_input_sgv
from sgv_build_information_field_geometry_90d_refactored import (
    build_information_field_geometry_90d,
)
from sgv_geodesic_field_full3d_90d_refactored import (
    build_geodesic_field_full3d_90d,
)
from sgv_build_singularity_detector_90d_refactored import (
    build_singularity_detector_90d,
)
from sgv_build_terrain_layer_90d_refactored import build_terrain_layer_90d
from sgv_build_expected_value_90d_refactored import build_expected_value_90d
from sgv_build_force_field_90d_refactored import build_force_field_90d
from sgv_force_alignment_90_refactored import build_force_alignment_90
from sgv_edge_signal_90_refactored import build_edge_signal_90

LIVE_TAIL_WINDOW = 220
TIMESTAMP_CANDIDATES = ["timestamp", "datetime", "date", "time"]
GEOMETRIC_EXPORT_COLS = [
    "sgv_singularity_score", "sgv_criticality_score", "criticality_regime", "is_high_critical",
    "is_extreme_critical", "field_stress_geodesic", "field_gravity", "field_curvature",
    "field_curvature_scalar", "rupture_prob_geodesic", "geodesic_valid", "geom_incoherence",
    "geom_incoherence_abs", "geo_resid_norm", "acc_geo_norm", "jerk_over_lambda", "memory_flux",
    "field_einstein_norm", "field_stress_tensor_norm", "gravitational_stress_score",
    "sgv_singularity_prob", "sgv_criticality_prob", "sgv_singularity_type", "sgv_stage",
    "sgv_singularity_valid",
]
FINAL_REQUIRED_COLS = ["close", "force_alignment_cos", "terrain_state"]
EDGE_SIGNAL_COL = "sgv_edge_signal"
EDGE_BUCKET_COL = "sgv_edge_bucket"
RUNTIME_TS_DEBUG = False


def _debug_print(msg: str) -> None:
    if RUNTIME_TS_DEBUG:
        print(msg)


def _copy_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()


def _find_timestamp_col(df: pd.DataFrame) -> str | None:
    for col in TIMESTAMP_CANDIDATES:
        if col in df.columns:
            return col
    return None


def _prepare_runtime_input(df_raw: pd.DataFrame) -> pd.DataFrame:
    if df_raw is None or df_raw.empty:
        raise ValueError("df_raw vazio ou ausente.")

    df = _copy_df(df_raw)
    ts_col = _find_timestamp_col(df)
    if ts_col is None:
        raise ValueError(f"Nenhuma coluna temporal encontrada. Esperado: {TIMESTAMP_CANDIDATES}")

    if ts_col == "timestamp":
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    else:
        df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce", utc=True)
        df = df.dropna(subset=[ts_col]).sort_values(ts_col)

    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    if ts_col == "timestamp":
        df = df.drop_duplicates(subset=["timestamp"], keep="last")
    else:
        df = df.drop_duplicates(subset=[ts_col], keep="last")

    df = df.tail(LIVE_TAIL_WINDOW).reset_index(drop=True)
    if df.empty:
        raise ValueError("Entrada vazia após preparação.")
    return df


def _ensure_timestamp_from_index(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ts_col = _find_timestamp_col(out)
    if ts_col is not None:
        return out

    idx = out.index
    if isinstance(idx, pd.DatetimeIndex):
        out["datetime"] = pd.to_datetime(idx, errors="coerce", utc=True)
        return out

    if isinstance(idx, pd.MultiIndex):
        for level_name in idx.names:
            if level_name in TIMESTAMP_CANDIDATES:
                out[level_name] = idx.get_level_values(level_name)
                return out
    return out


def _build_merge_timestamp(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError(f"{df_name} vazio ao preparar chave temporal de merge.")

    out = _ensure_timestamp_from_index(df.copy())
    ts_col = _find_timestamp_col(out)
    if ts_col is None:
        raise ValueError(f"{df_name} sem coluna temporal.")

    raw_ts = out[ts_col]
    if is_datetime64_any_dtype(raw_ts):
        ts_dt = pd.to_datetime(raw_ts, errors="coerce", utc=True)
    else:
        raw_num = pd.to_numeric(raw_ts, errors="coerce")
        ts_dt_num = pd.to_datetime(pd.Series([np.nan] * len(raw_ts)), errors="coerce", utc=True)
        if raw_num.notna().any():
            sample = raw_num.dropna()
            median_abs = sample.abs().median()
            if median_abs >= 1e17:
                unit = "ns"
            elif median_abs >= 1e14:
                unit = "us"
            elif median_abs >= 1e11:
                unit = "ms"
            else:
                unit = "s"
            ts_dt_num = pd.to_datetime(raw_num, unit=unit, errors="coerce", utc=True)

        ts_dt_obj = pd.to_datetime(raw_ts, errors="coerce", utc=True)
        num_valid = int(ts_dt_num.notna().sum())
        obj_valid = int(ts_dt_obj.notna().sum())
        if num_valid > obj_valid:
            ts_dt = ts_dt_num
        elif obj_valid > num_valid:
            ts_dt = ts_dt_obj
        else:
            num_max = ts_dt_num.dropna().max() if num_valid > 0 else pd.NaT
            obj_max = ts_dt_obj.dropna().max() if obj_valid > 0 else pd.NaT
            if pd.isna(num_max):
                ts_dt = ts_dt_obj
            elif pd.isna(obj_max):
                ts_dt = ts_dt_num
            else:
                ts_dt = ts_dt_num if num_max >= obj_max else ts_dt_obj

    out["__merge_ts__"] = ts_dt.dt.floor("1min")
    out = out.dropna(subset=["__merge_ts__"])
    out = out.sort_values("__merge_ts__").drop_duplicates(subset=["__merge_ts__"], keep="last").reset_index(drop=True)
    if out.empty:
        raise ValueError(f"{df_name} ficou vazio após normalização da chave temporal.")
    return out


def _to_datetime_for_debug(series: pd.Series) -> pd.Series:
    """
    Conversão tolerante para diagnóstico temporal (sem lançar exceções).
    """
    try:
        if is_datetime64_any_dtype(series):
            return pd.to_datetime(series, errors="coerce", utc=True)
        num = pd.to_numeric(series, errors="coerce")
        ts_num = pd.to_datetime(pd.Series([np.nan] * len(series)), errors="coerce", utc=True)
        if num.notna().any():
            sample = num.dropna()
            median_abs = sample.abs().median()
            if median_abs >= 1e17:
                unit = "ns"
            elif median_abs >= 1e14:
                unit = "us"
            elif median_abs >= 1e11:
                unit = "ms"
            else:
                unit = "s"
            ts_num = pd.to_datetime(num, unit=unit, errors="coerce", utc=True)
        ts_obj = pd.to_datetime(series, errors="coerce", utc=True)
        if ts_num.notna().sum() >= ts_obj.notna().sum():
            return ts_num
        return ts_obj
    except Exception:
        return pd.to_datetime(pd.Series([np.nan] * len(series)), errors="coerce", utc=True)


def _debug_temporal_df(df_name: str, df: pd.DataFrame | None, prefix: str = "[DEBUG TS]") -> None:
    """
    Diagnóstico temporal seguro para investigação de compatibilidade entre branches.
    """
    if not RUNTIME_TS_DEBUG:
        return
    try:
        if df is None:
            _debug_print(f"{prefix} {df_name} | df=None")
            return
        if df.empty:
            ts_cols = [c for c in ["__merge_ts__", *TIMESTAMP_CANDIDATES] if c in df.columns]
            _debug_print(f"{prefix} {df_name} | rows=0 | ts_cols={ts_cols} | ts_source=none(empty)")
            return

        ts_cols = [c for c in ["__merge_ts__", *TIMESTAMP_CANDIDATES] if c in df.columns]
        ts_source = "none"
        ts_series = None

        if "__merge_ts__" in df.columns:
            ts_source = "__merge_ts__"
            ts_series = _to_datetime_for_debug(df["__merge_ts__"])
        elif "timestamp" in df.columns:
            ts_source = "timestamp"
            ts_series = _to_datetime_for_debug(df["timestamp"])
        elif "datetime" in df.columns:
            ts_source = "datetime"
            ts_series = _to_datetime_for_debug(df["datetime"])
        elif isinstance(df.index, pd.DatetimeIndex):
            ts_source = "index"
            ts_series = pd.to_datetime(pd.Series(df.index), errors="coerce", utc=True)

        if ts_series is None:
            _debug_print(
                f"{prefix} {df_name} | rows={len(df)} | ts_cols={ts_cols} | "
                f"ts_source=none | note=sem_coluna_temporal"
            )
            return

        valid_ts = ts_series.dropna()
        nulls = int(ts_series.isna().sum())
        if valid_ts.empty:
            _debug_print(
                f"{prefix} {df_name} | rows={len(df)} | ts_cols={ts_cols} | ts_source={ts_source} | "
                f"first=None | last=None | tail5=[] | nulls={nulls}"
            )
            return

        tail5 = [str(x) for x in valid_ts.tail(5).tolist()]
        _debug_print(
            f"{prefix} {df_name} | rows={len(df)} | ts_cols={ts_cols} | ts_source={ts_source} | "
            f"first={valid_ts.iloc[0]} | last={valid_ts.iloc[-1]} | tail5={tail5} | nulls={nulls}"
        )
    except Exception as exc:
        _debug_print(f"{prefix} {df_name} | erro_diagnostico={repr(exc)}")


def merge_runtime_branches(df_trader: pd.DataFrame, df_geom: pd.DataFrame, geom_cols: Iterable[str] = GEOMETRIC_EXPORT_COLS) -> pd.DataFrame:
    if df_trader is None or df_trader.empty:
        raise ValueError("df_trader vazio no merge.")
    if df_geom is None or df_geom.empty:
        return df_trader.copy()

    trader = _build_merge_timestamp(df_trader, "df_trader")
    _debug_temporal_df("merge.trader.normalized", trader, prefix="[MERGE DEBUG]")
    geom = _build_merge_timestamp(df_geom, "df_geom")
    _debug_temporal_df("merge.geom.normalized", geom, prefix="[MERGE DEBUG]")

    available_geom_cols = [c for c in geom_cols if c in geom.columns]
    geom_merge = geom[["__merge_ts__", *available_geom_cols]].copy()

    trader_valid = int(trader["__merge_ts__"].notna().sum())
    geom_valid = int(geom_merge["__merge_ts__"].notna().sum())
    trader_last = trader["__merge_ts__"].dropna().max() if trader_valid > 0 else None
    geom_last = geom_merge["__merge_ts__"].dropna().max() if geom_valid > 0 else None
    shared_ts_count = len(set(trader["__merge_ts__"]).intersection(set(geom_merge["__merge_ts__"])))
    _debug_print(
        f"[MERGE DEBUG] shared_timestamps={shared_ts_count} | trader_valid={trader_valid} | "
        f"geom_valid={geom_valid} | trader_last={trader_last} | geom_last={geom_last}"
    )
    if shared_ts_count == 0:
        _debug_temporal_df("merge.df_trader.raw", df_trader, prefix="[MERGE DEBUG]")
        _debug_temporal_df("merge.df_geom.raw", df_geom, prefix="[MERGE DEBUG]")
        _debug_temporal_df("merge.df_trader.normalized", trader, prefix="[MERGE DEBUG]")
        _debug_temporal_df("merge.df_geom.normalized", geom, prefix="[MERGE DEBUG]")
        raise ValueError("Sem timestamps comuns entre branch trader e branch geométrico.")

    # Tolerância dinâmica: usa janela mínima de 30s, mas não menor que ~2 barras
    # do branch trader (quando possível), para evitar "drop" silencioso do geom.
    merge_tol = pd.Timedelta("30s")
    try:
        valid_trader_ts = trader["__merge_ts__"].dropna().sort_values()
        if len(valid_trader_ts) >= 3:
            dt = valid_trader_ts.diff().dropna().median()
            if pd.notna(dt) and dt > pd.Timedelta(0):
                merge_tol = max(pd.Timedelta("30s"), min(pd.Timedelta("5min"), dt * 2))
    except Exception:
        pass

    out = pd.merge_asof(
        trader.sort_values("__merge_ts__"),
        geom_merge.sort_values("__merge_ts__"),
        on="__merge_ts__",
        direction="nearest",
        tolerance=merge_tol,
        suffixes=("", "_geom"),
    )

    # Prioriza valores geométricos quando houver sobreposição de nomes.
    # Sem isso, uma coluna "pré-existente" no trader (ex.: defaults 0.0)
    # pode mascarar a coluna calculada no branch geom.
    for col in available_geom_cols:
        geom_col = f"{col}_geom"
        if geom_col not in out.columns:
            continue
        if col not in out.columns:
            out[col] = out[geom_col]
        else:
            geom_vals = pd.to_numeric(out[geom_col], errors="coerce")
            base_vals = pd.to_numeric(out[col], errors="coerce")
            out[col] = geom_vals.where(geom_vals.notna(), base_vals)
        out = out.drop(columns=[geom_col], errors="ignore")

    out = out.drop(columns=["__merge_ts__"], errors="ignore")
    return out


def _inject_missing_base_cols(target_df: pd.DataFrame, source_df: pd.DataFrame, force_cols: list[str] | None = None) -> pd.DataFrame:
    """
    PATCH CRÍTICO:
    - Primeiro tenta alinhamento temporal por merge timestamp
    - Se não der, usa alinhamento por cauda (tail), nunca por cabeça (head)
    """
    if target_df is None or target_df.empty:
        return target_df
    if source_df is None or source_df.empty:
        return target_df

    force_cols = force_cols or []
    out = target_df.copy().reset_index(drop=True)
    src = source_df.copy().reset_index(drop=True)

    try:
        out_ts = _build_merge_timestamp(out, "inject_out")
        src_ts = _build_merge_timestamp(src, "inject_src")
        merged = pd.merge_asof(
            out_ts.sort_values("__merge_ts__"),
            src_ts.sort_values("__merge_ts__"),
            on="__merge_ts__",
            direction="nearest",
            suffixes=("", "_src"),
        )
        for col in src.columns:
            src_col = f"{col}_src"
            if src_col not in merged.columns:
                continue
            if col not in merged.columns:
                merged[col] = merged[src_col].values
                continue
            if col in force_cols:
                src_vals = merged[src_col]
                merged[col] = src_vals.where(src_vals.notna(), merged[col])
        merged = merged.drop(columns=[c for c in merged.columns if c.endswith("_src")], errors="ignore")
        merged = merged.drop(columns=["__merge_ts__"], errors="ignore")
        return merged.reset_index(drop=True)
    except Exception:
        pass

    if len(out) == 0:
        return out
    if len(src) == 0:
        return out

    out = out.copy().reset_index(drop=True)
    src = src.copy().reset_index(drop=True)
    out_len = len(out)
    src_len = len(src)

    for col in src.columns:
        if col not in out.columns or col in force_cols:
            s = src[col].reset_index(drop=True)
            if src_len >= out_len:
                vals = s.iloc[-out_len:].to_numpy()
            else:
                padded = pd.Series([np.nan] * out_len)
                padded.iloc[-src_len:] = s.to_numpy()
                padded = padded.ffill().bfill()
                vals = padded.to_numpy()
            out[col] = vals
    return out


def _normalize_edge_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if EDGE_SIGNAL_COL not in out.columns:
        if "edge_direction" in out.columns:
            direction = out["edge_direction"].astype(str).str.upper()
            out[EDGE_SIGNAL_COL] = np.where(direction.eq("LONG"), 1, np.where(direction.eq("SHORT"), -1, 0))
        elif "edge_score" in out.columns:
            score = pd.to_numeric(out["edge_score"], errors="coerce").fillna(0.0)
            out[EDGE_SIGNAL_COL] = np.where(score > 0, 1, np.where(score < 0, -1, 0))
        else:
            out[EDGE_SIGNAL_COL] = 0

    if EDGE_BUCKET_COL not in out.columns:
        edge_signal = pd.to_numeric(out[EDGE_SIGNAL_COL], errors="coerce").fillna(0).astype(int)
        out[EDGE_BUCKET_COL] = np.where(edge_signal.ne(0), "ACTIVE", "NEUTRAL")
    return out


def _reanchor_edge_to_base(
    df_edge: pd.DataFrame,
    df_edge_base: pd.DataFrame,
    force_time_cols: list[str],
) -> pd.DataFrame:
    """
    Reprojeta colunas de edge sobre a base temporal do edge_base sem perder cardinalidade.
    """
    if df_edge is None or df_edge.empty:
        return df_edge
    if df_edge_base is None or df_edge_base.empty:
        return df_edge
    if len(df_edge) >= len(df_edge_base):
        return df_edge
    _debug_print(
        f"[RUNTIME DEBUG] edge_reanchor triggered | edge_rows={len(df_edge)} | "
        f"edge_base_rows={len(df_edge_base)}"
    )
    anchored = _inject_missing_base_cols(df_edge_base.copy(), df_edge, force_cols=force_time_cols)
    return _normalize_edge_columns(anchored)


def _build_trader_fallback(
    df_terrain: pd.DataFrame,
    df_expected_value: pd.DataFrame | None = None,
    df_input: pd.DataFrame | None = None,
    force_time_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Fallback resiliente para live runtime quando blocos do trader branch
    não têm dados suficientes (ex.: force field com janela curta).
    """
    base = df_terrain.copy().reset_index(drop=True)
    if base.empty:
        raise ValueError("Trader fallback recebeu terrain vazio.")

    if df_expected_value is not None and not df_expected_value.empty:
        ev = df_expected_value.copy().reset_index(drop=True)
        for col in ev.columns:
            if col in base.columns:
                continue
            if len(ev) >= len(base):
                base[col] = ev[col].iloc[-len(base):].to_numpy()
            else:
                fill_vals = pd.Series([np.nan] * len(base))
                fill_vals.iloc[-len(ev):] = ev[col].to_numpy()
                base[col] = fill_vals.ffill().bfill().to_numpy()

    if "force_alignment_cos" not in base.columns:
        base["force_alignment_cos"] = 0.0
    else:
        base["force_alignment_cos"] = pd.to_numeric(base["force_alignment_cos"], errors="coerce").fillna(0.0)

    if "terrain_state" not in base.columns:
        base["terrain_state"] = "UNKNOWN"
    else:
        terrain = base["terrain_state"].astype(str).str.strip()
        base["terrain_state"] = terrain.where(terrain.ne(""), "UNKNOWN")

    if EDGE_SIGNAL_COL not in base.columns:
        base[EDGE_SIGNAL_COL] = 0
    if EDGE_BUCKET_COL not in base.columns:
        base[EDGE_BUCKET_COL] = "NEUTRAL"

    out = _normalize_edge_columns(base)
    if df_input is not None and not df_input.empty:
        out = _inject_missing_base_cols(out, df_input, force_cols=(force_time_cols or []))
    return out


def validate_runtime_output(df_final: pd.DataFrame) -> pd.DataFrame:
    if df_final is None or df_final.empty:
        raise ValueError("Saída final do runtime vazia.")
    missing = [c for c in FINAL_REQUIRED_COLS if c not in df_final.columns]
    if missing:
        raise ValueError(f"Saída final sem colunas essenciais: {missing}")

    out = df_final.copy()
    numeric_cols = out.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return out


def run_geom_branch(df_input: pd.DataFrame) -> pd.DataFrame:
    df_information = build_information_field_geometry_90d(df_input)
    df_geodesic = build_geodesic_field_full3d_90d(df_information)
    df_singularity = build_singularity_detector_90d(df_geodesic)
    force_time_cols = [c for c in TIMESTAMP_CANDIDATES if c in df_input.columns]
    return _inject_missing_base_cols(df_singularity, df_input, force_cols=force_time_cols)


def run_trader_branch(df_input: pd.DataFrame) -> pd.DataFrame:
    df_terrain = build_terrain_layer_90d(df_input)
    _debug_temporal_df("trader_edge.df_terrain.raw", df_terrain, prefix="[TRADER EDGE DEBUG]")
    force_time_cols = [c for c in TIMESTAMP_CANDIDATES if c in df_input.columns]
    df_terrain = _inject_missing_base_cols(df_terrain, df_input, force_cols=force_time_cols)
    _debug_temporal_df("trader_edge.df_terrain.injected", df_terrain, prefix="[TRADER EDGE DEBUG]")

    df_expected_value = build_expected_value_90d(df_terrain)
    _debug_temporal_df("trader_edge.df_expected_value.raw", df_expected_value, prefix="[TRADER EDGE DEBUG]")
    try:
        df_force_map = build_force_field_90d(df_terrain)
        _debug_temporal_df("trader_edge.df_force_map.raw", df_force_map, prefix="[TRADER EDGE DEBUG]")
        df_alignment, _ = build_force_alignment_90(df_terrain, df_force_map)
        _debug_temporal_df("trader_edge.df_alignment.raw", df_alignment, prefix="[TRADER EDGE DEBUG]")
    except ValueError as exc:
        if "Dados insuficientes para force field" not in str(exc):
            raise
        fallback = _build_trader_fallback(
            df_terrain,
            df_expected_value=df_expected_value,
            df_input=df_input,
            force_time_cols=force_time_cols,
        )
        _debug_temporal_df("trader_edge.final.fallback", fallback, prefix="[TRADER EDGE DEBUG]")
        return fallback

    df_alignment = _inject_missing_base_cols(df_alignment, df_terrain, force_cols=force_time_cols)
    _debug_temporal_df("trader_edge.df_alignment.injected", df_alignment, prefix="[TRADER EDGE DEBUG]")
    df_expected_value = _inject_missing_base_cols(df_expected_value, df_terrain, force_cols=force_time_cols)
    _debug_temporal_df("trader_edge.df_expected_value.injected", df_expected_value, prefix="[TRADER EDGE DEBUG]")

    if df_alignment is None or df_alignment.empty:
        raise ValueError("Sem linhas suficientes no alignment.")

    df_edge_base = _inject_missing_base_cols(df_alignment, df_expected_value, force_cols=force_time_cols)
    _debug_temporal_df("trader_edge.df_edge_base", df_edge_base, prefix="[TRADER EDGE DEBUG]")

    df_edge = build_edge_signal_90(df_edge_base)
    _debug_temporal_df("trader_edge.df_edge.raw", df_edge, prefix="[TRADER EDGE DEBUG]")
    df_edge = _reanchor_edge_to_base(df_edge, df_edge_base, force_time_cols)
    _debug_temporal_df("trader_edge.df_edge.reanchored", df_edge, prefix="[TRADER EDGE DEBUG]")
    df_edge = _inject_missing_base_cols(df_edge, df_edge_base, force_cols=force_time_cols)
    _debug_temporal_df("trader_edge.df_edge.injected", df_edge, prefix="[TRADER EDGE DEBUG]")
    df_edge = _normalize_edge_columns(df_edge)
    _debug_temporal_df("trader_edge.df_edge.normalized", df_edge, prefix="[TRADER EDGE DEBUG]")
    final_trader = _inject_missing_base_cols(df_edge, df_input, force_cols=force_time_cols)
    _debug_temporal_df("trader_edge.final", final_trader, prefix="[TRADER EDGE DEBUG]")
    return final_trader


def run_sgv_runtime(df_raw: pd.DataFrame) -> pd.DataFrame:
    raw = _prepare_runtime_input(df_raw)
    _debug_temporal_df("runtime_edge.raw", raw, prefix="[RUNTIME EDGE DEBUG]")
    df_input = build_btc_90d_input_sgv(raw)
    _debug_temporal_df("runtime_edge.df_input", df_input, prefix="[RUNTIME EDGE DEBUG]")
    if df_input is None or df_input.empty:
        raise ValueError("Input físico retornou DataFrame vazio.")

    df_geom = run_geom_branch(df_input)
    _debug_temporal_df("runtime_edge.df_geom", df_geom, prefix="[RUNTIME EDGE DEBUG]")
    df_trader = run_trader_branch(df_input)
    _debug_temporal_df("runtime_edge.df_trader", df_trader, prefix="[RUNTIME EDGE DEBUG]")
    df_final = merge_runtime_branches(df_trader, df_geom, GEOMETRIC_EXPORT_COLS)
    _debug_temporal_df("runtime_edge.df_final_pre_validate", df_final, prefix="[RUNTIME EDGE DEBUG]")

    if "sgv_stage" in df_final.columns:
        if "criticality_regime" not in df_final.columns:
            df_final["criticality_regime"] = df_final["sgv_stage"]
        else:
            crit_reg = df_final["criticality_regime"]
            mask_missing = crit_reg.isna() | crit_reg.astype(str).str.strip().eq("")
            df_final.loc[mask_missing, "criticality_regime"] = df_final.loc[mask_missing, "sgv_stage"]

    if "is_high_critical" not in df_final.columns and "sgv_criticality_score" in df_final.columns:
        crit = pd.to_numeric(df_final["sgv_criticality_score"], errors="coerce")
        df_final["is_high_critical"] = crit >= 0.70

    if "is_extreme_critical" not in df_final.columns and "sgv_criticality_score" in df_final.columns:
        crit = pd.to_numeric(df_final["sgv_criticality_score"], errors="coerce")
        df_final["is_extreme_critical"] = crit >= 0.90

    df_final = _normalize_edge_columns(df_final)
    _debug_temporal_df("runtime_edge.df_final_post_normalize", df_final, prefix="[RUNTIME EDGE DEBUG]")
    return validate_runtime_output(df_final)
