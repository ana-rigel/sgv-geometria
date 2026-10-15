"""Exploração: o desacoplamento entre a forma de D e a forma da casca no fluxo é memória linear de 1 minuto, ou
estrutura não linear/local (de campo)?

Previsão registrada antes de qualquer cálculo: PREDICAO_memoria_D.md.

    python pipeline/explora_memoria_D.py --periodo fumaca   # só confere que o código roda (3 dias de maio, a âncora)
    python pipeline/explora_memoria_D.py --periodo junjul
    python pipeline/explora_memoria_D.py --periodo agoset

Mesmas coordenadas, régua, mapas, D̄ e Σ_mix de pipeline/explora_forma_D_casca.py (funções importadas, não copiadas).
Em cada mapa, além de D̄ e Σ_mix, ajusta um VAR(1) de 1 minuto nos pares (x_t, x_{t+1}) da janela:
x_{t+1} = c + Φ x_t + e, com Q = cov(e). Se a memória fosse linear, D(x) seria Q em todo ponto, e a forma média de D
seria a forma de Q. Forma de Q: FQ = Q / tr Q. Mudanças entre mapas: dFD, dFS, dFQ (norma de Frobenius) e |Δφ_jj|.

Nula de pipeline: 5 réplicas (sementes 2026 … 2030), a mesma permutação dentro do dia da exploração anterior.
Sem assinatura M11-I (não entra aqui), por isso sem build_shell.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
from sklearn.mixture import GaussianMixture

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_forma_D_casca as E  # noqa: E402  (carregar, COORDS, gaussianize, dbar, W, SNAP)

R_NULA, B_BOOT = 5, 1000
PERIODOS = {"fumaca": (["2026-05"], "2026-05-03", "2026-05-06"),
            "junjul": (["2026-05", "2026-06", "2026-07"], "2026-06-01", "2026-08-01"),
            "agoset": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"], "2026-08-01", "2026-10-01")}
EIXOS = {"flow": ["z", "iota", "nu"], "orig": ["E_norm", "jerk", "memory_flux"]}


def mapas(G, i0, i1, tag):
    out = []
    for k, s in enumerate(range(i0, i1, E.SNAP)):
        win = G[s - E.W + 1:s + 1]; win = win[np.isfinite(win).all(1)]
        Db, _ = E.dbar(win)
        gm = E.GaussianMixture(2, covariance_type="full", reg_covar=1e-4, max_iter=100, n_init=2, random_state=20261009 + k).fit(win)
        mu = (gm.weights_[:, None] * gm.means_).sum(0)
        Sig = sum(w * (C + np.outer(m, m)) for w, C, m in zip(gm.weights_, gm.covariances_, gm.means_)) - np.outer(mu, mu)
        X, Y = win[:-1], win[1:]; A = np.column_stack([np.ones(len(X)), X])
        coef = np.linalg.lstsq(A, Y, rcond=None)[0]; e = Y - A @ coef; Q = np.cov(e.T); Phi = coef[1:].T
        out.append({"FD": Db / np.trace(Db), "FS": Sig / np.trace(Sig), "FQ": Q / np.trace(Q), "phi": np.diag(Phi).copy(), "s": s})
        if k % 60 == 0: print(f"  [{tag}] mapa {k}", flush=True)
    return out


def series(M):
    n = len(M); s = {k: np.full(n, np.nan) for k in ("dFD", "dFS", "dFQ", "gapS", "gapQ")}
    s["dphi"] = np.full((n, 3), np.nan); s["phi"] = np.array([m["phi"] for m in M])
    for k in range(n):
        s["gapS"][k] = np.linalg.norm(M[k]["FD"] - M[k]["FS"]); s["gapQ"][k] = np.linalg.norm(M[k]["FD"] - M[k]["FQ"])
        if k == 0: continue
        a, b = M[k - 1], M[k]
        for key, f in (("dFD", "FD"), ("dFS", "FS"), ("dFQ", "FQ")): s[key][k] = np.linalg.norm(b[f] - a[f])
        s["dphi"][k] = np.abs(b["phi"] - a["phi"])
    return s


def rk(v): return rankdata(v)


def pcor(x, y, z):
    """Spearman parcial: postos de x e y residualizados no posto de z."""
    A = np.column_stack([np.ones(len(z)), rk(z)]); res = lambda v: rk(v) - A @ np.linalg.lstsq(A, rk(v), rcond=None)[0]
    return float(np.corrcoef(res(x), res(y))[0, 1])


def sp(x, y): return float(spearmanr(x, y).correlation)


def estat(real, nulas, idx):
    """A = ρ(dFD,dFS) real, B = ρ(dFD,dFQ) real, C = média nula de ρ(dFD,dFQ), F = (B−A)/(C−A)."""
    r = {k: real[k][idx] for k in ("dFD", "dFS", "dFQ")}
    A = sp(r["dFD"], r["dFS"]); B = sp(r["dFD"], r["dFQ"])
    C = float(np.mean([sp(n["dFD"][idx], n["dFQ"][idx]) for n in nulas]))
    CS = float(np.mean([sp(n["dFD"][idx], n["dFS"][idx]) for n in nulas]))
    return {"A_real_dFDxdFS": A, "B_real_dFDxdFQ": B, "C_nula_dFDxdFQ": C, "nula_dFDxdFS": CS,
            "F_fracao_fechada": (B - A) / (C - A) if abs(C - A) > 1e-9 else np.nan,
            "parcial_dFDxdFS_dado_dFQ": pcor(r["dFD"], r["dFS"], r["dFQ"]), "parcial_dFDxdFQ_dado_dFS": pcor(r["dFD"], r["dFQ"], r["dFS"])}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    i0 = int(np.argmax((ts >= pd.Timestamp(ini, tz="UTC")).to_numpy()))
    i1 = int(np.argmax((ts >= pd.Timestamp(fim, tz="UTC")).to_numpy())) if ts.iloc[-1] >= pd.Timestamp(fim, tz="UTC") else len(kl)
    day = ts.dt.floor("D").to_numpy()
    lc = np.log(kl.close.values); lr = np.diff(lc, prepend=lc[0]); hi = np.log(kl.high.values) - lc; lo = lc - np.log(kl.low.values)
    lv = np.log(kl.volume.values); frac = kl.taker_buy.values / kl.volume.values

    def nula_df(seed):
        rng = np.random.default_rng(seed); perm = np.arange(len(kl))
        for dd in np.unique(day[i0:i1]):
            sel = np.where(day == dd)[0]; sel = sel[(sel >= i0) & (sel < i1)]; perm[sel] = rng.permutation(sel)
        c2 = np.exp(lc[0] + np.cumsum(lr[perm]))
        return pd.DataFrame({"timestamp": kl.timestamp.values, "open": c2, "high": c2 * np.exp(hi[perm]), "low": c2 * np.exp(-lo[perm]), "close": c2,
                             "volume": np.exp(lv[perm]), "taker_buy": frac[perm] * np.exp(lv[perm])})

    out = {"periodo": a.periodo, "inicio": ini, "fim": fim, "R_nula": R_NULA, "espacos": {}}
    rb = np.random.default_rng(20261017)
    for spc in ("flow", "orig"):
        raw = E.COORDS[spc](kl); ok = np.isfinite(raw).all(1); anchor = raw[may & ok]

        def gauss(rw):
            G = np.full_like(rw, np.nan); g = np.isfinite(rw).all(1); G[g] = E.gaussianize(anchor, rw[g]); return G
        Mr = mapas(gauss(raw), i0, i1, f"{spc} real"); real = series(Mr)
        nulas = [series(mapas(gauss(E.COORDS[spc](nula_df(2026 + r))), i0, i1, f"{spc} nula {r}")) for r in range(R_NULA)]
        days = np.array([str(ts.iloc[m["s"]].date()) for m in Mr])
        m = np.isfinite(real["dFD"]) & np.isfinite(real["dFS"]) & np.isfinite(real["dFQ"])
        for n in nulas: m &= np.isfinite(n["dFD"]) & np.isfinite(n["dFS"]) & np.isfinite(n["dFQ"])
        idx = np.where(m)[0]; est = estat(real, nulas, idx)
        ud = np.unique(days[idx]); grp = [idx[days[idx] == d] for d in ud]; bs = {k: [] for k in ("F_fracao_fechada", "B_real_dFDxdFQ", "parcial_dFDxdFS_dado_dFQ")}
        for _ in range(B_BOOT):
            ii = np.concatenate([grp[i] for i in rb.integers(0, len(grp), len(grp))]); e = estat(real, nulas, ii)
            for k in bs: bs[k].append(e[k])
        ic = {k: [float(np.nanpercentile(v, 5)), float(np.nanpercentile(v, 95))] for k, v in bs.items()}
        # Qual eixo: resíduo de posto(dFD) dado posto(dFS) contra |Δφ_jj| de cada eixo
        A1 = np.column_stack([np.ones(len(idx)), rk(real["dFS"][idx])]); res = rk(real["dFD"][idx]) - A1 @ np.linalg.lstsq(A1, rk(real["dFD"][idx]), rcond=None)[0]
        eixo = {EIXOS[spc][j]: sp(res, real["dphi"][idx, j]) for j in range(3)}
        eixo_n = {EIXOS[spc][j]: float(np.mean([sp(rk(n["dFD"][idx]) - np.column_stack([np.ones(len(idx)), rk(n["dFS"][idx])]) @ np.linalg.lstsq(np.column_stack([np.ones(len(idx)), rk(n["dFS"][idx])]), rk(n["dFD"][idx]), rcond=None)[0], n["dphi"][idx, j]) for n in nulas])) for j in range(3)}
        nivel = {"phi_mediano_real": dict(zip(EIXOS[spc], np.round(np.median(real["phi"], 0), 3).tolist())),
                 "phi_mediano_nula": dict(zip(EIXOS[spc], np.round(np.median(np.concatenate([n["phi"] for n in nulas]), 0), 3).tolist())),
                 "fracao_mapas_FQ_mais_perto_de_FD_real": float(np.mean(real["gapQ"] < real["gapS"])),
                 "gap_mediano_real": {"FD-FS": float(np.median(real["gapS"])), "FD-FQ": float(np.median(real["gapQ"]))},
                 "gap_mediano_nula": {"FD-FS": float(np.median(np.concatenate([n["gapS"] for n in nulas]))), "FD-FQ": float(np.median(np.concatenate([n["gapQ"] for n in nulas])))}}
        out["espacos"][spc] = {"n_mapas": int(len(idx)), "n_dias": int(len(ud)), **{k: round(v, 4) for k, v in est.items()},
                               "ic90": {k: [round(x, 4) for x in v] for k, v in ic.items()},
                               "eixo_residuo_x_dphi_real": {k: round(v, 3) for k, v in eixo.items()},
                               "eixo_residuo_x_dphi_nula": {k: round(v, 3) for k, v in eixo_n.items()}, "nivel": nivel,
                               "serie_real": {k: [None if not np.isfinite(v) else round(float(v), 6) for v in real[k]] for k in ("dFD", "dFS", "dFQ")},
                               "phi_real": np.round(real["phi"], 5).tolist(), "dias": days.tolist()}
        o = out["espacos"][spc]
        print(f"\n== {spc} [{a.periodo}] A ρ(dFD,dFS) real {o['A_real_dFDxdFS']:+.3f} | B ρ(dFD,dFQ) real {o['B_real_dFDxdFQ']:+.3f} | "
              f"C ρ(dFD,dFQ) nula {o['C_nula_dFDxdFQ']:+.3f} | nula ρ(dFD,dFS) {o['nula_dFDxdFS']:+.3f}", flush=True)
        print(f"   F = (B−A)/(C−A) = {o['F_fracao_fechada']:+.3f} IC90 {o['ic90']['F_fracao_fechada']} | parcial ρ(dFD,dFS | dFQ) {o['parcial_dFDxdFS_dado_dFQ']:+.3f} "
              f"| parcial ρ(dFD,dFQ | dFS) {o['parcial_dFDxdFQ_dado_dFS']:+.3f}", flush=True)
        print(f"   eixo (resíduo de dFD dado dFS × |Δφ|): real {o['eixo_residuo_x_dphi_real']} | nula {o['eixo_residuo_x_dphi_nula']}", flush=True)
        print(f"   φ mediano real {nivel['phi_mediano_real']} | nula {nivel['phi_mediano_nula']} | FQ mais perto de FD que FS em "
              f"{nivel['fracao_mapas_FQ_mais_perto_de_FD_real']:.0%} dos mapas", flush=True)
    (ROOT / "resultados").mkdir(exist_ok=True)
    if a.periodo != "fumaca": (ROOT / "resultados" / f"memoria_D_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
