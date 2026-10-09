"""M11 exact triangle search and deterministic quadrature integrity."""
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from experiments.isosuperficies_morfometria import analytic_field,extract_mesh
from experiments.m11_distancia_superficie_nulos import (
    normalize_mesh,area_quadrature,NearestTriangle,
    direct_distance,measure_meshes,synthetic,pooled_null,refit)

def sphere():
    f,t,dx=analytic_field('sphere',61)
    m,bad=extract_mesh(f,t,dx)
    assert not bad
    return m

def test_exact_same_mesh_distance_vanishes():
    mesh=normalize_mesh(sphere())
    r=direct_distance(mesh,mesh,64)
    assert r['symmetric']<1e-8

def test_nearest_triangle_against_exhaustive_all_faces():
    mesh=normalize_mesh(sphere())
    proximity=NearestTriangle(mesh)
    points=np.array([[0,0,2.5],[1.7,0.2,.1],[-2,.4,.2]])
    actual=proximity.distances(points)
    brute=[]
    for p in points:
        q=trimesh.triangles.closest_point(
            proximity.faces,np.broadcast_to(p,(len(proximity.faces),3)))
        brute.append(np.linalg.norm(q-p,axis=1).min())
    np.testing.assert_allclose(actual,brute,rtol=1e-12,atol=1e-12)

def test_deterministic_quadrature_repeated():
    m=normalize_mesh(sphere())
    a=area_quadrature(m,64)
    b=area_quadrature(m,64)
    np.testing.assert_array_equal(a,b)
    assert a.shape==(64,3)

def test_known_shape_expansion_and_distortion():
    r=synthetic()
    assert r['identical_mesh']['symmetric']<1e-8
    assert r['deformed']['distance_512']>r['equivalent']['distance_512']

def test_stationary_null_reports_small_sample_as_diagnostic_only():
    rng=np.random.default_rng(31)
    x=rng.normal(size=(600,3))
    r=pooled_null(x[:300],x[300:],seed=12,block=15,reps=2)
    assert r['n_requested']==2 and r['quantiles'] is not None

def test_nonfinite_surface_is_rejected():
    from experiments.m11_distancia_superficie_nulos import measure_samples
    x=np.ones((400,3))
    x[0,0]=np.nan
    assert not measure_samples(x,x,11)['valid']
