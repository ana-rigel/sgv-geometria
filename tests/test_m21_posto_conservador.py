import numpy as np
from experiments.m21_posto_conservador import conservative_rank


def test_matches_ordinary_rank_without_failures():
    refs=[.1,.2,.3,.4];assert conservative_rank(.35,refs)==(1+1)/5
    assert conservative_rank(.5,refs)==1/5


def test_failures_count_against_alarm():
    refs=[.1,.2,None,.4];assert conservative_rank(.5,refs)==2/5
    assert conservative_rank(None,refs) is None


def test_conservative_under_null():
    rng=np.random.default_rng(0);al=0;n=4000
    for _ in range(n):
        x=rng.normal(size=40);refs=list(x[1:])
        for j in rng.choice(39,size=rng.integers(0,4),replace=False):refs[j]=None
        al+=conservative_rank(x[0],refs)<=.05
    assert al/n<=.05+.01
