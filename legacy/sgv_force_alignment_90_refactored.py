from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

INPUT_TERRAIN = SCRIPTS_DIR / "sgv_terrain_layer_v1_90d.csv"
INPUT_FORCE = SCRIPTS_DIR / "sgv_force_field_map_90d.csv"

OUTPUT_DETAIL = SCRIPTS_DIR / "sgv_force_alignment_detail_90d.csv"
OUTPUT_SUMMARY = SCRIPTS_DIR / "sgv_force_alignment_summary_90d.csv"

E_COL = "E_norm"
J_COL = "jerk"

EPS = 1e-12
FORCE_Q_LOW = 0.01
FORCE_Q_HIGH = 0.99


# =========================================================
# HELPERS
# =========================================================

def nearest_index(sorted_vals: np.ndarray, v: float) -> int:
    idx = np.searchsorted(sorted_vals, v)

    if idx <= 0:
        return 0
    if idx >= len(sorted_vals):
        return len(sorted_vals) - 1

    left = sorted_vals[idx - 1]
    right = sorted_vals[idx]

    if abs(v - left) <= abs(v - right):
        return idx - 1
    return idx


def robust_stats(x: pd.Series, prefix: str) -> dict:
    vals = pd.to_numeric(x, errors="coerce")
    vals = vals.replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)

    if len(vals) == 0:
        return {
            f"{prefix}_count": 0,
            f"{prefix}_mean": np.nan,
            f"{prefix}_median": np.nan,
            f"{prefix}_std": np.nan,
            f"{prefix}_p05": np.nan,
            f"{prefix}_p25": np.nan,
            f"{prefix}_p75": np.nan,
            f"{prefix}_p95": np.nan,
        }

    return {
        f"{prefix}_count": len(vals),
        f"{prefix}_mean": float(np.mean(vals)),
        f"{prefix}_median": float(np.median(vals)),
        f"{prefix}_std": float(np.std(vals)),
        f"{prefix}_p05": float(np.quantile(vals, 0.05)),
        f"{prefix}_p25": float(np.quantile(vals, 0.25)),
        f"{prefix}_p75": float(np.quantile(vals, 0.75)),
        f"{prefix}_p95": float(np.quantile(vals, 0.95)),
    }


def prepare_terrain_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    required_terrain = [E_COL, J_COL]
    missing_terrain = [c for c in required_terrain if c not in out.columns]
    if missing_terrain:
        raise ValueError(f"Colunas faltando no terrain: {missing_terrain}")

    out[E_COL] = pd.to_numeric(out[E_COL], errors="coerce")
    out[J_COL] = pd.to_numeric(out[J_COL], errors="coerce")

    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=[E_COL, J_COL]).reset_index(drop=True)

    if len(out) < 10:
        raise ValueError("Poucos dados válidos no terrain.")

    return out


def prepare_force_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    required_force = ["E", "jerk", "force_x", "force_y", "force_magnitude"]
    missing_force = [c for c in required_force if c not in out.columns]
    if missing_force:
        raise ValueError(f"Colunas faltando no force map: {missing_force}")

    for col in required_force:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=required_force).reset_index(drop=True)

    if out.empty:
        raise ValueError("Force map vazio após limpeza.")

    return out


# =========================================================
# MAIN FUNCTION
# =========================================================

def build_force_alignment_90(
    terrain_df: pd.DataFrame,
    force_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    terrain = prepare_terrain_dataframe(terrain_df)
    force = prepare_force_dataframe(force_df)

    work = terrain.copy()

    # movimento retrospectivo (live-safe: preserva última barra)
    work["dE_real"] = work[E_COL].diff()
    work["dJ_real"] = work[J_COL].diff()
    work["real_move_mag"] = np.sqrt(work["dE_real"] ** 2 + work["dJ_real"] ** 2)
    work["dE_real"] = work["dE_real"].fillna(0.0)
    work["dJ_real"] = work["dJ_real"].fillna(0.0)
    work["real_move_mag"] = work["real_move_mag"].fillna(0.0)

    grid_E = np.sort(force["E"].unique())
    grid_J = np.sort(force["jerk"].unique())

    if len(grid_E) == 0 or len(grid_J) == 0:
        raise ValueError("Grid do force map inválido.")

    fx_pivot = force.pivot(index="jerk", columns="E", values="force_x").sort_index().sort_index(axis=1)
    fy_pivot = force.pivot(index="jerk", columns="E", values="force_y").sort_index().sort_index(axis=1)
    fm_pivot = force.pivot(index="jerk", columns="E", values="force_magnitude").sort_index().sort_index(axis=1)

    fx_vals = fx_pivot.to_numpy(dtype=float)
    fy_vals = fy_pivot.to_numpy(dtype=float)
    fm_vals = fm_pivot.to_numpy(dtype=float)

    e_cols = fx_pivot.columns.to_numpy(dtype=float)
    j_rows = fx_pivot.index.to_numpy(dtype=float)

    force_x_list: list[float] = []
    force_y_list: list[float] = []
    force_mag_list: list[float] = []
    cos_list: list[float] = []
    dot_list: list[float] = []

    for _, row in work.iterrows():
        e = float(row[E_COL])
        j = float(row[J_COL])

        ie = nearest_index(e_cols, e)
        ij = nearest_index(j_rows, j)

        fx = float(fx_vals[ij, ie])
        fy = float(fy_vals[ij, ie])
        fm = float(fm_vals[ij, ie])

        dx = float(row["dE_real"])
        dy = float(row["dJ_real"])
        dm = float(row["real_move_mag"])

        dot = fx * dx + fy * dy
        denom = fm * dm

        if denom <= EPS:
            cos_theta = np.nan
        else:
            cos_theta = dot / denom
            cos_theta = max(-1.0, min(1.0, cos_theta))

        force_x_list.append(fx)
        force_y_list.append(fy)
        force_mag_list.append(fm)
        dot_list.append(dot)
        cos_list.append(cos_theta)

    work["force_x_local"] = pd.Series(force_x_list, index=work.index, dtype=float)
    work["force_y_local"] = pd.Series(force_y_list, index=work.index, dtype=float)
    work["force_mag_local"] = pd.Series(force_mag_list, index=work.index, dtype=float)
    work["force_dot_move"] = pd.Series(dot_list, index=work.index, dtype=float)
    work["force_alignment_cos"] = pd.Series(cos_list, index=work.index, dtype=float)
    work["force_alignment_cos_raw"] = work["force_alignment_cos"].copy()

    q_lo = float(work["force_mag_local"].quantile(FORCE_Q_LOW))
    q_hi = float(work["force_mag_local"].quantile(FORCE_Q_HIGH))

    work["force_mag_inlier"] = (
        (work["force_mag_local"] >= q_lo) &
        (work["force_mag_local"] <= q_hi)
    ).astype(int)

    work["force_alignment_valid"] = (
        work["force_alignment_cos"].notna() &
        (work["real_move_mag"] > EPS)
    ).astype(int)

    work["force_alignment_low_confidence"] = work["force_mag_inlier"].eq(0).astype(int)

    work["force_alignment_cos_live"] = work["force_alignment_cos"].where(
        work["force_mag_inlier"].eq(1), 0.0
    )
    work["force_alignment_cos_live"] = work["force_alignment_cos_live"].fillna(0.0)

    work["aligned_positive"] = (work["force_alignment_cos_live"] > 0).astype(int)
    work["aligned_strong"] = (work["force_alignment_cos_live"] > 0.25).astype(int)
    work["aligned_very_strong"] = (work["force_alignment_cos_live"] > 0.50).astype(int)
    work["anti_aligned"] = (work["force_alignment_cos_live"] < 0).astype(int)

    numeric_cols = work.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        work[col] = pd.to_numeric(work[col], errors="coerce")
        work[col] = work[col].replace([np.inf, -np.inf], np.nan)

    summary = {
        "rows_total": len(work),
        "rows_filtered": len(work),  # live-safe: não reduz cardinalidade
        "force_mag_q01": q_lo,
        "force_mag_q99": q_hi,
        "share_positive_alignment": float(work["aligned_positive"].mean()) if len(work) else np.nan,
        "share_strong_alignment": float(work["aligned_strong"].mean()) if len(work) else np.nan,
        "share_very_strong_alignment": float(work["aligned_very_strong"].mean()) if len(work) else np.nan,
        "share_anti_alignment": float(work["anti_aligned"].mean()) if len(work) else np.nan,
    }

    summary.update(robust_stats(work["force_alignment_cos_live"], "cos"))
    summary.update(robust_stats(work["force_dot_move"], "dot"))
    summary.update(robust_stats(work["force_mag_local"], "force_mag"))
    summary.update(robust_stats(work["real_move_mag"], "move_mag"))

    summary_df = pd.DataFrame([summary])

    return work, summary_df


# =========================================================
# DEBUG / LOCAL
# =========================================================

def main() -> None:
    print("=" * 72)
    print("SGV TEST FORCE ALIGNMENT")
    print("=" * 72)
    print("entrada terrain :", INPUT_TERRAIN)
    print("entrada force   :", INPUT_FORCE)
    print("saida detail    :", OUTPUT_DETAIL)
    print("saida summary   :", OUTPUT_SUMMARY)

    if not INPUT_TERRAIN.exists():
        raise FileNotFoundError(f"Arquivo terrain não encontrado: {INPUT_TERRAIN}")
    if not INPUT_FORCE.exists():
        raise FileNotFoundError(f"Arquivo force não encontrado: {INPUT_FORCE}")

    terrain = pd.read_csv(INPUT_TERRAIN)
    force = pd.read_csv(INPUT_FORCE)

    aligned, summary_df = build_force_alignment_90(terrain, force)

    aligned.to_csv(OUTPUT_DETAIL, index=False)
    summary_df.to_csv(OUTPUT_SUMMARY, index=False)

    summary = summary_df.iloc[0].to_dict()

    print("\nResumo:")
    print(f"linhas totais                    : {int(summary['rows_total'])}")
    print(f"linhas após filtro robusto       : {int(summary['rows_filtered'])}")
    print(f"force magnitude q01              : {summary['force_mag_q01']:.6f}")
    print(f"force magnitude q99              : {summary['force_mag_q99']:.6f}")
    print(f"share positive alignment         : {summary['share_positive_alignment']:.4%}")
    print(f"share strong alignment (>0.25)   : {summary['share_strong_alignment']:.4%}")
    print(f"share very strong (>0.50)        : {summary['share_very_strong_alignment']:.4%}")
    print(f"share anti alignment             : {summary['share_anti_alignment']:.4%}")
    print(f"cos mean                         : {summary['cos_mean']:.6f}")
    print(f"cos median                       : {summary['cos_median']:.6f}")
    print(f"cos p05                          : {summary['cos_p05']:.6f}")
    print(f"cos p95                          : {summary['cos_p95']:.6f}")

    print("\nArquivos salvos com sucesso.")


if __name__ == "__main__":
    main()
