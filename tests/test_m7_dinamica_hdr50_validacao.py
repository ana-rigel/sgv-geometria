"""M7 regression gates: paired error arithmetic, causality and descriptive bootstrap."""
import numpy as np
import pytest
from sgvgeo.flow import default_sf1,simulate_sf1
from experiments.m7_dinamica_hdr50_validacao import (
    paired_summary,real_precision,refine_real,same_flow,single_origin,
    calibrate,MEASURES,NAMES)

def test_summary_errors_preserve_pairing_and_direction():
    def record(value):
        return {'errors':{'delta_D':value,'D_b':value,'convex_deficit_b':value},
                'n_valid':4,'n_total':4}
    rows=[]
    for i in range(6):
        rows.append({'models':{
            'sf1':record(.3),
            'm5_independent':record(.15),
            'm6_coupled':record(.1 if i<4 else .2)}})
    s=paired_summary(rows)
    assert s['paired']['m6_vs_m5_independent']['n_paired']==6
    assert s['paired']['m6_vs_m5_independent']['quality_gate']
    assert s['paired']['m6_vs_m5_independent']['metrics']['delta_D']['m6_better_count']==4
    assert s['models']['m5_independent']['median_abs_error']['D_b']==.15

def test_insufficient_pairs_do_not_generate_winner():
    r={'models':{n:{'errors':None,'n_valid':0,'n_total':4} for n in NAMES}}
    s=paired_summary([r]*6)
    assert not s['paired']['m6_vs_m5_independent']['quality_gate']
    assert s['paired']['m6_vs_m5_independent']['n_paired']==0

def test_price_and_flow_cannot_be_changed():
    frame=simulate_sf1(default_sf1(),3000,seed=39)
    assert same_flow(frame,frame,1500)
    other=frame.copy()
    other.loc[2800:,'taker_buy']*=.8
    assert not same_flow(frame,other,1500)

def test_synthetic_origin_regression():
    r=calibrate()
    assert r['paired_control']
    assert set(r['model_valid_counts'])==set(NAMES)

def test_bootstrap_is_diagnostic_not_significance():
    frame=simulate_sf1(default_sf1(),3200,seed=40)
    r=real_precision(frame,1500,42,block=12,reps=4)
    assert r['n_total']==4
    assert r['delta_D_bootstrap_p10_p50_p90'] is None

def test_grid_has_two_prespecified_levels():
    frame=simulate_sf1(default_sf1(),3200,seed=43)
    result=refine_real(frame,1500,45)
    assert '35' in result and '49' in result

def test_origin_rejects_discontinuous_timestamps():
    frame=simulate_sf1(default_sf1(),7000,seed=46)
    frame.loc[5100:,'timestamp']+=60000
    with pytest.raises(ValueError,match='Discontinuous'):
        single_origin(frame.iloc[:5000],frame.iloc[5000:6500],
                      60000,47,reps=1)
