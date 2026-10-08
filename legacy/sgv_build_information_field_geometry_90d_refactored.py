from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity


# =========================================================
# CONFIG
# =========================================================

WINDOW = 200
BANDWIDTH = 0.35
EPS = 1e-9


# =========================================================
# HELPERS
# =========================================================

def compute_base_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    # retorno
    df["ret"] = df["close"].pct_change()

    # velocidade
    df["velocity"] = df["ret"]

    # aceleração
    df["acceleration"] = df["velocity"].diff()

    # jerk (terceira derivada)
    df["jerk"] = df["acceleration"].diff()

    # energia normalizada (mesma lógica original)
    df["E_norm"] = (
        (df["velocity"] ** 2 + df["acceleration"] ** 2)
    )

    return df


def compute_kde_field(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # garantir numérico
    df["E_norm"] = pd.to_numeric(df["E_norm"], errors="coerce")
    df["jerk"] = pd.to_numeric(df["jerk"], errors="coerce")

    scores = np.zeros(len(df), dtype=float)

    for i in range(len(df)):

        start = max(0, i - WINDOW)
        window_df = df.iloc[start:i].copy()

        if len(window_df) < max(10, WINDOW // 5):
            scores[i] = 0.0
            continue

        X = window_df[["E_norm", "jerk"]].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X["E_norm"] = pd.to_numeric(X["E_norm"], errors="coerce")
        X["jerk"] = pd.to_numeric(X["jerk"], errors="coerce")
        X = X.dropna()

        if len(X) < 10:
            scores[i] = 0.0
            continue

        X_np = X.to_numpy(dtype=float)

        kde = KernelDensity(kernel="gaussian", bandwidth=BANDWIDTH)
        kde.fit(X_np)

        point = df.loc[df.index[i], ["E_norm", "jerk"]].copy()
        point = pd.to_numeric(point, errors="coerce")
        point_np = point.to_numpy(dtype=float).reshape(1, -1)

        if np.isnan(point_np).any() or np.isinf(point_np).any():
            scores[i] = 0.0
            continue

        log_density = kde.score_samples(point_np)[0]
        density = np.exp(log_density)

        scores[i] = float(density)

    df["information_density"] = scores

    return df

# =========================================================
# MAIN FUNCTION
# =========================================================

def build_information_field_geometry_90d(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.replace([np.inf, -np.inf], np.nan)

    # =========================
    # BASE FEATURES
    # =========================
    df = compute_base_features(df)

    # =========================
    # KDE FIELD
    # =========================
    df = compute_kde_field(df)

    # =========================
    # DERIVAÇÕES DO CAMPO
    # =========================
    df["information_gradient"] = df["information_density"].diff()
    df["information_acceleration"] = df["information_gradient"].diff()

    # =========================
    # NORMALIZAÇÃO FINAL
    # =========================
    df["information_density"] = df["information_density"].fillna(0.0)
    df["information_gradient"] = df["information_gradient"].fillna(0.0)
    df["information_acceleration"] = df["information_acceleration"].fillna(0.0)

    return df


# =========================================================
# DEBUG / LOCAL
# =========================================================

def main() -> None:

    BASE_DIR = Path(__file__).resolve().parent.parent
    INPUT = BASE_DIR / "scripts" / "btc_90d_input_sgv.csv"
    OUTPUT = BASE_DIR / "scripts" / "sgv_information_field_geometry_90d.csv"

    print("=" * 72)
    print("SGV BUILD INFORMATION FIELD GEOMETRY")
    print("=" * 72)

    if not INPUT.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT}")

    df = pd.read_csv(INPUT)

    out = build_information_field_geometry_90d(df)

    print("\nResumo:")
    cols = [
        "information_density",
        "information_gradient",
        "information_acceleration",
    ]

    cols = [c for c in cols if c in out.columns]

    print(out[cols].describe().T[["mean", "std", "min", "max"]].round(6))

    out.to_csv(OUTPUT, index=False)

    print("\nArquivo salvo:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()