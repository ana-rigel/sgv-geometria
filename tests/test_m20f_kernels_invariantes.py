"""M20f invariance/cost/causality controls; synthetic only."""
import numpy as np
from experiments import m20f_kernels_invariantes as m
from experiments.m20c_acoplamento_condicional import random_rotation


def test_exact_rbf_and_dcov_invariant_under_joint_so3():
    rg=np.random.default_rng(48)
    x,y=rg.standard_normal((90,3)),rg.standard_normal((90,3))
    q=random_rotation(rg)
    a,b=m.distance_squared(x),m.distance_squared(y)
    ar,br=m.distance_squared(x@q),m.distance_squared(y@q)
    for sigma in (.3,1.0,2.0):
        score=m.hsic_from_d2(a,b,sigma)
        score_rot=m.hsic_from_d2(ar,br,sigma)
        assert abs(score-score_rot)<1e-9
    assert abs(m.distance_covariance_from_d2(a,b)
               -m.distance_covariance_from_d2(ar,br))<1e-9


def test_rbf_dcov_positive_for_coupling():
    rg=np.random.default_rng(44)
    x=rg.standard_normal((120,3))
    y=x+.05*rg.standard_normal((120,3))
    dz=m.distance_squared(x)
    dq=m.distance_squared(y)
    null=m.distance_squared(rg.standard_normal((120,3)))
    assert m.hsic_from_d2(dz,dq,1.0)>m.hsic_from_d2(dz,null,1.0)
    assert m.distance_covariance_from_d2(dz,dq)>m.distance_covariance_from_d2(dz,null)


def test_same_temporal_pairs_all_methods():
    rg=np.random.default_rng(32)
    x=rg.standard_normal((1800,3))
    for n,pairs_count in ((500,192),(1800,320)):
        a,b=m.pairs(x,n)
        assert a.shape==(pairs_count,3)
        assert b.shape==(pairs_count,3)
        v=m.score_pairs(a,b,1.0,2.0,0,np.array([1.,0.,0.]))
        assert set(v)==set(m.METHODS)
        assert all(np.isfinite(x) and x>=0 for x in v.values())


def test_prefix_train_validate_only():
    rg=np.random.default_rng(9)
    arr=rg.standard_normal((2600,3))
    a=m.bandwidth_from_prefix(arr[:800])
    arr[800:]*=1000.
    b=m.bandwidth_from_prefix(arr[:800])
    assert a==b


def test_future_scores_independent_of_reference_count():
    a=m.one_trial(2,1,seed=999,n_refs=2)
    b=m.one_trial(2,1,seed=999,n_refs=3)
    assert a["observed"]==b["observed"]
    assert a["bandwidth_index"]==b["bandwidth_index"]
    assert a["direction_index"]==b["direction_index"]


def test_score_reproducibility():
    a=m.one_trial(3,1,seed=12345,n_refs=2)
    b=m.one_trial(3,1,seed=12345,n_refs=2)
    assert a==b


def test_bandwidth_is_finite_positive():
    rg=np.random.default_rng(91)
    p=rg.standard_normal((800,3))
    sigma0,selected,idx,scores=m.bandwidth_from_prefix(p)
    assert sigma0>0 and selected>0
    assert idx in (0,1,2)
    assert len(scores)==3


def test_oracle_uses_1d_projected_series_pairwise():
    rg=np.random.default_rng(67)
    x,y=rg.standard_normal((100,3)),rg.standard_normal((100,3))
    scores=m.score_pairs(x,y,1,1,0,np.array([1.,0.,0.]))
    assert abs(scores["oracle_direction_hsic"]
               -m.directional_pair_hsic(x[:,[0]],y[:,[0]],np.array([[1.]]))[0])<1e-12
