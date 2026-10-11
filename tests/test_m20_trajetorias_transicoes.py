"""SGV-M20a: exact algebra + numerical controls without touching market data."""
import numpy as np
from experiments import m20_trajetorias_transicoes as m


def test_stationary_marginals_identical_for_rotations():
    for beta in (0.0, m.BETA, -m.BETA):
        a, q = m.system(beta)
        np.testing.assert_allclose(a@a.T+q, np.eye(3), atol=1e-13)
    # Even the univariate lag-one autocovariances are equal.
    np.testing.assert_allclose(np.diag(m.system(0)[0]),
                               np.diag(m.system(m.BETA)[0]))


def test_gaussian_w2_known_cases():
    rng = np.random.default_rng(2)
    x = rng.normal(size=(800,3))
    assert m.gaussian_w2_sq(x,x) < 1e-9
    offset = np.array([1.0,-2.0,0.5])
    assert abs(m.gaussian_w2_sq(x,x+offset)-5.25) < 1e-6


def test_rotation_changes_time_arrow_not_static_population():
    # The expected population marginals are identical even with circulation.
    rng = np.random.default_rng(39)
    plus = m.generate(16000, m.BETA, rng)
    minus = m.generate(16000, -m.BETA, rng)
    rp = m.scores(plus)
    rm = m.scores(minus)
    assert rp["signed_current"] > .25
    assert rm["signed_current"] < -.25
    assert abs(rp["lagdiag_departure"] - rm["lagdiag_departure"]) < .04


def test_nonnegative_coupling_excess_numerically():
    rng = np.random.default_rng(77)
    for beta in (0, m.BETA, -m.BETA):
        x = m.generate(700, beta, rng)
        r = m.scores(x)
        assert r["excess_cost"] > -1e-8
        assert np.all(np.isfinite(list(r.values())))


def test_slow_drift_changes_distributions_without_changing_covariance():
    rng = np.random.default_rng(10)
    x = m.generate(1200, 0, rng)
    y = x + np.linspace(0, 1.4, len(x))[:,None]*np.array([1.0,0,0])
    assert m.scores(y)["endpoint_w2"] > m.scores(x)["endpoint_w2"]
    assert np.linalg.norm(np.cov(y.T)-np.cov(x.T)) > 0


def test_pilot_reproducible_and_isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "ROOT", tmp_path)
    a = m.run("pilot")
    b = m.run("pilot")
    assert a == b
    assert len(a["results"]["null"]) == len(m.STATS)+1
    assert a["n_null_calibration"] != a["n_per_evaluation_group"] or a["mode"] == "pilot"
    assert (tmp_path/"reports/m20/piloto.json").exists()
