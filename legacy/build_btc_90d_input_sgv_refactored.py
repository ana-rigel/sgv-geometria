from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# ==========================================
# CONFIG
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

INPUT = DATA_DIR / "btc_90d_1m_raw.csv"
OUTPUT = DATA_DIR / "btc_90d_input_sgv.csv"

PRICE_COL = "close"

# memória
MEMORY_ALPHA = 0.05

# lambda / rigidez
LAMBDA_WINDOW = 30
LAMBDA_MIN = 1e-6

# normalização robusta
ROBUST_EPS = 1e-9
EPS = 1e-9


# ==========================================
# HELPERS
# ==========================================

def robust_zscore(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")

    med = s.median()
    mad = (s - med).abs().median()

    scale = 1.4826 * mad if pd.notna(mad) and mad > 0 else s.std(ddof=0)
    if pd.isna(scale) or scale < ROBUST_EPS:
        scale = 1.0

    return (s - med) / scale


def safe_pct_change(s: pd.Series, periods: int = 1) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return s.pct_change(periods=periods)


def build_lambda_dynamic(ret_1m: pd.Series, window: int) -> pd.Series:
    """
    Rigidez dinâmica simples:
    quanto menor a volatilidade local, maior a rigidez.
    """
    ret_1m = pd.to_numeric(ret_1m, errors="coerce")

    local_vol = ret_1m.rolling(
        window=window,
        min_periods=max(5, window // 3),
    ).std()

    lam = 1.0 / (local_vol.abs() + LAMBDA_MIN)
    return lam


# ==========================================
# MAIN FUNCTION
# ==========================================

def build_btc_90d_input_sgv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    required = ["timestamp", "datetime", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando no raw dataset: {missing}")

    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["timestamp", "close"]).sort_values("timestamp").reset_index(drop=True)

    close = pd.to_numeric(df[PRICE_COL], errors="coerce")

    # ======================================
    # RETORNOS
    # ======================================
    df["ret_1m"] = safe_pct_change(close, 1)
    df["ret_fwd_1m"] = close.shift(-1) / (close + EPS) - 1.0
    df["ret_fwd_3m"] = close.shift(-3) / (close + EPS) - 1.0
    df["ret_fwd_5m"] = close.shift(-5) / (close + EPS) - 1.0

    # ======================================
    # MEMÓRIA
    # ======================================
    df["memory_close"] = close.ewm(alpha=MEMORY_ALPHA, adjust=False).mean()
    df["memory_flux"] = df["memory_close"].diff()

    # ======================================
    # CINEMÁTICA DE PREÇO
    # ======================================
    # velocidade = retorno instantâneo
    df["velocity"] = df["ret_1m"]

    # aceleração = variação da velocidade
    df["acceleration"] = df["velocity"].diff()

    # jerk = variação da aceleração
    df["jerk"] = df["acceleration"].diff()

    # ======================================
    # ENERGIA / DESALINHAMENTO
    # ======================================
    # energia crua como desvio relativo entre preço e memória
    df["E_raw"] = (df["close"] - df["memory_close"]) / (df["memory_close"].abs() + ROBUST_EPS)

    # energia normalizada robustamente
    df["E_norm"] = robust_zscore(df["E_raw"])

    # ======================================
    # RIGIDEZ DINÂMICA
    # ======================================
    df["lambda_dynamic"] = build_lambda_dynamic(df["ret_1m"], LAMBDA_WINDOW)

    # ======================================
    # LIMPEZA FINAL
    # ======================================
    out_cols = [
        "timestamp",
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ret_1m",
        "ret_fwd_1m",
        "ret_fwd_3m",
        "ret_fwd_5m",
        "memory_close",
        "memory_flux",
        "velocity",
        "acceleration",
        "jerk",
        "E_raw",
        "E_norm",
        "lambda_dynamic",
    ]

    out = df[out_cols].copy()

    # Mantém a lógica original de remoção de linhas sem estrutura suficiente
    out = out.copy()

    numeric_cols = out.select_dtypes(include=[np.number]).columns

    # não remove linhas
    for col in numeric_cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    # flag de qualidade
    out["input_valid"] = out[numeric_cols].notna().all(axis=1).astype(int)

    # preencher NaN (para live não quebrar pipeline)
    out[numeric_cols] = out[numeric_cols].fillna(0.0)

    out = out.reset_index(drop=True)

    return out


# ==========================================
# DEBUG / LOCAL RUN
# ==========================================

def main() -> None:
    print("=" * 72)
    print("BUILD BTC 90D INPUT SGV")
    print("=" * 72)
    print("entrada :", INPUT)
    print("saida   :", OUTPUT)

    if not INPUT.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT}")

    raw_df = pd.read_csv(INPUT)
    out = build_btc_90d_input_sgv(raw_df)

    print("\nResumo das colunas SGV:")
    summary_cols = [
        "ret_1m",
        "ret_fwd_1m",
        "ret_fwd_3m",
        "ret_fwd_5m",
        "memory_flux",
        "velocity",
        "acceleration",
        "jerk",
        "E_norm",
        "lambda_dynamic",
    ]
    print(out[summary_cols].describe().T[["mean", "std", "min", "max"]].round(6))

    print("\nLinhas finais:", len(out))

    out.to_csv(OUTPUT, index=False)

    print("\nArquivo salvo com sucesso.")
    print("saida:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()