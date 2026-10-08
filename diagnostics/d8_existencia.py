"""D8 — Teste de existência: a geometria da série difere da de séries substitutas?

Se a geometria do mercado real for indistinguível da de uma série GARCH ajustada a
ele (mesma volatilidade agrupada, mesmas caudas, nenhuma estrutura além disso), não
há geometria própria a testar adiante. Aqui, com dados sintéticos, o "real" já É um
GARCH: o resultado esperado é z ≈ 0 contra o substituto GARCH (calibração do teste)
e diferenças contra substitutos que destroem o agrupamento de volatilidade
(embaralhado, IAAFT), o que mede a sensibilidade do teste.

Com poucas réplicas o desvio-padrão do nulo é mal estimado e o z engana (numa
rodada exploratória, não arquivada, 3 réplicas deram z = −4 contra o próprio GARCH).
Por isso os três nulos usam 19 réplicas e p-valor por postos. Atenção: com 19
réplicas, p ≤ 0,05 exige que a série seja a mais extrema das 20, sem folga.

Parâmetros fixados a partir de D7 (região confiável): gaussianização por postos,
h = 2 × Scott, janela 1500, reajuste 60, avaliação a cada 2 barras.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from common import Timer, dataset, save_json, slog
from sgvgeo.data import (fit_garch_t, ohlcv_from_returns, surrogate_garch, surrogate_iaaft,
                         surrogate_shuffle)
from sgvgeo.features import legacy_coordinates, scale_coordinates
from sgvgeo.field import causal_geometry

N, WINDOW, REFIT, EVERY = 4500, 1500, 60, 2
K_GARCH = int(os.environ.get("SGV_K_GARCH", 19))  # 19 → resolução 0,05; Fase 1 usa 39 (0,025)
K_OTHER = int(os.environ.get("SGV_K_OTHER", 19))
H_MULT = float(os.environ.get("SGV_HMULT", 2.0))


def stats_for(ohlcv: pd.DataFrame) -> dict:
    coords = legacy_coordinates(ohlcv)
    Z = scale_coordinates(coords, how="rank_gauss", window=WINDOW, min_periods=300).to_numpy()
    h = H_MULT * WINDOW ** (-1 / 7)
    f = causal_geometry(Z, lam=None, window=WINDOW, refit=REFIT, h=h, start=WINDOW + 300, every=EVERY)
    f["dF"] = slog(f["F_R"]) - slog(f["Fref_R"])
    neg = f["H_neg"]
    return {
        "H_frac_positiva_definida": float((neg == 0).mean()),
        "H_troca_assinatura": float((neg.diff().fillna(0) != 0).mean()),
        "H_mediana_slog_R": float(np.median(slog(f["H_R"]))),
        "F_mediana_slog_R": float(np.nanmedian(slog(f["F_R"]))),
        "dF_mediana": float(np.nanmedian(f["dF"])),
        "dF_media": float(np.nanmean(f["dF"])),
        "F_mediana_log_det": float(np.nanmedian(np.log(f["F_det"].clip(lower=1e-300)))),
        "mediana_phi": float(f["phi"].median()),
        "mediana_grad_phi": float(f["grad_phi_norm"].median()),
        "autocorr_phi": float(f["phi"].autocorr(1)),
    }


def main():
    raw, src = dataset(N)
    r = np.log(raw["close"]).diff().fillna(0).to_numpy()
    params = fit_garch_t(r)
    p0 = float(raw["close"].iloc[0])
    with Timer() as t:
        real = stats_for(raw)
        sur = {"garch_ajustado": [], "iaaft": [], "embaralhado": []}
        for k in range(K_GARCH):
            sur["garch_ajustado"].append(stats_for(ohlcv_from_returns(surrogate_garch(r, seed=100 + k, params=params), p0=p0)))
        for k in range(K_OTHER):
            sur["iaaft"].append(stats_for(ohlcv_from_returns(surrogate_iaaft(r, seed=200 + k), p0=p0)))
            sur["embaralhado"].append(stats_for(ohlcv_from_returns(surrogate_shuffle(r, seed=300 + k), p0=p0)))
    rows = []
    for stat, val in real.items():
        row = {"estatistica": stat, "serie": val}
        for name, lst in sur.items():
            vals = np.array([d[stat] for d in lst])
            row[f"{name}_media"] = vals.mean()
            row[f"{name}_z"] = (val - vals.mean()) / (vals.std(ddof=1) + 1e-12)
            # p-valor bilateral por postos (Monte Carlo): posição da série entre as réplicas
            dev = np.abs(vals - np.median(vals))
            row[f"{name}_p"] = (1 + np.sum(dev >= abs(val - np.median(vals)))) / (len(vals) + 1)
        rows.append(row)
    tab = pd.DataFrame(rows)
    print(tab.round(3).to_string(index=False))
    save_json(f"d8_existencia_h{H_MULT:g}x.json", {"fonte": src, "garch_ajustado": params, "replicas": {"garch_ajustado": K_GARCH, "iaaft": K_OTHER, "embaralhado": K_OTHER},
                                     "tempo_s": round(t.dt, 1), "tabela": tab.round(4).to_dict("records")})


if __name__ == "__main__":
    main()
