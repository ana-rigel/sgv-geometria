import numpy as np
from experiments import m26_resiliencia_cruzada as m


def _resilient(n=12000,seed=0):
    """Coordinate 1's variance falls after big coordinate-0 shocks (negative cross term)."""
    rng=np.random.default_rng(seed);r=np.zeros((n,3));h=np.ones(3)
    for t in range(1,n):
        r2=r[t-1]**2
        h=np.array([.3+.2*r2[0]+.5*h[0], .7+.3*r2[1]-.15*r2[0]+.15*h[1], .4+.2*r2[2]+.4*h[2]])
        h=np.maximum(h,.05);r[t]=np.sqrt(h)*rng.normal(size=3)
    return r/r.std(0)


def test_cross_term_sign_recovered():
    P=m.fit_cross(_resilient())
    assert P[1][0]<0           # iota <- z cross term negative
    assert P[1][1]>0           # own term positive


def test_harx_samples_finite():
    rng=np.random.default_rng(1);n=6000
    seg=np.repeat(rng.integers(0,2,size=n//300+1),300)[:n]
    x=rng.normal(size=(n,3));x[:,2]+=1.2*seg
    f,d=m.fit_harx(x,3);y=f(np.random.default_rng(2),1500)
    assert y.shape==(1500,3) and np.isfinite(y).all() and len(d['cross'])==3
