"""Geometria da métrica: projeção PSD (C4) e curvatura (3.A).

Para métrica Hessiana g_ij = ∂_i∂_jφ:

    Γ^k_ij = ½ g^{kl} φ_ijl
    R_ij   = ¼ (B_ij - A_ij)
        A_ij = φ_ijl v^l,  v^l = g^{lb} t_b,  t_b = g^{ka} φ_kab
        B_ij = tr(Φ_i g⁻¹ Φ_j g⁻¹),  (Φ_i)_kl = φ_ikl

Essa forma do Ricci foi obtida substituindo Γ = ½ g⁻¹ ∂³φ na mesma fórmula
usada pelos scripts originais,
    R_ij = ∂_kΓ^k_ij - ∂_jΓ^k_ik + Γ^k_ij Γ^l_kl - Γ^l_ik Γ^k_jl,
e as derivadas quartas de φ se cancelam. A convenção de sinal é, portanto, a
mesma do código original; o teste ``tests/test_geometry.py`` confirma isso
numericamente.
"""
from __future__ import annotations

import numpy as np


# ----------------------------------------------------------------------
# C4 — projeção PSD
# ----------------------------------------------------------------------
def project_psd(G: np.ndarray, floor: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """SoftAbs: autovalores λ → max(|λ|, floor).

    Retorna (G_psd, alterada, menor_autovalor_original). Linhas com NaN
    continuam NaN.
    """
    G = np.asarray(G, dtype=float)
    shape = G.shape
    flat = G.reshape(-1, shape[-2], shape[-1])
    out = np.full_like(flat, np.nan)
    changed = np.zeros(flat.shape[0], dtype=bool)
    min_eig = np.full(flat.shape[0], np.nan)
    ok = np.isfinite(flat).all(axis=(1, 2))
    if ok.any():
        sym = 0.5 * (flat[ok] + np.swapaxes(flat[ok], 1, 2))
        evals, evecs = np.linalg.eigh(sym)
        new = np.maximum(np.abs(evals), floor)
        out[ok] = np.einsum("nij,nj,nkj->nik", evecs, new, evecs)
        changed[ok] = (evals < floor).any(axis=1)
        min_eig[ok] = evals.min(axis=1)
    return out.reshape(shape), changed.reshape(shape[:-2]), min_eig.reshape(shape[:-2])


def safe_inv(G: np.ndarray) -> np.ndarray:
    G = np.asarray(G, dtype=float)
    out = np.full_like(G, np.nan)
    flat_g = G.reshape(-1, G.shape[-2], G.shape[-1])
    flat_o = out.reshape(-1, G.shape[-2], G.shape[-1])
    ok = np.isfinite(flat_g).all(axis=(1, 2))
    if ok.any():
        try:
            flat_o[ok] = np.linalg.inv(flat_g[ok])
        except np.linalg.LinAlgError:
            # uma matriz singular não derruba o lote: pseudo-inversa só onde precisa
            for i in np.where(ok)[0]:
                try:
                    flat_o[i] = np.linalg.inv(flat_g[i])
                except np.linalg.LinAlgError:
                    flat_o[i] = np.linalg.pinv(flat_g[i])
    return flat_o.reshape(G.shape)


# ----------------------------------------------------------------------
# 3.A — geometria Hessiana exata
# ----------------------------------------------------------------------
def christoffel_hessian(g_inv: np.ndarray, phi3: np.ndarray) -> np.ndarray:
    """Γ[..., k, i, j] = ½ g^{kl} φ_ijl."""
    return 0.5 * np.einsum("...kl,...ijl->...kij", g_inv, phi3)


def ricci_hessian(g_inv: np.ndarray, phi3: np.ndarray) -> np.ndarray:
    t = np.einsum("...ka,...kab->...b", g_inv, phi3)
    v = np.einsum("...lb,...b->...l", g_inv, t)
    A = np.einsum("...ijl,...l->...ij", phi3, v)
    Mx = np.einsum("...ikl,...la->...ika", phi3, g_inv)
    B = np.einsum("...ika,...jak->...ij", Mx, Mx)
    return 0.25 * (B - A)


# ----------------------------------------------------------------------
# Rota geral (diferenças finitas sobre a métrica)
# ----------------------------------------------------------------------
def christoffel_general(g_inv: np.ndarray, dg: np.ndarray) -> np.ndarray:
    """dg[..., m, i, j] = ∂_m g_ij  →  Γ[..., k, i, j].

    T[..., i, j, l] = ∂_i g_jl + ∂_j g_il - ∂_l g_ij
    """
    T = dg + np.swapaxes(dg, -3, -2) - np.moveaxis(dg, -3, -1)
    return 0.5 * np.einsum("...kl,...ijl->...kij", g_inv, T)


def ricci_general(gamma: np.ndarray, dgamma: np.ndarray) -> np.ndarray:
    """Mesma fórmula do script original.

    gamma[..., k, i, j] = Γ^k_ij;  dgamma[..., m, k, i, j] = ∂_m Γ^k_ij.
    """
    term1 = np.einsum("...kkij->...ij", dgamma)
    term2 = np.einsum("...jkik->...ij", dgamma)
    trace = np.einsum("...lkl->...k", gamma)
    term3 = np.einsum("...kij,...k->...ij", gamma, trace)
    term4 = np.einsum("...lik,...kjl->...ij", gamma, gamma)
    return term1 - term2 + term3 - term4


def scalar_curvature(ric: np.ndarray, g_inv: np.ndarray) -> np.ndarray:
    return np.einsum("...ij,...ij->...", g_inv, ric)


def einstein_tensor(ric: np.ndarray, R: np.ndarray, g: np.ndarray) -> np.ndarray:
    return ric - 0.5 * R[..., None, None] * g


def tensor_inner(A: np.ndarray, B: np.ndarray, g_inv: np.ndarray) -> np.ndarray:
    return np.einsum("...ij,...ab,...ia,...jb->...", A, B, g_inv, g_inv)


def tensor_norm(T: np.ndarray, g_inv: np.ndarray, check_psd: bool = False) -> np.ndarray:
    """|T| = sqrt(T_ij T_ab g^ia g^jb).

    Com métrica positiva definida o radicando nunca é negativo (3.5): com
    ``check_psd=True`` um valor negativo além do arredondamento é erro, em vez
    de ser escondido pelo max(·, 0) do original.
    """
    val = tensor_inner(T, T, g_inv)
    if check_psd:
        scale = np.einsum("...ij,...ij->...", T, T) * np.abs(np.einsum("...ii->...", g_inv)) ** 2
        bad = val < -1e-9 * np.maximum(scale, 1e-300)
        if np.any(bad[np.isfinite(val)]):
            raise AssertionError("norma tensorial negativa com métrica PSD: problema numérico")
    return np.sqrt(np.maximum(val, 0.0))


# ----------------------------------------------------------------------
# Diferenças finitas sobre um campo de métrica dado por função
# ----------------------------------------------------------------------
def fd_christoffel(metric_fn, X: np.ndarray, delta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Γ por diferenças centrais de ``metric_fn`` (pontos → métricas).

    Retorna (Γ, ∂g, g) nos pontos X.
    """
    X = np.atleast_2d(X)
    N, d = X.shape
    stacks = [X]
    for k in range(d):
        e = np.zeros(d)
        e[k] = delta
        stacks += [X + e, X - e]
    G_all = metric_fn(np.vstack(stacks)).reshape(1 + 2 * d, N, d, d)
    g0 = G_all[0]
    dg = np.empty((N, d, d, d))
    for k in range(d):
        dg[:, k] = (G_all[1 + 2 * k] - G_all[2 + 2 * k]) / (2.0 * delta)
    g_inv = safe_inv(g0)
    return christoffel_general(g_inv, dg), dg, g0


def fd_ricci(metric_fn, X: np.ndarray, delta: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ricci pela fórmula geral, com ∂g e ∂Γ por diferenças centrais.

    A métrica é avaliada uma única vez nos pontos distintos do estêncil
    (1 + 2d + 2d(d-1) + 2d pontos; 25 em 3D). Retorna (Ricci, Γ, g) em X.
    """
    X = np.atleast_2d(X)
    N, d = X.shape
    offsets: dict[tuple, int] = {}

    def key(*terms):
        v = np.zeros(d, dtype=int)
        for sign, k in terms:
            v[k] += sign
        return tuple(v)

    keys = [key()]
    for k in range(d):
        for s in (1, -1):
            keys.append(key((s, k)))
            keys.append(key((s, k), (s, k)))
            for m in range(d):
                if m != k:
                    for s2 in (1, -1):
                        keys.append(key((s, k), (s2, m)))
    for kk in keys:
        offsets.setdefault(kk, len(offsets))
    off_arr = np.array(list(offsets.keys()), dtype=float) * delta      # (P, d)
    pts = (X[None, :, :] + off_arr[:, None, :]).reshape(-1, d)
    Gall = metric_fn(pts).reshape(len(offsets), N, d, d)

    def g_at(v: tuple) -> np.ndarray:
        return Gall[offsets[v]]

    def gamma_at(base: tuple) -> tuple[np.ndarray, np.ndarray]:
        g0 = g_at(base)
        dg = np.empty((N, d, d, d))
        for k in range(d):
            p = list(base); p[k] += 1      # noqa: E702
            q = list(base); q[k] -= 1      # noqa: E702
            dg[:, k] = (g_at(tuple(p)) - g_at(tuple(q))) / (2.0 * delta)
        return christoffel_general(safe_inv(g0), dg), g0

    zero = tuple([0] * d)
    gamma0, g0 = gamma_at(zero)
    dgamma = np.empty((N, d, d, d, d))
    for m in range(d):
        p = [0] * d; p[m] = 1              # noqa: E702
        q = [0] * d; q[m] = -1             # noqa: E702
        gp, _ = gamma_at(tuple(p))
        gm, _ = gamma_at(tuple(q))
        dgamma[:, m] = (gp - gm) / (2.0 * delta)
    return ricci_general(gamma0, dgamma), gamma0, g0
