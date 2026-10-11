"""M20d aggregation integrity and paired-factor formulas."""
import json
import pytest
from scripts import m20d_agregar as m

def example(t=0,positive=False):
    cells={}
    values={}
    for d in m.D:
        for n in m.N:
            for r in m.R:
                ck=m.cell(d,n,r)
                cells[ck]={metric:bool(positive and d=="known" and n==1800)
                            for metric in m.METHODS}
                values[ck]={metric:1.0 for metric in m.METHODS}
    return {"scenario":"hidden_plus","trial":t,
            "alarms":cells,"observed_scores":values,
            "blind_rff3d":{f"n{n}_{r}":False for n in m.N for r in m.R}}

def test_effects_are_paired_and_not_eight_independent_units():
    result=m.paired_effects([example(i,positive=True) for i in range(64)],"hsic_1d")
    assert result["direction"]["delta_pp"]==25.
    assert result["sample_size"]["delta_pp"]==25.
    assert result["null_model"]["delta_pp"]==0.
    assert result["direction"]["paired_trial_n"]==64

def test_wilson_and_empty_mcnemar_design():
    assert m.wilson(0,64)[0]==0.
    assert 0.<m.wilson(0,64)[1]<.1

def test_missing_shards_fail_closed(tmp_path):
    with pytest.raises(FileNotFoundError):
        m.load(tmp_path)

def test_bad_duplicate_trial_fails_closed(tmp_path):
    obj={
        "mode":"full","seed":20261011,"prefix":800,
        "future_short":500,"future_long":1800,"references":19,
        "trials_per_scenario":64,"scenario_ids":[0],
        "scenarios":["null"],"metrics":list(m.METHODS),
        "records":[dict(example(0),scenario="null") for _ in range(64)]
    }
    (tmp_path/"shard_0.json").write_text(json.dumps(obj))
    with pytest.raises(ValueError, match="duplicate"):
        m.load(tmp_path)
