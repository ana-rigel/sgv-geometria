"""SGV-M11-I: integrated measurement of two HDR50 GMM2 shells.

Faithful definitions from original SGV M2/M6/M8/M9/M11; standalone,
computes ONE GMM per shell and reuses mesh and analytic parameters.
Observational density geometry only: not physical market dynamics.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import trimesh
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from scipy.special import ndtri
from sklearn.mixture import GaussianMixture
from skimage.measure import marching_cubes

GRID = 35
GRID_CHECK = 49
EXTENT = 3.5  # exactly RANGE of original isosuperficies_morfometria.py
MIN_COVERAGE = .95
QUADS = (256, 512)
BASE_SEED = 20261009


def gaussianize(anchor: np.ndarray, observations: np.ndarray) -> np.ndarray:
    """Same empirical normal scores as original split_historical/gaussianize_three."""
    a = np.asarray(anchor, float)
    x = np.asarray(observations, float)
    if a.ndim != 2 or x.ndim != 2 or a.shape[1] != 3 or x.shape[1] != 3 or len(a) < 60:
        raise ValueError("Expected (N,3) anchor >=60 and (M,3) observations")
    if not np.isfinite(a).all() or not np.isfinite(x).all():
        raise ValueError("Nonfinite observations")
    out = np.empty_like(x)
    for j in range(3):
        ordered = np.sort(a[:, j])
        left = np.searchsorted(ordered, x[:, j], side="left")
        right = np.searchsorted(ordered, x[:, j], side="right")
        u = (.5 * (left + right) + .5) / (len(ordered) + 1.)
        out[:, j] = ndtri(np.clip(u, .5 / (len(ordered) + 1.),
                                 (len(ordered) + .5) / (len(ordered) + 1.)))
    return out


def split_historical(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, float)
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 480:
        raise ValueError("Need >=480 points in 3D")
    n_anchor = int(.30 * len(x))
    standardized = gaussianize(x[:n_anchor], x[n_anchor:])
    mid = len(standardized) // 2
    if min(mid, len(standardized)-mid) < 120:
        raise ValueError("A/B samples too short")
    return standardized[:mid], standardized[mid:]


def flow_coordinates(df: pd.DataFrame) -> np.ndarray:
    """Same formula as historical sgvgeo.flow, at CLOSED bar t."""
    for k in ("close", "volume", "taker_buy"):
        if k not in df: raise ValueError("Missing column: " + k)
    close = pd.to_numeric(df["close"]).astype(float)
    volume = pd.to_numeric(df["volume"]).astype(float)
    buy = pd.to_numeric(df["taker_buy"]).astype(float)
    if not (np.isfinite(close).all() and np.isfinite(volume).all() and np.isfinite(buy).all()):
        raise ValueError("Nonfinite market records")
    if (close <= 0).any() or (volume <= 0).any() or (buy < 0).any() or (buy > volume).any():
        raise ValueError("Invalid close, volume or taker volume")
    if "timestamp" in df:
        ts = df["timestamp"].to_numpy(dtype=np.int64)
        if len(ts) > 1:
            step = np.diff(ts)
            if np.any(step <= 0) or np.any(step != step[0]):
                raise ValueError("Timestamp duplicates/gaps/irregular spacing")
    r = np.log(close).diff()
    sigma = r.shift(1).rolling(60, min_periods=30).std()
    iota = (2 * buy / volume - 1).clip(-1, 1)
    ell = np.log(volume)
    nu = ell - ell.shift(1).rolling(1500, min_periods=300).median()
    return np.column_stack(((r / sigma).to_numpy(), iota.to_numpy(), nu.to_numpy()))


def grid_points(n=GRID, extent=EXTENT):
    if n < 15 or n % 2 == 0 or extent <= 0:
        raise ValueError("Grid must be odd >=15 and extent positive")
    axis = np.linspace(-extent, extent, n)
    dx = float(axis[1]-axis[0])
    a,b,c = np.meshgrid(axis,axis,axis,indexing="ij")
    return np.column_stack((a.ravel(),b.ravel(),c.ravel())), dx


def implicit_curvatures(vertices, params):
    """Original SGV analytic level-set Gaussian curvature, not mesh angle deficit."""
    v = np.asarray(vertices, float)
    grad = np.zeros_like(v)
    hess = np.zeros((len(v),3,3),float)
    for weight, mean, precision in zip(params["weights"],params["means"],params["precisions"]):
        diff = v - mean
        force = -(diff @ precision)
        sign, logdet = np.linalg.slogdet(precision)
        if sign <= 0: raise ValueError("Non-PD mixture precision")
        quadratic = np.einsum("ni,ij,nj->n",diff,precision,diff)
        dens = weight*np.exp(.5*logdet-1.5*np.log(2*np.pi)-.5*quadratic)
        grad += dens[:,None]*force
        hess += dens[:,None,None]*(force[:,:,None]*force[:,None,:]-precision[None,:,:])
    norms = np.linalg.norm(grad,axis=1)
    if np.any(norms <= 1e-14): raise ValueError("Critical point of density on HDR")
    normal = grad/norms[:,None]
    proj = np.eye(3)[None,:,:]-normal[:,:,None]*normal[:,None,:]
    shape = (proj@hess@proj)/norms[:,None,None]
    trace = np.trace(shape,axis1=1,axis2=2)
    sq = np.einsum("nij,nji->n",shape,shape)
    return .5*(trace*trace-sq), np.abs(trace)/2.


def vertex_areas(mesh):
    """Historical barycentric vertex areas (1/3 incident triangle area)."""
    areas = np.zeros(len(mesh.vertices),float)
    tris = np.asarray(mesh.faces,int)
    a = np.asarray(mesh.area_faces,float)/3
    for k in range(3): np.add.at(areas,tris[:,k],a)
    return areas


def principal_axes(mesh, gap=.07):
    m = mesh.copy();m.fix_normals()
    vol = abs(float(m.volume))
    if vol <= 1e-12: return None,0.
    I = np.asarray(m.moment_inertia,float)
    cov = ((np.trace(I)/2)*np.eye(3)-I)/vol
    w,Q = np.linalg.eigh(cov)
    idx = np.argsort(w)[::-1]
    w,Q = w[idx],Q[:,idx]
    if np.linalg.det(Q)<0: Q[:,-1]*=-1
    separation = float(np.min((w[:-1]-w[1:])/max(w[0],1e-12)))
    if w[-1] <= 0 or separation < gap: return None,separation
    return Q,separation


def quotient_axis_angle(a,b,gap=.07):
    qa,ga = principal_axes(a,gap)
    qb,gb = principal_axes(b,gap)
    if qa is None or qb is None:
        return None,{"axis_identifiable":False,"gap_A":float(ga),"gap_B":float(gb)}
    flips=((1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1))
    angles=[]
    for signs in flips:
        R=qb@np.diag(signs)@qa.T
        angles.append(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))))
    return float(min(angles)),{"axis_identifiable":True,"gap_A":float(ga),"gap_B":float(gb)}


@dataclass
class Shell:
    mesh: trimesh.Trimesh
    params: dict | None = None
    source: str = "synthetic"
    coverage: float = 1.
    truncated: bool = False
    grid: int | None = None


def validate_shell(shell:Shell):
    m=shell.mesh.copy();m.fix_normals()
    if shell.truncated:raise ValueError("boundary_truncation")
    if not (.95 <= shell.coverage <= 1.05):raise ValueError("insufficient_coverage")
    if not m.is_watertight:raise ValueError("open_mesh")
    if len(m.vertices) < 8 or len(m.faces) < 12: raise ValueError("too_small_mesh")
    if not np.isfinite(m.vertices).all(): raise ValueError("nonfinite_mesh")
    if float(m.area)<=1e-9 or abs(float(m.volume))<=1e-10:raise ValueError("degenerate_shell")
    return m


def build_shell(sample,seed=BASE_SEED,n=GRID,extent=EXTENT)->Shell:
    """ONE full-cov GMM2 fit; same density creates mesh AND curvature."""
    x=np.asarray(sample,float)
    if x.ndim != 2 or x.shape[1]!=3 or len(x)<90 or not np.isfinite(x).all():
        raise ValueError("Need >=90 finite 3D points")
    model=GaussianMixture(n_components=2,covariance_type="full",reg_covar=1e-4,
                          max_iter=100,n_init=2,random_state=seed).fit(x)
    pts,dx=grid_points(n,extent)
    field=np.exp(model.score_samples(pts)).reshape((n,n,n))
    coverage=float(field.sum()*dx**3)
    if not .95<=coverage<=1.05:raise ValueError(f"insufficient_coverage:{coverage:.5f}")
    ordered=np.sort(field.ravel())[::-1]
    fractions=np.cumsum(ordered)/ordered.sum()
    idx=int(np.searchsorted(fractions,.5,side="left"))
    if idx+1>=len(ordered):raise ValueError("HDR threshold out of range")
    tau=float((ordered[idx]+ordered[idx+1])/2.)
    if not field.min()<tau<field.max():raise ValueError("HDR invalid level")
    boundary=np.zeros(field.shape,bool)
    for ax in range(3):
        for which in (0,-1):
            sl=[slice(None)]*3;sl[ax]=which
            boundary[tuple(sl)]=True
    touches=bool(np.any(field[boundary]>=tau))
    vertices,faces,_,_=marching_cubes(field.astype(np.float32),level=tau,
                          spacing=(dx,dx,dx),allow_degenerate=False)
    vertices=np.asarray(vertices,float)-extent
    touches |= bool(np.any(np.isclose(np.abs(vertices),extent,atol=dx*.02)))
    mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
    params={"weights":model.weights_.copy(),"means":model.means_.copy(),
            "precisions":model.precisions_.copy()}
    shell=Shell(mesh,params,"GMM2",coverage,touches,n)
    validate_shell(shell)
    return shell


def curvature_d(shell:Shell):
    """M2 negative intensity D: area mean(max(0,-K*r_eq^2))."""
    m=validate_shell(shell)
    if shell.params is None:
        return {"D":None,"K_negative_area_fraction":None,"status":"unavailable_no_density_model"}
    k,_=implicit_curvatures(m.vertices,shell.params)
    areas=vertex_areas(m)
    total=float(areas.sum())
    radius=(3*abs(float(m.volume))/(4*np.pi))**(1/3)
    d=float(np.dot(areas,np.maximum(0.,-k*radius**2))/total)
    negative=float(areas[k<0].sum()/total)
    return {"D":d,"K_negative_area_fraction":negative,"status":"valid"}


def normalize_mesh(mesh):
    m=mesh.copy();m.fix_normals()
    if not m.is_watertight:raise ValueError("Open mesh")
    vol=abs(float(m.volume))
    if vol<1e-12 or not np.isfinite(vol):raise ValueError("Degenerate volume")
    radius=(3*vol/(4*np.pi))**(1/3)
    m.apply_translation(-np.asarray(m.center_mass,float))
    m.apply_scale(1/radius)
    return m


def normalized_mesh_points(mesh,n,seed):
    m=mesh.copy();m.fix_normals()
    if not m.is_watertight:raise ValueError("Mesh not watertight")
    rad=(3*abs(float(m.volume))/(4*np.pi))**(1/3)
    pts,_=trimesh.sample.sample_surface(m,n,seed=seed)
    return (pts-np.asarray(m.center_mass,float))/rad


def kabsch(source,target):
    X=source-source.mean(axis=0);Y=target-target.mean(axis=0)
    u,_,vt=np.linalg.svd(X.T@Y)
    fix=np.eye(3);fix[-1,-1]=np.linalg.det(u@vt)
    return u@fix@vt


def heldout_chamfer(A,B):
    return float(.5*(cKDTree(B).query(A)[0].mean()+cKDTree(A).query(B)[0].mean()))


def initial_rotations(ma,mb):
    candidates=[np.eye(3)]
    for axis in np.eye(3):
        for deg in (90,180,270):
            candidates.append(Rotation.from_rotvec(axis*np.deg2rad(deg)).as_matrix())
    qa,_=principal_axes(ma);qb,_=principal_axes(mb)
    if qa is not None and qb is not None:
        for signs in ((1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)):
            candidates.append(qb@np.diag(signs)@qa.T)
    return candidates


def icp_fit(A,B,starts,iterations=14):
    tree=cKDTree(A);best=None
    for start in starts:
        R=np.asarray(start,float).copy();last=np.inf
        for _ in range(iterations):
            rotated=B@R
            ids=tree.query(rotated)[1]
            delta=kabsch(rotated,A[ids])
            R=R@delta
            score=heldout_chamfer(A,B@R)
            if abs(last-score)<1e-6:break
            last=score
        score=heldout_chamfer(A,B@R)
        if best is None or score<best[0]:best=(score,R.copy())
    return best[1],float(best[0])


def area_quadrature(mesh,n):
    triangles=np.asarray(mesh.triangles,float)
    weights=np.asarray(mesh.area_faces,float)
    if not np.isfinite(weights).all() or weights.sum()<=0:raise ValueError("Invalid triangle areas")
    goals=(np.arange(n)+.5)*weights.sum()/n
    idx=np.searchsorted(np.cumsum(weights),goals)
    return triangles[idx].mean(axis=1)


class NearestTriangle:
    """M11 exact closest-face query with conservative centroid-radius bound."""
    def __init__(self,mesh):
        self.faces=np.asarray(mesh.triangles,float)
        self.centres=self.faces.mean(axis=1)
        self.radii=np.linalg.norm(self.faces-self.centres[:,None,:],axis=2).max(axis=1)
        self.global_radius=float(self.radii.max())
        self.tree=cKDTree(self.centres)

    def distances(self,points):
        ans=[]
        for p in np.asarray(points,float):
            _,j=self.tree.query(p)
            cp=trimesh.triangles.closest_point(self.faces[int(j)][None],p[None])[0]
            upper=float(np.linalg.norm(cp-p))
            indices=np.asarray(self.tree.query_ball_point(p,upper+self.global_radius+1e-10),dtype=int)
            if len(indices):
                lower=np.linalg.norm(self.centres[indices]-p,axis=1)-self.radii[indices]
                indices=indices[lower<=upper+1e-10]
            if len(indices):
                closest=trimesh.triangles.closest_point(
                    self.faces[indices],np.broadcast_to(p,(len(indices),3)))
                upper=min(upper,float(np.linalg.norm(closest-p,axis=1).min()))
            ans.append(upper)
        return np.asarray(ans)


def direct_distance(a,b,n):
    A=area_quadrature(a,n);B=area_quadrature(b,n)
    ab=float(NearestTriangle(b).distances(A).mean())
    ba=float(NearestTriangle(a).distances(B).mean())
    return {"symmetric":(ab+ba)/2,"a_to_b":ab,"b_to_a":ba}


def registered_residual(ma,mb,seed=BASE_SEED):
    """Same normalized ICP multistart and triangle direct distance as M11."""
    a=normalize_mesh(ma);b=normalize_mesh(mb)
    sample_a=normalized_mesh_points(a,360,seed)
    sample_b=normalized_mesh_points(b,360,seed+1)
    R,train_error=icp_fit(sample_a,sample_b,initial_rotations(a,b))
    # Retain the historical multistart ICP, but audit it against the
    # four SO(3)/D2 principal-axis candidates on an independent direct
    # triangle-distance quadrature. Prevent a needless ICP perturbation
    # from appearing as residual for rigidly equivalent shells.
    rotations=[("icp",R)]
    qa,_=principal_axes(a);qb,_=principal_axes(b)
    if qa is not None and qb is not None:
        for signs in ((1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)):
            rotations.append(("axis_quotient",qb@np.diag(signs)@qa.T))
    options=[]
    for method,candidate in rotations:
        trial=b.copy()
        T=np.eye(4);T[:3,:3]=candidate.T
        trial.apply_transform(T)
        options.append((direct_distance(a,trial,64)["symmetric"],method,candidate))
    selection=min(options,key=lambda item:item[0])
    _,selection_method,R=selection
    T=np.eye(4);T[:3,:3]=R.T
    b.apply_transform(T)
    q={str(n):direct_distance(a,b,n) for n in QUADS}
    return {"distance_256":q["256"]["symmetric"],
            "distance_512":q["512"]["symmetric"],
            "directed_ab":q["512"]["a_to_b"],
            "directed_ba":q["512"]["b_to_a"],
            "relative_256_512_gap":abs(q["256"]["symmetric"]-q["512"]["symmetric"])/max(.01,q["512"]["symmetric"]),
            "icp_train_chamfer":train_error,
            "registration_method":selection_method,
            "registration_audit_d64":float(selection[0]),
            "registration_rotation":R.tolist()}


def signature(A:Shell,B:Shell,seed=BASE_SEED)->dict[str,Any]:
    """Integrated M8/M9/M11 + M2 curvature using EXACT SAME two shells."""
    out={"valid":False,"signature_complete":False,"errors":[],"source_A":A.source,
         "source_B":B.source,"grid_A":A.grid,"grid_B":B.grid}
    try:
        ma=validate_shell(A);mb=validate_shell(B)
    except (ValueError,RuntimeError) as exc:
        out["errors"].append("shell_quality:"+str(exc));return out
    ca=np.asarray(ma.center_mass,float);cb=np.asarray(mb.center_mass,float)
    va=abs(float(ma.volume));vb=abs(float(mb.volume))
    dc=cb-ca
    out.update({"valid":True,"center_A":ca.tolist(),"center_B":cb.tolist(),
                "delta_center":dc.tolist(),"translation_norm":float(np.linalg.norm(dc)),
                "volume_A":va,"volume_B":vb,"volume_ratio":vb/va,
                "delta_log_volume":float(np.log(vb/va)),"isotropic_scale":float((vb/va)**(1/3)),
                "area_A":float(ma.area),"area_B":float(mb.area),
                "coverage_A":A.coverage,"coverage_B":B.coverage})
    angle,diag=quotient_axis_angle(ma,mb)
    out.update({"theta_deg":angle,**diag})
    try:
        da=curvature_d(A);db=curvature_d(B)
        out.update({"D_A":da["D"],"D_B":db["D"],
                    "delta_D":db["D"]-da["D"] if da["D"] is not None and db["D"] is not None else None,
                    "negative_K_area_A":da["K_negative_area_fraction"],
                    "negative_K_area_B":db["K_negative_area_fraction"],
                    "curvature_status_A":da["status"],"curvature_status_B":db["status"]})
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as exc:
        out.update({"D_A":None,"D_B":None,"delta_D":None,
                    "curvature_status_A":"error","curvature_status_B":"error"})
        out["errors"].append("curvature:"+str(exc))
    try:
        out.update(registered_residual(ma,mb,seed))
        out["icp_status"]="valid"
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as exc:
        out.update({"distance_512":None,"icp_status":"error"})
        out["errors"].append("registration:"+str(exc))
    out["signature_complete"]=(out.get("distance_512") is not None
         and angle is not None and out.get("delta_D") is not None)
    out["G"]=(dc.tolist()+[out["delta_log_volume"],angle,out.get("distance_512"),
                         out.get("D_A"),out.get("D_B"),out.get("delta_D")])
    return out


def shell_from_gaussian_samples(n=1500,seed=BASE_SEED,grid=GRID):
    rng=np.random.default_rng(seed)
    x=rng.multivariate_normal([0.,0.,0.],[[1.4,.25,0.],[.25,.65,0.],[0.,0.,.25]],size=n)
    return build_shell(x,seed,grid)


def transform_shell(shell:Shell,matrix=None,translation=None,non_affine=None)->Shell:
    """Apply geometrically known transform to an existing mesh and its GMM model.

    For nonlinear warp the original GMM no longer defines an isosurface, so
    curvature remains unavailable rather than reported incorrectly.
    """
    m=shell.mesh.copy()
    A=np.eye(3) if matrix is None else np.asarray(matrix,float)
    shift=np.zeros(3) if translation is None else np.asarray(translation,float)
    if A.shape!=(3,3) or np.linalg.det(A)<=0:raise ValueError("Need invertible orientation-preserving 3x3 map")
    m.vertices=np.asarray(m.vertices,float)@A.T+shift
    params=None
    if shell.params is not None and non_affine is None:
        inv=np.linalg.inv(A)
        params={"weights":np.asarray(shell.params["weights"]).copy(),
                "means":np.asarray(shell.params["means"])@A.T+shift,
                "precisions":np.array([inv.T@P@inv for P in shell.params["precisions"]])}
    if non_affine is not None:
        m.vertices[:]=non_affine(np.asarray(m.vertices,float))
    m.fix_normals()
    return Shell(m,params,"transformed",shell.coverage,False,shell.grid)


def demo(outdir:Path,grid=GRID):
    base=shell_from_gaussian_samples(1100,seed=BASE_SEED,grid=grid)
    R=Rotation.from_euler("xyz",[12.,25.,-7.],degrees=True).as_matrix()
    center=np.asarray(base.mesh.center_mass,float)
    # Rotate around center, as opposed to origin.
    rot_shift=center-R@center
    transformations={
        "identity":transform_shell(base),
        "translation":transform_shell(base,translation=[.4,-.3,.2]),
        "expansion":transform_shell(base,matrix=np.eye(3)*1.1,translation=center-1.1*center),
        "rotation":transform_shell(base,matrix=R,translation=rot_shift),
        "anisotropic":transform_shell(base,matrix=np.diag([1.18,.78,1.])),
        "combined":transform_shell(base,matrix=R@np.diag([1.18,.78,1.]),translation=[.4,-.3,.2]),
    }
    rows=[]
    for j,(name,obj) in enumerate(transformations.items()):
        result=signature(base,obj,seed=BASE_SEED+100+j)
        result["case"]=name
        rows.append(result)
    save_results(rows,outdir)
    return rows


def save_results(rows,outdir):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"assinaturas.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
    cols=["case","window_end","signature_complete","valid","translation_norm",
          "delta_log_volume","theta_deg","distance_256","distance_512",
          "relative_256_512_gap","D_A","D_B","delta_D","errors"]
    with (outdir/"assinaturas.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for d in rows:
            writer.writerow({k:json.dumps(d[k],ensure_ascii=False) if k=="errors" else d.get(k) for k in cols})


def analyze_csv(file,outdir,window=1500,stride=None,grid=GRID,limit=None):
    """Analyze historical closed-bar CSV in M11 original 30%/35%/35% mode."""
    if window<480:raise ValueError("window must be >=480")
    stride=window if stride is None else stride
    if stride<1:raise ValueError("stride must be positive")
    df=pd.read_csv(file)
    xyz=flow_coordinates(df)
    rows=[]
    for t in range(window-1,len(xyz),stride):
        if limit is not None and len(rows)>=limit:break
        part=xyz[t+1-window:t+1]
        row={"window_end":int(t),"window_start":int(t+1-window),"valid":False,
             "signature_complete":False,"errors":[]}
        try:
            if not np.isfinite(part).all():raise ValueError("nonfinite coordinates / insufficient causal warmup")
            a,b=split_historical(part)
            seed=BASE_SEED+len(rows)*17
            A=build_shell(a,seed,grid)
            B=build_shell(b,seed+1,grid)
            row.update(signature(A,B,seed+2))
            row["window_end"]=int(t)
            row["window_start"]=int(t+1-window)
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as exc:
            row["errors"].append(str(exc))
        rows.append(row)
    if not rows:raise ValueError("No windows analyzed")
    save_results(rows,outdir)
    return rows


def main():
    p=argparse.ArgumentParser(description="SGV-M11-I: same-shell geometric transformation signature")
    sub=p.add_subparsers(dest="mode",required=True)
    d=sub.add_parser("demo",help="Synthetic known transformations; never BTC")
    d.add_argument("--out",default="resultados_m11i_demo")
    d.add_argument("--grid",type=int,default=GRID)
    c=sub.add_parser("csv",help="Historical closed bar CSV: close,volume,taker_buy,timestamp")
    c.add_argument("file")
    c.add_argument("--out",default="resultados_m11i_csv")
    c.add_argument("--window",type=int,default=1500)
    c.add_argument("--stride",type=int)
    c.add_argument("--grid",type=int,default=GRID)
    c.add_argument("--limit",type=int,default=6)
    args=p.parse_args()
    if args.mode=="demo":rows=demo(Path(args.out),grid=args.grid)
    else:rows=analyze_csv(args.file,Path(args.out),args.window,args.stride,args.grid,args.limit)
    print(json.dumps({"mode":args.mode,"n":len(rows),"complete":sum(r.get("signature_complete",False) for r in rows),
                      "cases":[(r.get("case",r.get("window_end")),round(r.get("distance_512") or 0,6),r.get("errors",[])) for r in rows]},ensure_ascii=False))


if __name__=="__main__":main()
