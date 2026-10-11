"""M20f aggregator fail closed and exact pairing."""
import json
import pytest
from scripts import m20f_agregar as m


def row(scenario,t):
    return {
        "scenario":scenario,"trial":t,
        "bandwidth_index":1,"sigma0":1.,"sigma_selected":1.,
        "prefix_validation_scores":[.1,.2,.3],
        "alarms":{n:{metric:metric in ("rbf_hsic_selected","rbf_hsic_fixed") for metric in m.METHODS}
                  for n in m.LENS},
        "observed":{n:{metric:1. for metric in m.METHODS} for n in m.LENS},
        "null_max":{n:{metric:0. for metric in m.METHODS} for n in m.LENS},
    }


def test_missing_shards_fail_closed(tmp_path):
    with pytest.raises(FileNotFoundError):
        m.load(tmp_path)


def test_duplicate_trial_fail_closed(tmp_path):
    x={"mode":"full","seed":20261011,"scenario_ids":[0],
       "scenarios":["null"],"trials_per_scenario":64,
       "prefix":800,"future_short":500,"future_long":1800,"references":19,
       "pair_counts":{"500":192,"1800":320},"methods":list(m.METHODS),
       "records":[row("null",0) for _ in range(64)]}
    (tmp_path/"shard_0.json").write_text(json.dumps(x))
    with pytest.raises(ValueError,match="duplicate"):
        m.load(tmp_path)


def test_wilson_bounds():
    assert m.wilson(0,64)[0]==0
    assert m.wilson(64,64)[1]==1


def test_mcnemar_paired_not_unpaired():
    arr=[row("hidden_plus",i) for i in range(64)]
    p=m.compare_paired(arr,"rbf_hsic_selected","rff3d_hsic")
    assert p["only_a"]==64 and p["only_b"]==0
    assert p["delta_pp"]==100.
    assert p["mcnemar_p_exact_one_sided"]<1e-6


def test_gate_model_keeps_negative_geometry_vs_baseline():
    groups={s:[row(s,i) for i in range(64)] for s in m.SCENARIOS}
    v=m.aggregate(groups)
    assert v["n_trials_independent"]==320
    assert v["gates"]["G6_band_selection_advantage"] is False
