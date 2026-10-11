import numpy as np
from experiments import m27_nao_estacionariedade as m


def _series(n=6000,seed=0,switch=False):
    """AR(1) in nu with persistence that changes across segments when switch=True."""
    rng=np.random.default_rng(seed);x=rng.normal(size=(n,3))
    seg=np.repeat(rng.integers(0,2,size=n//300+1),300)[:n]
    for t in range(1,n):
        phi=(.1 if (t*m.K)//n%2==0 else .8) if switch else .45
        x[t,2]=phi*x[t-1,2]+np.sqrt(1-phi**2)*x[t,2]
    x[:,2]+=1.2*seg
    return x


def test_local_sampler_shape_and_finite():
    f,d=m.fit_local(_series(),3)
    y=f(np.random.default_rng(2),1500)
    assert y.shape==(1500,3) and np.isfinite(y).all()
    assert len(d['segments'])==m.K


def test_dispersion_detects_planted_switch():
    _,ds=m.fit_local(_series(switch=True),3)
    _,dc=m.fit_local(_series(switch=False),3)
    assert m.dispersion(ds)['ar1_nu']>2*m.dispersion(dc)['ar1_nu']


def test_aggregate_reading_on_toy_rows():
    rng=np.random.default_rng(0);rows=[]
    for k in range(20):
        mods={}
        for name,rate in (('HXLOC',.0),('HXNOISE',.6),('HARLMFX',.6),('BL',.0)):
            mods[name]={s:{'p_rank':.5,'alarm':bool(rng.random()<rate)} for s in m.STATS}
        disp={kk:1. for kk in m.DISP_KEYS}
        rows.append({'origin':k,'status':'valid','models':mods,
                     'fit_diagnostics':{'dispersion':{'real':disp,'synthetic':{kk:.5 for kk in m.DISP_KEYS}}}})
    a=m.aggregate(rows,20)
    assert a['reading'].startswith('NAO ESTACIONARIEDADE APOIADA')
    assert a['dispersion']['ar1_nu']['frac_real_gt_synth']==1.
