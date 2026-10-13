"""Arquivo 7 — alinhamento entre força local e movimento da barra.

Reescrita de ``sgv_force_alignment_90_refactored.py``. A medida continua
sendo o cosseno entre a força média da célula e o movimento (ΔE, Δjerk) da
barra, dividido pela magnitude média da célula. Itens 7.1–7.8.

Modo novo: o mapa é causal (um por bloco, só com barras anteriores ao bloco),
então a própria barra nunca entra na média que a avalia. Modo legado: usa o
mapa global do arquivo 6 (ou o recebido em ``force_df``).
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from .common.binning import legacy_nearest_index_vec
from .common.blocks import causal_or_global_blocks, min_periods_for
from .common.stats import quantile_threshold
from .common.validity import add_meta, assign_columns
from .config import DEFAULT_CONFIG, SGVConfig
from .force_field import ForceMap, build_map, compute_forces

log = logging.getLogger("sgv.force_alignment")


def robust_stats(x, prefix: str) -> dict:
    vals = pd.to_numeric(pd.Series(x), errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    if len(vals) == 0:
        return {f"{prefix}_{k}": (0 if k == "count" else np.nan)
                for k in ("count", "mean", "median", "std", "p05", "p25", "p75", "p95")}
    return {
        f"{prefix}_count": len(vals), f"{prefix}_mean": float(np.mean(vals)),
        f"{prefix}_median": float(np.median(vals)), f"{prefix}_std": float(np.std(vals)),
        f"{prefix}_p05": float(np.quantile(vals, 0.05)), f"{prefix}_p25": float(np.quantile(vals, 0.25)),
        f"{prefix}_p75": float(np.quantile(vals, 0.75)), f"{prefix}_p95": float(np.quantile(vals, 0.95)),
    }


def prepare_terrain_dataframe(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c = cfg.alignment
    missing = [col for col in (c.E_COL, c.J_COL) if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando no terrain: {missing}")
    out = df.copy()
    out[c.E_COL] = pd.to_numeric(out[c.E_COL], errors="coerce")
    out[c.J_COL] = pd.to_numeric(out[c.J_COL], errors="coerce")
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=[c.E_COL, c.J_COL]).reset_index(drop=True)
    if len(out) < 10:
        raise ValueError("Poucos dados válidos no terrain.")
    return out


def _legacy_map_from_frame(force_df: pd.DataFrame) -> dict:
    """Mapa no formato do CSV original (pivot jerk × E)."""
    req = ["E", "jerk", "force_x", "force_y", "force_magnitude"]
    missing = [col for col in req if col not in force_df.columns]
    if missing:
        raise ValueError(f"Colunas faltando no force map: {missing}")
    f = force_df.copy()
    for col in req:
        f[col] = pd.to_numeric(f[col], errors="coerce")
    f = f.replace([np.inf, -np.inf], np.nan).dropna(subset=req).reset_index(drop=True)
    if f.empty:
        raise ValueError("Force map vazio após limpeza.")
    piv = {k: f.pivot(index="jerk", columns="E", values=k).sort_index().sort_index(axis=1)
           for k in ("force_x", "force_y", "force_magnitude")}
    return {
        "fx": piv["force_x"].to_numpy(float), "fy": piv["force_y"].to_numpy(float),
        "fm": piv["force_magnitude"].to_numpy(float),
        "e_cols": piv["force_x"].columns.to_numpy(float), "j_rows": piv["force_x"].index.to_numpy(float),
        "n_obs": None,
    }


def _legacy_cos(dot, fm, dm, eps):
    """Comportamento original: max(-1, min(1, nan)) devolve 1,0 (7.1)."""
    denom = fm * dm
    with np.errstate(invalid="ignore", divide="ignore"):
        small = denom <= eps                  # NaN <= eps é False, como no original
        v = dot / denom
    clipped = np.where(np.isnan(v), 1.0, np.clip(v, -1.0, 1.0))
    return np.where(small, np.nan, clipped)


def _fixed_cos(dot, fm, dm, eps):
    denom = fm * dm
    with np.errstate(invalid="ignore", divide="ignore"):
        cos = np.where(denom > eps, dot / denom, np.nan)
    return np.clip(cos, -1.0, 1.0)


def _lookup_rows(fmap: ForceMap, pos_rows: np.ndarray, e, j, fx_row, fy_row, self_included: bool,
                 loo: bool) -> dict[str, np.ndarray]:
    """Força da célula para cada barra.

    ``pos_rows[k]`` é a linha cuja posição define a célula consultada e cuja
    força é o movimento pontuado: a própria barra no modo "arrival" e a barra
    anterior no modo "departure" (célula de x_{t-1}, movimento x_t - x_{t-1}).
    """
    n_rows = len(pos_rows)
    fx = np.full(n_rows, np.nan)
    fy = np.full(n_rows, np.nan)
    fm = np.full(n_rows, np.nan)
    n_obs = np.zeros(n_rows)
    have = pos_rows >= 0
    if not have.any():
        return {"fx": fx, "fy": fy, "fm": fm, "n_obs": n_obs}
    pr = pos_rows[have]
    fx_m, fy_m, fm_m = fmap.means()
    ie_h, ij_h = fmap.lookup_index(e[pr], j[pr])
    ie = np.full(n_rows, -1)
    ij = np.full(n_rows, -1)
    ie[have], ij[have] = ie_h, ij_h
    ok = ie >= 0
    fx[ok], fy[ok], fm[ok] = fx_m[ie[ok], ij[ok]], fy_m[ie[ok], ij[ok]], fm_m[ie[ok], ij[ok]]
    n_obs[ok] = fmap.count[ie[ok], ij[ok]]
    if self_included and loo:
        # 7.2: tira do mapa a contribuição do próprio movimento pontuado
        safe = np.where(have, pos_rows, 0)
        ae, aj, _ = fmap.agg_index(e[safe], j[safe])
        own_x = fx_row[safe] / fmap.scale_x
        own_y = fy_row[safe] / fmap.scale_y
        own_ok = ok & have & (ae == ie) & (aj == ij) & np.isfinite(own_x) & np.isfinite(own_y)
        idx = np.where(own_ok)[0]
        cnt = fmap.count[ie[idx], ij[idx]] - 1
        good = cnt >= fmap.min_cell_n
        sel = idx[good]
        ce, cj, cn = ie[sel], ij[sel], cnt[good]
        own_m = np.sqrt(own_x[sel] ** 2 + own_y[sel] ** 2)
        fx[sel] = (fmap.sum_x[ce, cj] - own_x[sel]) / cn
        fy[sel] = (fmap.sum_y[ce, cj] - own_y[sel]) / cn
        fm[sel] = (fmap.sum_m[ce, cj] - own_m) / cn
        bad = idx[~good]
        fx[bad] = fy[bad] = fm[bad] = np.nan
        n_obs[idx] = cnt
    return {"fx": fx, "fy": fy, "fm": fm, "n_obs": n_obs}


def build_force_alignment_90(
    terrain_df: pd.DataFrame,
    force_df: pd.DataFrame | None = None,
    cfg: SGVConfig = DEFAULT_CONFIG,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    c, L = cfg.alignment, cfg.legacy
    work = prepare_terrain_dataframe(terrain_df, cfg)
    n = len(work)
    e = work[c.E_COL].to_numpy(float)
    j = work[c.J_COL].to_numpy(float)

    # movimento retrospectivo (barra t: x_t - x_{t-1})
    dE = pd.Series(e).diff().to_numpy()
    dJ = pd.Series(j).diff().to_numpy()
    fx_row, fy_row = compute_forces(e, j, cfg.force_field.FORCE_MODE)

    fx = np.full(n, np.nan)
    fy = np.full(n, np.nan)
    fm = np.full(n, np.nan)
    n_obs = np.full(n, np.nan)
    sx_row = np.ones(n)
    sy_row = np.ones(n)

    departure = cfg.force_field.FORCE_MODE == "departure"
    # A tabela do arquivo 6 só reproduz o original quando as demais escolhas do
    # mapa também são as originais; em qualquer outra combinação o mapa global
    # é montado aqui, com as mesmas regras de unidade, binning e leave-one-out.
    use_csv = (L.LEGACY_GLOBAL_MAP and force_df is not None and L.LEGACY_UNSCALED_FORCE
               and L.LEGACY_BINNING and L.LEGACY_SELF_INCLUDED and not departure)
    if use_csv:
        # o CSV só guarda as células presentes: a consulta é sempre pelo valor mais próximo
        m = _legacy_map_from_frame(force_df)
        ie = legacy_nearest_index_vec(m["e_cols"], e)
        ij = legacy_nearest_index_vec(m["j_rows"], j)
        fx, fy, fm = m["fx"][ij, ie], m["fy"][ij, ie], m["fm"][ij, ie]
    else:
        if force_df is not None:
            log.info("Mapa recebido ignorado: montando o(s) mapa(s) aqui para respeitar as flags de força.")
        blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_MAP, kind="map")
        min_map = min_periods_for(cfg, L.LEGACY_GLOBAL_MAP, kind="map")
        for b in blocks:
            fit_stop = b.fit_stop
            if departure and b.fit_stop <= b.start:
                # a força de partida da linha start-1 é o movimento pontuado em t=start
                fit_stop = max(b.fit_start, b.fit_stop - 1)
            fit = np.arange(b.fit_start, fit_stop)
            fin = np.isfinite(fx_row[fit]) & np.isfinite(fy_row[fit])
            if fin.sum() < max(min_map, 2):
                continue
            fmap = build_map(e[fit], j[fit], fx_row[fit], fy_row[fit], cfg)
            rows = np.arange(b.start, b.stop)
            pos_rows = rows - 1 if departure else rows
            self_included = fit_stop > b.start             # só no mapa global
            r = _lookup_rows(fmap, pos_rows, e, j, fx_row, fy_row, self_included,
                             loo=not L.LEGACY_SELF_INCLUDED)
            fx[rows], fy[rows], fm[rows], n_obs[rows] = r["fx"], r["fy"], r["fm"], r["n_obs"]
            sx_row[rows], sy_row[rows] = fmap.scale_x, fmap.scale_y

    # 7.4: movimento nas mesmas unidades da força
    dEs, dJs = dE / sx_row, dJ / sy_row
    real_move_mag = np.sqrt(dEs ** 2 + dJs ** 2)
    dEs0, dJs0, dm0 = (np.nan_to_num(a, nan=0.0) for a in (dEs, dJs, real_move_mag))

    dot = fx * dEs0 + fy * dJs0
    cos_raw = _legacy_cos(dot, fm, dm0, c.EPS)
    cos = cos_raw if L.LEGACY_NAN_COS else _fixed_cos(dot, fm, dm0, c.EPS)

    q_blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_QUANTILES)
    q_min = min_periods_for(cfg, L.LEGACY_GLOBAL_QUANTILES)
    q_lo = quantile_threshold(fm, q_blocks, c.FORCE_Q_LOW, q_min)
    q_hi = quantile_threshold(fm, q_blocks, c.FORCE_Q_HIGH, q_min)
    with np.errstate(invalid="ignore"):
        inlier = ((fm >= q_lo) & (fm <= q_hi)).astype(int)
        valid = (np.isfinite(cos) & (dm0 > c.EPS)).astype(int)
    cos_live = np.where(inlier == 1, cos, 0.0)
    cos_live = np.nan_to_num(cos_live, nan=0.0)

    cols: dict[str, Any] = {
        "dE_real": dEs0, "dJ_real": dJs0, "real_move_mag": dm0,
        "force_x_local": fx, "force_y_local": fy, "force_mag_local": fm,
        "force_dot_move": dot,
        "force_alignment_cos": cos,
        "force_alignment_cos_raw": cos_raw,
        "force_mag_inlier": inlier,
        "force_alignment_valid": valid,
        "force_alignment_low_confidence": (inlier == 0).astype(int),
        "force_alignment_cos_live": cos_live,
        "aligned_positive": (cos_live > 0).astype(int),
        "aligned_strong": (cos_live > 0.25).astype(int),
        "aligned_very_strong": (cos_live > 0.50).astype(int),
        "anti_aligned": (cos_live < 0).astype(int),
        # novos
        "force_cell_empty": (~np.isfinite(fx)).astype(int),
        "force_cell_n_obs": n_obs,
        "force_scale_x": sx_row, "force_scale_y": sy_row,
    }
    out = assign_columns(work, cols)

    q_lo_s = float(np.nanmedian(q_lo)) if np.isfinite(q_lo).any() else np.nan
    q_hi_s = float(np.nanmedian(q_hi)) if np.isfinite(q_hi).any() else np.nan
    summary = {
        "rows_total": n,
        "rows_filtered": n,   # mantido por compatibilidade: sempre igual a rows_total
        "force_mag_q01": q_lo_s,
        "force_mag_q99": q_hi_s,
        "share_positive_alignment": float(np.mean(cols["aligned_positive"])) if n else np.nan,
        "share_strong_alignment": float(np.mean(cols["aligned_strong"])) if n else np.nan,
        "share_very_strong_alignment": float(np.mean(cols["aligned_very_strong"])) if n else np.nan,
        "share_anti_alignment": float(np.mean(cols["anti_aligned"])) if n else np.nan,
        "share_empty_cell": float(np.mean(cols["force_cell_empty"])) if n else np.nan,
        "share_self_dominated": float(np.mean(np.nan_to_num(n_obs, nan=0.0) <= 2)) if (n and not use_csv) else np.nan,
    }
    summary.update(robust_stats(cos_live, "cos"))
    summary.update(robust_stats(dot, "dot"))
    summary.update(robust_stats(fm, "force_mag"))
    summary.update(robust_stats(dm0, "move_mag"))
    summary_df = pd.DataFrame([summary])
    add_meta(out, "force_alignment_summary", {k: v for k, v in summary.items() if not isinstance(v, float) or np.isfinite(v)})
    return out, summary_df
