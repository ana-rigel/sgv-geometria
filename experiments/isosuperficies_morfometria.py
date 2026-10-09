#!/usr/bin/env python3
"""SGV — isosuperficies HDR 3D, morfometria e movimentos de forma.

Reconstrucao de p(z, iota, nu) em janela historica FECHADA. A CDF dos
primeiros 30% define coordenadas; as duas metades subsequentes compartilham
a mesma transformacao causal. HDR25/50/75 sao LIMIARES de p, NAO valores
de p 0.25/0.50/0.75. Marching Cubes extrai p(x)=tau_alpha.

Objetos geometricos de densidade observacional, NAO curvatura intrinseca
Fisher–Rao, fluxo causal nem um mecanismo financeiro novo. Metrica geometrica
e sensivel a transformacao de coordenadas e resolucao da malha.

Portas obrigatorias para inferir volume e genero: superficie fechada,
ausencia de truncamento na borda, orientacao consistente, massa suficiente
capturada no cubo e convergencia numerica. Caso contrario valores anulados.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
from sklearn.mixture import GaussianMixture
from scipy.stats import multivariate_normal
import trimesh

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEVELS = (0.25, 0.50, 0.75)
RANGE = 3.5
RESOLUTION = 35
RESOLUTION_CHECK = 49
MIN_COVERAGE = 0.95
SEED = 20261009
WINDOW = {"1m": 1500, "1h": 1008}
STEP = {"1m": 60000, "1h": 3600000}
MAX_WINDOWS = 6
CHECK_WINDOWS = 2


def make_grid(n=RESOLUTION, extent=RANGE):
    if n < 15 or n % 2 == 0 or extent <= 0:
        raise ValueError("Grade impar >=15 e dominio positivo")
    spacing = 2 * extent / (n - 1)
    axis = np.linspace(-extent, extent, n)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    return np.column_stack([x.ravel(), y.ravel(), z.ravel()]), spacing


def density_values(sample, points, kind, seed=SEED):
    x = np.asarray(sample, float)
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 90 or not np.isfinite(x).all():
        raise ValueError("Dados 3D insuficientes ou invalidos")
    if kind == "gaussian":
        cov = np.cov(x, rowvar=False) + np.eye(3) * 1e-4
        out = multivariate_normal.pdf(points, mean=x.mean(axis=0), cov=cov)
    elif kind == "mixture":
        m = GaussianMixture(n_components=2, covariance_type="full",
                            reg_covar=1e-4, max_iter=100,
                            n_init=2, random_state=seed)
        m.fit(x)
        out = np.exp(m.score_samples(points))
    else:
        raise ValueError("Modelo invalido")
    return np.asarray(out, float)


def hdr_thresholds(density, spacing, levels=LEVELS):
    """HDR com massa ALVO CONDICIONAL ao dominio finito da grade."""
    p = np.asarray(density, float)
    if p.ndim != 3 or not np.isfinite(p).all() or np.any(p < 0) or not p.sum() > 0:
        raise ValueError("Densidade em grade 3D invalida")
    total_mass = float(p.sum() * spacing ** 3)
    ordered = np.sort(p.ravel())[::-1]
    fractions = np.cumsum(ordered) / ordered.sum()
    results = {}
    for alpha in levels:
        if not (0 < alpha < 1):
            raise ValueError("HDR alpha invalido")
        idx = int(np.searchsorted(fractions, alpha, side="left"))
        if idx + 1 >= len(ordered):
            raise ValueError("HDR impossivel")
        # Limiar suave entre dois niveis discretos: evitar triangulacao
        # degenerada exatamente no valor de algum vertice da grade.
        tau = float((ordered[idx] + ordered[idx+1]) / 2.)
        if not p.min() < tau < p.max():
            raise ValueError("Iso nivel nao contido no campo")
        realized = float(p[p > tau].sum() / p.sum())
        results[alpha] = {"tau": tau, "mass_in_grid": realized}
    return results, total_mass


def mesh_topology(vertices, faces):
    """V,E,F, chi e genus por componente; valido SOMENTE se fechado."""
    n = len(vertices)
    f = np.asarray(faces, int)
    edges = np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    edges = np.sort(edges, axis=1)
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    closed = bool(np.all(counts == 2))
    adjacency = coo_matrix((np.ones(2 * len(unique), dtype=np.int8),
                  (np.r_[unique[:,0], unique[:,1]],
                   np.r_[unique[:,1], unique[:,0]])), shape=(n, n)).tocsr()
    ncomp, labels = connected_components(adjacency, directed=False)
    nv = np.bincount(labels, minlength=ncomp)
    ne = np.bincount(labels[unique[:,0]], minlength=ncomp)
    nf = np.bincount(labels[f[:,0]], minlength=ncomp)
    chi = nv - ne + nf
    genera = []
    for c in chi:
        g = (2-int(c))/2.
        genera.append(int(round(g)) if closed and g>=0 and abs(g-round(g))<1e-7
                      else None)
    return {"closed_edges": closed, "n_components": int(ncomp),
            "euler_components": [int(x) for x in chi] if closed else None,
            "genus_components": genera if closed else None,
            "edges_bad": int(np.count_nonzero(counts != 2))}


def curvatures(vertices, faces):
    """Curvaturas EXTRINSECAS discretas por deficit angular e Laplace-cot.

    K_i = (2*pi - soma angulos das faces em i)/A_i para malha fechada.
    H_i em modulo = ||L_cot(x_i)||/2. Area dual BARICENTRICA A_i.
    Valores em malha poligonal podem mudar sob refinamento.
    """
    v = np.asarray(vertices, float)
    f = np.asarray(faces, np.int64)
    tri = v[f]  # (F,3,3)
    edges1 = tri[:,1] - tri[:,0]
    edges2 = tri[:,2] - tri[:,0]
    norm = np.linalg.norm(np.cross(edges1, edges2), axis=1)
    if np.any(norm <= 1e-14):
        raise ValueError("Triangulos degenerados")
    areas = norm * 0.5
    Ai = np.zeros(len(v))
    angles = np.zeros(len(v))
    lap = np.zeros_like(v)
    for vertex in range(3):
        i=f[:,vertex]
        j=f[:,(vertex+1)%3]
        k=f[:,(vertex+2)%3]
        u=v[j]-v[i]
        w=v[k]-v[i]
        cos = np.sum(u*w, axis=1) / (
            np.maximum(np.linalg.norm(u,axis=1)*np.linalg.norm(w,axis=1),1e-16))
        theta = np.arccos(np.clip(cos,-1,1))
        np.add.at(angles,i,theta)
        np.add.at(Ai,i,areas/3.)
        cot = np.sum(u*w,axis=1)/norm
        # The corner angle at i contributes to edge (j,k).
        np.add.at(lap,j,cot[:,None]*(v[k]-v[j]))
        np.add.at(lap,k,cot[:,None]*(v[j]-v[k]))
    K = (2*np.pi - angles) / np.maximum(Ai,1e-14)
    Habs = np.linalg.norm(lap/(2*np.maximum(Ai[:,None],1e-14)),axis=1)/2.
    return K,Habs,Ai


def extract_mesh(field, tau, spacing, extent=RANGE):
    p=np.asarray(field,float)
    if p.ndim!=3 or len(set(p.shape))!=1 or not np.isfinite(p).all():
        raise ValueError("Campo 3D cubico invalido")
    if not p.min()<tau<p.max():
        raise ValueError("Limiar sem isosuperficie")
    # Uma isosuperficie com probabilidade alta na borda sera aberta/truncada.
    border = np.zeros(p.shape,bool)
    for ax in range(3):
        first=[slice(None)]*3; last=[slice(None)]*3
        first[ax]=0; last[ax]=-1
        border[tuple(first)] = True; border[tuple(last)] = True
    touches_field_border = bool(np.any(p[border]>=tau))
    verts, faces, _, _ = marching_cubes(
        p.astype(np.float32), level=float(tau),
        spacing=(spacing,spacing,spacing),allow_degenerate=False)
    verts = np.asarray(verts,float) - extent
    faces = np.asarray(faces,int)
    touches_vertices_border=bool(np.any(
        np.isclose(np.abs(verts),extent,atol=spacing*.02)))
    return trimesh.Trimesh(vertices=verts,faces=faces,process=False), (
        touches_field_border or touches_vertices_border)


def describe_mesh(mesh, *, truncated=False, coverage=1., min_coverage=MIN_COVERAGE):
    v=np.asarray(mesh.vertices,float)
    f=np.asarray(mesh.faces,int)
    top=mesh_topology(v,f)
    enough_mass=bool(coverage>=min_coverage and coverage<=1.05)
    accepted=bool(top["closed_edges"] and not truncated and enough_mass)
    result={
        "n_vertices":int(len(v)),"n_triangles":int(len(f)),
        "components":top["n_components"],
        "watertight":top["closed_edges"],
        "truncated":bool(truncated),
        "coverage_domain":float(coverage),
        "coverage_valid":enough_mass,
        "quality_pass":accepted,
        "invalid_reason":None if accepted else (
            "open_mesh" if not top["closed_edges"] else
            "boundary_truncation" if truncated else "insufficient_coverage"),
        "euler_components":top["euler_components"] if accepted else None,
        "genus_components":top["genus_components"] if accepted else None,
        "volume":None,"area":None,"center":None,
        "isoperimetric_quotient":None,"negative_K_area_fraction":None,
        "robust_negative_K_area_fraction":None,
        "K_median":None,"H_abs_median":None,
        "gauss_bonnet_relative_error":None,"orientation_gap":None,
    }
    if not accepted:
        return result
    m=mesh.copy()
    m.fix_normals()
    volume=float(abs(m.volume))
    area=float(m.area)
    center=np.asarray(m.center_mass,float)
    if not (volume>1e-10 and area>1e-9 and np.isfinite(center).all()):
        result["quality_pass"]=False
        result["invalid_reason"]="invalid_volume_or_centroid"
        return result
    result.update({"volume":volume,"area":area,
                   "center":[float(x) for x in center],
                   "isoperimetric_quotient":float(36*np.pi*volume**2/area**3)})
    K,H,Ai=curvatures(v,f)
    req=(3*volume/(4*np.pi))**(1/3)
    threshold=-0.1 / max(req**2,1e-12)
    integral=float(np.sum(K*Ai))
    chi=sum(top["euler_components"])
    result.update({
        "negative_K_area_fraction":float(Ai[K<0].sum()/Ai.sum()),
        "robust_negative_K_area_fraction":float(Ai[K<threshold].sum()/Ai.sum()),
        "K_median":float(np.median(K)),
        "H_abs_median":float(np.median(H)),
        "gauss_bonnet_relative_error":float(abs(integral-2*np.pi*chi)/
                                                max(2*np.pi,abs(2*np.pi*chi))),
    })
    # Orientation = eigensystem of the SOLID inertia tensor, not moments
    # of vertices (vertex density would bias the principal axes).
    tensor=np.asarray(m.moment_inertia,float)
    geom_cov=((np.trace(tensor)/2)*np.eye(3)-tensor)/volume
    vals,_=np.linalg.eigh(geom_cov)
    vals=np.sort(vals)[::-1]
    if vals[-1]>0:
        gap=float(np.min((vals[:-1]-vals[1:])/max(vals[0],1e-12)))
        result["orientation_gap"]=gap
        result["principal_variances"]=[float(x) for x in vals]
    return result


def principal_axes(mesh):
    m=mesh.copy()
    m.fix_normals()
    volume=float(abs(m.volume))
    I=np.asarray(m.moment_inertia,float)
    cov=((np.trace(I)/2)*np.eye(3)-I)/volume
    w,Q=np.linalg.eigh(cov)
    order=np.argsort(w)[::-1]
    w,Q=w[order],Q[:,order]
    if np.linalg.det(Q)<0:Q[:,-1]*=-1
    gap=float(np.min((w[:-1]-w[1:])/max(w[0],1e-12)))
    if w[-1]<=0 or gap<0.07:
        return None,gap
    return Q,gap


def motion(mesh_a, props_a, mesh_b, props_b, seed=SEED):
    """Rigid+escala global + residuo de Chamfer sem correspondencia de vertices."""
    if not props_a["quality_pass"] or not props_b["quality_pass"]:
        return {"quality_pass":False,"reason":"invalid_isosurface"}
    ca=np.array(props_a["center"],float)
    cb=np.array(props_b["center"],float)
    va,vb=props_a["volume"],props_b["volume"]
    ratio=vb/va
    center_d=cb-ca
    out={"quality_pass":True,"translation_vector":[float(x) for x in center_d],
         "translation_norm":float(np.linalg.norm(center_d)),
         "volume_ratio":float(ratio),
         "volume_log_change":float(np.log(ratio)),
         "isotropic_scale":float(ratio**(1/3)),
         "rotation_angle_deg":None,
         "chamfer_residual_normalized":None,
         "orientation_identifiable":False,
         "warning":"Mudancas em coordenadas z, iota, nu; nao movimento direcional puro do preco"}
    Qa,ga=principal_axes(mesh_a)
    Qb,gb=principal_axes(mesh_b)
    if Qa is None or Qb is None:
        out["reason"]="near_degenerate_inertia_axes"
        return out
    sa,_=trimesh.sample.sample_surface(mesh_a,600,seed=seed)
    sb,_=trimesh.sample.sample_surface(mesh_b,600,seed=seed+1)
    rad_a=(3*va/(4*np.pi))**(1/3)
    rad_b=(3*vb/(4*np.pi))**(1/3)
    xa=(sa-ca)@Qa/rad_a
    sign_sets=((1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1))
    candidates=[]
    for signs in sign_sets:
        D=np.diag(signs)
        xb=(sb-cb)@Qb@D/rad_b
        da=cKDTree(xb).query(xa)[0]
        db=cKDTree(xa).query(xb)[0]
        ch=float((da.mean()+db.mean())/2)
        R=Qb@D@Qa.T
        angle=float(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))))
        candidates.append((ch,angle))
    ch,angle=min(candidates,key=lambda a:a[0])
    out.update({"rotation_angle_deg":angle,
                "chamfer_residual_normalized":ch,
                "orientation_identifiable":True,
                "warning":"Rotacao depende de eixos principais identificaveis; "
                          "residuo apos translação/escala/alinhamento, "
                          "nao deformacao material causal"})
    return out


def analytic_field(kind, n=61, extent=RANGE):
    pts,spacing=make_grid(n,extent)
    x,y,z=pts.T
    if kind=="sphere":
        f=np.exp(-(x*x+y*y+z*z)/2)
        level=float(np.exp(-.5))
    elif kind=="torus":
        R,tube=1.5,0.42
        f=np.exp(-((np.hypot(x,y)-R)**2+z*z)/(2*tube**2))
        level=float(np.exp(-.5))
    elif kind=="two_spheres":
        sig=.42
        f=np.exp(-((x-1.45)**2+y*y+z*z)/(2*sig**2)) + \
          np.exp(-((x+1.45)**2+y*y+z*z)/(2*sig**2))
        level=float(np.exp(-.5))
    elif kind=="clipped":
        f=np.exp(-((x-extent+.35)**2+y*y+z*z)/2)
        level=float(np.exp(-.5))
    else:
        raise ValueError(kind)
    return f.reshape(n,n,n),level,spacing


def evaluate_window(x,n=RESOLUTION,seed=SEED):
    """A e B sao estados posteriores a ancora. Eixos identicos entre A/B."""
    # Import somente quando avaliado, evita dependencia da base para testes
    # matematicos de campos analiticos.
    from experiments.precisao_formas_3d import split_historical
    a,b=split_historical(x)
    points,dx=make_grid(n)
    output={}
    surfaces={}
    for model in ("gaussian","mixture"):
        for half,sample in (("a",a),("b",b)):
            d=density_values(sample,points,model,seed+(half=="b"))
            field=d.reshape(n,n,n)
            thresholds,coverage=hdr_thresholds(field,dx)
            for alpha in LEVELS:
                tau=thresholds[alpha]["tau"]
                mesh,truncated=extract_mesh(field,tau,dx)
                properties=describe_mesh(mesh,truncated=truncated,coverage=coverage)
                properties["threshold_tau"]=tau
                properties["actual_mass_in_grid"]=thresholds[alpha]["mass_in_grid"]
                key=f"{model}_{half}_{int(alpha*100)}"
                output[key]=properties
                surfaces[key]=mesh
        for alpha in LEVELS:
            k=int(alpha*100)
            key=f"{model}_motion_{k}"
            output[key]=motion(surfaces[f"{model}_a_{k}"],
                               output[f"{model}_a_{k}"],
                               surfaces[f"{model}_b_{k}"],
                               output[f"{model}_b_{k}"],seed=seed+k)
    return output,surfaces


def analyze_synthetic():
    report={}
    for kind in ("sphere","torus","two_spheres","clipped"):
        field,level,spacing=analytic_field(kind)
        mesh,truncated=extract_mesh(field,level,spacing)
        data=describe_mesh(mesh,truncated=truncated,
                           coverage=1.)
        report[kind]=data
    return {"status":"ISOSUPERFICIES_CALIBRACAO",
            "synthetic_fields":report,
            "expected":["sphere: genus 0, positive K mostly",
                        "torus: genus 1 AND negative K without lobes",
                        "two_spheres: two components, genus 0 each",
                        "clipped: explicit rejection of genus and volume"]}


def export_scene(surfaces,output,folder,name):
    """GLB com duas fotografias lado a lado; medidas nunca usam a translacao."""
    scene=trimesh.Scene()
    shades={25:(35,162,206,70),50:(85,104,223,110),75:(42,180,124,55)}
    for half,shift in (("a",-4.5),("b",4.5)):
        for level in (75,50,25):
            key=f"mixture_{half}_{level}"
            if not output[key]["quality_pass"]:
                continue
            m=surfaces[key].copy()
            m.apply_translation([shift,0,0])
            m.visual.face_colors=shades[level]
            scene.add_geometry(m,node_name=f"{half}_HDR{level}",geom_name=key)
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/f"{name}_isosuperficies.glb"
    if len(scene.geometry):
        scene.export(str(path))
        return str(path.name)
    return None


def run_real(interval):
    from experiments.persistencia_dependencia import checked_exploratory_month
    from sgvgeo.data import load_binance_klines
    from sgvgeo.flow import flow_coordinates
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths:
        raise FileNotFoundError("Dados BTC exploratorios nao encontrados")
    for path in paths:
        checked_exploratory_month(path.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    flow=flow_coordinates(df)
    x=flow[["z","iota","nu"]].to_numpy(float)
    ts=df.timestamp.to_numpy(np.int64)
    window=WINDOW[interval]
    candidates=[]
    for end in range(window,len(x)+1,window):
        xx=x[end-window:end]
        tt=ts[end-window:end]
        if not np.isfinite(xx).all() or not np.all(np.diff(tt)==STEP[interval]):
            continue
        candidates.append((end,int(tt[-1]+STEP[interval]),xx))
    if not candidates:raise RuntimeError("Sem janelas continuas")
    # Escolha equiespaciada feita sem consultar formas.
    selected=np.linspace(0,len(candidates)-1,min(MAX_WINDOWS,len(candidates)),dtype=int)
    checkidx=set(np.linspace(0,len(selected)-1,
                            min(CHECK_WINDOWS,len(selected)),dtype=int))
    rows=[]
    assets=ROOT/"reports"/f"ISOMESH_{interval}"
    all_quality=[]
    for j,which in enumerate(selected):
        end,asof,xx=candidates[int(which)]
        data,meshes=evaluate_window(xx,n=RESOLUTION,seed=SEED+end)
        extra={}
        if j in checkidx:
            larger,_=evaluate_window(xx,n=RESOLUTION_CHECK,seed=SEED+end)
            for key in data:
                if "_motion_" in key:
                    extra[key+"_delta_chamfer_resolution"]=(None
                         if data[key]["chamfer_residual_normalized"] is None
                         or larger[key]["chamfer_residual_normalized"] is None
                         else float(larger[key]["chamfer_residual_normalized"]-
                                   data[key]["chamfer_residual_normalized"]))
                else:
                    extra[key+"_topology_stable_resolution"]=bool(
                        data[key]["quality_pass"] and larger[key]["quality_pass"]
                        and data[key]["euler_components"]==
                            larger[key]["euler_components"]
                        and data[key]["genus_components"]==
                            larger[key]["genus_components"])
        if j==len(selected)-1:
            export_scene(meshes,data,assets,interval)
        for key,record in data.items():
            row={"window_index":int(which),"asof_ms":int(asof),
                 "region":key,"resolution":RESOLUTION,
                 "resolution_checked":j in checkidx,**record}
            if extra:
                tag=key+("_delta_chamfer_resolution" if "_motion_" in key
                         else "_topology_stable_resolution")
                row["resolution_result"]=extra.get(tag)
            rows.append(row)
        all_quality.append(data)
    out=ROOT/"reports"/f"ISOSUPERFICIES_{interval}_medidas.csv"
    out.parent.mkdir(parents=True,exist_ok=True)
    # CSV serializa estruturas ricas como JSON, nao as modifica.
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with out.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list))
                             else v for k,v in r.items()})
    n_mesh=sum("motion" not in key for snapshot in all_quality for key in snapshot)
    valid=sum(v["quality_pass"] for snapshot in all_quality
              for key,v in snapshot.items() if "motion" not in key)
    output={"status":"ISOSUPERFICIES_MORFOMETRIA_EXPLORATORIA",
      "timeframe":interval,"ativo":"BTCUSDT spot",
      "periodo_confirmatorio_lido":False,
      "n_candidatas_validas":len(candidates),
      "n_fotografias_pares":len(all_quality),
      "n_isosuperficies":n_mesh,"n_isosuperficies_validas":int(valid),
      "n_testes_resolucao":len(checkidx),"hdr":list(LEVELS),
      "grades":[RESOLUTION,RESOLUTION_CHECK],
      "centroide_escala":"scores de postos nas tres coordenadas SGV",
      "superficie_real_glb":str((assets/f"{interval}_isosuperficies.glb").exists()),
      "estatisticas":{},"limites":[
         "Morfologia extrinseca da densidade, NAO curvatura intrinseca Fisher–Rao",
         "Raio de curvatura, area e volume dependem das unidades e dos scores gaussianizados",
         "HDR condicionada ao cubo; gate minimo de massa de 95%",
         "Curvatura negativa nao prova lobulos; genero exige malha fechada",
         "Orientacao e indefinida se tensor de inercia tem autovalores quase iguais",
         "Residuos de deformacao nao sao transporte de massa nem movimentos materiais",
         "Seis janelas equiespacadas exploratorias, sem teste estatistico de persistencia",
         "Precisao em streaming real prolongado permanece nao demonstrada",
      ]}
    for model in ("gaussian","mixture"):
        for k in (25,50,75):
            items=[snap[f"{model}_a_{k}"] for snap in all_quality]+[
                   snap[f"{model}_b_{k}"] for snap in all_quality]
            accepted=[p for p in items if p["quality_pass"]]
            mov=[s[f"{model}_motion_{k}"] for s in all_quality]
            motions=[m for m in mov if m["quality_pass"]]
            output["estatisticas"][f"{model}_HDR{k}"]={
               "n_surf_validas":len(accepted),"n_surf_total":len(items),
               "n_mov_validos":len(motions),
               "fracao_multicomponente":float(np.mean([
                   p["components"]>1 for p in accepted])) if accepted else None,
               "fracao_genus_positive":float(np.mean([
                   any(g is not None and g>0 for g in p["genus_components"])
                   for p in accepted])) if accepted else None,
               "K_negativo_area_mediana":float(np.median([
                   p["negative_K_area_fraction"] for p in accepted]))
                   if accepted else None,
               "volume_mediano":float(np.median([
                   p["volume"] for p in accepted])) if accepted else None,
               "deslocamento_mediano":float(np.median([
                   m["translation_norm"] for m in motions])) if motions else None,
               "escala_isotropica_mediana":float(np.median([
                   m["isotropic_scale"] for m in motions])) if motions else None,
               "deformacao_chamfer_mediana":float(np.median([
                   m["chamfer_residual_normalized"] for m in motions
                   if m["chamfer_residual_normalized"] is not None]))
                   if any(m["chamfer_residual_normalized"] is not None
                          for m in motions) else None,
            }
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--interval",choices=("synthetic","1m","1h"),required=True)
    args=p.parse_args()
    result=analyze_synthetic() if args.interval=="synthetic" else run_real(args.interval)
    path=ROOT/"reports"/f"ISOSUPERFICIES_{args.interval}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
