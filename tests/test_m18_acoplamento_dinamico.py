"""M18: DCC recovery, static limit, LM keeps real slow block, factorial aggregation."""
import numpy as np
import pytest
from experiments import m18_acoplamento_dinamico as m


def _toy(n=8000,seed=0):
    rng=np.random.default_rng(seed)
    s=np.repeat(rng.integers(0,2,size=n//200),200)[:n]
    x=rng.normal(size=(n,3));x[:,2]+=1.5*s;x[:,0]*=1+s
    return x


def test_design():
    assert m.NULLS==('MS','MSDCC','MSLM','MSDCCLM','BL','N3')
    assert m.ALPHA_CONTRAST==pytest.approx(.0125)
    assert m.n_shards(84,'1m')==42 and m.n_shards(18,'1h')==6


def test_dcc_recovers_dynamic_and_static():
    rng=np.random.default_rng(1)
    a,b,g=m.fit_dcc(m.dcc_innovations(rng,3000,.06,.9))
    assert .03<a<.1 and .8<b<.97 and g>20
    a0,b0,g0=m.fit_dcc(rng.standard_normal((3000,3)))
    assert g0<5


def test_dcc_innovations_unit_variance_and_static_limit():
    rng=np.random.default_rng(2)
    e=m.dcc_innovations(rng,20000,0.,0.)
    np.testing.assert_allclose(e.std(axis=0),1,atol=.03)
    assert abs(np.corrcoef(e.T)[0,1])<.03


def test_variants_sample_finite_windows():
    x=_toy()
    for dcc in (False,True):
        for lm in (False,True):
            f,d=m.two_scale_plus(x,'1m',3,dcc=dcc,lm=lm)
            y=f(np.random.default_rng(4),1500)
            assert y.shape==(1500,3) and np.isfinite(y).all()
            if dcc:assert 'dcc' in d


def test_lm_carries_real_slow_signal():
    x=_toy(8000,5)
    f,_=m.two_scale_plus(x,'1m',6,lm=True)
    y=f(np.random.default_rng(7),1500)
    sm=np.convolve(y[:,2],np.ones(60)/60,'valid')
    assert sm.std()>.4


def _fake(iv,n,alarm):
    rows=[]
    for k in range(n):
        models={nm:{s:{'valid':True,'p_rank':.025 if alarm(nm,s,k) else .5,'rank_position':1 if alarm(nm,s,k) else 20,
                        'alarm':alarm(nm,s,k)} for s in m.STATS} for nm in m.NULLS}
        diag={'MSDCC':{'dcc':{'a':.02,'b':.9,'nll_gain_vs_static':10.}}}
        rows.append({'interval':iv,'origin':k,'status':'valid','models':models,'fit_diagnostics':diag})
    return rows


def test_aggregate_factorial():
    rows=_fake('1m',84,lambda nm,s,k:(nm=='MS' and k<30) or (nm=='MSLM' and k<28) or (nm=='MSDCC' and k<5))
    a=m.aggregate(rows,{'1m':84})
    assert a['contrasts']['1m|D1_acoplamento_frcov']['significant']
    assert not a['contrasts']['1m|D2_memoria_longa_energy']['significant']
    with pytest.raises(ValueError,match='Missing'):m.aggregate(rows[1:],{'1m':84})
