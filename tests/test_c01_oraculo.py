"""C01: sanity tests only. Requires numpy, scipy, pytest. No market data."""
import numpy as np
from scipy.special import logsumexp
from scipy.stats import multivariate_normal

A=0.85

def model(axis=0, shift=(0,0,0)):
    e=np.eye(3)[axis]
    cov=np.eye(3)-A*A*np.outer(e,e)
    s=np.asarray(shift,float)
    return [(0.5,A*e+s,cov),(0.5,-A*e+s,cov)]

def moments(parts):
    mu=sum(w*m for w,m,_ in parts)
    return mu,sum(w*(c+np.outer(m-mu,m-mu)) for w,m,c in parts)

def logpdf(parts,x):
    return logsumexp(np.stack([np.log(w)+multivariate_normal.logpdf(x,mean=m,cov=c) for w,m,c in parts]),axis=0)

def sample(parts,n,rng):
    labels=rng.choice(len(parts),size=n,p=[p[0] for p in parts])
    xs=np.empty((n,3))
    for j,(_,mu,cov) in enumerate(parts):
        idx=np.flatnonzero(labels==j)
        if len(idx):xs[idx]=rng.multivariate_normal(mu,cov,size=len(idx))
    return xs

def affinity_mc(p,q,n=10000,seed=42):
    rng=np.random.default_rng(seed)
    x=np.vstack((sample(p,n//2,rng),sample(q,n-n//2,rng)))
    lp,lq=logpdf(p,x),logpdf(q,x)
    v=np.exp((lp+lq)/2-np.logaddexp(lp,lq)+np.log(2))
    return float(v.mean()),float(v.std(ddof=1)/np.sqrt(n))

def fr_cov(s,t):
    l=np.linalg.cholesky(s)
    z=np.linalg.solve(l,np.eye(len(l)))
    vals=np.linalg.eigvalsh(z@t@z.T)
    return float(np.sqrt(0.5*np.sum(np.log(vals)**2)))

def test_rotated_mixture_equal_moments():
    ma,sa=moments(model(0));mb,sb=moments(model(1))
    np.testing.assert_allclose(ma,mb,atol=1e-14)
    np.testing.assert_allclose(sa,np.eye(3),atol=1e-14)
    np.testing.assert_allclose(sb,np.eye(3),atol=1e-14)
    assert fr_cov(sa,sb)<1e-12

def test_identity_affinity():
    a,se=affinity_mc(model(0),model(0),n=4000)
    assert abs(a-1)<1e-12 and se<1e-10

def test_rotated_shape_detectable_by_full_density():
    p,q=model(0),model(1)
    assert abs(np.exp(logpdf(p,[A,0,0]))-np.exp(logpdf(q,[A,0,0])))>1e-3
    a,se=affinity_mc(p,q,n=20000,seed=20261014)
    assert a+4*se<1
    assert 0<2*np.arccos(a)<np.pi

def test_translation_preserves_covariance():
    ma,sa=moments(model(0));mb,sb=moments(model(0,shift=(0,0.65,0)))
    np.testing.assert_allclose(mb-ma,[0,0.65,0],atol=1e-14)
    np.testing.assert_allclose(sa,sb,atol=1e-14)

def test_fr_cov_is_symmetric():
    s=np.diag([0.7,1.2,1.7]);t=np.diag([1.9,0.8,1.1])
    assert abs(fr_cov(s,t)-fr_cov(t,s))<1e-12

def test_affinity_symmetric_in_expectation():
    p,q=model(0),model(0,shift=(0,0.65,0))
    ab,_=affinity_mc(p,q,5000,555)
    ba,_=affinity_mc(q,p,5000,555)
    assert abs(ab-ba)<0.025
