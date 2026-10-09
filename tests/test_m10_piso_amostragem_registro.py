"""M10: controlled rigid equivalence, point floor, bootstrap and quality gates."""
import numpy as np
import pytest
from experiments.m10_piso_amostragem_registro import (
    known_shape_controls,six_seed_scores,small_floor,
    one_window,summarise,synthetic,bootstrap_temporal,DENSITIES)
from experiments.isosuperficies_morfometria import analytic_field,extract_mesh
from sgvgeo.flow import default_sf1,simulate_sf1,flow_coordinates


def sphere():
    f,t,dx=analytic_field('sphere',61)
    s,truncated=extract_mesh(f,t,dx)
    assert not truncated
    return s


def test_same_mesh_has_positive_sampling_floor():
    s=sphere()
    v=six_seed_scores(s,s,seed=101,n=180,reps=4)
    assert v['floor_max_self_q90']>0.
    assert v['observed_median']>0.
    assert v['excess_over_floor']>=0.
    assert v['n_seed_repeats']==4


def test_exact_rigid_equivalence_and_shape_change_are_recorded():
    r=known_shape_controls(seed=111,n=180,reps=4)
    assert r['rigid_equivalent']['n_points_each_set']==180
    assert r['truly_deformed']['observed_median']>0


def test_larger_samples_reduce_floor_in_known_sphere():
    a=sphere()
    lo=six_seed_scores(a,a,seed=113,n=180,reps=4)
    hi=six_seed_scores(a,a,seed=113,n=720,reps=4)
    assert hi['floor_max_self_q90']<lo['floor_max_self_q90']


def test_invalid_seed_count_rejected():
    s=sphere()
    with pytest.raises(ValueError,match='At least four'):
        six_seed_scores(s,s,seed=103,n=180,reps=3)


def test_reduced_floor_is_a_diagnostic_not_significance():
    s=sphere()
    p=small_floor(s,s,seed=114,n=180,reps=3)
    assert p is not None
    assert p['deformation']>0
    assert p['excess']>=0


def test_bootstrap_reports_insufficient_replication():
    df=simulate_sf1(default_sf1(),3200,seed=121)
    v=flow_coordinates(df)[['z','iota','nu']].to_numpy(float)[-1500:]
    r=bootstrap_temporal(v,seed=122,block=15,reps=3)
    assert r['n_requested']==3
    assert r['q10_q50_q90']['excess'] is None


def test_summary_does_not_claim_unseen_precision():
    rows=[{'measurement':{'main_360':{
        'exceeds_sampling_floor':False,
        'observed_median':.12,'floor_max_self_q90':.10,
        'excess_over_floor':.02}}}]
    s=summarise(rows)
    assert s['n_windows']==1
    assert s['n_detected_above_floor']==0
    assert s['audit_windows']==0
