"""Unit-level controls for SGV-ID4, no sealed test trajectories."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from pipeline import id4_vol_direction as q


def test_disjoint_partitions():
    assert len(set(q.TRAIN_IDS+q.VALIDATION_IDS+q.TEST_IDS))==30
    assert len(q.TRAIN_IDS)==12 and len(q.VALIDATION_IDS)==6 and len(q.TEST_IDS)==12


def test_paired_squared_returns_identical():
    p=q.paired_path(0)
    np.testing.assert_array_equal(p['null']['r']**2,p['direction']['r']**2)
    assert p['null']['coord'].shape == p['direction']['coord'].shape == (q.N,3)
    assert np.isfinite(p['null']['coord'][q.FIRST_T:]).all()
    assert np.isfinite(p['direction']['coord'][q.FIRST_T:]).all()


def test_reproducible_with_distinct_ids():
    p=q.paired_path(0)
    p2=q.paired_path(0)
    other=q.paired_path(1)
    np.testing.assert_array_equal(p['sigma'],p2['sigma'])
    np.testing.assert_array_equal(p['direction']['sign'],p2['direction']['sign'])
    assert not np.array_equal(p['sigma'],other['sigma'])


def test_lag4_positive_control_has_directional_memory():
    p=q.paired_path(0)
    s=p['direction']['sign']
    same=np.mean(s[4:]==s[:-4])
    assert .82<same<.88
    sn=p['null']['sign']
    assert abs(np.mean(sn[4:]==sn[:-4])-.5)<.025


def test_state_coords_do_not_read_future():
    p=q.paired_path(0)
    r=p['null']['r'].copy()
    t=4000
    x=q.coordinates(r)
    r[t+1:]*=-1
    y=q.coordinates(r)
    np.testing.assert_allclose(x[t],y[t],rtol=0,atol=1e-14)


def test_sampled_energy_observer_identical():
    p=q.paired_path(0)
    a=q.clean_energy_memory(p)
    assert np.isfinite(a) and abs(a)<.05
    np.testing.assert_array_equal(
        p['oracle_energy'],
        (p['direction']['r']/p['sigma'])**2)


def test_design_uses_t_minus_3_only_as_added_feature():
    p=q.paired_path(0)
    base,extra,y=q.design_matrix(p,'direction')
    assert base.shape==(q.N-q.FIRST_T-1,8)
    assert extra.shape==(len(y),1)
    t=q.FIRST_T
    assert extra[0,0]==p['direction']['sign'][t-3]
    assert y[0]==int(p['direction']['sign'][t+1]>0)
    assert base[0,-1]==p['direction']['sign'][t-2]


def test_frozen_prediction_matches_sklearn():
    rng=np.random.default_rng(42)
    x=rng.normal(size=(500,8))
    y=(x[:,0]+x[:,1]+rng.normal(size=500)*.5>0).astype(int)
    f=q.fit_model(x,y)
    ref=StandardScaler().fit(x)
    classifier=LogisticRegression(C=1,max_iter=1000,solver='lbfgs').fit(ref.transform(x),y)
    np.testing.assert_allclose(q.frozen_predict(f,x),
        classifier.predict_proba(ref.transform(x))[:,1],atol=1e-12)


def test_primary_rules_are_frozen():
    assert q.BOOTSTRAPS==2000
    assert q.SIGN_PERSISTENCE==.85
    assert q.BASE_NAMES[-1]=='sign_t_minus_2'
    assert q.EXTRA_NAME=='sign_t_minus_3'
