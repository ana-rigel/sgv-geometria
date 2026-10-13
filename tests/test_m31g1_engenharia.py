"""M31-G1: fidelidade as definicoes originais, causalidade, regra de lacunas e maturacao."""
import numpy as np
import pandas as pd
from scipy.stats import rankdata,norm
from experiments import m31g1_engenharia as m

P0=2*norm.cdf(.3)-1


def _original_shape(x):
    # copia literal de scripts/forma_movimento.py @ e1e86b1 (cop + shape)
    def cop(x):return norm.ppf(np.column_stack([rankdata(x[:,j])/(len(x)+1) for j in range(3)]))
    u=cop(x);z,i,v=u.T;hv=v>=np.quantile(v,.6);s=z[hv]+i[hv];s=(s-s.mean())/s.std()
    lo=v<=np.quantile(v,1/3);hi=v>=np.quantile(v,2/3)
    return np.mean(np.abs(s)<.3)/P0, z[hi].std()/z[lo].std()


def test_shape_identical_to_original():
    rng=np.random.default_rng(3)
    for _ in range(5):
        x=rng.standard_t(4,size=(360,3))
        cint0,cone0=_original_shape(x)
        cone1,cint1=m.shape_original(x[:,0],x[:,1],x[:,2])
        assert abs(cone0-cone1)<1e-12 and abs(cint0-cint1)<1e-12


def _frame(n=6000,seed=1):
    return m.synthetic_klines(n=n,seed=seed)


def test_features_do_not_see_the_future():
    f=_frame();d0,_=m.build(f)
    cut=int(d0.origin_ts.iloc[len(d0)//2])
    g=f.copy();late=g.timestamp>cut
    g.loc[late,['close','high','low']]*=1.37;g.loc[late,'volume']*=5;g.loc[late,'taker_buy']*=.2
    d1,_=m.build(g)
    cols=[c for c in d0.columns if c not in ('rv_future_15',)]
    a=d0[d0.origin_ts<=cut-m.H*m.MIN][cols].reset_index(drop=True);b=d1[d1.origin_ts<=cut-m.H*m.MIN][cols].reset_index(drop=True)
    pd.testing.assert_frame_equal(a,b)


def test_gap_rule_no_bridging():
    f=_frame(n=9000)
    g=f.drop(index=range(4500,4520)).reset_index(drop=True)   # lacuna de 20 min
    d,info=m.build(g)
    assert info['n_segmentos']==2
    gap_end=int(g.timestamp.iloc[4500]);gap_start=int(g.timestamp.iloc[4499])
    o=d.origin_ts.to_numpy()
    # nenhuma origem cujo alvo atravessa a lacuna, nem origem antes do reaquecimento completo apos a lacuna
    assert not np.any((o<=gap_start)&(o+m.H*m.MIN>gap_start))
    assert not np.any((o>=gap_end)&(o<gap_end+m.WARM*m.MIN))
    # o segundo segmento e calculado como se o primeiro nao existisse
    d2,_=m.build(g.iloc[4500:].reset_index(drop=True))
    pd.testing.assert_frame_equal(d[d.origin_ts>=gap_end].reset_index(drop=True),d2.reset_index(drop=True))


def test_quarter_hour_dummies():
    d,_=m.build(_frame())
    mins=(d.origin_ts//m.MIN)%60
    for k in (1,2,3):assert np.all(d[f'q15_{k}'].to_numpy()==(mins//15==k))
    assert set(mins.unique())<={0,15,30,45}


def test_forecasts_use_only_matured_labels():
    d,_=m.build(_frame(n=20000))
    d=d.iloc[:230].reset_index(drop=True)
    v=m.rolling_forecasts(d,m.B0,train=200)
    k=len(d)-5;e=d.copy();e.loc[k-0:,'rv_future_15']*=50   # rotulos que ainda nao maturaram em k
    v2=m.rolling_forecasts(e,m.B0,train=200)
    assert np.isfinite(v[k]) and v[k]==v2[k]


def test_shell_saddle_deterministic_and_in_range():
    rng=np.random.default_rng(5);x=rng.standard_normal((360,3))
    a=m.shell_saddle(x[:,0],x[:,1],x[:,2]);b=m.shell_saddle(x[:,0],x[:,1],x[:,2])
    assert a is not None and a==b and 0<=a<=1


def test_shell_saddle_sees_a_waist():
    rng=np.random.default_rng(6)
    g=rng.standard_normal((360,3))
    # cintura moderada (lobulos ainda ligados); com separacao total a HDR50 vira duas pecas convexas
    l=np.r_[rng.normal(-.9,.7,(180,2)),rng.normal(.9,.7,(180,2))];lob=np.column_stack([l,rng.standard_normal(360)])
    sg=m.shell_saddle(*g.T);sl=m.shell_saddle(*lob.T)
    assert sl is not None and sg is not None and sl>sg+.05


def test_build_with_shell_adds_column():
    d,_=m.build(m.synthetic_klines(n=4200,seed=2),with_shell=True)
    assert 'saddle_frac' in d and d.saddle_frac.notna().mean()>.9
