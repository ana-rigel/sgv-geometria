"""Arquivo 2 — campo informacional 2D com métrica, incoerência e stress.

Versão canônica de ``sgv_build_information_field_refactored_cache.py``.
Também fornece :func:`compute_field_2d`, reutilizado pela camada geodésica
(item 3.1), e o runtime com cache incremental (item 2.7).

Itens implementados: 2.1–2.9 (ver especificação).
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .common import legacy_grid as lg
from .common.blocks import Block, block_of_rows, causal_or_global_blocks, min_periods_for
from .common.geometry import christoffel_hessian, fd_christoffel, project_psd, safe_inv
from .common.kde import kde_eval
from .common.numeric import ema, safe_ratio, sigmoid
from .common.scaling import RobustScale, scaler_for
from .common.validity import add_clip_count, add_meta, assign_columns, legacy_fill_zero, validate_time_index
from .config import DEFAULT_CONFIG, SGVConfig

log = logging.getLogger("sgv.information_field")


# =====================================================================
# Campo 2D compartilhado
# =====================================================================
@dataclass
class Field2DParams:
    bandwidth: float
    grid_n: int
    q_low: float
    q_high: float
    eps: float
    metric_reg: float
    det_floor: float = 1e-9
    clip_gamma: float = 1e6


def _metric_2x2_det_inv(g: np.ndarray, det_floor: float):
    """det, det_safe e inversa 2×2 exatamente como no script original."""
    g_ee, g_ej, g_jj = g[..., 0, 0], g[..., 0, 1], g[..., 1, 1]
    det = g_ee * g_jj - g_ej ** 2
    det_safe = det.copy()
    small = np.abs(det_safe) < det_floor
    det_safe[small] = np.where(det_safe[small] >= 0.0, det_floor, -det_floor)
    inv = np.empty_like(g)
    inv[..., 0, 0] = g_jj / det_safe
    inv[..., 0, 1] = -g_ej / det_safe
    inv[..., 1, 0] = inv[..., 0, 1]
    inv[..., 1, 1] = g_ee / det_safe
    return det, det_safe, inv


def compute_field_2d(
    e: np.ndarray,
    j: np.ndarray,
    cfg: SGVConfig,
    params: Field2DParams,
    *,
    need_geodesic: bool,
    start_row: int = 0,
) -> dict[str, np.ndarray]:
    """φ, ∇φ, Hessiana, métrica (e Christoffels) em cada linha.

    Coordenadas padronizadas por bloco (C1), KDE causal (C2), derivadas
    analíticas (C3) e métrica PSD (C4), cada uma com sua flag legada.
    Linhas com índice < ``start_row`` não são calculadas (cache incremental).
    """
    L = cfg.legacy
    n = len(e)
    X = np.column_stack([np.asarray(e, float), np.asarray(j, float)])
    blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_KDE, kind="fit")
    min_fit = min_periods_for(cfg, L.LEGACY_GLOBAL_KDE, kind="fit")

    keys = ["rho", "phi", "grad_e", "grad_j", "grad_norm", "h_ee", "h_ej", "h_jj",
            "g_ee", "g_ej", "g_jj", "g_min_eig", "g_indefinite", "geom_exact",
            "med_e", "med_j", "s_e", "s_j", "fit_valid"]
    if need_geodesic:
        keys += ["g_trace", "g_det", "g_det_safe", "g_inv_ee", "g_inv_ej", "g_inv_jj",
                 "dE_g_ee", "dJ_g_ee", "dE_g_ej", "dJ_g_ej", "dE_g_jj", "dJ_g_jj",
                 "gamma_e_ee", "gamma_e_ej", "gamma_e_jj", "gamma_j_ee", "gamma_j_ej", "gamma_j_jj",
                 "gamma_clipped"]
    out = {k: np.full(n, np.nan) for k in keys}
    out["fit_valid"] = np.zeros(n)
    out["gamma_clipped"] = np.zeros(n) if need_geodesic else None
    clip_total = 0

    for b in blocks:
        if b.stop <= start_row:
            continue
        ev = np.arange(max(b.start, start_row), b.stop)
        fit = X[b.fit_start:b.fit_stop]
        fit = fit[np.isfinite(fit).all(axis=1)]
        if len(fit) < max(min_fit, 3):
            continue
        sc = scaler_for(fit, L.LEGACY_UNSCALED_KDE)
        fit_s = sc.transform(fit)
        pts_s = sc.transform(X[ev])
        out["med_e"][ev], out["med_j"][ev] = sc.med[0], sc.med[1]
        out["s_e"][ev], out["s_j"][ev] = sc.scale[0], sc.scale[1]

        if L.LEGACY_GRID_DERIVATIVES:
            res = _field_2d_grid(fit_s, pts_s, cfg, params, need_geodesic)
        else:
            res = _field_2d_analytic(fit_s, pts_s, cfg, params, need_geodesic)
        for k, v in res.items():
            if k == "clip_count":
                clip_total += int(v)
                continue
            out[k][ev] = v
        out["fit_valid"][ev] = np.isfinite(res["phi"]).astype(float)

    out["clip_total"] = clip_total
    return out


def _field_2d_analytic(fit_s, pts_s, cfg: SGVConfig, p: Field2DParams, need_geodesic: bool) -> dict:
    L = cfg.legacy
    order = 3 if need_geodesic else 2
    r = kde_eval(pts_s, fit_s, p.bandwidth, order=order, chunk=None)
    H = r.hess_phi
    g_raw = H + p.metric_reg * np.eye(2)[None]
    min_eig = np.linalg.eigvalsh(np.where(np.isfinite(g_raw), g_raw, 0.0)).min(axis=1)
    min_eig = np.where(np.isfinite(g_raw).all(axis=(1, 2)), min_eig, np.nan)
    if L.LEGACY_RAW_METRIC:
        g = g_raw
        changed = np.zeros(len(g), dtype=bool)
    else:
        g, changed, _ = project_psd(g_raw, cfg.numeric.PSD_FLOOR)

    res = {
        "rho": np.exp(r.log_rho),
        "phi": r.phi,
        "grad_e": r.grad_phi[:, 0],
        "grad_j": r.grad_phi[:, 1],
        "grad_norm": np.sqrt(r.grad_phi[:, 0] ** 2 + r.grad_phi[:, 1] ** 2),
        "h_ee": H[:, 0, 0], "h_ej": H[:, 0, 1], "h_jj": H[:, 1, 1],
        "g_ee": g[:, 0, 0], "g_ej": g[:, 0, 1], "g_jj": g[:, 1, 1],
        "g_min_eig": min_eig,
        "g_indefinite": (min_eig < 0).astype(float),
        "geom_exact": (~changed).astype(float),
    }
    if not need_geodesic:
        return res

    det, det_safe, g_inv = _metric_2x2_det_inv(g, p.det_floor)
    phi3 = r.phi3
    gamma = christoffel_hessian(g_inv, phi3)      # exato onde g é a Hessiana
    dg = phi3.copy()                              # ∂_m g_ij = φ_mij
    fb = changed & np.isfinite(g).all(axis=(1, 2))
    if fb.any() and cfg.numeric.PSD_FALLBACK == "fd":
        floor, reg, h = cfg.numeric.PSD_FLOOR, p.metric_reg, p.bandwidth

        def metric_fn(Y):
            Hy = kde_eval(Y, fit_s, h, order=2).hess_phi + reg * np.eye(2)[None]
            return project_psd(Hy, floor)[0]

        gam_fd, dg_fd, _ = fd_christoffel(metric_fn, pts_s[fb], cfg.numeric.FD_DELTA)
        gamma[fb] = gam_fd
        dg[fb] = dg_fd
    raw_gamma = gamma
    gamma = np.clip(gamma, -p.clip_gamma, p.clip_gamma)
    clipped = (np.abs(raw_gamma) > p.clip_gamma).any(axis=(1, 2, 3))

    res.update({
        "g_trace": g[:, 0, 0] + g[:, 1, 1],
        "g_det": det, "g_det_safe": det_safe,
        "g_inv_ee": g_inv[:, 0, 0], "g_inv_ej": g_inv[:, 0, 1], "g_inv_jj": g_inv[:, 1, 1],
        # dg[m, i, j] = ∂_m g_ij
        "dE_g_ee": dg[:, 0, 0, 0], "dJ_g_ee": dg[:, 1, 0, 0],
        "dE_g_ej": dg[:, 0, 0, 1], "dJ_g_ej": dg[:, 1, 0, 1],
        "dE_g_jj": dg[:, 0, 1, 1], "dJ_g_jj": dg[:, 1, 1, 1],
        "gamma_e_ee": gamma[:, 0, 0, 0], "gamma_e_ej": gamma[:, 0, 0, 1], "gamma_e_jj": gamma[:, 0, 1, 1],
        "gamma_j_ee": gamma[:, 1, 0, 0], "gamma_j_ej": gamma[:, 1, 0, 1], "gamma_j_jj": gamma[:, 1, 1, 1],
        "gamma_clipped": clipped.astype(float),
        "clip_count": int(clipped.sum()),
    })
    return res


def _field_2d_grid(fit_s, pts_s, cfg: SGVConfig, p: Field2DParams, need_geodesic: bool) -> dict:
    """Rota dos scripts originais: grade, np.gradient e interpolação bilinear."""
    L = cfg.legacy
    ve, vj = fit_s[:, 0], fit_s[:, 1]
    pe, pj = pts_s[:, 0], pts_s[:, 1]
    grid_e, grid_j, d_e, d_j = lg.make_grid(ve, vj, p.grid_n, p.q_low, p.q_high, p.eps)
    rho_grid = lg.fit_kde_density(ve, vj, grid_e, grid_j, p.bandwidth)
    phi_grid = -np.log(rho_grid + p.eps)
    phi_e, phi_j, phi_ee, phi_ej, phi_jj = lg.gradient_and_hessian(phi_grid, d_e, d_j)
    grad_norm_grid = np.sqrt(phi_e ** 2 + phi_j ** 2)

    g_ee_grid = phi_ee + p.metric_reg
    g_ej_grid = phi_ej
    g_jj_grid = phi_jj + p.metric_reg
    g_grid = np.stack([np.stack([g_ee_grid, g_ej_grid], -1), np.stack([g_ej_grid, g_jj_grid], -1)], -2)
    if not L.LEGACY_RAW_METRIC:
        g_grid, _, _ = project_psd(g_grid, cfg.numeric.PSD_FLOOR)
        g_ee_grid, g_ej_grid, g_jj_grid = g_grid[..., 0, 0], g_grid[..., 0, 1], g_grid[..., 1, 1]

    I = lambda grid: lg.bilinear_interp(grid_e, grid_j, grid, pe, pj, p.eps)  # noqa: E731

    h_ee, h_ej, h_jj = I(phi_ee), I(phi_ej), I(phi_jj)
    g_raw_pts = np.stack([np.stack([h_ee + p.metric_reg, h_ej], -1), np.stack([h_ej, h_jj + p.metric_reg], -1)], -2)
    min_eig = np.linalg.eigvalsh(g_raw_pts).min(axis=1)
    if L.LEGACY_RAW_METRIC:
        g_ee_p, g_ej_p, g_jj_p = h_ee + p.metric_reg, h_ej, h_jj + p.metric_reg
    else:
        g_ee_p, g_ej_p, g_jj_p = I(g_ee_grid), I(g_ej_grid), I(g_jj_grid)
    res = {
        "rho": I(rho_grid),
        "phi": I(phi_grid),
        "grad_e": I(phi_e),
        "grad_j": I(phi_j),
        "grad_norm": I(grad_norm_grid),
        "h_ee": h_ee, "h_ej": h_ej, "h_jj": h_jj,
        "g_ee": g_ee_p, "g_ej": g_ej_p, "g_jj": g_jj_p,
        "g_min_eig": min_eig,
        "g_indefinite": (min_eig < 0).astype(float),
        "geom_exact": np.zeros(len(pe)),
    }
    if not need_geodesic:
        return res

    g_trace_grid = g_ee_grid + g_jj_grid
    g_det_grid = g_ee_grid * g_jj_grid - (g_ej_grid ** 2)
    g_det_safe_grid = g_det_grid.copy()
    mask_small = np.abs(g_det_safe_grid) < p.det_floor
    g_det_safe_grid[mask_small] = np.where(g_det_safe_grid[mask_small] >= 0.0, p.det_floor, -p.det_floor)
    g_inv_ee_grid = g_jj_grid / g_det_safe_grid
    g_inv_ej_grid = -g_ej_grid / g_det_safe_grid
    g_inv_jj_grid = g_ee_grid / g_det_safe_grid

    if g_ee_grid.shape[0] >= 3 and g_ee_grid.shape[1] >= 3:
        dE_g_ee, dJ_g_ee = np.gradient(g_ee_grid, d_e, d_j, edge_order=2)
        dE_g_ej, dJ_g_ej = np.gradient(g_ej_grid, d_e, d_j, edge_order=2)
        dE_g_jj, dJ_g_jj = np.gradient(g_jj_grid, d_e, d_j, edge_order=2)
    else:
        z = np.zeros_like(g_ee_grid)
        dE_g_ee = dJ_g_ee = dE_g_ej = dJ_g_ej = dE_g_jj = dJ_g_jj = z

    ge_ee = 0.5 * (g_inv_ee_grid * dE_g_ee + g_inv_ej_grid * (2.0 * dE_g_ej - dJ_g_ee))
    ge_ej = 0.5 * (g_inv_ee_grid * dJ_g_ee + g_inv_ej_grid * dE_g_jj)
    ge_jj = 0.5 * (g_inv_ee_grid * (2.0 * dJ_g_ej - dE_g_jj) + g_inv_ej_grid * dJ_g_jj)
    gj_ee = 0.5 * (g_inv_ej_grid * dE_g_ee + g_inv_jj_grid * (2.0 * dE_g_ej - dJ_g_ee))
    gj_ej = 0.5 * (g_inv_ej_grid * dJ_g_ee + g_inv_jj_grid * dE_g_jj)
    gj_jj = 0.5 * (g_inv_ej_grid * (2.0 * dJ_g_ej - dE_g_jj) + g_inv_jj_grid * dJ_g_jj)
    gammas = [ge_ee, ge_ej, ge_jj, gj_ee, gj_ej, gj_jj]
    clipped_grid = np.zeros_like(ge_ee, dtype=bool)
    for gm in gammas:
        clipped_grid |= np.abs(gm) > p.clip_gamma
    gammas = [np.clip(gm, -p.clip_gamma, p.clip_gamma) for gm in gammas]
    names = ["gamma_e_ee", "gamma_e_ej", "gamma_e_jj", "gamma_j_ee", "gamma_j_ej", "gamma_j_jj"]
    clipped_pts = I(clipped_grid.astype(float)) > 0

    res.update({
        "g_trace": I(g_trace_grid),
        "g_det": I(g_det_grid),
        "g_det_safe": I(g_det_safe_grid),
        "g_inv_ee": I(g_inv_ee_grid), "g_inv_ej": I(g_inv_ej_grid), "g_inv_jj": I(g_inv_jj_grid),
        "dE_g_ee": I(dE_g_ee), "dJ_g_ee": I(dJ_g_ee), "dE_g_ej": I(dE_g_ej),
        "dJ_g_ej": I(dJ_g_ej), "dE_g_jj": I(dE_g_jj), "dJ_g_jj": I(dJ_g_jj),
        "gamma_clipped": clipped_pts.astype(float),
        "clip_count": int(clipped_pts.sum()),
    })
    for nm, gm in zip(names, gammas):
        res[nm] = I(gm)
    return res


# =====================================================================
# Script 2
# =====================================================================
def prepare_input_dataframe(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c = cfg.info
    required = [c.TIMESTAMP_COL, c.E_COL, c.J_COL, c.L_COL]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
    out = df.copy()
    out[c.TIMESTAMP_COL] = pd.to_datetime(out[c.TIMESTAMP_COL], utc=True, errors="coerce")
    for col in (c.E_COL, c.J_COL, c.L_COL):
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=[c.TIMESTAMP_COL, c.E_COL, c.J_COL, c.L_COL]).copy()
    out = out.sort_values(c.TIMESTAMP_COL).drop_duplicates(subset=[c.TIMESTAMP_COL], keep="last")
    out = out.reset_index(drop=True)
    if out.empty:
        raise ValueError("Dataset vazio após limpeza.")
    out = validate_time_index(out, c.TIMESTAMP_COL, dedupe=False)
    return out


LEGACY_NUMERIC_COLS = [
    "rho_field", "phi_field", "grad_phi_e", "grad_phi_j", "grad_phi_norm",
    "hess_phi_ee", "hess_phi_ej", "hess_phi_jj", "field_curvature", "mem_e", "mem_j",
    "geom_incoherence", "geom_incoherence_abs", "field_stress", "rupture_prob_geom",
    "field_grid_n", "field_bandwidth",
]


def build_information_field_geometry_90d(
    df: pd.DataFrame,
    cfg: SGVConfig = DEFAULT_CONFIG,
    *,
    start_row: int = 0,
    _prepared: bool = False,
) -> pd.DataFrame:
    c, L = cfg.info, cfg.legacy
    df = df if _prepared else prepare_input_dataframe(df, cfg)
    n = len(df)
    e = df[c.E_COL].to_numpy(dtype=float)
    j = df[c.J_COL].to_numpy(dtype=float)
    lam = df[c.L_COL].to_numpy(dtype=float)

    params = Field2DParams(c.BANDWIDTH, c.GRID_N, c.Q_LOW, c.Q_HIGH, c.EPS, c.METRIC_REG)
    f = compute_field_2d(e, j, cfg, params, need_geodesic=False, start_row=start_row)

    # memória geométrica (EMA em unidades brutas; desvio nas coordenadas da métrica)
    mem_e = ema(df[c.E_COL], c.ALPHA_E)
    mem_j = ema(df[c.J_COL], c.ALPHA_J)
    d_mem_e = (df[c.E_COL] - mem_e).to_numpy() / f["s_e"]
    d_mem_j = (df[c.J_COL] - mem_j).to_numpy() / f["s_j"]
    g_ee, g_ej, g_jj = f["g_ee"], f["g_ej"], f["g_jj"]
    geom_incoherence = g_ee * d_mem_e ** 2 + 2.0 * g_ej * d_mem_e * d_mem_j + g_jj * d_mem_j ** 2

    q_blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_QUANTILES)
    jol, jol_floored = safe_ratio(
        np.abs(j), lam,
        legacy_abs_eps=L.LEGACY_ABS_EPS, eps=c.EPS, blocks=q_blocks,
        min_periods=min_periods_for(cfg, L.LEGACY_GLOBAL_QUANTILES), q=cfg.numeric.SAFE_RATIO_Q,
    )

    field_curvature = f["h_ee"] + f["h_jj"] + 2.0 * c.METRIC_REG
    gi_abs = np.abs(geom_incoherence)
    field_stress = c.W1 * gi_abs + c.W2 * np.abs(f["grad_norm"]) + c.W3 * np.abs(field_curvature) + c.W4 * jol
    score = c.B0 + c.B1 * gi_abs + c.B2 * np.abs(f["grad_norm"]) + c.B3 * np.abs(field_curvature) + c.B4 * jol
    # score sigmoide NÃO calibrado (β fixados à mão); ver calibrate_rupture_betas
    rupture = np.where(np.isfinite(score), sigmoid(np.nan_to_num(score)), np.nan)

    mem_valid = (np.arange(n) >= int(np.ceil(1.0 / c.ALPHA_E))).astype(int)

    cols: dict[str, Any] = {
        "rho_field": f["rho"], "phi_field": f["phi"],
        "grad_phi_e": f["grad_e"], "grad_phi_j": f["grad_j"], "grad_phi_norm": f["grad_norm"],
        "hess_phi_ee": f["h_ee"], "hess_phi_ej": f["h_ej"], "hess_phi_jj": f["h_jj"],
        "field_curvature": field_curvature,
        "mem_e": mem_e.to_numpy(), "mem_j": mem_j.to_numpy(),
        "geom_incoherence": geom_incoherence, "geom_incoherence_abs": gi_abs,
        "field_stress": field_stress, "rupture_prob_geom": rupture,
        "field_grid_n": float(c.GRID_N), "field_bandwidth": float(c.BANDWIDTH),
        # colunas novas
        "phi_laplacian": field_curvature,
        "g_ee": g_ee, "g_ej": g_ej, "g_jj": g_jj,
        "g_indefinite": f["g_indefinite"], "g_min_eig": f["g_min_eig"],
        "jerk_over_lambda": jol, "jerk_over_lambda_floored": jol_floored,
        "mem_valid": mem_valid,
        "kde_scale_e": f["s_e"], "kde_scale_j": f["s_j"],
        "info_valid": ((f["fit_valid"] > 0) & (mem_valid > 0) & np.isfinite(jol)).astype(int),
    }
    out = assign_columns(df, cols)
    add_meta(out, "info_field", {
        "g_indefinite_share": float(np.nanmean(f["g_indefinite"])) if n else None,
        "fit_valid_share": float(np.mean(f["fit_valid"])) if n else None,
    })
    if L.LEGACY_ZERO_FILL:
        out = legacy_fill_zero(out, LEGACY_NUMERIC_COLS)
    return out


# =====================================================================
# Gancho de calibração (2.6) — desligado por padrão
# =====================================================================
def calibrate_rupture_betas(info_df: pd.DataFrame, events, cfg: SGVConfig = DEFAULT_CONFIG) -> SGVConfig:
    """Ajusta B0..B4 de ``rupture_prob_geom`` por regressão logística.

    ``events``: série/array 0/1 alinhada às linhas de ``info_df`` com o evento
    que a "probabilidade de ruptura" deveria prever, definido pelo usuário nos
    dados de exploração (nunca nos dados reservados). Devolve uma nova
    configuração com os β ajustados; a configuração padrão não é alterada.
    """
    from sklearn.linear_model import LogisticRegression

    feats = np.column_stack([
        np.abs(info_df["geom_incoherence"].to_numpy(float)),
        np.abs(info_df["grad_phi_norm"].to_numpy(float)),
        np.abs(info_df["field_curvature"].to_numpy(float)),
        info_df["jerk_over_lambda"].to_numpy(float),
    ])
    y = np.asarray(events, dtype=float)
    ok = np.isfinite(feats).all(axis=1) & np.isfinite(y)
    if ok.sum() < 50 or len(np.unique(y[ok])) < 2:
        raise ValueError("Dados insuficientes para calibrar (precisa de ≥50 linhas e as duas classes).")
    model = LogisticRegression(C=1e6, max_iter=1000).fit(feats[ok], y[ok].astype(int))
    b = model.coef_[0]
    return cfg.with_section("info", B0=float(model.intercept_[0]), B1=float(b[0]), B2=float(b[1]),
                            B3=float(b[2]), B4=float(b[3]))


# =====================================================================
# Runtime com cache incremental (2.7)
# =====================================================================
@dataclass
class _CacheEntry:
    signature: tuple | None = None
    prepared: pd.DataFrame | None = None
    result: pd.DataFrame | None = None


def _region_hash(df: pd.DataFrame, cfg: SGVConfig, upto: int) -> str:
    """Hash das linhas [0, upto) das colunas de entrada (detecta revisão de barras antigas)."""
    c = cfg.info
    region = df.iloc[:upto][[c.TIMESTAMP_COL, c.E_COL, c.J_COL, c.L_COL]]
    raw = pd.util.hash_pandas_object(region, index=False).to_numpy().tobytes()
    return hashlib.sha256(raw).hexdigest()


def build_runtime_signature(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> tuple:
    return (cfg.config_hash(), len(df), _region_hash(df, cfg, len(df)))


class InformationFieldGeometryRuntime:
    """Wrapper para o live.

    - Mesmo snapshot → devolve o resultado em cache.
    - Snapshot que estende o anterior (mesmas linhas antigas) e modo causal →
      calcula só as linhas novas (O(1) por barra entre reajustes).
    - Caso contrário → recalcula tudo (inclusive no modo legado global, em
      que cada barra nova altera a KDE de todas as linhas).
    """

    def __init__(self, cfg: SGVConfig = DEFAULT_CONFIG) -> None:
        self.cfg = cfg
        self.cache = _CacheEntry()
        self.stats = {"hits": 0, "incremental": 0, "full": 0}

    def _incremental_ok(self) -> bool:
        L = self.cfg.legacy
        return not (L.LEGACY_GLOBAL_KDE or L.LEGACY_GLOBAL_QUANTILES)

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        prepared = prepare_input_dataframe(df, self.cfg)
        sig = build_runtime_signature(prepared, self.cfg)
        ce = self.cache
        if ce.signature == sig and ce.result is not None:
            self.stats["hits"] += 1
            return ce.result.copy()

        old_n = len(ce.prepared) if ce.prepared is not None else 0
        extends = (
            ce.prepared is not None
            and self._incremental_ok()
            and len(prepared) > old_n
            and _region_hash(prepared, self.cfg, old_n) == ce.signature[2]
        )
        if extends:
            new = build_information_field_geometry_90d(prepared, self.cfg, start_row=old_n, _prepared=True)
            old = ce.result
            result = pd.concat([old, new.iloc[old_n:]], axis=0)
            result.index = new.index
            result.attrs = new.attrs
            self.stats["incremental"] += 1
        else:
            result = build_information_field_geometry_90d(prepared, self.cfg, _prepared=True)
            self.stats["full"] += 1

        ce.signature = sig
        ce.prepared = prepared
        ce.result = result.copy()
        return result
