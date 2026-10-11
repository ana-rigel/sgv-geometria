import numpy as np
from experiments import m23_modelo_minimo as m


def _var_garch(n=6000,seed=0):
    rng=np.random.default_rng(seed);A=np.diag([.1,.2,.5]);x=np.zeros(3);h=np.ones(3);u=np.zeros(3);out=[]
    seg=np.repeat(rng.integers(0,2,size=n//300+1),300)[:n]
    for t in range(n):
        h=.05+.1*u**2+.85*h;u=np.sqrt(h)*rng.normal(size=3)
        x=np.array([0,0,1.2*seg[t]])+A@x+u;out.append(x.copy())
    return np.array(out)


def test_garch_recovers_parameters():
    rng=np.random.default_rng(1);h=1.;u=[]
    for _ in range(8000):
        h=.05+.1*(u[-1]**2 if u else 0)+.85*h;u.append(np.sqrt(h)*rng.normal())
    u=np.array(u);u/=u.std()
    a,b=m.fit_garch(u);assert .05<a<.2 and .7<b<.93


def test_msar_samples_reproduce_lag_structure():
    x=_var_garch()
    for lm in (False,True):
        f,d=m.fit_msar(x,3,lm=lm)
        y=f(np.random.default_rng(4),3000)
        assert y.shape==(3000,3) and np.isfinite(y).all()
        ac=np.corrcoef(y[1:,2],y[:-1,2])[0,1];assert ac>.4
        a2=np.corrcoef(np.abs(y[1:,0]),np.abs(y[:-1,0]))[0,1];assert a2>.02
        assert all(g['alpha']+g['beta']<.999 for g in d['garch'])


def test_design():
    assert m.NULLS==('MSAR','MSARLM','MSDCCLM','BL') and len(m.STATS)==12
