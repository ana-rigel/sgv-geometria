"""M17: prefix-only fitting, two-scale Markov vs semi-Markov, clock, strict aggregation."""
import numpy as np
import pytest
from experiments import m17_tipo_de_memoria as m


def _toy(n=4000,seed=0):
    rng=np.random.default_rng(seed)
    s=np.repeat(rng.integers(0,2,size=n//200),200)[:n]
    x=rng.normal(size=(n,3));x[:,2]+=1.5*s;x[:,0]*=1+s
    return x


def test_design():
    assert m.REFS==39 and m.NULLS==('H2','H4','MS','MSSM','MSR','MSSMR','N3')
    assert m.n_shards(84,'1m')==42 and m.n_shards(18,'1h')==6
    assert m.ALPHA_CONTRAST==pytest.approx(.01)


def test_clock_bins_and_profile():
    ts=np.arange(0,200*3600000,3600000,dtype=np.int64)
    assert set(m.clock_bin(ts,'1m'))==set(range(24))
    assert m.clock_bin(ts,'1h').max()==167
    nu=(m.clock_bin(ts,'1h')==5).astype(float)
    prof=m.clock_profile(nu,ts,'1h')
    assert prof[5]==1 and prof[6]==0
    with pytest.raises(ValueError):m.clock_profile(nu[:10],ts[:10],'1h')


def test_two_scale_recovers_slow_regimes_and_samples():
    x=_toy(8000)
    markov,semi,d=m.two_scale(x,'1m',1)
    assert all(v>.98 for v in d['slow_self_transition'])
    for f in (markov,semi):
        y=f(np.random.default_rng(2),1500)
        assert y.shape==(1500,3) and np.isfinite(y).all()
    # slow structure survives: nu mean differs between first/second of long stretches
    y=markov(np.random.default_rng(3),20000)
    sm=np.convolve(y[:,2],np.ones(60)/60,'valid')
    assert sm.std()>.4


def test_semi_markov_uses_empirical_durations():
    x=_toy(6000,4)
    _,semi,d=m.two_scale(x,'1m',5)
    for v in d['slow_durations'].values():
        assert v['n_runs']>=3 and v['mean_bars']>50


def test_runs():
    lab,ln=m.runs(np.array([0,0,1,1,1,0]))
    assert list(lab)==[0,1,0] and list(ln)==[2,3,1]


def _fake(iv,n,alarm):
    rows=[]
    for k in range(n):
        models={nm:{s:{'valid':True,'p_rank':.025 if alarm(nm,k) else .5,'rank_position':1 if alarm(nm,k) else 20,
                        'alarm':alarm(nm,k)} for s in m.STATS} for nm in m.NULLS}
        diag={'H2':{'converged':True,'time_scales_bars':[3.0]},'H4':{'converged':True,'time_scales_bars':[5.0,2.0]},
              'MS':{'slow_durations':{'0':{'mean_bars':300,'cv':1.0,'ks_vs_geometric':.2}}}}
        rows.append({'interval':iv,'origin':k,'status':'valid','models':models,'fit_diagnostics':diag})
    return rows


def test_aggregate_contrasts_and_gap():
    rows=_fake('1m',84,lambda nm,k:(nm=='H4' and k<40) or (nm=='MS' and k<5))
    a=m.aggregate(rows,{'1m':84})
    assert a['contrasts']['1m|C1_escala_lenta']['significant']
    assert not a['contrasts']['1m|C2_envelhecimento']['significant']
    assert a['closes_gap']['1m|MSSM'] and not a['closes_gap']['1m|H4']
    with pytest.raises(ValueError,match='Missing'):m.aggregate(rows[:-1],{'1m':84})
