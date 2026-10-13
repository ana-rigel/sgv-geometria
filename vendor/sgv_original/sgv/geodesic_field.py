"""Arquivo 3 — campo geodésico 2D + gravidade informacional 3D.

Reescrita de ``sgv_geodesic_field_full3d_90d_refactored.py``.

Essência mantida: φ = -log ρ, métrica Hessiana, Christoffels, aceleração
geodésica e resíduo, Ricci, escalar R, Einstein G, tensor T_info e
``field_gravity`` com as mesmas fórmulas e pesos.

Itens implementados: 3.A e 3.1–3.11.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from .common import legacy_grid as lg
from .common.blocks import block_reduce, causal_or_global_blocks, min_periods_for
from .common.geometry import (
    einstein_tensor, fd_ricci, project_psd, ricci_hessian, safe_inv, scalar_curvature,
    tensor_inner, tensor_norm,
)
from .common.kde import kde_eval
from .common.numeric import ema, safe_ratio, sigmoid
from .common.scaling import scaler_for
from .common.validity import add_clip_count, add_meta, assign_columns, legacy_fill_zero, validate_time_index
from .config import DEFAULT_CONFIG, SGVConfig
from .information_field import Field2DParams, compute_field_2d

log = logging.getLogger("sgv.geodesic")

TENSOR_PAIRS_9 = [(i, k) for i in range(3) for k in range(3)]
TENSOR_PAIRS_6 = [(i, k) for i in range(3) for k in range(i, 3)]


def prepare_input_dataframe(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c = cfg.geodesic
    missing = [col for col in (c.E_COL, c.J_COL, c.L_COL) if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando no input: {missing}")
    out = df.copy()
    for col in (c.E_COL, c.J_COL, c.L_COL):
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=[c.E_COL, c.J_COL, c.L_COL]).reset_index(drop=True)
    if out.empty:
        raise ValueError("Dataset vazio após limpeza.")
    if "timestamp" in out.columns:
        out = validate_time_index(out, "timestamp", dedupe=False, sort=False)
    return out


# =====================================================================
# Camada 3D
# =====================================================================
def compute_field_3d(e, j, m, lam, cfg: SGVConfig, start_row: int = 0) -> dict[str, Any]:
    c, L = cfg.geodesic, cfg.legacy
    n = len(e)
    X3 = np.column_stack([e, j, m]).astype(float)
    lam = np.asarray(lam, dtype=float)
    blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_KDE, kind="fit")
    min_fit = min_periods_for(cfg, L.LEGACY_GLOBAL_KDE, kind="fit")

    pairs = TENSOR_PAIRS_9 if L.LEGACY_9_COMPONENTS else TENSOR_PAIRS_6
    keys = ["R", "T_norm", "G_norm", "gravity", "einstein_T_cos", "gt_inner", "tt_inner",
            "g3_min_eig", "g3_indefinite", "geom3_exact", "curv_clipped", "grav_clipped",
            "s_m", "fit3_valid"]
    out: dict[str, Any] = {k: np.full(n, np.nan) for k in keys}
    out["fit3_valid"] = np.zeros(n)
    for (a, b_) in pairs:
        out[f"G_{a}{b_}"] = np.full(n, np.nan)
        out[f"T_{a}{b_}"] = np.full(n, np.nan)

    for blk in blocks:
        if blk.stop <= start_row:
            continue
        ev = np.arange(max(blk.start, start_row), blk.stop)
        fit_rows = slice(blk.fit_start, blk.fit_stop)
        Xf, lf = X3[fit_rows], lam[fit_rows]
        ok = np.isfinite(Xf).all(axis=1) & np.isfinite(lf)
        Xf, lf = Xf[ok], lf[ok]
        if len(Xf) < max(min_fit, 3):
            continue
        sc = scaler_for(Xf, L.LEGACY_UNSCALED_KDE)
        fit_s = sc.transform(Xf)
        pts_s = sc.transform(X3[ev])
        out["s_m"][ev] = sc.scale[2]
        if L.LEGACY_FD_CURVATURE:
            res = _field_3d_grid(fit_s, lf, pts_s, cfg, pairs)
        else:
            res = _field_3d_analytic(fit_s, lf, pts_s, cfg, pairs)
        for k, v in res.items():
            out[k][ev] = v
        out["fit3_valid"][ev] = np.isfinite(res["R"]).astype(float)
    return out


def _gravity(R, T_norm, G_norm, kappa, clip):
    raw = kappa * np.sign(R) * np.log1p(np.abs(R)) * np.log1p(np.abs(T_norm)) * np.log1p(np.abs(G_norm))
    clipped = np.abs(raw) > clip
    return np.clip(raw, -clip, clip), clipped


def _cosine(gt, G_norm, T_norm):
    """⟨G, T⟩ / (|G| |T|); NaN quando um dos tensores é nulo."""
    denom = G_norm * T_norm
    with np.errstate(invalid="ignore", divide="ignore"):
        cos = np.where(denom > 1e-300, gt / denom, np.nan)
    return np.clip(cos, -1.0, 1.0)


def _t_info(grad_phi, grad_lam, lam_hat, g, g_inv, c):
    grad_phi_sq = np.einsum("...i,...ij,...j->...", grad_phi, g_inv, grad_phi)
    grad_lam_sq = np.einsum("...i,...ij,...j->...", grad_lam, g_inv, grad_lam)
    outer_phi = np.einsum("...i,...j->...ij", grad_phi, grad_phi)
    outer_lam = np.einsum("...i,...j->...ij", grad_lam, grad_lam)
    return (
        c.W_PHI_STRESS * outer_phi
        + c.W_MEM_STRESS * outer_lam
        + c.W_LAMBDA_STRESS * lam_hat[..., None, None] * g
        - 0.5 * (c.W_PHI_STRESS * grad_phi_sq + c.W_MEM_STRESS * grad_lam_sq)[..., None, None] * g
    )


def _field_3d_analytic(fit_s, lam_fit, pts_s, cfg: SGVConfig, pairs) -> dict:
    c, L = cfg.geodesic, cfg.legacy
    h = c.BANDWIDTH_3D
    r = kde_eval(pts_s, fit_s, h, order=3, nw_values=lam_fit)
    reg = c.METRIC_REG
    g_raw = r.hess_phi + reg * np.eye(3)[None]
    finite = np.isfinite(g_raw).all(axis=(1, 2))
    min_eig = np.full(len(g_raw), np.nan)
    if finite.any():
        min_eig[finite] = np.linalg.eigvalsh(g_raw[finite]).min(axis=1)
    if L.LEGACY_RAW_METRIC:
        g, changed = g_raw, np.zeros(len(g_raw), dtype=bool)
    else:
        g, changed, _ = project_psd(g_raw, cfg.numeric.PSD_FLOOR)
    g_inv = safe_inv(g)

    ric = ricci_hessian(g_inv, r.phi3)
    fb = changed & finite
    if fb.any() and cfg.numeric.PSD_FALLBACK == "fd":
        floor = cfg.numeric.PSD_FLOOR

        def metric_fn(Y):
            Hy = kde_eval(Y, fit_s, h, order=2).hess_phi + reg * np.eye(3)[None]
            return project_psd(Hy, floor)[0]

        ric_fd, _, _ = fd_ricci(metric_fn, pts_s[fb], cfg.numeric.FD_DELTA)
        ric[fb] = ric_fd

    R_raw = scalar_curvature(ric, g_inv)
    curv_clipped = np.abs(R_raw) > c.CLIP_CURV_3D
    R = np.clip(R_raw, -c.CLIP_CURV_3D, c.CLIP_CURV_3D)
    G = einstein_tensor(ric, R, g)
    T = _t_info(r.grad_phi, r.nw_grad, r.nw_value, g, g_inv, c)
    psd = not L.LEGACY_RAW_METRIC
    T_norm = tensor_norm(T, g_inv, check_psd=psd)
    G_norm = tensor_norm(G, g_inv, check_psd=psd)
    gravity, grav_clipped = _gravity(R, T_norm, G_norm, c.KAPPA_INFO, c.CLIP_FIELD_GRAVITY)
    gt = tensor_inner(G, T, g_inv)
    tt = tensor_inner(T, T, g_inv)
    cos = _cosine(gt, G_norm, T_norm)

    res = {
        "R": R, "T_norm": T_norm, "G_norm": G_norm, "gravity": gravity,
        "einstein_T_cos": cos, "gt_inner": gt, "tt_inner": tt,
        "g3_min_eig": min_eig, "g3_indefinite": (min_eig < 0).astype(float),
        "geom3_exact": (~changed).astype(float),
        "curv_clipped": curv_clipped.astype(float), "grav_clipped": grav_clipped.astype(float),
    }
    for (a, b_) in pairs:
        res[f"G_{a}{b_}"] = G[:, a, b_]
        res[f"T_{a}{b_}"] = T[:, a, b_]
    return res


def _field_3d_grid(fit_s, lam_fit, pts_s, cfg: SGVConfig, pairs) -> dict:
    """Rota dos scripts originais (LEGACY_FD_CURVATURE)."""
    c, L = cfg.geodesic, cfg.legacy
    ve, vj, vm = fit_s[:, 0], fit_s[:, 1], fit_s[:, 2]
    grid_e3 = lg.make_axis_1d(ve, c.GRID_N_E3, c.Q_LOW, c.Q_HIGH, c.EPS)
    grid_j3 = lg.make_axis_1d(vj, c.GRID_N_J3, c.Q_LOW, c.Q_HIGH, c.EPS)
    grid_m3 = lg.make_axis_1d(vm, c.GRID_N_M3, c.Q_LOW, c.Q_HIGH, c.EPS)
    d_e3 = float(grid_e3[1] - grid_e3[0]) if len(grid_e3) > 1 else 1.0
    d_j3 = float(grid_j3[1] - grid_j3[0]) if len(grid_j3) > 1 else 1.0
    d_m3 = float(grid_m3[1] - grid_m3[0]) if len(grid_m3) > 1 else 1.0

    rho3 = lg.fit_kde_density_3d(ve, vj, vm, grid_e3, grid_j3, grid_m3, c.BANDWIDTH_3D)
    phi3 = -np.log(rho3 + c.EPS)
    g3 = lg.build_metric_3d(phi3, d_e3, d_j3, d_m3, c.METRIC_REG)
    g3_raw_min = np.linalg.eigvalsh(0.5 * (g3 + np.swapaxes(g3, -1, -2))).min(axis=-1)
    if not L.LEGACY_RAW_METRIC:
        g3, _, _ = project_psd(g3, cfg.numeric.PSD_FLOOR)
    g3_inv, _ = lg.invert_metric_3x3_field(g3, c.METRIC_REG, c.DET_FLOOR)

    phi_e3, phi_j3, phi_m3 = lg.gradient_3d(phi3, d_e3, d_j3, d_m3)
    lam_field = lg.build_lambda_field_3d(ve, vj, vm, lam_fit, grid_e3, grid_j3, grid_m3, c.BANDWIDTH_3D, c.EPS)
    lam_e3, lam_j3, lam_m3 = lg.gradient_3d(lam_field, d_e3, d_j3, d_m3)
    grad_phi = np.stack([phi_e3, phi_j3, phi_m3], axis=-1)
    grad_lam = np.stack([lam_e3, lam_j3, lam_m3], axis=-1)
    T = _t_info(grad_phi, grad_lam, lam_field, g3, g3_inv, c)
    T_norm = lg.tensor_frobenius_norm_3d(T, g3_inv)

    dg3 = lg.metric_derivatives_3d(g3, d_e3, d_j3, d_m3)
    gamma3 = lg.christoffel_3d(g3_inv, dg3, c.CLIP_GAMMA)
    dgamma3 = lg.gamma_derivatives_3d(gamma3, d_e3, d_j3, d_m3)
    ric3 = lg.ricci_tensor_3d(gamma3, dgamma3)
    R_raw = lg.scalar_curvature_3d(ric3, g3_inv)
    curv_clip_grid = (np.abs(R_raw) > c.CLIP_CURV_3D).astype(float)
    R = np.clip(R_raw, -c.CLIP_CURV_3D, c.CLIP_CURV_3D)
    G = lg.einstein_tensor_3d(ric3, R, g3)
    G_norm = lg.tensor_frobenius_norm_3d(G, g3_inv)
    gravity, grav_clip_grid = _gravity(R, T_norm, G_norm, c.KAPPA_INFO, c.CLIP_FIELD_GRAVITY)
    gt = np.einsum("...ij,...ab,...ia,...jb->...", G, T, g3_inv, g3_inv)
    tt = np.einsum("...ij,...ab,...ia,...jb->...", T, T, g3_inv, g3_inv)
    cos = _cosine(gt, G_norm, T_norm)

    pe, pj, pm = pts_s[:, 0], pts_s[:, 1], pts_s[:, 2]
    I = lambda grid: lg.trilinear_interp(grid_e3, grid_j3, grid_m3, grid, pe, pj, pm, c.EPS)  # noqa: E731
    min_eig = I(g3_raw_min)
    res = {
        "R": I(R), "T_norm": I(T_norm), "G_norm": I(G_norm), "gravity": I(gravity),
        "einstein_T_cos": I(cos), "gt_inner": I(gt), "tt_inner": I(tt),
        "g3_min_eig": min_eig, "g3_indefinite": (min_eig < 0).astype(float),
        "geom3_exact": np.zeros(len(pe)),
        "curv_clipped": (I(curv_clip_grid) > 0).astype(float),
        "grav_clipped": (I(grav_clip_grid.astype(float)) > 0).astype(float),
    }
    for (a, b_) in pairs:
        res[f"G_{a}{b_}"] = I(G[..., a, b_])
        res[f"T_{a}{b_}"] = I(T[..., a, b_])
    return res


# =====================================================================
# Script 3
# =====================================================================
LEGACY_FILL_ZERO_COLS = [
    "rho_field", "phi_field", "grad_phi_e", "grad_phi_j", "grad_phi_norm",
    "hess_phi_ee", "hess_phi_ej", "hess_phi_jj", "g_ee", "g_ej", "g_jj", "g_trace",
    "g_det", "g_det_safe", "g_inv_ee", "g_inv_ej", "g_inv_jj", "field_curvature",
    "dE_g_ee", "dJ_g_ee", "dE_g_ej", "dJ_g_ej", "dE_g_jj", "dJ_g_jj",
    "gamma_e_ee", "gamma_e_ej", "gamma_e_jj", "gamma_j_ee", "gamma_j_ej", "gamma_j_jj",
    "mem_e", "mem_j", "geom_incoherence", "geom_incoherence_abs", "vel_e", "vel_j",
    "acc_obs_e", "acc_obs_j", "acc_geo_e", "acc_geo_j", "acc_geo_norm",
    "geo_resid_e", "geo_resid_j", "geo_resid_norm", "jerk_over_lambda",
    "field_stress_geodesic", "rupture_prob_geodesic", "memory_flux",
    "field_curvature_scalar", "field_stress_tensor_norm", "field_einstein_norm",
    "field_gravity", "gravitational_stress_score", "field_grid_n_3d_e", "field_grid_n_3d_j",
    "field_grid_n_3d_m", "field_bandwidth_3d", "kappa_info", "field_grid_n", "field_bandwidth",
]
CRITICAL_PHYSICS_COLS = [
    "field_stress_geodesic", "geo_resid_norm", "acc_geo_norm", "grad_phi_norm",
    "geom_incoherence_abs", "jerk_over_lambda",
]


def build_geodesic_field_full3d_90d(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c, L = cfg.geodesic, cfg.legacy
    df = prepare_input_dataframe(df, cfg)
    n = len(df)
    e = df[c.E_COL].to_numpy(dtype=float)
    j = df[c.J_COL].to_numpy(dtype=float)
    lam = df[c.L_COL].to_numpy(dtype=float)

    # ---------------- 1–6: campo 2D (3.1: reutiliza o módulo do arquivo 2)
    params = Field2DParams(c.BANDWIDTH, c.GRID_N, c.Q_LOW, c.Q_HIGH, c.EPS, c.METRIC_REG,
                           c.DET_FLOOR, c.CLIP_GAMMA)
    f = compute_field_2d(e, j, cfg, params, need_geodesic=True)
    s_e, s_j = f["s_e"], f["s_j"]
    field_curvature = f["h_ee"] + f["h_jj"] + 2.0 * c.METRIC_REG

    # ---------------- 7: memória e incoerência
    mem_e = ema(df[c.E_COL], c.ALPHA_E).to_numpy()
    mem_j = ema(df[c.J_COL], c.ALPHA_J).to_numpy()
    d_mem_e = (e - mem_e) / s_e
    d_mem_j = (j - mem_j) / s_j
    geom_incoherence = f["g_ee"] * d_mem_e ** 2 + 2.0 * f["g_ej"] * d_mem_e * d_mem_j + f["g_jj"] * d_mem_j ** 2

    # ---------------- 8–10: cinemática e resíduo geodésico
    E = pd.Series(e)
    J = pd.Series(j)
    gam = {k: f[k] for k in ("gamma_e_ee", "gamma_e_ej", "gamma_e_jj", "gamma_j_ee", "gamma_j_ej", "gamma_j_jj")}
    if L.LEGACY_KINEMATICS:
        vel_e = E.diff().to_numpy() / s_e
        vel_j = J.diff().to_numpy() / s_j
        acc_obs_e = E.diff().diff().to_numpy() / s_e
        acc_obs_j = J.diff().diff().to_numpy() / s_j
        G2 = gam
    else:
        # 3.4: tudo centrado em t-1 (conhecido em t), nas coordenadas do bloco de t-1
        s_e_prev = pd.Series(s_e).shift(1).to_numpy()
        s_j_prev = pd.Series(s_j).shift(1).to_numpy()
        vel_e = ((E - E.shift(2)) / 2.0).to_numpy() / s_e_prev
        vel_j = ((J - J.shift(2)) / 2.0).to_numpy() / s_j_prev
        acc_obs_e = (E - 2.0 * E.shift(1) + E.shift(2)).to_numpy() / s_e_prev
        acc_obs_j = (J - 2.0 * J.shift(1) + J.shift(2)).to_numpy() / s_j_prev
        G2 = {k: pd.Series(v).shift(1).to_numpy() for k, v in gam.items()}
    if L.LEGACY_ZERO_FILL:
        acc_obs_e = np.nan_to_num(acc_obs_e, nan=0.0)
        acc_obs_j = np.nan_to_num(acc_obs_j, nan=0.0)

    acc_geo_e_raw = -(G2["gamma_e_ee"] * vel_e ** 2 + 2.0 * G2["gamma_e_ej"] * vel_e * vel_j + G2["gamma_e_jj"] * vel_j ** 2)
    acc_geo_j_raw = -(G2["gamma_j_ee"] * vel_e ** 2 + 2.0 * G2["gamma_j_ej"] * vel_e * vel_j + G2["gamma_j_jj"] * vel_j ** 2)
    acc_clipped = (np.abs(acc_geo_e_raw) > c.CLIP_ACC) | (np.abs(acc_geo_j_raw) > c.CLIP_ACC)
    acc_geo_e = np.clip(acc_geo_e_raw, -c.CLIP_ACC, c.CLIP_ACC)
    acc_geo_j = np.clip(acc_geo_j_raw, -c.CLIP_ACC, c.CLIP_ACC)
    acc_geo_norm = np.sqrt(acc_geo_e ** 2 + acc_geo_j ** 2)
    geo_resid_e = acc_obs_e - acc_geo_e
    geo_resid_j = acc_obs_j - acc_geo_j
    geo_resid_norm = np.sqrt(geo_resid_e ** 2 + geo_resid_j ** 2)

    # ---------------- 11–13
    q_blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_QUANTILES)
    q_min = min_periods_for(cfg, L.LEGACY_GLOBAL_QUANTILES)
    jol, jol_floored = safe_ratio(np.abs(j), lam, legacy_abs_eps=L.LEGACY_ABS_EPS, eps=c.EPS,
                                  blocks=q_blocks, min_periods=q_min, q=cfg.numeric.SAFE_RATIO_Q)
    gi_abs = np.abs(geom_incoherence)
    gnorm = np.abs(f["grad_norm"])
    stress = (c.W_INCOH * gi_abs + c.W_GRAD * gnorm + c.W_GEO_RESID * geo_resid_norm
              + c.W_ACC_GEO * acc_geo_norm + c.W_CURVATURE * np.abs(field_curvature)
              + c.W_JERK_OVER_LAMBDA * jol)
    score = (c.B0 + c.B1 * geo_resid_norm + c.B2 * acc_geo_norm + c.B3 * gnorm
             + c.B4 * gi_abs + c.B5 * np.abs(field_curvature) + c.B6 * jol)
    rupture = np.where(np.isfinite(score), sigmoid(np.nan_to_num(score)), np.nan)

    # ---------------- 14: camada 3D
    memory_flux = pd.Series(mem_e).diff().to_numpy()
    if L.LEGACY_ZERO_FILL:
        memory_flux = np.nan_to_num(memory_flux, nan=0.0)
    f3 = compute_field_3d(e, j, memory_flux, lam, cfg)
    R3, Tn, Gn = f3["R"], f3["T_norm"], f3["G_norm"]
    if L.LEGACY_ZERO_FILL:
        R_f, T_f = np.nan_to_num(R3, nan=0.0), np.nan_to_num(Tn, nan=0.0)
    else:
        R_f, T_f = R3, Tn
    grav_stress = np.sign(R_f) * np.log1p(np.abs(R_f)) * np.log1p(np.abs(T_f))

    gt_sum = block_reduce(f3["gt_inner"], q_blocks, np.sum, q_min)
    tt_sum = block_reduce(f3["tt_inner"], q_blocks, np.sum, q_min)
    with np.errstate(invalid="ignore", divide="ignore"):
        kappa_hat = gt_sum / tt_sum

    geom_clipped = ((f["gamma_clipped"] > 0) | acc_clipped | (f3["curv_clipped"] > 0) | (f3["grav_clipped"] > 0))

    cols: dict[str, Any] = {
        "rho_field": f["rho"], "phi_field": f["phi"],
        "grad_phi_e": f["grad_e"], "grad_phi_j": f["grad_j"], "grad_phi_norm": f["grad_norm"],
        "hess_phi_ee": f["h_ee"], "hess_phi_ej": f["h_ej"], "hess_phi_jj": f["h_jj"],
        "g_ee": f["g_ee"], "g_ej": f["g_ej"], "g_jj": f["g_jj"],
        "g_trace": f["g_trace"], "g_det": f["g_det"], "g_det_safe": f["g_det_safe"],
        "g_inv_ee": f["g_inv_ee"], "g_inv_ej": f["g_inv_ej"], "g_inv_jj": f["g_inv_jj"],
        "field_curvature": field_curvature,
        "dE_g_ee": f["dE_g_ee"], "dJ_g_ee": f["dJ_g_ee"], "dE_g_ej": f["dE_g_ej"],
        "dJ_g_ej": f["dJ_g_ej"], "dE_g_jj": f["dE_g_jj"], "dJ_g_jj": f["dJ_g_jj"],
        **gam,
        "mem_e": mem_e, "mem_j": mem_j,
        "geom_incoherence": geom_incoherence, "geom_incoherence_abs": gi_abs,
        "vel_e": vel_e, "vel_j": vel_j, "acc_obs_e": acc_obs_e, "acc_obs_j": acc_obs_j,
        "acc_geo_e": acc_geo_e, "acc_geo_j": acc_geo_j, "acc_geo_norm": acc_geo_norm,
        "geo_resid_e": geo_resid_e, "geo_resid_j": geo_resid_j, "geo_resid_norm": geo_resid_norm,
        "jerk_over_lambda": jol,
        "field_stress_geodesic": stress, "rupture_prob_geodesic": rupture,
        "memory_flux": memory_flux,
        "field_curvature_scalar": R3, "field_stress_tensor_norm": Tn,
        "field_einstein_norm": Gn, "field_gravity": f3["gravity"],
        "gravitational_stress_score": grav_stress,
    }
    pairs = TENSOR_PAIRS_9 if L.LEGACY_9_COMPONENTS else TENSOR_PAIRS_6
    for (a, b_) in pairs:
        cols[f"G_info_{a}{b_}"] = f3[f"G_{a}{b_}"]
    for (a, b_) in pairs:
        cols[f"T_info_{a}{b_}"] = f3[f"T_{a}{b_}"]
    cols.update({
        "field_grid_n_3d_e": float(c.GRID_N_E3), "field_grid_n_3d_j": float(c.GRID_N_J3),
        "field_grid_n_3d_m": float(c.GRID_N_M3), "field_bandwidth_3d": float(c.BANDWIDTH_3D),
        "kappa_info": float(c.KAPPA_INFO),
    })
    out = assign_columns(df, cols)

    op_cols = ["vel_e", "vel_j", "acc_obs_e", "acc_obs_j", "acc_geo_e", "acc_geo_j",
               "geo_resid_e", "geo_resid_j", "field_stress_geodesic", "rupture_prob_geodesic",
               "field_gravity", "field_curvature_scalar", "field_einstein_norm"]
    geodesic_valid = (~out[op_cols].isna().any(axis=1)).astype(int)
    if not L.LEGACY_ZERO_FILL:
        geodesic_valid = geodesic_valid & (f["fit_valid"] > 0) & (f3["fit3_valid"] > 0)
    new_cols: dict[str, Any] = {
        "geodesic_valid": np.asarray(geodesic_valid, dtype=int),
        "field_grid_n": float(c.GRID_N), "field_bandwidth": float(c.BANDWIDTH),
        # diagnósticos novos
        "phi_laplacian": field_curvature,
        "g_indefinite": f["g_indefinite"], "g_min_eig": f["g_min_eig"], "geom_exact": f["geom_exact"],
        "g3_indefinite": f3["g3_indefinite"], "g3_min_eig": f3["g3_min_eig"], "geom3_exact": f3["geom3_exact"],
        "geom_clipped": geom_clipped.astype(int),
        "jerk_over_lambda_floored": jol_floored,
        "einstein_T_cos": f3["einstein_T_cos"], "kappa_hat": kappa_hat,
        "kde_scale_e": s_e, "kde_scale_j": s_j, "kde_scale_m": f3["s_m"],
    }
    out = assign_columns(out, new_cols)

    add_clip_count(out, "gamma_2d", int(np.nansum(f["gamma_clipped"])))
    add_clip_count(out, "acc_geo", int(acc_clipped.sum()))
    add_clip_count(out, "field_curvature_scalar", int(np.nansum(f3["curv_clipped"])))
    add_clip_count(out, "field_gravity", int(np.nansum(f3["grav_clipped"])))
    add_meta(out, "geodesic", {
        "geom_clipped_share": float(geom_clipped.mean()) if n else None,
        "g_indefinite_share": float(np.nanmean(f["g_indefinite"])) if n else None,
        "g3_indefinite_share": float(np.nanmean(f3["g3_indefinite"])) if n else None,
    })

    if L.LEGACY_ZERO_FILL:
        fill = [col for col in LEGACY_FILL_ZERO_COLS if col not in CRITICAL_PHYSICS_COLS]
        out = legacy_fill_zero(out, fill)
        comp_cols = [col for col in out.columns if col.startswith("G_info_") or col.startswith("T_info_")]
        comp_cols = [col for col in comp_cols if not col.endswith("abs_sum")]
        out = legacy_fill_zero(out, comp_cols)

    out = assign_columns(out, {
        "stress_valid": pd.to_numeric(out["field_stress_geodesic"], errors="coerce").notna().astype(int).to_numpy()
    })
    return out
