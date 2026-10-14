"""C01 engineering only: independence, deterministic GMM3 and geometry."""
import numpy as np
import pytest
from experiments.c01_estimacao_independente import (
    N_PER_ARM, independent_pair, seed_for, estimate_gmm, estimate_pair,
    baseline_features, hdr_features, pilot_record,
)

def test_namespace_seeds_are_distinct_and_reproducible():
    roles=('nuisance','observed_A','observed_B','fit_A','fit_B','entropy','fr_ambient','hdr50','hdr95')
    seeds=[seed_for('calibration','T3',4,role) for role in roles]
    assert len(set(seeds))==len(seeds)
    assert seeds[0]==seed_for('calibration','T3',4,'nuisance')
    assert seeds[0]!=seed_for('training','T3',4,'nuisance')

def test_test_partition_stays_sealed():
    with pytest.raises(ValueError,match='sealed test'):
        independent_pair('T0',0,split='test')

def test_a_b_are_independent_and_immutable():
    p=independent_pair('T0',5)
    assert p.a.shape==p.b.shape==(N_PER_ARM,3)
    assert p.a_sha256!=p.b_sha256 and not np.shares_memory(p.a,p.b)
    assert not p.a.flags.writeable and not p.b.flags.writeable
    pp=independent_pair('T0',5)
    assert (p.a_sha256,p.b_sha256)==(pp.a_sha256,pp.b_sha256)
    assert p.a_seed!=p.b_seed

def test_seed_split_and_case_isolation():
    p=independent_pair('T2',0)
    q=independent_pair('T2',0,split='training')
    r=independent_pair('T3',0)
    assert len({p.a_sha256,q.a_sha256,r.a_sha256})==3

def test_n_is_locked():
    with pytest.raises(ValueError,match='750'):
        independent_pair('T0',0,n=749)

def test_gmm3_fits_separate_samples():
    p=independent_pair('T5',1)
    a,b=estimate_pair(p)
    assert a.converged and b.converged
    assert a.model.means.shape==(3,3) and b.model.means.shape==(3,3)
    assert np.all(np.linalg.eigvalsh(a.model.covs)>0)
    assert np.all(np.linalg.eigvalsh(b.model.covs)>0)
    assert not np.allclose(a.model.means,b.model.means)

def test_gmm_rejects_wrong_sample_size():
    with pytest.raises(ValueError,match='750'):
        estimate_gmm(np.zeros((749,3)),seed=1)

def test_baseline_metrics_finite_with_one_estimated_pair():
    p=independent_pair('T3',2)
    a,b=estimate_pair(p)
    out=baseline_features(p,a,b,n_mc=2000)
    assert {'entropy_delta','fr_ambient','energy'}.issubset(out)
    assert len([k for k in out if k.startswith('delta_cov_')])==6
    assert all(np.isfinite(v) for v in out.values())
    assert out['fr_ambient']>=0

def test_hdr_metrics_use_fitted_models_not_true_parameters():
    p=independent_pair('T1',0)
    a,b=estimate_pair(p)
    out=hdr_features(p,a,b,grid_n=35,cutoff_n=4000,cover_n=4000)
    assert all(np.isfinite(v) for v in out.values())
    assert .2<out['hdr50_center_distance']<1.2
    assert 'hdr95_center_distance' in out
    assert 0<=out['hdr50_voxel_iou_loss']<=1
    assert out['hdr50_shape_tensor_diff']>=0

def test_pilot_record_reproducible_and_no_labels_of_test():
    a=pilot_record('T0',0,n_mc=2000)
    b=pilot_record('T0',0,n_mc=2000)
    assert a==b
    assert a['status']=='ENGINEERING_ONLY' and a['split']=='calibration'
    assert a['samples_sha256']['A']!=a['samples_sha256']['B']

def test_t3_rotated_shape_tensor_can_see_orientation():
    pair=independent_pair('T3',7)
    fa,fb=estimate_pair(pair)
    out=hdr_features(pair,fa,fb,grid_n=35,cutoff_n=4000,cover_n=4000)
    assert out['hdr50_shape_tensor_diff']>.03
    assert out['hdr50_voxel_iou_loss']>.1
