"""Testes observacionais da forma: respostas conhecidas, causalidade e limites."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest
from scipy.special import gammaln
from scipy.stats import multivariate_t

PATH=Path(__file__).resolve().parents[1]/"experiments"/"teste_forma_distribuicoes.py"
spec=importlib.util.spec_from_file_location("forma_sgv",PATH)
shape=importlib.util.module_from_spec(spec)
spec.loader.exec_module(shape)


def test_student_logpdf_normalization_against_scipy():
    rng=np.random.default_rng(20)
    x=rng.normal(size=(20,3))
    mu=np.array([0.4,-0.3,0.1])
    sc=np.array([[2.0,0.2,0.1],[0.2,0.7,0.0],[0.1,0.0,1.4]])
    calc=shape.shape_logpdf(x,mu,sc,4.0)
    ref=multivariate_t.logpdf(x,loc=mu,shape=sc,df=4.0)
    np.testing.assert_allclose(calc,ref,rtol=1e-12,atol=1e-12)


@pytest.mark.parametrize("kind",["gauss","student_t4","mixture","curved"])
def test_all_fits_are_finite_for_known_shapes(kind):
    x=shape.synthetic_data(kind,1100,123)
    stats=shape.fit_evaluate_window(x)
    assert stats["n_test"]==330 and stats["n_train"]==770
    assert set(stats["logscore"])==set(shape.MODELS)
    assert all(np.isfinite(v) for v in stats["logscore"].values())
    assert stats["peso_menor_componente"]>=0
    assert stats["df_student"] in shape.DF_CANDIDATES


def test_causality_and_nonoverlap_of_historical_windows():
    rng=np.random.default_rng(30)
    X=rng.normal(size=(2000,3))
    ts=1_770_000_000_000+60_000*np.arange(len(X))
    before=list(shape.windows(X[:1400],ts[:1400],window=350,step=60_000))
    after=list(shape.windows(X,ts,window=350,step=60_000))
    assert len(before)==4
    for old,new in zip(before,after):
        assert old[0]==new[0] and old[1]==new[1]
        np.testing.assert_array_equal(old[2],new[2])
    assert all(after[i][0]-after[i-1][0]==350 for i in range(1,len(after)))


def test_gap_invalidates_full_window():
    x=np.random.default_rng(31).normal(size=(1200,3))
    t=60_000*np.arange(len(x),dtype="int64")
    t[500:]+=60_000
    out=list(shape.windows(x,t,window=300,step=60_000))
    assert [v[0] for v in out]==[300,900,1200]


def test_bootstrap_is_deterministic_and_only_scores_shape():
    rng=np.random.default_rng(15)
    rows=[]
    for j in range(10):
        x=rng.normal(size=(700,3))
        scores=shape.fit_evaluate_window(x)
        rows.append({"asof_ms":700*j*60000,"end":700*(j+1),**scores})
    a=shape.summarize(rows)
    b=shape.summarize(rows)
    assert a==b
    assert a["n_janelas_sem_sobreposicao"]==10


def test_known_mixture_prefers_non_single_gaussian():
    x=shape.synthetic_data("mixture",2800,64)
    scores=shape.fit_evaluate_window(x)["logscore"]
    assert scores["mixture2"]>scores["gauss"]+.08


def test_known_t_distribution_beats_gaussian_density():
    x=shape.synthetic_data("student_t4",2800,65)
    scores=shape.fit_evaluate_window(x)["logscore"]
    assert scores["student"]>scores["gauss"]+.04
