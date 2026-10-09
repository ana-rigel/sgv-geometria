#!/usr/bin/env python3
"""SGV — auditoria descritiva de adequação do SF1, sem reavaliar hipótese geométrica.

Ajusta SF1 em 2000 candles passados; confronta 1500 (1m) ou 1008 (1h)
candles futuros observados com trajetórias novas do modelo ajustado.
As comparações cobrem distribuições, autocorrelações, heterocedasticidade,
vínculos contemporâneos e mudança da lei entre duas metades.

IMPORTANTE: transformação real e sintética é a MESMA flow_coordinates;
simulações incluem 1700 candles de aquecimento, mas recebem parâmetros
ajustados exclusivamente no prefixo. Quatro a oito simulações => envelopes
grosseiros, NÃO p-valores e NÃO testes confirmatórios. SF1 gera dados pelo
modelo, não incorpora microestrutura/efeitos exógenos.
"""
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from experiments.dinamica_formas_sf1 import sliding_origins, valid_segment
from experiments.persistencia_dependencia import checked_exploratory_month
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates, fit_sf1, simulate_sf1, default_sf1

PREFIX=2000
W={"1m":1500,"1h":1008}
STEP={"1m":60000,"1h":3600000}
BURN=1700
N_ORIGINS=8
N_SIM=8
SEED=20261009


def safe_corr(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if len(a)<10 or min(float(np.std(a)),float(np.std(b)))<1e-12:
        return 0.
    return float(np.corrcoef(a,b)[0,1])


def acf(x,lag):
    x=np.asarray(x,float)
    if len(x)<=lag+3: raise ValueError("Serie curta")
    return safe_corr(x[:-lag],x[lag:])


def diagnostics(coords):
    """Shape (n,3) = z, iota, nu; todas as métricas são finitas."""
    x=np.asarray(coords,float)
    if x.ndim!=2 or x.shape[1]!=3 or len(x)<100 or not np.isfinite(x).all():
        raise ValueError("Matriz de coordenadas invalida")
    z,iota,nu=x.T
    mid=len(x)//2
    rho0=safe_corr(z[:mid],iota[:mid])
    rho1=safe_corr(z[mid:],iota[mid:])
    metrics={}
    for name,v in (("z",z),("iota",iota),("nu",nu)):
        metrics[name+"_std"]=float(v.std(ddof=1))
        metrics[name+"_q05"]=float(np.quantile(v,.05))
        metrics[name+"_q95"]=float(np.quantile(v,.95))
        metrics[name+"_acf1"]=acf(v,1)
        metrics[name+"_acf10"]=acf(v,10)
        metrics[name+"_mean_shift_scaled"]=float(
            (v[mid:].mean()-v[:mid].mean())/(v.std(ddof=1)+1e-12))
        metrics[name+"_std_ratio_halves"]=float(
            (v[mid:].std(ddof=1)+1e-12)/(v[:mid].std(ddof=1)+1e-12))
    metrics["abs_z_acf1"]=acf(np.abs(z),1)
    metrics["abs_z_acf10"]=acf(np.abs(z),10)
    metrics["rho_z_iota"]=safe_corr(z,iota)
    metrics["rho_abs_z_nu"]=safe_corr(np.abs(z),nu)
    metrics["rho_iota_nu"]=safe_corr(iota,nu)
    metrics["rho_z_iota_change_halves"]=float(rho1-rho0)
    metrics["rho_z_iota_abs_change_halves"]=float(abs(rho1-rho0))
    return metrics


def aggregate_compare(observed,simulations):
    keys=list(observed.keys())
    assert all(list(s.keys())==keys for s in simulations)
    out={}
    for k in keys:
        arr=np.array([s[k] for s in simulations],float)
        if not np.isfinite(arr).all():raise ValueError("Simulacao nao finita")
        lo,hi=np.quantile(arr,[.1,.9])
        value=observed[k]
        out[k]={
            "observado":float(value),"sf1_median":float(np.median(arr)),
            "sf1_q10":float(lo),"sf1_q90":float(hi),
            "observado_fora_q10_q90":bool(value<lo or value>hi),
            "obs_minus_sf1_median":float(value-np.median(arr)),
        }
    return out


def evaluate(df,start,window,step,seed,n_sim=N_SIM):
    before=df.iloc[start-PREFIX:start].copy()
    future=df.iloc[start:start+window].copy()
    if len(before)!=PREFIX or len(future)!=window:raise ValueError("Faixas incompletas")
    both=df.iloc[start-PREFIX:start+window]
    ts=both.timestamp.to_numpy(np.int64)
    if not valid_segment(ts,np.zeros((len(ts),3)),step):
        raise ValueError("Gap")
    coords=flow_coordinates(both)[["z","iota","nu"]].to_numpy(float)[-window:]
    obs=diagnostics(coords)
    sf1=fit_sf1(before)
    if not sf1.garch.get("converged",False):
        raise ValueError("GARCH-t nao convergiu — nao usar controle")
    sims=[]
    for k in range(n_sim):
        simulated=simulate_sf1(sf1,window+BURN,
                               seed=seed+1000*k+1,step_ms=step)
        simx=flow_coordinates(simulated)[["z","iota","nu"]].to_numpy(float)[-window:]
        sims.append(diagnostics(simx))
    return {"asof_ms":int(ts[-1]+step),"start_idx":int(start),
            "garch_converged":True,"garch_params":{
                key:float(sf1.garch[key]) for key in ("omega","alpha","beta","nu")},
            "n_sim":n_sim,"metricas":aggregate_compare(obs,sims)}


def summarize(results):
    if not results:raise ValueError("Sem janelas validas")
    keys=list(results[0]["metricas"])
    out={}
    for k in keys:
        vals=[r["metricas"][k] for r in results]
        out[k]={
           "n_janelas":len(vals),
           "observado_mediana":float(np.median([v["observado"] for v in vals])),
           "sf1_mediana_entre_janelas":float(np.median([v["sf1_median"] for v in vals])),
           "fracao_obs_fora_envelope_q10_q90":float(np.mean([
               v["observado_fora_q10_q90"] for v in vals])),
           "mediana_diferenca_obs_sf1":float(np.median([
               v["obs_minus_sf1_median"] for v in vals])),
        }
    return out


def synthetic():
    source=simulate_sf1(default_sf1(),8500,seed=200)
    k=evaluate(source,start=2300,window=1500,step=60000,seed=900,n_sim=3)
    changed=source.copy()
    loc=np.arange(2300+750,2300+1500)
    changed.loc[loc,"taker_buy"]=changed.loc[loc,"volume"]*.05
    l=evaluate(changed,start=2300,window=1500,step=60000,seed=900,n_sim=3)
    # Prefixo causal implica mesmos parâmetros nulos e simulações.
    assert k["garch_params"]==l["garch_params"]
    for name in k["metricas"]:
        assert k["metricas"][name]["sf1_median"]==l["metricas"][name]["sf1_median"]
    return {"status":"CALIBRACAO_ADEQUACAO_SF1",
        "sf1_fit_garch_converged":True,
        "modificacao_futura_detectada":bool(
            k["metricas"]["rho_z_iota_change_halves"]["observado"]!=
            l["metricas"]["rho_z_iota_change_halves"]["observado"]),
        "nao_vazamento_prefixo_e_simulacoes":True,
        "aviso":"Engenharia de causalidade e sensibilidade, nao inferencia sobre BTC."}


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths:raise FileNotFoundError("Dados de exploração ausentes")
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    w=W[interval];step=STEP[interval]
    starts=sliding_origins(len(df),w,PREFIX,w//2,N_ORIGINS)
    results=[]; skips=[]
    for j,start in enumerate(starts):
        try:
            results.append(evaluate(df,start,w,step,SEED+100*j))
        except (ValueError,np.linalg.LinAlgError,RuntimeError) as exc:
            skips.append({"start":int(start),"motivo":str(exc)})
    if not results:raise RuntimeError("Nao ha nenhum SF1 valido; consultar motivos de descarte")
    table=ROOT/"reports"/f"AUDITORIA_SF1_{interval}_metricas.csv"
    table.parent.mkdir(exist_ok=True)
    with table.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=[
            "asof_ms","start_idx","metrica","observado","sf1_median",
            "sf1_q10","sf1_q90","observado_fora_q10_q90"])
        writer.writeheader()
        for r in results:
            for name,v in r["metricas"].items():
                writer.writerow({"asof_ms":r["asof_ms"],"start_idx":r["start_idx"],
                                 "metrica":name,**{k:v[k] for k in
                                 ("observado","sf1_median","sf1_q10","sf1_q90",
                                  "observado_fora_q10_q90")}})
    return {"status":"AUDITORIA_ADEQUACAO_SF1_EXPLORATORIA",
       "interval":interval,"origens_candidatas":len(starts),
       "avaliacoes_validas":len(results),"descartes":skips,
       "prefix_barras":PREFIX,"amostra_futura_barras":w,
       "simulacoes_por_origem":N_SIM,
       "n_arquivos_exploratorios":len(paths),
       "periodos_confirmatorios_lidos":False,
       "metricas":summarize(results),
       "avisos":[
          "Quantis q10-q90 obtidos de 8 simulacoes sao estimativas grosseiras, nao bandas 80% calibradas",
          "A proporcao de ultrapassagem nao e teste independente porque janelas se sobrepoem",
          "Metricas marginais nao incluem toda a dependencia conjunta e nao diagnosticam geometria intrinseca",
          "Antes de afirmar que SGV contem estrutura ausente do SF1, auditar maior numero de sims e GARCH",
          "A simulacao nao reproduz exogenos, sazonalidade intradiaria nem microestrutura completa"
       ]}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--interval",choices=("synthetic","1m","1h"),required=True)
    a=ap.parse_args()
    report=synthetic() if a.interval=="synthetic" else real(a.interval)
    out=ROOT/"reports"/f"AUDITORIA_SF1_{a.interval}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
