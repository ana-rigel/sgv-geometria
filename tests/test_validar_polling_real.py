"""Controle de acesso e inicializacao do monitor publico por polling."""
import pytest
from experiments.validar_polling_real import run_poll


def test_nunca_observar_btc_reservado():
    with pytest.raises(ValueError,match="BTC reservado"):
        run_poll(symbol="BTCUSDT",seconds=1)


def test_polling_precisa_de_intervalo_valido():
    with pytest.raises(ValueError,match="invalida"):
        run_poll(symbol="ETHUSDT",seconds=1,poll_seconds=0)
