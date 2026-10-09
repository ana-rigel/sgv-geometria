"""Observador incremental: igualdade com replay histórico e proteção temporal."""
import numpy as np
import pandas as pd
import pytest

from experiments.stream_fotografia import ClosedCandleObserver, benchmark
from experiments.fotografia_informacional import direct_snapshots
from sgvgeo.flow import flow_coordinates


def sample(n=1100):
    rng=np.random.default_rng(33)
    r=rng.normal(0,1e-3,n)
    close=60_000*np.exp(np.cumsum(r))
    volume=np.exp(4.0+0.4*rng.normal(size=n))
    iota=np.tanh(0.7*r/1e-3+0.3*rng.normal(size=n))
    taker_buy=(1+iota)*volume/2
    ts=1_760_000_000_000+60_000*np.arange(n,dtype=np.int64)
    return pd.DataFrame({"timestamp":ts, "close":close, "volume":volume,
                         "taker_buy":taker_buy})


def run_stream(df,window=120,every=10):
    stream=ClosedCandleObserver(window=window,every=every,bar_ms=60_000)
    out=[]
    for row in df.itertuples():
        r=stream.on_closed_bar(open_ms=row.timestamp,
           available_ms=int(row.timestamp)+60_000,
           close=row.close,volume=row.volume,taker_buy=row.taker_buy)
        if r is not None:
            out.append(r)
    return out


def test_equivalencia_candle_a_candle_com_estatistica_em_lote():
    data=sample()
    X=flow_coordinates(data)[["z","iota","nu"]].to_numpy(float)
    batch=direct_snapshots(X,data.timestamp.to_numpy(),window=120,stride=10,bar_ms=60_000)
    stream=run_stream(data,window=120,every=10)
    assert len(stream)==len(batch) and len(batch)>30
    for a,b in zip(stream,batch):
        assert a["t"]==b["t"] and a["asof_ms"]==b["asof_ms"]
        np.testing.assert_allclose(a["mean"],b["mu"],rtol=1e-10,atol=1e-10)
        np.testing.assert_allclose(a["cov"],b["cov"],rtol=1e-10,atol=1e-10)
        assert abs(a["corr"][0,1]-b["rho_price_flow"])<1e-10


def test_future_does_not_change_snapshots_already_published():
    d=sample()
    a=run_stream(d.iloc[:950])
    d2=d.copy()
    d2.loc[950:,"close"]*=1.5
    d2.loc[950:,"taker_buy"]=0.01*d2.loc[950:,"volume"]
    b=run_stream(d2)
    assert len(a)>30
    for s,t in zip(a,b[:len(a)]):
        assert s["asof_ms"]==t["asof_ms"]
        np.testing.assert_array_equal(s["cov"],t["cov"])


def test_parcial_nao_pode_ser_processado():
    s=ClosedCandleObserver(window=60)
    with pytest.raises(ValueError,match="Candle parcial"):
        s.on_closed_bar(open_ms=1_000_000,available_ms=1_050_000,
                        close=100,volume=2,taker_buy=1)
    assert s.index==-1


def test_gap_limpa_estado_e_bloqueia_transicao_falsa():
    d=sample(1050)
    d.loc[850:,"timestamp"]+=60_000
    stream=run_stream(d,window=120,every=10)
    assert all(not(850<=x["t"]<1050) for x in stream)


def test_benchmark_de_6000_barras_sinteticas_e_finito():
    report=benchmark(n=1500,window=120,seed=3)
    assert report["fotografias_emitidas"]>500
    assert np.isfinite(report["latencia_processamento_p99_ms"])
    assert report["latencia_processamento_p99_ms"]>0
