#!/usr/bin/env python3
"""SGV: teste observacional da GEOMETRIA DA DEPENDENCIA entre variaveis.

Transforma CADA marginal com a CDF empirica do TREINO (70% inicial)
para score aproximadamente normal, SEM ler a validacao para ajustar o mapa.
Depois compara gaussiana, Student-t, GMM2 e KDE nos MESMOS scores.
O log-jacobiano da transformacao e identico para modelos: diferencas de
logscore continuam comparaveis, mas os scores absolutos NAO sao densidades
originais na escala bruta. Valores fora da amostra sao limitados aos postos
extremos da amostra de treino (ponto cego para extremidades/caudas).

Distincao: melhor Student-t sobre marginal-gaussianizado nao e prova
de geometria nao elipsoidal; mistura/KDE > Student-t e um indicio
que exigira ablacoes e controles posteriores.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
import numpy as np
from scipy.special import ndtri

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from experiments import teste_forma_distribuicoes as shape
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates


def empirical_marginal_gaussianize(a,b):
    """Treino e teste nas marginais de TREINO; nenhum quantil usa o teste."""
    if a.shape[1]!=b.shape[1]:
        raise ValueError("Dimensoes incompativeis")
    z1=np.zeros_like(a,dtype=float)
    z2=np.zeros_like(b,dtype=float)
    tail=np.zeros((len(b),a.shape[1]),dtype=bool)
    for j in range(a.shape[1]):
        s=np.sort(a[:,j])
        n=len(s)
        # Mid-rank para empates, incluindo iota quase discretizado.
        def transform(x):
            lo=np.searchsorted(s,x,side="left")
            hi=np.searchsorted(s,x,side="right")
            u=(0.5*(lo+hi)+0.5)/(n+1.)
            return ndtri(np.clip(u,0.5/(n+1.),(n+0.5)/(n+1.)))
        z1[:,j]=transform(a[:,j])
        z2[:,j]=transform(b[:,j])
        tail[:,j]=(b[:,j]<s[0])|(b[:,j]>s[-1])
    return z1,z2,float(np.mean(np.any(tail,axis=1)))


def fit_one_window(y):
    n=len(y)
    ntr=int(shape.FRACTION_TRAIN*n)
    a,b=y[:ntr],y[ntr:]
    az,bz,tail=empirical_marginal_gaussianize(a,b)
    transformed=np.concatenate([az,bz],axis=0)
    # Reaproveita as mesmas especificacoes dos 4 estimadores.
    res=shape.fit_evaluate_window(transformed)
    res["fracao_teste_extrapolacao_marginal"]=tail
    return res


def evaluate(X,ts,win,step):
    rows=[]
    for end,asof,y in shape.windows(X,ts,win,step):
        try:
            result=fit_one_window(y)
        except (ValueError,np.linalg.LinAlgError):
            continue
        rows.append({"end":int(end),"asof_ms":int(asof),**result})
    return rows


def synthetic():
    cases={}
    for j,kind in enumerate(("gauss","independent_t_marginals","nonlinear_univ_marginal",
                              "student_t4","mixture","curved")):
        rng=np.random.default_rng(900+j)
        if kind=="independent_t_marginals":
            X=rng.standard_t(3,size=(16*900,3))
        elif kind=="nonlinear_univ_marginal":
            X=shape.synthetic_data("gauss",16*900,901+j)
            X[:,2]=np.exp(0.85*X[:,2])
        else:
            X=shape.synthetic_data(kind,16*900,901+j)
        ts=np.arange(len(X),dtype=np.int64)*60_000
        rows=evaluate(X,ts,900,60_000)
        cases[kind]=shape.summarize(rows,seed=shape.SEED+j)
        cases[kind]["mediana_fracao_extrapolacao_marginal"]=float(np.median(
            [r["fracao_teste_extrapolacao_marginal"] for r in rows]))
    return cases


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    lo,hi=shape.PERIODS[interval]
    if not paths:
        raise FileNotFoundError("Sem dados exploratorios autorizados em data/")
    for p in paths:
        m=re.fullmatch(rf"BTCUSDT-{interval}-(\d{{4}}-\d{{2}})\.zip",p.name)
        if not m or not(lo<=m.group(1)<=hi):
            raise ValueError("Tentativa de ler dado reservado:"+p.name)
    df=load_binance_klines(paths,with_flow=True)
    coords=flow_coordinates(df)
    X=coords[["z","iota","nu"]].to_numpy(float)
    ts=df["timestamp"].to_numpy(np.int64)
    rows=evaluate(X,ts,shape.WINDOW[interval],shape.BARS_MS[interval])
    return [p.name for p in paths],rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--interval",choices=("synthetic","1m","1h"),required=True)
    args=ap.parse_args()
    if args.interval=="synthetic":
        report={"status":"CALIBRACAO_DEPENDENCIA_SINTETICA",
                "casos":synthetic()}
        rows=[]
    else:
        files,rows=real(args.interval)
        stats=shape.summarize(rows)
        stats["fracao_marginais_extrapoladas_mediana"]=float(np.median(
            [r["fracao_teste_extrapolacao_marginal"] for r in rows]))
        report={"status":"DEPENDENCIA_OBSERVACIONAL_EXPLORATORIA",
                "interval":args.interval,
                "n_arquivos_exploratorios":len(files),
                "janela":shape.WINDOW[args.interval],
                "sem_dados_confirmatorios":True,
                "modelos":"Gauss copula, t em scores marginais, mistura2, KDE",
                "aviso":"Comparacoes em scores de postos; normaliza marginais e preserva associacoes amostrais. Caudas externas saturadas e empates limitam sensibilidade.",
                "resultados":stats}
    out=ROOT/"reports"/f"FORMA_DEPENDENCIA_{args.interval}.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    if rows:
        import csv
        tab=out.with_name(out.stem+"_janelas.csv")
        with tab.open("w",newline="") as f:
            keys=["asof_ms","end","n_train","n_test",
                  "fracao_teste_extrapolacao_marginal",
                  "df_student","separacao_centros_mistura",
                  "peso_menor_componente",*shape.MODELS]
            wr=csv.DictWriter(f,fieldnames=keys)
            wr.writeheader()
            for row in rows:
                flat={k:v for k,v in row.items() if k!="logscore"}
                flat.update(row["logscore"])
                wr.writerow(flat)
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
