import numpy as np
from experiments import m24_har_fhs as m


def _two_scale(n=6000,seed=0):
    rng=np.random.default_rng(seed);seg=np.repeat(rng.integers(0,2,size=n//300+1),300)[:n]
    x=np.zeros((n,3));slowc=0.
    for t in range(1,n):
        slowc=.97*slowc+.25*rng.normal()                    # ~30-step memory (intermediate scale)
        x[t]=.2*x[t-1]+np.array([0,0,1.2*seg[t]])+np.array([0,slowc,slowc])+rng.standard_t(5,size=3)*.6
    return x


def test_har_features_alignment():
    x=np.arange(200*3,dtype=float).reshape(200,3)
    t,F=m.har_features(x)
    assert t[0]==60 and np.allclose(F[0,1:4],x[59]) and np.allclose(F[0,4:7],x[45:60].mean(0)) and np.allclose(F[0,7:10],x[0:60].mean(0))


def test_companion_radius_simple():
    A=np.eye(3)*.5;Z=np.zeros((3,3))
    assert abs(m.companion_radius(A,Z,Z)-.5)<1e-9


def test_har_reproduces_intermediate_memory_and_tails():
    x=_two_scale()
    for fhs in (False,True):
        f,d=m.fit_har(x,3,fhs)
        y=f(np.random.default_rng(4),3000)
        assert y.shape==(3000,3) and np.isfinite(y).all()
        ac=np.corrcoef(y[5:,1],y[:-5,1])[0,1];assert ac>.2
    assert max(d['z_excess_kurtosis'])>.3          # real residuals keep heavy tails
