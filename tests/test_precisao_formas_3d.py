"""Geometria 3D de regioes HDR: propriedades, causalidade e bootstrap."""
import numpy as np
import pytest

from experiments.precisao_formas_3d import (
    gaussianize_three, split_historical, build_grid,
    masks_from_density, topology, jaccard, assess_window,
    bootstrap_shape_noise, synthetic,
)

def test_map_de_quantis_so_usa_ancora_e_rejeita_nao_finitos():
    rng=np.random.default_rng(10)
    a=rng.normal(size=(300,3))
    x=rng.normal(size=(180,3))
    b=x.copy()
    b[100:]+=30
    z=gaussianize_three(a,x)
    changed=gaussianize_three(a,b)
    np.testing.assert_array_equal(z[:100],changed[:100])
    with pytest.raises(ValueError):
        gaussianize_three(a,np.full((100,3),np.nan))


def test_split_tem_ancora_temporal_separada():
    rng=np.random.default_rng(11)
    x=rng.normal(size=(1500,3))
    a,b=split_historical(x)
    assert a.shape==b.shape==(525,3)
    altered=x.copy()
    altered[1300:]+=100
    aa,bb=split_historical(altered)
    np.testing.assert_array_equal(a,aa)
    np.testing.assert_array_equal(b[:325],bb[:325])


def test_hdrs_aninhadas_e_massa_monotona():
    g=build_grid(21)
    density=np.exp(-.5*np.sum(g*g,axis=1))/(2*np.pi)**1.5
    mask,cov=masks_from_density(density,21)
    assert 0<cov<=1.1
    assert np.all(~mask[.25]|mask[.50])
    assert np.all(~mask[.50]|mask[.75])
    assert topology(mask[.50])==1


def test_topologia_grade_reconhece_ilhas():
    a=np.zeros((21,21,21),bool)
    a[2:5,3:5,2:5]=True
    a[14:17,14:17,14:17]=True
    assert topology(a)==2
    assert jaccard(a,a)==1
    assert jaccard(a,~a)==0


def test_tres_dimensoes_reagem_atividade_sem_alterar_preco_fluxo():
    rng=np.random.default_rng(12)
    x=rng.normal(size=(1500,3))
    y=x.copy()
    y[1100:,2]+=2
    a,b=split_historical(x)
    aa,bb=split_historical(y)
    np.testing.assert_array_equal(a,aa)
    assert not np.array_equal(b,bb)


def test_bootstrap_reprodutivel_com_controles():
    x=synthetic("stationary",1500,seed=13)
    a,b=split_historical(x)
    p=bootstrap_shape_noise(a,b,block=10,reps=5,seed=11)
    q=bootstrap_shape_noise(a,b,block=10,reps=5,seed=11)
    assert p==q
    for key in ("25","50","75"):
        assert 0<=p[key]["mudanca_observada_1_menos_jaccard"]<=1
        assert 0<p[key]["p_exploratorio_pool"]<=1


@pytest.mark.parametrize("kind",[
    "stationary","temporal_mixture","persistent_mixture",
    "nonlinear_curve","three_component","sf1",
])
def test_formas_controles_finitos(kind):
    x=synthetic(kind,1500,seed=55)
    assert x.shape==(1500,3)
    r=assess_window(x,seed=56,check_resolution=True)
    for model in ("gaussian","mixture"):
        for mass in ("25","50","75"):
            assert 0<=r[f"{model}_jaccard_hdr_{mass}"]<=1
            assert r[f"{model}_componentes_a_{mass}"]>=1
        assert r[f"{model}_massa_grade_a"]>0
        assert isinstance(r[f"{model}_topologia_coincide_resolution_50"],bool)


def test_nao_confundir_gmm_com_duas_ilhas():
    x=synthetic("stationary",1500,seed=14)
    r=assess_window(x)
    assert r["mixture_componentes_a_50"]==1
    assert r["mixture_componentes_b_50"]==1
