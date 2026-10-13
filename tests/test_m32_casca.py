"""M32: elegibilidade sem futuro, treino so com rotulos maturados/validos, modelos."""
import numpy as np,pandas as pd
from experiments import m32_casca as m


def _f(n=7000,seed=4):return m.synthetic_klines(n=n,seed=seed)


def test_eligibility_does_not_depend_on_future():
    f=_f();d0,_=m.build(f);cut=int(d0.origin_ts.iloc[len(d0)//2])
    g=f.copy();late=g.timestamp>cut
    g.loc[late,['close','high','low']]*=1.5;g.loc[late,'volume']*=7
    d1,_=m.build(g)
    a=d0[d0.origin_ts<=cut].drop(columns=['rv_future_15']).reset_index(drop=True)
    b=d1[d1.origin_ts<=cut].drop(columns=['rv_future_15']).reset_index(drop=True)
    pd.testing.assert_frame_equal(a,b)


def test_last_origins_kept_without_target():
    f=_f();d,_=m.build(f)
    last=int(f.timestamp.iloc[-1])
    tail=d[d.origin_ts>last-m.H*m.MIN]
    assert len(tail)>=1 and tail.rv_future_15.isna().all()


def test_training_skips_missing_and_immature_labels():
    d,_=m.build(_f(n=20000))
    d=d.iloc[:260].reset_index(drop=True)
    e=d.copy();e.loc[[10,20,30],'rv_future_15']=np.nan
    v=m.rolling_forecasts(e,m.B1,train=200)
    assert np.isfinite(v[-1])
    k=len(e)-3;e2=e.copy();e2.loc[k:,'rv_future_15']*=40
    v2=m.rolling_forecasts(e2,m.B1,train=200)
    assert v[k]==v2[k]


def test_models():
    assert m.B1S[-1]=='saddle_frac' and set(m.B1)<set(m.B1S) and 'elast' not in m.B1
