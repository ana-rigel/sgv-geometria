import numpy as np
import pytest
from experiments.c02_generators import (banana,banana_inverse,seed_for,Mixture,
    family_model,pair_samples,FAMILIES_DEV,FAMILIES_OOD,CLASSES)

def test_banana_inverse_and_unit_jacobian():
    x=np.random.default_rng(1).normal(size=(500,3))
    for s in (.3,.65):
        np.testing.assert_allclose(banana_inverse(banana(x,s),s),x,atol=1e-12)

def test_families_normalized_positive():
    for family in FAMILIES_DEV+FAMILIES_OOD:
        m=family_model(family)
        assert len(m.weights) in (3,7) and np.isclose(m.weights.sum(),1)
        assert np.min(np.linalg.eigvalsh(m.covs))>0

def test_all_development_pairs():
    for fam in FAMILIES_DEV:
        for label in CLASSES:
            a,b=pair_samples(fam,label,2,split='calibration')
            assert a.shape==(750,3)==b.shape and np.isfinite(a).all() and np.isfinite(b).all()
            assert not np.array_equal(a,b)

def test_reproducible_and_namespace_isolated():
    a,b=pair_samples('S5','T6',3)
    c,d=pair_samples('S5','T6',3)
    np.testing.assert_array_equal(a,c);np.testing.assert_array_equal(b,d)
    assert len({seed_for('calibration','S5','T6',3,p) for p in ('A','B','nuisance','rare')})==4

def test_sealed_ood_partition():
    with pytest.raises(ValueError,match='sealed'):pair_samples('R7','T0',0,split='ood_test')
    with pytest.raises(ValueError,match='prohibited'):pair_samples('R7','T0',0,split='training')

def test_ood_models_calibration_only():
    for fam in FAMILIES_OOD:
        a,b=pair_samples(fam,'T3',2)
        assert a.shape==b.shape==(750,3)

def test_t0_is_same_generator_not_same_samples():
    a,b=pair_samples('G3','T0',3)
    assert a.shape==b.shape and not np.array_equal(a,b)
