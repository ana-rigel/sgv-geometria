import numpy as np,pandas as pd
from experiments import m33_t3 as m
from experiments import m31g1_engenharia as g
from sgvgeo.flow import flow_coordinates


def test_models_are_original_t3():
    assert m.B1PLUS==g.B0+g.ELAST+g.SHAPE and m.B2==m.B1PLUS+g.SHELL


def test_elasticity_matches_original_and_is_causal():
    f=m.synthetic_klines(n=6000,seed=9);d,_=m.build(f)
    co=flow_coordinates(f);z=co['z'].to_numpy(float);nu=co['nu'].to_numpy(float)
    ts=f.timestamp.to_numpy(np.int64);row=d.iloc[len(d)//2];i=int(np.flatnonzero(ts==row.origin_ts)[0])
    assert abs(row.elast-g.elasticity(z[i-g.W+1:i+1],nu[i-g.W+1:i+1]))<1e-12
    cut=int(row.origin_ts);h=f.copy();late=h.timestamp>cut;h.loc[late,['close','high','low']]*=1.4;h.loc[late,'volume']*=6
    d2,_=m.build(h)
    a=d[d.origin_ts<=cut].drop(columns=['rv_future_15']).reset_index(drop=True)
    b=d2[d2.origin_ts<=cut].drop(columns=['rv_future_15']).reset_index(drop=True)
    pd.testing.assert_frame_equal(a,b)
