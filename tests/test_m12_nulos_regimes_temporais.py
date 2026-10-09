"""SGV-M12 calibration gates for causal regime-clock nulls."""
import numpy as np
import pytest
from experiments.m12_nulos_regimes_temporais import (
    clock_bin,temporal_metrics,score_metrics,state_catalog,stationary_path,
    regime_clock_path,calibration,aggregate,MODELS)

def test_regime_calibration_and_path():
    r=calibration()
    assert r['chronology_reused_past_only']
    assert r['regime_simulation']['n_blocks']>=20

def test_clock_bins_are_fixed_six_hour_bins():
    t=np.array([0,6*3600000,12*3600000,18*3600000,24*3600000])
    np.testing.assert_array_equal(clock_bin(t),[0,1,2,3,0])

def test_blocks_reproducible_and_joint_same_rows():
    x=np.column_stack([np.arange(4000,dtype=float),
                       np.arange(4000,dtype=float)*2,
                       np.arange(4000,dtype=float)*3])
    y=stationary_path(x,1500,seed=17,block=15)
    np.testing.assert_array_equal(y,stationary_path(x,1500,17,15))
    np.testing.assert_allclose(y[:,1],y[:,0]*2)
    np.testing.assert_allclose(y[:,2],y[:,0]*3)

def test_state_clock_path_uses_historical_rows_only():
    rng=np.random.default_rng(17)
    x=rng.normal(size=(3500,3))
    t=np.arange(3500,dtype=np.int64)*3600000
    cat=state_catalog(x,t,block=12)
    future=t[-1]+np.arange(1,1009)*3600000
    a,log=regime_clock_path(cat,future,seed=18)
    b,_=regime_clock_path(cat,future,seed=18)
    np.testing.assert_array_equal(a,b)
    assert log['n_blocks']>=80
    assert 0<=log['clock_matched_blocks']<=log['n_blocks']
    assert log['fallback_blocks']+log['clock_matched_blocks']==log['n_blocks']
    for row in a:
        assert np.any(np.all(x==row,axis=1))

def test_catalog_fails_on_discontinuous_history():
    x=np.random.default_rng(19).normal(size=(2500,3))
    t=np.arange(2500,dtype=np.int64)*60000
    t[2000]=t[1999]
    with pytest.raises(ValueError,match='strictly ascending'):
        state_catalog(x,t,block=15)

def test_temporal_metrics_and_errors_zero_on_identity():
    rng=np.random.default_rng(21)
    x=rng.normal(size=(1500,3))
    t=np.arange(1500,dtype=np.int64)*60000
    d=temporal_metrics(x,t)
    s=score_metrics(d,d)
    assert all(v==0.0 for v in s.values() if v is not None)

def test_aggregate_nonsignificant_when_missing_origins():
    d=aggregate([])
    assert d['n_origins']==0
    assert all(d['models'][name]['n_usable_origins']==0 for name in MODELS)
    assert all(d['models'][name]['n_above_q90']==0 for name in MODELS)
