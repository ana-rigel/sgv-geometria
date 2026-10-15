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


def test_rank_normal_removes_marginal_shape_keeps_ranks():
    rng=np.random.default_rng(20);x=np.exp(rng.standard_normal((800,3)))
    u=m.rank_normal(x)
    from scipy.stats import skew,kurtosis,spearmanr
    assert np.all(np.abs(skew(u,axis=0))<1e-6) and np.all(np.abs(kurtosis(u,axis=0))<.2)
    for j in range(3):assert spearmanr(x[:,j],u[:,j])[0]>.9999


def test_v_cop_invariant_to_monotone_marginal_transform():
    rng=np.random.default_rng(21);x=m.synth_joint(1050,.8,rng,'cintura')
    y=np.column_stack([np.exp(x[:,0]),x[:,1]**3,np.sinh(2*x[:,2])])
    assert m.measure_cop(x,3)['V_cop']==m.measure_cop(y,3)['V_cop']


def test_v_cop_sees_waist_and_cone():
    rng=np.random.default_rng(22)
    base=m.measure_cop(m.synth_joint(2100,0.,rng,'cintura'),4)['V_cop']
    for kind in ('cintura','cone'):
        assert m.measure_cop(m.synth_joint(2100,1.,rng,kind),4)['V_cop']>base+.05


def test_dependence_scales_keys():
    rng=np.random.default_rng(23);o=m.dependence_scales(rng.standard_normal((600,3)))
    assert len(o)==3*4+6+3 and all(np.isfinite(v) for v in o.values())


def _regimes(n,rng,sequential):
    lab=np.r_[np.zeros(n//2,int),np.ones(n-n//2,int)]
    if not sequential:lab=rng.permutation(lab)
    x=rng.standard_normal((n,3));x[:,0]+=np.where(lab==1,2.5,-2.5);x[:,2]+=np.where(lab==1,1.5,-1.5)
    return x


def test_contiguity_separates_regimes_in_time_from_interleaved():
    rng=np.random.default_rng(30)
    seq=m.lobe_contiguity(_regimes(1050,rng,True),1)['contiguidade'];mix=m.lobe_contiguity(_regimes(1050,rng,False),1)['contiguidade']
    assert seq>.8 and abs(mix)<.15


def test_mixture_part_positive_only_for_sequential_regimes():
    rng=np.random.default_rng(31)
    seq=m.mixture_part(_regimes(1050,rng,True),2)['mistura'];mix=m.mixture_part(_regimes(1050,rng,False),2)['mistura']
    assert seq>.05 and seq>mix+.05
