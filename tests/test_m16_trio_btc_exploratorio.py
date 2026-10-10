"""M16: exploratory-only data, prefix-only nulls, three rulers, strict aggregation."""
import numpy as np
import pytest
from experiments import m16_trio_btc_exploratorio as m
from experiments.persistencia_dependencia import checked_exploratory_month


def test_reserved_months_refused():
    for bad in ('BTCUSDT-1m-2026-08.zip','BTCUSDT-1h-2025-01.zip','BTCUSDT-1m-2026-09.zip'):
        interval=bad.split('-')[1]
        with pytest.raises(ValueError):checked_exploratory_month(bad,interval)
    assert checked_exploratory_month('BTCUSDT-1m-2026-07.zip','1m')=='2026-07'
    assert checked_exploratory_month('BTCUSDT-1h-2024-12.zip','1h')=='2024-12'


def test_budget_and_shards():
    assert m.REFS==39
    assert m.n_shards(84,'1m')==21 and m.n_shards(18,'1h')==6
    assert m.ALPHA_CLASS==pytest.approx(.00625)


def test_seeds_distinct():
    seen={m.seed_int(i,k,3,mi,j) for i in (1,2) for k in range(5) for mi in range(4) for j in range(39)}
    assert len(seen)==2*5*4*39


def _fake_rows(interval,n,alarm_m11,alarm_energy):
    rows=[]
    for k in range(n):
        models={}
        for mname in m.MODELS:
            models[mname]={s:{'valid':True,'p_rank':.025 if a else .5,'rank_position':1 if a else 20,'alarm':a}
                           for s,a in (('m11',alarm_m11(k)),('fr_cov',False),('energy',alarm_energy(k)))}
        rows.append({'interval':interval,'origin':k,'status':'valid','window_start_ms':0,'window_end_ms':1,'models':models})
    return rows


def test_classification_directions():
    shape=_fake_rows('1m',84,lambda k:k<40,lambda k:False)
    agg=m.aggregate(shape,{'1m':84})
    assert agg['classification']['1m|N0_stationary']['label'].startswith('falta forma')
    mem=_fake_rows('1m',84,lambda k:False,lambda k:k<40)
    assert m.aggregate(mem,{'1m':84})['classification']['1m|N0_stationary']['label'].startswith('falta memoria')
    none=_fake_rows('1m',84,lambda k:False,lambda k:False)
    assert m.aggregate(none,{'1m':84})['classification']['1m|N0_stationary']['label'].startswith('sem evidencia')
    both=_fake_rows('1m',84,lambda k:k<40,lambda k:k<40)
    assert m.aggregate(both,{'1m':84})['classification']['1m|N0_stationary']['label'].startswith('inadequado')


def test_aggregate_fails_closed():
    rows=_fake_rows('1m',3,lambda k:False,lambda k:False)
    with pytest.raises(ValueError,match='Missing'):m.aggregate(rows,{'1m':4})
    with pytest.raises(ValueError,match='Missing'):m.aggregate(rows+rows[:1],{'1m':3})
