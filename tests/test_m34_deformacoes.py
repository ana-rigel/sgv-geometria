"""M34: as deformacoes respondem a transformacoes conhecidas; causalidade; mesma capacidade."""
import numpy as np
from experiments import m34_deformacoes as m


def _win(seed=0,shift=0.,scale=1.,rot=0.):
    rng=np.random.default_rng(seed);C=np.array([[1,.5,.2],[.5,1,.1],[.2,.1,1]])
    x=rng.multivariate_normal([0,0,0],C,size=m.WINDOW)
    nb=m.WINDOW-(int(.3*m.WINDOW)+(m.WINDOW-int(.3*m.WINDOW))//2)
    tail=x[-nb:]
    c,s=np.cos(np.radians(rot)),np.sin(np.radians(rot));R=np.array([[c,-s,0],[s,c,0],[0,0,1]])
    x[-nb:]=(tail@R.T)*scale+shift
    return x


def test_capacity_equal():
    assert len(m.G_COLS)==len(m.E_COLS)==10


def test_shift_and_expansion_detected():
    G0,_,E0=m.features(_win(1));Gs,_,Es=m.features(_win(1,shift=np.array([.8,0,0])));Ge,_,_=m.features(_win(1,scale=1.5))
    assert G0 is not None and Gs is not None and Ge is not None
    assert Gs['trans']>G0['trans']+.3 and Es['dmean']>E0['dmean']+.3
    assert Ge['dlogvol']>G0['dlogvol']+.3


def test_identical_halves_small_deformation():
    G0,_,_=m.features(_win(2));Gs,_,_=m.features(_win(2,scale=1.6,shift=np.array([.5,.5,0])))
    assert Gs['m11']>=0 and Gs['jacc']<G0['jacc']


def test_causal_window_only():
    rng=np.random.default_rng(3);x=rng.standard_normal((m.WINDOW+50,3))
    G1,_,E1=m.features(x[:m.WINDOW]);y=x.copy();y[m.WINDOW:]*=9
    G2,_,E2=m.features(y[:m.WINDOW])
    assert G1==G2 and E1==E2
