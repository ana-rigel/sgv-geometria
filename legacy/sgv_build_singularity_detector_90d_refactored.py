from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# ==========================================
# CONFIG
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

INPUT = SCRIPTS_DIR / "sgv_geodesic_field_full_90d.csv"
OUTPUT = SCRIPTS_DIR / "sgv_singularity_field_90d.csv"

# colunas principais
L_COL = "lambda_dynamic"

# estabilidade numérica
EPS = 1e-9

# quantis para alertas
Q_ALERT_90 = 0.90
Q_ALERT_95 = 0.95
Q_ALERT_99 = 0.99

# clipping defensivo
MAX_LOG_COMPONENT = 50.0
MAX_SCORE = 1e6

# dominância para classificar tipo
DOMINANCE_RATIO = 1.12


# ==========================================
# HELPERS
# ==========================================

def safe_series(df: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce")
        return s.replace([np.inf, -np.inf], np.nan)
    return pd.Series(default, index=df.index, dtype=float)


def sigmoid(x: np.ndarray | pd.Series) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    x_arr = np.clip(x_arr, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-x_arr))


def log1p_safe(x: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    arr = np.where(np.isnan(arr), np.nan, np.maximum(arr, 0.0))
    out = np.log1p(arr)
    return np.clip(out, 0.0, MAX_LOG_COMPONENT)


def robust_zscore(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)

    med = s.median()
    mad = (s - med).abs().median()

    scale = 1.4826 * mad if pd.notna(mad) and mad > 0 else s.std(ddof=0)
    if pd.isna(scale) or scale < EPS:
        scale = 1.0

    return (s - med) / scale


def minmax_robust(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)

    q05 = s.quantile(0.05)
    q95 = s.quantile(0.95)
    denom = q95 - q05

    if pd.isna(denom) or abs(denom) < EPS:
        return pd.Series(0.0, index=s.index, dtype=float)

    out = (s - q05) / denom
    return out.clip(lower=0.0, upper=1.0)


def safe_quantile_threshold(s: pd.Series, q: float) -> float:
    s_num = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)
    if s_num.notna().sum() == 0:
        return np.nan
    return float(s_num.quantile(q))


def prepare_input_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.replace([np.inf, -np.inf], np.nan)

    if L_COL not in out.columns:
        raise ValueError(f"Coluna obrigatória faltando: {L_COL}")

    out[L_COL] = pd.to_numeric(out[L_COL], errors="coerce")

    return out


# ==========================================
# MAIN FUNCTION
# ==========================================

def build_singularity_detector_90d(df: pd.DataFrame) -> pd.DataFrame:
    df = prepare_input_dataframe(df)

    # --------------------------------------
    # BASE 2D
    # --------------------------------------
    df["g_det"] = safe_series(df, "g_det")
    df["g_inv_ee"] = safe_series(df, "g_inv_ee")
    df["g_inv_ej"] = safe_series(df, "g_inv_ej")
    df["g_inv_jj"] = safe_series(df, "g_inv_jj")

    df["field_curvature"] = safe_series(df, "field_curvature")
    df["geo_resid_norm"] = safe_series(df, "geo_resid_norm")
    df["field_stress_geodesic"] = safe_series(df, "field_stress_geodesic")
    df["geom_incoherence_abs"] = safe_series(df, "geom_incoherence_abs")
    df["grad_phi_norm"] = safe_series(df, "grad_phi_norm")
    df["jerk_over_lambda"] = safe_series(df, "jerk_over_lambda")
    df["rupture_prob_geodesic"] = safe_series(df, "rupture_prob_geodesic")

    gamma_cols = [
        "gamma_e_ee", "gamma_e_ej", "gamma_e_jj",
        "gamma_j_ee", "gamma_j_ej", "gamma_j_jj",
    ]
    for c in gamma_cols:
        df[c] = safe_series(df, c, default=0.0)

    # --------------------------------------
    # BASE 3D
    # --------------------------------------
    df["field_curvature_scalar"] = safe_series(df, "field_curvature_scalar")
    df["field_stress_tensor_norm"] = safe_series(df, "field_stress_tensor_norm")
    df["field_einstein_norm"] = safe_series(df, "field_einstein_norm")
    df["field_gravity"] = safe_series(df, "field_gravity")
    df["gravitational_stress_score"] = safe_series(df, "gravitational_stress_score")
    df["memory_flux"] = safe_series(df, "memory_flux")

    # componentes do tensor de Einstein e stress-energia podem existir ou não
    einstein_cols = [c for c in df.columns if str(c).startswith("G_info_")]
    stress_tensor_cols = [c for c in df.columns if str(c).startswith("T_info_")]

    # --------------------------------------
    # COMPONENTES FUNDAMENTAIS
    # --------------------------------------
    # 1) Rigidez: lambda -> 0
    lambda_abs = df[L_COL].abs()
    df["rigidity_inverse"] = 1.0 / (lambda_abs + EPS)

    # 2) Degeneração da métrica 2D
    df["det_inverse"] = 1.0 / (df["g_det"].abs() + EPS)

    # 3) Explosão da inversa da métrica 2D
    df["g_inv_norm"] = np.sqrt(
        (df["g_inv_ee"] ** 2)
        + 2.0 * (df["g_inv_ej"] ** 2)
        + (df["g_inv_jj"] ** 2)
    )

    # 4) Explosão da conexão 2D
    df["gamma_norm"] = (
        df["gamma_e_ee"].abs()
        + df["gamma_e_ej"].abs()
        + df["gamma_e_jj"].abs()
        + df["gamma_j_ee"].abs()
        + df["gamma_j_ej"].abs()
        + df["gamma_j_jj"].abs()
    )

    # 5) Curvatura 2D
    df["curvature_abs"] = df["field_curvature"].abs()

    # 6) Curvatura escalar 3D
    df["curvature_scalar_abs"] = df["field_curvature_scalar"].abs()

    # 7) Einstein / gravidade
    df["einstein_norm_abs"] = df["field_einstein_norm"].abs()
    df["gravity_abs"] = df["field_gravity"].abs()
    df["grav_stress_abs"] = df["gravitational_stress_score"].abs()

    # 8) Stress composto
    df["stress_energy_raw"] = (
        df["field_stress_geodesic"].fillna(0.0)
        + df["geom_incoherence_abs"].fillna(0.0)
        + df["geo_resid_norm"].fillna(0.0)
        + df["field_stress_tensor_norm"].fillna(0.0)
        + df["grav_stress_abs"].fillna(0.0)
    )

    # 9) Fluxo de memória
    df["memory_flux_abs"] = df["memory_flux"].abs()

    # --------------------------------------
    # LOG COMPONENTS
    # --------------------------------------
    df["rigidity_log"] = log1p_safe(df["rigidity_inverse"])
    df["det_log"] = log1p_safe(df["det_inverse"])
    df["ginv_log"] = log1p_safe(df["g_inv_norm"])
    df["gamma_log"] = log1p_safe(df["gamma_norm"])
    df["curvature_log"] = log1p_safe(df["curvature_abs"])
    df["curvature_scalar_log"] = log1p_safe(df["curvature_scalar_abs"])
    df["einstein_log"] = log1p_safe(df["einstein_norm_abs"])
    df["gravity_log"] = log1p_safe(df["gravity_abs"])
    df["grav_stress_log"] = log1p_safe(df["grav_stress_abs"])
    df["stress_log"] = log1p_safe(df["stress_energy_raw"])
    df["geo_resid_log"] = log1p_safe(df["geo_resid_norm"].fillna(0.0))
    df["memory_flux_log"] = log1p_safe(df["memory_flux_abs"].fillna(0.0))
    df["jerk_lambda_log"] = log1p_safe(df["jerk_over_lambda"].fillna(0.0))
    df["grad_phi_log"] = log1p_safe(df["grad_phi_norm"].fillna(0.0))

    # --------------------------------------
    # SCORES POR TIPO
    # --------------------------------------
    # Rigidez
    df["sgv_sing_rigidity_score"] = (
        0.60 * df["rigidity_log"]
        + 0.25 * df["jerk_lambda_log"]
        + 0.15 * df["memory_flux_log"]
    )

    # Curvatura / geometria
    df["sgv_sing_curvature_score"] = (
        0.15 * df["det_log"]
        + 0.10 * df["ginv_log"]
        + 0.15 * df["gamma_log"]
        + 0.20 * df["curvature_log"]
        + 0.20 * df["curvature_scalar_log"]
        + 0.20 * df["einstein_log"]
    )

    # Stress / energia
    df["sgv_sing_stress_score"] = (
        0.30 * df["stress_log"]
        + 0.20 * log1p_safe(df["geom_incoherence_abs"].fillna(0.0))
        + 0.15 * df["geo_resid_log"]
        + 0.10 * df["grad_phi_log"]
        + 0.10 * log1p_safe(df["field_stress_geodesic"].fillna(0.0))
        + 0.15 * log1p_safe(df["field_stress_tensor_norm"].fillna(0.0))
    )

    # Gravidade / colapso profundo do campo
    df["sgv_sing_gravity_score"] = (
        0.35 * df["gravity_log"]
        + 0.25 * df["einstein_log"]
        + 0.20 * df["grav_stress_log"]
        + 0.20 * df["curvature_scalar_log"]
    )

    # --------------------------------------
    # SCORE COMPOSTO GERAL
    # --------------------------------------
    df["sgv_singularity_score"] = (
        0.90 * df["sgv_sing_rigidity_score"]
        + 1.00 * df["sgv_sing_curvature_score"]
        + 1.00 * df["sgv_sing_stress_score"]
        + 1.10 * df["sgv_sing_gravity_score"]
        + 0.20 * log1p_safe(df["rupture_prob_geodesic"].fillna(0.0))
    ).clip(-MAX_SCORE, MAX_SCORE)

    df["sgv_singularity_score_z"] = robust_zscore(df["sgv_singularity_score"].fillna(0.0))
    df["sgv_singularity_score_01"] = minmax_robust(df["sgv_singularity_score"].fillna(0.0))
    df["sgv_singularity_prob"] = sigmoid(df["sgv_singularity_score_z"])

    # --------------------------------------
    # CRITICALITY SCORE
    # --------------------------------------
    df["sgv_criticality_score"] = (
        0.20 * df["rigidity_log"]
        + 0.20 * log1p_safe(df["geom_incoherence_abs"].fillna(0.0))
        + 0.15 * df["curvature_log"]
        + 0.15 * df["curvature_scalar_log"]
        + 0.10 * df["grad_phi_log"]
        + 0.10 * df["geo_resid_log"]
        + 0.10 * df["memory_flux_log"]
    ).clip(-MAX_SCORE, MAX_SCORE)

    df["sgv_criticality_score_z"] = robust_zscore(df["sgv_criticality_score"].fillna(0.0))
    df["sgv_criticality_score_01"] = minmax_robust(df["sgv_criticality_score"].fillna(0.0))
    df["sgv_criticality_prob"] = sigmoid(df["sgv_criticality_score_z"])

    # --------------------------------------
    # ALERTAS
    # --------------------------------------
    q90 = safe_quantile_threshold(df["sgv_singularity_score"], Q_ALERT_90)
    q95 = safe_quantile_threshold(df["sgv_singularity_score"], Q_ALERT_95)
    q99 = safe_quantile_threshold(df["sgv_singularity_score"], Q_ALERT_99)

    df["sgv_singularity_alert_q90"] = (df["sgv_singularity_score"] >= q90).astype(int)
    df["sgv_singularity_alert_q95"] = (df["sgv_singularity_score"] >= q95).astype(int)
    df["sgv_singularity_alert_q99"] = (df["sgv_singularity_score"] >= q99).astype(int)

    q95_c = safe_quantile_threshold(df["sgv_criticality_score"], Q_ALERT_95)
    df["sgv_criticality_alert_q95"] = (df["sgv_criticality_score"] >= q95_c).astype(int)

    # por tipo
    q95_rig = safe_quantile_threshold(df["sgv_sing_rigidity_score"], Q_ALERT_95)
    q95_curv = safe_quantile_threshold(df["sgv_sing_curvature_score"], Q_ALERT_95)
    q95_stress = safe_quantile_threshold(df["sgv_sing_stress_score"], Q_ALERT_95)
    q95_grav = safe_quantile_threshold(df["sgv_sing_gravity_score"], Q_ALERT_95)

    df["sgv_sing_rigidity_alert"] = (df["sgv_sing_rigidity_score"] >= q95_rig).astype(int)
    df["sgv_sing_curvature_alert"] = (df["sgv_sing_curvature_score"] >= q95_curv).astype(int)
    df["sgv_sing_stress_alert"] = (df["sgv_sing_stress_score"] >= q95_stress).astype(int)
    df["sgv_sing_gravity_alert"] = (df["sgv_sing_gravity_score"] >= q95_grav).astype(int)

    # alertas específicos úteis
    q95_ricci3 = safe_quantile_threshold(df["curvature_scalar_abs"], Q_ALERT_95)
    q95_gravity = safe_quantile_threshold(df["gravity_abs"], Q_ALERT_95)
    q95_einstein = safe_quantile_threshold(df["einstein_norm_abs"], Q_ALERT_95)

    df["ricci3_alert_q95"] = (df["curvature_scalar_abs"] >= q95_ricci3).astype(int)
    df["gravity_alert_q95"] = (df["gravity_abs"] >= q95_gravity).astype(int)
    df["einstein_alert_q95"] = (df["einstein_norm_abs"] >= q95_einstein).astype(int)

    # --------------------------------------
    # TIPO DOMINANTE
    # --------------------------------------
    type_scores = np.column_stack([
        df["sgv_sing_rigidity_score"].fillna(-np.inf).to_numpy(),
        df["sgv_sing_curvature_score"].fillna(-np.inf).to_numpy(),
        df["sgv_sing_stress_score"].fillna(-np.inf).to_numpy(),
        df["sgv_sing_gravity_score"].fillna(-np.inf).to_numpy(),
    ])
    type_names = np.array(["rigidity", "curvature", "stress", "gravity"])

    max_idx = np.argmax(type_scores, axis=1)
    max_vals = type_scores[np.arange(len(df)), max_idx]
    second_vals = np.partition(type_scores, -2, axis=1)[:, -2]

    dominant = type_names[max_idx].astype(object)
    compound_mask = second_vals > 0
    compound_mask &= (max_vals / np.maximum(second_vals, EPS) < DOMINANCE_RATIO)
    dominant[compound_mask] = "compound"

    df["sgv_singularity_type"] = dominant

    # --------------------------------------
    # FLAGS DE ESTÁGIO
    # --------------------------------------
    df["sgv_stage"] = np.where(
        df["sgv_singularity_alert_q99"] == 1,
        "singularity_extreme",
        np.where(
            df["sgv_singularity_alert_q95"] == 1,
            "singularity",
            np.where(
                df["sgv_criticality_alert_q95"] == 1,
                "criticality",
                "normal"
            )
        )
    )

    # --------------------------------------
    # RESUMOS TENSORIAIS OPCIONAIS
    # --------------------------------------
    if einstein_cols:
        df["G_info_abs_sum"] = df[einstein_cols].apply(pd.to_numeric, errors="coerce").abs().sum(axis=1)
    else:
        df["G_info_abs_sum"] = np.nan

    if stress_tensor_cols:
        df["T_info_abs_sum"] = df[stress_tensor_cols].apply(pd.to_numeric, errors="coerce").abs().sum(axis=1)
    else:
        df["T_info_abs_sum"] = np.nan

    # --------------------------------------
    # VALID FLAG
    # --------------------------------------
    valid_cols = [
        L_COL,
        "g_det",
        "field_curvature",
        "geo_resid_norm",
        "field_stress_geodesic",
        "field_curvature_scalar",
        "field_einstein_norm",
        "field_gravity",
    ]
    df["sgv_singularity_valid"] = (~df[valid_cols].isna().any(axis=1)).astype(int)

    # --------------------------------------
    # HARDENING FINAL PARA LIVE
    # --------------------------------------
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)

    fill_zero_cols = [
        "rigidity_inverse",
        "det_inverse",
        "g_inv_norm",
        "gamma_norm",
        "curvature_abs",
        "curvature_scalar_abs",
        "einstein_norm_abs",
        "gravity_abs",
        "grav_stress_abs",
        "stress_energy_raw",
        "memory_flux_abs",
        "rigidity_log",
        "det_log",
        "ginv_log",
        "gamma_log",
        "curvature_log",
        "curvature_scalar_log",
        "einstein_log",
        "gravity_log",
        "grav_stress_log",
        "stress_log",
        "geo_resid_log",
        "memory_flux_log",
        "jerk_lambda_log",
        "grad_phi_log",
        "sgv_sing_rigidity_score",
        "sgv_sing_curvature_score",
        "sgv_sing_stress_score",
        "sgv_sing_gravity_score",
        "sgv_singularity_score",
        "sgv_singularity_score_z",
        "sgv_singularity_score_01",
        "sgv_singularity_prob",
        "sgv_criticality_score",
        "sgv_criticality_score_z",
        "sgv_criticality_score_01",
        "sgv_criticality_prob",
        "sgv_singularity_alert_q90",
        "sgv_singularity_alert_q95",
        "sgv_singularity_alert_q99",
        "sgv_criticality_alert_q95",
        "sgv_sing_rigidity_alert",
        "sgv_sing_curvature_alert",
        "sgv_sing_stress_alert",
        "sgv_sing_gravity_alert",
        "ricci3_alert_q95",
        "gravity_alert_q95",
        "einstein_alert_q95",
        "G_info_abs_sum",
        "T_info_abs_sum",
        "sgv_singularity_valid",
    ]

    for col in fill_zero_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0.0)

    return df


# ==========================================
# DEBUG / LOCAL
# ==========================================

def main() -> None:
    print("=" * 72)
    print("SGV SINGULARITY DETECTOR 3D-AWARE")
    print("=" * 72)
    print("entrada :", INPUT)
    print("saida   :", OUTPUT)

    if not INPUT.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT}")

    raw_df = pd.read_csv(INPUT)
    out = build_singularity_detector_90d(raw_df)

    print("\nResumo dos principais scores:")
    summary_cols = [
        "sgv_sing_rigidity_score",
        "sgv_sing_curvature_score",
        "sgv_sing_stress_score",
        "sgv_sing_gravity_score",
        "sgv_singularity_score",
        "sgv_singularity_prob",
        "sgv_criticality_score",
        "sgv_criticality_prob",
    ]
    summary_cols = [c for c in summary_cols if c in out.columns]
    print(out[summary_cols].describe().T[["mean", "std", "min", "max"]].round(6))

    if "sgv_singularity_score" in out.columns:
        print("\nQuantis do singularity_score:")
        print(out["sgv_singularity_score"].quantile([0.50, 0.75, 0.90, 0.95, 0.99]).round(6))

    if "sgv_singularity_type" in out.columns:
        print("\nDistribuição por tipo dominante:")
        print(out["sgv_singularity_type"].value_counts(dropna=False))

    if "sgv_stage" in out.columns:
        print("\nDistribuição por estágio:")
        print(out["sgv_stage"].value_counts(dropna=False))

    out.to_csv(OUTPUT, index=False)

    print("\nArquivo salvo com sucesso.")
    print("saida:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()