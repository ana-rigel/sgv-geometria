"""M8 movement regression: translation, expansion, missing rotation, pairing."""
import numpy as np
import pytest
from experiments.m8_transformacoes_forma_3d import (
    calibrate,motion_of_pairs,summarise,bootstrap_observation,
    check_resolution,evaluate_origin,SCALARS)
from experiments.isosuperficies_morfometria import (
    make_grid,extract_mesh,describe_mesh,motion)
from sgvgeo.flow import default_sf1,simulate_sf1

def test_sphere_translation_does_not_claim_rotation():
    r=calibrate()
    np.testing.assert_allclose(r['known_sphere_shift'],
                               [.4,-.3,.2],atol=.005)
    assert r['sphere_rotation_unidentifiable']

def test_known_expansion_in_synthetic_ellipsoids():
    points,spacing=make_grid(61)
    def make(center,scale):
        d=(points-np.asarray(center))/scale
        f=np.exp(-.5*((d[:,0]/1.3)**2+
                       (d[:,1]/.85)**2+(d[:,2]/.48)**2))
        mesh,truncated=extract_mesh(f.reshape((61,61,61)),
                                     float(np.exp(-.5)),spacing)
        return mesh,describe_mesh(mesh,truncated=truncated,coverage=1.)
    a,pa=make([0,0,0],1.)
    b,pb=make([.2,-.1,0],1.10)
    report=motion(a,pa,b,pb,seed=10)
    assert report['quality_pass']
    assert np.isclose(report['isotropic_scale'],1.1,atol=.04)
    assert np.linalg.norm(np.array(report['translation_vector'])-
                          np.array([.2,-.1,0]))<.05
    assert report['chamfer_residual_normalized'] is not None

def test_unidentified_axis_is_not_imputed_as_zero():
    sample=np.random.default_rng(34).normal(size=(500,3))
    observed=motion_of_pairs(sample,sample,seed=35)
    assert observed['valid']
    if not observed['orientation_identifiable']:
        assert observed['rotation_angle_deg'] is None
        assert observed['chamfer_residual_normalized'] is None

def test_summary_does_not_claim_superiority_without_pairs():
    data={'asof_ms':1,
          'observed':{k:0 for k in SCALARS},
          'models':{v:{'errors':{k:None for k in SCALARS}}
                    for v in ('sf1','m5','m6')}}
    r=summarise([data]*6)
    assert not r['paired_m6_vs_m5']['rotation_angle_deg']['gate']
    assert r['paired_m6_vs_m5']['rotation_angle_deg']['n_pairs']==0

def test_bootstrap_reports_descriptive_not_confidence():
    s=simulate_sf1(default_sf1(),3200,seed=43)
    r=bootstrap_observation(s,1500,seed=44,block=15,reps=4)
    assert r['n_total']==4
    assert r['quantiles_descriptive']['translation_norm'] is None

def test_grid_uses_specified_resolution():
    s=simulate_sf1(default_sf1(),3200,seed=45)
    results=check_resolution(s,1500,seed=46)
    assert set(results)=={'35','49'}

def test_discontinuous_real_origin_rejected():
    s=simulate_sf1(default_sf1(),6800,seed=51)
    s.loc[5400:,'timestamp']+=60000
    with pytest.raises(ValueError,match='Gap'):
        evaluate_origin(s.iloc[:5000],s.iloc[5000:6500],
                        60000,seed=52,reps=1)
