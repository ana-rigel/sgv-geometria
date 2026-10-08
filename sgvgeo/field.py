"""Campo geométrico causal ao longo do tempo.

Para cada bloco de `refit` barras começando em t0, o KDE é ajustado SÓ nas
`window` barras anteriores a t0 e avaliado em cada barra t ∈ [t0, t0+refit).
Nenhuma barra entra no ajuste que a avalia; nada do futuro entra em nada.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .geometry import (W_LAM, LambdaField, curvature, gaussian_reference_fisher_metric,
                       info_stress_tensor, local_fisher_metric, observed_information_metric,
                       tensor_norm)
from .kde import GaussianKDE


def causal_geometry(Z: np.ndarray, lam: np.ndarray | None = None, window: int = 1500,
                    refit: int = 60, h: float | None = None, metrics=("H", "F"),
                    start: int | None = None, stop: int | None = None, every: int = 1,
                    delta: float = 1e-3) -> pd.DataFrame:
    Z = np.asarray(Z, float)
    T, d = Z.shape
    h = h if h is not None else window ** (-1.0 / (d + 4))
    start = max(window, start or 0)
    stop = T if stop is None else min(T, stop)
    rows = []
    for t0 in range(start, stop, refit):
        past = Z[t0 - window:t0]
        ok = np.all(np.isfinite(past), axis=1)
        if ok.sum() < window // 2:
            continue
        kde = GaussianKDE(past[ok], h)
        gH = observed_information_metric(kde)
        gF = local_fisher_metric(kde) if "F" in metrics else None
        gR = gaussian_reference_fisher_metric(kde) if "F" in metrics else None
        mu, Si = kde.X.mean(0), np.linalg.inv(np.cov(kde.X, rowvar=False))
        lamf = LambdaField(kde, lam[t0 - window:t0][ok]) if lam is not None else None
        for t in range(t0, min(t0 + refit, stop), every):
            x = Z[t]
            if not np.all(np.isfinite(x)):
                continue
            row = {"t": t, "phi": kde.phi(x), "grad_phi_norm": float(np.linalg.norm(kde.grad_phi(x))),
                   "mahalanobis": float(np.sqrt((x - mu) @ Si @ (x - mu))),
                   "max_abs_z": float(np.max(np.abs(x)))}
            if "H" in metrics:
                try:
                    c = curvature(gH, x, delta)
                except np.linalg.LinAlgError:
                    row["H_singular"] = 1
                    rows.append(row)
                    continue
                row.update(H_det=c.det, H_mineig=c.eigvals.min(), H_maxeig=c.eigvals.max(),
                           H_neg=int((c.eigvals < 0).sum()), H_R=c.R,
                           H_G_norm=tensor_norm(c.einstein, c.g),
                           H_ric_norm=tensor_norm(c.ricci, c.g))
                if lamf is not None:
                    Tinfo = info_stress_tensor(kde, lamf, c.g, x)
                    row["H_T_norm"] = tensor_norm(Tinfo, c.g)
                    lv, _ = lamf.value_grad(x)
                    row["lam_field"] = float(lv)
                    row["H_T_lam_share"] = tensor_norm(W_LAM * lv * c.g, c.g) / (row["H_T_norm"] + 1e-300)
                    # ajuste G = κT por mínimos quadrados nas 6 componentes independentes
                    iu = np.triu_indices(d)
                    gv, tv = c.einstein[iu], Tinfo[iu]
                    kappa = float(gv @ tv / (tv @ tv + 1e-300))
                    resid = gv - kappa * tv
                    row["H_field_eq_kappa"] = kappa
                    row["H_field_eq_r2"] = float(1 - resid @ resid / (gv @ gv + 1e-300))
                    for (a, b), gval, tval in zip(zip(*iu), gv, tv):
                        row[f"H_G_{a}{b}"] = float(gval)
                        row[f"H_T_{a}{b}"] = float(tval)
            if gF is not None:
                try:
                    cf = curvature(gF, x, delta)
                except np.linalg.LinAlgError:  # região esparsa: um só vizinho efetivo, posto 1
                    row["F_singular"] = 1
                    rows.append(row)
                    continue
                row.update(F_det=cf.det, F_mineig=cf.eigvals.min(), F_maxeig=cf.eigvals.max(),
                           F_R=cf.R, F_G_norm=tensor_norm(cf.einstein, cf.g))
                try:
                    row["Fref_R"] = curvature(gR, x, delta).R
                except np.linalg.LinAlgError:
                    row["Fref_R"] = np.nan
            rows.append(row)
    return pd.DataFrame(rows).set_index("t")
