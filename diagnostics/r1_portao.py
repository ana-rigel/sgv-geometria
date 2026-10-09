"""R1 — portão G1' para as coordenadas de fluxo (z, ι, ν). Pré-registro: PREREGISTRO_R1.md.

Fonte de dados (uma das duas):
  SGV_DATA=caminhos.zip:...   klines reais da Binance (com colunas de fluxo)
  SGV_SYNTH=null|alt          calibração: série gerada pelo nulo SF1 (null) ou com
                              interação impacto×atividade fora do nulo (alt)
Outras variáveis: SGV_TAG (pasta de saída), SGV_K (réplicas SF1, padrão 39),
SGV_INTERACTION (força da alternativa, padrão 0,8), SGV_N_SYNTH (barras, padrão 20000).

Passos (argumentos): d7 d4 d5 d8 — sem argumentos, roda todos e julga o portão.

Critério 2 revisado na calibração (antes de qualquer dado real): o original,
|ρ(ΔF, raio)| < 0,5, reprovou também a série ALTERNATIVA, que tem estrutura real —
com estas coordenadas ele não tem poder. Passa a ser: a diferença do critério 3
sobrevive ao pareamento por posição (ΔF menos o ΔF que o nulo tem no mesmo raio),
com p ≤ 0,05. O ρ original continua reportado.
Nenhum passo olha retorno futuro.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_predict

from common import Timer, out_path, save_json, slog
from sgvgeo.data import load_binance_klines
from sgvgeo.features import causal_rank_gauss, realized_vol
from sgvgeo.field import causal_geometry
from sgvgeo.flow import default_sf1, fit_sf1, flow_coordinates, simulate_sf1
from sgvgeo.geometry import curvature, gaussian_reference_fisher_metric, local_fisher_metric
from sgvgeo.kde import GaussianKDE

WINDOW, REFIT = 1500, 60
SCOTT = WINDOW ** (-1 / 7)
N_D4, N_D8, EVERY_D8 = 6000, 4500, 2
D7_EVAL, D7_MULTS, H_CHOICES = 240, (1.0, 2.0, 3.0, 4.0), (2.0, 3.0, 4.0)
K = int(os.environ.get("SGV_K", 39))
COORDS = ["z", "iota", "nu"]


# ---------------------------------------------------------------------------
def load() -> tuple[pd.DataFrame, str]:
    if os.environ.get("SGV_DATA"):
        src = os.environ["SGV_DATA"]
        return load_binance_klines(src.split(":"), with_flow=True), f"real:{src}"
    kind = os.environ.get("SGV_SYNTH", "null")
    n = int(os.environ.get("SGV_N_SYNTH", 20000))
    inter = float(os.environ.get("SGV_INTERACTION", 0.8)) if kind == "alt" else 0.0
    return simulate_sf1(default_sf1(), n, seed=11, interaction=inter), f"sintético SF1 ({kind}, interação={inter}), n={n}"


def scaled(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    c = flow_coordinates(df)
    Z = np.column_stack([causal_rank_gauss(c[k], WINDOW, 300).to_numpy() for k in COORDS])
    return c, Z


def geometry(Z: np.ndarray, h: float, start: int, every: int = 1) -> pd.DataFrame:
    f = causal_geometry(Z, lam=None, window=WINDOW, refit=REFIT, h=h, start=start, every=every)
    f["dF"] = slog(f["F_R"]) - slog(f["Fref_R"])
    return f


# ---------------------------------------------------------------------------
def d7(df) -> dict:
    """Confiabilidade de ΔF entre metades da janela, em barras sorteadas no período todo."""
    _, Z = scaled(df)
    rng = np.random.default_rng(0)
    ok_t = [t for t in range(WINDOW + 300, len(Z)) if np.all(np.isfinite(Z[t]))]
    ts = np.sort(rng.choice(ok_t, min(D7_EVAL, len(ok_t)), replace=False))
    rel = {}
    for c in D7_MULTS:
        A, B = [], []
        for t in ts:
            past = Z[t - WINDOW:t]
            past = past[np.all(np.isfinite(past), axis=1)]
            vals = []
            for half in (past[0::2], past[1::2]):
                kde = GaussianKDE(half, c * SCOTT)
                try:
                    vals.append(slog(curvature(local_fisher_metric(kde), Z[t]).R)
                                - slog(curvature(gaussian_reference_fisher_metric(kde), Z[t]).R))
                except np.linalg.LinAlgError:
                    vals.append(np.nan)
            A.append(vals[0]); B.append(vals[1])
        a, b = pd.Series(A), pd.Series(B)
        m = a.notna() & b.notna()
        rel[c] = float(a[m].corr(b[m], method="spearman"))
    chosen = next((c for c in H_CHOICES if rel[c] >= 0.8), None)
    return {"confiabilidade_dF": rel, "h_escolhido": chosen,
            "criterio1_aprovado": chosen is not None}


def d4_d5(df, hmult: float) -> dict:
    seg = df.tail(N_D4).reset_index(drop=True)
    coords, Z = scaled(seg)
    f = geometry(Z, hmult * SCOTT, start=WINDOW + 300)
    rho = float(f["dF"].corr(f["mahalanobis"], method="spearman"))
    vol = realized_vol(seg)
    r = coords["r"]
    vol["log_abs_v"] = np.log(r.abs() + 1e-12)
    vol["log_abs_a"] = np.log(r.diff().abs() + 1e-12)
    X, y = vol.loc[f.index], f["dF"]
    ok = X.notna().all(axis=1) & y.notna() & np.isfinite(y)
    X, y = X[ok], y[ok]
    pred = cross_val_predict(HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05,
                                                           max_leaf_nodes=15), X, y, cv=KFold(5))
    r2 = float(1 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))
    f.to_csv(out_path(f"r1_d4_geometria_h{hmult:g}x.csv"))
    return {"spearman_dF_mahalanobis": rho, "criterio2_original_aprovado": abs(rho) < 0.5,
            "R2_dF_volatilidade": r2, "criterio4_aprovado": r2 <= 0.5,
            "dF": {"mediana": float(f["dF"].median()), "media": float(f["dF"].mean())},
            "autocorr_dF": float(f["dF"].autocorr(1)), "barras": int(len(f))}


def _stats(seg: pd.DataFrame, hmult: float) -> tuple[dict, np.ndarray]:
    _, Z = scaled(seg)
    f = geometry(Z, hmult * SCOTT, start=WINDOW + 300, every=EVERY_D8)
    neg = f["H_neg"]
    pairs = f[["mahalanobis", "dF"]].dropna().to_numpy()
    return {"dF_media": float(np.nanmean(f["dF"])), "dF_mediana": float(np.nanmedian(f["dF"])),
            "F_mediana_log_det": float(np.nanmedian(np.log(f["F_det"].clip(lower=1e-300)))),
            "H_troca_assinatura": float((neg.diff().fillna(0) != 0).mean()),
            "autocorr_phi": float(f["phi"].autocorr(1))}, pairs


def _position_curve(pairs_list: list[np.ndarray], n_bins: int = 10):
    """Curva ΔF esperado por faixa de distância ao centro (raio de Mahalanobis), sob o nulo."""
    P = np.vstack(pairs_list)
    edges = np.quantile(P[:, 0], np.linspace(0, 1, n_bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    idx = np.clip(np.searchsorted(edges, P[:, 0], side="right") - 1, 0, n_bins - 1)
    med = np.array([np.median(P[idx == b, 1]) for b in range(n_bins)])
    return edges, med


def _matched_mean(pairs: np.ndarray, curve) -> float:
    edges, med = curve
    idx = np.clip(np.searchsorted(edges, pairs[:, 0], side="right") - 1, 0, len(med) - 1)
    return float(np.mean(pairs[:, 1] - med[idx]))


def d8(df, hmult: float) -> dict:
    seg = df.tail(N_D8).reset_index(drop=True)
    model = fit_sf1(seg)
    real, real_pairs = _stats(seg, hmult)
    p0 = float(seg["close"].iloc[0])
    out = [_stats(simulate_sf1(model, N_D8, seed=1000 + k, p0=p0), hmult) for k in range(K)]
    sims = [o[0] for o in out]
    sim_pairs = [o[1] for o in out]
    # Critério 2': ΔF pareado por posição — subtrai o ΔF que o nulo SF1 tem na mesma
    # distância ao centro (curva ajustada nas réplicas; deixe-uma-fora para cada réplica).
    real["dF_pareado_posicao"] = _matched_mean(real_pairs, _position_curve(sim_pairs))
    for k in range(K):
        sims[k]["dF_pareado_posicao"] = _matched_mean(
            sim_pairs[k], _position_curve(sim_pairs[:k] + sim_pairs[k + 1:]))
    rows = {}
    for s, v in real.items():
        vals = np.array([d[s] for d in sims])
        med = np.median(vals)
        p = (1 + np.sum(np.abs(vals - med) >= abs(v - med))) / (K + 1)
        rows[s] = {"serie": v, "sf1_media": float(vals.mean()),
                   "z": float((v - vals.mean()) / (vals.std(ddof=1) + 1e-12)), "p": float(p)}
    return {"sf1_ajustado": {"garch": model.garch, "a": model.a.tolist(), "b": model.b.tolist()},
            "replicas": K, "estatisticas": rows, "p_primario": rows["dF_media"]["p"],
            "criterio3_aprovado": rows["dF_media"]["p"] <= 0.05,
            "p_pareado_posicao": rows["dF_pareado_posicao"]["p"],
            "criterio2_aprovado": rows["dF_pareado_posicao"]["p"] <= 0.05}


# ---------------------------------------------------------------------------
def main():
    steps = sys.argv[1:] or ["d7", "d4", "d5", "d8"]
    df, src = load()
    res_path = out_path("r1_portao.json")
    res = {}
    if res_path.exists():
        import json
        res = json.loads(res_path.read_text())
    res["fonte"] = src
    with Timer() as t:
        if "d7" in steps:
            res["d7"] = d7(df)
            print("D7", res["d7"], flush=True)
        hm = (res.get("d7") or {}).get("h_escolhido") or 4.0
        if "d4" in steps or "d5" in steps:
            res["d4_d5"] = d4_d5(df, hm) | {"h": hm}
            print("D4/D5", res["d4_d5"], flush=True)
        if "d8" in steps:
            res["d8"] = d8(df, hm) | {"h": hm}
            print("D8", {k: v for k, v in res["d8"].items() if k != "estatisticas"}, flush=True)
            print(pd.DataFrame(res["d8"]["estatisticas"]).T.round(4).to_string(), flush=True)
    crit = [res.get("d7", {}).get("criterio1_aprovado"), res.get("d8", {}).get("criterio2_aprovado"),
            res.get("d8", {}).get("criterio3_aprovado"), res.get("d4_d5", {}).get("criterio4_aprovado")]
    res["criterios"] = dict(zip(["1_mensuravel", "2_alem_da_posicao", "3_existe", "4_alem_da_volatilidade"], crit))
    res["G1_aprovado"] = all(c is True for c in crit)
    res["tempo_s"] = round(t.dt, 1)
    save_json("r1_portao.json", res)
    print("CRITÉRIOS", res["criterios"], "→ G1' aprovado:", res["G1_aprovado"])


if __name__ == "__main__":
    main()
