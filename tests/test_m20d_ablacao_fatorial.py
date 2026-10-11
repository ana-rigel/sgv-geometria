"""SGV-M20d math/integrity/causality gates; synthetic trials only."""
import numpy as np
from experiments import m20d_ablacao_fatorial as m


def test_oracle_direction_matches_original_latent_data():
    rng=np.random.default_rng(1)
    q=m.random_rotation(rng)
    raw=np.random.default_rng(2).normal(size=(200,3))
    data=raw@q.T
    np.testing.assert_allclose(data@q[:,0],raw[:,0],atol=1e-12)


def test_same_known_model_for_hidden_and_iid():
    for sid in (0,2,3,4):
        a,A,chol=m.known_model(sid)
        np.testing.assert_array_equal(A,np.zeros((3,3)))
        np.testing.assert_array_equal(chol,np.eye(3))
    a,A,chol=m.known_model(1)
    np.testing.assert_allclose(A,np.eye(3)*.38)


def test_one_dimensional_coupling_detects_strong_but_not_exact():
    rng=np.random.default_rng(5)
    x=rng.normal(size=800)
    # Exact monotone motion has stronger dependence than an independent pair.
    dependent=np.column_stack((x,x))
    independent=np.column_stack((x,rng.normal(size=800)))
    assert m.projected_stats(dependent[:,0])["hsic_1d"]>=0
    assert m.projected_stats(independent[:,0])["cqw2_1d"]>=0


def test_no_future_leakage_in_var_fit():
    rng=np.random.default_rng(11)
    x=rng.normal(size=(1000,3))
    p=m.fit_var(x[:800])
    x[800:]*=1e8
    q=m.fit_var(x[:800])
    for a,b in zip(p,q):
        np.testing.assert_array_equal(a,b)


def test_observation_identical_under_null_factors():
    row=m.one_trial(2,0,seed=707,n_refs=2,prefix_length=400)
    for d in m.DIRECTIONS:
        for n in m.LENS:
            a=row["observed_scores"][m.cell_key(d,n,"known")]
            b=row["observed_scores"][m.cell_key(d,n,"fitted")]
            assert a==b
    assert len(row["alarms"])==8


def test_rotation_is_blind_to_detector_basis_in_generation():
    x,d=m.make_truth(1100,2,np.random.default_rng(44))
    assert x.shape==(1100,3)
    assert abs(np.linalg.norm(d)-1)<1e-12
    assert np.isfinite(x).all()


def test_trial_reproducible_across_calls():
    a=m.one_trial(3,7,seed=1618,n_refs=2,prefix_length=400)
    b=m.one_trial(3,7,seed=1618,n_refs=2,prefix_length=400)
    assert a==b


def test_known_and_blind_directions_are_valid():
    for x in (m.SHORT,m.LONG):
        for n in m.NULLS:
            for d in m.DIRECTIONS:
                assert m.cell_key(d,x,n)
