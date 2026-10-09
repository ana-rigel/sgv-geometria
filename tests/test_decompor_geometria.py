"""Identidades geometricas e respostas conhecidas da decomposicao."""
import numpy as np
import pytest
from experiments.decompor_geometria import (
    decompose, cov_divergence, stats, compare_and_bootstrap, synthetic_pair,
)
from experiments.fotografia_informacional import bhattacharyya


def snap(mu,cov):
    return {"mean":mu,"cov":cov,"logdet_cov":np.linalg.slogdet(cov)[1]}


def test_zero_same_distribution():
    mu=np.array([1.,2.,3.])
    cov=np.array([[2.,.2,.1],[.2,1.,.1],[.1,.1,.8]])
    d=decompose(mu,cov,mu,cov)
    for k in ("full","mean","covariance","scale_only","correlation_only",
              "scale_shapley","correlation_shapley"):
        assert abs(float(d[k]))<1e-12


def test_full_equals_bhattacharyya_and_accounting_identity():
    rng=np.random.default_rng(45)
    a=rng.normal(size=(800,3))
    b=rng.normal(size=(800,3))@np.array([[1.4,.2,0],[0,.7,.2],[0,0,1.2]])+0.4
    m0,c0=stats(a)
    m1,c1=stats(b)
    d=decompose(m0,c0,m1,c1)
    expected=bhattacharyya(snap(m0,c0),snap(m1,c1))
    assert np.isclose(d["full"],expected,atol=1e-12)
    assert np.isclose(d["mean"]+d["covariance"],d["full"])
    assert np.isclose(d["scale_shapley"]+d["correlation_shapley"],
                      d["covariance"],atol=1e-12)


def test_pure_mean_change_is_only_mean():
    mu=np.zeros(3)
    c=np.array([[1.,.2,.1],[.2,2.,0],[.1,0,1.]])
    d=decompose(mu,c,np.array([.8,0,0]),c)
    assert d["mean"]>0
    for key in ("covariance","scale_only","correlation_only",
                "scale_shapley","correlation_shapley"):
        assert abs(float(d[key]))<1e-12


def test_pure_scale_change_without_corr():
    mu=np.zeros(3)
    c0=np.diag([1.,2.,3.])
    c1=np.diag([4.,2.,3.])
    d=decompose(mu,c0,mu,c1)
    assert d["scale_only"]>0
    assert abs(float(d["correlation_only"]))<1e-12
    assert abs(float(d["correlation_shapley"]))<1e-12


def test_pure_correlation_change_without_scale():
    c0=np.eye(3)
    c1=np.array([[1.,-.7,0],[-.7,1.,0],[0,0,1.]])
    d=decompose(np.zeros(3),c0,np.zeros(3),c1)
    assert d["correlation_only"]>0
    assert abs(float(d["scale_only"]))<1e-12
    assert abs(float(d["scale_shapley"]))<1e-12


def test_common_affine_transform_of_full_distance():
    rng=np.random.default_rng(47)
    m0=np.array([1.,0.,2.])
    m1=np.array([1.3,-.4,1.8])
    c0=np.array([[2.,.1,.1],[.1,.9,0],[.1,0,.8]])
    c1=np.array([[2.,-.2,.1],[-.2,1.2,.3],[.1,.3,1.1]])
    matrix=np.array([[1.5,.3,-.1],[.2,.8,0],[0,0,1.3]])
    bias=np.array([1.2,-3.,4.])
    d0=decompose(m0,c0,m1,c1)
    d1=decompose(matrix@m0+bias,matrix@c0@matrix.T,
                 matrix@m1+bias,matrix@c1@matrix.T)
    assert abs(float(d0["full"]-d1["full"]))<1e-11


def test_scale_and_correlation_share_depend_on_coordinate_convention():
    """Nao requer invariancia individual Shapley a rotacao arbitraria."""
    rng=np.random.default_rng(48)
    data=rng.normal(size=(600,3))
    m0,c0=stats(data)
    m1,c1=stats(data@np.array([[1.,.5,0],[0,1.,.2],[0,0,1.1]]))
    d=decompose(m0,c0,m1,c1)
    assert np.isclose(d["full"],d["mean"]+
         d["scale_shapley"]+d["correlation_shapley"],atol=1e-12)


def test_vectorized_bootstrap_decomposition_matches_scalar():
    rng=np.random.default_rng(49)
    m0=rng.normal(size=(15,3))
    m1=rng.normal(size=(15,3))
    a=rng.normal(size=(15,3,3))
    b=rng.normal(size=(15,3,3))
    c0=np.matmul(a,np.swapaxes(a,-1,-2))+np.eye(3)
    c1=np.matmul(b,np.swapaxes(b,-1,-2))+np.eye(3)
    d=decompose(m0,c0,m1,c1)
    for j in range(15):
        scalar=decompose(m0[j],c0[j],m1[j],c1[j])
        for key in d:
            assert np.isclose(d[key][j],scalar[key],atol=1e-11)


def test_null_pvalues_and_known_changes_finite():
    for kind in ("stationary","mean","scale","correlation"):
        a,b=synthetic_pair(kind,seed=351,window=180)
        row=compare_and_bootstrap(a,b,block=8,reps=49,seed=303)
        for key in ("full","mean","scale_only","correlation_only"):
            assert 0<row["p_nom_"+key]<=1
            assert np.isfinite(row[key])
            assert row["ruido95_"+key]>=0


def test_reject_degenerate_covariance():
    x=np.ones((70,3))
    with pytest.raises(ValueError,match="degenerada"):
        stats(x)
