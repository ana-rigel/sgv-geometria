"""M5: prior-only seasonal fit, controls, joint loss and invariants."""
import numpy as np
import pytest
from sgvgeo.flow import default_sf1,simulate_sf1
from experiments.m5_validacao_conjunta_sf1 import (
    fit_volume,season,calibrate,aggregate,joint_loss,
    VOL_KEYS,SCALE
)

def test_hourly_seasonal_fit_and_causal_prefix():
    assert calibrate()['hourly_season_available']

def test_daily_cycles_required_independently_of_sample_count():
    df=simulate_sf1(default_sf1(),2100,seed=42,step_ms=60000)
    with pytest.raises(ValueError,match='daily cycles'):
        fit_volume(df,'season',60000)

def test_hourly_memory_and_season_both_available():
    x=simulate_sf1(default_sf1(),2300,seed=16,step_ms=3600000)
    for name in ('memory','season','both'):
        f=fit_volume(x,name,3600000)
        assert f['effective_n']>1500
        assert f['lag_norm']<=.9700001
        assert np.isfinite(f['coef']).all()

def test_gap_is_not_silently_accepted():
    x=simulate_sf1(default_sf1(),2200,seed=31,step_ms=3600000)
    x.loc[1100:,'timestamp']+=3600000
    with pytest.raises(ValueError,match='Gap'):
        fit_volume(x,'memory',3600000)

def test_metric_loss_exact_on_reference():
    sample={k:.25 for k in VOL_KEYS}
    assert joint_loss(sample,sample)==0.
    one=sample.copy()
    one['nu_acf10']+=SCALE['nu_acf10']
    assert abs(joint_loss(one,sample)-.25)<1e-12

def test_gate_rejects_one_metric_gain_with_acf1_degradation():
    from experiments.m5_validacao_conjunta_sf1 import (
        VARIANTS,CONTROL_KEYS,OTHER_KEYS)
    keys=(*VOL_KEYS,*CONTROL_KEYS,*OTHER_KEYS)
    obs={k:0. for k in keys}
    base={k:{'observed':0.,'sim_median':.08,'abs_error':.08} for k in keys}
    better={k:{'observed':0.,'sim_median':.01,'abs_error':.01} for k in keys}
    better['nu_acf1']={'observed':0.,'sim_median':.15,'abs_error':.15}
    r={'metrics':{'sf1':{'metrics':base,'joint_loss':1.0},
                  'memory':{'metrics':better,'joint_loss':.5}}}
    result=aggregate([r])
    assert result['models']['memory']['passes_gate'] is False
    assert result['eligible_best_under_protocol'] is None
