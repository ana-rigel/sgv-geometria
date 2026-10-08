"""Geometria diferencial pontual sobre uma métrica dada como função g(x).

A métrica é avaliada EXATAMENTE (analiticamente, a partir do KDE). As derivadas da
métrica (para Christoffel) e dos Christoffel (para Riemann) usam diferenças centrais
sobre essa função exata, com passo δ pequeno nas coordenadas padronizadas — erro de
truncamento O(δ²) e sem a malha grossa do legado. Os testes (tests/) conferem contra
casos de resposta conhecida: espaço plano (R = 0), esfera S² (R = 2) e S³ (R = 6).

Convenções
  Γ^k_ij = ½ g^kl (∂_i g_jl + ∂_j g_il − ∂_l g_ij)
  R^r_smn = ∂_m Γ^r_ns − ∂_n Γ^r_ms + Γ^r_ml Γ^l_ns − Γ^r_nl Γ^l_ms
  Ric_sn  = R^r_srn,   R = g^sn Ric_sn,   G = Ric − ½ R g
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .kde import GaussianKDE

Metric = Callable[[np.ndarray], np.ndarray]


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------
def observed_information_metric(kde: GaussianKDE) -> Metric:
    """g = ∇²(−log ρ): a métrica do legado (Hessiana da surpresa), sem regularização."""
    return kde.hess_phi


def local_fisher_metric(kde: GaussianKDE, ridge: float = 0.0) -> Metric:
    """g(x) = Σ_i K_i(x) s_i s_iᵀ / Σ_i K_i(x),  s_i = ∇φ(X_i).

    Média local do produto externo do escore: a informação de Fisher (de translação)
    restrita à vizinhança de x. Pela identidade da informação, E_ρ[∇²φ] = E_ρ[∇φ∇φᵀ],
    então esta métrica e a de informação observada coincidem em média, mas esta é
    positiva semidefinida em todo ponto."""
    S = kde.score_at_samples()
    SS = np.einsum("ij,ik->ijk", S, S)
    eye = np.eye(kde.d)

    def g(x):
        _, w, _ = kde._weights(np.asarray(x, float))
        return np.einsum("i,ijk->jk", w, SS) / w.sum() + ridge * eye

    return g


def gaussian_reference_fisher_metric(kde: GaussianKDE, ridge: float = 0.0) -> Metric:
    """Mesma construção da Fisher local, mas com o escore de UMA gaussiana ajustada
    à janela: s_i = Σ⁻¹(X_i − μ). Mesmos pesos de vizinhança K_i(x).

    Serve de linha de base: a curvatura de F que já aparece quando a distribuição é
    gaussiana vem da POSIÇÃO do ponto (o escore cresce com a distância ao centro),
    não da forma da distribuição. Só o que sobra além desta referência pode ser
    "geometria do mercado"."""
    mu = kde.X.mean(0)
    Si = np.linalg.inv(np.cov(kde.X, rowvar=False))
    S = (kde.X - mu) @ Si
    SS = np.einsum("ij,ik->ijk", S, S)
    eye = np.eye(kde.d)

    def g(x):
        _, w, _ = kde._weights(np.asarray(x, float))
        return np.einsum("i,ijk->jk", w, SS) / w.sum() + ridge * eye

    return g


def conformal_sphere_metric(dim: int, radius: float = 1.0) -> Metric:
    """Projeção estereográfica da esfera S^dim de raio r: g = 4r⁴/(r²+|x|²)² · I.
    Curvatura escalar exata: R = dim(dim−1)/r²."""
    def g(x):
        x = np.asarray(x, float)
        f = 4.0 * radius ** 4 / (radius ** 2 + x @ x) ** 2
        return f * np.eye(dim)
    return g


# ---------------------------------------------------------------------------
# Curvatura
# ---------------------------------------------------------------------------
def christoffel(g: Metric, x: np.ndarray, delta: float = 1e-3) -> np.ndarray:
    x = np.asarray(x, float)
    d = len(x)
    gi = np.linalg.inv(g(x))
    dg = np.empty((d, d, d))  # dg[l, i, j] = ∂_l g_ij
    for l in range(d):
        e = np.zeros(d); e[l] = delta
        dg[l] = (g(x + e) - g(x - e)) / (2 * delta)
    # T[i,j,l] = ∂_i g_jl + ∂_j g_il − ∂_l g_ij
    T = dg + dg.transpose(1, 0, 2) - dg.transpose(1, 2, 0)
    return 0.5 * np.einsum("kl,ijl->kij", gi, T)


@dataclass
class Curvature:
    g: np.ndarray
    eigvals: np.ndarray
    det: float
    gamma: np.ndarray
    riemann: np.ndarray
    ricci: np.ndarray
    R: float
    einstein: np.ndarray

    @property
    def signature(self) -> tuple[int, int]:
        return int(np.sum(self.eigvals > 0)), int(np.sum(self.eigvals < 0))

    @property
    def positive_definite(self) -> bool:
        return bool(np.all(self.eigvals > 0))


def curvature(g: Metric, x: np.ndarray, delta: float = 1e-3) -> Curvature:
    x = np.asarray(x, float)
    d = len(x)
    G = g(x)
    gam = christoffel(g, x, delta)
    dgam = np.empty((d, d, d, d))  # dgam[m, r, n, s] = ∂_m Γ^r_ns
    for m in range(d):
        e = np.zeros(d); e[m] = delta
        dgam[m] = (christoffel(g, x + e, delta) - christoffel(g, x - e, delta)) / (2 * delta)
    # R^r_smn = ∂_m Γ^r_ns − ∂_n Γ^r_ms + Γ^r_ml Γ^l_ns − Γ^r_nl Γ^l_ms
    t1 = np.einsum("mrns->rsmn", dgam)
    t2 = np.einsum("nrms->rsmn", dgam)
    t3 = np.einsum("rml,lns->rsmn", gam, gam)
    t4 = np.einsum("rnl,lms->rsmn", gam, gam)
    riem = t1 - t2 + t3 - t4
    ric = np.einsum("rsrn->sn", riem)
    gi = np.linalg.inv(G)
    R = float(np.einsum("sn,sn->", gi, ric))
    ein = ric - 0.5 * R * G
    ev = np.linalg.eigvalsh(0.5 * (G + G.T))
    return Curvature(g=G, eigvals=ev, det=float(np.linalg.det(G)), gamma=gam,
                     riemann=riem, ricci=ric, R=R, einstein=ein)


def tensor_norm(T: np.ndarray, g: np.ndarray) -> float:
    """|T| = sqrt(|T_ij T_ab g^ia g^jb|) — a norma que o legado usa."""
    gi = np.linalg.inv(g)
    return float(np.sqrt(abs(np.einsum("ij,ab,ia,jb->", T, T, gi, gi))))


# ---------------------------------------------------------------------------
# "Tensor energia-momento" do legado, reconstruído de forma exata
# ---------------------------------------------------------------------------
W_PHI, W_MEM, W_LAM = 1.00, 0.75, 0.25  # pesos do legado (W_PHI_STRESS etc.)


class LambdaField:
    """Campo λ suavizado por Nadaraya–Watson (como o legado), com gradiente analítico."""

    def __init__(self, kde: GaussianKDE, lam: np.ndarray):
        self.kde = kde
        self.lam = np.asarray(lam, float)

    def value_grad(self, x):
        u, w, _ = self.kde._weights(np.asarray(x, float))
        W = w.sum()
        val = (w @ self.lam) / W
        # ∂_x w_i = −w_i u_i / h ;  ∇(Σwλ/Σw) = −(1/h)[Σ w λ u /W − val Σ w u /W]
        grad = -((w * self.lam) @ u / W - val * (w @ u) / W) / self.kde.h
        return val, grad


def info_stress_tensor(kde: GaussianKDE, lamf: LambdaField, g: np.ndarray, x) -> np.ndarray:
    """T = ∇φ∇φᵀ + 0,75∇λ∇λᵀ + 0,25 λ g − ½(|∇φ|²_g + 0,75|∇λ|²_g) g  (forma do legado)."""
    gp = kde.grad_phi(x)
    lv, gl = lamf.value_grad(x)
    gi = np.linalg.inv(g)
    return (W_PHI * np.outer(gp, gp) + W_MEM * np.outer(gl, gl) + W_LAM * lv * g
            - 0.5 * (W_PHI * gp @ gi @ gp + W_MEM * gl @ gi @ gl) * g)
