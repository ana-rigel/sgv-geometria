import numpy as np
from scipy import stats

from regua import rb01 as R


def test_volume_verdadeiro_gaussiana_analitico():
    d = R.MVN(np.zeros(3), R.COV0)
    t = R.truth_stats(d, ("teste", "gauss"))
    for a in R.ALPHAS:
        r2 = stats.chi2.ppf(a, 3)
        v = 4 / 3 * np.pi * r2 ** 1.5 * np.sqrt(np.linalg.det(R.COV0))
        assert abs(t[f"{int(a*100)}"]["logV"] - np.log(v)) < 0.02


def test_affine_bate_com_normal_transformada():
    M = np.array([[1.2, 0.1, 0], [0, 0.8, 0.2], [0, 0, 1.5]])
    c, t = np.array([0.3, -0.2, 0.1]), np.array([0.5, 0, -0.4])
    d = R.Affine(R.MVN(np.zeros(3), R.COV0), M, c, t)
    mean = c + M @ (np.zeros(3) - c) + t
    ref = stats.multivariate_normal(mean, M @ R.COV0 @ M.T)
    x = np.random.default_rng(1).normal(size=(50, 3))
    assert np.allclose(d.logpdf(x), ref.logpdf(x), atol=1e-9)


def test_amostra_e_densidade_coerentes_t():
    d = R.MVT(np.zeros(3), R.COV0, 3.0)
    x = d.sample(200_000, np.random.default_rng(2))
    # massa verdadeira de uma região definida pela própria densidade = fração amostral
    lp = d.logpdf(x)
    tau = np.quantile(lp, 0.05)
    y = d.sample(100_000, np.random.default_rng(3))
    assert abs(np.mean(d.logpdf(y) >= tau) - 0.95) < 0.003


def test_hyndman_gmm_em_gaussiana_acerta_massa():
    d = R.MVN(np.zeros(3), R.COV0)
    x = d.sample(1500, np.random.default_rng(4))
    ev = d.sample(20_000, np.random.default_rng(5))
    out = R.measure_window("B", x, d, ev, np.random.default_rng(6))
    for a in R.ALPHAS:
        s = out[f"{int(a*100)}"]
        assert abs(s["mass_int"] - a) < 0.01
        assert abs(s["mass_true"] - a) < 0.03


def test_tmix_reconhece_cauda_pesada():
    d = R.MVT(np.zeros(3), R.COV0, 3.0)
    x = d.sample(1500, np.random.default_rng(7))
    m = R.TMixModel(x, 2)
    assert m.nu <= 4.0


def test_vendor_invalida_quando_grade_curta():
    # nuvem larga demais para a grade de ±3,5 do HDR50: o candidato A precisa recusar
    x = np.random.default_rng(8).normal(scale=2.5, size=(1500, 3))
    m = R.GMMModel(x, 2)
    try:
        R.tau_grid_vendor(m, 0.50)
        assert False, "deveria ser inválida"
    except R.Invalid as e:
        assert "cobertura" in str(e) or "borda" in str(e)
