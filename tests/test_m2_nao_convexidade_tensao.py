"""SGV-M2: analytic Gaussian control and chronological separation."""
import numpy as np
import pytest
from experiments.m2_nao_convexidade_tensao import (
    morphology, fit_conditional, conditional_rmse,measure_window,
    moving_block, association
)

def test_gaussian_ellipsoid_has_no_negative_implicit_curvature():
    rng=np.random.default_rng(31)
    x=rng.normal(size=(520,3))*np.array([.7,1.,1.5])
    result=morphology(x,model='gaussian',alpha=.5)
    assert result['valid'],result
    assert result['negative_intensity']<1e-10
    assert result['convex_hull_deficit']<.05

def test_tension_model_uses_only_prior_anchor():
    x=np.random.default_rng(32).normal(size=(560,3))
    b,s=fit_conditional(x[:250])
    y=x.copy()
    y[250:,0]+=10
    bb,ss=fit_conditional(y[:250])
    np.testing.assert_array_equal(b,bb)
    assert s==ss
    assert conditional_rmse(y[250:],b,s)>conditional_rmse(x[250:],b,s)

def test_future_changes_do_not_repaint_earlier_metrics():
    rng=np.random.default_rng(33)
    x=rng.normal(size=(1500,3))
    y=x.copy()
    y[-110:,0]+=1.3
    a=measure_window(x,levels=(.5,))
    b=measure_window(y,levels=(.5,))
    assert a['tension_a']==b['tension_a']
    assert a['tension_b']!=b['tension_b']
    assert a['gaussian_50_valid']
    assert b['gaussian_50_valid']

def test_resampling_is_valid_and_repeatable():
    x=np.arange(900).reshape(300,3)
    a=moving_block(np.random.default_rng(34),x,15)
    b=moving_block(np.random.default_rng(34),x,15)
    np.testing.assert_array_equal(a,b)
    assert a.shape==x.shape

def test_no_association_claim_if_geometry_is_constant():
    rows=[{'mixture_50_valid':True,
           'mixture_50_negative_intensity_delta':0.1,
           'delta_tension':float(i)} for i in range(7)]
    assert association(rows)['status']=='degenerate_variation'

def test_conditional_rejects_short_training():
    with pytest.raises(ValueError):
        fit_conditional(np.ones((40,3)))
