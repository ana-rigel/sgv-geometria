import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from sgv_m11i.integrated import integrate_meshes,synthetic,integrate_window

def test_known_transformations():
    results={x["case"]:x for x in synthetic()}
    for name in ("identity","translation","isotropic","rotation"):
        assert results[name]["valid"]
        assert results[name]["distance_512"]<.005,(name,results[name]["distance_512"])
    np.testing.assert_allclose(results["translation"]["delta_center"],[.4,-.3,.2],atol=1e-6)
    assert abs(results["isotropic"]["delta_log_volume"]-3*np.log(1.1))<1e-5
    assert abs(results["rotation"]["theta_deg"]-25)<1e-3
    assert results["anisotropic"]["distance_512"]>.02
    assert results["sphere_unidentifiable"]["theta_deg"] is None

def test_bad_mesh():
    a=trimesh.creation.icosphere(subdivisions=2)
    bad=trimesh.Trimesh(vertices=a.vertices,faces=a.faces[:-1],process=False)
    assert not integrate_meshes(a,bad)["valid"]

def test_integrated_gmm_window():
    rng=np.random.default_rng(12)
    x=rng.standard_normal((1500,3))
    z=integrate_window(x)
    assert z["valid"]
    assert len(z["G"])==9
    assert z["D_A"]>=0 and z["D_B"]>=0
    assert abs(z["D_B"]-z["D_A"]-z["delta_D"])<1e-10
