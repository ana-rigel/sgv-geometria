"""L2 — mensurabilidade nos dados de exploração (PREREGISTRO_L2.md, seção 6.2).

Não calcula o alvo Y. Fixa ν por escala (GARCH-t no período de exploração inteiro)
e mede a confiabilidade de v_fluxo entre as barras pares e ímpares de cada metade
(Spearman entre as duas versões, ao longo das avaliações). Mínimo: 0,5. Se não
atingir, W cresce UMA vez: 1,5× e depois 2× (a primeira que atingir).

Uso: SGV_TAG=l2 python diagnostics/l2_mensurabilidade.py 1m data/BTCUSDT-1m-*.zip
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from common import Timer, save_json
from sgvgeo.data import fit_garch_t, load_binance_klines
from sgvgeo.l2 import evaluations

ESCALAS = {"1m": {"W": 1440, "S": 60}, "1h": {"W": 1008, "S": 24}}
MULTS_W = (1.0, 1.5, 2.0)
MINIMO = 0.5


def main():
    esc, paths = sys.argv[1], sys.argv[2:]
    cfg = ESCALAS[esc]
    df = load_binance_klines(paths, with_flow=True)
    r = np.log(df["close"]).diff().dropna().to_numpy()
    with Timer() as t:
        g = fit_garch_t(r - r.mean())
        nu = float(g["nu"])
        tent = {}
        escolhido = None
        for m in MULTS_W:
            W = int(round(cfg["W"] * m / 2) * 2)
            a = evaluations(df, W, cfg["S"], nu, split="par", with_target=False)
            b = evaluations(df, W, cfg["S"], nu, split="impar", with_target=False)
            j = a.merge(b, on="t", suffixes=("_par", "_impar"))
            rel = float(j["v_fluxo_par"].corr(j["v_fluxo_impar"], method="spearman"))
            tent[f"{m:g}x (W={W})"] = {"confiabilidade_v_fluxo": rel, "n_avaliacoes": int(len(j))}
            print(esc, m, W, round(rel, 3), len(j), flush=True)
            if rel >= MINIMO:
                escolhido = {"W": W, "multiplicador": m, "confiabilidade": rel}
                break
    save_json(f"l2_mensurabilidade_{esc}.json", {
        "escala": esc, "dados": f"{df['datetime'].iloc[0]} → {df['datetime'].iloc[-1]} ({len(df)} barras)",
        "garch_exploracao": g, "nu_fixado": nu, "S": cfg["S"], "tentativas": tent,
        "W_escolhido": escolhido, "aprovado": escolhido is not None, "tempo_s": round(t.dt, 1)})


if __name__ == "__main__":
    main()
