"""Rota de grade dos scripts originais (C3/3.A desligados).

Código portado de ``legacy/sgv_geodesic_field_full3d_90d_refactored.py`` e
``legacy/sgv_build_information_field_refactored_cache.py`` com as constantes
virando parâmetros. A única mudança é o campo de λ (Nadaraya–Watson), que era
um laço amostra a amostra e agora soma em blocos vetorizados: o resultado é o
mesmo até o arredondamento de ponto flutuante.
"""
from __future__ import annotations

import numpy as np
from sklearn.neighbors import KernelDensity


def make_grid(values_e, values_j, grid_n, q_low, q_high, eps):
    values_e = np.asarray(values_e, dtype=float)
    values_j = np.asarray(values_j, dtype=float)
    e_lo, e_hi = np.quantile(values_e, [q_low, q_high])
    j_lo, j_hi = np.quantile(values_j, [q_low, q_high])
    e_span = max(e_hi - e_lo, eps)
    j_span = max(j_hi - j_lo, eps)
    e_min = e_lo - 0.10 * e_span
    e_max = e_hi + 0.10 * e_span
    j_min = j_lo - 0.10 * j_span
    j_max = j_hi + 0.10 * j_span
    grid_e = np.linspace(e_min, e_max, grid_n)
    grid_j = np.linspace(j_min, j_max, grid_n)
    d_e = float(grid_e[1] - grid_e[0]) if grid_n > 1 else 1.0
    d_j = float(grid_j[1] - grid_j[0]) if grid_n > 1 else 1.0
    return grid_e, grid_j, d_e, d_j


def fit_kde_density(values_e, values_j, grid_e, grid_j, bandwidth):
    samples = np.column_stack([values_e, values_j])
    kde = KernelDensity(kernel="gaussian", bandwidth=bandwidth)
    kde.fit(samples)
    ee, jj = np.meshgrid(grid_e, grid_j, indexing="ij")
    grid_points = np.column_stack([ee.ravel(), jj.ravel()])
    log_density = kde.score_samples(grid_points)
    return np.exp(log_density).reshape(len(grid_e), len(grid_j))


def bilinear_interp(grid_e, grid_j, grid_values, e_points, j_points, eps):
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
    de = np.maximum(e1 - e0, eps)
    dj = np.maximum(j1 - j0, eps)
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


def gradient_and_hessian(phi_grid, d_e, d_j):
    if phi_grid.shape[0] < 3 or phi_grid.shape[1] < 3:
        zeros = np.zeros_like(phi_grid, dtype=float)
        return zeros, zeros, zeros, zeros, zeros
    phi_e, phi_j = np.gradient(phi_grid, d_e, d_j, edge_order=2)
    phi_ee, phi_ej = np.gradient(phi_e, d_e, d_j, edge_order=2)
    _, phi_jj = np.gradient(phi_j, d_e, d_j, edge_order=2)
    return phi_e, phi_j, phi_ee, phi_ej, phi_jj


# ------------------------------------------------------------------ 3D
def make_axis_1d(values, n, q_low, q_high, eps):
    values = np.asarray(values, dtype=float)
    lo, hi = np.quantile(values, [q_low, q_high])
    span = max(hi - lo, eps)
    return np.linspace(lo - 0.10 * span, hi + 0.10 * span, n)


def trilinear_interp(grid_e, grid_j, grid_m, grid_values, e_points, j_points, m_points, eps):
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
    de = np.maximum(e1 - e0, eps)
    dj = np.maximum(j1 - j0, eps)
    dm = np.maximum(m1 - m0, eps)
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


def fit_kde_density_3d(values_e, values_j, values_m, grid_e, grid_j, grid_m, bandwidth):
    samples = np.column_stack([values_e, values_j, values_m])
    kde = KernelDensity(kernel="gaussian", bandwidth=bandwidth)
    kde.fit(samples)
    ee, jj, mm = np.meshgrid(grid_e, grid_j, grid_m, indexing="ij")
    grid_points = np.column_stack([ee.ravel(), jj.ravel(), mm.ravel()])
    log_density = kde.score_samples(grid_points)
    return np.exp(log_density).reshape(len(grid_e), len(grid_j), len(grid_m))


def gradient_3d(arr, d_e, d_j, d_m):
    if arr.shape[0] < 3 or arr.shape[1] < 3 or arr.shape[2] < 3:
        zeros = np.zeros_like(arr, dtype=float)
        return zeros, zeros, zeros
    return np.gradient(arr, d_e, d_j, d_m, edge_order=2)


def build_lambda_field_3d(values_e, values_j, values_m, values_l, grid_e, grid_j, grid_m, bandwidth, eps,
                          chunk: int = 128):
    """Nadaraya–Watson de λ na grade (3.3): somas vetorizadas por bloco de amostras."""
    ee, jj, mm = np.meshgrid(grid_e, grid_j, grid_m, indexing="ij")
    gp = np.column_stack([ee.ravel(), jj.ravel(), mm.ravel()])
    samples = np.column_stack([values_e, values_j, values_m])
    lam = np.asarray(values_l, dtype=float)
    out_num = np.zeros(len(gp), dtype=float)
    out_den = np.zeros(len(gp), dtype=float)
    bw2 = bandwidth ** 2
    gp_sq = np.einsum("gd,gd->g", gp, gp)
    for s0 in range(0, len(samples), chunk):
        s = samples[s0:s0 + chunk]
        lv = lam[s0:s0 + chunk]
        d2 = gp_sq[:, None] + np.einsum("sd,sd->s", s, s)[None, :] - 2.0 * gp @ s.T
        d2 = np.maximum(d2, 0.0)
        w = np.exp(-0.5 * d2 / np.maximum(bw2, eps))
        out_num += w @ lv
        out_den += w.sum(axis=1)
    return (out_num / np.maximum(out_den, eps)).reshape(len(grid_e), len(grid_j), len(grid_m))


def invert_metric_3x3_field(g, metric_reg, det_floor):
    flat = g.reshape(-1, 3, 3)
    inv_list = []
    det_list = []
    for mat in flat:
        mat = 0.5 * (mat + mat.T)
        mat = mat + metric_reg * np.eye(3)
        det = np.linalg.det(mat)
        if (not np.isfinite(det)) or (abs(det) < det_floor):
            mat = mat + (10.0 * metric_reg) * np.eye(3)
            det = np.linalg.det(mat)
        try:
            inv = np.linalg.inv(mat)
        except np.linalg.LinAlgError:
            mat = mat + (100.0 * metric_reg) * np.eye(3)
            inv = np.linalg.inv(mat)
            det = np.linalg.det(mat)
        inv_list.append(inv)
        det_list.append(det)
    inv = np.array(inv_list).reshape(g.shape)
    det = np.array(det_list).reshape(g.shape[:-2])
    return inv, det


def tensor_frobenius_norm_3d(T, g_inv):
    val = np.einsum("...ij,...ab,...ia,...jb->...", T, T, g_inv, g_inv)
    val = np.maximum(val, 0.0)
    return np.sqrt(val)


def build_metric_3d(phi_grid, d_e, d_j, d_m, metric_reg):
    phi_e, phi_j, phi_m = gradient_3d(phi_grid, d_e, d_j, d_m)
    if phi_grid.shape[0] < 3 or phi_grid.shape[1] < 3 or phi_grid.shape[2] < 3:
        g = np.zeros(phi_grid.shape + (3, 3), dtype=float)
        g[..., 0, 0] = metric_reg
        g[..., 1, 1] = metric_reg
        g[..., 2, 2] = metric_reg
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
    g[..., 0, 0] = phi_ee + metric_reg
    g[..., 0, 1] = 0.5 * (phi_ej + phi_je)
    g[..., 0, 2] = 0.5 * (phi_em + phi_me)
    g[..., 1, 0] = g[..., 0, 1]
    g[..., 1, 1] = phi_jj + metric_reg
    g[..., 1, 2] = 0.5 * (phi_jm + phi_mj)
    g[..., 2, 0] = g[..., 0, 2]
    g[..., 2, 1] = g[..., 1, 2]
    g[..., 2, 2] = phi_mm + metric_reg
    return g


def metric_derivatives_3d(g, d_e, d_j, d_m):
    dg = np.zeros((3,) + g.shape, dtype=float)
    if g.shape[0] < 3 or g.shape[1] < 3 or g.shape[2] < 3:
        return dg
    for i in range(3):
        for j in range(3):
            dg[0, ..., i, j] = np.gradient(g[..., i, j], d_e, axis=0, edge_order=2)
            dg[1, ..., i, j] = np.gradient(g[..., i, j], d_j, axis=1, edge_order=2)
            dg[2, ..., i, j] = np.gradient(g[..., i, j], d_m, axis=2, edge_order=2)
    return dg


def christoffel_3d(g_inv, dg, clip_gamma):
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
    return np.clip(gamma, -clip_gamma, clip_gamma)


def gamma_derivatives_3d(gamma, d_e, d_j, d_m):
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


def ricci_tensor_3d(gamma, dgamma):
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


def scalar_curvature_3d(ric, g_inv):
    return np.einsum("...ij,...ij->...", g_inv, ric)


def einstein_tensor_3d(ric, scalar_r, g):
    return ric - 0.5 * scalar_r[..., None, None] * g
