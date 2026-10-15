"""Exploração: quantas dimensões o campo de agitação tem de fato?

A variação de tr D(x) de lugar para lugar é só volume (ν) e raridade (log ρ)? Ou sobra uma geografia em 3D que se
repete de uma semana para a outra mais do que numa nula que preserva a memória linear e o agrupamento de volatilidade?

Previsão registrada antes de qualquer cálculo: PREDICAO_dimensao_campo.md.

    python pipeline/explora_dimensao_campo.py --periodo fumaca   # só confere que roda (maio, a âncora); não imprime estatísticas
    python pipeline/explora_dimensao_campo.py --periodo junjul
    python pipeline/explora_dimensao_campo.py --periodo agoset

Campo: o estimador do H-DIF-01 (núcleo gaussiano h = 0,45 sobre os pares (x_t, x_{t+1} − x_t) de uma semana;
log tr D = log(E_w‖s‖² − ‖E_w s‖²); log ρ = log(massa/n)), avaliado em 1.500 pontos fixos sorteados dos estados de
maio (a âncora). Semanas de 7 dias a partir do início do período (a última entra se tiver ≥ 5 dias).

Em cada semana: log tr D(p) é regredido (MQO) num polinômio cúbico completo em (ν(p), log ρ_w(p)) no fluxo, e em
log ρ_w(p) no original, nos pontos com massa efetiva ≥ 30. O resíduo é a "geografia que sobra".
Persistência: Spearman, entre pontos, do resíduo da semana w com o da semana w+1 (dados disjuntos).

Nula (5 réplicas, sementes 2026 … 2030), por semana: VAR(1) ajustado nos dados reais da semana; resíduos
padronizados pela sua volatilidade local no tempo (RMS centrado de 61 min, por eixo); os resíduos padronizados são
embaralhados dentro da semana e reescalados pela volatilidade na ordem original; a série é reconstruída a partir do
primeiro estado real da semana. Preserva memória linear e agrupamento de volatilidade no tempo; destrói a ligação entre o
tamanho do passo e o lugar onde ele acontece (exceto a ligação radial: surtos geram excursões maiores).
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_forma_D_casca as E  # noqa: E402  (carregar, COORDS, gaussianize)

H, NPTS, NEFF_MIN, R_NULA = 0.45, 1500, 30.0, 5
PERIODOS = {"fumaca": (["2026-05"], "2026-05-03", "2026-05-24"),
            "junjul": (["2026-05", "2026-06", "2026-07"], "2026-06-01", "2026-08-01"),
            "agoset": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"], "2026-08-01", "2026-10-01")}
EIXOS = {"flow": ["z", "iota", "nu"], "orig": ["E_norm", "jerk", "memory_flux"]}


def kernel_w(X, P):
    d2 = (P ** 2).sum(1)[:, None] + (X ** 2).sum(1)[None, :] - 2 * P @ X.T
    return np.exp(-0.5 * np.maximum(d2, 0) / H ** 2)


def campo(Gw, P):
    """Gw: estados consecutivos finitos de uma semana. Devolve log tr D, log ρ e massa efetiva em P."""
    X = Gw[:-1]; S = Gw[1:] - Gw[:-1]; S2 = (S ** 2).sum(1)
    ltr = np.empty(len(P)); lrho = np.empty(len(P)); neff = np.empty(len(P))
    for a in range(0, len(P), 500):
        W = kernel_w(X, P[a:a + 500]); n = np.maximum(W.sum(1), 1e-12); mu = (W @ S) / n[:, None]
        ltr[a:a + 500] = np.log(np.maximum((W @ S2) / n - (mu ** 2).sum(1), 1e-9))
        lrho[a:a + 500] = np.log(n / len(X) + 1e-12); neff[a:a + 500] = n ** 2 / np.maximum((W ** 2).sum(1), 1e-300)
    return ltr, lrho, neff


def base(spc, P, lrho):
    if spc == "flow":
        v, l = P[:, 2], lrho
        return np.column_stack([np.ones(len(v)), v, l, v * v, v * l, l * l, v ** 3, v * v * l, v * l * l, l ** 3])
    l = lrho
    return np.column_stack([np.ones(len(l)), l, l * l, l ** 3])


def residuo(spc, P, ltr, lrho, ok):
    A = base(spc, P, lrho); r = np.full(len(P), np.nan)
    coef = np.linalg.lstsq(A[ok], ltr[ok], rcond=None)[0]; r[ok] = ltr[ok] - A[ok] @ coef
    r2 = 1 - np.var(r[ok]) / np.var(ltr[ok])
    return r, float(r2)


def nula_semana(Gw, rng):
    X, Y = Gw[:-1], Gw[1:]; A = np.column_stack([np.ones(len(X)), X])
    coef = np.linalg.lstsq(A, Y, rcond=None)[0]; e = Y - A @ coef
    sig = np.sqrt(pd.DataFrame(e ** 2).rolling(61, center=True, min_periods=10).mean().to_numpy()); sig = np.maximum(sig, 1e-6)
    es = sig * (e / sig)[rng.permutation(len(e))]
    xs = np.empty_like(Gw); xs[0] = Gw[0]; c, B = coef[0], coef[1:]
    for t in range(len(e)): xs[t + 1] = c + xs[t] @ B + es[t]
    return xs


def semanas(ts, ini, fim):
    out = []; s = pd.Timestamp(ini, tz="UTC"); f = pd.Timestamp(fim, tz="UTC")
    while s < f:
        e = min(s + pd.Timedelta(days=7), f)
        if e - s < pd.Timedelta(days=5): break
        out.append((str(s.date()), np.where((ts >= s).to_numpy() & (ts < e).to_numpy())[0])); s = e
    return out


def analisar(spc, P, Gws, tag):
    """Gws: lista de semanas (estados finitos consecutivos). Devolve resíduos, R² e persistências."""
    res, r2s, raws, oks = [], [], [], []
    for Gw in Gws:
        ltr, lrho, neff = campo(Gw, P); ok = np.isfinite(ltr) & (neff >= NEFF_MIN)
        r, r2 = residuo(spc, P, ltr, lrho, ok); res.append(r); r2s.append(r2); raws.append(np.where(ok, ltr, np.nan)); oks.append(ok)
    pres, praw, npts = [], [], []
    for w in range(len(Gws) - 1):
        m = oks[w] & oks[w + 1]; npts.append(int(m.sum()))
        pres.append(float(spearmanr(res[w][m], res[w + 1][m]).correlation)); praw.append(float(spearmanr(raws[w][m], raws[w + 1][m]).correlation))
    print(f"  [{tag}] {len(Gws)} semanas", flush=True)
    return {"P_res": pres, "P_raw": praw, "R2": r2s, "n_pontos": npts, "residuos": res}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); wk = semanas(ts, ini, fim)
    out = {"periodo": a.periodo, "inicio": ini, "fim": fim, "semanas": [w[0] for w in wk], "R_nula": R_NULA, "espacos": {}}
    for spc in ("flow", "orig"):
        raw = E.COORDS[spc](kl); ok = np.isfinite(raw).all(1); anchor = raw[may & ok]
        G = np.full_like(raw, np.nan); G[ok] = E.gaussianize(anchor, raw[ok])
        P = G[may & ok][np.random.default_rng(20261018).choice(int((may & ok).sum()), NPTS, replace=False)]
        Gws = [G[idx][np.isfinite(G[idx]).all(1)] for _, idx in wk]
        real = analisar(spc, P, Gws, f"{spc} real")
        nulas = []
        for r in range(R_NULA):
            rng = np.random.default_rng(2026 + r); nulas.append(analisar(spc, P, [nula_semana(Gw, rng) for Gw in Gws], f"{spc} nula {r}"))
        nm = np.mean([n["P_res"] for n in nulas], 0); d = np.array(real["P_res"]) - nm
        # Onde está a geografia que sobra: resíduo médio do real × coordenadas do ponto
        rm = np.nanmean(np.vstack(real["residuos"]), 0); okm = np.isfinite(rm)
        onde = {}
        for j, nome in enumerate(EIXOS[spc]):
            onde[nome] = round(float(spearmanr(rm[okm], P[okm, j]).correlation), 3); onde[f"|{nome}|"] = round(float(spearmanr(rm[okm], np.abs(P[okm, j])).correlation), 3)
        o = {"P_res_real": [round(x, 4) for x in real["P_res"]], "P_res_nula_media": [round(float(x), 4) for x in nm],
             "P_res_nula_replicas": [[round(x, 4) for x in n["P_res"]] for n in nulas],
             "P_raw_real": [round(x, 4) for x in real["P_raw"]], "P_raw_nula_media": [round(float(x), 4) for x in np.mean([n["P_raw"] for n in nulas], 0)],
             "R2_real": [round(x, 4) for x in real["R2"]], "R2_nula_media": [round(float(x), 4) for x in np.mean([n["R2"] for n in nulas], 0)],
             "n_pontos": real["n_pontos"], "Delta_medio": round(float(d.mean()), 4), "pares_real_acima": int((d > 0).sum()), "n_pares": int(len(d)),
             "onde_residuo_medio_x_coordenada": onde}
        out["espacos"][spc] = o
        if a.periodo != "fumaca":
            print(f"\n== {spc} [{a.periodo}] {len(wk)} semanas, {len(d)} pares consecutivos", flush=True)
            print(f"   persistência do resíduo: real {np.mean(real['P_res']):+.3f} | nula {nm.mean():+.3f} | Δ médio {d.mean():+.3f} | real acima em {(d > 0).sum()}/{len(d)} pares", flush=True)
            print(f"   persistência de log tr D bruto: real {np.mean(real['P_raw']):+.3f} | nula {np.mean(o['P_raw_nula_media']):+.3f}", flush=True)
            print(f"   R² de {'ν e log ρ' if spc == 'flow' else 'log ρ'}: real {np.mean(real['R2']):.3f} | nula {np.mean(o['R2_nula_media']):.3f}", flush=True)
            print(f"   resíduo médio × coordenada: {onde}", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"dimensao_campo_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
