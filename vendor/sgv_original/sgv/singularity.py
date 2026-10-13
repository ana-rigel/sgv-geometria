"""Arquivo 4 — detector de singularidade e criticalidade.

Reescrita de ``sgv_build_singularity_detector_90d_refactored.py``. Pesos,
tipos, score composto e estágios inalterados. Itens 4.1–4.8.

Atenção (4.5): as colunas ``*_prob`` são a sigmoide de um z-score robusto,
NÃO uma probabilidade calibrada de nenhum evento. Os alertas são faixas de
quantil: disparam em ~10%/5%/1% das barras por construção, em qualquer
mercado (ver ``alert_rate_realized``).
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .common.blocks import causal_or_global_blocks, min_periods_for
from .common.numeric import log1p_safe, safe_ratio, sigmoid
from .common.stats import minmax_robust, quantile_threshold, robust_z_singularity
from .common.validity import add_meta, assign_columns, legacy_fill_zero
from .config import DEFAULT_CONFIG, SGVConfig

LOG_COMPONENTS = [
    "rigidity_log", "det_log", "ginv_log", "gamma_log", "curvature_log", "curvature_scalar_log",
    "einstein_log", "gravity_log", "grav_stress_log", "stress_log", "geo_resid_log",
    "memory_flux_log", "jerk_lambda_log", "grad_phi_log",
]

FILL_ZERO_COLS = [
    "rigidity_inverse", "det_inverse", "g_inv_norm", "gamma_norm", "curvature_abs",
    "curvature_scalar_abs", "einstein_norm_abs", "gravity_abs", "grav_stress_abs",
    "stress_energy_raw", "memory_flux_abs", *LOG_COMPONENTS,
    "sgv_sing_rigidity_score", "sgv_sing_curvature_score", "sgv_sing_stress_score",
    "sgv_sing_gravity_score", "sgv_singularity_score", "sgv_singularity_score_z",
    "sgv_singularity_score_01", "sgv_singularity_prob", "sgv_criticality_score",
    "sgv_criticality_score_z", "sgv_criticality_score_01", "sgv_criticality_prob",
    "sgv_singularity_alert_q90", "sgv_singularity_alert_q95", "sgv_singularity_alert_q99",
    "sgv_criticality_alert_q95", "sgv_sing_rigidity_alert", "sgv_sing_curvature_alert",
    "sgv_sing_stress_alert", "sgv_sing_gravity_alert", "ricci3_alert_q95", "gravity_alert_q95",
    "einstein_alert_q95", "G_info_abs_sum", "T_info_abs_sum", "sgv_singularity_valid",
]


def _col(df: pd.DataFrame, name: str, default: float = np.nan) -> np.ndarray:
    if name in df.columns:
        return pd.to_numeric(df[name], errors="coerce").replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)
    return np.full(len(df), default, dtype=float)


def _alert(score: np.ndarray, thr: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore"):
        return (score >= thr).astype(int)


def build_singularity_detector_90d(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c, L = cfg.singularity, cfg.legacy
    df = df.copy().replace([np.inf, -np.inf], np.nan)
    if c.L_COL not in df.columns:
        raise ValueError(f"Coluna obrigatória faltando: {c.L_COL}")
    df[c.L_COL] = pd.to_numeric(df[c.L_COL], errors="coerce")
    n = len(df)
    ML = c.MAX_LOG_COMPONENT
    lg = lambda x: log1p_safe(x, ML)  # noqa: E731
    def nz(x):  # fillna(0) aplicado pelo original a componentes específicos
        return np.nan_to_num(x, nan=0.0)

    base_names = ["g_det", "g_inv_ee", "g_inv_ej", "g_inv_jj", "field_curvature", "geo_resid_norm",
                  "field_stress_geodesic", "geom_incoherence_abs", "grad_phi_norm", "jerk_over_lambda",
                  "rupture_prob_geodesic", "field_curvature_scalar", "field_stress_tensor_norm",
                  "field_einstein_norm", "field_gravity", "gravitational_stress_score", "memory_flux"]
    b = {k: _col(df, k) for k in base_names}
    gamma_names = ["gamma_e_ee", "gamma_e_ej", "gamma_e_jj", "gamma_j_ee", "gamma_j_ej", "gamma_j_jj"]
    for k in gamma_names:
        b[k] = _col(df, k, default=0.0)

    q_blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_QUANTILES)
    q_min = min_periods_for(cfg, L.LEGACY_GLOBAL_QUANTILES)

    lam = df[c.L_COL].to_numpy(dtype=float)
    ones = np.ones(n)
    rigidity_inverse, rig_floored = safe_ratio(ones, lam, legacy_abs_eps=L.LEGACY_ABS_EPS, eps=c.EPS,
                                               blocks=q_blocks, min_periods=q_min, q=cfg.numeric.SAFE_RATIO_Q,
                                               legacy_fill_zero=False)
    det_inverse, det_floored = safe_ratio(ones, b["g_det"], legacy_abs_eps=L.LEGACY_ABS_EPS, eps=c.EPS,
                                          blocks=q_blocks, min_periods=q_min, q=cfg.numeric.SAFE_RATIO_Q,
                                          legacy_fill_zero=False)
    g_inv_norm = np.sqrt(b["g_inv_ee"] ** 2 + 2.0 * b["g_inv_ej"] ** 2 + b["g_inv_jj"] ** 2)
    gamma_norm = sum(np.abs(b[k]) for k in gamma_names)
    curvature_abs = np.abs(b["field_curvature"])
    curvature_scalar_abs = np.abs(b["field_curvature_scalar"])
    einstein_norm_abs = np.abs(b["field_einstein_norm"])
    gravity_abs = np.abs(b["field_gravity"])
    grav_stress_abs = np.abs(b["gravitational_stress_score"])
    stress_energy_raw = (nz(b["field_stress_geodesic"]) + nz(b["geom_incoherence_abs"]) + nz(b["geo_resid_norm"])
                         + nz(b["field_stress_tensor_norm"]) + nz(grav_stress_abs))
    memory_flux_abs = np.abs(b["memory_flux"])

    comp = {
        "rigidity_log": lg(rigidity_inverse),
        "det_log": lg(det_inverse),
        "ginv_log": lg(g_inv_norm),
        "gamma_log": lg(gamma_norm),
        "curvature_log": lg(curvature_abs),
        "curvature_scalar_log": lg(curvature_scalar_abs),
        "einstein_log": lg(einstein_norm_abs),
        "gravity_log": lg(gravity_abs),
        "grav_stress_log": lg(grav_stress_abs),
        "stress_log": lg(stress_energy_raw),
        "geo_resid_log": lg(nz(b["geo_resid_norm"])),
        "memory_flux_log": lg(nz(memory_flux_abs)),
        "jerk_lambda_log": lg(nz(b["jerk_over_lambda"])),
        "grad_phi_log": lg(nz(b["grad_phi_norm"])),
    }
    gi_log = lg(nz(b["geom_incoherence_abs"]))

    rig = 0.60 * comp["rigidity_log"] + 0.25 * comp["jerk_lambda_log"] + 0.15 * comp["memory_flux_log"]
    curv = (0.15 * comp["det_log"] + 0.10 * comp["ginv_log"] + 0.15 * comp["gamma_log"]
            + 0.20 * comp["curvature_log"] + 0.20 * comp["curvature_scalar_log"] + 0.20 * comp["einstein_log"])
    stress = (0.30 * comp["stress_log"] + 0.20 * gi_log + 0.15 * comp["geo_resid_log"]
              + 0.10 * comp["grad_phi_log"] + 0.10 * lg(nz(b["field_stress_geodesic"]))
              + 0.15 * lg(nz(b["field_stress_tensor_norm"])))
    grav = (0.35 * comp["gravity_log"] + 0.25 * comp["einstein_log"] + 0.20 * comp["grav_stress_log"]
            + 0.20 * comp["curvature_scalar_log"])
    sing = np.clip(0.90 * rig + 1.00 * curv + 1.00 * stress + 1.10 * grav
                   + 0.20 * lg(nz(b["rupture_prob_geodesic"])), -c.MAX_SCORE, c.MAX_SCORE)
    crit = np.clip(0.20 * comp["rigidity_log"] + 0.20 * gi_log + 0.15 * comp["curvature_log"]
                   + 0.15 * comp["curvature_scalar_log"] + 0.10 * comp["grad_phi_log"]
                   + 0.10 * comp["geo_resid_log"] + 0.10 * comp["memory_flux_log"], -c.MAX_SCORE, c.MAX_SCORE)

    # z / minmax / prob: o original aplica a score.fillna(0)
    sing_in = nz(sing) if L.LEGACY_ZERO_FILL else sing
    crit_in = nz(crit) if L.LEGACY_ZERO_FILL else crit
    sing_z = robust_z_singularity(sing_in, q_blocks, q_min, c.EPS)
    crit_z = robust_z_singularity(crit_in, q_blocks, q_min, c.EPS)
    sing_01 = minmax_robust(sing_in, q_blocks, q_min, c.EPS)
    crit_01 = minmax_robust(crit_in, q_blocks, q_min, c.EPS)
    sing_prob = np.where(np.isfinite(sing_z), sigmoid(np.nan_to_num(sing_z)), np.nan)
    crit_prob = np.where(np.isfinite(crit_z), sigmoid(np.nan_to_num(crit_z)), np.nan)

    qt = lambda v, q: quantile_threshold(v, q_blocks, q, q_min)  # noqa: E731
    alerts = {
        "sgv_singularity_alert_q90": _alert(sing, qt(sing, c.Q_ALERT_90)),
        "sgv_singularity_alert_q95": _alert(sing, qt(sing, c.Q_ALERT_95)),
        "sgv_singularity_alert_q99": _alert(sing, qt(sing, c.Q_ALERT_99)),
        "sgv_criticality_alert_q95": _alert(crit, qt(crit, c.Q_ALERT_95)),
        "sgv_sing_rigidity_alert": _alert(rig, qt(rig, c.Q_ALERT_95)),
        "sgv_sing_curvature_alert": _alert(curv, qt(curv, c.Q_ALERT_95)),
        "sgv_sing_stress_alert": _alert(stress, qt(stress, c.Q_ALERT_95)),
        "sgv_sing_gravity_alert": _alert(grav, qt(grav, c.Q_ALERT_95)),
        "ricci3_alert_q95": _alert(curvature_scalar_abs, qt(curvature_scalar_abs, c.Q_ALERT_95)),
        "gravity_alert_q95": _alert(gravity_abs, qt(gravity_abs, c.Q_ALERT_95)),
        "einstein_alert_q95": _alert(einstein_norm_abs, qt(einstein_norm_abs, c.Q_ALERT_95)),
    }

    # tipo dominante (4.1)
    type_scores = np.column_stack([np.nan_to_num(v, nan=-np.inf) for v in (rig, curv, stress, grav)])
    type_names = np.array(["rigidity", "curvature", "stress", "gravity"])
    max_idx = np.argmax(type_scores, axis=1)
    max_vals = type_scores[np.arange(n), max_idx]
    second_vals = np.partition(type_scores, -2, axis=1)[:, -2] if n else np.array([])
    dominant = type_names[max_idx].astype(object)
    with np.errstate(invalid="ignore", divide="ignore"):
        compound = (second_vals > 0) & (max_vals / np.maximum(second_vals, c.EPS) < c.DOMINANCE_RATIO)
    dominant[compound] = "compound"
    if not L.LEGACY_TYPE_ARGMAX:
        # O score de stress é montado só com componentes preenchidos com zero,
        # então nunca é NaN: numa linha sem dados ele vale 0 e vence o argmax.
        # Sem rigidez, curvatura e gravidade, a linha é "undefined".
        no_data = ~np.isfinite(np.column_stack([rig, curv, grav])).any(axis=1)
        dominant[no_data] = "undefined"

    stage = np.select(
        [alerts["sgv_singularity_alert_q99"] == 1, alerts["sgv_singularity_alert_q95"] == 1,
         alerts["sgv_criticality_alert_q95"] == 1],
        ["singularity_extreme", "singularity", "criticality"],
        default="normal",
    )

    einstein_cols = [col for col in df.columns if str(col).startswith("G_info_") and not str(col).endswith("abs_sum")]
    stress_cols = [col for col in df.columns if str(col).startswith("T_info_") and not str(col).endswith("abs_sum")]
    G_sum = df[einstein_cols].apply(pd.to_numeric, errors="coerce").abs().sum(axis=1).to_numpy() if einstein_cols else np.full(n, np.nan)
    T_sum = df[stress_cols].apply(pd.to_numeric, errors="coerce").abs().sum(axis=1).to_numpy() if stress_cols else np.full(n, np.nan)

    valid_cols = [c.L_COL, "g_det", "field_curvature", "geo_resid_norm", "field_stress_geodesic",
                  "field_curvature_scalar", "field_einstein_norm", "field_gravity"]
    valid = np.ones(n, dtype=bool)
    for col in valid_cols:
        valid &= np.isfinite(_col(df, col))
    if not L.LEGACY_ZERO_FILL:
        for col in ("geodesic_valid", "info_valid"):           # 4.8
            if col in df.columns:
                valid &= pd.to_numeric(df[col], errors="coerce").fillna(0).to_numpy() > 0
        valid &= np.isfinite(sing)

    cols: dict[str, Any] = {
        "g_det": b["g_det"], "g_inv_ee": b["g_inv_ee"], "g_inv_ej": b["g_inv_ej"], "g_inv_jj": b["g_inv_jj"],
        "field_curvature": b["field_curvature"], "geo_resid_norm": b["geo_resid_norm"],
        "field_stress_geodesic": b["field_stress_geodesic"], "geom_incoherence_abs": b["geom_incoherence_abs"],
        "grad_phi_norm": b["grad_phi_norm"], "jerk_over_lambda": b["jerk_over_lambda"],
        "rupture_prob_geodesic": b["rupture_prob_geodesic"],
        **{k: b[k] for k in gamma_names},
        "field_curvature_scalar": b["field_curvature_scalar"], "field_stress_tensor_norm": b["field_stress_tensor_norm"],
        "field_einstein_norm": b["field_einstein_norm"], "field_gravity": b["field_gravity"],
        "gravitational_stress_score": b["gravitational_stress_score"], "memory_flux": b["memory_flux"],
        "rigidity_inverse": rigidity_inverse, "det_inverse": det_inverse, "g_inv_norm": g_inv_norm,
        "gamma_norm": gamma_norm, "curvature_abs": curvature_abs, "curvature_scalar_abs": curvature_scalar_abs,
        "einstein_norm_abs": einstein_norm_abs, "gravity_abs": gravity_abs, "grav_stress_abs": grav_stress_abs,
        "stress_energy_raw": stress_energy_raw, "memory_flux_abs": memory_flux_abs,
        **comp,
        "sgv_sing_rigidity_score": rig, "sgv_sing_curvature_score": curv,
        "sgv_sing_stress_score": stress, "sgv_sing_gravity_score": grav,
        "sgv_singularity_score": sing, "sgv_singularity_score_z": sing_z,
        "sgv_singularity_score_01": sing_01, "sgv_singularity_prob": sing_prob,
        "sgv_criticality_score": crit, "sgv_criticality_score_z": crit_z,
        "sgv_criticality_score_01": crit_01, "sgv_criticality_prob": crit_prob,
        **alerts,
        "sgv_singularity_type": dominant, "sgv_stage": stage,
        "G_info_abs_sum": G_sum, "T_info_abs_sum": T_sum,
        "sgv_singularity_valid": valid.astype(int),
        # novos
        "rigidity_floored": rig_floored, "det_floored": det_floored,
    }
    out = assign_columns(df, cols)

    # monitor da taxa realizada de alertas (4.3)
    w = cfg.causal.W_QUANTILE
    mp = 1 if L.LEGACY_GLOBAL_QUANTILES else min(cfg.causal.MIN_QUANTILE, w)
    rate = pd.Series(alerts["sgv_singularity_alert_q95"], dtype=float).rolling(w, min_periods=mp).mean().to_numpy()
    out = assign_columns(out, {"alert_rate_realized": rate})

    # diagnóstico de redundância (4.6)
    comp_df = pd.DataFrame(comp)
    corr = comp_df.corr(method="spearman") if n > 2 else pd.DataFrame()
    add_meta(out, "singularity_component_spearman", corr.round(4).to_dict() if not corr.empty else {})
    add_meta(out, "singularity_alert_rate_q95", float(np.mean(alerts["sgv_singularity_alert_q95"])) if n else None)

    if L.LEGACY_ZERO_FILL:
        out = legacy_fill_zero(out, FILL_ZERO_COLS)
    return out
