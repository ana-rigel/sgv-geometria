"""SGV — teste de causalidade SF1, seleção de janelas e simulação nula."""
import numpy as np
import pytest
from experiments.dinamica_formas_sf1 import (
    sliding_origins, valid_segment, compare_real_and_simulated,
    summarize, PREFIX,
)
from sgvgeo.flow import simulate_sf1, default_sf1


def test_origins_are_chronological_and_bounded():
    ids=sliding_origins(50_000,1500,2000,750,12)
    assert len(ids)==12
    assert ids==sorted(ids)
    assert all(2000<=i and i+1500<=50000 for i in ids)


def test_gap_breaks_contiguity():
    ts=np.arange(20,dtype=np.int64)*60000
    x=np.zeros((20,3))
    assert valid_segment(ts,x,60000)
    ts[10:]+=60000
    assert not valid_segment(ts,x,60000)


def test_future_change_does_not_change_sf1_training():
    raw=simulate_sf1(default_sf1(),6500,seed=87)
    a=compare_real_and_simulated(raw,start=2200,window=1500,step=60000,
                                 seed=5,surrogates=1)
    copy=raw.copy()
    mask=np.arange(2200+450,2200+1500)
    copy.loc[mask,"taker_buy"]=copy.loc[mask,"volume"]*.01
    b=compare_real_and_simulated(copy,start=2200,window=1500,step=60000,
                                 seed=5,surrogates=1)
    assert a["sf1_param_garch"]==b["sf1_param_garch"]
    assert a["sf1_mediana_mixture_J50"]==b["sf1_mediana_mixture_J50"]
    assert a["obs_mixture_J50"]!=b["obs_mixture_J50"]


def test_cannot_fit_without_full_prefix():
    raw=simulate_sf1(default_sf1(),4500,seed=4)
    with pytest.raises(ValueError):
        compare_real_and_simulated(raw,start=1900,window=1500,
                                   step=60000,seed=15,surrogates=1)


def test_summary_is_descriptive_not_claiming_significance():
    raw=simulate_sf1(default_sf1(),5000,seed=3)
    a=compare_real_and_simulated(raw,start=PREFIX,window=1500,
                                 step=60000,seed=4,surrogates=1)
    r=summarize([a])
    assert r["n_janelas"]==1
    assert "comparacoes" in r
    assert "limites" in r
