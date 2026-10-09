"""L2: casos de resposta conhecida para o ajuste local, a métrica e o teste."""
import numpy as np
import pandas as pd

from sgvgeo.flow import default_sf1, simulate_sf1
from sgvgeo.l2 import (build_rows, evaluations, fisher_rao_speed, fit_local, partial_spearman_test,
                       t_scale_mle)


def test_t_scale_mle_recovers_scale():
    rng = np.random.default_rng(0)
    x = 0.003 * rng.standard_t(4, 200_000)
    assert abs(t_scale_mle(x, 4.0) / 0.003 - 1) < 0.02


def test_local_fit_recovers_sf1_and_zero_speed_for_same_block():
    m = default_sf1()
    df = simulate_sf1(m, 40_000, seed=3)
    rows = build_rows(df)
    idx = np.arange(1000, 40_000)
    L = fit_local(rows, idx, 4.0)
    assert np.allclose(L.a, m.a, atol=0.05)
    assert abs(L.b[1] - m.b[1]) < 0.05
    v = fisher_rao_speed(L, L, 4.0)
    assert v["v_fluxo"] == 0 and v["v_total"] == 0


def test_speed_grows_with_parameter_change():
    m = default_sf1()
    rows = build_rows(simulate_sf1(m, 20_000, seed=4))
    A = fit_local(rows, np.arange(1000, 10_000), 4.0)
    B = fit_local(rows, np.arange(10_000, 20_000), 4.0)
    B2 = fit_local(rows, np.arange(10_000, 20_000), 4.0)
    B2.a = B2.a + np.array([0, 0.3, 0])  # impacto mais forte
    assert fisher_rao_speed(A, B2, 4.0)["v_fluxo"] > 3 * fisher_rao_speed(A, B, 4.0)["v_fluxo"]


def test_partial_spearman_permutation_size_and_power():
    rng = np.random.default_rng(5)
    n = 800
    ts = 1_700_000_000_000 + 3_600_000 * np.arange(n)
    c = rng.normal(size=n)
    x = np.convolve(rng.normal(size=n), np.ones(5) / 5, "same")  # autocorrelado
    y_null = c + rng.normal(size=n)
    y_alt = c + 0.5 * x + rng.normal(size=n)
    ev = pd.DataFrame({"timestamp": ts, "x": x, "c": c, "y0": y_null, "y1": y_alt})
    p0 = partial_spearman_test(ev, "x", "y0", ["c"], "hora", min_shift=10)["p_unilateral"]
    p1 = partial_spearman_test(ev, "x", "y1", ["c"], "hora", min_shift=10)["p_unilateral"]
    assert p0 > 0.025 and p1 < 0.01
