"""2ª rodada: surpresa no RETORNO do preço dado o estado 3D e a volatilidade. Previsão: PREDICAO_volatilidade_escondida_v2.md.

    python pipeline/explora_volatilidade_escondida_v2.py --periodo fumaca|junjul|agoset
    python pipeline/explora_volatilidade_escondida_v2.py --combinar
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
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402
import explora_volatilidade_escondida as V  # noqa: E402  (gerar, estimativas, SEEDS_*, CAUSAIS)

E = GR.E
K = 200


def memoria_r(G, r, sig, wk, rng):
    a, b = [], []
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        X = G[tr[:-1]]; y = r[tr[1:]] ** 2 / sig[tr[:-1]] ** 2
        ok = np.isfinite(X).all(1) & np.isfinite(y); X, y = X[ok], y[ok]
        Xe = G[te[:-1]]; re2 = r[te[1:]] ** 2; se = sig[te[:-1]]
        oke = np.isfinite(Xe).all(1) & np.isfinite(re2) & np.isfinite(se)
        m = np.full(len(Xe), np.nan)
        if oke.any():
            d, idx = cKDTree(X).query(Xe[oke], k=K)
            rk = np.maximum(d[:, -1], 1e-12); w = np.clip(1 - (d / rk[:, None]) ** 3, 0, None) ** 3
            m[oke] = (w * y[idx]).sum(1) / w.sum(1)
        eps = re2 / (se ** 2 * m)
        fin = np.isfinite(eps); cs = np.r_[0, np.cumsum(fin)]
        cand = np.arange(10, len(eps)); cand = cand[fin[cand] & ((cs[cand] - cs[cand - 10]) == 10)]
        pick = rng.choice(cand, min(5000, len(cand)), replace=False)
        a.append(eps[pick]); b.append(np.array([eps[i - 10:i].mean() for i in pick]))
    return float(spearmanr(np.concatenate(a), np.concatenate(b)).correlation)


def medir(kl, ts, may, wk, orc=None):
    G = GR.regua(E.coords_orig(kl), may); est = V.estimativas(kl, orc)
    r = np.diff(np.log(kl.close.values.astype(float)), prepend=np.nan)
    out = {"sem_vol": memoria_r(G, r, np.ones(len(G)), wk, np.random.default_rng(20261020))}
    for nome, sig in est.items():
        out[nome] = memoria_r(G, r, sig, wk, np.random.default_rng(20261020))
    return out


def combinar():
    R = {p: json.loads((ROOT / "resultados" / f"volatilidade_escondida_v2_{p}.json").read_text()) for p in ("junjul", "agoset")}
    red = lambda m, k: 1 - m[k] / m["sem_vol"]  # noqa: E731
    A = {p: {"red_oraculo_G": float(np.mean([red(r["series"][f"G_{s}"], "oraculo") for s in V.SEEDS_G])),
             **{f"red_{c}_G": float(np.mean([red(r["series"][f"G_{s}"], c) for s in V.SEEDS_G])) for c in V.CAUSAIS}} for p, r in R.items()}
    valida = all(A[p]["red_oraculo_G"] >= 0.7 for p in R)
    esc = max(V.CAUSAIS, key=lambda c: sum(A[p][f"red_{c}_G"] for p in R))
    res = {"etapa_A": A, "validacao_passa": valida, "estimativa_escolhida": esc}
    if not valida:
        res["veredito"] = "INCONCLUSIVO"
    else:
        cl = {}
        for p, r in R.items():
            mr = r["series"]["real"][esc]; mg = [r["series"][f"G_{s}"][esc] for s in V.SEEDS_G]
            cl[p] = {"M_real": mr, "M_G": mg, "classe": "fechado" if mr <= max(mg) else "sobra além da volatilidade"}
        res["etapa_B"] = cl; cls = {v["classe"] for v in cl.values()}
        res["veredito"] = ("FECHADO: a volatilidade é a dimensão escondida" if cls == {"fechado"} else
                           "SOBRA memória além da volatilidade" if cls == {"sobra além da volatilidade"} else "NÃO ESTÁVEL")
    print(json.dumps(res, ensure_ascii=False, indent=1))
    (ROOT / "resultados" / "volatilidade_escondida_v2_veredito.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS)); ap.add_argument("--combinar", action="store_true")
    ap.add_argument("--dados", default=str(ROOT / "dados")); a = ap.parse_args()
    if a.combinar:
        return combinar()
    meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    if a.periodo == "fumaca":
        may = (ts < pd.Timestamp("2026-05-03", tz="UTC")).to_numpy()
    i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    res = {"real": medir(kl, ts, may, wk)}; print("  real: ok", flush=True)
    for s in V.SEEDS_G:
        k_, o = V.gerar(kl, ts, i0, s, True); res[f"G_{s}"] = medir(k_, ts, may, wk, o); print(f"  G_{s}: ok", flush=True)
    for s in V.SEEDS_S:
        k_, o = V.gerar(kl, ts, i0, s, False); res[f"S_{s}"] = medir(k_, ts, may, wk, o); print(f"  S_{s}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    print(f"\n== volatilidade escondida v2 [{a.periodo}]  (M = memória da surpresa do retorno; menor = mais markoviano)")
    for nome, m in res.items():
        print(f"  {nome:7s} " + "  ".join(f"{k} {v:+.3f}" for k, v in m.items()), flush=True)
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"volatilidade_escondida_v2_{a.periodo}.json").write_text(json.dumps({"periodo": a.periodo, "series": res}, ensure_ascii=False))


if __name__ == "__main__":
    main()
