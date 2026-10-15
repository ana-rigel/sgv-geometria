"""Exploração: no espaço original, sobra geografia de agitação depois de descontar raridade E volume?

Continuação de explora_dimensao_campo.py (mesmo estimador, pontos, semanas, critérios). Previsão: PREDICAO_dimensao_original_nu.md.

    python pipeline/explora_dimensao_original_nu.py --periodo fumaca   # só confere que roda (maio); não imprime estatísticas
    python pipeline/explora_dimensao_original_nu.py --periodo junjul
    python pipeline/explora_dimensao_original_nu.py --periodo agoset

ν é o volume logarítmico relativo de 1.500 min do espaço de fluxo (flow_coordinates do M11-I, gaussianizado com a âncora
de maio). Como ν é do minuto e o mapa é de lugares, o "volume no lugar p" é ν̄_w(p) = Σ w_t(p) ν_t / Σ w_t(p), com o
mesmo núcleo h = 0,45 do campo, nos minutos da semana w. Resíduo: log tr D(p) menos um polinômio cúbico completo em
(ν̄_w(p), log ρ_w(p)). Para comparação, o mesmo resíduo só com log ρ (a medida da rodada anterior).

Nula: VAR(1) em 4 dimensões (E_norm, jerk, memory_flux, ν) por semana, com os resíduos padronizados pela volatilidade
local no tempo, embaralhados dentro da semana e reescalados na ordem original (5 réplicas, sementes 2026 … 2030). Assim
a nula carrega o ν, com a sua memória e a sua ligação linear com o espaço original.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_dimensao_campo as M  # noqa: E402
E = M.E


def campo_nu(Gw4, P):
    X = Gw4[:-1, :3]; S = Gw4[1:, :3] - Gw4[:-1, :3]; S2 = (S ** 2).sum(1); nu = Gw4[:-1, 3]
    out = {k: np.empty(len(P)) for k in ("ltr", "lrho", "neff", "nubar")}
    for a in range(0, len(P), 500):
        W = M.kernel_w(X, P[a:a + 500]); n = np.maximum(W.sum(1), 1e-12); mu = (W @ S) / n[:, None]
        out["ltr"][a:a + 500] = np.log(np.maximum((W @ S2) / n - (mu ** 2).sum(1), 1e-9))
        out["lrho"][a:a + 500] = np.log(n / len(X) + 1e-12); out["neff"][a:a + 500] = n ** 2 / np.maximum((W ** 2).sum(1), 1e-300)
        out["nubar"][a:a + 500] = (W @ nu) / n
    return out


def cubica(*vs):
    if len(vs) == 1:
        l = vs[0]; return np.column_stack([np.ones(len(l)), l, l * l, l ** 3])
    v, l = vs
    return np.column_stack([np.ones(len(v)), v, l, v * v, v * l, l * l, v ** 3, v * v * l, v * l * l, l ** 3])


def resid(y, A, ok):
    r = np.full(len(y), np.nan); c = np.linalg.lstsq(A[ok], y[ok], rcond=None)[0]; r[ok] = y[ok] - A[ok] @ c
    return r, float(1 - np.var(r[ok]) / np.var(y[ok]))


def analisar(P, Gws):
    R = {"rho": [], "nu": []}; R2 = {"rho": [], "nu": []}; oks = []
    for Gw in Gws:
        c = campo_nu(Gw, P); ok = np.isfinite(c["ltr"]) & (c["neff"] >= M.NEFF_MIN); oks.append(ok)
        for key, A in (("rho", cubica(c["lrho"])), ("nu", cubica(c["nubar"], c["lrho"]))):
            r, r2 = resid(c["ltr"], A, ok); R[key].append(r); R2[key].append(r2)
    pers = {k: [] for k in R}
    for w in range(len(Gws) - 1):
        m = oks[w] & oks[w + 1]
        for k in R: pers[k].append(float(spearmanr(R[k][w][m], R[k][w + 1][m]).correlation))
    return pers, R2, R


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(M.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = M.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); wk = M.semanas(ts, ini, fim)
    rawo = E.COORDS["orig"](kl); oko = np.isfinite(rawo).all(1)
    G = np.full_like(rawo, np.nan); G[oko] = E.gaussianize(rawo[may & oko], rawo[oko])
    rawf = E.COORDS["flow"](kl); okf = np.isfinite(rawf).all(1)
    F = np.full_like(rawf, np.nan); F[okf] = E.gaussianize(rawf[may & okf], rawf[okf]); nu = F[:, 2]
    P = G[may & oko][np.random.default_rng(20261018).choice(int((may & oko).sum()), M.NPTS, replace=False)]  # os mesmos pontos da rodada anterior
    G4 = np.column_stack([G, nu])
    Gws = [G4[idx][np.isfinite(G4[idx]).all(1)] for _, idx in wk]
    pr, r2r, Rr = analisar(P, Gws)
    pn, r2n = [], []
    for r in range(M.R_NULA):
        rng = np.random.default_rng(2026 + r); p_, r2_, _ = analisar(P, [M.nula_semana(Gw, rng) for Gw in Gws]); pn.append(p_); r2n.append(r2_)
    out = {"periodo": a.periodo, "semanas": [w[0] for w in wk], "R_nula": M.R_NULA, "orig": {}}
    for k, nome in (("nu", "log ρ e ν̄ (primária desta exploração)"), ("rho", "só log ρ (rodada anterior, para comparação)")):
        nm = np.mean([p[k] for p in pn], 0); d = np.array(pr[k]) - nm
        rm = np.nanmean(np.vstack(Rr[k]), 0); okm = np.isfinite(rm)
        onde = {f"|{n}|": round(float(spearmanr(rm[okm], np.abs(P[okm, j])).correlation), 3) for j, n in enumerate(M.EIXOS["orig"])}
        out["orig"][k] = {"controle": nome, "P_res_real": [round(x, 4) for x in pr[k]], "P_res_nula_media": [round(float(x), 4) for x in nm],
                          "Delta_medio": round(float(d.mean()), 4), "pares_real_acima": int((d > 0).sum()), "n_pares": int(len(d)),
                          "R2_real": [round(x, 4) for x in r2r[k]], "R2_nula_media": [round(float(x), 4) for x in np.mean([r[k] for r in r2n], 0)],
                          "onde_residuo_medio": onde}
        if a.periodo != "fumaca":
            o = out["orig"][k]
            print(f"\n== orig [{a.periodo}] controle: {nome}", flush=True)
            print(f"   persistência do resíduo: real {np.mean(pr[k]):+.3f} | nula {nm.mean():+.3f} | Δ médio {d.mean():+.3f} | real acima em {(d > 0).sum()}/{len(d)} pares", flush=True)
            print(f"   R²: real {np.mean(r2r[k]):.3f} | nula {np.mean(o['R2_nula_media']):.3f} | resíduo médio × {onde}", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"dimensao_original_nu_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
