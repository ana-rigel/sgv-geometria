"""D3 — Vazamento de futuro, camada por camada.

Teste do prefixo: calcula cada camada com as barras [0, N_PREF) e de novo com
[0, N_FULL). Numa camada causal, o valor de uma barra antiga não pode mudar quando
barras futuras são acrescentadas. Mede-se a fração de barras alteradas por coluna.

Teste de repintura ao vivo: run_sgv_runtime com a janela terminando na barra t e
na barra t+1; compara o valor da barra t nas duas execuções.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import Timer, dataset, out_path, save_json
from sgvgeo import legacy

N_PREF, N_FULL, SKIP = 2400, 3200, 400
LIVE_COLS = ["terrain_state", "terrain_transition_score", "force_alignment_cos", "expected_value_score",
             "edge_score", "sgv_edge_signal", "sgv_criticality_score", "field_stress_geodesic",
             "field_curvature_scalar", "field_gravity", "rupture_prob_geodesic"]


def changed_share(a: pd.Series, b: pd.Series) -> float:
    a, b = a.reset_index(drop=True), b.reset_index(drop=True)
    if a.dtype == object or b.dtype == object:
        return float((a.astype(str) != b.astype(str)).mean())
    a, b = pd.to_numeric(a, errors="coerce"), pd.to_numeric(b, errors="coerce")
    both = a.notna() & b.notna()
    diff = (a - b).abs() > 1e-9 * (1 + a.abs())
    return float((diff & both).mean() + (a.isna() ^ b.isna()).mean())


def main():
    raw, src = dataset(N_FULL)
    with Timer() as t:
        full = legacy.run_offline_chain(raw)
        pref = legacy.run_offline_chain(raw.iloc[:N_PREF].copy())
    rows = []
    for layer in full:
        if layer == "force_field":
            continue  # mapa de células, não série temporal
        F, P = full[layer], pref[layer]
        # alinhar pelo timestamp quando existe (algumas camadas descartam linhas)
        key = "timestamp" if "timestamp" in F and "timestamp" in P else None
        if key:
            F = F.set_index(key)
            P = P.set_index(key)
            common_idx = P.index[SKIP:]
            common_idx = common_idx[common_idx.isin(F.index)]
            F, P = F.loc[common_idx], P.loc[common_idx]
        else:
            F, P = F.iloc[SKIP:N_PREF], P.iloc[SKIP:N_PREF]
        for c in P.columns:
            if c in F.columns and not c.startswith("ret_fwd"):
                rows.append({"camada": layer, "coluna": c, "frac_barras_alteradas": changed_share(P[c], F[c])})
    tab = pd.DataFrame(rows)
    tab.to_csv(out_path("d3_vazamento_por_coluna.csv"), index=False)
    by_layer = tab.groupby("camada").agg(
        colunas=("coluna", "size"),
        colunas_afetadas=("frac_barras_alteradas", lambda s: int((s > 0.01).sum())),
        colunas_com_qualquer_alteracao=("frac_barras_alteradas", lambda s: int((s > 0).sum())),
        mediana_frac_alterada=("frac_barras_alteradas", "median"),
        max_frac_alterada=("frac_barras_alteradas", "max"),
    ).reset_index()
    print(by_layer.to_string(index=False))

    # repintura ao vivo
    live_rows = []
    ts = raw["timestamp"].to_numpy()
    for t_end in range(N_FULL - 40, N_FULL - 1, 3):
        a = legacy.run_live(raw.iloc[:t_end + 1].copy())
        b = legacy.run_live(raw.iloc[:t_end + 2].copy())
        tgt = ts[t_end]
        ra = a.loc[pd.to_numeric(a["timestamp"], errors="coerce") == tgt] if "timestamp" in a else a.iloc[[-1]]
        rb = b.loc[pd.to_numeric(b["timestamp"], errors="coerce") == tgt] if "timestamp" in b else b.iloc[[-2]]
        if ra.empty or rb.empty:
            ra, rb = a.iloc[[-1]], b.iloc[[-2]]
        for c in LIVE_COLS:
            if c in ra and c in rb:
                va, vb = ra[c].iloc[0], rb[c].iloc[0]
                if isinstance(va, str) or isinstance(vb, str):
                    ch = str(va) != str(vb)
                else:
                    ch = bool(abs(float(va) - float(vb)) > 1e-9 * (1 + abs(float(va))))
                live_rows.append({"barra": int(t_end), "coluna": c, "mudou": ch})
    live = pd.DataFrame(live_rows)
    rep = live.groupby("coluna")["mudou"].mean().round(3).to_dict()
    print("repintura ao vivo:", rep)
    save_json("d3_vazamento.json", {
        "fonte": src, "n_prefixo": N_PREF, "n_completo": N_FULL, "barras_ignoradas_aquecimento": SKIP,
        "tempo_s": round(t.dt, 1), "por_camada": by_layer.to_dict("records"),
        "repintura_ao_vivo_frac": rep, "n_pares_ao_vivo": int(live["barra"].nunique()),
        "piores_colunas": tab.sort_values("frac_barras_alteradas", ascending=False).head(25).to_dict("records"),
    })


if __name__ == "__main__":
    main()
