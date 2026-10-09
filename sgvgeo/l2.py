"""Linha L2 — geometria de Fisher–Rao do espaço de modelos SF1 (PREREGISTRO_L2.md).

Cada avaliação t (a cada S barras) divide a janela [t−W, t) em duas metades A e B,
ajusta o modelo local SF1-L em cada uma e mede a velocidade de Fisher–Rao
v = √(Δθᵀ Ī Δθ) entre elas.

SF1-L, θ = (log σ; a0, a1, a2, log s1; b0, b1, b2, b3, log s2):
  r  = σ·ε,  ε ~ t_ν (ν fixo por escala)
  ι* = arctanh(ι) = a0 + a1·z + a2·ι*₋₁ + e1,  e1 ~ N(0, s1²)
  ℓ  = log volume = b0 + b1·ℓ₋₁ + b2·|z| + b3·z + e2,  e2 ~ N(0, s2²)
Informação de Fisher por observação (bloco-diagonal; correlação e1–e2 ignorada):
  log σ: 2ν/(ν+3);  (a, log s1): E[xxᵀ]/s1² ⊕ 2;  (b, log s2): E[xxᵀ]/s2² ⊕ 2
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data import T0_MS
from .flow import CLIP, _garch_paths, default_sf1, flow_coordinates


# ---------------------------------------------------------------------------
# Regressores por barra (calculados na série inteira; as janelas só recortam linhas)
# ---------------------------------------------------------------------------
@dataclass
class Rows:
    r: np.ndarray
    Xa: np.ndarray   # [1, z, ι*₋₁]
    ya: np.ndarray   # ι*
    Xb: np.ndarray   # [1, ℓ₋₁, |z|, z]
    yb: np.ndarray   # ℓ
    ok: np.ndarray   # linha utilizável
    ts: np.ndarray


def build_rows(df: pd.DataFrame) -> Rows:
    c = flow_coordinates(df)
    r = c["r"].to_numpy(float)
    z = c["z"].to_numpy(float)
    istar = np.arctanh(np.clip(c["iota"].to_numpy(float), -CLIP, CLIP))
    ell = c["ell"].to_numpy(float)
    istar_l = np.r_[np.nan, istar[:-1]]
    ell_l = np.r_[np.nan, ell[:-1]]
    one = np.ones(len(r))
    Xa = np.column_stack([one, z, istar_l])
    Xb = np.column_stack([one, ell_l, np.abs(z), z])
    ok = np.isfinite(r) & np.all(np.isfinite(Xa), 1) & np.all(np.isfinite(Xb), 1) & np.isfinite(istar) & np.isfinite(ell)
    return Rows(r, Xa, istar, Xb, ell, ok, df["timestamp"].to_numpy())


# ---------------------------------------------------------------------------
# Ajuste local e informação de Fisher
# ---------------------------------------------------------------------------
def t_scale_mle(r: np.ndarray, nu: float, iters: int = 30) -> float:
    """MV da escala de uma t de Student com ν fixo (iteração de pesos)."""
    r = r[np.isfinite(r)]
    s2 = np.mean(r * r) * (nu - 2) / nu if nu > 2 else np.mean(r * r)
    s2 = max(s2, 1e-24)
    for _ in range(iters):
        w = (nu + 1.0) / (nu + r * r / s2)
        s2 = max(np.mean(w * r * r), 1e-24)
    return float(np.sqrt(s2))


def _ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    s = float(np.sqrt(res @ res / max(1, len(y) - X.shape[1])))
    return beta, max(s, 1e-12)


@dataclass
class Local:
    log_sigma: float
    a: np.ndarray
    log_s1: float
    b: np.ndarray
    log_s2: float
    Ia: np.ndarray   # 4×4 (a, log s1)
    Ib: np.ndarray   # 5×5 (b, log s2)

    @property
    def theta_flow(self):
        return np.r_[self.a, self.log_s1, self.b, self.log_s2]


def fit_local(rows: Rows, idx: np.ndarray, nu: float) -> Local:
    idx = idx[rows.ok[idx]]
    sig = t_scale_mle(rows.r[idx], nu)
    a, s1 = _ols(rows.Xa[idx], rows.ya[idx])
    b, s2 = _ols(rows.Xb[idx], rows.yb[idx])
    Ia = np.zeros((4, 4)); Ia[:3, :3] = rows.Xa[idx].T @ rows.Xa[idx] / len(idx) / s1 ** 2; Ia[3, 3] = 2.0
    Ib = np.zeros((5, 5)); Ib[:4, :4] = rows.Xb[idx].T @ rows.Xb[idx] / len(idx) / s2 ** 2; Ib[4, 4] = 2.0
    return Local(np.log(sig), a, np.log(s1), b, np.log(s2), Ia, Ib)


def fisher_rao_speed(A: Local, B: Local, nu: float) -> dict:
    d = B.theta_flow - A.theta_flow
    I = np.zeros((9, 9))
    I[:4, :4] = 0.5 * (A.Ia + B.Ia)
    I[4:, 4:] = 0.5 * (A.Ib + B.Ib)
    v2_flow = float(d @ I @ d)
    dls = B.log_sigma - A.log_sigma
    v2_sig = 2.0 * nu / (nu + 3.0) * dls * dls
    return {"v_fluxo": np.sqrt(max(v2_flow, 0.0)), "v_total": np.sqrt(max(v2_flow + v2_sig, 0.0)),
            "dlog_sigma": dls, "da1": float(B.a[1] - A.a[1])}


# ---------------------------------------------------------------------------
# Série de avaliações (velocidade, alvo e controles)
# ---------------------------------------------------------------------------
def _rv(r, lo, hi):
    seg = r[lo:hi]
    seg = seg[np.isfinite(seg)]
    return float(np.sqrt(np.sum(seg * seg))) if len(seg) else np.nan


def evaluations(df: pd.DataFrame, W: int, S: int, nu: float, split: str | None = None,
                with_target: bool = True, eval_from_ms: int | None = None) -> pd.DataFrame:
    """split=None: ajuste em todas as barras de cada metade; 'par'/'impar': só barras
    de índice par/ímpar (para a confiabilidade). with_target=False não calcula Y.
    eval_from_ms: avalia só a partir desse instante (barras anteriores entram apenas
    como histórico das janelas, nunca como alvo)."""
    rows = build_rows(df)
    n, half = len(rows.r), W // 2
    first = W + 2 * S + 61  # aquecimento: janela, RV anterior e σ de 60 barras de z
    out = []
    for t in range(first, n - (S if with_target else 0) + 1, S):
        if eval_from_ms is not None and rows.ts[t - 1] < eval_from_ms:
            continue  # dados anteriores servem só de histórico das janelas
        ia = np.arange(t - W, t - half)
        ib = np.arange(t - half, t)
        if split == "par":
            ia, ib = ia[ia % 2 == 0], ib[ib % 2 == 0]
        elif split == "impar":
            ia, ib = ia[ia % 2 == 1], ib[ib % 2 == 1]
        if rows.ok[ia].sum() < 0.8 * len(ia) or rows.ok[ib].sum() < 0.8 * len(ib):
            continue
        A, B = fit_local(rows, ia, nu), fit_local(rows, ib, nu)
        rec = {"t": t, "timestamp": int(rows.ts[t - 1])} | fisher_rao_speed(A, B, nu)
        rv_prev = _rv(rows.r, t - S, t)
        rec |= {"log_rv_S": np.log(rv_prev), "log_rv_W": np.log(_rv(rows.r, t - W, t)),
                "abs_dlog_rv_recente": abs(np.log(rv_prev / _rv(rows.r, t - 2 * S, t - S)))}
        if with_target:
            rec["Y"] = abs(np.log(_rv(rows.r, t, t + S) / rv_prev))
        out.append(rec)
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# Teste primário: Spearman parcial + permutação por deslocamento circular
# ---------------------------------------------------------------------------
def _ranks(x):
    return pd.Series(x).rank().to_numpy(float)


def partial_spearman_test(ev: pd.DataFrame, x: str, y: str, controls: list[str], season: str,
                          min_shift: int, n_perm: int = 999, seed: int = 0) -> dict:
    d = ev.dropna(subset=[x, y] + controls).reset_index(drop=True)
    ts = pd.to_datetime(d["timestamp"], unit="ms", utc=True)
    dummies = (pd.get_dummies(ts.dt.hour if season == "hora" else ts.dt.dayofweek, drop_first=True)
               .to_numpy(float))
    C = np.column_stack([np.ones(len(d))] + [_ranks(d[c]) for c in controls] + [dummies])
    def resid(v):
        beta, *_ = np.linalg.lstsq(C, v, rcond=None)
        return v - C @ beta
    rx, ry = resid(_ranks(d[x])), resid(_ranks(d[y]))
    rho = float(np.corrcoef(rx, ry)[0, 1])
    n = len(d)
    rng = np.random.default_rng(seed)
    lo, hi = min_shift, n - min_shift
    shifts = rng.choice(np.arange(lo, hi), size=min(n_perm, hi - lo), replace=False) if hi > lo else []
    null = np.array([np.corrcoef(np.roll(rx, s), ry)[0, 1] for s in shifts])
    p = float((1 + np.sum(null >= rho)) / (1 + len(null)))
    return {"rho_parcial": rho, "p_unilateral": p, "n": int(n), "n_perm": int(len(null)),
            "nulo_p95": float(np.quantile(null, 0.95)) if len(null) else np.nan}


CONTROLS = ["log_rv_S", "log_rv_W", "abs_dlog_rv_recente", "abs_dlog_sigma"]


def run_primary(ev: pd.DataFrame, W: int, S: int, season: str, n_perm: int = 999, seed: int = 0) -> dict:
    ev = ev.copy()
    ev["abs_dlog_sigma"] = ev["dlog_sigma"].abs()
    return partial_spearman_test(ev, "v_fluxo", "Y", CONTROLS, season, min_shift=W // S,
                                 n_perm=n_perm, seed=seed)


# ---------------------------------------------------------------------------
# Sintéticos de calibração
# ---------------------------------------------------------------------------
def simulate_planted(n: int, seed: int, S: int, lag_steps: int = 2, p_stay: float = 0.999,
                     a1_shift: float = 0.65, vol_mult: float = 2.0, step_ms: int = 60_000,
                     planted: bool = True) -> pd.DataFrame:
    """SF1 padrão; se planted, um regime oculto de Markov muda a curva de impacto (a1)
    e a persistência do fluxo AGORA, e multiplica a volatilidade só lag_steps·S barras
    DEPOIS — a estrutura que H-L2 diz existir. planted=False: SF1 estacionário."""
    m = default_sf1()
    rng = np.random.default_rng(seed)
    r0, sig = _garch_paths(n, m.garch, rng)
    s = np.zeros(n, int)
    if planted:
        flips = rng.random(n) > p_stay
        for t in range(1, n):
            s[t] = 1 - s[t - 1] if flips[t] else s[t - 1]
    lag = lag_steps * S
    s_lag = np.r_[np.zeros(lag, int), s[:-lag]] if planted else s
    mult = 1.0 + (vol_mult - 1.0) * s_lag
    r = r0 * mult
    z = r0 / sig
    s1, s2 = m.e_sd
    cov = [[s1 * s1, m.e_corr * s1 * s2], [m.e_corr * s1 * s2, s2 * s2]]
    E = rng.multivariate_normal([0, 0], cov, n)
    b0, b1, b2, b3 = m.b
    ell = np.empty(n); prev = b0 / (1 - b1)
    for t in range(n):
        prev = b0 + b1 * prev + b2 * abs(z[t]) + b3 * z[t] + E[t, 1] + 0.3 * np.log(mult[t])
        ell[t] = prev
    a0, a1, a2 = m.a
    istar = np.empty(n); prev = 0.0
    for t in range(n):
        prev = a0 + (a1 + a1_shift * s[t]) * z[t] + (a2 + 0.3 * s[t]) * prev + E[t, 0]
        istar[t] = prev
    iota = np.tanh(istar)
    p0 = 60_000.0
    close = p0 * np.exp(np.cumsum(r))
    open_ = np.r_[p0, close[:-1]]
    vol = np.exp(ell)
    ts = T0_MS + step_ms * np.arange(n)
    return pd.DataFrame({"timestamp": ts, "open": open_, "high": np.maximum(open_, close),
                         "low": np.minimum(open_, close), "close": close, "volume": vol,
                         "taker_buy": (iota + 1) / 2 * vol, "regime_oculto": s})
