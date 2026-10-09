"""Validação sintética independente do coletor Binance WebSocket."""
import json
import numpy as np
import pytest
from experiments.validar_stream_real import (
    kline_event, closed_rest_rows, row_to_candle, capture, BAR_MS,
)


def event(t=1760000000000,*,closed=True,symbol="ETHUSDT"):
    return {"e":"kline","E":t+60045,"s":symbol,
            "k":{"t":t,"T":t+BAR_MS-1,"i":"1m","x":closed,
                 "c":"3000.25","v":"125.5","V":"70.2"}}


def test_rejeita_kline_parcial():
    assert kline_event(event(closed=False),"ETHUSDT") is None


def test_kline_final_preserva_tempo_e_quantidades():
    out=kline_event(event(),"ETHUSDT")
    assert out["open_ms"]==1760000000000
    assert out["close"]==3000.25
    assert out["volume"]==125.5
    assert out["taker_buy"]==70.2


def test_simbolo_e_intervalo_invalidos_falham_fechado():
    with pytest.raises(ValueError,match="Unexpected symbol"):
        kline_event(event(),"BNBUSDT")
    e=event()
    e["k"]["i"]="5m"
    with pytest.raises(ValueError,match="Unexpected interval"):
        kline_event(e,"ETHUSDT")
    e=event()
    e["k"]["T"]+=1
    with pytest.raises(ValueError,match="close time mismatch"):
        kline_event(e,"ETHUSDT")


def test_resto_parcial_nao_usa_info_do_futuro():
    t=1760000000000
    def row(x):
        return [x,"0","0","0","5.0","1.2",x+59999,"0",6,"0.8"]
    items=[row(t),row(t+BAR_MS)]
    out=closed_rest_rows(items,t+BAR_MS+30000)
    assert len(out)==1
    assert out[0]["open_ms"]==t


def test_resto_sem_candle_final_eh_erro():
    t=1760000000000
    row=[t,"0","0","0","5.0","1.2",t+59999,"0",6,"0.8"]
    with pytest.raises(ValueError,match="integralmente fechados"):
        closed_rest_rows([row],t+100)


def test_stream_nao_acessa_btc_reservado():
    with pytest.raises(ValueError,match="Somente ativos independentes"):
        capture(symbol="BTCUSDT",duration=1)
