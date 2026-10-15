"""Poder do H-FORMA-D-02 por simulação (não julga nada).

Usa só as séries da exploração (jun–jul e ago–set/2026, real e nula semente 2026, já gravadas em resultados/).
Em cada réplica: sorteia 31 dias (com reposição) dos 122 dias de jun–set, calcula Δ = ρ_real − ρ_nula e aplica o
mesmo teste do confirmatório (bootstrap pareado por dia, aqui B = 1.000). O encolhimento s desloca Δ e a sua
distribuição bootstrap em s·|Δ̂| na direção da nula. Conservador: o confirmatório usa a média de 20 réplicas da nula,
aqui há uma só.
"""
import json
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
CASOS = [("flow", "dFD", "dFS", -1, "primária"), ("flow", "angD", "angS", -1, "secundária"), ("orig", "dFD", "dFS", +1, "secundária")]
NDIAS, REPS, B = 31, 400, 1000


def sp(x, y):
    rx = rankdata(x); ry = rankdata(y); rx -= rx.mean(); ry -= ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx * rx).sum() * (ry * ry).sum()))


def main():
    rng = np.random.default_rng(20261015); out = {"n_dias": NDIAS, "replicas": REPS, "B": B, "casos": {}}
    for esp, a, b, sinal, papel in CASOS:
        grupos = []
        for per in ("junjul", "agoset"):
            e = json.load(open(ROOT / "resultados" / f"forma_D_casca_{per}.json"))["espacos"][esp]
            xr, yr = (np.array(e["real"]["serie"][k], float) for k in (a, b))
            xn, yn = (np.array(e["nula"]["serie"][k], float) for k in (a, b))
            dias = np.array(e["real"]["dias"]); m = np.isfinite(xr) & np.isfinite(yr) & np.isfinite(xn) & np.isfinite(yn)
            for d in np.unique(dias[m]):
                i = np.where(m & (dias == d))[0]; grupos.append((xr[i], yr[i], xn[i], yn[i]))
        cat = lambda gs, j: np.concatenate([g[j] for g in gs])
        d_hat = sp(cat(grupos, 0), cat(grupos, 1)) - sp(cat(grupos, 2), cat(grupos, 3))
        res = {"delta_exploracao_jun_set": round(d_hat, 4)}
        ENC = (0.0, 0.4, 0.65, 0.8); hits = dict.fromkeys(ENC, 0)
        for _ in range(REPS):
            gs = [grupos[i] for i in rng.integers(0, len(grupos), NDIAS)]
            bs = np.empty(B)
            for t in range(B):
                g2 = [gs[i] for i in rng.integers(0, NDIAS, NDIAS)]
                bs[t] = sp(cat(g2, 0), cat(g2, 1)) - sp(cat(g2, 2), cat(g2, 3))
            for s in ENC:  # desloca Δ na direção da nula
                p = (1 + int(np.sum(sinal * (bs - s * d_hat) <= 0))) / (B + 1); hits[s] += p < 0.05
        for s in ENC:
            res[f"encolhe_{int(s * 100)}"] = round(hits[s] / REPS, 3)
            print(esp, a, b, papel, s, res[f"encolhe_{int(s * 100)}"], flush=True)
        out["casos"][f"{esp} {a}×{b}@+0 ({papel})"] = res
    (ROOT / "referencia" / "H-FORMA-D-02_poder.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
