"""Arquivo 5 — camada de terreno.

Reescrita de ``sgv_build_terrain_layer_90d_refactored.py``. Atrator local
ponderado, Mahalanobis, bacia, histerese, score
``z_disp + z_curv - z_basin + z_hyst`` e os quatro estados inalterados.
Itens 5.1–5.8.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.neighbors import KernelDensity

from .common.blocks import Block, causal_or_global_blocks, min_periods_for
from .common.kde import kde_eval
from .common.scaling import scaler_for
from .common.stats import quantile_threshold
from .common.validity import add_meta, assign_columns, legacy_fill_zero, validate_time_index
from .config import DEFAULT_CONFIG, SGVConfig

FILL_ZERO_COLS = [
    "terrain_cov_11", "terrain_cov_12", "terrain_cov_22",
    "terrain_fisher_proxy_11", "terrain_fisher_proxy_12", "terrain_fisher_proxy_22",
    "terrain_informational_displacement_raw", "terrain_informational_displacement",
    "terrain_log_density", "terrain_grad_logp_E", "terrain_grad_logp_jerk", "terrain_curvature",
    "terrain_hessian_trace", "terrain_hessian_maxeig_abs", "terrain_basin_depth",
    "terrain_regime_hysteresis", "terrain_informational_displacement_w", "terrain_curvature_w",
    "terrain_basin_depth_w", "terrain_regime_hysteresis_w", "terrain_z_disp", "terrain_z_curv",
    "terrain_z_basin", "terrain_z_hyst", "terrain_transition_score_raw", "terrain_transition_score",
]


def build_weights(window: int, alpha: float) -> np.ndarray:
    idx = np.arange(window)
    w = alpha ** (window - 1 - idx)
    return w / np.maximum(w.sum(), 1e-12)


def prepare_input_dataframe(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c = cfg.terrain
    out = df.copy()
    for col in ("timestamp", c.E_COL, c.J_COL):
        if col not in out.columns:
            raise ValueError(f"btc_90d_input_sgv.csv não possui coluna '{col}'.")
    src_cols = ["timestamp", c.E_COL, c.J_COL]
    for col in [c.LAMBDA_COL, c.R_COL, "close", "regime", "ret_fwd_1m", "ret_fwd_5m"]:
        if col in out.columns and col not in src_cols:
            src_cols.append(col)
    out = validate_time_index(out[src_cols].copy(), "timestamp", dedupe=False, sort=False)   # 5.8
    for col in [c.E_COL, c.J_COL, c.LAMBDA_COL, c.R_COL, "close", "ret_fwd_1m", "ret_fwd_5m"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=[c.E_COL, c.J_COL]).reset_index(drop=True)
    return out


# ------------------------------------------------------------- KDE local
def _legacy_numeric_derivs(kde: KernelDensity, x: np.ndarray, delta: float):
    """Gradiente e Hessiana numéricos do log da densidade (rota original)."""
    def lp(p):
        return float(kde.score_samples(p.reshape(1, -1))[0])

    d = len(x)
    grad = np.zeros(d)
    for k in range(d):
        xp, xm = x.copy(), x.copy()
        xp[k] += delta
        xm[k] -= delta
        grad[k] = (lp(xp) - lp(xm)) / (2.0 * delta)
    H = np.zeros((d, d))
    f0 = lp(x)
    for i in range(d):
        xp, xm = x.copy(), x.copy()
        xp[i] += delta
        xm[i] -= delta
        H[i, i] = (lp(xp) - 2.0 * f0 + lp(xm)) / (delta ** 2)
        for k in range(i + 1, d):
            xpp, xpm, xmp, xmm = x.copy(), x.copy(), x.copy(), x.copy()
            xpp[i] += delta; xpp[k] += delta     # noqa: E702
            xpm[i] += delta; xpm[k] -= delta     # noqa: E702
            xmp[i] -= delta; xmp[k] += delta     # noqa: E702
            xmm[i] -= delta; xmm[k] -= delta     # noqa: E702
            val = (lp(xpp) - lp(xpm) - lp(xmp) + lp(xmm)) / (4.0 * delta ** 2)
            H[i, k] = H[k, i] = val
    return f0, grad, H


def _kde_terrain(X: np.ndarray, disp_valid: np.ndarray, cfg: SGVConfig) -> dict[str, np.ndarray]:
    c, L = cfg.terrain, cfg.legacy
    n = len(X)
    blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_KDE, kind="fit")
    min_fit = min_periods_for(cfg, L.LEGACY_GLOBAL_KDE, kind="fit")
    out = {k: np.full(n, np.nan) for k in ("lp", "ge", "gj", "trace", "maxeig")}
    out["fit_valid"] = np.zeros(n)
    for b in blocks:
        rows = np.arange(b.fit_start, b.fit_stop)
        rows = rows[disp_valid[rows]]
        fit = X[rows]
        fit = fit[np.isfinite(fit).all(axis=1)]
        if L.LEGACY_GLOBAL_KDE and len(fit) == 0:
            raise ValueError("Não há dados válidos para ajuste do KDE do terrain layer.")
        if len(fit) < max(min_fit, 1):
            continue
        sc = scaler_for(fit, L.LEGACY_UNSCALED_KDE)
        fit_s = sc.transform(fit)
        ev = np.arange(b.start, b.stop)
        pts = sc.transform(X[ev])
        if L.LEGACY_GRID_DERIVATIVES:
            kde = KernelDensity(kernel="gaussian", bandwidth=c.BANDWIDTH).fit(fit_s)
            for r_i, x in zip(ev, pts):
                lp, g, H = _legacy_numeric_derivs(kde, x, c.DELTA)
                eig = np.linalg.eigvalsh(H)
                out["lp"][r_i], out["ge"][r_i], out["gj"][r_i] = lp, g[0], g[1]
                out["trace"][r_i] = float(np.trace(H))
                out["maxeig"][r_i] = float(np.max(np.abs(eig)))
        else:
            r = kde_eval(pts, fit_s, c.BANDWIDTH, order=2)
            grad_lp = -r.grad_phi                      # ∇ log ρ
            H_lp = -r.hess_phi                         # ∇² log ρ
            ok = np.isfinite(H_lp).all(axis=(1, 2))
            eig = np.full((len(ev), 2), np.nan)
            if ok.any():
                eig[ok] = np.linalg.eigvalsh(H_lp[ok])
            out["lp"][ev] = r.log_rho
            out["ge"][ev], out["gj"][ev] = grad_lp[:, 0], grad_lp[:, 1]
            out["trace"][ev] = H_lp[:, 0, 0] + H_lp[:, 1, 1]
            out["maxeig"][ev] = np.max(np.abs(eig), axis=1)
        out["fit_valid"][ev] = 1.0
    return out


# ------------------------------------------------------------- estabilização
def _winsor_z(values: np.ndarray, blocks: Sequence[Block], q_lo: float, q_hi: float,
              min_periods: int) -> tuple[np.ndarray, np.ndarray]:
    """Winsorização e z robusto (0,6745 · (x - med)/MAD) com parâmetros por bloco.

    Os parâmetros de cada bloco vêm só da janela de ajuste: quantis da janela,
    janela winsorizada, mediana e MAD da janela winsorizada. Com o bloco global
    o resultado é idêntico ao do script original.
    """
    v = np.asarray(values, dtype=float)
    n = len(v)
    w_out = np.full(n, np.nan)
    z_out = np.full(n, np.nan)
    for b in blocks:
        w = v[b.fit_start:b.fit_stop]
        w = w[np.isfinite(w)]
        if len(w) < max(1, min_periods):
            continue
        lo, hi = np.quantile(w, [q_lo, q_hi])
        wc = np.clip(w, lo, hi)
        med = float(np.median(wc))
        mad = float(np.median(np.abs(wc - med)))
        cur = np.clip(v[b.start:b.stop], lo, hi)
        w_out[b.start:b.stop] = cur
        if mad < 1e-12:
            z_out[b.start:b.stop] = np.where(np.isfinite(cur), 0.0, np.nan)
        else:
            z_out[b.start:b.stop] = 0.6745 * (cur - med) / mad
    return w_out, z_out


def build_terrain_layer_90d(df: pd.DataFrame, cfg: SGVConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    c, L = cfg.terrain, cfg.legacy
    work = prepare_input_dataframe(df, cfg)
    X = work[[c.E_COL, c.J_COL]].to_numpy(dtype=float)
    n = len(X)
    W = c.WINDOW
    if n < W:
        raise ValueError(f"Dados insuficientes: n={n}, WINDOW={W}")

    # ---------------- atrator local + covariância + Mahalanobis (vetorizado, 5.5)
    weights = build_weights(W, c.ALPHA)
    win = sliding_window_view(X, (W, 2))[:, 0]                 # (n-W+1, W, 2)
    mu_v = np.einsum("w,nwd->nd", weights, win)
    XC = win - mu_v[:, None, :]
    cov_v = np.einsum("w,nwi,nwj->nij", weights, XC, XC)
    if L.LEGACY_ABS_EPS:
        cov_v = cov_v + c.EPS * np.eye(2)[None]
        fisher_v = np.linalg.pinv(cov_v)
    else:
        # 5.2: regularização relativa por eixo, Σ + eps·diag(Σ). A forma
        # eps·traço(Σ)/d da especificação mistura as unidades de E e jerk e
        # quebra a invariância de escala do Mahalanobis; esta não.
        var = np.stack([cov_v[:, 0, 0], cov_v[:, 1, 1]], axis=1)
        reg = np.where(var > 0, c.EPS * var, c.EPS)
        cov_v = cov_v.copy()
        cov_v[:, 0, 0] += reg[:, 0]
        cov_v[:, 1, 1] += reg[:, 1]
        fisher_v = np.linalg.inv(cov_v)                              # 5.6
    diff = X[W - 1:] - mu_v
    disp_raw_v = np.maximum(np.einsum("ni,nij,nj->n", diff, fisher_v, diff), 0.0)

    def pad(a):
        p = np.full((W - 1,) + a.shape[1:], np.nan)
        return np.concatenate([p, a], axis=0)

    mu, cov, fisher = pad(mu_v), pad(cov_v), pad(fisher_v)
    disp_raw = pad(disp_raw_v)
    disp_log = np.log1p(disp_raw)
    disp_valid = np.isfinite(disp_log)

    # ---------------- KDE local (causal, padronizada, analítica)
    kd = _kde_terrain(X, disp_valid, cfg)
    grad_norm = np.sqrt(kd["ge"] ** 2 + kd["gj"] ** 2)
    basin = kd["lp"] - c.BETA * grad_norm

    # ---------------- histerese
    mu_df = pd.DataFrame(mu)
    hyst = np.linalg.norm((mu_df - mu_df.shift(c.HYST_K)).to_numpy(), axis=1)
    hyst[: min(n, W - 1 + c.HYST_K)] = np.nan

    # ---------------- estabilização (5.1, 5.4)
    def fill(a):
        s = pd.Series(a)
        return (s.bfill().ffill() if L.LEGACY_BFILL else s.ffill()).to_numpy()

    disp_s, curv_s, basin_s, hyst_s = fill(disp_log), fill(grad_norm), fill(basin), fill(hyst)
    q_blocks = causal_or_global_blocks(n, cfg, L.LEGACY_GLOBAL_QUANTILES)
    q_min = min_periods_for(cfg, L.LEGACY_GLOBAL_QUANTILES)
    disp_w, z_disp = _winsor_z(disp_s, q_blocks, c.WINSOR_LO, c.WINSOR_HI, q_min)
    curv_w, z_curv = _winsor_z(curv_s, q_blocks, c.WINSOR_LO, c.WINSOR_HI, q_min)
    basin_w, z_basin = _winsor_z(basin_s, q_blocks, c.WINSOR_LO, c.WINSOR_HI, q_min)
    hyst_w, z_hyst = _winsor_z(hyst_s, q_blocks, c.WINSOR_LO, c.WINSOR_HI, q_min)

    raw_score = z_disp + z_curv - z_basin + z_hyst
    lo = quantile_threshold(raw_score, q_blocks, c.FINAL_SCORE_LO, q_min)
    hi = quantile_threshold(raw_score, q_blocks, c.FINAL_SCORE_HI, q_min)
    final = np.clip(raw_score, lo, hi)

    q1 = quantile_threshold(final, q_blocks, c.STATE_Q1, q_min)
    q2 = quantile_threshold(final, q_blocks, c.STATE_Q2, q_min)
    q3 = quantile_threshold(final, q_blocks, c.STATE_Q3, q_min)
    with np.errstate(invalid="ignore"):
        state = np.select(
            [~np.isfinite(final) | ~np.isfinite(q1), final < q1, final < q2, final < q3],
            ["UNDEFINED", "COHERENT", "TENSIONED", "TRANSITION_EDGE"],
            default="RUPTURE_CORRIDOR",
        )

    cols: dict[str, Any] = {
        "terrain_attractor_E": mu[:, 0], "terrain_attractor_jerk": mu[:, 1],
        "terrain_cov_11": cov[:, 0, 0], "terrain_cov_12": cov[:, 0, 1], "terrain_cov_22": cov[:, 1, 1],
        "terrain_fisher_proxy_11": fisher[:, 0, 0], "terrain_fisher_proxy_12": fisher[:, 0, 1],
        "terrain_fisher_proxy_22": fisher[:, 1, 1],
        "terrain_informational_displacement_raw": disp_raw,
        "terrain_informational_displacement": disp_log,
        "terrain_log_density": kd["lp"],
        "terrain_grad_logp_E": kd["ge"], "terrain_grad_logp_jerk": kd["gj"],
        "terrain_curvature": grad_norm,
        "terrain_hessian_trace": kd["trace"], "terrain_hessian_maxeig_abs": kd["maxeig"],
        "terrain_basin_depth": basin,
        "terrain_regime_hysteresis": hyst,
        "terrain_informational_displacement_w": disp_w, "terrain_curvature_w": curv_w,
        "terrain_basin_depth_w": basin_w, "terrain_regime_hysteresis_w": hyst_w,
        "terrain_z_disp": z_disp, "terrain_z_curv": z_curv, "terrain_z_basin": z_basin, "terrain_z_hyst": z_hyst,
        "terrain_transition_score_raw": raw_score, "terrain_transition_score": final,
        "terrain_state": state,
        # novos
        "terrain_grad_norm": grad_norm,
        "terrain_valid": (np.isfinite(final) & disp_valid & (kd["fit_valid"] > 0)).astype(int),
    }
    out = assign_columns(work, cols)
    vc = pd.Series(state).value_counts(normalize=True).round(4).to_dict()
    add_meta(out, "terrain_state_shares", vc)
    if L.LEGACY_ZERO_FILL:
        out = legacy_fill_zero(out, FILL_ZERO_COLS)
    return out
