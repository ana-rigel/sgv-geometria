"""Exploração: o que sobra da geometria do mercado quando memória linear + volatilidade agrupada são reproduzidas?

Previsão e critérios: PREDICAO_geometria_residual.md (registrada antes deste código).

    python pipeline/explora_geometria_residual.py --periodo fumaca   # maio, só confere que roda; não imprime estatísticas
    python pipeline/explora_geometria_residual.py --periodo junjul
    python pipeline/explora_geometria_residual.py --periodo agoset
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline")); sys.path.insert(0, str(ROOT / "vendor" / "u031"))
import explora_forma_D_casca as E  # noqa: E402  (carregar, coords_orig; importa vendor/m11i e vendor/sgv_original)
import u031_casca  # noqa: E402
from u031_casca import build_shell, hdr_mesh  # noqa: E402

u031_casca.OUTER_EXTENT = 10.0; u031_casca.OUTER_GRID = 61
PERIODOS = {"fumaca": (["2026-05"], "2026-05-03", "2026-05-17"),
            "junjul": (["2026-05", "2026-06", "2026-07"], "2026-06-01", "2026-08-01"),
            "agoset": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"], "2026-08-01", "2026-10-01")}
K, P_LL, W, SNAP, LAG = 200, 4, 1500, 240, 7
SEEDS_SINT = [2026, 2027, 2028, 2029, 2030]
FAIXAS = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 10)]


# ---------- séries: real, sintéticas (AR(1) + caminho de volatilidade), nula antiga (permutação no dia) ----------
def semanas(ts, ini, fim):
    out = []; s = pd.Timestamp(ini, tz="UTC"); fim = pd.Timestamp(fim, tz="UTC")
    while s < fim:
        e = min(s + pd.Timedelta(days=7), fim)
        idx = np.where((ts >= s).to_numpy() & (ts < e).to_numpy())[0]
        if len(idx): out.append(idx)
        s = e
    return out


def sintetica(kl, ts, i0, seed):
    """Fechamento sintético a partir de i0 (antes de i0 fica real). Ver PREDICAO §'O mercado sintético'."""
    rng = np.random.default_rng(seed); lc = np.log(kl.close.values.astype(float)); r = np.diff(lc, prepend=lc[0])
    rs = r.copy()
    for idx in semanas(ts, str(ts.iloc[i0].date()), str((ts.iloc[-1] + pd.Timedelta(minutes=1)))):
        idx = idx[idx >= i0]
        if len(idx) < 100: continue
        x = r[idx]; A = np.column_stack([np.ones(len(x) - 1), x[:-1]]); a, phi = np.linalg.lstsq(A, x[1:], rcond=None)[0]
        e = np.r_[0.0, x[1:] - (a + phi * x[:-1])]
        s = np.sqrt(pd.Series(e ** 2).rolling(61, center=True, min_periods=10).mean().to_numpy())
        s = np.where(np.isfinite(s) & (s > 0), s, np.nanmedian(s))
        u = e / s; u[0] = 0.0; us = rng.permutation(u)
        y = np.empty(len(x)); y[0] = x[0]
        for t in range(1, len(x)): y[t] = a + phi * y[t - 1] + s[t] * us[t]
        rs[idx] = y
    c = np.exp(lc[0] + np.cumsum(np.r_[0.0, rs[1:]]))
    out = kl.copy(); out["close"] = c; out["open"] = np.r_[c[0], c[:-1]]
    up = np.log(kl.high.values / kl.close.values); dn = np.log(kl.close.values / kl.low.values)
    out["high"] = c * np.exp(np.maximum(up, 0)); out["low"] = c * np.exp(-np.maximum(dn, 0))
    return out


def permutada(kl, ts, i0, seed=2026):
    rng = np.random.default_rng(seed); day = ts.dt.floor("D").to_numpy(); r0 = np.log(kl.close.values.astype(float))
    lr = np.diff(r0, prepend=r0[0]); hi = np.log(kl.high.values) - r0; lo = r0 - np.log(kl.low.values); perm = np.arange(len(kl))
    for d_ in np.unique(day[i0:]):
        s = np.where(day == d_)[0]; s = s[s >= i0]; perm[s] = rng.permutation(s)
    c2 = np.exp(r0[0] + np.cumsum(lr[perm])); out = kl.copy()
    out["close"] = c2; out["open"] = np.r_[c2[0], c2[:-1]]; out["high"] = c2 * np.exp(hi[perm]); out["low"] = c2 * np.exp(-lo[perm])
    out["volume"] = kl.volume.values[perm]
    return out


def regua(raw, may):
    ok = np.isfinite(raw).all(1); anc = raw[may & ok]
    med = np.median(anc, 0); esc = np.quantile(np.abs(anc - med), 0.995, axis=0) / 3.0
    G = np.full_like(raw, np.nan); G[ok] = (raw[ok] - med) / esc
    return G


# ---------- P1: campo localmente linear (idêntico ao H-CAUDA-01) ----------
def campo_ll(Xtr, Str, P0):
    d, idx = cKDTree(Xtr).query(P0, k=K)
    rk = np.maximum(d[:, -1], 1e-12)
    w = np.clip(1 - (d / rk[:, None]) ** 3, 0, None) ** 3
    sw = w.sum(1); ess = sw ** 2 / np.maximum((w ** 2).sum(1), 1e-300)
    Z = np.concatenate([np.ones((len(P0), K, 1)), Xtr[idx] - P0[:, None, :]], axis=2)
    ZtW = Z * w[:, :, None]
    beta = np.linalg.solve(np.einsum("nki,nkj->nij", ZtW, Z) + 1e-9 * np.eye(P_LL), np.einsum("nki,nkj->nij", ZtW, Str[idx]))
    R = Str[idx] - np.einsum("nki,nij->nkj", Z, beta)
    return np.einsum("nk,nkj->n", w, R ** 2) / sw / np.maximum(1 - P_LL / ess, 0.05)


def p1(G, wk):
    rng = np.random.default_rng(20261019); D, X = [], []
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        Xa = G[tr[:-1]]; S = G[tr[1:]] - G[tr[:-1]]; ok = np.isfinite(Xa).all(1) & np.isfinite(S).all(1)
        P0 = G[te]; P0 = P0[np.isfinite(P0).all(1)]; ext = np.abs(P0).max(1)
        core = np.where(ext < 1)[0]; core = rng.choice(core, min(3000, len(core)), replace=False)
        sel = np.r_[core, np.where(ext >= 1)[0]]
        for a in range(0, len(sel), 2000):
            s = sel[a:a + 2000]; D.append(campo_ll(Xa[ok], S[ok], P0[s])); X.append(ext[s])
    D, X = np.concatenate(D), np.concatenate(X)
    perfil = {f"{lo}-{hi}": float(np.median(D[(X >= lo) & (X < hi)])) if ((X >= lo) & (X < hi)).any() else None for lo, hi in FAIXAS}
    ext_m = (X >= 3) & (X < 10)
    return {"R": float(np.median(D[ext_m]) / np.median(D[X < 1])) if ext_m.any() else None, "perfil": perfil,
            "n_extremos": int(ext_m.sum())}


# ---------- P2/P3: cascas ----------
def axes(t):
    I = np.asarray(t.moment_inertia, float); vol = abs(float(t.volume))
    cov = ((np.trace(I) / 2) * np.eye(3) - I) / vol
    w, Q = np.linalg.eigh(cov); idx = np.argsort(w)[::-1]
    return Q[:, idx]


def angulo(Qa, Qb):
    best = 180.0
    for s in ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)):
        R = Qb @ np.diag(s) @ Qa.T
        best = min(best, np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
    return best


def mapas(G, absr, i_ini, i_fim):
    M = {}
    for k, s in enumerate(range(i_ini, i_fim + 1, SNAP)):
        X = G[s - W:s]; X = X[np.isfinite(X).all(1)]; r = absr[s - W:s]; r = r[np.isfinite(r)]
        if len(X) < 0.95 * W: continue
        try:
            inner = build_shell(X, seed=20261009, n=25); outer, _ = hdr_mesh(inner.params, .95)
            M[k] = {"v50": float(abs(inner.mesh.volume)), "v95": float(abs(outer.volume)), "Q": axes(inner.mesh),
                    "q": float(np.quantile(r, .999) / np.median(r))}
        except Exception:
            continue
    return M


def p23(G, kl, i_ini, i_fim):
    absr = np.abs(np.diff(np.log(kl.close.values.astype(float)), prepend=np.nan))
    M = mapas(G, absr, i_ini, i_fim); pares = [(M[k], M[k + LAG]) for k in M if k + LAG in M]
    rot = [angulo(a["Q"], b["Q"]) for a, b in pares]; lv = [abs(np.log(b["v50"] / a["v50"])) / 3 for a, b in pares]
    feat = [np.log(b["v95"] / a["v95"]) / 3 - np.log(b["v50"] / a["v50"]) / 3 for a, b in pares]
    ref = [np.log(b["q"] / a["q"]) for a, b in pares]
    return {"mapas_validos": len(M), "pares": len(pares), "rot_mediana": float(np.median(rot)), "logV50_mediano": float(np.median(lv)),
            "rho_caudas": float(spearmanr(feat, ref).correlation)}


def medir(kl, ts, may, wk, i_ini, i_fim):
    G = regua(E.coords_orig(kl), may)
    return {"P1": p1(G, wk), **{"P23": p23(G, kl, i_ini, i_fim)}}


def classificar(real, sint, menor_melhor=False):
    s = np.array(sint)
    if menor_melhor:
        return "própria" if real < s.min() else ("indício" if real < s.mean() else "reproduzida")
    return "própria" if real > s.max() else ("indício" if real > s.mean() else "reproduzida")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    if a.periodo == "fumaca":
        may = (ts < pd.Timestamp("2026-05-03", tz="UTC")).to_numpy()
    i0 = int(np.argmax(~may)); wk = semanas(ts, ini, fim)
    i_ini = int(np.searchsorted(ts.values, pd.Timestamp(ini, tz="UTC").to_datetime64())); i_fim = int(np.searchsorted(ts.values, pd.Timestamp(fim, tz="UTC").to_datetime64()))
    series = {"real": kl, **{f"sint_{s}": sintetica(kl, ts, i0, s) for s in SEEDS_SINT}, "perm": permutada(kl, ts, i0)}
    res = {}
    for nome, k_ in series.items():
        res[nome] = medir(k_, ts, may, wk, i_ini, i_fim); print(f"  {nome}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    sint = [res[f"sint_{s}"] for s in SEEDS_SINT]
    out = {"periodo": a.periodo, "series": res, "classificacao": {
        "P1_agitacao_extremos": classificar(res["real"]["P1"]["R"], [x["P1"]["R"] for x in sint]),
        "P2_rotacao_cascas": classificar(res["real"]["P23"]["rot_mediana"], [x["P23"]["rot_mediana"] for x in sint], menor_melhor=True),
        "P2_secundaria_logV50": classificar(res["real"]["P23"]["logV50_mediano"], [x["P23"]["logV50_mediano"] for x in sint], menor_melhor=True),
        "P3_assinatura_caudas": classificar(res["real"]["P23"]["rho_caudas"], [x["P23"]["rho_caudas"] for x in sint])}}
    print(f"\n== geometria residual [{a.periodo}]")
    for nome in series:
        r = res[nome]; print(f"  {nome:10s} P1 R {r['P1']['R']:.2f}  perfil {[round(v, 2) if v else None for v in r['P1']['perfil'].values()]}  "
                             f"| P2 rot {r['P23']['rot_mediana']:.1f}° logV50 {r['P23']['logV50_mediano']:.3f} | P3 ρ {r['P23']['rho_caudas']:+.3f} (pares {r['P23']['pares']})")
    print("  classificação:", out["classificacao"])
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"geometria_residual_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
