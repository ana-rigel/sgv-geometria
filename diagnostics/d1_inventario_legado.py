"""D1 — Inventário do legado: o que cada coluna das 10 camadas realmente carrega.

Roda a cadeia offline (9 camadas) e o run_sgv_runtime sem modificar o código e mede,
coluna a coluna: variação (CV, fração de valores distintos), saturação nos cortes
artificiais (±1e6), duplicatas exatas e colunas quase constantes. Também resume o
único dado real do legado (132 barras ao vivo de 31/03/2026).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import ROOT, Timer, dataset, out_path, save_json
from sgvgeo import legacy

N = 4000


def profile(df: pd.DataFrame, layer: str) -> pd.DataFrame:
    rows = []
    for c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().mean() < 0.5:
            continue
        s = s.dropna()
        sd, mu = s.std(), s.abs().mean()
        rows.append({
            "camada": layer, "coluna": c, "n": len(s),
            "media": s.mean(), "dp": sd, "cv": sd / (mu + 1e-300),
            "frac_distintos": s.nunique() / len(s),
            "frac_saturado_1e6": float((s.abs() >= 0.999e6).mean()),
            "frac_moda": float((s == s.mode().iloc[0]).mean()) if len(s) else np.nan,
        })
    return pd.DataFrame(rows)


def duplicates(df: pd.DataFrame) -> list[tuple[str, str]]:
    num = df.select_dtypes("number").dropna(axis=1, how="any")
    num = num.loc[:, num.std() > 0]
    seen, dup = {}, []
    for c in num.columns:
        key = tuple(np.round(num[c].to_numpy()[:200], 12))
        if key in seen and np.allclose(num[c], num[seen[key]], rtol=0, atol=0):
            dup.append((seen[key], c))
        else:
            seen.setdefault(key, c)
    return dup


def main():
    raw, src = dataset(N)
    with Timer() as t:
        layers = legacy.run_offline_chain(raw)
    with Timer() as t2:
        live = legacy.run_live(raw)
    layers["runtime_live"] = live

    prof = pd.concat([profile(df, k) for k, df in layers.items()], ignore_index=True)
    prof.to_csv(out_path("d1_perfil_colunas.csv"), index=False)

    geo = layers["geodesic"]
    key_cols = ["field_curvature", "field_curvature_scalar", "field_einstein_norm",
                "field_stress_tensor_norm", "field_gravity", "field_stress_geodesic",
                "rupture_prob_geodesic", "g_det", "geom_incoherence", "jerk_over_lambda"]
    key = prof[(prof.camada == "geodesic") & prof.coluna.isin(key_cols)].set_index("coluna")

    sing = layers["singularity"]
    summary = {
        "fonte": src,
        "tempo_cadeia_offline_s": round(t.dt, 1),
        "tempo_run_sgv_runtime_s": round(t2.dt, 1),
        "colunas_por_camada": {k: int(v.shape[1]) for k, v in layers.items()},
        "escala_coordenadas_geodesic": {
            "E_norm(v2+a2)_dp": float(layers["info"]["E_norm"].std()),
            "jerk_dp": float(layers["info"]["jerk"].std()),
            "memory_flux_3d_dp": float(geo["memory_flux"].std()),
            "largura_de_banda_2d": 0.35, "largura_de_banda_3d": 0.45,
        },
        "curvatura_escalar_3d": {
            "frac_saturada_1e6": float((geo["field_curvature_scalar"].abs() >= 0.999e6).mean()),
            "mediana": float(geo["field_curvature_scalar"].median()),
            "p05": float(geo["field_curvature_scalar"].quantile(0.05)),
            "p95": float(geo["field_curvature_scalar"].quantile(0.95)),
        },
        "rupture_prob_geodesic": {"mediana": float(geo["rupture_prob_geodesic"].median()),
                                  "dp": float(geo["rupture_prob_geodesic"].std())},
        "g_det_2d": {"min": float(geo["g_det"].min()), "frac_negativo": float((geo["g_det"] < 0).mean())},
        "information_density_dp": float(layers["info"]["information_density"].std()),
        "information_density_valor": float(layers["info"]["information_density"].median()),
        "tipo_singularidade": sing["sgv_singularity_type"].value_counts(normalize=True).round(3).to_dict(),
        "is_high_critical_frac_live": float(pd.to_numeric(live["is_high_critical"]).mean()),
        "sgv_criticality_score_faixa_live": [float(live["sgv_criticality_score"].min()),
                                             float(live["sgv_criticality_score"].max())],
        "sgv_criticality_score_faixa_offline": [float(sing["sgv_criticality_score"].min()),
                                                float(sing["sgv_criticality_score"].max())],
        "information_density_dp_apos_aquecimento": float(layers["info"]["information_density"].iloc[300:].std()),
        "duplicatas_exatas_geodesic": duplicates(geo),
        "chaves_geodesic": key[["dp", "cv", "frac_distintos", "frac_saturado_1e6"]].round(6).to_dict("index"),
    }

    real = ROOT / "legacy" / "dados_reais_31mar2026" / "sgv_tori_metrics.csv"
    if real.exists():
        r = pd.read_csv(real)
        cols = [c for c in ["field_curvature_scalar", "field_stress_geodesic", "rupture_prob_geodesic",
                            "field_curvature", "field_gravity", "force_alignment_cos"] if c in r]
        summary["dados_reais_31mar2026"] = r[cols].describe().T[["min", "50%", "max", "std"]].round(4).to_dict("index")
    save_json("d1_resumo.json", summary)
    print(pd.Series(summary).to_string()[:4000])


if __name__ == "__main__":
    main()
