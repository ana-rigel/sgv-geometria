#!/usr/bin/env python3
"""SGV: núcleo incremental da fotografia informacional por candle FECHADO.

Reproduz X_t=(z,iota,nu) sem ler o futuro: retornos anteriores, sigma das
60 barras anteriores e mediana do log-volume das 1500 anteriores. O estado
gaussiano de uma janela fixa W e sua Fisher de localização são emitidos no
fechamento da barra, com atualização em O(W) por amostra para o protótipo.

Não conecta a exchange, não observa ticks intra-candle e não promete latência
de rede: é uma interface pronta para integrar com coletor de eventos fechados.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path
from time import perf_counter_ns

import numpy as np

from experiments.fotografia_informacional import gaussian_snapshot

ROOT=Path(__file__).resolve().parents[1]


class ClosedCandleObserver:
    """Um estado por candle fechado. Falha fechada em gaps e dados inválidos."""

    def __init__(self, *, window=600, every=1, bar_ms=60_000):
        if window < 24 or every < 1 or bar_ms < 1:
            raise ValueError("janela/cadencia/tamanho inválidos")
        self.window,self.every,self.bar_ms=window,every,bar_ms
        self.return_history=deque(maxlen=60)
        self.volume_history=deque(maxlen=1500)
        self.points=deque(maxlen=window)
        self.previous_close=None
        self.previous_open_ms=None
        self.index=-1
        self.gaps=0

    def _clear_history(self):
        self.return_history.clear()
        self.volume_history.clear()
        self.points.clear()
        self.previous_close=None

    def on_closed_bar(self, *, open_ms, available_ms, close, volume, taker_buy):
        """available_ms deve ser >= open_ms+bar_ms, nunca candle parcial.

        Retorna None durante aquecimento, gaps ou entre emissões.
        """
        t=int(open_ms); avail=int(available_ms)
        if avail < t+self.bar_ms:
            raise ValueError("Candle parcial: não pode fotografar o futuro")
        if self.previous_open_ms is not None and t <= self.previous_open_ms:
            raise ValueError("Candles não estritamente ordenados")
        if self.previous_open_ms is not None and t-self.previous_open_ms!=self.bar_ms:
            self.gaps+=1
            self._clear_history()
        self.previous_open_ms=t
        self.index+=1
        c,v,b=float(close),float(volume),float(taker_buy)
        if not (np.isfinite(c) and c>0 and np.isfinite(v) and v>=0
                and np.isfinite(b) and 0 <= b <= v+1e-9):
            self._clear_history()
            return None

        r=np.log(c)-np.log(self.previous_close) if self.previous_close is not None else np.nan
        sigma=(float(np.std(self.return_history,ddof=1))
               if len(self.return_history)>=30 else np.nan)
        z=r/sigma if np.isfinite(r) and np.isfinite(sigma) and sigma>0 else np.nan
        iota=float(np.clip(2*b/v-1,-1,1)) if v>0 else 0.
        ell=float(np.log(max(v,1e-12)))
        nu=(ell-float(np.median(self.volume_history))
            if len(self.volume_history)>=300 else np.nan)

        self.previous_close=c
        if np.isfinite(r):
            self.return_history.append(r)
        self.volume_history.append(ell)

        pt=np.array([z,iota,nu],float)
        if np.isfinite(pt).all():
            self.points.append(pt)
        else:
            self.points.clear()

        if len(self.points)<self.window or (self.index-(self.window-1))%self.every:
            return None
        try:
            snap=gaussian_snapshot(np.array(self.points))
        except ValueError:
            return None
        return {"asof_ms": t+self.bar_ms, "processed_at_ms": avail,
                "latencia_disponibilidade_ms": avail-(t+self.bar_ms),
                "t":self.index, "mean":snap["mean"],
                "cov":snap["cov"], "fisher_location":snap["fisher_location"],
                "corr":snap["corr"], "condition":snap["condition"]}


def benchmark(*, n=6000, window=600, seed=123):
    rng=np.random.default_rng(seed)
    ret=rng.normal(0,0.001,n)
    close=60_000*np.exp(np.cumsum(ret))
    volume=np.exp(4.5+0.5*rng.normal(size=n))
    impact=np.tanh(0.8*(ret/.001)+.45*rng.normal(size=n))
    buy=(impact+1)/2*volume
    stream=ClosedCandleObserver(window=window,every=1,bar_ms=60_000)
    tim=[];n_snap=0
    for j in range(n):
        open_ms=1_760_000_000_000+j*60_000
        start=perf_counter_ns()
        x=stream.on_closed_bar(open_ms=open_ms,available_ms=open_ms+60_000,
                               close=close[j],volume=volume[j],taker_buy=buy[j])
        tim.append((perf_counter_ns()-start)/1e6)
        n_snap+=x is not None
    after=np.array(tim[window+300:])
    return {"status":"REPLAY_STREAM_SINTETICO","n_barras":n,
            "janela":window,"fotografias_emitidas":n_snap,
            "atualizacao_a_cada":"candle fechado","latencia_processamento_mediana_ms":float(np.median(after)),
            "latencia_processamento_p99_ms":float(np.quantile(after,.99)),
            "nao_mede":"tempo de rede, qualidade do provedor de dados, atrasos da exchange ou latencia end-to-end"}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--benchmark",type=int,default=6000)
    args=p.parse_args()
    result=benchmark(n=args.benchmark)
    path=ROOT/"reports"/"FOTO_STREAM_BENCHMARK.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
