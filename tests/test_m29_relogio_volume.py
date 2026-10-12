import numpy as np
from experiments import m29_relogio_volume as m


def _clocked(n=6000,seed=0,amp=1.0):
    rng=np.random.default_rng(seed);x=rng.normal(size=(n,3))
    for t in range(1,n):x[t,2]=.5*x[t-1,2]+np.sqrt(.75)*x[t,2]
    moh=np.arange(n)%60
    true=np.zeros(60);true[0]=amp;true[30]=amp/2;true[58]=-amp/2
    x[:,2]+=true[moh]
    seg=np.repeat(rng.integers(0,2,size=n//300+1),300)[:n];x[:,2]+=1.2*seg
    return x,moh,true


def test_profile_recovers_planted_clock():
    x,moh,true=_clocked()
    prof,d=m.clock_profile(x[:,2],moh)
    assert int(np.argmax(prof))==0 and d['shrink']>.5
    assert np.corrcoef(prof,true-true.mean())[0,1]>.8


def test_profile_shrinks_without_clock():
    x,moh,_=_clocked(amp=0.)
    _,d=m.clock_profile(x[:,2],moh)
    assert d['shrink']<.5


def test_clock_sampler_finite_and_periodic():
    x,moh,_=_clocked(amp=1.5)
    f,d=m.fit_local_clk(x,moh,3)
    y=f(np.random.default_rng(2),1500,0)
    assert y.shape==(1500,3) and np.isfinite(y).all()
    prof=np.bincount(np.arange(1500)%60,weights=y[:,2],minlength=60)/25
    assert int(np.argmax(prof))==0
