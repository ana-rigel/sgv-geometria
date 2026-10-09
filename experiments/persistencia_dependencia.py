#!/usr/bin/env python3
"""SGV - Persistencia local da geometria NAO gaussiana das dependencias.

OBJETIVO: separar heterogeneidade temporal de dependencia conjunta estavel.
Nao e modelo preditivo, nao opera, nao antecipa retornos ou volatilidade.

Caso A: duas copulas gaussianas com correlacoes diferentes em metades
temporais (mistura temporal). O conjunto pode parecer nao gaussiano,
enquanto cada metade, analisada isoladamente, e bem descrita por gaussiana.

Caso B: duas dependencias gaussianas distintas misturadas a CADA instante
(estrutura transversal persistente); cada metade conserva a mistura.

Metodo:
- X=(z,iota,nu), known at close of candles.
- Partition into non-overlapping contiguous windows of 1500 (1m)
  and 1008 (1h), no reserved BTC data.
- For each entire window and two disjoint temporal halves, transform each
  marginal into Gaussian rank scores using ONLY the FIRST 70% of that
  segment; compare density logscore on LAST 30% (observations not used
  to fit CDF or density) of that segment.
- Baselines Gaussian and Student-t; flexible 2-Gaussian mixture, KDE.
  Same scoring and frozen hyperparameters as previous SGV experiments.
- Measure improvement GMM vs Gaussian AND GMM vs Student-t in each half.
- Moving-block bootstrap over original non-overlapping windows, not bars.
- Time-specific CDFs may differ between halves; score DIFFERENCES
  comparable within each segment, absolute scores across different CDFs
  should NOT be directly compared.
- Gains within halves indicate repeated descriptive complexity, not
  identical geometric shape. Multiple testing and changes in window
  duration remain important limitations.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from experiments import teste_forma_distribuicoes as base
from experiments import teste_forma_dependencia as dep
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates

WIN={"1m":1500,"1h":1008}
STEPS={"1m":60_000,"1h":3_600_000}
AUTHORIZED={"1m":("2026-05","2026-07"),
            "1h":("2020-01","2024-12")}
REPS=2000
SEED=20261009


def segment_score(segment):
    """Conveniencia: guarda todas as medidas e nao apenas o melhor modelo."""
    s=dep.fit_one_window(segment)
    score=s["logscore"]
    return {
        "gmm_vs_gauss":float(score["mixture2"]-score["gauss"]),
        "gmm_vs_student":float(score["mixture2"]-score["student"]),
        "kde_vs_gauss":float(score["kde"]-score["gauss"]),
        "kde_vs_student":float(score["kde"]-score["student"]),
        "student_vs_gauss":float(score["student"]-score["gauss"]),
        "extrapolacao_marginal":float(s["fracao_teste_extrapolacao_marginal"]),
        "n_train":int(s["n_train"]),"n_test":int(s["n_test"]),
    }


def assess_window(x):
    """Cortes temporais fixos: duas metades completas e janela agregada."""
    x=np.asarray(x,float)
    if x.ndim!=2 or x.shape[1]!=3 or len(x)<400 or len(x)%2:
        raise ValueError("Esperado N par >=400 e 3 coordenadas")
    half=len(x)//2
    a=segment_score(x[:half])
    b=segment_score(x[half:])
    pooled=segment_score(x)
    d={"janela_inteira":pooled,"metade_a":a,"metade_b":b}
    for key in ("gmm_vs_gauss","gmm_vs_student",
                "kde_vs_gauss","kde_vs_student",
                "student_vs_gauss"):
        d["media_local_"+key]=(a[key]+b[key])/2.
        d["minimo_local_"+key]=min(a[key],b[key])
        d["ganho_pooled_menos_local_"+key]=(
            pooled[key]-d["media_local_"+key])
        d["ambas_metades_positivas_"+key]=bool(
            a[key]>0 and b[key]>0)
    return d


def bootstrap_means(data,seed=SEED,reps=REPS):
    """CI de media por janelas disjuntas; grupos adjacentes podem depender."""
    arr=np.asarray(data,float)
    n=len(arr)
    if n<6:
        raise ValueError("Minimo de 6 janelas disjuntas")
    block=4 if n>=20 else 2
    rng=np.random.default_rng(seed)
    starts=np.arange(n-block+1)
    bs=np.empty(reps)
    for i in range(reps):
        ids=[]
        while len(ids)<n:
            j=int(rng.choice(starts))
            ids.extend(range(j,j+block))
        bs[i]=float(arr[np.array(ids[:n])].mean())
    return {
        "media":float(arr.mean()),
        "mediana":float(np.median(arr)),
        "IC95_blocos_temporais":[float(z) for z in np.quantile(bs,[.025,.975])],
        "IC95_inteiramente_positivo":bool(np.quantile(bs,.025)>0),
        "bloco_n_janelas":block,
    }


def summarize(rows,seed=SEED):
    if len(rows)<6:
        raise ValueError("Janelas insuficientes")
    wanted=("gmm_vs_gauss","gmm_vs_student",
            "kde_vs_gauss","kde_vs_student")
    output={"n_janelas_sem_sobreposicao":len(rows),
            "diagnosticos":{}}
    for j,k in enumerate(wanted):
        pooled=[v["janela_inteira"][k] for v in rows]
        a=[v["metade_a"][k] for v in rows]
        b=[v["metade_b"][k] for v in rows]
        local=[v["media_local_"+k] for v in rows]
        both=[v["ambas_metades_positivas_"+k] for v in rows]
        output["diagnosticos"][k]={
            "janela_inteira":bootstrap_means(pooled,seed+j*10+1),
            "primeira_metade":bootstrap_means(a,seed+j*10+2),
            "segunda_metade":bootstrap_means(b,seed+j*10+3),
            "media_das_metades":bootstrap_means(local,seed+j*10+4),
            "fracao_janelas_ambas_metades_positivas":float(np.mean(both)),
            "fracao_primeira_metade_positiva":float(np.mean(np.array(a)>0)),
            "fracao_segunda_metade_positiva":float(np.mean(np.array(b)>0)),
            "ganho_pooled_menos_local":bootstrap_means(
                np.array(pooled)-np.array(local),seed+j*10+5),
        }
    output["extrapolacao_marginal_mediana_por_segmento"]={
        name:float(np.median([v[name]["extrapolacao_marginal"] for v in rows]))
        for name in ("janela_inteira","metade_a","metade_b")
    }
    output["interpretacao_obrigatoria"]=[
        "Ganho local persistente nao prova identidade da forma em metades; "
        "apenas que a complexidade descritiva reaparece nos dois trechos",
        "Ganhos nao sao indicadores de direcao de fluxo ou antecipacao de preco",
        "Metades possuem menor N; penalizacao amostral diferente do pooled",
        "Mapas marginais estimados independentemente em cada segmento; "
        "somente diferencias de logscore entre modelos em MESMO segmento",
        "Student-t em scores marginais tem contornos elipsoidais",
        "Mistura de duas gaussianas melhor nao prova dois modos ou curvatura intrinseca",
        "Boostrap e exploratorio e nao corrige busca de modelos nem regime de volatilidade",
    ]
    return output


def synthetic_one(kind,win,seed):
    rng=np.random.default_rng(seed)
    n=win
    # Respeita tempos de regime; dependencia AR(1) fraca no fluxo.
    corr1,corr2=.83,-.83
    eps=rng.normal(size=(n,3))
    if kind=="stationary":
        rho=np.full(n,.55)
    elif kind=="temporal_mixture":
        rho=np.where(np.arange(n)<n//2,corr1,corr2)
    elif kind=="persistent_mixture":
        rho=np.where(rng.random(n)<.5,corr1,corr2)
    elif kind=="independent_skew_marginals":
        rho=np.zeros(n)
    elif kind=="nonlinear_curve":
        rho=np.zeros(n)
    else:
        raise ValueError(kind)
    eps[:,1]=rho*eps[:,0]+np.sqrt(1-rho*rho)*eps[:,1]
    if kind=="nonlinear_curve":
        eps[:,1]=(.95*(eps[:,0]**2-1)+.26*rng.normal(size=n))
    x=np.empty_like(eps)
    x[0]=eps[0]
    phi=.20
    for t in range(1,n):
        x[t]=phi*x[t-1]+np.sqrt(1-phi*phi)*eps[t]
    if kind=="independent_skew_marginals":
        x[:,0]=np.exp(.8*x[:,0])
        x[:,2]=np.exp(.7*x[:,2])
    return x


def calibrate():
    result={}
    n_per=12
    for j,kind in enumerate(("stationary","temporal_mixture",
                             "persistent_mixture",
                             "independent_skew_marginals",
                             "nonlinear_curve")):
        rows=[assess_window(synthetic_one(kind,1500,2000+j*100+i))
              for i in range(n_per)]
        result[kind]=summarize(rows,SEED+j)
    return {
        "status":"CALIBRACAO_SINTETICA_PERSISTENCIA_DEPENDENCIA",
        "n_janelas_por_caso":n_per,
        "n_barras_por_janela":1500,
        "casos":result,
        "criterio_positivo":"Modelo flexivel versus gauss e Student-t "
                            "nos dois trechos e nao apenas no agregado",
        "aviso":"Controles demonstram poder e falhas em geradores estilizados, "
                "nao confiabilidade garantida em mercado real."
    }


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    lo,hi=AUTHORIZED[interval]
    if not paths:
        raise FileNotFoundError("Sem dados exploratorios; execute scripts/baixar_klines.py --so")
    for p in paths:
        m=re.fullmatch(rf"BTCUSDT-{re.escape(interval)}-([0-9]{{4}}-[0-9]{{2}})\.zip",p.name)
        if m is None or not(lo<=m.group(1)<=hi):
            raise ValueError("Arquivo de periodo reservado ou invalido: "+p.name)
    df=load_binance_klines(paths,with_flow=True)
    feats=flow_coordinates(df)
    x=feats[["z","iota","nu"]].to_numpy(float)
    ts=df.timestamp.to_numpy(np.int64)
    rows=[]
    for _,asof,segment in base.windows(x,ts,WIN[interval],STEPS[interval]):
        try:
            row=assess_window(segment)
        except (ValueError,np.linalg.LinAlgError):
            continue
        rows.append({"asof_ms":int(asof),**row})
    if not rows:
        raise RuntimeError("Nenhuma janela valida")
    return {
        "status":"PERSISTENCIA_DEPENDENCIA_OBSERVACIONAL_EXPLORATORIA",
        "timeframe":interval,
        "n_arquivos":len(paths),
        "janela":WIN[interval],
        "metade":WIN[interval]//2,
        "calibracao_do_controle_marginal":"Cada segmento usa somente o treino 70%",
        "dados_confirmatorios_usados":False,
        "resultados":summarize(rows),
    },rows


def write_rows(rows,interval):
    path=ROOT/"reports"/f"PERSISTENCIA_DEPENDENCIA_{interval}_janelas.csv"
    keys=["asof_ms","segmento","n_train","n_test","extrapolacao_marginal",
          "gmm_vs_gauss","gmm_vs_student",
          "kde_vs_gauss","kde_vs_student","student_vs_gauss"]
    path.parent.mkdir(exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=keys)
        w.writeheader()
        for row in rows:
            for part in ("janela_inteira","metade_a","metade_b"):
                w.writerow({"asof_ms":row["asof_ms"],"segmento":part,
                            **row[part]})


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--interval",required=True,choices=("synthetic","1m","1h"))
    args=p.parse_args()
    if args.interval=="synthetic":
        report=calibrate()
    else:
        report,rows=real(args.interval)
        write_rows(rows,args.interval)
    dest=ROOT/"reports"/f"PERSISTENCIA_DEPENDENCIA_{args.interval}.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
