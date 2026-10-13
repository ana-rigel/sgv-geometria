"""SGV M11-I — integração fiel dos instrumentos M2/M8/M9/M11.

Uma superfície HDR50 GMM2 por fotografia A/B. Engenharia sintética, não
preregistro financeiro. Dependências são módulos históricos no repo.
"""
from __future__ import annotations
import argparse, json, csv, sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

from experiments.precisao_formas_3d import split_historical
from experiments.isosuperficies_morfometria import (
    make_grid,density_values,hdr_thresholds,extract_mesh,describe_mesh,
    implicit_curvatures,curvatures)
from experiments.m9_registro_simetrico_3d import quotient_axis_angle, normalized_mesh_points,icp_fit,initial_rotations
from experiments.m11_distancia_superficie_nulos import normalize_mesh,direct_distance
from sgvgeo.flow import flow_coordinates
from sgvgeo.data import load_binance_klines

SEED=20261009

def one_shell(sample,seed,n=35):
    """Retorna mesh, parâmetros GMM e propriedades sobre o MESMO fit."""
    grid,dx=make_grid(n)
    dens,model=density_values(sample,grid,"mixture",seed,with_model=True)
    field=dens.reshape((n,n,n))
    levels,coverage=hdr_thresholds(field,dx)
    mesh,truncated=extract_mesh(field,levels[.5]["tau"],dx)
    props=describe_mesh(mesh,truncated=truncated,coverage=coverage,implicit_model=model)
    if not props["quality_pass"]:
        raise ValueError("invalid_shell: "+str(props["invalid_reason"]))
    return mesh,model,props

def D_index(mesh,model):
    K,_=implicit_curvatures(mesh.vertices,model)
    _,_,areas=curvatures(mesh.vertices,mesh.faces)
    vol=abs(float(mesh.volume))
    r=(3*vol/(4*np.pi))**(1/3)
    D=float(np.average(np.maximum(0.,-K*r*r),weights=areas))
    frac=float(areas[K<0].sum()/areas.sum())
    return D,frac

def residual_M11(ma,mb,seed=SEED):
    """Distância ponto→triângulo do M11; registrar ICP+auditoria axis."""
    A=normalize_mesh(ma)
    B=normalize_mesh(mb)
    xa=normalized_mesh_points(A,360,seed)
    xb=normalized_mesh_points(B,360,seed+1)
    R,training=icp_fit(xa,xb,initial_rotations(A,B))
    options=[("icp",R)]
    from experiments.isosuperficies_morfometria import principal_axes
    qa,_=principal_axes(A);qb,_=principal_axes(B)
    if qa is not None and qb is not None:
        for signs in ((1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)):
            options.append(("axis_quotient",qb@np.diag(signs)@qa.T))
    scores=[]
    for method,r in options:
        b=B.copy()
        T=np.eye(4);T[:3,:3]=r.T
        b.apply_transform(T)
        scores.append((direct_distance(A,b,64)["symmetric"],method,r))
    audit,method,R=min(scores,key=lambda a:a[0])
    T=np.eye(4);T[:3,:3]=R.T
    B.apply_transform(T)
    q={str(n):direct_distance(A,B,n) for n in (256,512)}
    return {"distance_256":float(q["256"]["symmetric"]),
            "distance_512":float(q["512"]["symmetric"]),
            "directed_ab":float(q["512"]["a_to_b"]),
            "directed_ba":float(q["512"]["b_to_a"]),
            "relative_256_512_gap":float(abs(q["256"]["symmetric"]-q["512"]["symmetric"])/max(.01,q["512"]["symmetric"])),
            "icp_training_chamfer":float(training),
            "registration_audit_d64":float(audit),
            "registration_method":method}

def integrate_meshes(ma,mb,model_a=None,model_b=None,seed=SEED):
    """Mesmo par de malhas para translação, escala, ângulo, curvatura e M11."""
    out={"valid":False,"signature_complete":False,"errors":[]}
    if not (ma.is_watertight and mb.is_watertight):
        return {**out,"errors":["open_mesh"]}
    aa=ma.copy();bb=mb.copy()
    aa.fix_normals();bb.fix_normals()
    va=abs(float(aa.volume));vb=abs(float(bb.volume))
    if min(va,vb)<1e-10:return {**out,"errors":["degenerate_volume"]}
    ca=np.asarray(aa.center_mass,float);cb=np.asarray(bb.center_mass,float)
    dc=cb-ca
    theta,diag=quotient_axis_angle(aa,bb)
    out.update({"valid":True,"delta_center":dc.tolist(),
        "translation_norm":float(np.linalg.norm(dc)),
        "volume_A":va,"volume_B":vb,
        "volume_ratio":vb/va,
        "delta_log_volume":float(np.log(vb/va)),
        "isotropic_scale":float((vb/va)**(1/3)),
        "theta_deg":theta,**diag})
    try:
        out.update(residual_M11(aa,bb,seed))
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
        out["errors"].append("registration:"+str(e))
    if model_a is not None and model_b is not None:
        try:
            da,fa=D_index(aa,model_a);db,fb=D_index(bb,model_b)
            out.update({"D_A":da,"D_B":db,"delta_D":db-da,
                        "K_negative_area_A":fa,"K_negative_area_B":fb})
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
            out["errors"].append("curvature:"+str(e))
    else:
        out.update({"D_A":None,"D_B":None,"delta_D":None,
                    "curvature_status":"unavailable_no_density_model"})
    out["signature_complete"]=(theta is not None and
        out.get("distance_512") is not None and out.get("delta_D") is not None)
    out["G"]=dc.tolist()+[out["delta_log_volume"],theta,out.get("distance_512"),
                              out.get("D_A"),out.get("D_B"),out.get("delta_D")]
    return out

def integrate_samples(sample_a,sample_b,seed=SEED,grid=35):
    ma,pa,meta_a=one_shell(sample_a,seed,grid)
    mb,pb,meta_b=one_shell(sample_b,seed+1,grid)
    output=integrate_meshes(ma,mb,pa,pb,seed+2)
    output.update({"coverage_A":meta_a["coverage_domain"],
                   "coverage_B":meta_b["coverage_domain"],
                   "grid":grid,"seed":seed})
    return output

def integrate_window(x,seed=SEED,grid=35):
    a,b=split_historical(np.asarray(x,float))
    return integrate_samples(a,b,seed,grid)

def synthetic():
    """Controles conhecidos de malha. Curvatura indisponível: não fingir GMM."""
    sphere=trimesh.creation.icosphere(subdivisions=3)
    ellipsoid=trimesh.creation.icosphere(subdivisions=3)
    ellipsoid.apply_scale([1.5,1.0,.65])
    cases=[]
    for name,mat,translation in [
        ("identity",np.eye(3),[0,0,0]),
        ("translation",np.eye(3),[.4,-.3,.2]),
        ("isotropic",np.eye(3)*1.1,[0,0,0]),
        ("rotation",Rotation.from_euler("z",25,degrees=True).as_matrix(),[0,0,0]),
        ("anisotropic",np.diag([1.18,.78,1.]),[0,0,0])]:
        b=ellipsoid.copy()
        T=np.eye(4);T[:3,:3]=mat;T[:3,3]=translation
        b.apply_transform(T)
        got=integrate_meshes(ellipsoid,b,seed=SEED)
        got["case"]=name
        cases.append(got)
    s=sphere.copy();s.apply_transform(Rotation.from_euler("x",48,degrees=True).as_matrix())
    got=integrate_meshes(sphere,s,seed=SEED);got["case"]="sphere_unidentifiable";cases.append(got)
    return cases

def export(rows,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"assinaturas.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    keys=["case","index","valid","signature_complete","translation_norm",
          "delta_log_volume","theta_deg","distance_256","distance_512",
          "D_A","D_B","delta_D"]
    with (out/"assinaturas.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        for row in rows:writer.writerow({k:row.get(k) for k in keys})

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--synthetic",action="store_true")
    p.add_argument("--csv",type=Path)
    p.add_argument("--window",type=int,default=1500)
    p.add_argument("--stride",type=int,default=1500)
    p.add_argument("--limit",type=int,default=6)
    p.add_argument("--out",type=Path,default=Path("reports/m11i/outputs"))
    args=p.parse_args()
    if args.synthetic: rows=synthetic()
    elif args.csv:
        import pandas as pd
        df=pd.read_csv(args.csv)
        coords=flow_coordinates(df)[["z","iota","nu"]].to_numpy(float)
        rows=[]
        for i in range(args.window-1,len(coords),args.stride):
            if len(rows)>=args.limit:break
            window=coords[i+1-args.window:i+1]
            try:
                if not np.isfinite(window).all():raise ValueError("causal_warmup")
                r=integrate_window(window,SEED+len(rows)*3)
            except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
                r={"valid":False,"signature_complete":False,"errors":[str(e)]}
            r["index"]=int(i);rows.append(r)
    else:p.error("Choose --synthetic or --csv")
    export(rows,args.out)
    print(json.dumps({"n":len(rows),"valid":sum(r.get("valid",False) for r in rows),
        "full":sum(r.get("signature_complete",False) for r in rows)},ensure_ascii=False))

if __name__=="__main__":main()
