from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

INPUT_SOURCE = SCRIPTS_DIR / "btc_90d_input_sgv.csv"
OUTPUT = SCRIPTS_DIR / "sgv_terrain_layer_v1_90d.csv"

# Colunas mínimas da V1
E_COL = "E_norm"
J_COL = "jerk"

# Opcionais para futuras versões
LAMBDA_COL = "lambda_dynamic"
R_COL = "r"

# Janela local do atrator / covariância
WINDOW = 80

# Peso exponencial: quanto mais próximo de 1, mais memória
ALPHA = 0.97

# Regularização numérica estabilizada
EPS = 1e-4

# KDE
BANDWIDTH = 0.35

# Passo pequeno para derivadas numéricas da log densidade
DELTA = 0.03

# Profundidade de bacia: penalização da curvatura
BETA = 0.60

# Histerese: distância entre atratores separados por K
HYST_K = 10

# Winsorização robusta
WINSOR_LO = 0.005
WINSOR_HI = 0.995

# Clip final do score
FINAL_SCORE_LO = 0.005
FINAL_SCORE_HI = 0.995


# =========================================================
# HELPERS
# =========================================================

def build_weights(window: int, alpha: float) -> np.ndarray:
    idx = np.arange(window)
    w = alpha ** (window - 1 - idx)
    w = w / np.maximum(w.sum(), 1e-12)
    return w


def weighted_mean_cov(X: np.ndarray, w: np.ndarray, eps: float = 1e-4) -> tuple[np.ndarray, np.ndarray]:
    """
    X: (n, d)
    w: (n,)
    """
    mu = np.sum(X * w[:, None], axis=0)
    XC = X - mu
    cov = np.einsum("n,ni,nj->ij", w, XC, XC)
    cov = cov + eps * np.eye(X.shape[1])
    return mu, cov


def mahalanobis_squared(x: np.ndarray, mu: np.ndarray, cov: np.ndarray) -> float:
    diff = x - mu
    inv_cov = np.linalg.pinv(cov)
    val = float(diff.T @ inv_cov @ diff)
    return max(val, 0.0)


def robust_zscore(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)

    med = s.median()
    mad = np.median(np.abs(s.dropna() - med)) if s.notna().any() else np.nan

    if pd.isna(mad) or mad < 1e-12:
        return pd.Series(np.zeros(len(s)), index=s.index, dtype=float)

    return 0.6745 * (s - med) / mad


def winsorize_series(series: pd.Series, q_low: float, q_high: float) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).copy()

    if s.notna().sum() == 0:
        return pd.Series(0.0, index=s.index, dtype=float)

    lo = s.quantile(q_low)
    hi = s.quantile(q_high)
    return s.clip(lower=lo, upper=hi)


def robust_fill(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)
    return s.bfill().ffill()


def fit_kde(X: np.ndarray, bandwidth: float) -> KernelDensity:
    kde = KernelDensity(kernel="gaussian", bandwidth=bandwidth)
    kde.fit(X)
    return kde


def log_density(kde: KernelDensity, x: np.ndarray) -> float:
    return float(kde.score_samples(x.reshape(1, -1))[0])


def numerical_grad_log_density(kde: KernelDensity, x: np.ndarray, delta: float) -> np.ndarray:
    """
    Gradiente numérico central da log densidade.
    """
    d = len(x)
    grad = np.zeros(d, dtype=float)

    for j in range(d):
        xp = x.copy()
        xm = x.copy()
        xp[j] += delta
        xm[j] -= delta
        fp = log_density(kde, xp)
        fm = log_density(kde, xm)
        grad[j] = (fp - fm) / (2.0 * delta)

    return grad


def numerical_hessian_log_density(kde: KernelDensity, x: np.ndarray, delta: float) -> np.ndarray:
    """
    Hessiana numérica central da log densidade.
    """
    d = len(x)
    H = np.zeros((d, d), dtype=float)

    f0 = log_density(kde, x)

    for i in range(d):
        xp = x.copy()
        xm = x.copy()
        xp[i] += delta
        xm[i] -= delta
        fp = log_density(kde, xp)
        fm = log_density(kde, xm)
        H[i, i] = (fp - 2.0 * f0 + fm) / (delta ** 2)

        for j in range(i + 1, d):
            xpp = x.copy()
            xpm = x.copy()
            xmp = x.copy()
            xmm = x.copy()

            xpp[i] += delta
            xpp[j] += delta

            xpm[i] += delta
            xpm[j] -= delta

            xmp[i] -= delta
            xmp[j] += delta

            xmm[i] -= delta
            xmm[j] -= delta

            fpp = log_density(kde, xpp)
            fpm = log_density(kde, xpm)
            fmp = log_density(kde, xmp)
            fmm = log_density(kde, xmm)

            val = (fpp - fpm - fmp + fmm) / (4.0 * delta ** 2)
            H[i, j] = val
            H[j, i] = val

    return H


def prepare_input_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if "timestamp" not in out.columns:
        raise ValueError("btc_90d_input_sgv.csv não possui coluna 'timestamp'.")

    if E_COL not in out.columns:
        raise ValueError(f"btc_90d_input_sgv.csv não possui coluna '{E_COL}'.")

    if J_COL not in out.columns:
        raise ValueError(f"btc_90d_input_sgv.csv não possui coluna '{J_COL}'.")

    ts = out["timestamp"]

    if pd.api.types.is_datetime64_any_dtype(ts):
        out["timestamp"] = pd.to_datetime(ts, errors="coerce", utc=True)
    else:
        ts_num = pd.to_numeric(ts, errors="coerce")
        if ts_num.notna().mean() > 0.8:
            sample = ts_num.dropna()
            if sample.empty:
                out["timestamp"] = pd.to_datetime(ts, errors="coerce", utc=True)
            else:
                median_abs = sample.abs().median()
                if median_abs >= 1e17:
                    unit = "ns"
                elif median_abs >= 1e14:
                    unit = "us"
                elif median_abs >= 1e11:
                    unit = "ms"
                else:
                    unit = "s"
                out["timestamp"] = pd.to_datetime(ts_num, unit=unit, errors="coerce", utc=True)
        else:
            out["timestamp"] = pd.to_datetime(ts, errors="coerce", utc=True)

    src_cols = ["timestamp", E_COL, J_COL]
    for c in [LAMBDA_COL, R_COL, "close", "regime", "ret_fwd_1m", "ret_fwd_5m"]:
        if c in out.columns and c not in src_cols:
            src_cols.append(c)

    out = out[src_cols].copy()

    for c in [E_COL, J_COL, LAMBDA_COL, R_COL, "close", "ret_fwd_1m", "ret_fwd_5m"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")

    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=[E_COL, J_COL]).reset_index(drop=True)

    return out


# =========================================================
# MAIN FUNCTION
# =========================================================

def build_terrain_layer_90d(df: pd.DataFrame) -> pd.DataFrame:
    work = prepare_input_dataframe(df)

    # -----------------------------------------------------
    # Vetor de estado da V1: x_t = [E_norm, jerk]
    # -----------------------------------------------------
    X = work[[E_COL, J_COL]].to_numpy(dtype=float)
    n, d = X.shape

    if n < WINDOW:
        raise ValueError(f"Dados insuficientes: n={n}, WINDOW={WINDOW}")

    weights = build_weights(WINDOW, ALPHA)

    mu_list: list[list[float]] = []
    cov11_list: list[float] = []
    cov12_list: list[float] = []
    cov22_list: list[float] = []
    fisher11_list: list[float] = []
    fisher12_list: list[float] = []
    fisher22_list: list[float] = []
    disp_raw_list: list[float] = []
    disp_log_list: list[float] = []

    # -----------------------------------------------------
    # ATRATOR LOCAL + COV LOCAL + DISTÂNCIA INFORMACIONAL
    # -----------------------------------------------------
    for t in range(n):
        if t < WINDOW - 1:
            mu_list.append([np.nan, np.nan])
            cov11_list.append(np.nan)
            cov12_list.append(np.nan)
            cov22_list.append(np.nan)
            fisher11_list.append(np.nan)
            fisher12_list.append(np.nan)
            fisher22_list.append(np.nan)
            disp_raw_list.append(np.nan)
            disp_log_list.append(np.nan)
            continue

        Xw = X[t - WINDOW + 1:t + 1]
        mu_t, cov_t = weighted_mean_cov(Xw, weights, eps=EPS)

        # proxy de Fisher local gaussiana
        fisher_t = np.linalg.pinv(cov_t)

        x_t = X[t]
        disp_raw_t = mahalanobis_squared(x_t, mu_t, cov_t)
        disp_log_t = float(np.log1p(disp_raw_t))

        mu_list.append(mu_t.tolist())
        cov11_list.append(float(cov_t[0, 0]))
        cov12_list.append(float(cov_t[0, 1]))
        cov22_list.append(float(cov_t[1, 1]))

        fisher11_list.append(float(fisher_t[0, 0]))
        fisher12_list.append(float(fisher_t[0, 1]))
        fisher22_list.append(float(fisher_t[1, 1]))

        disp_raw_list.append(float(disp_raw_t))
        disp_log_list.append(float(disp_log_t))

    work["terrain_attractor_E"] = [m[0] if isinstance(m, list) else np.nan for m in mu_list]
    work["terrain_attractor_jerk"] = [m[1] if isinstance(m, list) else np.nan for m in mu_list]

    work["terrain_cov_11"] = cov11_list
    work["terrain_cov_12"] = cov12_list
    work["terrain_cov_22"] = cov22_list

    work["terrain_fisher_proxy_11"] = fisher11_list
    work["terrain_fisher_proxy_12"] = fisher12_list
    work["terrain_fisher_proxy_22"] = fisher22_list

    work["terrain_informational_displacement_raw"] = disp_raw_list
    work["terrain_informational_displacement"] = disp_log_list

    # -----------------------------------------------------
    # KDE GLOBAL NO PLANO DE ESTADOS
    # -----------------------------------------------------
    valid_mask = work["terrain_informational_displacement"].notna()
    X_valid = work.loc[valid_mask, [E_COL, J_COL]].to_numpy(dtype=float)

    if len(X_valid) == 0:
        raise ValueError("Não há dados válidos para ajuste do KDE do terrain layer.")

    kde = fit_kde(X_valid, bandwidth=BANDWIDTH)

    logp_list: list[float] = []
    grad_norm_list: list[float] = []
    grad_e_list: list[float] = []
    grad_j_list: list[float] = []
    hess_trace_list: list[float] = []
    hess_maxeig_abs_list: list[float] = []
    basin_depth_list: list[float] = []

    for idx in range(n):
        x_t = X[idx]

        lp = log_density(kde, x_t)
        grad = numerical_grad_log_density(kde, x_t, DELTA)
        hess = numerical_hessian_log_density(kde, x_t, DELTA)

        grad_norm = float(np.linalg.norm(grad))
        eigvals = np.linalg.eigvalsh(hess)
        hess_trace = float(np.trace(hess))
        hess_maxeig_abs = float(np.max(np.abs(eigvals)))

        basin_depth = lp - BETA * grad_norm

        logp_list.append(float(lp))
        grad_e_list.append(float(grad[0]))
        grad_j_list.append(float(grad[1]))
        grad_norm_list.append(float(grad_norm))
        hess_trace_list.append(float(hess_trace))
        hess_maxeig_abs_list.append(float(hess_maxeig_abs))
        basin_depth_list.append(float(basin_depth))

    work["terrain_log_density"] = logp_list
    work["terrain_grad_logp_E"] = grad_e_list
    work["terrain_grad_logp_jerk"] = grad_j_list
    work["terrain_curvature"] = grad_norm_list
    work["terrain_hessian_trace"] = hess_trace_list
    work["terrain_hessian_maxeig_abs"] = hess_maxeig_abs_list
    work["terrain_basin_depth"] = basin_depth_list

    # -----------------------------------------------------
    # HISTERESE
    # -----------------------------------------------------
    work["terrain_regime_hysteresis"] = np.nan

    for t in range(n):
        if t < WINDOW - 1 + HYST_K:
            continue

        mu_now = np.array(
            [
                work.at[t, "terrain_attractor_E"],
                work.at[t, "terrain_attractor_jerk"],
            ],
            dtype=float,
        )

        mu_prev = np.array(
            [
                work.at[t - HYST_K, "terrain_attractor_E"],
                work.at[t - HYST_K, "terrain_attractor_jerk"],
            ],
            dtype=float,
        )

        work.at[t, "terrain_regime_hysteresis"] = float(np.linalg.norm(mu_now - mu_prev))

    # -----------------------------------------------------
    # ESTABILIZAÇÃO DAS SÉRIES
    # -----------------------------------------------------
    disp_s = robust_fill(work["terrain_informational_displacement"])
    curv_s = robust_fill(work["terrain_curvature"])
    basin_s = robust_fill(work["terrain_basin_depth"])
    hyst_s = robust_fill(work["terrain_regime_hysteresis"])

    disp_w = winsorize_series(disp_s, WINSOR_LO, WINSOR_HI)
    curv_w = winsorize_series(curv_s, WINSOR_LO, WINSOR_HI)
    basin_w = winsorize_series(basin_s, WINSOR_LO, WINSOR_HI)
    hyst_w = winsorize_series(hyst_s, WINSOR_LO, WINSOR_HI)

    work["terrain_informational_displacement_w"] = disp_w
    work["terrain_curvature_w"] = curv_w
    work["terrain_basin_depth_w"] = basin_w
    work["terrain_regime_hysteresis_w"] = hyst_w

    z_disp = robust_zscore(disp_w)
    z_curv = robust_zscore(curv_w)
    z_basin = robust_zscore(basin_w)
    z_hyst = robust_zscore(hyst_w)

    work["terrain_z_disp"] = z_disp
    work["terrain_z_curv"] = z_curv
    work["terrain_z_basin"] = z_basin
    work["terrain_z_hyst"] = z_hyst

    raw_score = z_disp + z_curv - z_basin + z_hyst

    lo = raw_score.quantile(FINAL_SCORE_LO)
    hi = raw_score.quantile(FINAL_SCORE_HI)
    final_score = raw_score.clip(lower=lo, upper=hi)

    work["terrain_transition_score_raw"] = raw_score
    work["terrain_transition_score"] = final_score

    # -----------------------------------------------------
    # RÓTULO INTERPRETATIVO
    # -----------------------------------------------------
    q1 = work["terrain_transition_score"].quantile(0.50)
    q2 = work["terrain_transition_score"].quantile(0.80)
    q3 = work["terrain_transition_score"].quantile(0.93)

    def classify(score: float) -> str:
        if pd.isna(score):
            return "UNDEFINED"
        if score < q1:
            return "COHERENT"
        elif score < q2:
            return "TENSIONED"
        elif score < q3:
            return "TRANSITION_EDGE"
        return "RUPTURE_CORRIDOR"

    work["terrain_state"] = work["terrain_transition_score"].apply(classify)

    # -----------------------------------------------------
    # HARDENING FINAL PARA LIVE
    # -----------------------------------------------------
    numeric_cols = work.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        work[col] = pd.to_numeric(work[col], errors="coerce")
        work[col] = work[col].replace([np.inf, -np.inf], np.nan)

    fill_zero_cols = [
        "terrain_cov_11",
        "terrain_cov_12",
        "terrain_cov_22",
        "terrain_fisher_proxy_11",
        "terrain_fisher_proxy_12",
        "terrain_fisher_proxy_22",
        "terrain_informational_displacement_raw",
        "terrain_informational_displacement",
        "terrain_log_density",
        "terrain_grad_logp_E",
        "terrain_grad_logp_jerk",
        "terrain_curvature",
        "terrain_hessian_trace",
        "terrain_hessian_maxeig_abs",
        "terrain_basin_depth",
        "terrain_regime_hysteresis",
        "terrain_informational_displacement_w",
        "terrain_curvature_w",
        "terrain_basin_depth_w",
        "terrain_regime_hysteresis_w",
        "terrain_z_disp",
        "terrain_z_curv",
        "terrain_z_basin",
        "terrain_z_hyst",
        "terrain_transition_score_raw",
        "terrain_transition_score",
    ]
    for col in fill_zero_cols:
        if col in work.columns:
            work[col] = work[col].fillna(0.0)

    return work


# =========================================================
# DEBUG / LOCAL
# =========================================================

def main() -> None:
    print("=" * 72)
    print("SGV TERRAIN LAYER V1 90D")
    print("=" * 72)
    print("entrada src  :", INPUT_SOURCE)
    print("saida        :", OUTPUT)

    if not INPUT_SOURCE.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT_SOURCE}")

    df_src = pd.read_csv(INPUT_SOURCE)
    out = build_terrain_layer_90d(df_src)

    print("\nResumo:")
    print(f"linhas processadas              : {len(out)}")
    print(f"window local                    : {WINDOW}")
    print(f"bandwidth KDE                   : {BANDWIDTH}")
    print(f"delta derivadas numéricas       : {DELTA}")
    print(f"histerese lag                   : {HYST_K}")
    print(f"eps regularização               : {EPS}")
    print(f"winsor low/high                 : {WINSOR_LO} / {WINSOR_HI}")
    print(f"score clip low/high             : {FINAL_SCORE_LO} / {FINAL_SCORE_HI}")

    print("\nColunas principais geradas:")
    main_cols = [
        "terrain_attractor_E",
        "terrain_attractor_jerk",
        "terrain_informational_displacement_raw",
        "terrain_informational_displacement",
        "terrain_fisher_proxy_11",
        "terrain_fisher_proxy_12",
        "terrain_fisher_proxy_22",
        "terrain_log_density",
        "terrain_curvature",
        "terrain_basin_depth",
        "terrain_regime_hysteresis",
        "terrain_transition_score_raw",
        "terrain_transition_score",
        "terrain_state",
    ]
    for c in main_cols:
        print(" -", c)

    out.to_csv(OUTPUT, index=False)

    print("\nArquivo salvo com sucesso.")
    print("saida:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()