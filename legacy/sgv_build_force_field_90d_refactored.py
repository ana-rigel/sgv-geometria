from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

INPUT = SCRIPTS_DIR / "sgv_terrain_layer_v1_90d.csv"
OUTPUT = SCRIPTS_DIR / "sgv_force_field_map_90d.csv"

EPS = 1e-9

# grid
GRID_SIZE = 40

# janela de suavização
WINDOW = 200


# =========================================================
# HELPERS
# =========================================================

def safe_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def build_grid(series: pd.Series, size: int) -> np.ndarray:
    s = safe_numeric(series).dropna()

    if len(s) == 0:
        return np.linspace(-1, 1, size)

    return np.linspace(s.min(), s.max(), size)


def compute_gradients(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["dE"] = safe_numeric(df["E_norm"]).diff()
    df["dJ"] = safe_numeric(df["jerk"]).diff()

    return df


def compute_force_components(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # força proporcional ao deslocamento
    df["force_x"] = safe_numeric(df["dE"])
    df["force_y"] = safe_numeric(df["dJ"])

    df["force_magnitude"] = np.sqrt(
        df["force_x"] ** 2 +
        df["force_y"] ** 2
    )

    return df


def aggregate_on_grid(df: pd.DataFrame, grid_E: np.ndarray, grid_J: np.ndarray) -> pd.DataFrame:
    rows = []

    E_vals = safe_numeric(df["E_norm"])
    J_vals = safe_numeric(df["jerk"])

    for i in range(len(df)):

        e = E_vals.iloc[i]
        j = J_vals.iloc[i]

        if pd.isna(e) or pd.isna(j):
            continue

        ie = np.searchsorted(grid_E, e)
        ij = np.searchsorted(grid_J, j)

        ie = max(0, min(len(grid_E) - 1, ie))
        ij = max(0, min(len(grid_J) - 1, ij))

        rows.append({
            "E": grid_E[ie],
            "jerk": grid_J[ij],
            "force_x": df["force_x"].iloc[i],
            "force_y": df["force_y"].iloc[i],
            "force_magnitude": df["force_magnitude"].iloc[i],
        })

    out = pd.DataFrame(rows)

    if out.empty:
        raise ValueError("Falha ao construir grid de força.")

    # média por célula
    out = (
        out
        .groupby(["E", "jerk"], as_index=False)
        .mean()
    )

    return out


# =========================================================
# MAIN FUNCTION
# =========================================================

def build_force_field_90d(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.replace([np.inf, -np.inf], np.nan)

    # ======================================
    # INPUT CHECK
    # ======================================
    required_cols = ["E_norm", "jerk"]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando: {missing}")

    df["E_norm"] = safe_numeric(df["E_norm"])
    df["jerk"] = safe_numeric(df["jerk"])

    df = df.dropna(subset=["E_norm", "jerk"]).reset_index(drop=True)

    if len(df) < 10:
        raise ValueError("Dados insuficientes para force field.")

    # ======================================
    # GRADIENTES (MOVIMENTO DO CAMPO)
    # ======================================
    df = compute_gradients(df)

    # ======================================
    # COMPONENTES DE FORÇA
    # ======================================
    df = compute_force_components(df)

    # ======================================
    # GRID
    # ======================================
    grid_E = build_grid(df["E_norm"], GRID_SIZE)
    grid_J = build_grid(df["jerk"], GRID_SIZE)

    # ======================================
    # AGREGAÇÃO NO GRID
    # ======================================
    out = aggregate_on_grid(df, grid_E, grid_J)

    # ======================================
    # HARDENING FINAL
    # ======================================
    numeric_cols = out.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        out[col] = safe_numeric(out[col])
        out[col] = out[col].fillna(0.0)

    return out


# =========================================================
# DEBUG / LOCAL
# =========================================================

def main() -> None:
    print("=" * 72)
    print("SGV BUILD FORCE FIELD")
    print("=" * 72)
    print("entrada :", INPUT)
    print("saida   :", OUTPUT)

    if not INPUT.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT}")

    df = pd.read_csv(INPUT)

    out = build_force_field_90d(df)

    print("\nResumo:")
    print("linhas grid:", len(out))
    print(out.describe().T[["mean", "std", "min", "max"]].round(6))

    out.to_csv(OUTPUT, index=False)

    print("\nArquivo salvo:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()