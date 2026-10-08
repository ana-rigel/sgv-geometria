"""D6 — Física da informação: o campo obedece a uma equação de campo G = κT?

O legado calcula, sobre a mesma métrica, o tensor de Einstein G (geometria) e um
"tensor energia-momento" T montado com a surpresa φ e o campo λ
(T = ∇φ∇φᵀ + 0,75∇λ∇λᵀ + 0,25λg − ½(|∇φ|² + 0,75|∇λ|²)g), e depois os multiplica
num índice de "gravidade". Uma leitura física só se sustenta se G e T estiverem
ligados por uma constante: G = κT com κ estável.

Mede-se (i) o melhor κ barra a barra e o R² do ajuste com κ livre por barra
(teto otimista) e (ii) o R² com um κ único para a série inteira.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import out_path, save_json
from d4_geometria_exata import CONFIGS, config_name

COMP = ["00", "01", "02", "11", "12", "22"]


def main():
    out = {}
    for how, mult in CONFIGS:
        name = config_name(how, mult)
        f = pd.read_csv(out_path(f"d4_geometria_{name}.csv"), index_col=0)
        G = f[[f"H_G_{c}" for c in COMP]].to_numpy()
        T = f[[f"H_T_{c}" for c in COMP]].to_numpy()
        ok = np.all(np.isfinite(G), 1) & np.all(np.isfinite(T), 1)
        G, T, k = G[ok], T[ok], f.loc[ok, "H_field_eq_kappa"]
        kappa_global = float(np.sum(G * T) / np.sum(T * T))
        resid = G - kappa_global * T
        r2_global = float(1 - np.sum(resid ** 2) / np.sum(G ** 2))
        out[name] = {
            "barras": int(ok.sum()),
            "R2_kappa_livre_por_barra_mediana": float(f.loc[ok, "H_field_eq_r2"].median()),
            "kappa_por_barra": {"p05": float(k.quantile(.05)), "mediana": float(k.median()),
                                "p95": float(k.quantile(.95)),
                                "frac_sinal_positivo": float((k > 0).mean())},
            "kappa_global": kappa_global,
            "R2_kappa_global": r2_global,
            "parcela_do_termo_lambda_g_em_T_mediana": float(f.loc[ok, "H_T_lam_share"].median()),
            "lambda_mediano": float(f.loc[ok, "lam_field"].median()),
        }
        print(name, pd.Series(out[name]).to_string())
    save_json("d6_equacao_de_campo.json", out)


if __name__ == "__main__":
    main()
