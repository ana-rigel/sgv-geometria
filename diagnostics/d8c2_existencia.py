"""D8-C2 — Critério 3 do G1 da reformulação C2 (PREREGISTRO_C2.md, seções 4 e 5).

Estatística primária: S = desvio-padrão, entre os blocos de reajuste (60 barras), da
média de ΔF no bloco — a variabilidade temporal da geometria preço–fluxo.
Secundária (não decide): média de ΔF.
Nulo: "GARCH + lei de impacto estacionária" (sgvgeo.flow.ImpactNull), ajustado no
mesmo segmento, 39 réplicas, p-valor por postos bilateral.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from common import Timer, dataset, save_json, slog
from sgvgeo.features import scale_coordinates
from sgvgeo.field import causal_geometry
from sgvgeo.flow import C2_COLS, ImpactNull, c2_coordinates

N, WINDOW, REFIT, EVERY = 4500, 1500, 60, 2
K = int(os.environ.get("SGV_K_NULL", 39))
H_MULT = float(os.environ.get("SGV_HMULT", 2.0))
BLOCK = int(os.environ.get("SGV_BLOCK", REFIT))  # tamanho do bloco de S (emendável só antes do dado real)


def stats_for(ohlcv: pd.DataFrame) -> dict:
    c = c2_coordinates(ohlcv)
    Z = scale_coordinates(c, cols=C2_COLS, how="rank_gauss", window=WINDOW, min_periods=300).to_numpy()
    h = H_MULT * WINDOW ** (-1 / 7)
    start = WINDOW + 300
    f = causal_geometry(Z, lam=None, window=WINDOW, refit=REFIT, h=h, start=start, every=EVERY)
    dF = pd.Series(slog(f["F_R"]) - slog(f["Fref_R"]), index=f.index)
    blocks = dF.groupby((dF.index - start) // BLOCK).mean()
    return {"S_desvio_medias_bloco": float(blocks.std(ddof=1)), "media_dF": float(dF.mean()),
            "mediana_dF": float(dF.median()), "n_blocos": int(len(blocks))}


def rank_p(val: float, vals: np.ndarray) -> float:
    dev = np.abs(vals - np.median(vals))
    return float((1 + np.sum(dev >= abs(val - np.median(vals)))) / (len(vals) + 1))


def main():
    raw, src = dataset(N)
    with Timer() as t:
        null = ImpactNull(raw)
        real = stats_for(raw)
        reps = [stats_for(null.sample(seed=500 + k)) for k in range(K)]
    rows = []
    for stat in ("S_desvio_medias_bloco", "media_dF", "mediana_dF"):
        vals = np.array([d[stat] for d in reps])
        rows.append({"estatistica": stat, "serie": real[stat], "nulo_media": vals.mean(),
                     "nulo_p05": np.quantile(vals, .05), "nulo_p95": np.quantile(vals, .95),
                     "z": (real[stat] - vals.mean()) / (vals.std(ddof=1) + 1e-12), "p": rank_p(real[stat], vals)})
    tab = pd.DataFrame(rows)
    print(tab.round(4).to_string(index=False))
    save_json(f"d8c2_existencia_h{H_MULT:g}x.json", {
        "fonte": src, "nulo": "GARCH + lei de impacto estacionária", "garch": null.params,
        "replicas": K, "bloco": BLOCK, "n_blocos": real["n_blocos"], "tempo_s": round(t.dt, 1),
        "criterio_3_passa": bool(rows[0]["p"] <= 0.05), "tabela": tab.round(5).to_dict("records")})


if __name__ == "__main__":
    main()
