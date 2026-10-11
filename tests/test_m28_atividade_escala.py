import numpy as np
from experiments import m28_atividade_escala as m


def _activity(n=6000,seed=0,gz=.4,gi=-.6):
    """nu persistent; scale of z grows and scale of iota shrinks with previous nu."""
    rng=np.random.default_rng(seed);x=np.zeros((n,3))
    for t in range(1,n):
        x[t,2]=.9*x[t-1,2]+np.sqrt(1-.81)*rng.normal()
        x[t,0]=np.exp(.5*gz*x[t-1,2])*rng.normal()
        x[t,1]=np.exp(.5*gi*x[t-1,2])*rng.normal()
    return x


def test_gamma_signs_recovered():
    _,d=m.fit_local_act(_activity(),3)
    gz=np.median([s['gamma_z'] for s in d['segments']]);gi=np.median([s['gamma_iota'] for s in d['segments']])
    assert gz>.15 and gi<-.25


def test_gamma_near_zero_without_effect():
    _,d=m.fit_local_act(_activity(gz=0,gi=0),3)
    gi=np.median([s['gamma_iota'] for s in d['segments']])
    assert abs(gi)<.15


def test_sampler_reproduces_scale_dependence():
    f,_=m.fit_local_act(_activity(),3)
    y=f(np.random.default_rng(5),3000)
    assert y.shape==(3000,3) and np.isfinite(y).all()
    c=np.corrcoef(y[:-1,2],np.abs(y[1:,1]))[0,1]
    assert c<-.05
