"""D2 — A curvatura do legado é sinal ou erro numérico?

Compara, nos MESMOS pontos e com o MESMO KDE:
  (a) a curvatura escalar R calculada pelas funções do legado (malha 3D + np.gradient),
      em quatro resoluções de malha;
  (b) a curvatura escalar exata (derivadas analíticas do KDE, sem malha).

Feito em duas escalas:
  - "legado": coordenadas brutas e largura de banda 0,45 (como no repositório);
  - "padronizada": coordenadas em z-score robusto e largura de Scott.
Um método numérico correto converge para o valor exato quando a malha refina;
erro de arredondamento amplificado faz o contrário.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import Timer, dataset, out_path, save_json
from sgvgeo import legacy
from sgvgeo.geometry import curvature, observed_information_metric
from sgvgeo.kde import GaussianKDE

geo = legacy.geodesic
GRIDS = [(16, 16, 12), (24, 24, 16), (32, 32, 24), (48, 48, 32)]
N_FIT, N_EVAL = 2000, 300


def legacy_grid_R(V: np.ndarray, h: float, shape) -> np.ndarray:
    """Reproduz as etapas 14 do legado (sem o campo λ, que não entra em R)."""
    e, j, m = V.T
    ge, gj, gm = (geo.make_axis_1d(e, shape[0]), geo.make_axis_1d(j, shape[1]),
                  geo.make_axis_1d(m, shape[2]))
    de, dj, dm = ge[1] - ge[0], gj[1] - gj[0], gm[1] - gm[0]
    rho = geo.fit_kde_density_3d(e, j, m, ge, gj, gm, bandwidth=h)
    phi = -np.log(rho + geo.EPS)
    g = geo.build_metric_3d(phi, de, dj, dm)
    gi, _ = geo.invert_metric_3x3_field(g)
    dg = geo.metric_derivatives_3d(g, de, dj, dm)
    gam = geo.christoffel_3d(gi, dg)
    dgam = geo.gamma_derivatives_3d(gam, de, dj, dm)
    R = np.clip(geo.scalar_curvature_3d(geo.ricci_tensor_3d(gam, dgam), gi),
                -geo.CLIP_CURV_3D, geo.CLIP_CURV_3D)
    return ge, gj, gm, R


def run(V: np.ndarray, h: float, label: str, rng) -> dict:
    idx = rng.choice(len(V), N_EVAL, replace=False)
    P = V[idx]
    # pontos dentro do miolo da malha (evita bordas, onde np.gradient é de 2ª ordem unilateral)
    kde = GaussianKDE(V, h)
    gH = observed_information_metric(kde)
    scale = V.std(0)
    with Timer() as t:
        exact = np.array([curvature(lambda y, s=scale: gH(y * s) * np.outer(s, s), p / scale).R
                          for p in P])
    res = {"escala": label, "largura_de_banda": h, "R_exato": {
        "mediana": float(np.median(exact)), "mediana_abs": float(np.median(np.abs(exact))), "p05": float(np.percentile(exact, 5)),
        "p95": float(np.percentile(exact, 95)), "max_abs": float(np.abs(exact).max())},
        "tempo_exato_s": round(t.dt, 1), "malhas": []}
    for shp in GRIDS:
        with Timer() as t:
            ge, gj, gm, Rg = legacy_grid_R(V, h, shp)
        Ri = geo.trilinear_interp(ge, gj, gm, Rg, P[:, 0], P[:, 1], P[:, 2])
        ok = np.isfinite(Ri) & np.isfinite(exact)
        corr = float(spearmanr(Ri[ok], exact[ok]).statistic) if np.std(Ri[ok]) > 0 and np.std(exact[ok]) > 0 else np.nan
        res["malhas"].append({
            "malha": "x".join(map(str, shp)), "tempo_s": round(t.dt, 1),
            "R_malha_mediana": float(np.median(Ri)), "R_malha_p95_abs": float(np.percentile(np.abs(Ri), 95)),
            "frac_saturada": float((np.abs(Ri) >= 0.999e6).mean()),
            "erro_mediano_abs": float(np.median(np.abs(Ri - exact))),
            "correlacao_postos_com_exato": corr,
        })
    return res


def main():
    rng = np.random.default_rng(0)
    raw, src = dataset(N_FIT + 300)
    inp = legacy.build_btc_90d_input_sgv(raw)
    info = legacy.build_information_field_geometry_90d(inp)
    E = info["E_norm"].to_numpy(float)
    J = info["jerk"].to_numpy(float)
    M = pd.Series(E).ewm(alpha=0.05, adjust=False).mean().diff().to_numpy()  # memory_flux da camada 3D
    V = np.column_stack([E, J, M])[-N_FIT:]
    V = V[np.all(np.isfinite(V), axis=1)]

    out = {"fonte": src, "n_ajuste": len(V), "n_avaliados": N_EVAL}
    out["legado"] = run(V, 0.45, "legado (bruta, h=0,45)", rng)
    med = np.median(V, 0)
    mad = 1.4826 * np.median(np.abs(V - med), 0)
    Vz = (V - med) / mad
    out["padronizada"] = run(Vz, len(Vz) ** (-1 / 7), "z-score robusto, h de Scott", rng)
    save_json("d2_numerica.json", out)
    for k in ("legado", "padronizada"):
        print(k, out[k]["R_exato"])
        print(pd.DataFrame(out[k]["malhas"]).to_string(index=False))


if __name__ == "__main__":
    main()
