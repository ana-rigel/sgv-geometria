#!/usr/bin/env python3
"""SGV - Decomposicao observacional da geometria dos fluxos de mercado.

Sem previsao e sem alegacao de "nova lei". Comparar duas fotografias com
janelas SEM sobreposicao, apenas dados de candle disponiveis ao fechamento.

A distancia Bhattacharyya de gaussianas admite decomposicao EXATA:
    DB = M + C
    M = (mu1-mu0)' ((Sigma0+Sigma1)/2)^-1 (mu1-mu0)/8
    C = .5 logdet((Sigma0+Sigma1)/2) - .25 logdet(Sigma0)
        - .25 logdet(Sigma1)

Sigma = D R D. C tem interacao entre D e R: nao ha separacao canonica.
Usa-se atribuicao SHAPLEY simetrica (2 fatores) para contabilizar C:
    V(S,R) = C(Sigma0, D_S R_R D_S)
    S_share=.5 * (V(1,0) + V(1,1) - V(0,1))
    R_share=.5 * (V(0,1) + V(1,1) - V(1,0))
Essas contribuicoes somam exatamente C; podem ser negativas.
Indicadores nao-negativos separados: V(1,0) (apenas escala) e
C(R0,R1) (apenas correlacao). Nao sao aditivos.

Nulo aproximado: bootstrap circular por blocos em amostra A|B combinada,
declarando a hipotese forte de mesma lei local, nao-estacionariedade e
testes multiplos como LIMITES. Valores p NOMINAIS, apenas diagnosticos.

Dados: somente BTCUSDT EXPLORACAO: 1m mai-jul/2026; 1h 2020-2024.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.precisao_trajetorias import (
    DESIGNS, EXPLORE, BAR_MS, SEED, REPS,
    draw_blocks, gaussian_batch, disjoint_windows,
)
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates

KEYS = ("full", "mean", "covariance", "scale_only", "correlation_only")


def _as_batch(c):
    arr = np.asarray(c, float)
    if arr.shape[-2:] != (3, 3):
        raise ValueError("Esperada matriz 3x3 ou lote (...,3,3)")
    return arr


def cov_divergence(c0, c1):
    """Parcela Bhattacharyya SOMENTE covariancia, nao-negativa (3D)."""
    c0 = _as_batch(c0)
    c1 = _as_batch(c1)
    cm = (c0 + c1) / 2.0
    s0, ld0 = np.linalg.slogdet(c0)
    s1, ld1 = np.linalg.slogdet(c1)
    sm, ldm = np.linalg.slogdet(cm)
    if np.any(s0 <= 0) or np.any(s1 <= 0) or np.any(sm <= 0):
        raise ValueError("A covariancia deve ser positiva definida")
    return np.maximum(0., .5 * ldm - .25 * (ld0 + ld1))


def _corr_and_scales(cov):
    std = np.sqrt(np.diagonal(cov, axis1=-2, axis2=-1))
    if np.any(std <= 0):
        raise ValueError("Variancia nao positiva")
    corr = cov / (std[..., :, None] * std[..., None, :])
    return corr, std


def decompose(m0, c0, m1, c1):
    """Devolve arrays OU escalares, com atribuicao completa exata.

    Testes de dimensao impedem broadcasting silencioso entre lotes.
    """
    m0, m1 = np.asarray(m0, float), np.asarray(m1, float)
    c0, c1 = _as_batch(c0), _as_batch(c1)
    if m0.shape != m1.shape or c0.shape != c1.shape:
        raise ValueError("Estados de diferentes dimensoes")
    if m0.shape[-1] != 3 or c0.shape[:-2] != m0.shape[:-1]:
        raise ValueError("Batch de medias e covariancias incompativel")
    if not (np.isfinite(m0).all() and np.isfinite(m1).all()
            and np.isfinite(c0).all() and np.isfinite(c1).all()):
        raise ValueError("Estado nao finito")
    cm = (c0+c1)/2.
    d = m1-m0
    mean = np.einsum("...i,...i->...",d,
                     np.linalg.solve(cm,d[...,None])[...,0])/8.
    cov = cov_divergence(c0,c1)
    full = mean + cov

    r0,s0 = _corr_and_scales(c0)
    r1,s1 = _corr_and_scales(c1)
    # Mudanca so de marginal de dispersao, referencia R0.
    scale_counterfactual = r0 * s1[..., :, None] * s1[..., None, :]
    # Mudanca so na matriz de correlacoes, referencia D0.
    corr_counterfactual = r1 * s0[..., :, None] * s0[..., None, :]
    pure_scale = cov_divergence(c0, scale_counterfactual)
    pure_corr_ref = cov_divergence(c0, corr_counterfactual)
    # C(R0,R1): livre das unidades do X por transformacao diagonal fixa.
    corr_only = cov_divergence(r0,r1)

    scale_shapley = .5 * (pure_scale + cov - pure_corr_ref)
    corr_shapley = cov - scale_shapley
    if not np.allclose(mean+scale_shapley+corr_shapley,full,
                       rtol=1e-10,atol=1e-10):
        raise AssertionError("Identidade de atribuicao violada")
    return {
        "full":full,"mean":mean,"covariance":cov,
        "scale_only":pure_scale,"correlation_only":corr_only,
        "scale_shapley":scale_shapley,
        "correlation_shapley":corr_shapley,
        "pure_correlation_fixed_scale":pure_corr_ref,
    }


def stats(samples):
    x = np.asarray(samples,float)
    if x.shape[0]<24 or x.shape[1:]!=(3,):
        raise ValueError("Fotografia exige >=24 linhas em 3 coordenadas")
    if not np.isfinite(x).all():
        raise ValueError("Nao finito")
    m = x.mean(axis=0)
    c = np.cov(x,rowvar=False)
    # Proibir degeneracao e nao fabricar formas por ridge.
    ev = np.linalg.eigvalsh(c)
    if ev[0] <= max(1e-14,ev[-1]*1e-10):
        raise ValueError("Matriz degenerada")
    return m,c


def compare_and_bootstrap(a, b, *, block, reps=REPS, seed=SEED):
    a,b = np.asarray(a,float),np.asarray(b,float)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=3:
        raise ValueError("Janelas devem ter tamanho e dimensao identicos")
    ma,ca = stats(a)
    mb,cb = stats(b)
    actual = decompose(ma,ca,mb,cb)
    rng = np.random.default_rng(seed)
    # Nulo estacionario APROXIMADO: pool mistura A e B (cautela para regimes).
    pool=np.concatenate([a,b])
    ia=draw_blocks(rng,len(pool),len(a),block,reps)
    ib=draw_blocks(rng,len(pool),len(a),block,reps)
    ma0,ca0=gaussian_batch(pool[ia])
    mb0,cb0=gaussian_batch(pool[ib])
    null=decompose(ma0,ca0,mb0,cb0)
    out={}
    for k in ("full","mean","covariance","scale_only","correlation_only",
              "scale_shapley","correlation_shapley"):
        out[k]=float(actual[k])
    for key in KEYS:
        dist=np.asarray(null[key],float)
        out["p_nom_"+key]=float((1+np.sum(dist>=actual[key]))/(reps+1))
        out["ruido95_"+key]=float(np.quantile(dist,.95))
        out["excede_ruido95_"+key]=bool(actual[key]>out["ruido95_"+key])
    out["delta_corr_preco_fluxo"]=float(
        cb[0,1]/np.sqrt(cb[0,0]*cb[1,1])-
        ca[0,1]/np.sqrt(ca[0,0]*ca[1,1]))
    out["delta_logstd_z"]=float(.5*np.log(cb[0,0]/ca[0,0]))
    out["delta_logstd_iota"]=float(.5*np.log(cb[1,1]/ca[1,1]))
    out["delta_logstd_nu"]=float(.5*np.log(cb[2,2]/ca[2,2]))
    return out


def summarize(rows, n_states, block, window):
    if not rows:
        raise ValueError("Nenhuma dupla valida")
    d={}
    for key in KEYS:
        a=np.array([r[key] for r in rows])
        noise=np.array([r["ruido95_"+key] for r in rows])
        d[key]={
            "mediana_distancia":float(np.median(a)),
            "mediana_limiar_ruido95":float(np.median(noise)),
            "fracao_acima_ruido95":float(np.mean(a>noise)),
            "contagem_acima_ruido95":int(np.sum(a>noise)),
            "fracao_p_nom_005":float(np.mean(
                [r["p_nom_"+key]<=.05 for r in rows])),
        }
    shares={}
    for k in ("mean","scale_shapley","correlation_shapley"):
        values=np.array([r[k] for r in rows])
        shares[k]={
            "soma":float(values.sum()),
            "fracao_soma_distancia_total":float(
                values.sum()/sum(r["full"] for r in rows)),
            "mediana_valor":float(np.median(values)),
            "fracao_valores_negativos":float(np.mean(values < -1e-10)),
        }
    return {
        "janela":window,"bloco":block,
        "n_estados":n_states,"n_comparacoes":len(rows),
        "componentes":d,"atribuicao_contabil":shares,
        "alerta":"Shapley de escala/correlacao pode ser negativo. "
                 "Shares sao atribuicoes convencionadas, nao causalidade.",
        "avisos":[
            "Somente exploratorio, multiplas comparacoes sem correcao",
            "Nulo de bootstrap pooling pressupoe estacionariedade local",
            "Janelas adjacentes partilham o estado intermediario, "
            "logo testes em tempo nao independentes",
            "Medidas de correlacao e escala descrevem variaveis observadas, "
            "nao toda informacao do mercado",
            "Ajuste gaussiano nao captura diretamente dependencias nao lineares",
        ],
    }


def synthetic_pair(kind, seed, window=360, phi=.35):
    """Casos de resposta conhecida, variaveis autocorrelacionadas."""
    rng=np.random.default_rng(seed)
    # Normal base de correlacao positiva bem definida.
    R=np.array([[1.,.50,.12],[.50,1.,.08],[.12,.08,1.]])
    y=rng.standard_normal((2*window,3)) @ np.linalg.cholesky(R).T
    v=np.zeros_like(y)
    v[0]=y[0]
    for i in range(1,len(v)):
        v[i]=phi*v[i-1]+np.sqrt(1-phi*phi)*y[i]
    a,b=v[:window].copy(),v[window:].copy()
    if kind=="mean":
        b += np.array([.75,-.25,.1])
    elif kind=="scale":
        b[:,0] *= 1.85
    elif kind=="correlation":
        # Ortogonaliza z e depois recria correlacao com sinal inverso,
        # preservando aproximadamente variancias marginais da amostra.
        R2=np.array([[1.,-.60,.12],[-.60,1.,.08],[.12,.08,1.]])
        # Novo segmento com correlacao modificada, e mesmo processo AR.
        b_innov=rng.standard_normal((window,3))@np.linalg.cholesky(R2).T
        b=np.empty_like(b_innov)
        b[0]=b_innov[0]
        for i in range(1,window):
            b[i]=phi*b[i-1]+np.sqrt(1-phi*phi)*b_innov[i]
    elif kind!="stationary":
        raise ValueError(kind)
    return a,b


def calibrate():
    out={"status":"CALIBRACAO_DECOMPOSICAO","n_pares_por_cenario":32,
         "reps_bootstrap":199,"window":360,"bloco":12,"cenarios":{}}
    for j,kind in enumerate(("stationary","mean","scale","correlation")):
        rows=[compare_and_bootstrap(
            *synthetic_pair(kind,seed=1000+i,window=360),
            block=12,reps=199,seed=3000+i
        ) for i in range(32)]
        scenario={}
        for key in ("full","mean","scale_only","correlation_only"):
            scenario[key]={
                "fracao_acima_ruido95":float(np.mean([
                    r["excede_ruido95_"+key] for r in rows])),
                "mediana":float(np.median([r[key] for r in rows])),
            }
        out["cenarios"][kind]=scenario
    out["limites"]="Mecanismos artificiais fortes, correlacoes e autocorrelacoes simples. "
    out["limites"]+="Taxas nao sao validadas para BTC heterocedastico."
    return out


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths:
        raise FileNotFoundError("Nao ha klines exploratorios; baixar apenas via scripts/baixar_klines.py")
    lo,hi=EXPLORE[interval]
    for p in paths:
        m=re.fullmatch(rf"BTCUSDT-{interval}-(\d{{4}}-\d{{2}})\.zip",p.name)
        if not m or not(lo<=m.group(1)<=hi):
            raise ValueError(f"Arquivo proibido/periodo confirmatorio: {p.name}")
    df=load_binance_klines(paths,with_flow=True)
    coordinates=flow_coordinates(df)
    X=coordinates[["z","iota","nu"]].to_numpy(float)
    ts=df.timestamp.to_numpy(np.int64)
    result={
        "status":"DECOMPOSICAO_DESCRITIVA_EXPLORATORIA",
        "interval":interval,"ativo":"BTCUSDT spot",
        "reps_bootstrap":REPS,
        "arquivos_exploratorios":[p.name for p in paths],
        "sem_dados_confirmatorios":True,
        "resultados":{},
    }
    outdir=ROOT/"reports"
    outdir.mkdir(exist_ok=True)
    for j,design in enumerate(DESIGNS[interval]):
        previous=None
        rows=[]
        nstates=0
        for segment,t,asof,x in disjoint_windows(
                X,ts,BAR_MS[interval],design["window"]):
            try:
                stats(x)
            except ValueError:
                previous=None
                continue
            nstates+=1
            if previous is not None and previous[0]==segment:
                old_seg,old_t,old_asof,old_samples=previous
                one=compare_and_bootstrap(
                    old_samples,x,block=design["block"],
                    reps=REPS,seed=SEED+int(t)+j)
                rows.append({"asof_old_ms":int(old_asof),
                             "asof_new_ms":int(asof),
                             "segment":int(segment), **one})
            previous=(segment,t,asof,x)
        summary=summarize(rows,nstates,design["block"],design["window"])
        result["resultados"][design["name"]]=summary
        filename=outdir/f"DECOMP_GEOMETRIA_{interval}_{design['name']}_pares.csv"
        with filename.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--interval",required=True,
                        choices=("synthetic","1m","1h"))
    args=parser.parse_args()
    result=calibrate() if args.interval=="synthetic" else real(args.interval)
    out=ROOT/"reports"/f"DECOMP_GEOMETRIA_{args.interval}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
