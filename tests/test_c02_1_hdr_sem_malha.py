"""SGV-C02.1: analytic checks of the mesh-free HDR extractor (no market data)."""
import numpy as np
import pytest
from scipy.stats import chi2

from experiments.c01_oraculo_hdr_fisher import GMM3
from experiments.c02_1_hdr_sem_malha import (
    feature_names, hdr12_ml, precision_checks, region, w2_hdr,
)

SIG = np.diag([1.0, 0.6, 0.35]) ** 2


def gauss(mu=(0., 0., 0.), cov=SIG):
    return GMM3(np.array([1.0]), np.array([mu], float), np.array([cov], float))


def obs(p, seed, n=750):
    return p.sample(n, np.random.default_rng(seed))


def test_names_dimension():
    assert len(feature_names()) == 12 and len(feature_names(include_w2=False)) == 10


@pytest.mark.parametrize('alpha', [0.50, 0.95])
def test_gaussian_volume_and_coverage_exact(alpha):
    r = region(gauss(), alpha, seed=1)
    exact = 4 / 3 * np.pi * chi2.ppf(alpha, 3) ** 1.5 * np.sqrt(np.linalg.det(SIG))
    assert abs(np.log(r.volume / exact)) < 0.03
    assert abs(r.coverage - alpha) < 0.015
    assert np.linalg.norm(r.centroid) < 0.03
    # uniform measure on an ellipsoid: covariance ∝ Σ, so trace-normalised shape = Σ/trΣ
    assert np.linalg.norm(r.shape - SIG / np.trace(SIG)) < 0.02


def test_identity_is_near_zero():
    p = gauss()
    a, b = obs(p, 10), obs(p, 11)
    f = hdr12_ml(a, b, p, p, seed=3)
    # tolerâncias de engenharia ≈ 4 desvios do ruído de Monte Carlo medido (sd log V: 0,005 no HDR50, 0,013 no HDR95)
    for lab, tol in (('hdr50', 0.03), ('hdr95', 0.08)):
        assert abs(f[f'{lab}_log_volume_ratio']) < tol
        assert f[f'{lab}_center_distance'] < 0.05
        assert f[f'{lab}_jaccard_loss'] < tol          # dominado pelo mesmo ruído do limiar τ
        assert f[f'{lab}_cross_mass_shift'] < 0.01
        assert f[f'{lab}_shape_tensor_diff'] < 0.03
    assert w2_hdr(a, a, p, p, 0.5) == 0.0


def test_translation_known_values():
    p, v = gauss(), np.array([0.0, 0.65, 0.0])
    q = p.affine(np.eye(3), v)
    f = hdr12_ml(obs(p, 20), obs(q, 21), p, q, seed=4)
    for lab in ('hdr50', 'hdr95'):
        assert abs(f[f'{lab}_center_distance'] - 0.65) < 0.03
        assert abs(f[f'{lab}_log_volume_ratio']) < 0.03
        assert f[f'{lab}_shape_tensor_diff'] < 0.03
        assert f[f'{lab}_cross_mass_shift'] > 0.05
    assert f['hdr50_w2_hdr'] > 0.2


def test_scale_known_values():
    p, s = gauss(), 1.25
    q = p.affine(s * np.eye(3))
    f = hdr12_ml(obs(p, 30), obs(q, 31), p, q, seed=5)
    for lab in ('hdr50', 'hdr95'):
        assert abs(f[f'{lab}_log_volume_ratio'] - 3 * np.log(s)) < 0.03
        # concentric similar ellipsoids: Jaccard loss = 1 - 1/s^3
        assert abs(f[f'{lab}_jaccard_loss'] - (1 - s ** -3)) < 0.02
        assert f[f'{lab}_shape_tensor_diff'] < 0.03


def test_rotation_changes_shape_not_volume():
    p = gauss()
    rot = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
    q = p.affine(rot)
    f = hdr12_ml(obs(p, 40), obs(q, 41), p, q, seed=6)
    for lab in ('hdr50', 'hdr95'):
        assert abs(f[f'{lab}_log_volume_ratio']) < 0.03
        assert f[f'{lab}_shape_tensor_diff'] > 0.3
        assert f[f'{lab}_center_distance'] < 0.05


def test_precision_gate_passes_on_gaussian_and_is_deterministic():
    p = gauss()
    q = p.affine(np.eye(3), (0.3, 0.0, 0.0))
    a, b = obs(p, 50), obs(q, 51)
    r1 = hdr12_ml(a, b, p, q, seed=7, scale=1)
    r2 = hdr12_ml(a, b, p, q, seed=8, scale=2)
    assert precision_checks(r1, r2) == []
    assert hdr12_ml(a, b, p, q, seed=7) == r1


def test_fail_closed():
    with pytest.raises(ValueError):
        region(gauss(), 1.2, seed=1)
    with pytest.raises(ValueError):
        hdr12_ml(obs(gauss(), 1), obs(gauss(), 2), gauss(), gauss(), seed=1, scale=3)
    with pytest.raises(ValueError):
        w2_hdr(np.zeros((5, 3)), np.zeros((6, 3)), gauss(), gauss(), 0.5)
