from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

INPUT = SCRIPTS_DIR / "sgv_force_alignment_detail_90d.csv"
OUTPUT = SCRIPTS_DIR / "sgv_edge_signal_90d.csv"

EPS = 1e-9

# thresholds (mantidos)
ALIGNMENT_STRONG = 0.25
ALIGNMENT_VERY_STRONG = 0.50

EV_THRESHOLD = 0.0


# =========================================================
# HELPERS
# =========================================================

def safe_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def safe_bool(cond: pd.Series) -> pd.Series:
    return cond.fillna(False).astype(int)


def build_edge_score(df: pd.DataFrame) -> pd.Series:
    """
    Mantém lógica original:
    Edge = combinação de:
    - expected value
    - alignment
    - terrain state
    """

    ev = safe_numeric(df["expected_value_score"])
    align = safe_numeric(df["force_alignment_cos"])

    score = ev * align

    return score.fillna(0.0)


def classify_edge(score: float) -> str:
    if pd.isna(score):
        return "NO_EDGE"

    if score > 0.0:
        return "LONG"
    elif score < 0.0:
        return "SHORT"
    return "NEUTRAL"


# =========================================================
# MAIN FUNCTION
# =========================================================

def build_edge_signal_90(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.replace([np.inf, -np.inf], np.nan)

    # ======================================
    # INPUT CHECK
    # ======================================
    required_cols = [
        "expected_value_score",
        "force_alignment_cos",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando: {missing}")

    df["expected_value_score"] = safe_numeric(df["expected_value_score"])
    df["force_alignment_cos"] = safe_numeric(df["force_alignment_cos"])

    # ======================================
    # EDGE SCORE
    # ======================================
    df["edge_score"] = build_edge_score(df)

    # ======================================
    # FILTROS DE QUALIDADE
    # ======================================
    df["edge_valid_long"] = safe_bool(
        (df["expected_value_score"] > EV_THRESHOLD) &
        (df["force_alignment_cos"] > ALIGNMENT_STRONG)
    )

    df["edge_valid_short"] = safe_bool(
        (df["expected_value_score"] > EV_THRESHOLD) &
        (df["force_alignment_cos"] < -ALIGNMENT_STRONG)
    )

    df["edge_strong_long"] = safe_bool(
        (df["expected_value_score"] > EV_THRESHOLD) &
        (df["force_alignment_cos"] > ALIGNMENT_VERY_STRONG)
    )

    df["edge_strong_short"] = safe_bool(
        (df["expected_value_score"] > EV_THRESHOLD) &
        (df["force_alignment_cos"] < -ALIGNMENT_VERY_STRONG)
    )

    # ======================================
    # DIREÇÃO FINAL
    # ======================================
    df["edge_direction"] = df["edge_score"].apply(classify_edge)

    # ======================================
    # HARDENING FINAL
    # ======================================
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        df[col] = safe_numeric(df[col])
        df[col] = df[col].fillna(0.0)

    return df


# =========================================================
# DEBUG / LOCAL
# =========================================================

def main() -> None:
    print("=" * 72)
    print("SGV BUILD EDGE SIGNAL")
    print("=" * 72)
    print("entrada :", INPUT)
    print("saida   :", OUTPUT)

    if not INPUT.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT}")

    df = pd.read_csv(INPUT)

    out = build_edge_signal_90(df)

    print("\nResumo:")
    print("linhas:", len(out))

    print("\nDistribuição de sinais:")
    print(out["edge_direction"].value_counts())

    print("\nEdge score stats:")
    print(out["edge_score"].describe().round(6))

    out.to_csv(OUTPUT, index=False)

    print("\nArquivo salvo:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()