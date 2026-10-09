#!/usr/bin/env python3
"""Auditoria do diagnóstico exploratório Fisher–Rao (ramo experiment/fisher-rao-trajectory).

Reaproveita EXATAMENTE o pipeline de fisher_rao_trajectory.py (mesmos dados, mesma janela,
mesmo alvo, mesmos folds) e acrescenta:
  1. perdas individuais + Diebold–Mariano com HAC (Newey–West) e bootstrap por blocos;
  2. controle de amplitude de curto prazo (HAR sobre o range high/low passado);
  3. controle GARCH(1,1) (parâmetros estimados só antes do 1º fold de teste);
  4. controle não linear (gradient boosting) com e sem a curvatura;
  5. decomposição da curvatura: quanto dela é explicado por |r| recentes e pelo
     retorno que SAI da janela retangular (r_{t-W}), o "eco" de 1500 barras atrás.
Somente períodos de exploração. Uso: python experiments/fisher_rao_auditoria.py --interval 1m
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fisher_rao_trajectory as fr  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def build(interval, window=1500, max_rows=18000):
    """Cópia linha a linha do main() original, devolvendo os arrays em vez de só o MSE."""
    ts, hi, lo, close, files = fr.read_exploration(interval)
    if len(close) > max_rows:
        ts, hi, lo, close = [a[-max_rows:] for a in (ts, hi, lo, close)]
    step_ms = 60000 if interval == "1m" else 3600000
    valid_step = np.r_[False, np.diff(ts) == step_ms]
    ret = np.r_[np.nan, np.diff(np.log(close))]
    ret[~valid_step] = np.nan
    gaps = np.flatnonzero(~valid_step)
    last_gap = int(gaps[-1]) if len(gaps) else 0
    if last_gap > 0:
        ts, hi, lo, close, ret = [a[last_gap:] for a in (ts, hi, lo, close, ret)]
    ret[0] = 0.
    mu, sig = fr.rolling_mean_std(ret, window)
    start = window + 5
    kraw = fr.curvature(mu[start-3:], sig[start-3:])
    k = np.full(len(ret), np.nan)
    k[start:] = kraw[:-3]
    horizon = 5 if interval == "1m" else 4
    target = np.full(len(ret), np.nan)
    for t in range(start, len(ret)-horizon):
        target[t] = np.log(np.max(hi[t+1:t+horizon+1])/np.min(lo[t+1:t+horizon+1]))
    lag = np.column_stack([np.roll(ret, j) for j in (0, 1, 2, 3, 4)])
    vol = np.column_stack([sig, np.roll(sig, 1), np.roll(sig, 2)])
    fmu, fsig = mu.copy(), sig.copy()
    fmu[:window-1] = mu[window-1]
    fsig[:window-1] = sig[window-1]
    vol_der = np.column_stack([np.gradient(fsig), np.gradient(np.gradient(fsig)),
                               np.gradient(fmu), np.gradient(np.gradient(fmu))])
    vol_der = np.roll(vol_der, 2, axis=0)
    base = np.column_stack([lag, vol])
    expanded = np.column_stack([base, vol_der])
    fisher = np.column_stack([expanded, np.log1p(k)])
    valid = np.isfinite(target) & np.all(np.isfinite(fisher), axis=1)
    valid[:start+5] = False

    # ---- controles novos (todos conhecidos no fechamento da barra t) ----
    lr = np.log(hi/lo)                       # range da própria barra t
    spans = (5, 15, 60) if interval == "1m" else (4, 24, 168)
    har = [np.log(lr + 1e-6)]
    for s in spans:
        c = np.r_[0., np.cumsum(lr)]
        m = np.full(len(lr), np.nan)
        m[s-1:] = (c[s:] - c[:-s]) / s
        har.append(np.log(m + 1e-6))
    absr = [np.abs(np.roll(ret, j)) for j in range(5)]
    har = np.column_stack(har + absr)
    ghost = np.column_stack([np.abs(np.roll(ret, window + j)) for j in range(0, 4)])
    return dict(ts=ts, ret=ret, k=k, y=target, valid=valid, horizon=horizon, window=window,
                base=base, expanded=expanded, fisher=fisher, har=har, ghost=ghost,
                files=files)


def garch_feature(ret, valid, horizon, embargo):
    """GARCH(1,1) gaussiano, parâmetros estimados só nas barras anteriores ao 1º fold de teste;
    feature = log da variância prevista acumulada t+1..t+h, usando info até t."""
    from arch import arch_model
    idx = np.flatnonzero(valid)
    n = len(idx)
    fit_end = idx[n//2 - embargo]
    scale = 1000.0
    r = np.nan_to_num(ret) * scale
    res = arch_model(r[:fit_end], mean="Zero", vol="GARCH", p=1, q=1, dist="normal").fit(disp="off")
    om, al, be = res.params["omega"], res.params["alpha[1]"], res.params["beta[1]"]
    s2 = np.empty(len(r))
    s2[0] = np.var(r[:fit_end])
    for t in range(1, len(r)):
        s2[t] = om + al*r[t-1]**2 + be*s2[t-1]   # s2[t] = var de r_t dado info até t-1
    nxt = om + al*r**2 + be*s2                  # var de r_{t+1} dado info até t
    persist = al + be
    uncond = om / max(1 - persist, 1e-6)
    cum = np.zeros(len(r))
    for j in range(horizon):
        cum += uncond + persist**j * (nxt - uncond)
    return np.log(cum / scale**2)[:, None], dict(omega=om, alpha=al, beta=be)


def oos(x, y, folds=5, embargo=8, model="ridge"):
    n = len(y)
    bounds = np.linspace(n//2, n, folds+1, dtype=int)
    pred = np.full(n, np.nan)
    for left, right in zip(bounds[:-1], bounds[1:]):
        te = left - embargo
        if model == "ridge":
            pred[left:right] = fr.fit_predict(x[:te], y[:te], x[left:right])
        else:
            from sklearn.ensemble import HistGradientBoostingRegressor
            m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                              min_samples_leaf=100, l2_regularization=1.0,
                                              random_state=0)
            m.fit(x[:te], y[:te])
            pred[left:right] = m.predict(x[left:right])
    ok = np.isfinite(pred)
    return (y[ok] - pred[ok])**2, bounds - n//2


def nw_t(d, lag):
    d = d - 0  # loss differential
    T = len(d)
    m = d.mean()
    e = d - m
    v = e @ e / T
    for L in range(1, lag+1):
        v += 2 * (1 - L/(lag+1)) * (e[L:] @ e[:-L]) / T
    return m / np.sqrt(v / T)


def block_boot(la, lb, block, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    T = len(la)
    nb = int(np.ceil(T / block))
    gains = np.empty(B)
    for b in range(B):
        starts = rng.integers(0, T - block, nb)
        ii = (starts[:, None] + np.arange(block)).ravel()[:T]
        gains[b] = (la[ii].mean() - lb[ii].mean()) / la[ii].mean()
    return np.percentile(gains, [2.5, 97.5]).tolist(), float(np.mean(gains <= 0))


def compare(name_a, la, name_b, lb, horizon, fold_bounds, block):
    d = la - lb                                      # >0 ⇒ B melhor
    gain = (la.mean() - lb.mean()) / la.mean()
    folds = [float((la[a:b].mean() - lb[a:b].mean()) / la[a:b].mean())
             for a, b in zip(fold_bounds[:-1], fold_bounds[1:])]
    ci, p_boot = block_boot(la, lb, block)
    T = len(d)
    lag_auto = int(np.floor(4 * (T/100)**(2/9)))
    return {"A": name_a, "B": name_b, "ganho_relativo_MSE_B_sobre_A": float(gain),
            "DM_t_HAC_lag_h": float(nw_t(d, horizon)),
            f"DM_t_HAC_lag_{max(lag_auto, 10*horizon)}": float(nw_t(d, max(lag_auto, 10*horizon))),
            "IC95_bootstrap_blocos": ci, "p_bootstrap_unilateral": p_boot,
            "ganho_por_fold": folds}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", choices=["1m", "1h"], required=True)
    args = ap.parse_args()
    D = build(args.interval)
    v, h = D["valid"], D["horizon"]
    emb = h + 4
    y = D["y"][v]
    lk = np.log1p(D["k"])[:, None]
    g, gpar = garch_feature(D["ret"], v, h, emb)

    X = {
        "baseline": D["base"],
        "derivadas": D["expanded"],
        "derivadas+k": D["fisher"],
        "derivadas+HAR": np.column_stack([D["expanded"], D["har"]]),
        "derivadas+HAR+k": np.column_stack([D["expanded"], D["har"], lk]),
        "derivadas+HAR+GARCH": np.column_stack([D["expanded"], D["har"], g]),
        "derivadas+HAR+GARCH+k": np.column_stack([D["expanded"], D["har"], g, lk]),
        "derivadas+HAR+GARCH+eco": np.column_stack([D["expanded"], D["har"], g, D["ghost"]]),
        "derivadas+HAR+GARCH+eco+k": np.column_stack([D["expanded"], D["har"], g, D["ghost"], lk]),
    }
    loss, mse = {}, {}
    for name, x in X.items():
        loss[name], fb = oos(x[v], y, embargo=emb)
        mse[name] = float(loss[name].mean())
    for name in ("derivadas+HAR+GARCH+eco", "derivadas+HAR+GARCH+eco+k"):
        key = "GBM:" + name
        loss[key], fb = oos(X[name][v], y, embargo=emb, model="gbm")
        mse[key] = float(loss[key].mean())

    block = 60 if args.interval == "1m" else 48
    pairs = [("derivadas", "derivadas+k"),
             ("derivadas", "derivadas+HAR"),
             ("derivadas+HAR", "derivadas+HAR+k"),
             ("derivadas+HAR+GARCH", "derivadas+HAR+GARCH+k"),
             ("derivadas+HAR+GARCH+eco", "derivadas+HAR+GARCH+eco+k"),
             ("GBM:derivadas+HAR+GARCH+eco", "GBM:derivadas+HAR+GARCH+eco+k")]
    tests = [compare(a, loss[a], b, loss[b], h, fb, block) for a, b in pairs]

    # Decomposição da curvatura: o que log(1+k) "é"?
    from sklearn.linear_model import LinearRegression
    kk = lk[v].ravel()
    decomp = {}
    for label, Z in {"|r| t..t-4 + range HAR": D["har"][v],
                     "eco |r_{t-W..t-W-3}|": D["ghost"][v],
                     "HAR + eco": np.column_stack([D["har"][v], D["ghost"][v]]),
                     "HAR + eco + derivadas": np.column_stack([D["har"][v], D["ghost"][v],
                                                               D["expanded"][v]])}.items():
        decomp[label] = float(LinearRegression().fit(Z, kk).score(Z, kk))
    ts_v = D["ts"][v]
    n = len(y)
    test_span = [int(ts_v[n//2]), int(ts_v[-1])]

    out = {"status": "AUDITORIA_EXPLORATORIA", "interval": args.interval, "rows": int(n),
           "linhas_teste": int(len(loss["baseline"])),
           "periodo_teste_ms": test_span, "garch_params_x1000": gpar,
           "mse": mse, "testes": tests, "R2_de_log1p_k_explicado_por": decomp}
    p = ROOT / "reports" / f"FISHER_RAO_AUDITORIA_{args.interval}.json"
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
