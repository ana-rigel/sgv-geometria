"""Poder do H-SGV-01 (rascunho v2) por simulação; não julga nada.

Pares de resíduos de jun–jul (controles "fluxo"), as duas primárias. Em cada réplica: sorteia 28 dias com reposição
(4 semanas, como outubro), atenua o sinal por f = 1 − encolhimento (x = f·x + √(1−f²)·ruído), e calcula o p unilateral da
permutação do par dentro do dia. Para caber no tempo, o p usa a aproximação normal da distribuição de permutação
(média e variância exatas da soma Σ a_i b_π(i) com π dentro de cada dia). 2.000 réplicas por cenário.
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
_ARGV = list(sys.argv); sys.argv = [sys.argv[0], "--periodo", "exploracao"]
sys.path.insert(0, str(ROOT / "pipeline"))
import confirmatorio_sgv as CS  # noqa: E402
F, XS = CS.F, CS.XS

REPS = 2000
NDIAS = int(_ARGV[_ARGV.index("--dias") + 1]) if "--dias" in _ARGV else 28


def p_aprox(x, y, lab, sinal):
    rx = stats.rankdata(x); ry = stats.rankdata(y); T = (rx * ry).sum(); E = 0.0; V = 0.0
    for g in np.unique(lab):
        i = lab == g; a, b = rx[i], ry[i]; n = len(a)
        if n < 2: continue
        E += n * a.mean() * b.mean(); V += ((a - a.mean()) ** 2).sum() * ((b - b.mean()) ** 2).sum() / (n - 1)
    z = (T - E) / np.sqrt(V)
    return float(stats.norm.cdf(z)) if sinal < 0 else float(stats.norm.sf(z))


def main():
    P = F.PERIODOS["exploracao"]; kl = F.carregar(P["meses"]); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy(); wk = F.semanas(ts, P["treino0"], P["inicio"], P["fim"])
    hour_d = pd.get_dummies(pd.Series(np.asarray(ts.dt.hour)), drop_first=True).astype(float).to_numpy()
    G = {}
    for sp in ("orig", "flow"):
        raw = F.COORDS[sp](kl); ok = np.isfinite(raw).all(1); G[sp] = np.full_like(raw, np.nan); G[sp][ok] = F.gaussianize(raw[may & ok], raw[ok])
    res = CS.analisar(XS.variaveis_sgv(kl), G["orig"], G["flow"], kl, ts, wk, hour_d, "real")
    rng = np.random.default_rng(7); out = {"replicas": REPS, "dias": NDIAS, "metodo": "aproximação normal da permutação dentro do dia", "hipoteses": {}}
    for nome, var, _, sg in CS.PRIMARIAS:
        xr, yr, d = res[nome]["pares"]; dias = np.unique(d); grp = {k: np.where(d == k)[0] for k in dias}
        zx = (xr - xr.mean()) / xr.std(); rho0 = float(stats.spearmanr(xr, yr)[0]); r = {"rho_agrupado_junjul": round(rho0, 4)}
        for s in (0.0, 0.35, 0.4, 0.65):
            f = 1 - s; h05 = h025 = 0
            for _ in range(REPS):
                pick = rng.choice(dias, NDIAS, replace=True); idx = np.concatenate([grp[k] for k in pick])
                lab = np.concatenate([[i] * len(grp[k]) for i, k in enumerate(pick)])
                x = f * zx[idx] + np.sqrt(1 - f * f) * rng.standard_normal(len(idx))
                p = p_aprox(x, yr[idx], lab, sg); h05 += p <= 0.05; h025 += p <= 0.025
            r[f"encolhe_{int(s * 100)}"] = {"poder_p<=0,025": round(h025 / REPS, 3), "poder_p<=0,05": round(h05 / REPS, 3)}
            print(nome, var, s, r[f"encolhe_{int(s * 100)}"], flush=True)
        out["hipoteses"][nome] = r
    (ROOT / "referencia").mkdir(exist_ok=True)
    (ROOT / "referencia" / ("H-SGV-01_poder.json" if NDIAS == 28 else f"H-SGV-01_poder_{NDIAS}dias.json")).write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
