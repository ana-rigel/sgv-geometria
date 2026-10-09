#!/usr/bin/env python3
"""SGV observacional: precisao amostral e trajetorias de estados (sem previsao).

Objetivo: distinguir uma mudanca mensuravel entre retratos gaussianos de
flutuacoes esperadas no ajuste finito a um processo estacionario. A trajetoria
aqui usa janelas DISJUNTAS e apenas dados fechados antes de cada asof.

Metodologia:
- Estado F_t = (mu, Sigma) para X=(z, iota, nu).
- Distancia de Bhattacharyya entre gaussianas = descritiva e nao-direcional.
- Comprimento Fisher local simetrizado = aproximacao QUADRATICA no ponto medio,
  nao geodesica exata entre gaussianas, nem uma lei do mercado.
- Bootstrap em blocos circulares para IC da correlacao de cada janela.
- Bootstrap nulo de duas janelas de mesmo tamanho AMOSTRADAS de uma serie
  COMBINADA A|B: H0 de estacionariedade local e estrutura de dependencia
  aproximadamente preservada ate comprimento L.
- Taxa de alertas p<=.05 e ruido estimado, sem alcunha de descoberta devido
  a multiplas janelas, selecao exploratoria e nao-estacionariedade potencial.

PROIBIDO usar meses BTC confirmatorios. Todos os controles e parametros
podem ser auditados no codigo e devem permanecer congelados nesta execucao.
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

from experiments.fotografia_informacional import gaussian_snapshot, bhattacharyya
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates

EXPLORE={"1m":("2026-05","2026-07"),"1h":("2020-01","2024-12")}
BAR_MS={"1m":60000,"1h":3600000}
DESIGNS={
  "1m":[{"name":"principal","window":600,"block":15},
        {"name":"janela_curta","window":300,"block":15}],
  "1h":[{"name":"principal","window":168,"block":12},
        {"name":"janela_longa","window":336,"block":12}],
}
REPS=399
SEED=20261009


def gaussian_batch(x:np.ndarray):
    """(repeticoes, n, 3) -> mu e cov sem ajustar referencias futuras."""
    m=x.mean(axis=1)
    centered=x-m[:,None,:]
    c=np.einsum("bni,bnj->bij",centered,centered)/(x.shape[1]-1)
    return m,c


def draw_blocks(rng, n, length, block, reps):
    """Indices de bootstrap circular mantendo dependencia dentro de blocos."""
    if n<2 or not (1<=block<=length) or reps<1:
        raise ValueError("Parametros de blocos invalidos")
    count=(length+block-1)//block
    start=rng.integers(n,size=(reps,count))
    return ((start[:,:,None]+np.arange(block)[None,None,:])%n).reshape(
        reps,count*block)[:,:length]


def bhat_batch(ma,ca,mb,cb):
    """Distancias de Bhattacharyya para gaussianas 3D em lotes."""
    mid=(ca+cb)*.5
    delta=mb-ma
    s1,ldmid=np.linalg.slogdet(mid)
    s2,lda=np.linalg.slogdet(ca)
    s3,ldb=np.linalg.slogdet(cb)
    if not (np.all(s1>0) and np.all(s2>0) and np.all(s3>0)):
        raise ValueError("Covariancia bootstrap nao definida")
    term=np.einsum("bi,bi->b",delta,np.linalg.solve(mid,delta[:,:,None])[:,:,0])/8
    return np.maximum(0.,term+.5*(ldmid-.5*(lda+ldb)))


def midpoint_fisher_quadratic(a:dict,b:dict):
    """Norma linearizada local no ponto medio de duas gaussianas."""
    mid=(a["cov"]+b["cov"])/2.
    dm=b["mean"]-a["mean"]
    dc=b["cov"]-a["cov"]
    m=np.linalg.solve(mid,dc)
    squared=float(dm@np.linalg.solve(mid,dm)+.5*np.trace(m@m))
    return float(np.sqrt(max(squared,0.)))


def rho_boot_interval(x:np.ndarray,rng,block:int,reps:int=REPS):
    idx=draw_blocks(rng,len(x),len(x),block,reps)
    _,cov=gaussian_batch(x[idx])
    denom=np.sqrt(cov[:,0,0]*cov[:,1,1])
    rho=cov[:,0,1]/denom
    if not np.isfinite(rho).all():
        raise ValueError("Bootstrap de correlacao invalido")
    return [float(z) for z in np.quantile(rho,[.025,.975])]


def noise_test(a,b,*,block,reps=REPS,seed=SEED):
    """Intervalo para rho de A e B, e H0 de mesma lei local A==B.

    O nulo e CONDICIONAL a mistura A|B: se ha uma mudanca forte, o pool
    incorpora a heterogeneidade. A amostragem em blocos nao prova
    estacionariedade e os p-values sao aproximados e exploratorios.
    """
    a,b=np.asarray(a,float),np.asarray(b,float)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=3:
        raise ValueError("Estados precisam da mesma janela 3D")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Dados nao finitos")
    A,B=gaussian_snapshot(a),gaussian_snapshot(b)
    actual=bhattacharyya(A,B)
    fisher=midpoint_fisher_quadratic(A,B)
    rng=np.random.default_rng(seed)
    ciA=rho_boot_interval(a,rng,block,reps)
    ciB=rho_boot_interval(b,rng,block,reps)
    combined=np.concatenate([a,b])
    ia=draw_blocks(rng,len(combined),len(a),block,reps)
    ib=draw_blocks(rng,len(combined),len(a),block,reps)
    ma,ca=gaussian_batch(combined[ia])
    mb,cb=gaussian_batch(combined[ib])
    null=bhat_batch(ma,ca,mb,cb)
    q95=float(np.quantile(null,.95))
    return {
       "distancia_bhattacharyya":float(actual),
       "comprimento_fisher_quadratico_aprox":fisher,
       "rho_preco_fluxo_a":float(A["corr"][0,1]),
       "rho_preco_fluxo_b":float(B["corr"][0,1]),
       "ic95_rho_a":ciA,"ic95_rho_b":ciB,
       "p_nulo_local":float((1+np.sum(null>=actual))/(reps+1)),
       "ruido_bh_p50":float(np.median(null)),
       "ruido_bh_p95":q95,
       "observado_maior_ruido_p95":bool(actual>q95),
       "razao_observado_mais_epsilon_sobre_ruido_p95":float(
          actual/max(q95,1e-12)),
    }


def segments(x,ts,step):
    """Fragmenta gaps/NaNs antes de formar janelas; nunca interpola."""
    x=np.asarray(x,float)
    ts=np.asarray(ts,np.int64)
    if len(x)!=len(ts) or x.shape[1]!=3:
        raise ValueError("Formato invalido")
    contiguous=np.isfinite(x).all(axis=1)
    pieces=[]
    start=None
    for i in range(len(ts)):
        valid=bool(contiguous[i])
        joins=bool(i and valid and contiguous[i-1] and
                   ts[i]-ts[i-1]==step)
        if start is not None and not joins:
            if i-start>=2:
                pieces.append((start,i))
            start=None
        if valid and start is None:
            start=i
    if start is not None and len(ts)-start>=2:
        pieces.append((start,len(ts)))
    return pieces


def disjoint_windows(x,ts,step,window):
    """Indices causais, sem sobreposicao dentro de cada segmento contiguo."""
    for seg_id,(start,end) in enumerate(segments(x,ts,step)):
        for j in range(start+window,end+1,window):
            yield (seg_id,j-1,int(ts[j-1]+step),x[j-window:j])


def analyze(x,ts,*,interval,design,reps=REPS,seed=SEED):
    win,block=design["window"],design["block"]
    path=[]
    comparisons=[]
    prev=None
    for seg,t,asof,window_samples in disjoint_windows(x,ts,BAR_MS[interval],win):
        try:
            snap=gaussian_snapshot(window_samples)
        except ValueError:
            prev=None
            continue
        eigen=np.linalg.eigvalsh(snap["cov"])
        state={
            "segment":int(seg),"t_end":int(t),"asof_ms":int(asof),
            "mu_z":float(snap["mean"][0]),
            "mu_iota":float(snap["mean"][1]),
            "mu_nu":float(snap["mean"][2]),
            "rho_preco_fluxo":float(snap["corr"][0,1]),
            "rho_atividade_fluxo":float(snap["corr"][1,2]),
            "logdet_cov":float(snap["logdet_cov"]),
            "condicionamento":float(snap["condition"]),
            "autovalor_menor":float(eigen[0]),
            "autovalor_maior":float(eigen[-1]),
        }
        path.append(state)
        if prev is not None and prev[0]==seg:
            oldseg,old_t,old_asof,old=prev
            result=noise_test(old,window_samples,block=block,reps=reps,
                              seed=seed+int(t))
            comparisons.append({
                "from_asof_ms":int(old_asof),"to_asof_ms":int(asof),
                "passo_minutos":int(win*BAR_MS[interval]//60000),
                **result,
            })
        prev=(seg,t,asof,window_samples)

    if not comparisons:
        raise RuntimeError("Nenhuma comparacao entre janelas completas")
    p=np.array([r["p_nulo_local"] for r in comparisons])
    distance=np.array([r["distancia_bhattacharyya"] for r in comparisons])
    threshold=np.array([r["ruido_bh_p95"] for r in comparisons])
    ratio=distance/np.maximum(threshold,1e-12)
    # Contagem como DIAGNOSTICO sem correcao de multiplas hipoteses.
    return {
      "n_estados":len(path),"n_comparacoes_disjuntas_adjacentes":len(comparisons),
      "n_segmentos":len(set(row["segment"] for row in path)),
      "n_alertas_nominais_005":int(np.sum(p<=.05)),
      "fracao_alertas_nominais_005":float(np.mean(p<=.05)),
      "distancia_bh_mediana":float(np.median(distance)),
      "ruido_local_p95_mediano":float(np.median(threshold)),
      "razao_distancia_ao_ruido_p95_mediana":float(np.median(ratio)),
      "fracao_diferencas_acima_ruido_95pct":float(np.mean(distance>threshold)),
      "rho_mediana_amplitude_ic95":float(np.median([
        r["ic95_rho_b"][1]-r["ic95_rho_b"][0] for r in comparisons])),
      "fracao_rho_ic95_nao_sobrepostos":float(np.mean([
        r["ic95_rho_b"][0]>r["ic95_rho_a"][1] or
        r["ic95_rho_a"][0]>r["ic95_rho_b"][1] for r in comparisons])),
      "nota":"Exploratorio: p nominal nao e evidencia confirmatoria; "
             "transicoes adjacentes compartilham um estado, "
             "bootstrap nulo pressupoe estacionariedade dentro da dupla.",
    },path,comparisons


def synthetic_pair(seed,*,changed=False,window=600,phi=.35):
    rng=np.random.default_rng(seed)
    n=2*window
    z=rng.standard_normal((n,3))
    if changed:
        # Copula de covariancia muda entre as metades, sem mudanca nas marginais.
        z[:window,1]=.75*z[:window,0]+np.sqrt(1-.75**2)*z[:window,1]
        z[window:,1]=-.75*z[window:,0]+np.sqrt(1-.75**2)*z[window:,1]
    else:
        z[:,1]=.55*z[:,0]+np.sqrt(1-.55**2)*z[:,1]
    v=np.empty_like(z)
    v[0]=z[0]
    for t in range(1,n):
        v[t]=phi*v[t-1]+np.sqrt(1-phi**2)*z[t]
    return v[:window],v[window:]


def calibrate(*,window=360,block=12,reps=199,n_pairs=40):
    reports={}
    for kind in ("estacionario","mudanca_copula"):
        rows=[]
        for i in range(n_pairs):
            a,b=synthetic_pair(200+i,changed=(kind=="mudanca_copula"),
                               window=window)
            r=noise_test(a,b,block=block,reps=reps,seed=1000+i)
            rows.append(r)
        reports[kind]={
            "n_pares":len(rows),
            "taxa_alertas_p005":float(np.mean([r["p_nulo_local"]<=.05 for r in rows])),
            "fracao_obs_acima_ruido95":float(np.mean([
                r["observado_maior_ruido_p95"] for r in rows])),
            "distancia_mediana":float(np.median([
                r["distancia_bhattacharyya"] for r in rows])),
        }
    return {"status":"CALIBRACAO_SINTETICA_RUIDO_TRAJETORIAS",
            "janela":window,"bloco":block,"bootstrap_reps":reps,
            "gerador":"AR(0.35), covariancia fixa versus inversao de correlacao "
                     "sem mudanca de marginal univariada",
            "controles":reports,
            "interpretacao":"Poder apenas neste gerador; sem generalizacao ao BTC."}


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)


def run_real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths:
        raise FileNotFoundError("Sem dados BTC exploratorios; baixar scripts/baixar_klines.py --so")
    for path in paths:
        m=re.fullmatch(rf"BTCUSDT-{interval}-(\d{{4}}-\d{{2}})\.zip",path.name)
        if not m or not(EXPLORE[interval][0]<=m.group(1)<=EXPLORE[interval][1]):
            raise ValueError(f"Arquivo de periodo nao autorizado: {path.name}")
    df=load_binance_klines(paths,with_flow=True)
    coords=flow_coordinates(df)
    x=coords[["z","iota","nu"]].to_numpy(float)
    ts=df.timestamp.to_numpy(np.int64)
    report={"status":"TRAJETORIAS_GEOMETRICAS_EXPLORATORIAS",
            "timeframe":interval,"ativo":"BTCUSDT spot",
            "arquivos_exploratorios":[path.name for path in paths],
            "bar_ms":BAR_MS[interval],"repeticoes_bootstrap":REPS,
            "sem_dados_confirmatorios":True,
            "definicao":"F_t=(mu,Sigma), distancia Bhattacharyya, comprimento "
                        "Fisher linearizado no ponto medio (nao geodesica exata)",
            "resultados":{}}
    dest=ROOT/"reports"
    for j,design in enumerate(DESIGNS[interval]):
        summary,states,tests=analyze(x,ts,interval=interval,
                                    design=design,seed=SEED+j)
        key=design["name"]
        report["resultados"][key]={"window":design["window"],
                                  "block":design["block"],
                                  **summary}
        write_csv(dest/f"TRAJETORIAS_{interval}_{key}_estados.csv",states)
        write_csv(dest/f"TRAJETORIAS_{interval}_{key}_mudancas.csv",tests)
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--interval",choices=("synthetic","1m","1h"),required=True)
    args=parser.parse_args()
    report=calibrate() if args.interval=="synthetic" else run_real(args.interval)
    out=ROOT/"reports"/f"TRAJETORIAS_SGV_{args.interval}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
