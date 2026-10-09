"""M3: numerical controls, block reproducibility and protected fit."""
import numpy as np
import pytest
from experiments.m3_precisao_nao_convexidade import (
    simulate_case,initial_summary,numerical_check,circular_blocks,
    baseline_null, resample_audit, picture, summary
)

def test_three_calibration_generators():
    for kind in ('gaussian','t5','persistent_mixture'):
        x=simulate_case(kind,seed=47)
        assert x.shape==(1500,3)
        assert np.isfinite(x).all()

def test_gaussian_reference_D_zero():
    x=simulate_case('gaussian',seed=48)
    a,b=__import__('experiments.precisao_formas_3d',fromlist=['split_historical']).split_historical(x)
    from experiments.m2_nao_convexidade_tensao import morphology
    result=morphology(a,'gaussian',.5,35)
    assert result['valid'] and result['negative_intensity']<1e-10

def test_block_resampling_preserves_shape_and_seed():
    x=np.arange(1500).reshape(500,3)
    aa=circular_blocks(x,np.random.default_rng(10),12)
    bb=circular_blocks(x,np.random.default_rng(10),12)
    np.testing.assert_array_equal(aa,bb)
    assert aa.shape==x.shape

def test_parametric_elliptic_null_has_finite_output():
    rng=np.random.default_rng(16)
    x=rng.normal(size=(525,3))
    for kind in ('gauss','t5'):
        sim=baseline_null(x,np.random.default_rng(17),kind)
        assert sim.shape==x.shape
        assert np.isfinite(sim).all()

def test_grid_resolution_and_causal_split():
    x=simulate_case('gaussian',seed=49)
    result=numerical_check(x,seed=50)
    assert 'a_HDR50' in result and 'b_HDR50' in result
    assert set(('25','35','49')).issubset(result['a_HDR50'])
    assert all(result['a_HDR50'][n]['valid'] for n in ('25','35','49'))

def test_bootstrap_control_reports_validity_not_significance():
    x=simulate_case('gaussian',seed=51)
    output=resample_audit(x,seed=52,block_sizes=(8,20),reps=4)
    assert output['status'] in ('diagnostic_only','invalid_original')
    if output['status']=='diagnostic_only':
        assert set(output['block_bootstrap'])=={'8','20'}
        assert set(output['convex_null'])=={'gauss','t5'}
        assert output['convex_null']['gauss']['obs_above_q90'] is None

def test_reject_invalid_block():
    with pytest.raises(ValueError):
        circular_blocks(np.ones((30,3)),np.random.default_rng(12),31)
