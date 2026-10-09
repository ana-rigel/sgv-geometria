#!/usr/bin/env python3
"""SGV -- morfologia observacional da dependencia preco/fluxo.

Estuda formas de *superficies de densidade* em duas coordenadas (z, iota),
com marginais gaussianizadas pelo prefixo da janela. A terceira coordenada
atividade nu permanece disponivel no SGV, mas NAO integra esta fatia 2D.
Isso nao mede a topologia do espaco de distribuicoes nem uma lei geometrica.

Janela: primeiro 30% ancora quantis; depois duas metades cronologicas
independentes (35%+35%). Ambas usam a MESMA transformacao da ancora,
sem acessar futuros ao montar as fotografias. Ajustes GMM2 e gaussiano 2D
sao treinados independentemente em cada metade, mantendo coordenadas comuns.

Reconstrucao: grade fixa [-3,3]^2 e region-of-highest-density de 50%
da massa numerica dentro da grade. Componentes conexas (8 vizinhos)
e Jaccard entre regioes, com controle por rotacao da covariancia gaussiana.

Nulo SF1 e calibracoes gaussianas, curvadas, bimodais, mistura temporal.
SF1 usa o gerador EXISTENTE, nao uma lei de mercado. Primeiro estudo
exploratorio, sem thresholds confirmatorios ou BTC reservado.
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
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from experiments.persistencia_dependencia import checked_exploratory_month, synthetic_one
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates, default_sf1, simulate_sf1

WIN={"1m":1500,"1h":1008}
BARMS={"1m":60000,"1h":3600000}
GRID_N=61
GRID_RANGE=3.0
HDR_MASS=.50
RIDGE=1.e-4
SEED=20261009


def gaussianize_prefix(anchor, remainder):
    """Ajusta CDF empírica só na âncora; retorna projeção 2D comum."""
    anchor=np.asarray(anchor,float)
    remainder=np.asarray(remainder,float)
    if anchor.ndim!=2 or remainder.ndim!=2 or anchor.shape[1]!=2 or remainder.shape[1]!=2:
        raise ValueError("Coordenadas 2D esperadas")
    if not np.isfinite(anchor).all() or not np.isfinite(remainder).all():
        raise ValueError("Dados nao finitos")
    result=np.empty_like(remainder,dtype=float)
    n=len(anchor)
    for j in range(2):
        sorted_col=np.sort(anchor[:,j])
        lo=np.searchsorted(sorted_col,remainder[:,j],side="left")
        hi=np.searchsorted(sorted_col,remainder[:,j],side="right")
        u=(.5*(lo+hi)+.5)/(n+1.)
        result[:,j]=ndtri(np.clip(u,.5/(n+1.),(n+.5)/(n+1.)))
    return result


def split_causal(X):
    X=np.asarray(X,float)
    n=len(X)
    if X.ndim!=2 or X.shape[1]<2 or n<300:
        raise ValueError("Janela invalida")
    na=int(.30*n)
    rest=X[na:,:2]
    cut=len(rest)//2
    if cut<60 or len(rest)-cut<60:
        raise ValueError("Metades muito pequenas")
    common=gaussianize_prefix(X[:na,:2],rest)
    return common[:cut],common[cut:]


def grid():
    axis=np.linspace(-GRID_RANGE,GRID_RANGE,GRID_N)
    x,y=np.meshgrid(axis,axis,indexing="xy")
    return np.column_stack([x.ravel(),y.ravel()])


def fit_densities(x,seed=SEED):
    x=np.asarray(x,float)
    if x.shape[1]!=2 or len(x)<60:
        raise ValueError("Ajuste 2D requer >=60 observacoes")
    model=GaussianMixture(n_components=2,reg_covar=RIDGE,
            covariance_type="full",random_state=seed,n_init=2,max_iter=100)
    model.fit(x)
    mean=x.mean(axis=0)
    cov=np.cov(x,rowvar=False)+RIDGE*np.eye(2)
    g=grid()
    gm=np.exp(model.score_samples(g))
    ga=np.exp(multivariate_normal.logpdf(g,mean=mean,cov=cov))
    return gm,ga


def hdr_mask(weights,mass=HDR_MASS):
    weights=np.asarray(weights,float).reshape(GRID_N,GRID_N)
    if np.any(weights<0) or not np.isfinite(weights).all() or weights.sum()<=0:
        raise ValueError("Densidade invalida")
    p=weights/weights.sum()
    idx=np.argsort(-p.ravel())
    selected=np.zeros(GRID_N*GRID_N,dtype=bool)
    end=int(np.searchsorted(np.cumsum(p.ravel()[idx]),mass,side="left"))+1
    selected[idx[:end]]=True
    return selected.reshape(GRID_N,GRID_N)


def components(mask):
    conn=np.ones((3,3),dtype=int)
    return int(label(mask,structure=conn)[1])


def overlap(a,b):
    inter=np.logical_and(a,b).sum()
    union=np.logical_or(a,b).sum()
    return float(inter/union) if union else 1.


def morphology(X,seed=SEED):
    a,b=split_causal(X)
    d1,g1=fit_densities(a,seed)
    d2,g2=fit_densities(b,seed+1)
    A,B=hdr_mask(d1),hdr_mask(d2)
    AG,BG=hdr_mask(g1),hdr_mask(g2)
    # Comparacao de forma entre metades no MESMO espaco de quantis da ancora.
    return {
        "hdr_gmm_componentes_a":components(A),
        "hdr_gmm_componentes_b":components(B),
        "hdr_gauss_componentes_a":components(AG),
        "hdr_gauss_componentes_b":components(BG),
        "jaccard_hdr_gmm_metades":overlap(A,B),
        "jaccard_hdr_gauss_metades":overlap(AG,BG),
        "jaccard_gmm_gauss_a":overlap(A,AG),
        "jaccard_gmm_gauss_b":overlap(B,BG),
        "fracao_metades_gmm_mais_de_um_componente":float((components(A)>1)+(components(B)>1))/2.,
        "n_a":len(a),"n_b":len(b),
        "nota":"Componentes conexas na grade fixa, com massa HDR normalizada DENTRO dela. Nao e topologia intrinseca."
    }


def synthetic(kind,n=1500,seed=1):
    if kind in ("stationary","temporal_mixture","persistent_mixture","nonlinear_curve"):
        return synthetic_one(kind,n,seed)
    if kind=="sf1":
        sim=simulate_sf1(default_sf1(),n+1700,seed=seed)
        feats=flow_coordinates(sim)
        return feats[["z","iota","nu"]].to_numpy(float)[-n:]
    raise ValueError(kind)


def calibrate():
    cases={}
    for kind in ("stationary","temporal_mixture","persistent_mixture","nonlinear_curve","sf1"):
        rows=[morphology(synthetic(kind,1500,seed=100+i),seed=200+i) for i in range(10)]
        cases[kind]=summary(rows)
    return {"status":"MORFOLOGIA_CALIBRACAO_SINTETICA","n_replicas":10,
            "sf1_e_referencia":"gerador default_sf1 original, sem ajuste ao BTC desta etapa",
            "casos":cases}


def summary(rows):
    vals={}
    for key in ("jaccard_hdr_gmm_metades","jaccard_hdr_gauss_metades",
                "jaccard_gmm_gauss_a","jaccard_gmm_gauss_b",
                "fracao_metades_gmm_mais_de_um_componente"):
        x=np.array([r[key] for r in rows],float)
        vals[key]={"media":float(x.mean()),"mediana":float(np.median(x)),
                   "p10":float(np.quantile(x,.1)),"p90":float(np.quantile(x,.9))}
    return {
        "n_janelas":len(rows),
        "resumo":vals,
        "fracao_duas_metades_hdr_gmm_conexa":float(np.mean([
             r["hdr_gmm_componentes_a"]==1 and r["hdr_gmm_componentes_b"]==1
             for r in rows])),
        "fracao_duas_metades_hdr_gmm_multicomponente":float(np.mean([
             r["hdr_gmm_componentes_a"]>1 and r["hdr_gmm_componentes_b"]>1
             for r in rows])),
        "fracao_gmm_jaccard_supera_gauss":float(np.mean([
            r["jaccard_hdr_gmm_metades"]>r["jaccard_hdr_gauss_metades"] for r in rows])),
    }


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths: raise FileNotFoundError("Sem dados de exploracao")
    for p in paths: checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    feats=flow_coordinates(df)
    X=feats[["z","iota","nu"]].to_numpy(float)
    ts=df["timestamp"].to_numpy(np.int64)
    # Observacoes disjuntas, sem gaps, com parametros fixos ANTES do replay.
    rows=[]
    win=WIN[interval]
    for end in range(win,len(X)+1,win):
        block=X[end-win:end]
        times=ts[end-win:end]
        if not np.isfinite(block).all() or np.any(np.diff(times)!=BARMS[interval]):
            continue
        m=morphology(block,seed=SEED+end)
        rows.append({"asof_ms":int(times[-1]+BARMS[interval]),**m})
    if not rows: raise RuntimeError("Nenhuma janela morfologica valida")
    return {
        "status":"MORFOLOGIA_DESCRITIVA_EXPLORATORIA",
        "interval":interval,"n_arquivos":len(paths),"janela":win,
        "variaveis_projetadas":["z","iota"],
        "atividade_nu_nao_modelada_na_superficie":True,
        "dados_confirmatorios_lidos":False,
        "resultado":summary(rows),
    },rows


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--interval",choices=("synthetic","1m","1h"),required=True)
    a=p.parse_args()
    if a.interval=="synthetic":
        result=calibrate()
    else:
        result,rows=real(a.interval)
        out=ROOT/"reports"/f"MORFOLOGIA_{a.interval}_janelas.csv"
        out.parent.mkdir(exist_ok=True)
        with out.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    out=ROOT/"reports"/f"MORFOLOGIA_{a.interval}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
