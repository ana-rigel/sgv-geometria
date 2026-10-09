"""M14: independent outer trials, past-only fitting and unchanged M11 instrument."""
import numpy as np
import pytest
from experiments.m14_calibracao_aninhada import (
    SCENARIOS,PREFIX,WINDOW,REFS,SHARDS,PER_SHARD,
    stationary_prob,sample_truth,fit_var,fit_hmm,
    sample_null,fit_null,full_m11_distance,run_trial,aggregate
)

def test_scenarios_and_budget():
    assert len(SCENARIOS)==4
    assert REFS==19
    assert SHARDS*PER_SHARD==500
    assert PREFIX==2000 and WINDOW==1500

def test_stationary_markov_probability():
    p=stationary_prob(np.array([[.98,.02],[.03,.97]]))
    np.testing.assert_allclose(p,[.6,.4])
    assert p.sum()==1

def test_independent_known_truth_and_reproducible_seed():
    for scenario in SCENARIOS:
        first=sample_truth(scenario,72)
        again=sample_truth(scenario,72)
        assert first[0].shape==(2000,3) and first[1].shape==(1500,3)
        np.testing.assert_array_equal(first[0],again[0])
        np.testing.assert_array_equal(first[1],again[1])
        assert np.isfinite(first[0]).all()
    v=sample_truth('VAR_fit',72)[1]
    h=sample_truth('HMM_fit',72)[1]
    assert not np.array_equal(v,h)

def test_var_fits_only_historical_prefix():
    prefix,future=sample_truth('VAR_fit',73)
    f1=fit_var(prefix)
    changed=future.copy()
    changed*=300
    f2=fit_var(prefix.copy())
    for k in ('A','cov','mean','intercept'):
        np.testing.assert_array_equal(f1[k],f2[k])
    assert f1['spectral_radius']<.995
    assert min(np.linalg.eigvalsh(f1['cov']))>0

def test_hmm_fit_and_sampling():
    prefix,_=sample_truth('HMM_fit',77)
    model=fit_hmm(prefix,87,restarts=2)
    assert model['type']=='hmm'
    assert np.isfinite(model['log_likelihood'])
    assert model['model'].n_components==2
    a=sample_null(model,np.random.default_rng(88),1500)
    assert a.shape==(1500,3)
    assert np.isfinite(a).all()

def test_block_null_joint_samples_are_exact_past_rows():
    prefix,_=sample_truth('HMM_to_blocks',79)
    f=fit_null('HMM_to_blocks',prefix,seed=80)
    out=sample_null(f,np.random.default_rng(81),WINDOW)
    assert out.shape==(WINDOW,3)
    assert all(np.any(np.all(prefix==row,axis=1)) for row in out[:50])

def test_full_m11_geometric_measurement():
    _,future=sample_truth('VAR_fit',93)
    d=full_m11_distance(future,94)
    assert d>=0 and np.isfinite(d)

def test_nested_rank_with_lightweight_metric_is_labeled():
    # Code-path only; statistical results MUST use default full M11 metric.
    def simple_metric(x,seed):return float(np.mean(x[:,2]**2))
    a=run_trial('VAR_fit',5,metric=simple_metric)
    b=run_trial('VAR_fit',5,metric=simple_metric)
    assert a==b
    assert a['status']=='valid'
    assert a['n_references_valid']==REFS
    assert a['rank_statistic_uncalibrated'] in np.arange(1,21)/20

def test_calibration_missing_and_duplicate_fail_closed():
    rows=[{'scenario':'VAR_fit','trial_id':0,
           'status':'valid','alarm_at_005':False}]
    with pytest.raises(ValueError,match='Missing'):
        aggregate(rows,2)
    with pytest.raises(ValueError,match='Duplicate'):
        aggregate(rows*2,2)
    vals=aggregate(rows,1)
    assert vals['n_valid']==1 and vals['alarms']==0

def test_invalid_reference_never_silently_replaced():
    def invalid_metric(x,seed):
        raise ValueError('fake instrument problem')
    trial=run_trial('VAR_fit',4,metric=invalid_metric)
    assert trial['status']=='invalid'
    assert trial['failure_stage']=='fit_or_observation'
