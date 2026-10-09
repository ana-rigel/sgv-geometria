"""M9 calibration: symmetry quotient, ICP holdout, fail-closed axes."""
import numpy as np
from scipy.spatial.transform import Rotation
from experiments.isosuperficies_morfometria import (
    analytic_field,extract_mesh,describe_mesh)
from experiments.m9_registro_simetrico_3d import (
    calibrate,compare_meshes,quotient_axis_angle,
    heldout_chamfer,aggregate,bootstrap,
    METRICS)

def known_mesh(kind='sphere'):
    f,t,d=analytic_field(kind,61)
    m,cut=extract_mesh(f,t,d)
    assert not cut
    return m

def test_analytic_calibration_known_transforms():
    result=calibrate()
    assert result['sphere_axis_rotation'] is None
    assert 15<result['ellipsoid_axis_angle']<35
    assert result['ellipsoid_deformed_holdout']>0

def test_sphere_rotations_do_not_create_identifiable_axes():
    a=known_mesh()
    b=a.copy()
    T=np.eye(4)
    T[:3,:3]=Rotation.from_euler('xyz',[40,-15,70],degrees=True).as_matrix()
    b.apply_transform(T)
    angle,details=quotient_axis_angle(a,b)
    assert angle is None
    assert not details['axis_identifiable']
    measured=compare_meshes(a,b,seed=110)
    assert measured['valid']
    assert measured['axis_angle_deg'] is None
    assert measured['heldout_deformation'] is not None

def test_quotient_axis_angle_resolves_sign_symmetry():
    a=known_mesh()
    a.apply_scale([1.5,1.0,.55])
    b=a.copy()
    T=np.eye(4)
    T[:3,:3]=Rotation.from_euler('z',20,degrees=True).as_matrix()
    b.apply_transform(T)
    angle,details=quotient_axis_angle(a,b)
    assert details['axis_identifiable']
    assert 18<angle<22

def test_holdout_distance_is_nonnegative():
    rng=np.random.default_rng(5)
    A=rng.normal(size=(100,3))
    assert heldout_chamfer(A,A)<1e-12
    assert heldout_chamfer(A,A+np.array([5,0,0]))>1

def test_invalid_pairs_do_not_fake_winner():
    record={'models':{k:{'abs_error':{n:None for n in METRICS}}
                      for k in ('sf1','m5','m6')}}
    result=aggregate([record]*6)
    assert result['paired_m6_vs_m5']['axis_angle_deg']['n_paired']==0
    assert not result['paired_m6_vs_m5']['axis_angle_deg']['comparison_gate']

def test_bootstrap_is_diagnostic_only_when_few_draws():
    from sgvgeo.flow import simulate_sf1,default_sf1
    sample=simulate_sf1(default_sf1(),3200,seed=98)
    report=bootstrap(sample,1500,seed=99,block=15,reps=3)
    assert report['n_replicates']==3
    assert report['q10_q50_q90']['axis_angle_deg'] is None
    assert not report['rotation_stable']

def test_two_grids_prespecified():
    from sgvgeo.flow import simulate_sf1,default_sf1
    sample=simulate_sf1(default_sf1(),3200,seed=101)
    from experiments.m9_registro_simetrico_3d import measure_frame
    out={str(n):measure_frame(sample,1500,104,n=n) for n in (35,49)}
    assert set(out)=={'35','49'}
