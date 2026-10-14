"""C01 synthetic-only sanity tests for density, entropy, information and HDR."""
import numpy as np
from scipy.stats import multivariate_normal
from experiments.c01_oraculo_hdr_fisher import (
    GMM3, base_model, known_pair, entropy_mc, delta_entropy_mc,
    fr_covariance, fr_ambient_mc, energy_distance, hdr_measure,
    hdr_pair, common_bounds,
)

def test_gmm_mass_and_spd():
    p=base_model()
    assert p.weights.sum()==1.
    assert np.min(np.linalg.eigvalsh(p.covs))>0.
    mu,cov=p.moments()
    np.testing.assert_allclose(mu,0,atol=1e-14)
    np.testing.assert_allclose(cov,np.eye(3),atol=1e-14)

def test_mixture_against_scipy():
    p=GMM3(np.array([1.]),np.zeros((1,3)),np.eye(3)[None,:,:])
    x=np.random.default_rng(3).normal(size=(12,3))
    np.testing.assert_allclose(p.logpdf(x),multivariate_normal.logpdf(x,mean=np.zeros(3),cov=np.eye(3)))

def test_entropy_gaussian_analytic():
    p=GMM3(np.array([1.]),np.zeros((1,3)),np.eye(3)[None,:,:])
    observed,se=entropy_mc(p,n=30000,seed=201)
    exact=1.5*np.log(2*np.pi*np.e)
    assert abs(observed-exact)<4*se

def test_transformation_analytic_entropy():
    p=base_model();q=p.affine(1.25*np.eye(3))
    delta,se=delta_entropy_mc(p,q,n=40000,seed=777)
    assert abs(delta-3*np.log(1.25))<4*se

def test_rotated_mixture_equal_moments_not_equal_density():
    p,q=known_pair('T3')
    np.testing.assert_allclose(p.moments()[0],q.moments()[0],atol=1e-13)
    np.testing.assert_allclose(p.moments()[1],q.moments()[1],atol=1e-13)
    assert fr_covariance(p,q)<1e-12
    assert abs(p.logpdf([[.85,0,0]])[0]-q.logpdf([[.85,0,0]])[0])>.01
    v=fr_ambient_mc(p,q,n=20000,seed=51)
    assert v['affinity']+4*v['affinity_se']<1

def test_ambient_identity_and_symmetry():
    p,q=known_pair('T0')
    assert fr_ambient_mc(p,q,n=8000,seed=44)['fr_ambient']<1e-7
    p,q=known_pair('T1')
    ab=fr_ambient_mc(p,q,n=20000,seed=44)
    ba=fr_ambient_mc(q,p,n=20000,seed=44)
    assert abs(ab['affinity']-ba['affinity'])<5*(ab['affinity_se']+ba['affinity_se'])

def test_translation_frcov_blind():
    p,q=known_pair('T1')
    assert fr_covariance(p,q)<1e-12
    assert fr_ambient_mc(p,q,n=20000,seed=65)['fr_ambient']>.1

def test_energy_identity_and_translation():
    rng=np.random.default_rng(14)
    x=base_model().sample(300,rng)
    assert abs(energy_distance(x,x))<1e-10
    assert energy_distance(x,x+np.array([0.,.8,0.]))>.02

def test_hdr_mass_calibration_and_closed_mesh():
    p=base_model()
    for alpha in (.5,.95):
        z=hdr_measure(p,alpha=alpha,seed=200,grid_n=35)
        assert z['is_watertight'] and not z['touches_boundary']
        assert abs(z['coverage_error'])<.015
        assert z['volume']>0 and z['area']>0

def test_hdr_precision_35_49():
    p=base_model();bounds=common_bounds(p,p)
    a=hdr_measure(p,alpha=.5,seed=200,grid_n=35,bounds=bounds)
    b=hdr_measure(p,alpha=.5,seed=200,grid_n=49,bounds=bounds)
    assert abs(b['volume']/a['volume']-1)<.1
    assert abs(b['area']/a['area']-1)<.1

def test_hdr_t0_t1_centers():
    p,q=known_pair('T0')
    null=hdr_pair(p,q,alpha=.5,seed=113,grid_n=35)
    assert null['center_distance']<.15
    p,q=known_pair('T1')
    move=hdr_pair(p,q,alpha=.5,seed=113,grid_n=35)
    assert .35<move['center_distance']<.85

def test_independent_samples_and_immutable_parameters():
    p,q=known_pair('T0')
    aa=p.sample(500,np.random.default_rng(4))
    bb=q.sample(500,np.random.default_rng(5))
    assert not np.array_equal(aa,bb)
    try:p.means[0,0]=99
    except ValueError:pass
    else:raise AssertionError('oracle parameters must be read-only')
