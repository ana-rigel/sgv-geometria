"""Controle de geometria de dependência sem confundir forma marginal."""
from pathlib import Path
import importlib.util
import numpy as np
import pytest

P=Path(__file__).resolve().parents[1]/"experiments"/"teste_forma_dependencia.py"
spec=importlib.util.spec_from_file_location("forma_dependencia",P)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_transformacao_sem_vazamento_entre_treino_e_teste():
    rng=np.random.default_rng(100)
    a=np.column_stack([rng.normal(size=900),
                       rng.standard_t(3,size=900),
                       rng.lognormal(size=900)])
    b=rng.normal(size=(300,3))
    z1,z2,f=mod.empirical_marginal_gaussianize(a,b)
    bb=b.copy()
    bb[200:]+=1e5
    new_a,new_b,new_f=mod.empirical_marginal_gaussianize(a,bb)
    np.testing.assert_array_equal(z1,new_a)
    np.testing.assert_array_equal(z2[:200],new_b[:200])
    assert f>=0 and new_f>=0


def test_normalizacao_gaussiana_de_marginal_assimetrica():
    rng=np.random.default_rng(101)
    x=np.exp(rng.normal(size=4000))
    a=x[:3000,None]
    b=x[3000:,None]
    z1,z2,f=mod.empirical_marginal_gaussianize(a,b)
    assert abs(float(z1.mean()))<0.02
    assert 0.9<float(z1.std())<1.1
    assert np.isfinite(z2).all()


def test_transformada_preserva_dependencia_monotonica():
    rng=np.random.default_rng(102)
    x=rng.normal(size=1800)
    y=np.exp(.8*x+.25*rng.normal(size=len(x)))
    z=np.column_stack([x,y,rng.normal(size=len(x))])
    transformed,_,_=mod.empirical_marginal_gaussianize(z[:1200],z[1200:])
    assert np.corrcoef(transformed[:,0],transformed[:,1])[0,1]>.8


def test_numeros_finitos_para_dependencia_curvada():
    x=mod.shape.synthetic_data("curved",1800,321)
    r=mod.fit_one_window(x)
    assert all(np.isfinite(v) for v in r["logscore"].values())
    assert r["kde" if False else "logscore"]["kde"] > r["logscore"]["gauss"]+.05


def test_mistura_tem_alternativa_identificavel():
    x=mod.shape.synthetic_data("mixture",2400,333)
    r=mod.fit_one_window(x)
    assert r["logscore"]["mixture2"]>r["logscore"]["gauss"]+.05
