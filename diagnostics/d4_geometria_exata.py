"""D4 — A geometria exata e causal: assinatura da métrica e curvatura.

Coordenadas do legado (E = v²+a², jerk, memory_flux), escaladas de forma causal,
KDE ajustado só no passado (janela 1500, reajuste a cada 60 barras). Métricas:
  H    = ∇²(−log ρ)  informação observada (a escolha do legado)
  F    = média local de ∇φ∇φᵀ  Fisher local (positiva semidefinida por construção)
  Fref = a mesma construção com o escore de uma gaussiana ajustada à janela
  ΔF   = slog R(F) − slog R(Fref): o que a forma da distribuição acrescenta à curvatura

Configurações (largura de banda em múltiplos de Scott(1500) ≈ 0,351):
  robust_z  × 1  — escala do legado corrigida, largura "natural"
  rank_gauss × 1
  rank_gauss × 2
  rank_gauss × SGV_HMULT — a largura escolhida por D7 (regra do G1), se diferente

Salva a série barra a barra (reusada por D5 e D6).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from common import Timer, dataset, out_path, save_json, slog
from sgvgeo.features import legacy_coordinates, scale_coordinates
from sgvgeo.field import causal_geometry

N, WINDOW, REFIT = 6000, 1500, 60
SCOTT = WINDOW ** (-1 / 7)
H_CHOSEN = float(os.environ.get("SGV_HMULT", 2.0))  # múltiplo de Scott a fixar na Fase 1 via D7
CHOSEN = ("rank_gauss", H_CHOSEN)
CONFIGS = [("robust_z", 1.0), ("rank_gauss", 1.0), ("rank_gauss", 2.0)]
if CHOSEN not in CONFIGS:
    CONFIGS.append(CHOSEN)


def config_name(how: str, mult: float) -> str:
    return f"{how}_h{mult:g}x"


def add_derived(f: pd.DataFrame) -> pd.DataFrame:
    f = f.copy()
    if "F_R" in f and "Fref_R" in f:
        f["dF"] = slog(f["F_R"]) - slog(f["Fref_R"])
    return f


def summarize(f: pd.DataFrame) -> dict:
    sp = lambda a, b: float(pd.Series(np.asarray(a)).corr(pd.Series(np.asarray(b)), method="spearman"))  # noqa: E731
    neg = f["H_neg"]
    change = (neg.diff().fillna(0) != 0)
    runs = (change.cumsum()).value_counts()
    absR = f["H_R"].abs()
    small_det = f["H_det"].abs() <= f["H_det"].abs().quantile(0.10)
    blow = absR > 100
    q = lambda s: {"p05": float(s.quantile(.05)), "mediana": float(s.median()),  # noqa: E731
                   "p95": float(s.quantile(.95))}
    return {
        "barras_avaliadas": int(len(f)),
        "max_abs_z": {"p99": float(f["max_abs_z"].quantile(.99)), "max": float(f["max_abs_z"].max())},
        "H_frac_positiva_definida": float((neg == 0).mean()),
        "H_distribuicao_autovalores_negativos": neg.value_counts(normalize=True).sort_index().round(4).to_dict(),
        "H_taxa_troca_assinatura_por_barra": float(change.mean()),
        "H_duracao_media_regime_barras": float(runs.mean()),
        "H_R": q(f["H_R"]),
        "H_frac_R_exatamente_zero": float((f["H_R"] == 0).mean()),
        "H_frac_absR_maior_100": float(blow.mean()),
        "H_frac_explosoes_entre_10pct_menor_det": float((blow & small_det).sum() / max(1, blow.sum())),
        "F_R": q(f["F_R"]),
        "F_frac_singular": float(f.get("F_singular", pd.Series(0, index=f.index)).fillna(0).mean()),
        "F_frac_absR_maior_100": float((f.F_R.abs() > 100).mean()),
        "F_condicionamento_mediano": float((f.F_maxeig / f.F_mineig).median()),
        "spearman_F_vs_Fref": sp(slog(f.F_R), slog(f.Fref_R)),
        "spearman_F_vs_mahalanobis": sp(slog(f.F_R), f.mahalanobis),
        "spearman_dF_vs_mahalanobis": sp(f.dF, f.mahalanobis),
        "dF": q(f["dF"]),
        "autocorr_lag1": {
            "indicador_H_indefinida": float((neg > 0).astype(float).autocorr(1)),
            "slog_HR": float(pd.Series(slog(f.H_R), index=f.index).autocorr(1)),
            "slog_FR": float(pd.Series(slog(f.F_R), index=f.index).autocorr(1)),
            "dF": float(f["dF"].autocorr(1)),
            "phi": float(f.phi.autocorr(1)),
        },
        "spearman_HR_FR": sp(slog(f.H_R), slog(f.F_R)),
        "parcela_lambda_em_T_mediana": float(f["H_T_lam_share"].median()) if "H_T_lam_share" in f else None,
        "lambda_mediano": float(f["lam_field"].median()) if "lam_field" in f else None,
    }


def main():
    raw, src = dataset(N)
    coords = legacy_coordinates(raw)
    res = {"fonte": src, "janela": WINDOW, "reajuste": REFIT, "scott_1500": SCOTT,
           "configuracao_escolhida": config_name(*CHOSEN)}
    for how, mult in CONFIGS:
        name = config_name(how, mult)
        Z = scale_coordinates(coords, how=how, window=WINDOW, min_periods=300).to_numpy()
        csv = out_path(f"d4_geometria_{name}.csv")
        with Timer() as t:
            if os.environ.get("REUSE") and csv.exists():
                f = pd.read_csv(csv, index_col=0)
            else:
                f = add_derived(causal_geometry(Z, lam=coords["lam"].to_numpy(), window=WINDOW,
                                                refit=REFIT, h=mult * SCOTT, start=WINDOW + 300))
                f.to_csv(csv)
        res[name] = summarize(f) | {"largura_de_banda": mult * SCOTT, "tempo_s": round(t.dt, 1)}
        print(name, pd.Series(res[name]).to_string())
    save_json("d4_geometria_exata.json", res)


if __name__ == "__main__":
    main()
