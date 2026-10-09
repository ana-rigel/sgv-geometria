"""Propriedades analiticas: esfera, toro, dois corpos, superfície cortada."""
import numpy as np
import pytest
from experiments.isosuperficies_morfometria import (
    analytic_field,extract_mesh,describe_mesh,mesh_topology,curvatures,
    hdr_thresholds,make_grid,motion,principal_axes,SEED,
)


@pytest.mark.parametrize("kind,components,genera",[
    ("sphere",1,[0]),("torus",1,[1]),("two_spheres",2,[0,0])
])
def test_known_topology_euler_genus(kind,components,genera):
    field,tau,dx=analytic_field(kind,n=61)
    mesh,truncated=extract_mesh(field,tau,dx)
    p=describe_mesh(mesh,truncated=truncated,coverage=1.)
    assert p["quality_pass"],p["invalid_reason"]
    assert p["components"]==components
    assert p["genus_components"]==genera
    assert p["watertight"]
    assert p["gauss_bonnet_relative_error"]<1e-6


def test_torus_negative_K_does_not_prove_two_lobes():
    f,t,dx=analytic_field("torus",n=61)
    m,trunc=extract_mesh(f,t,dx)
    d=describe_mesh(m,truncated=trunc,coverage=1.)
    assert d["components"]==1
    assert d["genus_components"]==[1]
    assert d["negative_K_area_fraction"]>.05


def test_clipped_surface_suppresses_volume_and_genus():
    f,t,dx=analytic_field("clipped",n=61)
    m,trunc=extract_mesh(f,t,dx)
    p=describe_mesh(m,truncated=trunc,coverage=1.)
    assert trunc
    assert not p["quality_pass"]
    assert p["genus_components"] is None
    assert p["volume"] is None


def test_sphere_area_volume_and_curvature_approximation():
    f,t,dx=analytic_field("sphere",n=61)
    m,trunc=extract_mesh(f,t,dx)
    p=describe_mesh(m,truncated=trunc,coverage=1.)
    assert abs(p["volume"]-(4*np.pi/3))<.12
    assert abs(p["area"]-4*np.pi)<.4
    assert p["isoperimetric_quotient"]>.95
    assert abs(p["K_median"]-1)<.5
    assert p["negative_K_area_fraction"]<.05


def test_HDR_threshold_nested_and_mass():
    pts,dx=make_grid(35)
    rho=np.exp(-np.sum(pts**2,axis=1)/2) / (2*np.pi)**1.5
    field=rho.reshape(35,35,35)
    h,coverage=hdr_thresholds(field,dx)
    assert .90<coverage<1.05
    assert h[.25]["tau"]>h[.5]["tau"]>h[.75]["tau"]
    for k in (.25,.5,.75):
        assert abs(h[k]["mass_in_grid"]-k)<.025


def test_reject_insufficient_coverage_without_claiming_topology():
    f,t,dx=analytic_field("sphere",n=61)
    mesh,trunc=extract_mesh(f,t,dx)
    p=describe_mesh(mesh,truncated=trunc,coverage=.7)
    assert not p["quality_pass"]
    assert p["genus_components"] is None


def test_same_sphere_motion_is_near_zero():
    f,t,dx=analytic_field("sphere",n=61)
    mesh,trunc=extract_mesh(f,t,dx)
    p=describe_mesh(mesh,truncated=trunc,coverage=1.)
    out=motion(mesh,p,mesh,p,seed=SEED)
    assert out["quality_pass"]
    assert out["translation_norm"]<1e-6
    assert abs(out["volume_ratio"]-1)<1e-6
    assert not out["orientation_identifiable"]


def test_nondegenerate_ellipsoid_translation_scale():
    pts,dx=make_grid(61)
    mu=np.array([0.,0.,0.])
    def p(center,scale):
        d=(pts-center)/scale
        return np.exp(-.5*((d[:,0]/1.25)**2+(d[:,1]/.8)**2+
                              (d[:,2]/.45)**2)).reshape((61,61,61))
    a=p(mu,1.)
    b=p(np.array([.3,0.,0.]),1.12)
    t=float(np.exp(-.5))
    ma,ta=extract_mesh(a,t,dx)
    mb,tb=extract_mesh(b,t,dx)
    pa=describe_mesh(ma,truncated=ta,coverage=1.)
    pb=describe_mesh(mb,truncated=tb,coverage=1.)
    mov=motion(ma,pa,mb,pb)
    assert mov["quality_pass"]
    assert mov["orientation_identifiable"]
    assert .20 < mov["translation_norm"] < .40
    assert 1.05 < mov["isotropic_scale"] < 1.18
    assert mov["rotation_angle_deg"]<8


def test_invalid_grid_rejected():
    with pytest.raises(ValueError):
        make_grid(20)
    with pytest.raises(ValueError):
        hdr_thresholds(np.ones((5,5,5)),1.0)
