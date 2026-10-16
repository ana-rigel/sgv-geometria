"""SGV D01: preflight without synthetic heldout and without August/September."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from pipeline import sgv_d01_direcao as d

def test_lag21_is_aligned_with_t20_predictor():
    a=d.synthetic_pair(0)
    s=np.sign(a['direction'])
    t=np.arange(100,d.SYN_N-1)
    assert .79<float(np.mean(s[t+1]==s[t-20]))<.85
    assert abs(float(np.mean(np.sign(a['null'][t+1])==np.sign(a['null'][t-20])))-.5)<.025

def test_energy_paired_in_volatility_and_magnitudes():
    z=d.synthetic_pair(0)
    np.testing.assert_array_equal(z['null']**2,z['direction']**2)

def test_features_are_strictly_causal():
    z=d.synthetic_pair(0)
    r=z['null'].copy()
    x=d.synthetic_coords(r)
    t0,x0,y0=d.feature_matrix(r,x)
    k=1500
    r[k+1:]*=-1
    xx=d.synthetic_coords(r)
    t1,x1,y1=d.feature_matrix(r,xx)
    np.testing.assert_allclose(x0[t0==k],x1[t1==k],atol=1e-12,rtol=0)
    assert not np.array_equal(y0[t0==k],y1[t1==k])  # o alvo futuro DEVE mudar; as features nao

def test_feature_design_columns_and_lags():
    z=d.synthetic_pair(0)
    r=z['direction'];x=d.synthetic_coords(r)
    t,X,y=d.feature_matrix(r,x)
    assert X.shape[1]==19
    assert d.FEATURE_NAMES[16]=='sign20'
    j=1010
    ix=np.where(t==j)[0][0]
    assert X[ix,16]==np.sign(r[j-20])
    assert X[ix,18]==np.sign(r[j-60])
    assert y[ix]==int(r[j+1]>0)

def test_data_partitions_disjoint_and_no_holdout_used_in_training():
    assert d.TRAIN_IDS==tuple(range(12))
    assert d.VAL_IDS==tuple(range(12,16))
    assert d.TEST_IDS==tuple(range(16,24))
    assert len(set(d.TRAIN_IDS+d.VAL_IDS+d.TEST_IDS))==24

def test_reproducibility_of_development_path():
    a=d.synthetic_pair(1)
    b=d.synthetic_pair(1)
    np.testing.assert_array_equal(a['null'],b['null'])
    np.testing.assert_array_equal(a['direction'],b['direction'])

def test_frozen_model_predictor_sklearn_parity():
    gen=np.random.default_rng(55)
    x=gen.normal(size=(600,11))
    y=(x[:,0]>.1).astype(int)
    m=d.fit(x,y)
    scaler=StandardScaler().fit(x)
    lr=LogisticRegression(C=.1,max_iter=500,solver='lbfgs').fit(scaler.transform(x),y)
    np.testing.assert_allclose(d.predict(m,x),lr.predict_proba(scaler.transform(x))[:,1],atol=1e-12)

def test_features_dont_contain_price_future():
    z=d.synthetic_pair(0)
    r=z['null']
    xyz=d.synthetic_coords(r)
    t,x,y=d.feature_matrix(r,xyz)
    assert t.min()>=61 and t.max()<=len(r)-2
    assert (np.isfinite(x)).all() and (y>=0).all()

def test_protocol_knobs():
    assert d.LONG_LAGS==(5,10,20,40,60)
    assert d.ARMS=={'B0':11,'B1':14,'B2':19}
    assert d.BOOT_N==2000
    assert d.SYN_START>=d.SYN_ANCHOR+60
