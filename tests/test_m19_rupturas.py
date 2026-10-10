"""M19: reserved-month gate, window grid, event mapping, permutation test."""
import hashlib,json
import numpy as np
import pytest
from experiments import m19_rupturas as m


def test_gate_refuses_without_frozen_protocol(tmp_path,monkeypatch):
    p=tmp_path/'P.md';monkeypatch.setattr(m,'PROTOCOL',p)
    with pytest.raises(PermissionError):m.protocol_gate('x')
    p.write_text('rascunho');
    with pytest.raises(PermissionError,match='not frozen'):m.protocol_gate(hashlib.sha256(p.read_bytes()).hexdigest())
    p.write_text('STATUS: CONGELADO\n')
    with pytest.raises(PermissionError,match='mismatch'):m.protocol_gate('0'*64)
    assert m.protocol_gate(hashlib.sha256(p.read_bytes()).hexdigest())


def test_reserved_months_only_in_confirmatory_mode(monkeypatch,tmp_path):
    monkeypatch.setattr(m,'PROTOCOL',tmp_path/'none.md')
    with pytest.raises(PermissionError):m.archives('confirmatorio','abc')
    bad=dict(m.PERIODS['ensaio']);bad['months']=['2026-08']
    monkeypatch.setitem(m.PERIODS,'ensaio',bad)
    with pytest.raises(PermissionError,match='outside confirmatory'):m.archives('ensaio')


def test_grid_fits_period():
    assert m.N_WINDOWS*m.WINDOW<=61*1440
    assert (m.N_WINDOWS+1)*m.WINDOW>61*1440


def test_event_mapping():
    rows=[{'window':k,'start_ms':k*90_000_000,'end_ms':(k+1)*90_000_000-60000} for k in range(5)]
    ev=m.event_windows([{'utc':'1970-01-02T02:00:00'}],rows)   # 26 h -> window 1
    assert ev=={1}
    ev=m.event_windows([{'date':'1970-01-02'}],rows)            # 24h..48h overlaps windows 0,1
    assert ev=={0,1}


def test_circular_shift_detects_and_respects_null():
    x=np.zeros(58,bool);x[[5,20,40]]=True
    y=x.copy()
    d,p=m.circular_shift_p(x,y);assert d==1 and p<.05
    rng=np.random.default_rng(0);y=rng.random(58)<.1
    _,p=m.circular_shift_p(x,y);assert p>.01
