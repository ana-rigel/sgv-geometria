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
OUTPUT = SCRIPTS_DIR / "sgv_expected_value_90d.csv"

EPS = 1e-9

# janelas
WINDOW = 200

# quantis
Q_HIGH = 0.95
Q_LOW = 0.05


# =========================================================
# HELPERS
# =========================================================

def safe_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def compute_forward_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "close" not in df.columns:
        raise ValueError("Coluna 'close' necessária.")

    close = safe_numeric(df["close"])

    df["ret_fwd_1"] = close.shift(-1) / (close + EPS) - 1.0
    df["ret_fwd_3"] = close.shift(-3) / (close + EPS) - 1.0
    df["ret_fwd_5"] = close.shift(-5) / (close + EPS) - 1.0

    return df


def rolling_expected_value(signal: pd.Series, returns: pd.Series, window: int) -> pd.Series:
    """
    Mantém exatamente a lógica:
    EV = média condicional dos retornos quando sinal ativo
    """
    out = np.zeros(len(signal))

    sig = safe_numeric(signal)
    ret = safe_numeric(returns)

    for i in range(len(signal)):

        start = max(0, i - window)
        sig_w = sig.iloc[start:i]
        ret_w = ret.iloc[start:i]

        mask = sig_w > 0

        if mask.sum() < 10:
            out[i] = 0.0
            continue

        ev = ret_w[mask].mean()

        if pd.isna(ev):
            ev = 0.0

        out[i] = float(ev)

    return pd.Series(out, index=signal.index)


def compute_probabilities(signal: pd.Series, window: int) -> pd.Series:
    sig = safe_numeric(signal)

    out = np.zeros(len(sig))

    for i in range(len(sig)):

        start = max(0, i - window)
        sig_w = sig.iloc[start:i]

        if len(sig_w) < 10:
            out[i] = 0.0
            continue

        prob = (sig_w > 0).mean()

        out[i] = float(prob)

    return pd.Series(out, index=sig.index)


# =========================================================
# MAIN FUNCTION
# =========================================================

def build_expected_value_90d(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.replace([np.inf, -np.inf], np.nan)

    # ======================================
    # INPUT CHECK
    # ======================================
    required_cols = [
        "terrain_transition_score",
        "close",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando: {missing}")

    df["terrain_transition_score"] = safe_numeric(df["terrain_transition_score"])

    # ======================================
    # RETURNS
    # ======================================
    df = compute_forward_returns(df)

    # ======================================
    # SIGNALS
    # ======================================
    q_high = df["terrain_transition_score"].quantile(Q_HIGH)
    q_low = df["terrain_transition_score"].quantile(Q_LOW)

    df["signal_long"] = (df["terrain_transition_score"] >= q_high).astype(int)
    df["signal_short"] = (df["terrain_transition_score"] <= q_low).astype(int)

    # ======================================
    # EXPECTED VALUE
    # ======================================
    df["ev_long_1"] = rolling_expected_value(df["signal_long"], df["ret_fwd_1"], WINDOW)
    df["ev_long_3"] = rolling_expected_value(df["signal_long"], df["ret_fwd_3"], WINDOW)
    df["ev_long_5"] = rolling_expected_value(df["signal_long"], df["ret_fwd_5"], WINDOW)

    df["ev_short_1"] = rolling_expected_value(df["signal_short"], -df["ret_fwd_1"], WINDOW)
    df["ev_short_3"] = rolling_expected_value(df["signal_short"], -df["ret_fwd_3"], WINDOW)
    df["ev_short_5"] = rolling_expected_value(df["signal_short"], -df["ret_fwd_5"], WINDOW)

    # ======================================
    # PROBABILIDADES
    # ======================================
    df["prob_long"] = compute_probabilities(df["signal_long"], WINDOW)
    df["prob_short"] = compute_probabilities(df["signal_short"], WINDOW)

    # ======================================
    # SCORE FINAL
    # ======================================
    df["expected_value_score"] = (
        df["prob_long"] * df["ev_long_1"] +
        df["prob_short"] * df["ev_short_1"]
    )

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
    print("SGV BUILD EXPECTED VALUE")
    print("=" * 72)
    print("entrada :", INPUT)
    print("saida   :", OUTPUT)

    if not INPUT.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT}")

    df = pd.read_csv(INPUT)

    out = build_expected_value_90d(df)

    print("\nResumo:")
    cols = [
        "expected_value_score",
        "prob_long",
        "prob_short",
        "ev_long_1",
        "ev_short_1",
    ]

    cols = [c for c in cols if c in out.columns]

    print(out[cols].describe().T[["mean", "std", "min", "max"]].round(6))

    out.to_csv(OUTPUT, index=False)

    print("\nArquivo salvo:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()