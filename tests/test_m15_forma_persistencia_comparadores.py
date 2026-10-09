"""M15: paired nulls on one observed window, unchanged M11, cheap comparators."""
import numpy as np
import pytest
from experiments import m15_forma_persistencia_comparadores as m


def test_budget_and_design():
    assert m.REFS==19 and m.PREFIX==2000 and m.WINDOW==1500
    assert m.NULLS['HMM']==('HMM','GMM_IID','VAR','B15','B60','B150')
    for t in m.TRUTHS:
        assert m.SHARDS[t]*m.PER_SHARD[t]==m.TRIALS==500


def test_truth_reproducible_and_independent_across_trials():
    a=m.sample_truth('HMM',3);b=m.sample_truth('HMM',3);c=m.sample_truth('HMM',4)
    np.testing.assert_array_equal(a[1],b[1])
    assert not np.array_equal(a[1],c[1])
    assert a[0].shape==(2000,3) and a[1].shape==(1500,3)


def test_seeds_do_not_collide():
    seen=set()
    for t in (1,2):
        for trial in range(30):
            for parts in [(t,trial,1)]+[(t,trial,4,n,k) for n in range(1,7) for k in range(19)]:
                s=m.seed_int(*parts)
                assert s not in seen
                seen.add(s)


def test_fisher_rao_known_values():
    rng=np.random.default_rng(0)
    x=rng.normal(size=(4000,3))
    assert m.fisher_rao_cov(x,x)==pytest.approx(0,abs=1e-9)
    # scaling one covariance by s^2 in all 3 directions: d = sqrt(1/2*3*(log s^2)^2)
    d=m.fisher_rao_cov(x,2*x)
    assert d==pytest.approx(np.sqrt(.5*3*np.log(4)**2),rel=1e-9)
    # invariance under a common linear map (intrinsic geometry)
    A=np.array([[2,.3,0],[0,1,.5],[.1,0,3]])
    y=rng.normal(size=(4000,3))*[1,1.5,.7]
    assert m.fisher_rao_cov(x@A.T,y@A.T)==pytest.approx(m.fisher_rao_cov(x,y),rel=1e-8)


def test_energy_distance_properties():
    rng=np.random.default_rng(1)
    x=rng.normal(size=(300,3))
    assert m.energy_distance(x,x)==pytest.approx(0,abs=1e-12)
    far=m.energy_distance(x,x+3)
    near=m.energy_distance(x,x+.1)
    assert far>near>0


def test_gmm_iid_is_memoryless_with_right_shape():
    prefix,_=m.sample_truth('HMM',5)
    f=m.fit_null('GMM_IID',prefix,7)
    s=m.sample_null(f,np.random.default_rng(2),20000)
    assert s.shape==(20000,3) and np.isfinite(s).all()
    # IID: lag-1 autocorrelation of nu ~ 0
    z=s[:,2]-s[:,2].mean()
    assert abs(np.dot(z[1:],z[:-1])/np.dot(z,z))<.03
    # bimodal-ish: the mixture weights are both substantial
    assert min(f['weights'])>.2


def test_blocks_lengths_and_exact_rows():
    prefix,_=m.sample_truth('HMM',6)
    for name,L in m.BLOCKS.items():
        f=m.fit_null(name,prefix,0)
        out=m.sample_null(f,np.random.default_rng(3),m.WINDOW)
        assert out.shape==(m.WINDOW,3) and f['block_length']==L
        assert all(np.any(np.all(prefix==row,axis=1)) for row in out[:20])


def test_fit_uses_prefix_only():
    prefix,window=m.sample_truth('HMM',8)
    f1=m.fit_null('GMM_IID',prefix,11)
    f2=m.fit_null('GMM_IID',prefix.copy(),11)
    np.testing.assert_allclose(f1['model'].means_,f2['model'].means_)


def test_trial_paths_with_light_statistic():
    calls=[]
    def light(x,seed):
        calls.append(seed)
        a,b=x[:700],x[700:1400]
        return {'m11':float(np.var(a[:,2])-np.var(b[:,2]))**2,'m11_reason':None,
                'fr_cov':m.fisher_rao_cov(a,b),'energy':m.energy_distance(a[:200],b[:200])}
    r=m.run_trial('HMM',0,stats_fn=light)
    r2=m.run_trial('HMM',0,stats_fn=light)
    assert r==r2
    assert set(r['nulls'])==set(m.NULLS['HMM'])
    for n,v in r['nulls'].items():
        assert v['status']=='valid'
        for s in m.STATS:
            assert v[s]['valid'] and 1<=v[s]['rank_position']<=20
            assert v[s]['alarm']==(v[s]['rank_position']==1)
    assert len(calls)==2*(1+6*19)   # two identical runs, one observed + 6x19 refs each


def test_invalid_statistic_never_replaced():
    def broken(x,seed):
        return {'m11':None,'m11_reason':'fake','fr_cov':1.0,'energy':1.0}
    r=m.run_trial('VAR',1,stats_fn=broken)
    v=r['nulls']['VAR']
    assert v['m11']['valid'] is False
    assert v['fr_cov']['valid'] is True


def test_aggregate_fails_closed_and_mcnemar():
    with pytest.raises(ValueError,match='Missing'):
        m.aggregate([],requested=2)
    res=m.mcnemar_exact([True]*10+[False]*5,[False]*10+[False]*5)
    assert res['x_only']==10 and res['y_only']==0 and res['p_one_sided']<.001


def test_full_statistics_on_one_window():
    _,w=m.sample_truth('VAR',9)
    s=m.all_stats(w,10)
    assert s['m11'] is not None and s['m11']>=0
    assert s['fr_cov']>=0 and s['energy']>=0
