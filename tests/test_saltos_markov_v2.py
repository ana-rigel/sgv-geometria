"""Sanity invariants for V2, no financial data."""
import numpy as np
import pytest
from pipeline import reteste_saltos_markov_v2 as v


def test_multiscale_increments_are_paired():
    brown, jump, number = v.generate_a(103)
    assert brown.shape == jump.shape == (int(v.DURATION / v.DT0),)
    assert number > 0 and not np.array_equal(brown, jump)


def test_synthetic_reproducibility():
    a = v.generate_a(341)
    b = v.generate_a(341)
    np.testing.assert_array_equal(a[0], b[0])
    np.testing.assert_array_equal(a[1], b[1])
    assert a[2] == b[2]


def test_fourth_moment_of_zero_is_zero():
    z = np.zeros(int(v.DURATION / v.DT0))
    np.testing.assert_allclose(v.m4_dt(z), np.zeros(len(v.SCALES)))


def test_linear_intercept_exact():
    h = np.asarray(v.SCALES)
    assert np.isclose(v.intercept(.35 + .20*h), .35)


def test_past_mean_has_no_current_value_or_future():
    x = np.arange(20., dtype=float)
    p = v.past_mean(x, 5)
    assert np.isnan(p[:5]).all()
    assert p[5] == 2
    assert p[6] == 3
    y = x.copy()
    y[5:] = 999
    assert p[5] == v.past_mean(y, 5)[5]


def test_memory_oracle_known_model_has_correct_alignment():
    d = v.generate_b(5023, True)
    assert len(d["resid"]) == len(d["h"]) == len(d["x"]) == v.N_B
    x = v.evaluate_b(d)
    assert set(x) == {"M_sem", "M_proxy", "M_oracle"}
    assert all(np.isfinite(z) for z in x.values())


def test_homoscedastic_oracle_equals_raw_up_to_scale():
    d = v.generate_b(931, False)
    x = v.evaluate_b(d)
    assert np.isclose(x["M_sem"], x["M_oracle"])


def test_bootstrap_reproducibility():
    v1 = np.linspace(-1, 1, 24)
    assert v.ci_bootstrap(v1, 42, 200) == v.ci_bootstrap(v1, 42, 200)


def test_no_old_market_pipeline_imported():
    import inspect
    source = inspect.getsource(v)
    assert "import explora_geometria_residual" not in source
    assert "import yfinance" not in source
    assert "binance.vision" not in source
