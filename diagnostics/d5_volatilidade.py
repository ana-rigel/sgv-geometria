"""D5 — A geometria é só volatilidade disfarçada?

Para cada grandeza geométrica exata (de D4), mede quanto dela é explicado por
volatilidade realizada passada (10/30/60 barras) e pelo tamanho do movimento da
própria barra (|v|, |a|). R² fora da amostra, em 5 blocos contíguos, com gradient
boosting (captura relações não lineares). Como teto de referência, o mesmo R²
usando as próprias coordenadas Z (E, jerk, memory_flux) da barra.

Nenhum retorno futuro é usado.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_predict

from common import coordinates, dataset, out_path, save_json, slog
from d4_geometria_exata import CONFIGS, config_name
from sgvgeo.features import realized_vol, scale_coordinates

N, WINDOW = 6000, 1500
TARGETS = {
    "phi (surpresa)": lambda f: f["phi"],
    "|∇φ|": lambda f: f["grad_phi_norm"],
    "H: nº autovalores negativos": lambda f: f["H_neg"],
    "H: slog det": lambda f: slog(f["H_det"]),
    "H: slog R": lambda f: slog(f["H_R"]),
    "H: log |G|": lambda f: np.log(f["H_G_norm"] + 1e-12),
    "F: slog R": lambda f: slog(f["F_R"]),
    "F: log det": lambda f: np.log(f["F_det"].clip(lower=1e-300)),
    "Fref: slog R (referência gaussiana)": lambda f: slog(f["Fref_R"]),
    "ΔF = slog R(F) − slog R(Fref)": lambda f: f["dF"],
}


def oof_r2(X: pd.DataFrame, y: pd.Series) -> float:
    ok = X.notna().all(axis=1) & y.notna() & np.isfinite(y)
    X, y = X[ok], y[ok]
    model = HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15)
    pred = cross_val_predict(model, X, y, cv=KFold(5, shuffle=False))
    return float(1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))


def main():
    raw, src = dataset(N)
    coords, cols, _ = coordinates(raw)
    vol = realized_vol(raw)
    vol["log_abs_v"] = np.log(coords["v"].abs() + 1e-12)
    vol["log_abs_a"] = np.log(coords["a"].abs() + 1e-12)
    out = {"fonte": src}
    for how, mult in CONFIGS:
        name = config_name(how, mult)
        f = pd.read_csv(out_path(f"d4_geometria_{name}.csv"), index_col=0)
        Z = scale_coordinates(coords, cols=cols, how=how, window=WINDOW, min_periods=300)
        Xv = vol.loc[f.index]
        Xz = Z.loc[f.index]
        rows = []
        for label, fn in TARGETS.items():
            try:
                y = pd.Series(np.asarray(fn(f), float), index=f.index)
            except KeyError:
                continue
            rows.append({"grandeza": label, "R2_volatilidade": oof_r2(Xv, y), "R2_coordenadas_Z": oof_r2(Xz, y)})
        tab = pd.DataFrame(rows)
        print(name); print(tab.round(3).to_string(index=False))
        out[name] = tab.round(4).to_dict("records")
    save_json("d5_volatilidade.json", out)


if __name__ == "__main__":
    main()
