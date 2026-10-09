#!/usr/bin/env python3
"""SGV observacional: captura REAL ETHUSDT spot candle FECHADO via WebSocket.

Objetivo: medir disponibilidade, integridade, observador causal e auditabilidade.
NAO e backtest, NAO opera, NAO usa periodos BTC confirmatorios.

1) REST busca somente os ultimos candles inteiramente fechados para aquecimento.
2) WebSocket recebe klines; ignora x=false e duplicatas. NUNCA emite snapshot
   com dados futuros; disponibilidade e anotada ao receber x=true.
3) REST consultado APOS evento para verificar a barra; nao alimenta o estado.
4) Relatorio explicita outages, dados divergentes, erros e lacunas.
Atrasos medidos em relacao ao timestamp no payload nao sao prova de
latencia end-to-end nem de sincronizacao perfeita entre relogios.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from experiments.stream_fotografia import ClosedCandleObserver

API="https://data-api.binance.vision"
WS="wss://stream.binance.com:9443/ws/"
BAR_MS=60000


def api_json(path,params=None,timeout=12):
    url=API+path
    if params:
        url+="?"+urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(
            url,headers={"User-Agent":"SGV-Observational-Research/1.0"}),
            timeout=timeout) as resp:
        return json.load(resp)


def row_to_candle(row):
    return {"open_ms":int(row[0]),"close":float(row[4]),
            "volume":float(row[5]),"taker_buy":float(row[9])}


def closed_rest_rows(rows,server_ms):
    data=[row_to_candle(row) for row in rows
          if int(row[0])+BAR_MS <= server_ms]
    if not data:
        raise ValueError("REST nao retornou candles integralmente fechados")
    return data


def kline_event(obj,symbol):
    """Retorna None se nao for kline final: nenhuma barra parcial passa."""
    if obj.get("e")!="kline":
        return None
    if obj.get("s")!=symbol:
        raise ValueError("Unexpected symbol")
    k=obj["k"]
    if k.get("i")!="1m":
        raise ValueError("Unexpected interval")
    if not k.get("x",False):
        return None
    t=int(k["t"])
    if int(k["T"]) != t+BAR_MS-1:
        raise ValueError("Kline close time mismatch")
    return {"open_ms":t,"close":float(k["c"]),
            "volume":float(k["v"]),"taker_buy":float(k["V"]),
            "event_ms":int(obj["E"])}


def bootstrap(observer,symbol,warmup=700):
    # Server timestamp faz filtro de candles fechados, incluindo descartar
    # o candle corrente mesmo se REST o fornecer com OHLC parciais.
    before=int(api_json("/api/v3/time")["serverTime"])
    rows=api_json("/api/v3/klines",{"symbol":symbol,"interval":"1m",
                                 "limit":warmup})
    after=int(api_json("/api/v3/time")["serverTime"])
    close_data=closed_rest_rows(rows,before)
    if len(close_data) < observer.window+300:
        raise ValueError("Warmup REST insuficiente; sem fotografia confiavel")
    for c in close_data:
        observer.on_closed_bar(available_ms=c["open_ms"]+BAR_MS,**c)
    return {
        "ultimo_bootstrap_open_ms":int(close_data[-1]["open_ms"]),
        "n_bootstrap":len(close_data),"time_server_before_ms":before,
        "time_server_after_ms":after,
        "server_time_roundtrip_ms":after-before,
    }


def compare_rest(c,symbol):
    # Auditoria POS evento; nao usa REST para predicao/retrato no instante.
    rows=api_json("/api/v3/klines",{
        "symbol":symbol,"interval":"1m","startTime":int(c["open_ms"]),
        "limit":1})
    if not rows or int(rows[0][0])!=c["open_ms"]:
        return {"matched":False,"error":"REST sem mesma barra"}
    rest=row_to_candle(rows[0])
    ok=all(np.isclose(float(c[field]),float(rest[field]),
                      rtol=1e-7,atol=1e-10)
           for field in ("close","volume","taker_buy"))
    return {"matched":bool(ok),"rest_open_ms":rest["open_ms"],
            "max_abs_difference":float(max(abs(c[f]-rest[f]) for f in
                ("close","volume","taker_buy")))}


def capture(*, symbol="ETHUSDT", duration=215, target=2, window=120):
    from websocket import create_connection, WebSocketTimeoutException
    if symbol not in ("ETHUSDT","BNBUSDT"):
        raise ValueError("Somente ativos independentes dos periodos reservados BTC")
    observer=ClosedCandleObserver(window=window,every=1,bar_ms=BAR_MS)
    start_monotonic=time.monotonic()
    clock_ms=lambda: int(time.time()*1000)
    captures=[]
    report={
        "tipo":"TESTE_OBSERVACIONAL_STREAMING_SPOT",
        "simbolo":symbol,"intervalo":"1m","limite_segundos":duration,
        "alvo_barras_ws":target,"janela":window,
        "feed":"Binance Spot public REST+WebSocket",
        "sem_btc_reservado":True,"acesso_futuro_para_estado":False,
        "status":"INICIADO","erros":[],"parciais_ignoradas":0,
        "duplicatas_ignoradas":0,"lacunas_detectadas":0,
        "snapshot_emitidos_ws":0,
    }
    try:
        report["bootstrap"]=bootstrap(observer,symbol)
        previous=observer.previous_open_ms
        report["bootstrap_completa_ms"]=clock_ms()
        url=WS+symbol.lower()+"@kline_1m"
        report["endpoint"]="spot kline_1m"
        # Reconnects suportados apenas para monitoramento: se houver lacuna,
        # o observador zera o estado, sem preenchimento futuro.
        while len(captures)<target and time.monotonic()-start_monotonic<duration:
            ws=None
            try:
                ws=create_connection(url,timeout=12)
                ws.settimeout(6)
                while len(captures)<target and time.monotonic()-start_monotonic<duration:
                    try:
                        raw=ws.recv()
                    except WebSocketTimeoutException:
                        continue
                    receive_ms=clock_ms()
                    event=kline_event(json.loads(raw),symbol)
                    if event is None:
                        report["parciais_ignoradas"]+=1
                        continue
                    if event["open_ms"]<=previous:
                        report["duplicatas_ignoradas"]+=1
                        continue
                    previous=event["open_ms"]
                    process_start=time.perf_counter_ns()
                    snap=observer.on_closed_bar(
                        open_ms=event["open_ms"],
                        available_ms=max(receive_ms,event["open_ms"]+BAR_MS),
                        close=event["close"],volume=event["volume"],
                        taker_buy=event["taker_buy"])
                    duration_ms=(time.perf_counter_ns()-process_start)/1e6
                    c={"open_ms":event["open_ms"],"event_ms":event["event_ms"],
                       "received_ms":receive_ms,
                       "exchange_end_ms":event["open_ms"]+BAR_MS,
                       "event_minus_close_ms":event["event_ms"]-(event["open_ms"]+BAR_MS),
                       "receipt_minus_close_ms":receive_ms-(event["open_ms"]+BAR_MS),
                       "receipt_minus_event_ms":receive_ms-event["event_ms"],
                       "processing_ms":duration_ms,
                       "snapshot":snap is not None}
                    if snap is not None:
                        report["snapshot_emitidos_ws"]+=1
                        c["foto"]={
                            "asof_ms":snap["asof_ms"],
                            "rho_price_flow":float(snap["corr"][0,1]),
                            "condition":float(snap["condition"]),
                            "mu":[float(z) for z in snap["mean"]],
                            "cov":[[float(z) for z in row] for row in snap["cov"]]}
                    try:
                        c["rest_audit"]=compare_rest(event,symbol)
                    except Exception as exc:
                        c["rest_audit"]={"matched":None,"error":repr(exc)}
                    captures.append(c)
                break
            except Exception as exc:
                report["erros"].append("websocket: "+repr(exc))
                if len(report["erros"])>=3:
                    break
                time.sleep(3)
            finally:
                if ws is not None:
                    ws.close()
        report["capturas"]=captures
        report["lacunas_detectadas"]=observer.gaps
        report["duracao_real_segundos"]=round(time.monotonic()-start_monotonic,3)
        report["barras_ws_fechadas"]=len(captures)
        report["rest_auditoria_iguais"]=sum(
            c["rest_audit"]["matched"] is True for c in captures)
        report["rest_auditoria_divergentes"]=sum(
            c["rest_audit"]["matched"] is False for c in captures)
        report["rest_auditoria_inconclusiva"]=sum(
            c["rest_audit"]["matched"] is None for c in captures)
        if captures:
            for label,field in (("latencia_desde_fechamento_ms",
                                  "receipt_minus_close_ms"),
                                 ("latencia_recepcao_evento_ms",
                                  "receipt_minus_event_ms"),
                                 ("processamento_ms","processing_ms")):
                vals=np.array([c[field] for c in captures],float)
                report[label]={"mediana":float(np.median(vals)),
                               "max":float(vals.max())}
        # Falha fechada: nao alegar sucesso caso dados escassos, divergencia
        # de REST, janelas incompletas, ou gaps durante o periodo.
        report["status"]=("PASSOU_STREAM_CURTO" if len(captures)>=target
             and report["rest_auditoria_iguais"]==len(captures)
             and observer.gaps==0 and report["snapshot_emitidos_ws"]>=target
             else "INCONCLUSIVO_OU_FALHOU")
    except Exception as exc:
        report["status"]="FALHOU_BOOTSTRAP_OU_FEED"
        report["erros"].append(repr(exc))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--symbol",choices=["ETHUSDT","BNBUSDT"],default="ETHUSDT")
    p.add_argument("--seconds",type=int,default=215)
    p.add_argument("--min-closed",type=int,default=2)
    p.add_argument("--window",type=int,default=120)
    p.add_argument("--out",type=Path,default=ROOT/"reports"/"STREAM_REAL_ETHUSDT.json")
    a=p.parse_args()
    report=capture(symbol=a.symbol,duration=a.seconds,
                   target=a.min_closed,window=a.window)
    a.out.parent.mkdir(exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    if report["status"]!="PASSOU_STREAM_CURTO":
        raise SystemExit(2)


if __name__=="__main__":
    main()
