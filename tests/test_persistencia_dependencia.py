"""SGV: testes matematicos e controles do experimento local de dependencias."""
import numpy as np
import pytest

from experiments.persistencia_dependencia import (
    assess_window, bootstrap_means, segment_score, summarize, synthetic_one,
)


@pytest.mark.parametrize("kind",[
    "stationary", "temporal_mixture", "persistent_mixture",
    "independent_skew_marginals", "nonlinear_curve",
])
def test_formas_sinteticas_produzem_metricas_finitas(kind):
    x=synthetic_one(kind,1000,seed=83)
    res=assess_window(x)
    for name in ("janela_inteira","metade_a","metade_b"):
        assert res[name]["n_train"]>0
        assert res[name]["n_test"]>0
        assert 0<=res[name]["extrapolacao_marginal"]<=1
        assert np.isfinite(res[name]["gmm_vs_gauss"])
        assert np.isfinite(res[name]["gmm_vs_student"])
    assert np.isclose(res["media_local_gmm_vs_gauss"],
        (res["metade_a"]["gmm_vs_gauss"]+
         res["metade_b"]["gmm_vs_gauss"])/2)
    assert res["minimo_local_gmm_vs_gauss"]==min(
        res["metade_a"]["gmm_vs_gauss"],
        res["metade_b"]["gmm_vs_gauss"])


def test_causalidade_do_score_em_cada_metade():
    rng=np.random.default_rng(124)
    x=rng.normal(size=(1000,3))
    a=segment_score(x[:500])
    altered=x.copy()
    altered[500:]+=10
    b=segment_score(altered[:500])
    assert a==b


def test_sem_mutacao_do_array_original():
    rng=np.random.default_rng(125)
    x=rng.normal(size=(1000,3))
    original=x.copy()
    assess_window(x)
    np.testing.assert_array_equal(x,original)


def test_bootstrap_reproducivel_e_conserva_valores():
    values=np.arange(12)/40.
    a=bootstrap_means(values,seed=123,reps=300)
    b=bootstrap_means(values,seed=123,reps=300)
    assert a==b
    assert a["IC95_blocos_temporais"][0] <= a["IC95_blocos_temporais"][1]
    assert abs(a["media"]-values.mean())<1e-12


def test_resumo_nao_inventa_persistencia_com_dados_misturados():
    rng=np.random.default_rng(126)
    rows=[assess_window(rng.normal(size=(1000,3))) for _ in range(6)]
    s=summarize(rows)
    item=s["diagnosticos"]["gmm_vs_gauss"]
    both=np.mean([
        r["metade_a"]["gmm_vs_gauss"]>0 and r["metade_b"]["gmm_vs_gauss"]>0
        for r in rows
    ])
    assert s["n_janelas_sem_sobreposicao"]==6
    assert np.isclose(
        item["fracao_janelas_ambas_metades_positivas"],both)


def test_nao_aceita_janelas_impares_ou_curta_demais():
    rng=np.random.default_rng(127)
    with pytest.raises(ValueError):
        assess_window(rng.normal(size=(999,3)))
    with pytest.raises(ValueError):
        assess_window(rng.normal(size=(200,3)))


def test_boostrap_rejeita_inferencia_com_poucas_janelas():
    with pytest.raises(ValueError):
        bootstrap_means(np.arange(3.),seed=4)


def test_mistura_temporal_forte_gera_correlacoes_diferentes_por_metade():
    x=synthetic_one("temporal_mixture",1500,seed=128)
    a=np.corrcoef(x[:750,0],x[:750,1])[0,1]
    b=np.corrcoef(x[750:,0],x[750:,1])[0,1]
    assert a>.65 and b<-.65


def test_mistura_persistente_tem_correlacao_global_proxima_de_zero():
    x=synthetic_one("persistent_mixture",6000,seed=129)
    a=np.corrcoef(x[:3000,0],x[:3000,1])[0,1]
    b=np.corrcoef(x[3000:,0],x[3000:,1])[0,1]
    assert abs(a)<.15 and abs(b)<.15
