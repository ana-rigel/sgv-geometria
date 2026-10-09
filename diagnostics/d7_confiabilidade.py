"""D7 — A curvatura é mensurável? Confiabilidade sob reamostragem.

Antes de perguntar se a curvatura prevê algo, é preciso saber se ela é uma
propriedade estável do estado ou um artefato da amostra que alimenta o KDE.
Para cada barra avaliada, a janela de ajuste (1500 barras passadas) é dividida em
duas metades intercaladas (pares/ímpares), cada metade gera seu KDE, e a mesma
grandeza é calculada nos dois. Confiabilidade = correlação de postos entre as duas
versões, ao longo das barras. 1 = propriedade do estado; 0 = ruído de amostra.

Repetido para larguras de banda h = c × Scott(1500), c ∈ {0,5; 1; 2; 3; 4} — o MESMO h
que D4 e D8 usam na janela inteira (cada metade tem 750 barras, então esta medida é
conservadora). Largura maior dá mais estabilidade, mas aproxima a densidade de uma
gaussiana só (espaço plano).

Inclui a referência gaussiana (Fref) e o excesso ΔF = slog R(F) − slog R(Fref).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import Timer, coordinates, dataset, out_path, save_json, slog
from sgvgeo.features import scale_coordinates
from sgvgeo.geometry import (curvature, gaussian_reference_fisher_metric, local_fisher_metric,
                             observed_information_metric)
from sgvgeo.kde import GaussianKDE

N, WINDOW, N_EVAL = 6000, 1500, 240
MULTS = (0.5, 1.0, 2.0, 3.0, 4.0)


def quantities(kde: GaussianKDE, x: np.ndarray) -> dict:
    cH = curvature(observed_information_metric(kde), x)
    q = {"phi": kde.phi(x), "|∇φ|": float(np.linalg.norm(kde.grad_phi(x))),
         "H indefinida (0/1)": float(cH.eigvals.min() < 0), "H slog det": float(slog(cH.det)),
         "H slog R": float(slog(cH.R))}
    try:
        q["F slog R"] = float(slog(curvature(local_fisher_metric(kde), x).R))
    except np.linalg.LinAlgError:
        q["F slog R"] = np.nan
    try:
        q["Fref slog R"] = float(slog(curvature(gaussian_reference_fisher_metric(kde), x).R))
    except np.linalg.LinAlgError:
        q["Fref slog R"] = np.nan
    q["ΔF"] = q["F slog R"] - q["Fref slog R"]
    return q


def main():
    raw, src = dataset(N)
    coords, cols, _ = coordinates(raw)
    rng = np.random.default_rng(0)
    res = {"fonte": src, "janela": WINDOW, "barras_avaliadas": N_EVAL}
    for how in ("rank_gauss", "robust_z"):
        Z = scale_coordinates(coords, cols=cols, how=how, window=WINDOW, min_periods=300).to_numpy()
        ts = np.sort(rng.choice(np.arange(WINDOW + 300, len(Z)), N_EVAL, replace=False))
        h0 = WINDOW ** (-1 / 7)  # Scott da janela inteira, igual a D4/D8
        rows = []
        with Timer() as t:
            for c in MULTS:
                A, B = [], []
                for tt in ts:
                    past = Z[tt - WINDOW:tt]
                    past = past[np.all(np.isfinite(past), axis=1)]
                    x = Z[tt]
                    if not np.all(np.isfinite(x)):
                        continue
                    A.append(quantities(GaussianKDE(past[0::2], c * h0), x))
                    B.append(quantities(GaussianKDE(past[1::2], c * h0), x))
                A, B = pd.DataFrame(A), pd.DataFrame(B)
                for col in A.columns:
                    ok = A[col].notna() & B[col].notna()
                    rel = A.loc[ok, col].corr(B.loc[ok, col], method="spearman")
                    rows.append({"multiplicador_h": c, "grandeza": col, "confiabilidade": rel,
                                 "mediana_abs": float(np.median(np.abs(A.loc[ok, col])))})
        tab = pd.DataFrame(rows)
        piv = tab.pivot(index="grandeza", columns="multiplicador_h", values="confiabilidade")
        flat = tab[tab.grandeza == "H slog R"].set_index("multiplicador_h")["mediana_abs"]
        print(how, f"({t.dt:.0f}s)"); print(piv.round(3).to_string()); print("mediana |slog R| (H):", flat.round(3).to_dict())
        res[how] = {"confiabilidade": piv.round(4).to_dict(), "mediana_abs_slogR_H": flat.round(4).to_dict(),
                    "tempo_s": round(t.dt, 1)}
        tab.to_csv(out_path(f"d7_confiabilidade_{how}.csv"), index=False)
    save_json("d7_confiabilidade.json", res)


if __name__ == "__main__":
    main()
