"""AMB01 preflight: use ONLY IDs 0..11, never sealed IDs 12..19."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from pipeline import sgv_amb01_memoria_ambiental as d

def test_partitions_disjoint():
    assert d.TRAIN_IDS==tuple(range(8))
    assert d.VAL_IDS==tuple(range(8,12))
    assert d.TEST_IDS==tuple(range(12,20))
    assert len(set(d.TRAIN_IDS+d.VAL_IDS+d.TEST_IDS))==20

def test_squared_returns_same_for_four_conditions():
    p=d.synthetic_path(0)
    for k in d.KINDS[1:]:
        np.testing.assert_array_equal(p['N']['r']**2,p[k]['r']**2)

def test_internal_control_has_the_correct_lag():
    p=d.synthetic_path(0)
    s=p['I']['sign']
    t=np.arange(100,d.N-1)
    assert .79<np.mean(s[t+1]==s[t-20])<.85
    sn=p['N']['sign']
    assert abs(np.mean(sn[t+1]==sn[t-20])-.5)<.03

def test_environment_persistence_and_forward_response():
    p=d.synthetic_path(0)
    a=p['E']['env'][:,0]
    assert np.corrcoef(a[2:],a[:-2])[0,1]>.12
    s=p['E']['sign']
    assert np.mean(s[1:][a[:-1]>2])>np.mean(s[1:][a[:-1]<-2])

def test_33_features_and_arm_semantics():
    p=d.synthetic_path(1)
    t,X,y=d.feature_matrix(p['I']['r'],p['I']['coords'],p['I']['env'],start=d.SYN_START)
    assert X.shape[1]==33
    assert t.min()>=d.SYN_START
    assert len(y)==len(t)
    assert [d.arm_matrix(X,arm).shape[1] for arm in d.ARMS]==[16,28,21,33]
    j=t[0]
    assert X[0,28+2]==np.sign(p['I']['r'][j-20])
    assert X[0,16]==p['I']['env'][j-1,0]
    assert y[0]==int(p['I']['r'][j+1]>0)

def test_no_future_in_features():
    p=d.synthetic_path(1)
    r=p['N']['r'].copy();env=p['N']['env'].copy()
    coords=d.D01.synthetic_coords(r)
    t,x,y=d.feature_matrix(r,coords,env,start=950)
    idx=1600
    r[idx+1:]*=-1;env[idx+1:]*=-1
    coords2=d.D01.synthetic_coords(r)
    t2,xx,yy=d.feature_matrix(r,coords2,env,start=950)
    np.testing.assert_array_equal(x[t==idx],xx[t2==idx])
    assert y[t==idx][0]!=yy[t2==idx][0]

def test_reproducible_path():
    a=d.synthetic_path(2);b=d.synthetic_path(2)
    for k in d.KINDS:
        np.testing.assert_array_equal(a[k]['r'],b[k]['r'])
        np.testing.assert_array_equal(a[k]['env'],b[k]['env'])

def test_frozen_inference_matches_sklearn():
    rg=np.random.default_rng(99)
    X=rg.normal(size=(800,16));y=(X[:,0]+rg.normal(size=800)>.1).astype(int)
    frozen=d.fit_model(X,y)
    ss=StandardScaler().fit(X)
    m=LogisticRegression(C=d.C,solver='lbfgs',max_iter=1500).fit(ss.transform(X),y)
    np.testing.assert_allclose(d.predict(frozen,X),m.predict_proba(ss.transform(X))[:,1],atol=1e-12)

def test_all_metrics_are_differences_of_logloss():
    ll={'A0':np.array([.7,.5]),'AE':np.array([.6,.4]),'AI':np.array([.6,.5]),'AEI':np.array([.5,.3])}
    q=d.diffs(ll)
    assert np.isclose(q['D_E'],.1)
    assert np.isclose(q['D_I_given_E'],.1)
    assert np.isclose(q['D_E_given_I'],.15)

def test_registered_knobs():
    assert d.ENV_LAGS==(1,5,15,30,60,120)
    assert d.INNER_LAGS==(5,10,20,40,60)
    assert d.BOOT_N==2000
    assert d.C==.2
