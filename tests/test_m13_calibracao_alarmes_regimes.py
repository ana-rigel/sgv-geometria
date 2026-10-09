"""M13 finite-rank and causal-gate tests; no BTC confirmation files."""
import numpy as np
import pytest
from experiments.m13_calibracao_alarmes_regimes import (
    mc_rank,wilson,known_generator,geom_distance,synthetic_rank_sanity,
    joint_tail_metrics,extended_adequacy,aggregate_market,REFS,GENERATORS
)

def test_rank_reference_extremes():
    vals=np.arange(REFS,dtype=float)
    assert mc_rank(100.,vals)==1/(REFS+1)
    assert mc_rank(-1.,vals)==1.
    assert mc_rank(5.,np.ones(REFS)*5)==1.

def test_rank_rejects_invalid_reference_and_observation():
    with pytest.raises(ValueError,match='Insufficient'):
        mc_rank(0.,np.ones(6))
    with pytest.raises(ValueError):
        mc_rank(0.,np.r_[np.ones(18),np.nan])
    with pytest.raises(ValueError):
        mc_rank(np.nan,np.ones(REFS))

def test_interval_does_not_claim_zero_risk():
    bounds=wilson(0,6)
    assert bounds[0]==0.
    assert bounds[1]>.1

def test_generator_reproducibility_and_distinct_known_states():
    for name in GENERATORS:
        a=known_generator(name,seed=410)
        b=known_generator(name,seed=410)
        assert a.shape==(1500,3)
        assert np.isfinite(a).all()
        np.testing.assert_array_equal(a,b)
    assert not np.array_equal(known_generator(GENERATORS[0],410),
                              known_generator(GENERATORS[1],410))

def test_synthetic_sample_reenters_exact_M11_geometry():
    x=known_generator('gaussian_var',seed=489)
    d=geom_distance(x,seed=490)
    assert d['valid'],d
    assert d['distance_512']>=0.
    assert np.isfinite(d['distance_512'])

def test_rank_sanity_is_not_geometry():
    r=synthetic_rank_sanity(trials=1000)
    assert r['n']==1000
    assert r['scope'].startswith('Scalar rank')
    assert 0<=r['frequency']<=.15

def test_joint_tails_and_self_error():
    x=known_generator('gaussian_var',seed=419)
    ts=np.arange(len(x),dtype=np.int64)*60000
    tails=joint_tail_metrics(x)
    assert 0<=tails['joint_upper_tail']<=.1
    error=extended_adequacy(x,x,ts)
    assert all(abs(v)<1e-12 for v in error.values() if v is not None)

def test_empty_market_aggregate_is_not_a_claim():
    a=aggregate_market([])
    assert a['n_valid_origins']==0
    assert all(v['complete_origins']==0 for v in a['models'].values())
