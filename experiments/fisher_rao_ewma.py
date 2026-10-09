#!/usr/bin/env python3
"""Reformulação única da linha Fisher–Rao (PLANO.md, após G1 reprovado).

Especificação congelada em reports/PREREGISTRO_FR_EWMA.md. Resumo:
  • estados (μ_t, σ_t) da gaussiana dos retornos log de 1 barra, por EWMA com o mesmo
    centro de massa da janela retangular de 1.500 barras (span 1.500 ⇒ λ = 1 − 2/1501);
  • curvatura geodésica κ_t da trajetória na métrica de Fisher ds² = (dμ² + 2dσ²)/σ²,
    com diferenças só para trás (κ_t usa informação até o fechamento de t, sem deslocamento);
  • alvo: log R, com R = log(max high / min low) em t+1..t+h (h = 5 em 1m, 4 em 1h);
  • M0 (controle): retornos com sinal t..t−4, |r| t..t−4, log-range HAR (barra t e médias),
    variância GARCH(1,1) prevista para t+1..t+h, log σ_t, μ_t/σ_t, derivadas EWMA
    normalizadas (u, v, du, dv)/σ, dummies de hora UTC;  M1 = M0 + log κ_t;
  • ridge (λ=10) em janela expansiva com embargo, perda quadrática, DM unilateral com HAC.

Uso:
  python experiments/fisher_rao_ewma.py --interval 1m --fase exploracao
  python experiments/fisher_rao_ewma.py --interval 1h --fase confirmatorio   # só após aprovação
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "reports" / "PREREGISTRO_FR_EWMA.md"

# ---------------- constantes congeladas ----------------
SPAN = 1500
LAMBDA = 1.0 - 2.0 / (SPAN + 1)
WARMUP = 3 * SPAN                        # barras descartadas no início da série
HORIZON = {"1m": 5, "1h": 4}
HAR_SPANS = {"1m": (5, 15, 60), "1h": (4, 24, 168)}
STEP_MS = {"1m": 60_000, "1h": 3_600_000}
RIDGE = 10.0
EMBARGO_EXTRA = 4                        # embargo = h + 4 barras
HAC_LAG = {"1m": 1440, "1h": 24}         # um dia de barras
EXPLORACAO = {"1m": ("2026-05", "2026-07"), "1h": ("2020-01", "2024-12")}
CONFIRMATORIO_DESDE = {"1m": "2026-08", "1h": "2025-01"}
CONFIRMATORIO_ATE = {"1m": "2026-09", "1h": "2026-09"}   # fixado no pré-registro
N_FOLDS_EXPLORACAO = 6
PORTAO_P = 0.10


# ---------------- dados ----------------
def _month_of(path: Path, interval: str) -> str:
    m = re.fullmatch(rf"BTCUSDT-{interval}-(\d{{4}}-\d{{2}})\.zip", path.name)
    if not m:
        raise ValueError(f"nome inesperado: {path.name}")
    return m.group(1)


def load(interval: str, fase: str):
    """Exploração: só os meses de exploração. Confirmatório: exploração + reservado
    (o reservado só é usado como teste; exploração entra como treino inicial)."""
    paths = sorted((ROOT / "data").glob(f"BTCUSDT-{interval}-*.zip"))
    lo, hi = EXPLORACAO[interval]
    keep = []
    for p in paths:
        mo = _month_of(p, interval)
        if lo <= mo <= hi:
            keep.append(p)
        elif mo >= CONFIRMATORIO_DESDE[interval]:
            if fase != "confirmatorio":
                raise ValueError(f"{p.name} é do período reservado; remova-o de data/ ou use --fase confirmatorio")
            ate = CONFIRMATORIO_ATE[interval]
            if ate is None or mo <= ate:
                keep.append(p)
    if fase == "confirmatorio" and not PREREG.exists():
        raise RuntimeError("pré-registro ausente; confirmatório bloqueado")
    rows = []
    for p in keep:
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():
                if not name.endswith(".csv"):
                    continue
                with z.open(name) as s:
                    for r in csv.reader(io.TextIOWrapper(s)):
                        try:
                            ts = int(r[0]); h = float(r[2]); l = float(r[3]); c = float(r[4])
                        except (ValueError, IndexError):
                            continue
                        if ts > 10**14:
                            ts //= 1000
                        rows.append((ts, h, l, c))
    a = np.array(rows, dtype=float)
    a = a[np.argsort(a[:, 0])]
    ts = a[:, 0].astype(np.int64)
    if np.any(np.diff(ts) <= 0):
        raise ValueError("timestamps duplicados/fora de ordem")
    return ts, a[:, 1], a[:, 2], a[:, 3], [p.name for p in keep]


# ---------------- geometria ----------------
def ewma_states(ret: np.ndarray, ok: np.ndarray, lam: float = LAMBDA):
    """μ_t, σ_t usando retornos até t. Barras com ok=False não atualizam o estado."""
    n = len(ret)
    mu = np.full(n, np.nan); s2 = np.full(n, np.nan)
    first = int(np.flatnonzero(ok)[0])
    m, v = 0.0, float(ret[first]) ** 2 + 1e-10   # inicialização irrelevante após WARMUP
    for t in range(first, n):
        if ok[t]:
            e = ret[t] - m
            m = lam * m + (1 - lam) * ret[t]
            v = lam * v + (1 - lam) * e * e
        mu[t] = m; s2[t] = v
    return mu, np.sqrt(np.maximum(s2, 1e-16))


def fisher_curvature_backward(mu: np.ndarray, sig: np.ndarray):
    """Curvatura geodésica da curva (μ_t, σ_t) na métrica (dμ² + 2dσ²)/σ².
    Velocidade e aceleração por diferenças para trás: em t usa t, t−1, t−2.
    Christoffel: Γ^μ_{μσ} = −1/σ; Γ^σ_{μμ} = 1/(2σ); Γ^σ_{σσ} = −1/σ."""
    u = np.full_like(mu, np.nan); v = np.full_like(mu, np.nan)
    u[1:] = np.diff(mu); v[1:] = np.diff(sig)
    du = np.full_like(mu, np.nan); dv = np.full_like(mu, np.nan)
    du[1:] = np.diff(u); dv[1:] = np.diff(v)
    s = sig
    ax = du - 2 * u * v / s
    ay = dv + u * u / (2 * s) - v * v / s
    sp2 = (u * u + 2 * v * v) / (s * s)
    aa = (ax * ax + 2 * ay * ay) / (s * s)
    ua = (u * ax + 2 * v * ay) / (s * s)
    # κ² = (|a|²|v|² − ⟨v,a⟩²)/|v|⁶; velocidade nula (barra sem atualização) ⇒ indefinida
    with np.errstate(divide="ignore", invalid="ignore"):
        k2 = np.where(sp2 > 0, (aa * sp2 - ua**2) / sp2**3, np.nan)
    return np.sqrt(np.maximum(k2, 0.0)), u, v, du, dv


# ---------------- features ----------------
def _trailing_mean(x, w):
    c = np.r_[0.0, np.cumsum(x)]
    out = np.full(len(x), np.nan)
    out[w - 1:] = (c[w:] - c[:-w]) / w
    return out


def _lag(x, j):
    out = np.full(len(x), np.nan)
    out[j:] = x[: len(x) - j] if j else x
    return out


def garch_logvar(ret, fit_mask, h):
    from arch import arch_model
    scale = 1000.0
    r = np.nan_to_num(ret) * scale
    res = arch_model(r[fit_mask], mean="Zero", vol="GARCH", p=1, q=1, dist="normal").fit(disp="off")
    om, al, be = (float(res.params[k]) for k in ("omega", "alpha[1]", "beta[1]"))
    s2 = np.empty(len(r)); s2[0] = np.var(r[fit_mask])
    for t in range(1, len(r)):
        s2[t] = om + al * r[t - 1] ** 2 + be * s2[t - 1]
    nxt = om + al * r**2 + be * s2              # var(r_{t+1} | info até t)
    p = al + be; unc = om / max(1 - p, 1e-6)
    cum = sum(unc + p**j * (nxt - unc) for j in range(h))
    return np.log(cum / scale**2), dict(omega=om, alpha=al, beta=be)


def build(interval: str, fase: str):
    ts, hi, lo, close, files = load(interval, fase)
    h = HORIZON[interval]
    step = STEP_MS[interval]
    contig = np.r_[False, np.diff(ts) == step]
    ret = np.r_[np.nan, np.diff(np.log(close))]
    ret[~contig] = np.nan
    ok = np.isfinite(ret)
    # barras desde a última lacuna (para aquecimento após lacuna)
    since = np.zeros(len(ts), dtype=np.int64)
    c = 0
    for t in range(len(ts)):
        c = c + 1 if contig[t] else 0
        since[t] = c
    mu, sig = ewma_states(ret, ok)
    k, u, v, du, dv = fisher_curvature_backward(mu, sig)
    logk = np.log(k + 1e-12)

    # alvo: log do range de t+1..t+h, só se as h barras seguintes forem contíguas
    from numpy.lib.stride_tricks import sliding_window_view as swv
    y = np.full(len(ts), np.nan)
    hmax = swv(hi[1:], h).max(1); lmin = swv(lo[1:], h).min(1)
    cont = swv(contig[1:], h).all(1)
    yy = np.log(np.log(hmax / lmin) + 1e-6)
    y[: len(yy)] = np.where(cont, yy, np.nan)

    rng = np.log(hi / lo)
    har = [np.log(rng + 1e-6)] + [np.log(_trailing_mean(rng, w) + 1e-6) for w in HAR_SPANS[interval]]
    r0 = np.nan_to_num(ret)
    signed = [_lag(r0, j) for j in range(5)]
    absr = [np.abs(_lag(r0, j)) for j in range(5)]
    hour = ((ts // 3_600_000) % 24).astype(int)
    hours = [(hour == j).astype(float) for j in range(1, 24)]
    ders = [u / sig, v / sig, du / sig, dv / sig]
    state = [np.log(sig), mu / sig]

    m0_cols = signed + absr + har + state + ders + hours
    names = ([f"r_l{j}" for j in range(5)] + [f"absr_l{j}" for j in range(5)]
             + ["logrange_t"] + [f"logrange_mean{w}" for w in HAR_SPANS[interval]]
             + ["log_sigma", "mu_over_sigma", "u_s", "v_s", "du_s", "dv_s"]
             + [f"hora_{j}" for j in range(1, 24)])
    first = int(np.flatnonzero(ok)[0])
    valid = np.isfinite(y) & (np.arange(len(ts)) >= first + WARMUP) & np.isfinite(logk)
    valid &= since >= max(HAR_SPANS[interval]) + 3      # nada atravessa lacuna
    valid &= np.all(np.isfinite(np.column_stack(m0_cols)), axis=1)

    # fronteira de teste
    if fase == "exploracao":
        idx = np.flatnonzero(valid)
        oos_start = idx[len(idx) // 2]
    else:
        cut = int(datetime.strptime(CONFIRMATORIO_DESDE[interval], "%Y-%m")
                  .replace(tzinfo=timezone.utc).timestamp() * 1000)
        oos_start = int(np.searchsorted(ts, cut))
    emb = h + EMBARGO_EXTRA
    fit_mask = np.zeros(len(ts), bool); fit_mask[: max(oos_start - emb, 0)] = True
    g, gpar = garch_logvar(ret, fit_mask, h)
    X0 = np.column_stack(m0_cols + [g])
    X1 = np.column_stack([X0, logk])
    names = names + ["garch_logvar_h", "log_kappa"]
    valid &= np.isfinite(g)
    return dict(ts=ts, y=y, X0=X0, X1=X1, valid=valid, oos_start=oos_start, h=h,
                emb=emb, names=names, garch=gpar, files=files, logk=logk)


# ---------------- avaliação ----------------
def ridge_fit_predict(xtr, ytr, xte, lam=RIDGE):
    m = xtr.mean(0); s = xtr.std(0); s[s < 1e-12] = 1.0
    a = np.column_stack([np.ones(len(xtr)), (xtr - m) / s])
    b = np.column_stack([np.ones(len(xte)), (xte - m) / s])
    P = np.eye(a.shape[1]) * lam; P[0, 0] = 0
    return b @ np.linalg.solve(a.T @ a + P, a.T @ ytr)


def fold_bounds(D, interval, fase):
    ts, valid, start = D["ts"], D["valid"], D["oos_start"]
    test_idx = np.flatnonzero(valid & (np.arange(len(ts)) >= start))
    if fase == "exploracao":
        cuts = np.linspace(0, len(test_idx), N_FOLDS_EXPLORACAO + 1, dtype=int)
        return [(test_idx[a], test_idx[b - 1] + 1) for a, b in zip(cuts[:-1], cuts[1:])]
    months = np.array([datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%Y-%m")
                       for t in ts[test_idx]])
    out = []
    for mo in dict.fromkeys(months):
        sel = test_idx[months == mo]
        out.append((sel[0], sel[-1] + 1))
    return out


def run_oos(D, interval, fase):
    y, valid, emb = D["y"], D["valid"], D["emb"]
    pred0 = np.full(len(y), np.nan); pred1 = np.full(len(y), np.nan)
    folds = fold_bounds(D, interval, fase)
    for a, b in folds:
        tr = np.flatnonzero(valid[: a - emb])
        te = np.arange(a, b)[valid[a:b]]
        pred0[te] = ridge_fit_predict(D["X0"][tr], y[tr], D["X0"][te])
        pred1[te] = ridge_fit_predict(D["X1"][tr], y[tr], D["X1"][te])
    return pred0, pred1, folds


def newey_west_t(d, lag):
    T = len(d); e = d - d.mean()
    v = e @ e / T
    for L in range(1, lag + 1):
        v += 2 * (1 - L / (lag + 1)) * (e[L:] @ e[:-L]) / T
    return d.mean() / np.sqrt(v / T)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", choices=["1m", "1h"], required=True)
    ap.add_argument("--fase", choices=["exploracao", "confirmatorio"], required=True)
    args = ap.parse_args()
    from scipy.stats import norm
    D = build(args.interval, args.fase)
    p0, p1, folds = run_oos(D, args.interval, args.fase)
    te = np.isfinite(p0)
    y = D["y"][te]
    l0 = (y - p0[te]) ** 2; l1 = (y - p1[te]) ** 2
    d = l0 - l1
    t = float(newey_west_t(d, HAC_LAG[args.interval]))
    p = float(1 - norm.cdf(t))
    gain = float(d.mean() / l0.mean())
    per_fold = []
    for a, b in folds:
        sel = te[a:b]
        y_ = D["y"][a:b][sel]; a0 = (y_ - p0[a:b][sel]) ** 2; a1 = (y_ - p1[a:b][sel]) ** 2
        per_fold.append({"inicio": datetime.fromtimestamp(D["ts"][a] / 1000, timezone.utc).isoformat(),
                         "n": int(sel.sum()), "ganho": float((a0.mean() - a1.mean()) / a0.mean())})
    # descritivo: quanto de log κ o controle explica (na amostra de teste)
    from sklearn.linear_model import LinearRegression
    X0te = D["X0"][te]; kte = D["logk"][te]
    r2 = float(LinearRegression().fit(X0te, kte).score(X0te, kte))
    out = {
        "status": "PORTAO_EXPLORATORIO" if args.fase == "exploracao" else "CONFIRMATORIO",
        "interval": args.interval, "arquivos": D["files"],
        "prereg_sha256": hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None,
        "span": SPAN, "lambda": LAMBDA, "horizon": D["h"], "hac_lag": HAC_LAG[args.interval],
        "n_teste": int(te.sum()), "garch_x1000": D["garch"],
        "mse_M0": float(l0.mean()), "mse_M1": float(l1.mean()),
        "ganho_relativo_M1_sobre_M0": gain, "DM_t": t, "p_unilateral": p,
        "folds": per_fold, "R2_logkappa_pelo_controle": r2,
    }
    if args.fase == "exploracao":
        out["portao"] = {"regra": f"ganho > 0 e p < {PORTAO_P}",
                         "passa": bool(gain > 0 and p < PORTAO_P)}
    tag = f"FR_EWMA_{'EXPLORACAO' if args.fase == 'exploracao' else 'CONFIRMATORIO'}_{args.interval}"
    (ROOT / "reports" / f"{tag}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    with gzip.open(ROOT / "reports" / f"{tag}_perdas.csv.gz", "wt", newline="") as f:
        w = csv.writer(f); w.writerow(["ts", "y", "pred_M0", "pred_M1"])
        for i in np.flatnonzero(te):
            w.writerow([int(D["ts"][i]), f"{D['y'][i]:.8g}", f"{p0[i]:.8g}", f"{p1[i]:.8g}"])
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
