import numpy as np
from experiments import m25_vol_multiescala as m


def _multiscale_vol(n=8000,seed=0):
    rng=np.random.default_rng(seed);slow=0.;h=1.;u=[]
    for t in range(n):
        slow=.995*slow+.1*rng.normal()
        h=.2+.15*(u[-1]**2 if u else 1)+.5*h
        u.append(np.sqrt(h*np.exp(slow))*rng.normal())
    u=np.array(u);return u/u.std()


def test_lagged_means_alignment():
    u2=np.arange(1,301,dtype=float);M=m.lagged_means(u2)
    assert M[100,0]==u2[99] and np.isclose(M[100,1],u2[85:100].mean()) and np.isclose(M[260,3],u2[20:260].mean())


def test_harch_finds_slow_component():
    u=_multiscale_vol();p=m.fit_harch(u)
    assert sum(p)<.999 and min(p)>=0
    assert p[2]+p[3]>.02          # some weight on the 60/240 horizons


def test_harv_samples_finite():
    rng=np.random.default_rng(1);n=6000
    seg=np.repeat(rng.integers(0,2,size=n//300+1),300)[:n]
    x=rng.normal(size=(n,3));x[:,2]+=1.2*seg
    f,d=m.fit_harv(x,3);y=f(np.random.default_rng(2),1500)
    assert y.shape==(1500,3) and np.isfinite(y).all() and len(d['harch'])==3
