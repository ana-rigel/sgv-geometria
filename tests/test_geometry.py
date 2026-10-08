"""Casos de resposta conhecida. Se algum falhar, nenhum número do projeto vale."""
import numpy as np
import pytest

from sgvgeo.geometry import (conformal_sphere_metric, curvature, local_fisher_metric,
                             observed_information_metric)
from sgvgeo.kde import GaussianKDE


def test_flat_metric_has_zero_curvature():
    g = lambda x: np.diag([2.0, 3.0, 5.0])
    c = curvature(g, np.array([0.3, -0.2, 0.1]))
    assert abs(c.R) < 1e-6
    assert np.max(np.abs(c.riemann)) < 1e-6


@pytest.mark.parametrize("dim,r", [(2, 1.0), (2, 2.0), (3, 1.0), (3, 0.5)])
def test_sphere_scalar_curvature(dim, r):
    g = conformal_sphere_metric(dim, r)
    expected = dim * (dim - 1) / r ** 2
    for x in [np.zeros(dim), np.full(dim, 0.3), np.linspace(-0.4, 0.5, dim)]:
        c = curvature(g, x, delta=1e-3)
        assert c.R == pytest.approx(expected, rel=1e-4)


def test_sphere_einstein_tensor_in_3d():
    # Em S³ unitária: Ric = 2g, R = 6, G = Ric − 3g = −g
    g = conformal_sphere_metric(3, 1.0)
    x = np.array([0.2, -0.1, 0.3])
    c = curvature(g, x)
    assert np.allclose(c.einstein, -c.g, rtol=1e-4, atol=1e-6)


def test_kde_derivatives_match_finite_differences():
    rng = np.random.default_rng(0)
    kde = GaussianKDE(rng.normal(size=(400, 3)), h=0.4)
    x = np.array([0.1, -0.3, 0.7])
    d = 1e-4
    num_grad = np.array([(kde.phi(x + d * e) - kde.phi(x - d * e)) / (2 * d) for e in np.eye(3)])
    assert np.allclose(kde.grad_phi(x), num_grad, rtol=1e-5, atol=1e-7)
    num_hess = np.array([(kde.grad_phi(x + d * e) - kde.grad_phi(x - d * e)) / (2 * d) for e in np.eye(3)])
    assert np.allclose(kde.hess_phi(x), num_hess, rtol=1e-5, atol=1e-6)


def test_single_wide_kernel_is_flat_space():
    """A situação do legado: largura de banda enorme frente à escala dos dados.
    A densidade vira uma gaussiana só e a métrica Hessiana fica g = I/h² (plana)."""
    rng = np.random.default_rng(1)
    X = rng.normal(scale=1e-4, size=(500, 3))
    kde = GaussianKDE(X, h=0.45)
    c = curvature(observed_information_metric(kde), X[0], delta=1e-3)
    assert np.allclose(c.g, np.eye(3) / 0.45 ** 2, rtol=1e-6, atol=1e-6)
    assert abs(c.R) < 1e-6


def test_local_fisher_is_positive_semidefinite():
    rng = np.random.default_rng(2)
    X = np.r_[rng.normal(-1.5, 0.5, size=(200, 3)), rng.normal(1.5, 0.5, size=(200, 3))]
    kde = GaussianKDE(X, h=0.4)
    gF = local_fisher_metric(kde)
    gH = observed_information_metric(kde)
    pts = rng.normal(size=(50, 3))
    assert all(np.linalg.eigvalsh(gF(p)).min() > -1e-12 for p in pts)
    # entre os dois modos a informação observada deixa de ser positiva definida
    assert np.linalg.eigvalsh(gH(np.zeros(3))).min() < 0


def test_information_identity_on_average():
    """E_ρ[∇²φ] = E_ρ[∇φ∇φᵀ] (identidade da informação) para a própria densidade do KDE.

    Os pontos de avaliação são sorteados DE ρ_KDE (amostra + h·ruído), não as próprias
    amostras: avaliar no ponto que gerou o kernel infla a Hessiana (autoinclusão)."""
    rng = np.random.default_rng(3)
    X = rng.standard_t(5, size=(800, 2))
    kde = GaussianKDE(X, h=0.35)
    Y = X[rng.integers(0, len(X), 6000)] + kde.h * rng.normal(size=(6000, 2))
    H = np.mean([kde.hess_phi(y) for y in Y], axis=0)
    S = np.array([kde.grad_phi(y) for y in Y])
    F = S.T @ S / len(S)
    assert np.allclose(H, F, rtol=0.08, atol=0.03)


def test_gaussian_reference_matches_fisher_on_gaussian_data():
    """Em dados gaussianos, a Fisher local e sua referência gaussiana devem coincidir
    (a menos do ruído do KDE): o excesso F − ref só aparece com forma não gaussiana."""
    from scipy.stats import spearmanr
    from sgvgeo.geometry import gaussian_reference_fisher_metric
    rng = np.random.default_rng(4)
    kde = GaussianKDE(rng.normal(size=(1500, 3)), h=0.7)
    gF, gR = local_fisher_metric(kde), gaussian_reference_fisher_metric(kde)
    pts = rng.normal(size=(60, 3))
    f = [curvature(gF, p).R for p in pts]
    r = [curvature(gR, p).R for p in pts]
    assert spearmanr(f, r).statistic > 0.8
