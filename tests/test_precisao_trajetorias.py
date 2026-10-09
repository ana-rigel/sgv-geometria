"""SGV observacional: testes de integridade numerica, nulo e trajetorias."""
import numpy as np
import pytest
from experiments.precisao_trajetorias import (
  draw_blocks, gaussian_batch, bhat_batch, noise_test, synthetic_pair,
  segments, disjoint_windows, midpoint_fisher_quadratic, calibrate
)
from experiments.fotografia_informacional import gaussian_snapshot, bhattacharyya


def test_batch_gauss_equals_scalar():
    rng=np.random.default_rng(4)
    a=rng.normal(size=(3,150,3))
    m,c=gaussian_batch(a)
    for i in range(3):
        snap=gaussian_snapshot(a[i])
        np.testing.assert_allclose(m[i],snap["mean"],atol=1e-12)
        np.testing.assert_allclose(c[i],snap["cov"],atol=1e-12)


def test_bh_batch_matches_original_and_zero():
    rng=np.random.default_rng(41)
    x=rng.normal(size=(2,190,3))
    m,c=gaussian_batch(x)
    d=bhat_batch(m[:1],c[:1],m[1:],c[1:])[0]
    ref=bhattacharyya(gaussian_snapshot(x[0]),gaussian_snapshot(x[1]))
    assert abs(d-ref)<1e-12
    assert bhat_batch(m,c,m,c).max()<1e-12


def test_local_fisher_zero_and_symmetric():
    rng=np.random.default_rng(10)
    a=gaussian_snapshot(rng.normal(size=(200,3)))
    b=gaussian_snapshot(rng.normal(loc=[.3,.1,.2],size=(200,3)))
    assert midpoint_fisher_quadratic(a,a)==0
    assert abs(midpoint_fisher_quadratic(a,b)-
               midpoint_fisher_quadratic(b,a))<1e-12


def test_block_bootstrap_wraps_and_keeps_shape():
    r=np.random.default_rng(10)
    ix=draw_blocks(r,17,22,5,99)
    assert ix.shape==(99,22)
    assert (ix>=0).all() and (ix<17).all()
    assert all((row[j+1]-row[j])%17==1 for row in ix for j in range(0,19,5))


def test_segments_gap_and_nan_fail_closed():
    a=np.random.default_rng(50).normal(size=(70,3))
    ts=np.arange(70)*60000
    ts[40:]+=60000
    a[20]=np.nan
    seg=segments(a,ts,60000)
    assert seg==[(0,20),(21,40),(40,70)]
    win=list(disjoint_windows(a,ts,60000,10))
    assert [x[1] for x in win]==[9,19,30,49,59,69]


def test_null_and_changed_pair_score():
    a,b=synthetic_pair(71,changed=True,window=350)
    out=noise_test(a,b,block=12,reps=99)
    assert out["distancia_bhattacharyya"]>0
    assert 0<out["p_nulo_local"]<=1
    assert out["ic95_rho_a"][0]<out["ic95_rho_a"][1]
    assert out["rho_preco_fluxo_a"]>0.4
    assert out["rho_preco_fluxo_b"]<-.4


def test_all_states_prefix_causal():
    rng=np.random.default_rng(6)
    a=rng.normal(size=(1300,3))
    ts=np.arange(1300)*60000
    initial=list(disjoint_windows(a[:800],ts[:800],60000,200))
    entire=list(disjoint_windows(a,ts,60000,200))
    assert len(initial)==4
    for x,y in zip(initial,entire):
        assert x[:3]==y[:3]
        np.testing.assert_array_equal(x[3],y[3])


def test_seed_deterministic_and_calibration_has_both_groups():
    a,b=synthetic_pair(102,changed=False,window=200)
    one=noise_test(a,b,block=10,reps=49,seed=18)
    two=noise_test(a,b,block=10,reps=49,seed=18)
    assert one==two
    result=calibrate(window=160,block=8,reps=29,n_pairs=6)
    assert set(result["controles"])=={"estacionario","mudanca_copula"}
