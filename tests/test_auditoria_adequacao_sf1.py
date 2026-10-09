"""Protecao temporal e reproduzibilidade da auditoria do SF1."""
import numpy as np
import pytest
from experiments.auditoria_adequacao_sf1 import (
    diagnostics,aggregate_compare,evaluate,valid_segment,synthetic
)
from sgvgeo.flow import simulate_sf1,default_sf1


def test_metricas_de_series_finitas():
    rng=np.random.default_rng(5)
    x=rng.normal(size=(400,3))
    out=diagnostics(x)
    assert len(out)>=20
    assert np.isfinite(list(out.values())).all()


def test_rejeita_nan():
    x=np.ones((300,3))
    x[120,1]=np.nan
    with pytest.raises(ValueError):
        diagnostics(x)


def test_simulacoes_identicas_geram_envelope_identico():
    x=diagnostics(np.random.default_rng(10).normal(size=(400,3)))
    c=aggregate_compare(x,[x,x,x])
    assert all(abs(c[k]["obs_minus_sf1_median"])<1e-12 for k in c)
    assert not any(c[k]["observado_fora_q10_q90"] for k in c)


def test_gap_temporal_rejeitado():
    ts=np.arange(80,dtype=np.int64)*60_000
    assert valid_segment(ts,np.zeros((80,3)),60_000)
    ts[40:]+=60_000
    assert not valid_segment(ts,np.zeros((80,3)),60_000)


def test_rejeita_prefixo_incompleto():
    x=simulate_sf1(default_sf1(),3300,seed=24)
    with pytest.raises(ValueError):
        evaluate(x,1999,1000,60_000,42,n_sim=1)


def test_perturbacao_futura_nao_muda_ajuste_sintetico():
    out=synthetic()
    assert out["sf1_fit_garch_converged"]
    assert out["nao_vazamento_prefixo_e_simulacoes"]
    assert out["modificacao_futura_detectada"]
