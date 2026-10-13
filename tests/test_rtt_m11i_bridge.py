"""Tests for SGV RTT->M11-I engineering bridge (all synthetic)."""
import numpy as np
import pytest
from sgv_bridge.engine import (
    stationary,reversible,models_from_A,heldout_logscore,mean_occupation,
    resample_nodes,errors,synthetic_hj,counts,stochastic,geometry_forecast
)

def test_reversible_has_identical_stationary_occupation_and_no_current():
    P=np.array([[.3,.7,0],[0,.3,.7],[.7,0,.3]])+.01
    P/=P.sum(axis=1,keepdims=True)
    Q,pi=reversible(P)
    np.testing.assert_allclose(pi@P,pi,atol=1e-9)
    np.testing.assert_allclose(pi@Q,pi,atol=1e-9)
    np.testing.assert_allclose(pi[:,None]*Q,(pi[:,None]*Q).T,atol=1e-9)
    assert not np.allclose(P,Q)

def test_only_matured_training_nodes_and_strict_future_scoring():
    a=np.array([0,0,1,1,2,1,0,2,2])
    b=np.array([1,2,1,0])
    models=models_from_A(a,n_nodes=3)
    observed=heldout_logscore(models,int(a[-1]),b)
    expected=np.log(models['rtt'][np.array([2,1,2,1]),b]).mean()
    assert observed['rtt']==pytest.approx(expected)

def test_past_model_is_unchanged_if_future_changes():
    a=np.tile(np.array([0,1,2,3]),50)
    b1=np.zeros(55,dtype=int)
    b2=np.ones(55,dtype=int)*3
    model=models_from_A(a,n_nodes=4)
    same=models_from_A(a,n_nodes=4)
    np.testing.assert_array_equal(model['rtt'],same['rtt'])
    assert heldout_logscore(model,a[-1],b1)!=heldout_logscore(same,a[-1],b2)

def test_future_mean_occupation_is_not_endpoint():
    P=np.array([[0.,1.],[1.,0.]])
    np.testing.assert_allclose(mean_occupation(P,0,2),[.5,.5])

def test_uses_only_historical_cloud():
    X=np.arange(18).reshape(6,3).astype(float)
    n=np.array([0,0,0,1,1,1])
    sample,missing=resample_nodes(X,n,[.9,.1])
    assert missing==0
    assert len(sample)==len(X)
    assert all(any(np.array_equal(x,y) for y in X) for x in sample)

def test_synthetic_nonreversible_circulation_detected():
    v=synthetic_hj(n=7000)
    assert v['clockwise']['rtt_minus_reversible']>.2
    assert v['counterclockwise']['rtt_minus_reversible']>.2
    assert abs(v['reversible']['rtt_minus_reversible'])<.035

def test_component_loss_zero_on_exact_match():
    x={'valid':True,'delta_center':[1.,2.,3.],
       'delta_log_volume':.3,'theta_deg':15.,
       'distance_512':.2,'delta_D':.12}
    assert errors(x,x)['diagnostic_loss']==0
    y=dict(x);y['delta_center']=[0.,0.,0.]
    assert errors(x,y)['diagnostic_loss']>0

def test_gmm2_hdr_m11i_synthetic_geometry_integration():
    # Use only synthetic Gaussian clouds; no markets, no future datasets.
    rng=np.random.default_rng(13)
    A=rng.standard_normal((1500,3))
    B=A+.1
    # Random codebook tests force all 20 nodes to have >=1 historical point.
    nodes=np.arange(len(A))%20
    model=models_from_A(nodes)
    result=geometry_forecast(A,B,nodes,model,last_A_node=int(nodes[-1]),seed=20261013)
    assert set(result['losses'])=={
        'persistence','rtt','reversible','shuffled_training','iid'}
    assert all(np.isfinite(x['diagnostic_loss']) for x in result['losses'].values())
