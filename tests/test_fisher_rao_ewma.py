"""Casos de resposta conhecida para a curvatura Fisher–Rao e a causalidade (só dados sintéticos)."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location(
    "fr_ewma", Path(__file__).resolve().parents[1] / "experiments" / "fisher_rao_ewma.py")
fr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fr)


def test_horizontal_line_has_curvature_one_over_sqrt2():
    # σ constante é horociclo; em (dμ²+2dσ²)/σ² = 2·hiperbólica, κ = 1/√2
    t = np.arange(200.0)
    mu = 1e-3 * t; sig = np.full_like(t, 0.5)
    k = fr.fisher_curvature_backward(mu, sig)[0]
    assert np.allclose(k[2:], 1 / np.sqrt(2), rtol=1e-9)


def test_vertical_line_is_geodesic():
    t = np.arange(200.0)
    k = fr.fisher_curvature_backward(np.zeros_like(t), np.exp(1e-3 * t))[0]
    assert np.max(k[2:]) < 1e-2


@pytest.mark.parametrize("param", ["uniforme", "nao_uniforme"])
def test_half_ellipse_is_geodesic(param):
    # x = μ/√2 leva a 2(dx²+dσ²)/σ²: geodésicas são semicírculos em (x, σ)
    s = np.linspace(0.3, 2.8, 20000)
    th = s if param == "uniforme" else s + 0.2 * np.sin(3 * s)
    mu = np.sqrt(2) * (0.1 + np.cos(th)); sig = np.sin(th)
    k = fr.fisher_curvature_backward(mu, sig)[0]
    assert np.max(k[5:]) < 5e-3


def test_curvature_and_state_are_causal():
    rng = np.random.default_rng(1)
    r = rng.standard_t(4, 6000) * 1e-3
    ok = np.ones(len(r), bool)
    mu, sig = fr.ewma_states(r, ok)
    k = fr.fisher_curvature_backward(mu, sig)[0]
    r2 = r.copy(); r2[4000:] = rng.normal(0, 5e-3, 2000)   # muda só o futuro de t=3999
    mu2, sig2 = fr.ewma_states(r2, ok)
    k2 = fr.fisher_curvature_backward(mu2, sig2)[0]
    assert np.array_equal(k[:4000], k2[:4000], equal_nan=True) and np.array_equal(sig[:4000], sig2[:4000])
    assert not np.array_equal(k[4000:], k2[4000:])
