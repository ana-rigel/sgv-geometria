"""Instrumento de observação — casos de resposta conhecida, sem dados confirmatórios."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

path = Path(__file__).resolve().parents[1] / "experiments" / "fotografia_informacional.py"
spec = importlib.util.spec_from_file_location("sgv_foto", path)
foto = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foto)


def test_fisher_translation_matches_inverse_covariance():
    rng = np.random.default_rng(123)
    X = rng.normal(size=(200, 3)) @ np.array([[1., .3, 0.], [0., 2., .1], [.1, 0., .8]])
    s = foto.gaussian_snapshot(X)
    np.testing.assert_allclose(s["cov"] @ s["fisher_location"], np.eye(3), atol=1e-10)
    assert np.min(np.linalg.eigvalsh(s["fisher_location"])) > 0


def test_distance_zero_and_affine_invariant():
    rng = np.random.default_rng(7)
    X = rng.normal(size=(600, 3))
    Y = rng.normal(loc=[.3, 0., -.1], size=(600, 3))
    a, b = foto.gaussian_snapshot(X), foto.gaussian_snapshot(Y)
    assert abs(foto.bhattacharyya(a, a)) < 1e-12
    M = np.array([[2.2, .3, .2], [.1, 1.4, -.1], [.2, .1, .75]])
    d0 = foto.bhattacharyya(a, b)
    d1 = foto.bhattacharyya(foto.gaussian_snapshot(X@M+4),
                            foto.gaussian_snapshot(Y@M+4))
    assert abs(d0-d1) < 1e-10


def test_fotografias_sao_prefixo_causais_e_tem_asof_fechamento():
    rng = np.random.default_rng(25)
    X = rng.normal(size=(720, 3))
    ts = 1_760_000_000_000 + 60_000 * np.arange(720)
    first = foto.direct_snapshots(X[:540], ts[:540], window=120, stride=20, bar_ms=60_000)
    longer = foto.direct_snapshots(X, ts, window=120, stride=20, bar_ms=60_000)
    assert first == longer[:len(first)]
    assert first[0]["asof_ms"] == int(ts[119]+60_000)
    assert all(x["asof_ms"] > ts[x["t"]] for x in first)


def test_lacuna_ou_nao_finito_invalidam_retrato():
    rng = np.random.default_rng(27)
    X = rng.normal(size=(240, 3))
    ts = 1_760_000_000_000 + 60_000 * np.arange(240)
    ts[120:] += 60_000
    rows = foto.direct_snapshots(X, ts, window=60, stride=10, bar_ms=60_000)
    # A primeira janela totalmente POSTERIOR ao gap termina em t=179.\n    assert all(not (x["t"] >= 120 and x["t"] < 179) for x in rows)
    X[215] = np.nan
    rows2 = foto.direct_snapshots(X, ts, window=60, stride=10, bar_ms=60_000)
    assert len(rows2) < len(rows)


def test_flips_do_fluxo_sao_fotografados_sem_mudar_marginais():
    d = foto.synthetic_calibration()
    assert d["rho_preco_fluxo_antes"] > .6
    assert d["rho_preco_fluxo_depois"] < -.6
    assert d["bhattacharyya_regime"] > .2
    assert d["erro_invariancia_transformacao_afim"] < 1e-10


def test_dependencia_nao_linear_e_ponto_cego_do_gaussiano():
    d = foto.synthetic_calibration()
    assert abs(d["ponto_cego_correlacao_linear"]) < .1
    assert d["ponto_cego_correlacao_quadratica"] > .98


def test_covariancia_degenerada_nao_e_retrato_valido():
    x = np.ones((120, 3))
    with pytest.raises(ValueError, match="degenerada"):
        foto.gaussian_snapshot(x)


def test_variacao_pura_do_volume_tem_lugar_na_geometria():
    rng = np.random.default_rng(91)
    X = rng.normal(size=(250, 3))
    Y = X.copy()
    Y[:, 2] = 3*Y[:, 2] + 1
    a, b = foto.gaussian_snapshot(X), foto.gaussian_snapshot(Y)
    assert foto.bhattacharyya(a, b) > 0
    # Em relação a uma base física fixa, escala/centro da atividade mudaram.
