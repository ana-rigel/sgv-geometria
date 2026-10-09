"""Testes de resolução temporal e de risco de joins com timestamps futuros.

Não altera o motor legado; explicita dois mecanismos responsáveis por sinais
aparentemente úteis que não são causalmente disponíveis.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def step_contrast_fraction(W: int, lag: int) -> float:
    """Resposta de contraste entre duas meias-janelas à mudança em degrau.

    Prova exata para média de parâmetro em cada metade. Aproximação de 1a ordem
    para uma regressão com regressores estacionários, NÃO poder empírico do L2.
    """
    if W < 2 or W % 2 or lag < 0 or lag > W // 2:
        raise ValueError("W par, 0<=lag<=W/2")
    t0 = W + 1
    theta = np.r_[np.zeros(t0), np.ones(W + 2)]
    t = t0 + lag
    a = theta[t-W:t-W//2].mean()
    b = theta[t-W//2:t].mean()
    return float(b-a)


def test_l2_precoce_janela_1440_dilui_alternativa():
    # L2 1m: W=1440, S=60, mudança de vol no passo 2S após fluxo.
    assert np.isclose(step_contrast_fraction(1440, 120), 1/6)


def test_l2_precoce_janela_1008_dilui_ainda_mais():
    # L2 1h: W=1008, S=24, antecedência = 48 barras.
    assert np.isclose(step_contrast_fraction(1008, 48), 2*48/1008)


def test_nearest_asof_pode_usar_medida_futura():
    # O código sgv_runtime usa direction='nearest', inclusive em runtime.
    ts = pd.date_range("2026-01-01", periods=4, freq="min", tz="UTC")
    trader = pd.DataFrame({"timestamp":[ts[0],ts[1],ts[2]], "preco":[1,2,3]})
    geometry = pd.DataFrame({"timestamp":[ts[0],ts[3]],"geometria":[10,99]})
    nearest = pd.merge_asof(trader, geometry, on="timestamp",
                            direction="nearest", tolerance=pd.Timedelta("2min"))
    causal = pd.merge_asof(trader, geometry, on="timestamp",
                           direction="backward", tolerance=pd.Timedelta("2min"))
    assert nearest.loc[2, "geometria"] == 99  # dado de t+1 minuto
    assert causal.loc[2, "geometria"] == 10    # dado no passado
