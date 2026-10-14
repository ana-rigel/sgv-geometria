"""M35: retomada em lotes, sem usar BTC nem qualquer holdout."""
import json

import pytest

from scripts import m35_retomar_lotes as m


def test_synthetic_jobs_match_frozen_count_and_seeds():
    a = m.synthetic_jobs()
    assert len(a) == 60
    assert a == m.synthetic_jobs()
    assert a[0]["seed"] == 9000 and a[39]["seed"] == 9039
    assert a[40]["seed"] == 9500 and a[-1]["seed"] == 9519
    assert all(x["kind"] == "synth" for x in a)
    assert all(x["sep_a"] == x["sep_b"] for x in a[40:])


def test_shards_partition_without_repeats():
    for n in (1, 2, 3, 7, 24, 60):
        parts = [m.selected_indices(60, i, n) for i in range(n)]
        flat = [j for p in parts for j in p]
        assert len(flat) == len(set(flat)) == 60
        assert sorted(flat) == list(range(60))
    with pytest.raises(ValueError):
        m.selected_indices(60, 2, 2)


def test_resume_after_interruption(tmp_path, monkeypatch):
    path = tmp_path / "partial.json"
    seen = []

    def fail_on_second(stage, spec):
        seen.append(spec["seed"])
        if len(seen) == 2:
            raise RuntimeError("interruption")
        return {"kind": "synth", "seed": spec["seed"]}

    monkeypatch.setattr(m, "execute_spec", fail_on_second)
    with pytest.raises(RuntimeError, match="interruption"):
        m.run("synthetic", 0, 20, path, max_jobs=2)
    assert json.loads(path.read_text())["rows"] == [{"kind": "synth", "seed": 9000}]

    resumed = []
    def finish(stage, spec):
        resumed.append(spec["seed"])
        return {"kind": "synth", "seed": spec["seed"]}

    monkeypatch.setattr(m, "execute_spec", finish)
    result = m.run("synthetic", 0, 20, path, max_jobs=2)
    assert resumed == [9020]  # no repeated work from first completed job
    assert len(result["rows"]) == 2
    assert result["rows"][0]["seed"] == 9000
    assert result["rows"][1]["seed"] == 9020
    assert m.run("synthetic", 0, 20, path, max_jobs=2)["rows"] == result["rows"]
    assert len(resumed) == 1


def test_incompatible_checkpoint_is_refused(tmp_path, monkeypatch):
    path = tmp_path / "bad.json"
    monkeypatch.setattr(m, "execute_spec", lambda stage, spec: {"seed": spec["seed"]})
    m.run("synthetic", 1, 30, path, max_jobs=1)
    old = json.loads(path.read_text())
    old["source_sha256"]["experiments/m35_instrumento.py"] = "wrong"
    path.write_text(json.dumps(old))
    with pytest.raises(ValueError, match="incompatível"):
        m.run("synthetic", 1, 30, path, max_jobs=1)
