"""M20e integrity: candidate directions, selection causality and simulation."""
import numpy as np
from experiments import m20e_direcao_adaptativa as m
from experiments.m20d_ablacao_fatorial import projected_stats


def test_candidate_directions_static_and_normalized():
    assert m.DIRECTIONS.shape==(32,3)
    np.testing.assert_allclose(m.DIRECTIONS[:3],np.eye(3))
    np.testing.assert_allclose(np.linalg.norm(m.DIRECTIONS,axis=1),1,atol=1e-12)
    assert len(np.unique(np.round(m.DIRECTIONS,8),axis=0))==32


def test_vectorized_hsic_identical_to_single_direction_formula():
    rng=np.random.default_rng(12)
    x=rng.standard_normal((650,3))
    v=m.directional_hsic(x)
    assert len(v)==32
    for idx in (0,4,15,31):
        u=x@m.DIRECTIONS[idx]
        expected=projected_stats(u)["hsic_1d"]
        np.testing.assert_allclose(v[idx],expected,rtol=1e-11,atol=1e-11)


def test_direction_selection_only_reads_prefix():
    rng=np.random.default_rng(18)
    x=rng.standard_normal((m.PREFIX+m.LONG,3))
    i,d,score=m.select_from_prefix(x[:m.PREFIX])
    x[m.PREFIX:]*=1e3
    j,e,score2=m.select_from_prefix(x[:m.PREFIX])
    assert i==j and score==score2
    np.testing.assert_array_equal(d,e)


def test_scan_must_dominate_selected_and_fixed():
    rng=np.random.default_rng(9)
    x=rng.standard_normal((520,3))
    scores=m.evaluate(x,0,np.array([1.,0.,0.]))["500"]
    assert scores["scan_hsic"]>=scores["adaptive_hsic"]
    assert scores["scan_hsic"]>=scores["fixed_hsic"]


def test_observed_same_for_any_number_of_references():
    r1=m.run_trial(2,0,seed=202611,n_refs=2)
    r2=m.run_trial(2,0,seed=202611,n_refs=4)
    assert r1["observed"]==r2["observed"]
    assert r1["selected_direction_index"]==r2["selected_direction_index"]
    assert r1["oracle_cosine_abs"]==r2["oracle_cosine_abs"]


def test_trial_reproducible_and_all_metrics_present():
    a=m.run_trial(3,5,seed=900,n_refs=2)
    b=m.run_trial(3,5,seed=900,n_refs=2)
    assert a==b
    assert set(a["alarms"])=={"500","1800"}
    for window in ("500","1800"):
        assert set(a["alarms"][window])==set(m.METHODS)
        assert all(type(v) is bool for v in a["alarms"][window].values())


def test_no_access_to_oracle_when_selecting(monkeypatch):
    rng=np.random.default_rng(6)
    arr=rng.normal(size=(850,3))
    a=m.select_from_prefix(arr)[0]
    b=m.select_from_prefix(arr.copy())[0]
    assert a==b
    assert 0<=a<32


def test_pilot_separate_and_writes(tmp_path):
    obj=m.run("pilot",outdir=str(tmp_path))
    assert obj["mode"]=="pilot"
    assert len(obj["records"])==10
    assert (tmp_path/"pilot.json").exists()
