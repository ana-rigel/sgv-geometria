#!/usr/bin/env python3
"""SGV -- precisao das superfícies tridimensionais dos observáveis.

Fotografa distribuição estimada de (z, iota, nu) em janela HISTÓRICA fechada:
30% inicial ancora a transformação marginal, 35% e 35% finais são duas
subjanelas cronológicas, com a MESMA transformação baseada só na ancora.
Contrasta GMM2 e gaussiana 3D em regiões HDR de 25%, 50% e 75% da massa
NUMERICA DA GRADE, com conectividade 26 vizinhos.

Bootstrap em blocos:
- Reamostra dentro de cada metade para ver flutuação da fotografia.
- Reamostra de A|B combinado para nulo APROXIMADO de mesma distribuição;
  se houve regime, o pool incorpora o regime. P nominais, não confirmatórios.
- Distribuições são condições à janela, grade e transformação de coordenadas.
- Não mede curvatura intrínseca do manifold de Fisher nem informação causal.
- Somente BTC exploratório autorizado, NUNCA períodos confirmatórios.

Uso:
python experiments/precisao_formas_3d.py --interval synthetic|1m|1h
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
import numpy as np
from scipy.ndimage import label
from scipy.special import ndtri
from scipy.stats import multivariate_normal
from sklearn.mixture import GaussianMixture

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from experiments.persistencia_dependencia import checked_exploratory_month, synthetic_one
from experiments.precisao_trajetorias import draw_blocks
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates, default_sf1, simulate_sf1

WIN={"1m":1500,"1h":1008}
STEP={"1m":60000,"1h":3600000}
BLOCK={"1m":15,"1h":12}
GRID_N=21
GRID_CHECK_N=27
GRID_RANGE=3.0
MASSES=(.25,.50,.75)
RIDGE=1.e-4
BOOT_REPS=29
BOOT_WINDOWS=8
SEED=20261009


def gaussianize_three(anchor, future):
    a=np.asarray(anchor,float)
    x=np.asarray(future,float)
    if a.ndim!=2 or x.ndim!=2 or a.shape[1]!=3 or x.shape[1]!=3 or len(a)<60:
        raise ValueError("Tres dimensoes, ancora de >=60 observacoes")
    if not np.isfinite(a).all() or not np.isfinite(x).all():
        raise ValueError("Observacoes nao finitas")
    result=np.empty_like(x)
    for j in range(3):
        ordered=np.sort(a[:,j])
        left=np.searchsorted(ordered,x[:,j],side="left")
        right=np.searchsorted(ordered,x[:,j],side="right")
        u=(.5*(left+right)+.5)/(len(ordered)+1.)
        result[:,j]=ndtri(np.clip(u,.5/(len(ordered)+1.),(len(ordered)+.5)/(len(ordered)+1.)))
    return result


def split_historical(X):
    x=np.asarray(X,float)
    if x.ndim!=2 or x.shape[1]!=3 or len(x)<480:
        raise ValueError("Janela 3D deve ter >=480 observacoes")
    n_anchor=int(.30*len(x))
    remainder=gaussianize_three(x[:n_anchor],x[n_anchor:])
    half=len(remainder)//2
    if half<120 or len(remainder)-half<120:
        raise ValueError("Metades curtas")
    return remainder[:half],remainder[half:]


def build_grid(n=GRID_N):
    if n<11 or n%2==0:
        raise ValueError("Resolucao precisa ser impar e >=11")
    axis=np.linspace(-GRID_RANGE,GRID_RANGE,n)
    x,y,z=np.meshgrid(axis,axis,axis,indexing="ij")
    return np.column_stack([x.ravel(),y.ravel(),z.ravel()])


def fit_density(x, gridpoints, kind="mixture",seed=SEED):
    x=np.asarray(x,float)
    if x.ndim!=2 or x.shape[1]!=3 or len(x)<90 or not np.isfinite(x).all():
        raise ValueError("Amostra invalida")
    if kind=="mixture":
        model=GaussianMixture(n_components=2,covariance_type="full",
            reg_covar=RIDGE,n_init=2,max_iter=100,random_state=seed)
        model.fit(x)
        values=np.exp(model.score_samples(gridpoints))
    elif kind=="gaussian":
        mu=x.mean(axis=0)
        sigma=np.cov(x,rowvar=False)+RIDGE*np.eye(3)
        values=np.exp(multivariate_normal.logpdf(gridpoints,mean=mu,cov=sigma))
    else:
        raise ValueError("Modelo invalido")
    if not np.isfinite(values).all() or values.sum()<=0:
        raise ValueError("Densidade nao finita")
    return values


def masks_from_density(density,n,masses=MASSES):
    p=np.asarray(density,float).reshape((n,n,n))
    if np.any(p<0) or not np.isfinite(p).all() or p.sum()<=0:
        raise ValueError("Grid invalida")
    prob=p.ravel()/p.sum()
    order=np.argsort(-prob)
    cs=np.cumsum(prob[order])
    out={}
    for mass in masses:
        if not 0<mass<1:
            raise ValueError("Nivel HDR invalido")
        take=int(np.searchsorted(cs,mass,side="left")+1)
        mask=np.zeros(len(prob),bool)
        mask[order[:take]]=True
        out[mass]=mask.reshape((n,n,n))
    spacing=2*GRID_RANGE/(n-1)
    # Aproxima massa total do modelo capturada dentro do cubo; NÃO HDR.
    coverage=float(p.sum()*spacing**3)
    return out,coverage


def topology(mask):
    return int(label(mask,structure=np.ones((3,3,3),int))[1])


def jaccard(a,b):
    union=np.logical_or(a,b).sum()
    return float(np.logical_and(a,b).sum()/union) if union else 1.


def measure_pair(a,b,*,n=GRID_N,seed=SEED):
    g=build_grid(n)
    out={}
    for kind in ("gaussian","mixture"):
        d0=fit_density(a,g,kind,seed)
        d1=fit_density(b,g,kind,seed+1)
        ma,ca=masks_from_density(d0,n)
        mb,cb=masks_from_density(d1,n)
        out[kind]={
            "density_a":ma,"density_b":mb,
            "coverage_a":ca,"coverage_b":cb,
            "components_a":{m:topology(ma[m]) for m in MASSES},
            "components_b":{m:topology(mb[m]) for m in MASSES},
            "jaccard":{m:jaccard(ma[m],mb[m]) for m in MASSES},
        }
    return out


def bootstrap_shape_noise(a,b,*,block,reps=BOOT_REPS,seed=SEED,n=GRID_N):
    """Incerteza de ajuste local e nulo aproximado de igualdade A/B."""
    rng=np.random.default_rng(seed)
    g=build_grid(n)
    reference_a,_=masks_from_density(fit_density(a,g,"mixture",seed),n)
    reference_b,_=masks_from_density(fit_density(b,g,"mixture",seed+1),n)
    obs={m:1-jaccard(reference_a[m],reference_b[m]) for m in MASSES}
    pool=np.concatenate([a,b])
    local={m:[] for m in MASSES}
    null={m:[] for m in MASSES}
    for i in range(reps):
        ia=draw_blocks(rng,len(a),len(a),block,1)[0]
        ib=draw_blocks(rng,len(b),len(b),block,1)[0]
        a0,_=masks_from_density(fit_density(a[ia],g,"mixture",seed+10+i*4),n)
        b0,_=masks_from_density(fit_density(b[ib],g,"mixture",seed+11+i*4),n)
        pa=draw_blocks(rng,len(pool),len(a),block,1)[0]
        pb=draw_blocks(rng,len(pool),len(b),block,1)[0]
        an,_=masks_from_density(fit_density(pool[pa],g,"mixture",seed+12+i*4),n)
        bn,_=masks_from_density(fit_density(pool[pb],g,"mixture",seed+13+i*4),n)
        for m in MASSES:
            local[m].append(.5*((1-jaccard(reference_a[m],a0[m]))+
                                 (1-jaccard(reference_b[m],b0[m]))))
            null[m].append(1-jaccard(an[m],bn[m]))
    result={}
    for m in MASSES:
        q=np.quantile(local[m],[.1,.5,.9])
        n95=float(np.quantile(null[m],.95))
        result[str(int(m*100))]={
            "mudanca_observada_1_menos_jaccard":float(obs[m]),
            "ruido_bootstrap_local_p10_p50_p90":[float(x) for x in q],
            "limiar_nulo_pool_p95":n95,
            "p_exploratorio_pool":float((1+np.sum(np.asarray(null[m])>=obs[m]))/(reps+1)),
            "excede_limiar_pool95":bool(obs[m]>n95),
        }
    return result


def assess_window(x,*,seed=SEED,bootstrap=False,block=15,
                  reps=BOOT_REPS,check_resolution=False):
    a,b=split_historical(x)
    measure=measure_pair(a,b,seed=seed)
    out={}
    for model,v in measure.items():
        for m in MASSES:
            k=str(int(m*100))
            out[f"{model}_jaccard_hdr_{k}"]=v["jaccard"][m]
            out[f"{model}_componentes_a_{k}"]=v["components_a"][m]
            out[f"{model}_componentes_b_{k}"]=v["components_b"][m]
        out[f"{model}_massa_grade_a"]=v["coverage_a"]
        out[f"{model}_massa_grade_b"]=v["coverage_b"]
    out["n_a"],out["n_b"]=len(a),len(b)
    if bootstrap:
        out["bootstrap"]=bootstrap_shape_noise(a,b,seed=seed,block=block,reps=reps)
    if check_resolution:
        larger=measure_pair(a,b,n=GRID_CHECK_N,seed=seed)
        for model in ("gaussian","mixture"):
            out[f"{model}_delta_jaccard_resolution_50"]=(
                larger[model]["jaccard"][.5]-measure[model]["jaccard"][.5])
            out[f"{model}_topologia_coincide_resolution_50"]=bool(
                larger[model]["components_a"][.5]==measure[model]["components_a"][.5]
                and larger[model]["components_b"][.5]==measure[model]["components_b"][.5])
    return out


def summarize(rows):
    results={"n_janelas":len(rows)}
    for model in ("gaussian","mixture"):
        for mass in (25,50,75):
            j=np.asarray([r[f"{model}_jaccard_hdr_{mass}"] for r in rows])
            c=np.asarray([r[f"{model}_componentes_a_{mass}"]+
                          r[f"{model}_componentes_b_{mass}"] for r in rows])
            results[f"{model}_HDR{mass}"]={
                "jaccard_medio":float(j.mean()),
                "jaccard_mediano":float(np.median(j)),
                "fracao_metades_multicomponentes":float(np.mean(c>2)),
            }
        cover=np.asarray([min(r[f"{model}_massa_grade_a"],
                               r[f"{model}_massa_grade_b"]) for r in rows])
        results[f"{model}_cobertura_grade_minima_mediana"]=float(np.median(cover))
        results[f"{model}_fracao_cobertura_menor_085"]=float(np.mean(cover<.85))
    checked=[r for r in rows if "bootstrap" in r]
    results["n_janelas_com_bootstrap"]=len(checked)
    if checked:
        for mass in (25,50,75):
            b=[r["bootstrap"][str(mass)] for r in checked]
            results[f"bootstrap_HDR{mass}"]={
                "mediana_ruido_local_p50":float(np.median([
                    x["ruido_bootstrap_local_p10_p50_p90"][1] for x in b])),
                "mediana_mudanca_observada":float(np.median([
                    x["mudanca_observada_1_menos_jaccard"] for x in b])),
                "quantidade_acima_limiar_pool95":int(sum(
                    x["excede_limiar_pool95"] for x in b)),
                "n_amostras":len(b),
                "nota":"Amostra deterministica equiespaciada; p nominais, "
                       "sem controle multiplas comparacoes."
            }
        for model in ("mixture","gaussian"):
            results[f"{model}_resolucao_50"]={
                "mediana_delta_jaccard_21_para_27":float(np.median([
                    r[f"{model}_delta_jaccard_resolution_50"] for r in checked])),
                "fracao_topologia_concordante":float(np.mean([
                    r[f"{model}_topologia_coincide_resolution_50"]
                    for r in checked]))
            }
    return results


def synthetic(kind,n=1500,seed=SEED):
    if kind=="sf1":
        df=simulate_sf1(default_sf1(),n+1700,seed=seed)
        coords=flow_coordinates(df)
        return coords[["z","iota","nu"]].to_numpy(float)[-n:]
    if kind=="three_component":
        rng=np.random.default_rng(seed)
        x=rng.normal(size=(n,3))
        # Duas concentracoes NO EIXO DA ATIVIDADE (terceira dimensao).
        state=rng.choice([-1,1],size=n)
        x[:,2]=2.1*state+.35*x[:,2]
        return x
    return synthetic_one(kind,n,seed)


def calibrate():
    cases={}
    for kind in ("stationary","temporal_mixture","persistent_mixture",
                 "nonlinear_curve","three_component","sf1"):
        rows=[assess_window(synthetic(kind,1500,SEED+1000*i+j),
              seed=SEED+i*10+j) for i in range(6) for j in [0]]
        cases[kind]=summarize(rows)
    # Controle bootstrap de nulo estacionario e mudanca temporal,
    # apenas diagnostico de propriedades desse simulador.
    for kind in ("stationary","temporal_mixture","three_component"):
        rows=[assess_window(synthetic(kind,1500,SEED+4000+j),
                    seed=SEED+5000+j,bootstrap=True,block=15,reps=BOOT_REPS,
                    check_resolution=True) for j in range(2)]
        cases[kind]["auditoria_bootstrap_controles"]=summarize(rows)
    return {"status":"CALIBRACAO_MORFOLOGIA_3D",
            "n_replicas_basicas_por_caso":6,"bootstrap_reps":BOOT_REPS,
            "n_replicas_bootstrap_em_tres_casos":2,
            "modelos":["gaussian","mixture2"],"massa_HDR":list(MASSES),
            "sf1":"SF1 DEFAULT, nao calibrado especificamente ao BTC em cada janela",
            "cenarios":cases}


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths: raise FileNotFoundError("Dados de exploracao ausentes")
    for path in paths:
        checked_exploratory_month(path.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    features=flow_coordinates(df)
    X=features[["z","iota","nu"]].to_numpy(float)
    ts=df["timestamp"].to_numpy(np.int64)
    w=WIN[interval]; step=STEP[interval]
    windows=[]
    for end in range(w,len(X)+1,w):
        xx=X[end-w:end]; tt=ts[end-w:end]
        if not np.isfinite(xx).all() or np.any(np.diff(tt)!=step):
            continue
        windows.append((end,int(tt[-1]+step),xx))
    if not windows: raise ValueError("Sem janelas validas")
    # Nomes e indice de selecao definidos ANTES de olhar resultados.
    idx=set(int(i) for i in np.linspace(0,len(windows)-1,
                                      min(BOOT_WINDOWS,len(windows)),dtype=int))
    rows=[]
    for i,(end,asof,x) in enumerate(windows):
        audit=i in idx
        z=assess_window(x,seed=SEED+end,bootstrap=audit,
                        block=BLOCK[interval],check_resolution=audit)
        rows.append({"index":i,"asof_ms":asof,"bootstrap_selecionado":audit,**z})
    stats=summarize(rows)
    out=ROOT/"reports"/f"FORMA_3D_{interval}_janelas.csv"
    out.parent.mkdir(exist_ok=True)
    flat=[]
    for row in rows:
        r={k:v for k,v in row.items() if k!="bootstrap"}
        if "bootstrap" in row:
            for mass,info in row["bootstrap"].items():
                for k,v in info.items():
                    if isinstance(v,(int,float,bool)):
                        r[f"bootstrap_{mass}_{k}"]=v
        flat.append(r)
    keys=list(dict.fromkeys(k for r in flat for k in r))
    with out.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=keys)
        writer.writeheader()
        writer.writerows(flat)
    return {
       "status":"RECONSTRUCAO_MORFOLOGICA_3D_EXPLORATORIA",
       "interval":interval,"ativo":"BTCUSDT spot",
       "arquivos_exploratorios":[p.name for p in paths],
       "periodo_confirmatorio_lido":False,
       "n_janelas_completas":len(rows),"n_amostras_bootstrap":len(idx),
       "bootstrap_por_amostra":BOOT_REPS,
       "coordenadas":["z","iota","nu"],
       "grade":{"resolucao":GRID_N,"limites":[-GRID_RANGE,GRID_RANGE],
                "checagem":GRID_CHECK_N},
       "HDR":[.25,.5,.75],
       "resultado":stats,
       "avisos":[
         "HDR corresponde a massa da grade TRUNCADA; cobertura fora dela reportada",
         "Testa forma da densidade, NAO geometria intrinseca Fisher–Rao",
         "Nulo de pool pressupoe mesma lei local, aproximacao possivelmente invalida sob regime",
         "Bootstrap B=29 e auditoria de apenas 8 janelas; p nominal grosseiro",
         "Nao detecta direcao causal de fluxo nem superioridade preditiva",
         "Controle SF1 default nao ajustado aos dados de cada janela",
       ]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--interval",choices=("synthetic","1m","1h"),required=True)
    args=p.parse_args()
    report=calibrate() if args.interval=="synthetic" else real(args.interval)
    target=ROOT/"reports"/f"FORMA_3D_{args.interval}.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
