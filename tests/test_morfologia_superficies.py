"""SGV: limites e invariantes de superficies de densidade observacionais."""
import numpy as np
import pytest
from experiments.morfologia_superficies import (
    gaussianize_prefix, split_causal, grid, hdr_mask, components,
    overlap, morphology, synthetic
)


def test_sem_vazamento_no_mapa_de_quantis():
    rng=np.random.default_rng(30)
    anchor=rng.normal(size=(450,2))
    x=rng.normal(size=(500,2))
    before=gaussianize_prefix(anchor,x)
    other=x.copy()
    other[250:]+=100
    after=gaussianize_prefix(anchor,other)
    np.testing.assert_array_equal(before[:250],after[:250])


def test_duas_metades_causais_e_ancora_previa():
    rng=np.random.default_rng(32)
    x=rng.normal(size=(1500,3))
    a,b=split_causal(x)
    assert a.shape==(525,2) and b.shape==(525,2)
    y=x.copy()
    y[-100:]+=50
    a2,b2=split_causal(y)
    np.testing.assert_array_equal(a,a2)
    np.testing.assert_array_equal(b[:-100],b2[:-100])


def test_mascara_hdr_com_meia_massa_grid():
    g=grid()
    p=np.exp(-np.sum(g*g,axis=1)/2)
    mask=hdr_mask(p)
    assert mask.shape==(61,61)
    assert 0<mask.sum()<mask.size
    assert components(mask)==1


def test_topologia_conectividade_nao_assume_gmm_componentes():
    grid=np.zeros((61,61),dtype=bool)
    grid[5:9,5:9]=True
    grid[32:38,40:44]=True
    assert components(grid)==2
    assert overlap(grid,grid)==1
    assert overlap(grid,~grid)==0


@pytest.mark.parametrize("kind",[
    "stationary","temporal_mixture","persistent_mixture","nonlinear_curve","sf1"
])
def test_calibracao_de_casos_conhecidos(kind):
    x=synthetic(kind,1500,seed=17)
    assert x.shape==(1500,3)
    result=morphology(x)
    assert 0<=result["jaccard_hdr_gmm_metades"]<=1
    assert 0<=result["jaccard_hdr_gauss_metades"]<=1
    assert result["hdr_gauss_componentes_a"]==1
    assert result["hdr_gauss_componentes_b"]==1


def test_variaveis_nao_finitas_rejeitadas():
    x=np.ones((1500,3))
    x[100,0]=np.nan
    with pytest.raises(ValueError,match="nao finitos"):
        morphology(x)


def test_tamanho_insuficiente_rejeitado():
    with pytest.raises(ValueError):
        morphology(np.zeros((100,3)))
