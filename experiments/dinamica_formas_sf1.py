#!/usr/bin/env python3
"""SGV: trajetorias de HDR 3D sob referencia SF1 ajustada somente no passado.

Cada avaliacao possui:
  prefixo historico de 2000 candles -> fit_sf1 (GARCH-t, fluxo, volume)
  janela posterior de W candles -> 30% ancora marginal, 35% + 35% forma.
  Simulacoes SF1 feitas do ajuste do prefixo, SEM ajustar no teste.
  Distancias 1-Jaccard (HDR25, HDR50, HDR75) dos estados A/B.
  Repeticoes nulas independentes por janela com simulação e queimadura.
  Compare observacao com distrib. simulada: nao e teste confirmatorio com
  apenas 4 simulacoes nem avalia a dinamica real de news/order book.

Stride W//2 cria sobreposicao entre janelas sucessivas. Cada medida A/B usa
subjanelas internas disjuntas, mas sequencia de medidas NÃO independente.

NUNCA le BTC confirmatorio. SF1 calibrado localmente, primeira tentativa
de controle condicional, nao suficiente para provar estrutura extraordinaria.
"""
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from experiments.precisao_formas_3d import (
    WIN, STEP, assess_window, gaussianize_three
)
from experiments.persistencia_dependencia import checked_exploratory_month
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates, fit_sf1, simulate_sf1

PREFIX=2000
MAX_WINDOWS=12
SURROGATES=4
BURN=1700
SEED=20261009


def valid_segment(ts,x,step):
    return len(ts)>0 and np.isfinite(x).all() and bool(np.all(np.diff(ts)==step))


def sliding_origins(total,window,prefix,stride,max_windows):
    """Causal, chronological evaluation starts; cap uniformly by index."""
    possible=np.arange(prefix,total-window+1,stride,dtype=int)
    if len(possible)<=max_windows:return possible.tolist()
    selected=np.linspace(0,len(possible)-1,max_windows,dtype=int)
    return possible[selected].tolist()


def compact_features(out):
    return {f"{model}_J{level}":float(out[f"{model}_jaccard_hdr_{level}"])
            for model in ("mixture","gaussian") for level in (25,50,75)}


def compare_real_and_simulated(raw,*,start,window,step,seed,surrogates=SURROGATES):
    """Ajusta SF1 estritamente ate inicio da janela; simula futuro nulo."""
    prefix=raw.iloc[start-PREFIX:start].copy()
    test=raw.iloc[start:start+window].copy()
    if len(prefix)!=PREFIX or len(test)!=window:
        raise ValueError("Faixas incompletas")
    combined=raw.iloc[start-PREFIX:start+window]
    # As coordenadas reais da janela devem usar aquecimento historico causal;
    # evitar calcula-las sobre teste sem historico.
    coordinates=flow_coordinates(combined)
    x=coordinates[["z","iota","nu"]].to_numpy(float)[-window:]
    tt=test.timestamp.to_numpy(np.int64)
    if not valid_segment(tt,x,step):
        raise ValueError("Gap ou dados invalidos")
    observed=assess_window(x,seed=seed)
    fitted=fit_sf1(prefix)
    null=[]
    for j in range(surrogates):
        s=simulate_sf1(fitted,window+BURN,seed=seed+j*100+1,step_ms=step)
        simulated=flow_coordinates(s)
        x_sim=simulated[["z","iota","nu"]].to_numpy(float)[-window:]
        if not np.isfinite(x_sim).all():raise ValueError("SF1 simulado invalido")
        z=assess_window(x_sim,seed=seed+j*100+100)
        null.append(compact_features(z))
    real=compact_features(observed)
    result={
        "asof_ms":int(tt[-1]+step),"start_idx":int(start),
        "sf1_prefix_barras":PREFIX,"janelas_sf1":surrogates,
        "escala_intervalo_minutos":step//60000,
        "sf1_param_garch":str(fitted.garch),
    }
    for key,value in real.items():
        simulations=np.array([m[key] for m in null])
        # Small surrogate count: percentiles are exploratory descriptors ONLY.
        result[f"obs_{key}"]=float(value)
        result[f"sf1_mediana_{key}"]=float(np.median(simulations))
        result[f"sf1_min_{key}"]=float(simulations.min())
        result[f"sf1_max_{key}"]=float(simulations.max())
        result[f"obs_menor_todas_sf1_{key}"]=bool(value<simulations.min())
    return result


def summarize(rows):
    output={"n_janelas":len(rows),"n_simulacoes_sf1_por_janela":SURROGATES,
            "prefixo_sf1":PREFIX,"janela_deslizante_pode_sobrepor":True,
            "coordenadas":["z","iota","nu"],"comparacoes":{}}
    for model in ("mixture","gaussian"):
        for level in (25,50,75):
            key=f"{model}_J{level}"
            obs=np.array([r[f"obs_{key}"] for r in rows])
            n=np.array([r[f"sf1_mediana_{key}"] for r in rows])
            output["comparacoes"][key]={
                "jaccard_observado_mediana":float(np.median(obs)),
                "jaccard_sf1_mediana_entre_janelas":float(np.median(n)),
                "diferenca_observado_menos_sf1_mediana":float(np.median(obs-n)),
                "fracao_observada_menos_estavel_que_todas_simulacoes":float(
                    np.mean([r[f"obs_menor_todas_sf1_{key}"] for r in rows])),
            }
    output["limites"]=[
      "SF1 e um nulo de mecanismo parametrico ajustado ao prefixo, nao um espelho completo do mercado",
      "Quatro simulacoes por ponto tornam extrema imprecisa e impedem p confirmatorio",
      "Janelas deslizantes e prefixes se sobrepoem, estatisticas de janelas nao independentes",
      "HDR depende de grade, nivel, transformacao marginal e amostra; nao mede curvatura intrinseca",
      "SF1 precisa ter diagnosticos de qualidade de ajuste ao longo de muitas janelas antes de rejeicao",
      "Nao testa previsao, novidades fisicas ou informacao alem das tres series publicas",
    ]
    return output


def calibrate():
    import pandas as pd
    from sgvgeo.flow import default_sf1
    # Calibration uses an ordinary SF1, synthetic. Strong transient is also present.
    raw=simulate_sf1(default_sf1(),8500,seed=12)
    start=PREFIX+100
    stable=compare_real_and_simulated(raw,start=start,window=1500,step=60000,
                                      seed=8,surrogates=2)
    modified=raw.copy()
    # Future-only perturbation of the *taker flow* cannot change fit on prefix.
    idx=np.arange(start+450,start+1500)
    modified.loc[idx,"taker_buy"]=modified.loc[idx,"volume"] * .08
    change=compare_real_and_simulated(modified,start=start,window=1500,step=60000,
                                      seed=8,surrogates=2)
    return {"status":"CALIBRACAO_TRAJETORIA_SF1",
            "sf1_gerador_puro_obs":compact_keys(stable),
            "mudanca_fluxo_na_janela_obs":compact_keys(change),
            "identicos_parametros_fit_prefix":stable["sf1_param_garch"]==change["sf1_param_garch"],
            "nota":"Calibracao de teste de engenharia; efeito artificial apos prefixo, nao inferencia sobre BTC."}


def compact_keys(x):
    return {k:v for k,v in x.items()
            if k.startswith("obs_mixture_J") or k.startswith("sf1_mediana_mixture_J")}


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths:raise FileNotFoundError("Klines exploratorios ausentes")
    for path in paths:checked_exploratory_month(path.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    step=STEP[interval];win=WIN[interval]
    times=df.timestamp.to_numpy(np.int64)
    starts=sliding_origins(len(df),win,PREFIX,win//2,MAX_WINDOWS)
    rows=[]
    for j,start in enumerate(starts):
        # Pass only contiguous prefix + window to SF1; never fill gaps.
        seg=times[start-PREFIX:start+win]
        if not valid_segment(seg,np.zeros((len(seg),3)),step):
            continue
        try:
            row=compare_real_and_simulated(df,start=start,window=win,
                step=step,seed=SEED+j*100)
            rows.append(row)
        except (ValueError,np.linalg.LinAlgError,RuntimeError) as ex:
            print("SKIP",interval,start,repr(ex),flush=True)
    if not rows:raise RuntimeError("Nao foi possivel calibrar SF1 em nenhuma janela")
    path=ROOT/"reports"/f"SF1_DINAMICA_{interval}_janelas.csv"
    path.parent.mkdir(exist_ok=True)
    with path.open("w",newline="",encoding="utf8") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]))
        wr.writeheader();wr.writerows(rows)
    return {"status":"TRAJETORIAS_SF1_EXPLORATORIAS",
        "interval":interval,"n_arquivos":len(paths),
        "dados_confirmatorios":False,"resultado":summarize(rows)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--interval",choices=("synthetic","1m","1h"),required=True)
    a=ap.parse_args()
    result=calibrate() if a.interval=="synthetic" else real(a.interval)
    path=ROOT/"reports"/f"SF1_DINAMICA_{a.interval}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
