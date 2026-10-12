import numpy as np
from experiments import m30_volume_reage_choques as m


def _feedback(n=6000,seed=0,bz=.4,bi=-.3):
    """Volume mean responds to |z| (+) and |iota| (-) of the previous minute."""
    rng=np.random.default_rng(seed);x=rng.normal(size=(n,3))
    for t in range(1,n):
        x[t,2]=.5*x[t-1,2]+bz*abs(x[t-1,0])+bi*abs(x[t-1,1])+.8*x[t,2]
    seg=np.repeat(rng.integers(0,2,size=n//300+1),300)[:n];x[:,2]+=1.2*seg
    return x,np.arange(n)%60


def test_magnitude_signs_recovered():
    x,moh=_feedback()
    _,d=m.fit_local_fb(x,moh,3)
    assert d['beta_median']['beta_absz_tot']>.15
    assert d['beta_median']['beta_absiota_tot']<-.1


def test_no_feedback_gives_small_betas():
    x,moh=_feedback(bz=0.,bi=0.)
    _,d=m.fit_local_fb(x,moh,3)
    assert abs(d['beta_median']['beta_absz_tot'])<.1 and abs(d['beta_median']['beta_absiota_tot'])<.1


def test_sampler_finite_and_reproduces_feedback():
    x,moh=_feedback(bz=.6,bi=0.)
    f,_=m.fit_local_fb(x,moh,3)
    y=f(np.random.default_rng(2),1500,0)
    assert y.shape==(1500,3) and np.isfinite(y).all()
    c=np.corrcoef(np.abs(y[:-1,0]),y[1:,2])[0,1]
    assert c>.05
