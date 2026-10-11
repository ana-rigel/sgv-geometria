"""M20e consolidation math and fail-closed unit checks."""
import json
import pytest
from scripts import m20e_agregar as m


def fake_row(scenario,trial):
    return {
        "scenario":scenario,"trial":trial,
        "oracle_cosine_abs":0.9,
        "selected_direction_index":0,
        "alarms":{
            n:{metric:bool(metric=="adaptive_hsic") for metric in m.METHODS}
            for n in m.LENS},
        "observed":{n:{metric:1. for metric in m.METHODS}
                    for n in m.LENS},
        "null_max":{n:{metric:0. for metric in m.METHODS}
                    for n in m.LENS},
    }


def test_mcnemar_exact_pairing():
    rows=[fake_row("hidden_plus",i) for i in range(64)]
    val=m.mcnemar(rows,"adaptive_hsic","fixed_hsic")
    assert val["only_a"]==64 and val["only_b"]==0
    assert val["delta_pp"]==100
    assert val["p_one_sided_exact"]<.000001


def test_wilson_boundaries():
    assert m.wilson(0,64)[0]==0
    assert m.wilson(64,64)[1]==1
    assert m.wilson(0,64)[1]<.1


def test_missing_shards_fail_closed(tmp_path):
    with pytest.raises(FileNotFoundError):
        m.load(tmp_path)


def test_duplicate_trials_fail_closed(tmp_path):
    obj={
        "mode":"full","seed":20261011,
        "scenario_ids":[0],"scenarios":["null"],"trials_per_scenario":64,
        "prefix":800,"future_short":500,"future_long":1800,
        "references":19,"n_directions":32,"methods":list(m.METHODS),
        "records":[fake_row("null",0) for _ in range(64)]}
    (tmp_path/"shard_0.json").write_text(json.dumps(obj))
    with pytest.raises(ValueError,match="duplicate"):
        m.load(tmp_path)


def test_rate_algebra_for_two_processes():
    groups={scenario:[fake_row(scenario,i) for i in range(64)]
            for scenario in m.SCENARIOS}
    res=m.summarize(groups)
    assert res["rates"]["hidden_plus"]["500"]["adaptive_hsic"]["rate"]==1
    assert res["rates"]["hidden_plus"]["500"]["fixed_hsic"]["rate"]==0
    assert res["gates"]["G4_adaptive_beats_fixed_10pp_paired_p_lt_025"]
