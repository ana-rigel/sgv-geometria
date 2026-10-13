"""All tests synthetic; no market downloads or reserved-data access."""
import numpy as np
import pandas as pd
import pytest
from sgv_m34.core import (
    geometry_vector,conventional_signature,past_features,fit_and_score,
    geometry_signature,N_NODES)
from sgv_m34.synthetic import generate_episodes

def test_geometry_vector_and_undefined_orientation():
    s={'delta_center':[.1,-.3,.4],'delta_log_volume':.2,
       'theta_deg':None,'distance_512':.1,'delta_D':.03}
    v=geometry_vector(s)
    assert v.shape==(8,) and v[4]==0 and v[-1]==1

def test_moment_translation():
    rng=np.random.default_rng(9);A=rng.normal(size=(525,3))
    B=A+[.5,-.3,.2]
    sig=conventional_signature(A,B)
    np.testing.assert_allclose(sig[:3],[.5,-.3,.2],atol=1e-10)
    assert len(sig)==15

def test_no_future_data_in_causal_features():
    rng=np.random.default_rng(10)
    X=rng.normal(size=(100,3));nodes=rng.integers(0,20,size=100)
    ts=1777593600000+np.arange(100)*60000
    original=past_features(X,nodes,ts)
    X[70:]+=500;nodes[70:]=10
    altered=past_features(X,nodes,ts)
    np.testing.assert_allclose(original[:70],altered[:70])
    assert original.shape[1]==37

def test_chronological_holdout():
    ep=generate_episodes('S1_markov',n_episodes=10,episode_size=15)
    r=fit_and_score(ep)
    assert r['splits']=={'train':list(range(6)),
                         'validation':[6,7],'test':[8,9]}

def test_planted_geo_power():
    r=fit_and_score(generate_episodes('S4_geometry',n_episodes=60))
    assert r['test_differences_nats']['B0plus_minus_B_GEO']>.08

def test_moment_control():
    r=fit_and_score(generate_episodes('S2_moments',n_episodes=60))
    assert r['test_differences_nats']['B0_minus_B0plus']>.08

def test_end_to_end_shell_M11I_synthetic():
    rng=np.random.default_rng(13)
    A=rng.normal(size=(525,3));B=A+[.3,0,0]
    s=geometry_signature(A,B,grid=35)
    assert s['valid'] and s['distance_512'] is not None
    assert s['delta_D'] is not None
    assert len(geometry_vector(s))==8

def test_invalid_geometry_does_not_fabricate_values():
    with pytest.raises(ValueError):
        geometry_vector({'delta_center':[0,0,0],'delta_log_volume':0,
            'theta_deg':None,'distance_512':None,'delta_D':None})
