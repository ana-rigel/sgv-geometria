"""M35 passo 1: propriedades basicas das variantes do instrumento."""
import numpy as np
from experiments import m35_instrumento as m


def test_whiten_fixes_first_two_moments():
    rng=np.random.default_rng(1);x=rng.standard_normal((500,3))@np.array([[2,.5,0],[0,1,.3],[0,0,.4]])+3
    w=m.whiten(x)
    assert np.allclose(w.mean(0),0,atol=1e-10) and np.allclose(np.cov(w,rowvar=False),np.eye(3),atol=1e-10)


def test_planted_keeps_moments_changes_shape():
    rng=np.random.default_rng(2);a=m.planted(0.,600,rng);b=m.planted(3.,600,rng)
    for x in (a,b):assert np.allclose(np.cov(x,rowvar=False),np.eye(3),atol=1e-10)
    # a separacao aparece na curtose ao longo da direcao plantada (bimodal -> curtose < 3)
    d=np.array([1,1,0])/np.sqrt(2);ka=np.mean((a@d)**4);kb=np.mean((b@d)**4)
    assert kb<ka-.5


def test_v4_zero_for_identical_halves_and_deterministic():
    rng=np.random.default_rng(3);a=m.planted(1.,525,rng)
    r1=m.measure(a,a.copy(),'V4',7);r2=m.measure(a,a.copy(),'V4',7)
    assert r1==r2
    # mesma amostra, sementes do ensacamento diferentes para A e B -> perto de zero, nao exatamente
    assert r1['V4']<.15


def test_bagged_field_is_deterministic_and_normalised_like_gmm():
    rng=np.random.default_rng(4);a=rng.standard_normal((525,3))
    f1=m.bagged_field(a,5);f2=m.bagged_field(a,5);g=m.gmm_field(a,5)
    assert np.array_equal(f1,f2)
    assert abs(f1.sum()*m.DX**3-g.sum()*m.DX**3)<.05


def test_planted_change_increases_v0_and_v4():
    rng=np.random.default_rng(5);base=m.planted(0.,525,rng)
    same=m.measure_all(base,m.planted(0.,525,rng),11,('V0','V4'))
    big=m.measure_all(base,m.planted(3.,525,rng),11,('V0','V4'))
    assert big['V0']>same['V0'] and big['V4']>same['V4']


def test_radial_map_gaussian_is_near_ball_and_shapes():
    rng=np.random.default_rng(10);x=m.whiten(rng.standard_normal((2100,3)))
    d,s,a=m.radial_map(m.bagged_field(x,1))
    assert d.shape==(26,) and s.shape==(13,) and a.shape==(13,)
    assert np.nanmax(np.abs(d))<.15


def test_radial_map_recovers_planted_lobe_direction():
    rng=np.random.default_rng(11)
    for ax in range(6):
        x,e=m.planted_lobe(2100,rng,ax);_,_,a=m.radial_map(m.bagged_field(x,ax))
        assert m.map_hit(a,e)


def test_measure_v4_map_matches_v4():
    rng=np.random.default_rng(12);a=m.planted(1.,525,rng);b=m.planted(2.,525,rng)
    v=m.measure(a,b,'V4',5);w=m.measure_v4_map(a,b,5)
    for k in v:assert v[k]==w[k]
    assert 'aB_i+' in w and 'sB_n+' in w and 'dA_z-' in w
