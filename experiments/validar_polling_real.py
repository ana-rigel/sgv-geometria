#!/usr/bin/env python3
"""SGV: observacao REAL de ETHUSDT spot por REST polling de candles FECHADOS.

Alternativa legitima ao WebSocket indisponivel no GitHub Actions (HTTP 451).
Nao finge ser push/stream de eventos. Mede a disponibilidade de barras
fechadas em consultas PERIODICAS, com fonte, horarios e correcoes.
Nao acessa qualquer BTC, nem os periodos reservados.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from experiments.stream_fotografia import ClosedCandleObserver
from experiments.validar_stream_real import api_json,bootstrap,closed_rest_rows,compare_rest,BAR_MS


def run_poll(*,symbol="ETHUSDT",seconds=200,target=2,poll_seconds=5.,window=120):
    if symbol not in ("ETHUSDT","BNBUSDT"):
        raise ValueError("BTC reservado nunca consultado")
    if seconds < 1 or not (1<=poll_seconds<=120):
        raise ValueError("configuracao de polling invalida")
    observer=ClosedCandleObserver(window=window,every=1,bar_ms=BAR_MS)
    monotonic=time.monotonic()
    result={
        "tipo":"OBSERVACAO_REST_POLLING_REAL_NAO_WEBSOCKET",
        "simbolo":symbol,"periodo_barra_ms":BAR_MS,
        "poll_interval_segundos":poll_seconds,
        "duracao_maxima_segundos":seconds,
        "alvo_barras_novas":target,"status":"INICIADO",
        "erros":[],"amostras":[],"requisoes":0,
        "ignorados_candles_parciais":0,"gaps":0,
    }
    try:
        result["bootstrap"]=bootstrap(observer,symbol)
        latest=observer.previous_open_ms
        while time.monotonic()-monotonic<seconds and len(result["amostras"])<target:
            try:
                srv=int(api_json("/api/v3/time")["serverTime"])
                rows=api_json("/api/v3/klines",{
                    "symbol":symbol,"interval":"1m","limit":5})
                now_ms=int(time.time()*1000)
                result["requisoes"]+=1
                result["ignorados_candles_parciais"]+=sum(
                    int(row[0])+BAR_MS>srv for row in rows)
                closed=closed_rest_rows(rows,srv)
                new=[r for r in closed if r["open_ms"]>latest]
                for r in new:
                    latest=r["open_ms"]
                    t1=time.perf_counter_ns()
                    snap=observer.on_closed_bar(
                        available_ms=max(now_ms,r["open_ms"]+BAR_MS),
                        **r)
                    work_ms=(time.perf_counter_ns()-t1)/1e6
                    rec={"open_ms":r["open_ms"],"received_ms":now_ms,
                         "server_time_ms":srv,"server_reported_minus_close_ms":
                             srv-(r["open_ms"]+BAR_MS),
                         "local_received_minus_close_ms":
                             now_ms-(r["open_ms"]+BAR_MS),
                         "processing_ms":work_ms,
                         "snapshot":snap is not None}
                    if snap is not None:
                        rec["fotografia"]={
                            "asof_ms":int(snap["asof_ms"]),
                            "rho_preco_fluxo":float(snap["corr"][0,1]),
                            "condition":float(snap["condition"]),
                            "mean":[float(x) for x in snap["mean"]],
                            "cov":[[float(x) for x in row] for row in snap["cov"]]}
                    try:
                        rec["auditoria_rest_posterior"]=compare_rest(r,symbol)
                    except Exception as ex:
                        rec["auditoria_rest_posterior"]={
                            "matched":None,"erro":repr(ex)}
                    result["amostras"].append(rec)
                    if len(result["amostras"])>=target:
                        break
            except Exception as ex:
                result["erros"].append(repr(ex))
                if len(result["erros"])>5:
                    break
            if time.monotonic()-monotonic<seconds and len(result["amostras"])<target:
                time.sleep(poll_seconds)
        result["gaps"]=observer.gaps
        result["n_novos_candles"]=len(result["amostras"])
        result["n_fotografias"]=sum(x["snapshot"] for x in result["amostras"])
        result["audit_ok"]=sum(x["auditoria_rest_posterior"]["matched"] is True
                               for x in result["amostras"])
        result["duracao_real_segundos"]=round(time.monotonic()-monotonic,2)
        if result["amostras"]:
            for key in ("server_reported_minus_close_ms",
                        "local_received_minus_close_ms","processing_ms"):
                a=np.array([x[key] for x in result["amostras"]],float)
                result[key]={"min":float(np.min(a)),"median":float(np.median(a)),
                             "max":float(np.max(a))}
        result["status"]=("PASSOU_OBSERVACAO_POR_POLLING" if
                          result["n_novos_candles"]>=target and
                          result["n_fotografias"]>=target and
                          result["audit_ok"]>=target and observer.gaps==0
                          else "INCONCLUSIVO_OU_FALHOU")
    except Exception as ex:
        result["status"]="ERRO_AQUECIMENTO"
        result["erros"].append(repr(ex))
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--symbol",choices=["ETHUSDT","BNBUSDT"],default="ETHUSDT")
    p.add_argument("--seconds",type=int,default=200)
    p.add_argument("--min-closed",type=int,default=2)
    p.add_argument("--poll-seconds",type=float,default=5.)
    p.add_argument("--window",type=int,default=120)
    p.add_argument("--out",type=Path,
                   default=ROOT/"reports"/"STREAM_REAL_REST_ETHUSDT.json")
    a=p.parse_args()
    r=run_poll(symbol=a.symbol,seconds=a.seconds,target=a.min_closed,
               poll_seconds=a.poll_seconds,window=a.window)
    a.out.parent.mkdir(exist_ok=True)
    a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(r,ensure_ascii=False,indent=2))
    if r["status"]!="PASSOU_OBSERVACAO_POR_POLLING":
        raise SystemExit(2)


if __name__=="__main__":
    main()
