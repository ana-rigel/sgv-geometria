"""M20c code gates: only synthetic observations, strict prefix-only fitting."""
import numpy as np
import pytest
from experiments import m20c_acoplamento_condicional as m


def test_rotations_are_proper_orthogonal():
    r=m.random_rotation(np.random.default_rng(8))
    np.testing.assert_allclose(r.T@r,np.eye(3),atol=1e-12)
    assert np.linalg.det(r)>0.999


def test_marginals_and_direction_randomization():
    for i,scenario in enumerate(m.SCENARIOS):
        x=m.generate_series(1300,scenario,np.random.default_rng(110+i))
        assert x.shape==(1300,3)
        assert np.isfinite(x).all()
        assert abs(np.mean(x[:,0]))<0.16


def test_var_fit_does_not_read_future():
    rng=np.random.default_rng(71)
    x=m.generate_series(950,"gaussian_var",rng)
    a=m.fit_var(x[:600])
    y=x.copy()
    y[600:]=1e9
    b=m.fit_var(y[:600])
    for u,v in zip(a,b):
        np.testing.assert_allclose(u,v,rtol=0,atol=0)


def test_var_simulator_and_scores():
    rng=np.random.default_rng(34)
    prefix=rng.normal(size=(800,3))
    fit=m.fit_var(prefix)
    x=m.simulate_var(prefix[-1],fit,500,rng)
    v=m.scores(x)
    assert set(v)==set(m.METRICS)
    assert all(np.isfinite(z) and z>=0 for z in v.values())


def test_statistic_detects_strong_nonlinear_coupling():
    rng=np.random.default_rng(66)
    x=rng.normal(size=(500,3))
    y=x.copy()
    independent=rng.normal(size=(500,3))
    # Evaluate current x -> y with deliberately coupled vs independent.
    assert m.conditional_sw2(x,y)>m.conditional_sw2(x,independent)
    assert m.rff_hsic(x,y)>m.rff_hsic(x,independent)
    assert m.joint_mmd(x,y)>m.joint_mmd(x,independent)


def test_single_trial_deterministic():
    a=m.one_trial(2,0,240,200,3,888)
    b=m.one_trial(2,0,240,200,3,888)
    assert a==b
    assert a["scenario"]=="hidden_plus"
    assert set(a["alarms"])==set(m.METRICS)


def test_simulated_null_scenario_no_lookahead_trick():
    rng=np.random.default_rng(95)
    x=rng.normal(size=(800,3))
    fit=m.fit_var(x[:400])
    fitted=m.simulate_var(x[399],fit,300,rng)
    assert fitted.shape==(300,3)
    assert all(isinstance(v,bool) for v in m.one_trial(
        0,10,240,200,3,123)["alarms"].values())


def test_projections_are_fixed_and_nonzero():
    assert m.PROJECTIONS.shape==(6,3)
    np.testing.assert_allclose(m.PROJECTIONS[:3],np.eye(3))
    assert m.RFF_DIR.shape==(8,3)
    assert m.JOINT_DIR.shape==(12,6)
    assert np.isfinite(m.PROJECTIONS).all()
