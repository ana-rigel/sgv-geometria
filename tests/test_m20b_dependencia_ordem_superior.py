"""Analytical controls for M20b; all tests use synthetic draws only."""
import numpy as np
from experiments import m20b_dependencia_ordem_superior as m


def test_orthogonality_and_kernel_positive():
    t=m.theoretical_checks()
    assert t["pass"]
    assert t["transition_lower_bound"] > 0.0
    assert 0.0 < t["integrals"]["E_h2"] < 1.0
    for k in ("E_h","E_xh","E_x2h","E_absh"):
        assert abs(t["integrals"][k]) < 1e-10


def test_kernel_conditional_density_normalizes():
    from numpy.polynomial.hermite import hermgauss
    x,w=hermgauss(70)
    y=x*np.sqrt(2)
    w=w/np.sqrt(np.pi)
    for current in (-3,-.5,0,.5,3):
        mass=np.dot(w,1+m.ETA*m.h(current)*m.h(y))
        assert abs(mass-1)<1e-9


def test_no_linear_or_quadratic_autocovariance_theory():
    from numpy.polynomial.hermite import hermgauss
    x,w=hermgauss(90)
    x=x*np.sqrt(2)
    w=w/np.sqrt(np.pi)
    funcs=[x,x*x,np.abs(x)]
    for f in funcs:
        assert abs(np.dot(w,f*m.h(x))) < 1e-10


def test_hidden_generator_has_nonlinear_memory_not_linear():
    rng=np.random.default_rng(1001)
    x=m.gen_hidden(19000,m.ETA,rng)
    assert abs(m.cov1(x[:-1],x[1:])) < .04
    assert m.cov1(m.h(x[:-1]),m.h(x[1:])) > .015
    assert abs(np.mean(x)) < .05
    assert abs(np.var(x)-1) < .06


def test_opposite_h_correlations():
    for eta,seed in ((m.ETA,101),(-m.ETA,102)):
        x=m.gen_hidden(15000,eta,np.random.default_rng(seed))
        c=m.cov1(m.h(x[:-1]),m.h(x[1:]))
        assert c*eta > 0.01


def test_volatility_memory_without_signed_autocorrelation():
    x=m.generate(12000,"volatility_memory",np.random.default_rng(103))
    u=x[:,0]
    assert abs(m.cov1(u[:-1],u[1:])) < .06
    assert m.cov1(np.abs(u[:-1]),np.abs(u[1:])) > .15


def test_score_invariance_under_exchange_of_pair_order():
    rng=np.random.default_rng(5)
    x=rng.normal(size=(800,3))
    y=x[::-1].copy()
    # Pair Fourier cross-cov Frobenius norm invariant to time reversal.
    assert abs(m.scores(x)["fourier_hsic"]-m.scores(y)["fourier_hsic"])<1e-12


def test_reproducible_pilot(tmp_path,monkeypatch):
    monkeypatch.setattr(m,"ROOT",tmp_path)
    a=m.experiment("pilot")
    b=m.experiment("pilot")
    assert a==b
    assert a["n_per_series"]==450
    assert (tmp_path/"reports/m20b/piloto.json").exists()
