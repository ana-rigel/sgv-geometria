"""Engineering T0 gate controls, no official held-out data."""
import pytest
from scripts import c01_t0_null_calibration as c01

def test_disjoint_groups():
    sets=[set(range(*v)) for v in c01.GROUPS.values()]
    assert list(map(len,sets))==[40,40,40]
    assert all(not sets[i]&sets[j] for i in range(3) for j in range(i+1,3))
    assert c01.REPLICATE_BASE>=1000000

def test_absolute_signed_metrics():
    assert c01.anomaly({'hdr50_log_volume_ratio':-.45},'hdr50_log_volume_ratio')==.45
    assert c01.anomaly({'hdr50_delta_components':-2.},'hdr50_delta_components')==2.
    with pytest.raises(ValueError,match='negative'):
        c01.anomaly({'hdr95_voxel_iou_loss':-.5},'hdr95_voxel_iou_loss')

def test_wilson_interval_bounds():
    for k in (0,2,4,40):
        lo,hi=c01.wilson(k,40)
        assert 0<=lo<=k/40<=hi<=1

def test_joint_score_with_all_twelve():
    row={'values':{k:0. for k in c01.SCORING_FEATURES}}
    scales={k:1. for k in c01.SCORING_FEATURES}
    row['values']['hdr95_voxel_iou_loss']=.7
    assert c01.score(row,scales)==.7
    row['values']['hdr50_log_area_ratio']=-.9
    assert c01.score(row,scales)==.9

def test_independent_diagnostic_cannot_change_threshold(monkeypatch):
    def stub(rep):
        v={k:float((rep%17)+1) for k in c01.SCORING_FEATURES}
        if rep>=80:v['hdr50_center_distance']=1e6
        for k in c01.NUMERIC_FEATURES:v.setdefault(k,0.)
        for a in ('hdr50','hdr95'):
            for side in ('a','b'):v[f'_num_{a}_coverage_error_{side}']=0.
        return {'values':v,'replicate':rep,'sample_hash_A':str(rep)+'a',
                'sample_hash_B':str(rep)+'b'}
    monkeypatch.setattr(c01,'measure',stub)
    out=c01.run()
    assert out['all_valid'] and out['threshold']<10
    assert out['validation_alerts']==40

def test_fails_closed_if_fit_invalid(monkeypatch):
    def fail(_):
        raise ValueError('nonconvergent')
    monkeypatch.setattr(c01,'measure',fail)
    outcome=c01.run()
    assert not outcome['all_valid']
    assert outcome['status']=='INCONCLUSIVE_FAILURES'
    assert 'threshold' not in outcome
