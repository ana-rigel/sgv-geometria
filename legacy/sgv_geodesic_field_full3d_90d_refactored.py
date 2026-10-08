from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity


# ==========================================
# CONFIG
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

INPUT = SCRIPTS_DIR / "sgv_information_field_geometry_90d.csv"
OUTPUT = SCRIPTS_DIR / "sgv_geodesic_field_full_90d.csv"

# colunas principais
E_COL = "E_norm"
J_COL = "jerk"
L_COL = "lambda_dynamic"

# reconstrução do campo 2D
GRID_N = 200
BANDWIDTH = 0.35
Q_LOW = 0.01
Q_HIGH = 0.99

# camada 3D de gravidade informacional
GRID_N_E3 = 48
GRID_N_J3 = 48
GRID_N_M3 = 32
BANDWIDTH_3D = 0.45

# estabilidade numérica
EPS = 1e-9
METRIC_REG = 1e-6
DET_FLOOR = 1e-9

# memória geométrica
ALPHA_E = 0.05
ALPHA_J = 0.05

# clipping
CLIP_GAMMA = 1e6
CLIP_ACC = 1e6
CLIP_CURV_3D = 1e6
CLIP_FIELD_GRAVITY = 1e6

# stress geodésico
W_INCOH = 1.00
W_GRAD = 0.50
W_GEO_RESID = 1.00
W_ACC_GEO = 0.25
W_CURVATURE = 0.25
W_JERK_OVER_LAMBDA = 0.50

# score heurístico inicial
B0 = -2.0
B1 = 1.00   # geo_resid_norm
B2 = 0.50   # acc_geo_norm
B3 = 0.40   # grad_phi_norm
B4 = 0.50   # geom_incoherence_abs
B5 = 0.30   # abs(field_curvature)
B6 = 0.40   # abs(jerk)/lambda

# stress-energia informacional 3D
W_PHI_STRESS = 1.00
W_MEM_STRESS = 0.75
W_LAMBDA_STRESS = 0.25

# acoplamento gravitacional informacional
KAPPA_INFO = 1.0


# ==========================================
# HELPERS
# ==========================================

def sigmoid(x: np.ndarray | pd.Series) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    x_arr = np.clip(x_arr, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-x_arr))


def ema(series: pd.Series, alpha: float) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    return series.ewm(alpha=alpha, adjust=False).mean()


def clip_series(s: pd.Series, lo: float, hi: float) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return s.clip(lower=lo, upper=hi)


def ensure_required_columns(df: pd.DataFrame) -> None:
    required = [E_COL, J_COL, L_COL]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando no input: {missing}")


def prepare_input_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    ensure_required_columns(df)

    out = df.copy()

    out[E_COL] = pd.to_numeric(out[E_COL], errors="coerce")
    out[J_COL] = pd.to_numeric(out[J_COL], errors="coerce")
    out[L_COL] = pd.to_numeric(out[L_COL], errors="coerce")

    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=[E_COL, J_COL, L_COL]).reset_index(drop=True)

    if out.empty:
        raise ValueError("Dataset vazio após limpeza.")

    return out


def make_grid(
    values_e: np.ndarray,
    values_j: np.ndarray,
    grid_n: int,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    values_e = np.asarray(values_e, dtype=float)
    values_j = np.asarray(values_j, dtype=float)

    e_lo, e_hi = np.quantile(values_e, [Q_LOW, Q_HIGH])
    j_lo, j_hi = np.quantile(values_j, [Q_LOW, Q_HIGH])

    e_span = max(e_hi - e_lo, EPS)
    j_span = max(j_hi - j_lo, EPS)

    e_min = e_lo - 0.10 * e_span
    e_max = e_hi + 0.10 * e_span
    j_min = j_lo - 0.10 * j_span
    j_max = j_hi + 0.10 * j_span

    grid_e = np.linspace(e_min, e_max, grid_n)
    grid_j = np.linspace(j_min, j_max, grid_n)

    d_e = float(grid_e[1] - grid_e[0]) if grid_n > 1 else 1.0
    d_j = float(grid_j[1] - grid_j[0]) if grid_n > 1 else 1.0

    return grid_e, grid_j, d_e, d_j


def fit_kde_density(
    values_e: np.ndarray,
    values_j: np.ndarray,
    grid_e: np.ndarray,
    grid_j: np.ndarray,
    bandwidth: float,
) -> np.ndarray:
    samples = np.column_stack([values_e, values_j])

    kde = KernelDensity(kernel="gaussian", bandwidth=bandwidth)
    kde.fit(samples)

    ee, jj = np.meshgrid(grid_e, grid_j, indexing="ij")
    grid_points = np.column_stack([ee.ravel(), jj.ravel()])

    log_density = kde.score_samples(grid_points)
    density = np.exp(log_density).reshape(len(grid_e), len(grid_j))

    return density


def bilinear_interp(
    grid_e: np.ndarray,
    grid_j: np.ndarray,
    grid_values: np.ndarray,
    e_points: np.ndarray,
    j_points: np.ndarray,
) -> np.ndarray:
    e_points = np.asarray(e_points, dtype=float)
    j_points = np.asarray(j_points, dtype=float)

    e_points = np.clip(e_points, grid_e[0], grid_e[-1])
    j_points = np.clip(j_points, grid_j[0], grid_j[-1])

    i = np.searchsorted(grid_e, e_points, side="right") - 1
    j = np.searchsorted(grid_j, j_points, side="right") - 1

    i = np.clip(i, 0, len(grid_e) - 2)
    j = np.clip(j, 0, len(grid_j) - 2)

    e0 = grid_e[i]
    e1 = grid_e[i + 1]
    j0 = grid_j[j]
    j1 = grid_j[j + 1]

    de = np.maximum(e1 - e0, EPS)
    dj = np.maximum(j1 - j0, EPS)

    we = (e_points - e0) / de
    wj = (j_points - j0) / dj

    v00 = grid_values[i, j]
    v10 = grid_values[i + 1, j]
    v01 = grid_values[i, j + 1]
    v11 = grid_values[i + 1, j + 1]

    return (
        (1.0 - we) * (1.0 - wj) * v00
        + we * (1.0 - wj) * v10
        + (1.0 - we) * wj * v01
        + we * wj * v11
    )


def gradient_and_hessian(
    phi_grid: np.ndarray,
    d_e: float,
    d_j: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if phi_grid.shape[0] < 3 or phi_grid.shape[1] < 3:
        zeros = np.zeros_like(phi_grid, dtype=float)
        return zeros, zeros, zeros, zeros, zeros

    phi_e, phi_j = np.gradient(phi_grid, d_e, d_j, edge_order=2)
    phi_ee, phi_ej = np.gradient(phi_e, d_e, d_j, edge_order=2)
    _, phi_jj = np.gradient(phi_j, d_e, d_j, edge_order=2)

    return phi_e, phi_j, phi_ee, phi_ej, phi_jj


# ==========================================
# HELPERS 3D - GRAVIDADE INFORMACIONAL
# ==========================================

def make_axis_1d(values: np.ndarray, n: int) -> np.ndarray:
    values = np.asarray(values, dtype=float)

    lo, hi = np.quantile(values, [Q_LOW, Q_HIGH])
    span = max(hi - lo, EPS)

    vmin = lo - 0.10 * span
    vmax = hi + 0.10 * span

    return np.linspace(vmin, vmax, n)


def trilinear_interp(
    grid_e: np.ndarray,
    grid_j: np.ndarray,
    grid_m: np.ndarray,
    grid_values: np.ndarray,
    e_points: np.ndarray,
    j_points: np.ndarray,
    m_points: np.ndarray,
) -> np.ndarray:
    e_points = np.asarray(e_points, dtype=float)
    j_points = np.asarray(j_points, dtype=float)
    m_points = np.asarray(m_points, dtype=float)

    e_points = np.clip(e_points, grid_e[0], grid_e[-1])
    j_points = np.clip(j_points, grid_j[0], grid_j[-1])
    m_points = np.clip(m_points, grid_m[0], grid_m[-1])

    ie = np.searchsorted(grid_e, e_points, side="right") - 1
    ij = np.searchsorted(grid_j, j_points, side="right") - 1
    im = np.searchsorted(grid_m, m_points, side="right") - 1

    ie = np.clip(ie, 0, len(grid_e) - 2)
    ij = np.clip(ij, 0, len(grid_j) - 2)
    im = np.clip(im, 0, len(grid_m) - 2)

    e0, e1 = grid_e[ie], grid_e[ie + 1]
    j0, j1 = grid_j[ij], grid_j[ij + 1]
    m0, m1 = grid_m[im], grid_m[im + 1]

    de = np.maximum(e1 - e0, EPS)
    dj = np.maximum(j1 - j0, EPS)
    dm = np.maximum(m1 - m0, EPS)

    we = (e_points - e0) / de
    wj = (j_points - j0) / dj
    wm = (m_points - m0) / dm

    c000 = grid_values[ie, ij, im]
    c100 = grid_values[ie + 1, ij, im]
    c010 = grid_values[ie, ij + 1, im]
    c110 = grid_values[ie + 1, ij + 1, im]
    c001 = grid_values[ie, ij, im + 1]
    c101 = grid_values[ie + 1, ij, im + 1]
    c011 = grid_values[ie, ij + 1, im + 1]
    c111 = grid_values[ie + 1, ij + 1, im + 1]

    c00 = (1.0 - we) * c000 + we * c100
    c01 = (1.0 - we) * c001 + we * c101
    c10 = (1.0 - we) * c010 + we * c110
    c11 = (1.0 - we) * c011 + we * c111

    c0 = (1.0 - wj) * c00 + wj * c10
    c1 = (1.0 - wj) * c01 + wj * c11

    return (1.0 - wm) * c0 + wm * c1


def fit_kde_density_3d(
    values_e: np.ndarray,
    values_j: np.ndarray,
    values_m: np.ndarray,
    grid_e: np.ndarray,
    grid_j: np.ndarray,
    grid_m: np.ndarray,
    bandwidth: float,
) -> np.ndarray:
    samples = np.column_stack([values_e, values_j, values_m])

    kde = KernelDensity(kernel="gaussian", bandwidth=bandwidth)
    kde.fit(samples)

    ee, jj, mm = np.meshgrid(grid_e, grid_j, grid_m, indexing="ij")
    grid_points = np.column_stack([ee.ravel(), jj.ravel(), mm.ravel()])

    log_density = kde.score_samples(grid_points)
    density = np.exp(log_density).reshape(len(grid_e), len(grid_j), len(grid_m))

    return density


def gradient_3d(
    arr: np.ndarray,
    d_e: float,
    d_j: float,
    d_m: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if arr.shape[0] < 3 or arr.shape[1] < 3 or arr.shape[2] < 3:
        zeros = np.zeros_like(arr, dtype=float)
        return zeros, zeros, zeros

    return np.gradient(arr, d_e, d_j, d_m, edge_order=2)


def build_lambda_field_3d(
    values_e: np.ndarray,
    values_j: np.ndarray,
    values_m: np.ndarray,
    values_l: np.ndarray,
    grid_e: np.ndarray,
    grid_j: np.ndarray,
    grid_m: np.ndarray,
    bandwidth: float,
) -> np.ndarray:
    ee, jj, mm = np.meshgrid(grid_e, grid_j, grid_m, indexing="ij")
    gp = np.column_stack([ee.ravel(), jj.ravel(), mm.ravel()])

    samples = np.column_stack([values_e, values_j, values_m])
    lam = np.asarray(values_l, dtype=float)

    out_num = np.zeros(len(gp), dtype=float)
    out_den = np.zeros(len(gp), dtype=float)
    bw2 = bandwidth ** 2

    for s, lv in zip(samples, lam):
        d2 = np.sum((gp - s) ** 2, axis=1)
        w = np.exp(-0.5 * d2 / np.maximum(bw2, EPS))
        out_num += w * lv
        out_den += w

    field = (out_num / np.maximum(out_den, EPS)).reshape(len(grid_e), len(grid_j), len(grid_m))
    return field


def invert_metric_3x3_field(g: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    flat = g.reshape(-1, 3, 3)
    inv_list: list[np.ndarray] = []
    det_list: list[float] = []

    for mat in flat:
        mat = 0.5 * (mat + mat.T)
        mat = mat + METRIC_REG * np.eye(3)

        det = np.linalg.det(mat)
        if (not np.isfinite(det)) or (abs(det) < DET_FLOOR):
            mat = mat + (10.0 * METRIC_REG) * np.eye(3)
            det = np.linalg.det(mat)

        try:
            inv = np.linalg.inv(mat)
        except np.linalg.LinAlgError:
            mat = mat + (100.0 * METRIC_REG) * np.eye(3)
            inv = np.linalg.inv(mat)
            det = np.linalg.det(mat)

        inv_list.append(inv)
        det_list.append(det)

    inv = np.array(inv_list).reshape(g.shape)
    det = np.array(det_list).reshape(g.shape[:-2])

    return inv, det


def tensor_frobenius_norm_3d(T: np.ndarray, g_inv: np.ndarray) -> np.ndarray:
    val = np.einsum("...ij,...ab,...ia,...jb->...", T, T, g_inv, g_inv)
    val = np.maximum(val, 0.0)
    return np.sqrt(val)


def build_metric_3d(
    phi_grid: np.ndarray,
    d_e: float,
    d_j: float,
    d_m: float,
) -> np.ndarray:
    phi_e, phi_j, phi_m = gradient_3d(phi_grid, d_e, d_j, d_m)

    if phi_grid.shape[0] < 3 or phi_grid.shape[1] < 3 or phi_grid.shape[2] < 3:
        g = np.zeros(phi_grid.shape + (3, 3), dtype=float)
        g[..., 0, 0] = METRIC_REG
        g[..., 1, 1] = METRIC_REG
        g[..., 2, 2] = METRIC_REG
        return g

    phi_ee = np.gradient(phi_e, d_e, axis=0, edge_order=2)
    phi_ej = np.gradient(phi_e, d_j, axis=1, edge_order=2)
    phi_em = np.gradient(phi_e, d_m, axis=2, edge_order=2)

    phi_je = np.gradient(phi_j, d_e, axis=0, edge_order=2)
    phi_jj = np.gradient(phi_j, d_j, axis=1, edge_order=2)
    phi_jm = np.gradient(phi_j, d_m, axis=2, edge_order=2)

    phi_me = np.gradient(phi_m, d_e, axis=0, edge_order=2)
    phi_mj = np.gradient(phi_m, d_j, axis=1, edge_order=2)
    phi_mm = np.gradient(phi_m, d_m, axis=2, edge_order=2)

    g = np.zeros(phi_grid.shape + (3, 3), dtype=float)
    g[..., 0, 0] = phi_ee + METRIC_REG
    g[..., 0, 1] = 0.5 * (phi_ej + phi_je)
    g[..., 0, 2] = 0.5 * (phi_em + phi_me)

    g[..., 1, 0] = g[..., 0, 1]
    g[..., 1, 1] = phi_jj + METRIC_REG
    g[..., 1, 2] = 0.5 * (phi_jm + phi_mj)

    g[..., 2, 0] = g[..., 0, 2]
    g[..., 2, 1] = g[..., 1, 2]
    g[..., 2, 2] = phi_mm + METRIC_REG

    return g


def metric_derivatives_3d(
    g: np.ndarray,
    d_e: float,
    d_j: float,
    d_m: float,
) -> np.ndarray:
    dg = np.zeros((3,) + g.shape, dtype=float)

    if g.shape[0] < 3 or g.shape[1] < 3 or g.shape[2] < 3:
        return dg

    for i in range(3):
        for j in range(3):
            dg[0, ..., i, j] = np.gradient(g[..., i, j], d_e, axis=0, edge_order=2)
            dg[1, ..., i, j] = np.gradient(g[..., i, j], d_j, axis=1, edge_order=2)
            dg[2, ..., i, j] = np.gradient(g[..., i, j], d_m, axis=2, edge_order=2)

    return dg


def christoffel_3d(g_inv: np.ndarray, dg: np.ndarray) -> np.ndarray:
    shape = g_inv.shape[:-2]
    gamma = np.zeros(shape + (3, 3, 3), dtype=float)

    for k in range(3):
        for i in range(3):
            for j in range(3):
                acc = np.zeros(shape, dtype=float)
                for l in range(3):
                    term = dg[i, ..., j, l] + dg[j, ..., i, l] - dg[l, ..., i, j]
                    acc += 0.5 * g_inv[..., k, l] * term
                gamma[..., k, i, j] = acc

    return np.clip(gamma, -CLIP_GAMMA, CLIP_GAMMA)


def gamma_derivatives_3d(
    gamma: np.ndarray,
    d_e: float,
    d_j: float,
    d_m: float,
) -> np.ndarray:
    dgamma = np.zeros((3,) + gamma.shape, dtype=float)

    if gamma.shape[0] < 3 or gamma.shape[1] < 3 or gamma.shape[2] < 3:
        return dgamma

    for k in range(3):
        for i in range(3):
            for j in range(3):
                dgamma[0, ..., k, i, j] = np.gradient(gamma[..., k, i, j], d_e, axis=0, edge_order=2)
                dgamma[1, ..., k, i, j] = np.gradient(gamma[..., k, i, j], d_j, axis=1, edge_order=2)
                dgamma[2, ..., k, i, j] = np.gradient(gamma[..., k, i, j], d_m, axis=2, edge_order=2)

    return dgamma


def ricci_tensor_3d(gamma: np.ndarray, dgamma: np.ndarray) -> np.ndarray:
    shape = gamma.shape[:-3]
    ric = np.zeros(shape + (3, 3), dtype=float)

    for i in range(3):
        for j in range(3):
            term1 = np.zeros(shape, dtype=float)
            term2 = np.zeros(shape, dtype=float)
            term3 = np.zeros(shape, dtype=float)
            term4 = np.zeros(shape, dtype=float)

            for k in range(3):
                term1 += dgamma[k, ..., k, i, j]
                term2 += dgamma[j, ..., k, i, k]

                inner3 = np.zeros(shape, dtype=float)
                inner4 = np.zeros(shape, dtype=float)

                for l in range(3):
                    inner3 += gamma[..., l, k, l]
                    inner4 += gamma[..., l, i, k] * gamma[..., k, j, l]

                term3 += gamma[..., k, i, j] * inner3
                term4 += inner4

            ric[..., i, j] = term1 - term2 + term3 - term4

    return ric


def scalar_curvature_3d(ric: np.ndarray, g_inv: np.ndarray) -> np.ndarray:
    return np.einsum("...ij,...ij->...", g_inv, ric)


def einstein_tensor_3d(
    ric: np.ndarray,
    scalar_r: np.ndarray,
    g: np.ndarray,
) -> np.ndarray:
    return ric - 0.5 * scalar_r[..., None, None] * g


# ==========================================
# MAIN FUNCTION
# ==========================================

def build_geodesic_field_full3d_90d(df: pd.DataFrame) -> pd.DataFrame:
    df = prepare_input_dataframe(df)

    values_e = df[E_COL].to_numpy(dtype=float)
    values_j = df[J_COL].to_numpy(dtype=float)

    # ======================================
    # 1. RECONSTRUIR CAMPO KDE E MALHA 2D
    # ======================================
    grid_e, grid_j, d_e, d_j = make_grid(values_e, values_j, GRID_N)

    rho_grid = fit_kde_density(
        values_e=values_e,
        values_j=values_j,
        grid_e=grid_e,
        grid_j=grid_j,
        bandwidth=BANDWIDTH,
    )

    phi_grid = -np.log(rho_grid + EPS)

    # ======================================
    # 2. GRADIENTE E HESSIANA DE PHI
    # ======================================
    phi_e_grid, phi_j_grid, phi_ee_grid, phi_ej_grid, phi_jj_grid = gradient_and_hessian(
        phi_grid=phi_grid,
        d_e=d_e,
        d_j=d_j,
    )

    grad_phi_norm_grid = np.sqrt(phi_e_grid ** 2 + phi_j_grid ** 2)

    # ======================================
    # 3. MÉTRICA LOCAL E CURVATURA PROXY
    # ======================================
    g_ee_grid = phi_ee_grid + METRIC_REG
    g_ej_grid = phi_ej_grid
    g_jj_grid = phi_jj_grid + METRIC_REG

    g_trace_grid = g_ee_grid + g_jj_grid
    g_det_grid = g_ee_grid * g_jj_grid - (g_ej_grid ** 2)

    g_det_safe_grid = g_det_grid.copy()
    mask_small = np.abs(g_det_safe_grid) < DET_FLOOR
    g_det_safe_grid[mask_small] = np.where(
        g_det_safe_grid[mask_small] >= 0.0,
        DET_FLOOR,
        -DET_FLOOR,
    )

    g_inv_ee_grid = g_jj_grid / g_det_safe_grid
    g_inv_ej_grid = -g_ej_grid / g_det_safe_grid
    g_inv_jj_grid = g_ee_grid / g_det_safe_grid

    field_curvature_grid = g_trace_grid

    # ======================================
    # 4. DERIVADAS ESPACIAIS REAIS DA MÉTRICA
    # ======================================
    if g_ee_grid.shape[0] >= 3 and g_ee_grid.shape[1] >= 3:
        dE_g_ee_grid, dJ_g_ee_grid = np.gradient(g_ee_grid, d_e, d_j, edge_order=2)
        dE_g_ej_grid, dJ_g_ej_grid = np.gradient(g_ej_grid, d_e, d_j, edge_order=2)
        dE_g_jj_grid, dJ_g_jj_grid = np.gradient(g_jj_grid, d_e, d_j, edge_order=2)
    else:
        zeros = np.zeros_like(g_ee_grid, dtype=float)
        dE_g_ee_grid, dJ_g_ee_grid = zeros.copy(), zeros.copy()
        dE_g_ej_grid, dJ_g_ej_grid = zeros.copy(), zeros.copy()
        dE_g_jj_grid, dJ_g_jj_grid = zeros.copy(), zeros.copy()

    # ======================================
    # 5. CHRISTOFFELS NA MALHA
    # ======================================
    gamma_e_ee_grid = 0.5 * (
        g_inv_ee_grid * dE_g_ee_grid
        + g_inv_ej_grid * (2.0 * dE_g_ej_grid - dJ_g_ee_grid)
    )

    gamma_e_ej_grid = 0.5 * (
        g_inv_ee_grid * dJ_g_ee_grid
        + g_inv_ej_grid * dE_g_jj_grid
    )

    gamma_e_jj_grid = 0.5 * (
        g_inv_ee_grid * (2.0 * dJ_g_ej_grid - dE_g_jj_grid)
        + g_inv_ej_grid * dJ_g_jj_grid
    )

    gamma_j_ee_grid = 0.5 * (
        g_inv_ej_grid * dE_g_ee_grid
        + g_inv_jj_grid * (2.0 * dE_g_ej_grid - dJ_g_ee_grid)
    )

    gamma_j_ej_grid = 0.5 * (
        g_inv_ej_grid * dJ_g_ee_grid
        + g_inv_jj_grid * dE_g_jj_grid
    )

    gamma_j_jj_grid = 0.5 * (
        g_inv_ej_grid * (2.0 * dJ_g_ej_grid - dE_g_jj_grid)
        + g_inv_jj_grid * dJ_g_jj_grid
    )

    gamma_e_ee_grid = np.clip(gamma_e_ee_grid, -CLIP_GAMMA, CLIP_GAMMA)
    gamma_e_ej_grid = np.clip(gamma_e_ej_grid, -CLIP_GAMMA, CLIP_GAMMA)
    gamma_e_jj_grid = np.clip(gamma_e_jj_grid, -CLIP_GAMMA, CLIP_GAMMA)
    gamma_j_ee_grid = np.clip(gamma_j_ee_grid, -CLIP_GAMMA, CLIP_GAMMA)
    gamma_j_ej_grid = np.clip(gamma_j_ej_grid, -CLIP_GAMMA, CLIP_GAMMA)
    gamma_j_jj_grid = np.clip(gamma_j_jj_grid, -CLIP_GAMMA, CLIP_GAMMA)

    # ======================================
    # 6. INTERPOLAR TUDO PARA CADA CANDLE
    # ======================================
    df["rho_field"] = bilinear_interp(grid_e, grid_j, rho_grid, values_e, values_j)
    df["phi_field"] = bilinear_interp(grid_e, grid_j, phi_grid, values_e, values_j)

    df["grad_phi_e"] = bilinear_interp(grid_e, grid_j, phi_e_grid, values_e, values_j)
    df["grad_phi_j"] = bilinear_interp(grid_e, grid_j, phi_j_grid, values_e, values_j)
    df["grad_phi_norm"] = bilinear_interp(grid_e, grid_j, grad_phi_norm_grid, values_e, values_j)

    df["hess_phi_ee"] = bilinear_interp(grid_e, grid_j, phi_ee_grid, values_e, values_j)
    df["hess_phi_ej"] = bilinear_interp(grid_e, grid_j, phi_ej_grid, values_e, values_j)
    df["hess_phi_jj"] = bilinear_interp(grid_e, grid_j, phi_jj_grid, values_e, values_j)

    df["g_ee"] = bilinear_interp(grid_e, grid_j, g_ee_grid, values_e, values_j)
    df["g_ej"] = bilinear_interp(grid_e, grid_j, g_ej_grid, values_e, values_j)
    df["g_jj"] = bilinear_interp(grid_e, grid_j, g_jj_grid, values_e, values_j)

    df["g_trace"] = bilinear_interp(grid_e, grid_j, g_trace_grid, values_e, values_j)
    df["g_det"] = bilinear_interp(grid_e, grid_j, g_det_grid, values_e, values_j)
    df["g_det_safe"] = bilinear_interp(grid_e, grid_j, g_det_safe_grid, values_e, values_j)

    df["g_inv_ee"] = bilinear_interp(grid_e, grid_j, g_inv_ee_grid, values_e, values_j)
    df["g_inv_ej"] = bilinear_interp(grid_e, grid_j, g_inv_ej_grid, values_e, values_j)
    df["g_inv_jj"] = bilinear_interp(grid_e, grid_j, g_inv_jj_grid, values_e, values_j)

    df["field_curvature"] = bilinear_interp(grid_e, grid_j, field_curvature_grid, values_e, values_j)

    df["dE_g_ee"] = bilinear_interp(grid_e, grid_j, dE_g_ee_grid, values_e, values_j)
    df["dJ_g_ee"] = bilinear_interp(grid_e, grid_j, dJ_g_ee_grid, values_e, values_j)
    df["dE_g_ej"] = bilinear_interp(grid_e, grid_j, dE_g_ej_grid, values_e, values_j)
    df["dJ_g_ej"] = bilinear_interp(grid_e, grid_j, dJ_g_ej_grid, values_e, values_j)
    df["dE_g_jj"] = bilinear_interp(grid_e, grid_j, dE_g_jj_grid, values_e, values_j)
    df["dJ_g_jj"] = bilinear_interp(grid_e, grid_j, dJ_g_jj_grid, values_e, values_j)

    df["gamma_e_ee"] = bilinear_interp(grid_e, grid_j, gamma_e_ee_grid, values_e, values_j)
    df["gamma_e_ej"] = bilinear_interp(grid_e, grid_j, gamma_e_ej_grid, values_e, values_j)
    df["gamma_e_jj"] = bilinear_interp(grid_e, grid_j, gamma_e_jj_grid, values_e, values_j)
    df["gamma_j_ee"] = bilinear_interp(grid_e, grid_j, gamma_j_ee_grid, values_e, values_j)
    df["gamma_j_ej"] = bilinear_interp(grid_e, grid_j, gamma_j_ej_grid, values_e, values_j)
    df["gamma_j_jj"] = bilinear_interp(grid_e, grid_j, gamma_j_jj_grid, values_e, values_j)

    # ======================================
    # 7. MEMÓRIA GEOMÉTRICA E INCOERÊNCIA
    # ======================================
    df["mem_e"] = ema(df[E_COL], alpha=ALPHA_E)
    df["mem_j"] = ema(df[J_COL], alpha=ALPHA_J)

    d_mem_e = df[E_COL] - df["mem_e"]
    d_mem_j = df[J_COL] - df["mem_j"]

    df["geom_incoherence"] = (
        df["g_ee"] * (d_mem_e ** 2)
        + 2.0 * df["g_ej"] * d_mem_e * d_mem_j
        + df["g_jj"] * (d_mem_j ** 2)
    )
    df["geom_incoherence_abs"] = df["geom_incoherence"].abs()

    # ======================================
    # 8. CINEMÁTICA OBSERVADA
    # ======================================
    df["vel_e"] = df[E_COL].diff()
    df["vel_j"] = df[J_COL].diff()

    df["acc_obs_e"] = df[E_COL].diff().diff()
    df["acc_obs_j"] = df[J_COL].diff().diff()

    df["acc_obs_e"] = df["acc_obs_e"].fillna(0.0)
    df["acc_obs_j"] = df["acc_obs_j"].fillna(0.0)

    # ======================================
    # 9. ACELERAÇÃO GEODÉSICA
    # ======================================
    vE = df["vel_e"]
    vJ = df["vel_j"]

    df["acc_geo_e"] = -(
        df["gamma_e_ee"] * (vE ** 2)
        + 2.0 * df["gamma_e_ej"] * vE * vJ
        + df["gamma_e_jj"] * (vJ ** 2)
    )

    df["acc_geo_j"] = -(
        df["gamma_j_ee"] * (vE ** 2)
        + 2.0 * df["gamma_j_ej"] * vE * vJ
        + df["gamma_j_jj"] * (vJ ** 2)
    )

    df["acc_geo_e"] = clip_series(df["acc_geo_e"], -CLIP_ACC, CLIP_ACC)
    df["acc_geo_j"] = clip_series(df["acc_geo_j"], -CLIP_ACC, CLIP_ACC)

    df["acc_geo_norm"] = np.sqrt(df["acc_geo_e"] ** 2 + df["acc_geo_j"] ** 2)

    # ======================================
    # 10. RESIDUAL GEODÉSICO
    # ======================================
    df["geo_resid_e"] = df["acc_obs_e"] - df["acc_geo_e"]
    df["geo_resid_j"] = df["acc_obs_j"] - df["acc_geo_j"]
    df["geo_resid_norm"] = np.sqrt(df["geo_resid_e"] ** 2 + df["geo_resid_j"] ** 2)

    # ======================================
    # 11. TERMOS AUXILIARES
    # ======================================
    lambda_safe = df[L_COL].abs().fillna(0.0) + EPS
    df["jerk_over_lambda"] = df[J_COL].abs().fillna(0.0) / lambda_safe

    # ======================================
    # 12. STRESS GEODÉSICO
    # ======================================
    df["field_stress_geodesic"] = (
        W_INCOH * df["geom_incoherence_abs"]
        + W_GRAD * df["grad_phi_norm"].abs()
        + W_GEO_RESID * df["geo_resid_norm"]
        + W_ACC_GEO * df["acc_geo_norm"]
        + W_CURVATURE * df["field_curvature"].abs()
        + W_JERK_OVER_LAMBDA * df["jerk_over_lambda"]
    )

    # ======================================
    # 13. SCORE LOGÍSTICO GEODÉSICO
    # ======================================
    score = (
        B0
        + B1 * df["geo_resid_norm"]
        + B2 * df["acc_geo_norm"]
        + B3 * df["grad_phi_norm"].abs()
        + B4 * df["geom_incoherence_abs"]
        + B5 * df["field_curvature"].abs()
        + B6 * df["jerk_over_lambda"]
    )
    df["rupture_prob_geodesic"] = sigmoid(score)

    # ======================================
    # 14. CAMADA 3D - GRAVIDADE INFORMACIONAL
    # ======================================
    df["memory_flux"] = df["mem_e"].diff().fillna(0.0)

    values_m = df["memory_flux"].to_numpy(dtype=float)
    values_l = df[L_COL].to_numpy(dtype=float)

    grid_e3 = make_axis_1d(values_e, GRID_N_E3)
    grid_j3 = make_axis_1d(values_j, GRID_N_J3)
    grid_m3 = make_axis_1d(values_m, GRID_N_M3)

    d_e3 = float(grid_e3[1] - grid_e3[0]) if len(grid_e3) > 1 else 1.0
    d_j3 = float(grid_j3[1] - grid_j3[0]) if len(grid_j3) > 1 else 1.0
    d_m3 = float(grid_m3[1] - grid_m3[0]) if len(grid_m3) > 1 else 1.0

    rho_grid_3d = fit_kde_density_3d(
        values_e=values_e,
        values_j=values_j,
        values_m=values_m,
        grid_e=grid_e3,
        grid_j=grid_j3,
        grid_m=grid_m3,
        bandwidth=BANDWIDTH_3D,
    )

    phi_grid_3d = -np.log(rho_grid_3d + EPS)

    g3 = build_metric_3d(phi_grid_3d, d_e3, d_j3, d_m3)
    g3_inv, g3_det = invert_metric_3x3_field(g3)

    phi_e3, phi_j3, phi_m3 = gradient_3d(phi_grid_3d, d_e3, d_j3, d_m3)
    grad_phi_norm_3d = np.sqrt(phi_e3 ** 2 + phi_j3 ** 2 + phi_m3 ** 2)

    lambda_field_3d = build_lambda_field_3d(
        values_e=values_e,
        values_j=values_j,
        values_m=values_m,
        values_l=values_l,
        grid_e=grid_e3,
        grid_j=grid_j3,
        grid_m=grid_m3,
        bandwidth=BANDWIDTH_3D,
    )

    lam_e3, lam_j3, lam_m3 = gradient_3d(lambda_field_3d, d_e3, d_j3, d_m3)

    grad_phi_vec = np.stack([phi_e3, phi_j3, phi_m3], axis=-1)
    grad_lam_vec = np.stack([lam_e3, lam_j3, lam_m3], axis=-1)

    grad_phi_sq = np.einsum("...i,...ij,...j->...", grad_phi_vec, g3_inv, grad_phi_vec)
    grad_lam_sq = np.einsum("...i,...ij,...j->...", grad_lam_vec, g3_inv, grad_lam_vec)

    outer_phi = np.einsum("...i,...j->...ij", grad_phi_vec, grad_phi_vec)
    outer_lam = np.einsum("...i,...j->...ij", grad_lam_vec, grad_lam_vec)

    T_info = (
        W_PHI_STRESS * outer_phi
        + W_MEM_STRESS * outer_lam
        + W_LAMBDA_STRESS * lambda_field_3d[..., None, None] * g3
        - 0.5 * (
            W_PHI_STRESS * grad_phi_sq + W_MEM_STRESS * grad_lam_sq
        )[..., None, None] * g3
    )

    T_info_norm = tensor_frobenius_norm_3d(T_info, g3_inv)

    dg3 = metric_derivatives_3d(g3, d_e3, d_j3, d_m3)
    gamma3 = christoffel_3d(g3_inv, dg3)
    dgamma3 = gamma_derivatives_3d(gamma3, d_e3, d_j3, d_m3)

    ric3 = ricci_tensor_3d(gamma3, dgamma3)
    scalar_R3 = scalar_curvature_3d(ric3, g3_inv)
    scalar_R3 = np.clip(scalar_R3, -CLIP_CURV_3D, CLIP_CURV_3D)

    G_info = einstein_tensor_3d(ric3, scalar_R3, g3)
    G_info_norm = tensor_frobenius_norm_3d(G_info, g3_inv)

    field_gravity_grid = (
        KAPPA_INFO
        * np.sign(scalar_R3)
        * np.log1p(np.abs(scalar_R3))
        * np.log1p(np.abs(T_info_norm))
        * np.log1p(np.abs(G_info_norm))
    )
    field_gravity_grid = np.clip(field_gravity_grid, -CLIP_FIELD_GRAVITY, CLIP_FIELD_GRAVITY)

    df["field_curvature_scalar"] = trilinear_interp(
        grid_e3, grid_j3, grid_m3, scalar_R3,
        values_e, values_j, values_m
    )

    df["field_stress_tensor_norm"] = trilinear_interp(
        grid_e3, grid_j3, grid_m3, T_info_norm,
        values_e, values_j, values_m
    )

    df["field_einstein_norm"] = trilinear_interp(
        grid_e3, grid_j3, grid_m3, G_info_norm,
        values_e, values_j, values_m
    )

    df["field_gravity"] = trilinear_interp(
        grid_e3, grid_j3, grid_m3, field_gravity_grid,
        values_e, values_j, values_m
    )

    df["gravitational_stress_score"] = (
        np.sign(df["field_curvature_scalar"].fillna(0.0))
        * np.log1p(np.abs(df["field_curvature_scalar"].fillna(0.0)))
        * np.log1p(np.abs(df["field_stress_tensor_norm"].fillna(0.0)))
    )

    for i in range(3):
        for j in range(3):
            df[f"G_info_{i}{j}"] = trilinear_interp(
                grid_e3, grid_j3, grid_m3, G_info[..., i, j],
                values_e, values_j, values_m
            )

    for i in range(3):
        for j in range(3):
            df[f"T_info_{i}{j}"] = trilinear_interp(
                grid_e3, grid_j3, grid_m3, T_info[..., i, j],
                values_e, values_j, values_m
            )

    df["field_grid_n_3d_e"] = GRID_N_E3
    df["field_grid_n_3d_j"] = GRID_N_J3
    df["field_grid_n_3d_m"] = GRID_N_M3
    df["field_bandwidth_3d"] = BANDWIDTH_3D
    df["kappa_info"] = KAPPA_INFO

    # ======================================
    # 15. VALIDADE OPERACIONAL
    # ======================================
    op_cols = [
        "vel_e", "vel_j",
        "acc_obs_e", "acc_obs_j",
        "acc_geo_e", "acc_geo_j",
        "geo_resid_e", "geo_resid_j",
        "field_stress_geodesic",
        "rupture_prob_geodesic",
        "field_gravity",
        "field_curvature_scalar",
        "field_einstein_norm",
    ]
    df["geodesic_valid"] = (~df[op_cols].isna().any(axis=1)).astype(int)

    df["field_grid_n"] = GRID_N
    df["field_bandwidth"] = BANDWIDTH

    # ======================================
    # 16. HARDENING FINAL PARA LIVE
    # ======================================
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)

    fill_zero_cols = [
        "rho_field",
        "phi_field",
        "grad_phi_e",
        "grad_phi_j",
        "grad_phi_norm",
        "hess_phi_ee",
        "hess_phi_ej",
        "hess_phi_jj",
        "g_ee",
        "g_ej",
        "g_jj",
        "g_trace",
        "g_det",
        "g_det_safe",
        "g_inv_ee",
        "g_inv_ej",
        "g_inv_jj",
        "field_curvature",
        "dE_g_ee",
        "dJ_g_ee",
        "dE_g_ej",
        "dJ_g_ej",
        "dE_g_jj",
        "dJ_g_jj",
        "gamma_e_ee",
        "gamma_e_ej",
        "gamma_e_jj",
        "gamma_j_ee",
        "gamma_j_ej",
        "gamma_j_jj",
        "mem_e",
        "mem_j",
        "geom_incoherence",
        "geom_incoherence_abs",
        "vel_e",
        "vel_j",
        "acc_obs_e",
        "acc_obs_j",
        "acc_geo_e",
        "acc_geo_j",
        "acc_geo_norm",
        "geo_resid_e",
        "geo_resid_j",
        "geo_resid_norm",
        "jerk_over_lambda",
        "field_stress_geodesic",
        "rupture_prob_geodesic",
        "memory_flux",
        "field_curvature_scalar",
        "field_stress_tensor_norm",
        "field_einstein_norm",
        "field_gravity",
        "gravitational_stress_score",
        "field_grid_n_3d_e",
        "field_grid_n_3d_j",
        "field_grid_n_3d_m",
        "field_bandwidth_3d",
        "kappa_info",
        "field_grid_n",
        "field_bandwidth",
    ]

    critical_physics_cols = [
        "field_stress_geodesic",
        "geo_resid_norm",
        "acc_geo_norm",
        "grad_phi_norm",
        "geom_incoherence_abs",
        "jerk_over_lambda",
    ]

    for col in fill_zero_cols:
        if col in df.columns:
            if col in critical_physics_cols:
                # NÃO zerar
                continue
            df[col] = df[col].fillna(0.0)

   
    
    for i in range(3):
        for j in range(3):
            g_col = f"G_info_{i}{j}"
            t_col = f"T_info_{i}{j}"
            if g_col in df.columns:
                df[g_col] = pd.to_numeric(df[g_col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
            if t_col in df.columns:
                df[t_col] = pd.to_numeric(df[t_col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    
     # Desfragmenta antes de inserir nova coluna
    
    df = df.copy()
    df["stress_valid"] = (
        pd.to_numeric(df["field_stress_geodesic"], errors="coerce").notna()
    ).astype(int)

    return df


# ==========================================
# DEBUG / LOCAL
# ==========================================

def main() -> None:
    print("=" * 72)
    print("SGV GEODESIC FIELD FULL")
    print("=" * 72)
    print("entrada :", INPUT)
    print("saida   :", OUTPUT)

    if not INPUT.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {INPUT}")

    raw_df = pd.read_csv(INPUT)
    out = build_geodesic_field_full3d_90d(raw_df)

    print("\nResumo das features geodésicas:")
    summary_cols = [
        "g_trace",
        "g_det",
        "acc_geo_norm",
        "geo_resid_norm",
        "field_stress_geodesic",
        "rupture_prob_geodesic",
        "field_curvature_scalar",
        "field_einstein_norm",
        "field_gravity",
    ]
    summary_cols = [c for c in summary_cols if c in out.columns]
    print(out[summary_cols].describe().T[["mean", "std", "min", "max"]].round(6))

    out.to_csv(OUTPUT, index=False)

    print("\nArquivo salvo com sucesso.")
    print("saida:", OUTPUT)
    print("=" * 72)


if __name__ == "__main__":
    main()