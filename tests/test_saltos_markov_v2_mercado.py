"""Guards for causal V2b reanalysis; synthetic fixtures, no BTC downloaded."""
import numpy as np
from pipeline import reteste_saltos_markov_v2_mercado as m


def test_scaling_fourth_moment():
    z=np.array([.001, -.002, .003, -.001]*300,dtype=float)
    out=m.finite_scales(z)
    assert list(out)==["1","2","4","8"]
    assert all(np.isfinite(v["m4_per_min"]) for v in out.values())


def test_causal_std_uses_only_past():
    z=np.arange(1.,201.)
    orig=m.past_std(z,30)
    changed=z.copy();changed[120:]=10000.
    assert orig[120]==m.past_std(changed,30)[120]
    assert np.isnan(orig[:15]).all()


def test_train_only_previous_week():
    rng=np.random.default_rng(11)
    prev=rng.normal(0,.001,12000)
    fit=m.calibrate_prior_week(prev)
    assert fit["h_sd"]>0 and 0<=fit["h_rho"]<=.995
    assert -.98<=fit["phi"]<=.98


def test_forward_sim_uses_separate_seeds():
    rng=np.random.default_rng(12)
    prev=rng.normal(0,.001,13000)
    fit=m.calibrate_prior_week(prev)
    x=m.simulate_week(fit,500,kind="G",seed=10)
    y=m.simulate_week(fit,500,kind="G",seed=10)
    z=m.simulate_week(fit,500,kind="S",seed=10)
    np.testing.assert_array_equal(x,y)
    assert not np.array_equal(x,z)


def test_seed_namespaces():
    keys=[m.sha_seed("junjul",kind,s,k) for kind in ("S","G") for s in (1,2) for k in (0,1)]
    assert len(set(keys))==len(keys)


def test_finite_scales_reject_bad_values():
    from pytest import raises
    with raises(ValueError):
        m.finite_scales(np.full(200,np.nan))
    with raises(ValueError):
        m.finite_scales(np.zeros(200))
