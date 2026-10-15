"""Exploração: a sobra de geografia do original (depois de raridade e volume) tem ligação própria com |jerk|, ou é
artefato da medida (como |ι| no fluxo)?

Previsão registrada antes de calcular: PREDICAO_jerk_original.md. Usa exatamente o resíduo de
explora_dimensao_original_nu.py (cúbica em ν̄_w(p) e log ρ_w(p)), os mesmos pontos, semanas e nula VAR(1) 4D com
volatilidade agrupada (5 réplicas, sementes 2026 … 2030).

Por semana w: J_w = Spearman, entre pontos, do resíduo r_w(p) com |jerk(p)| (a coordenada do ponto). O mesmo na nula.
Δ_w = J_w(real) − média das réplicas.

    python pipeline/explora_jerk_original.py --periodo fumaca   # só confere que roda; não imprime estatísticas
    python pipeline/explora_jerk_original.py --periodo junjul
    python pipeline/explora_jerk_original.py --periodo agoset
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_dimensao_original_nu as N  # noqa: E402
M, E = N.M, N.E


def liga(R, alvo):
    out = []
    for r in R:
        k = np.isfinite(r); out.append(float(spearmanr(r[k], alvo[k]).correlation))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(M.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = M.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); wk = M.semanas(ts, ini, fim)
    rawo = E.COORDS["orig"](kl); oko = np.isfinite(rawo).all(1)
    G = np.full_like(rawo, np.nan); G[oko] = E.gaussianize(rawo[may & oko], rawo[oko])
    rawf = E.COORDS["flow"](kl); okf = np.isfinite(rawf).all(1)
    F = np.full_like(rawf, np.nan); F[okf] = E.gaussianize(rawf[may & okf], rawf[okf])
    P = G[may & oko][np.random.default_rng(20261018).choice(int((may & oko).sum()), M.NPTS, replace=False)]
    G4 = np.column_stack([G, F[:, 2]]); Gws = [G4[idx][np.isfinite(G4[idx]).all(1)] for _, idx in wk]
    alvos = {"|jerk|": np.abs(P[:, 1]), "jerk": P[:, 1]}
    _, _, Rr = N.analisar(P, Gws)
    real = {k: liga(Rr["nu"], v) for k, v in alvos.items()}
    nul = {k: [] for k in alvos}
    for r in range(M.R_NULA):
        rng = np.random.default_rng(2026 + r); _, _, Rn = N.analisar(P, [M.nula_semana(Gw, rng) for Gw in Gws])
        for k, v in alvos.items(): nul[k].append(liga(Rn["nu"], v))
    out = {"periodo": a.periodo, "semanas": [w[0] for w in wk], "ligacoes": {}}
    for k in alvos:
        nm = np.mean(nul[k], 0); d = real[k] - nm
        out["ligacoes"][k] = {"J_real": np.round(real[k], 4).tolist(), "J_nula_media": np.round(nm, 4).tolist(),
                              "J_nula_replicas": [np.round(x, 4).tolist() for x in nul[k]], "Delta_medio": round(float(d.mean()), 4),
                              "semanas_real_acima": int((d > 0).sum()), "n_semanas": int(len(d))}
        if a.periodo != "fumaca":
            print(f"== orig [{a.periodo}] resíduo (raridade + volume) × {k}: real {real[k].mean():+.3f} | nula {nm.mean():+.3f} "
                  f"[réplicas {np.min(np.mean(nul[k], 1)):+.3f} a {np.max(np.mean(nul[k], 1)):+.3f}] | Δ médio {d.mean():+.3f} | real acima em {(d > 0).sum()}/{len(d)} semanas", flush=True)
            print(f"   por semana, real: {np.round(real[k], 2).tolist()}", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    (ROOT / "resultados" / f"jerk_original_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
