import numpy as np
from experiments import m21b_dependencia_btc as m


def test_stats_detect_known_dependence():
    rng=np.random.default_rng(0);n=1500
    iid=rng.normal(size=(n,3))
    s0=m.dep_stats(iid)
    # nonlinear lag-1 dependence invisible to linear covariance: y_t = sin(2 x_{t-1}) + noise
    x=np.empty((n,3));x[0]=rng.normal(size=3)
    for t in range(1,n):x[t]=np.r_[np.sin(2*x[t-1,0])+.3*rng.normal(),rng.normal(size=2)]
    s1=m.dep_stats(x)
    assert s1['hsic_1']>3*s0['hsic_1']
    # volatility memory shows in vol_1
    v=np.empty((n,3));sig=1.
    for t in range(n):
        sig=np.sqrt(.1+.85*sig**2*rng.normal()**2/1.0) if t else 1.;v[t]=sig*rng.normal(size=3)
    assert m.dep_stats(v)['vol_1']>m.dep_stats(iid)['vol_1']


def test_copula_is_rank_invariant():
    rng=np.random.default_rng(1);x=rng.normal(size=(500,3))
    y=np.c_[np.exp(x[:,0]),x[:,1]**3,x[:,2]]
    np.testing.assert_allclose(m.copula(x),m.copula(y))


def test_design():
    assert m.REFS==39 and m.LAGS==(1,5,30) and abs(m.ALPHA-.05/3)<1e-12
