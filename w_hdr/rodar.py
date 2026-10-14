"""W-HDR — M11-I contra Wasserstein. Desenho em PREREGISTRO_W-HDR.md.

    OPENBLAS_NUM_THREADS=1 python w_hdr/rodar.py --parte A     # dose-resposta (cascas M11-I novas)
    OPENBLAS_NUM_THREADS=1 python w_hdr/rodar.py --parte B     # painel W nas 630 comparações do U2
    python w_hdr/rodar.py --parte analise
"""
import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.linalg import sqrtm
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
from sklearn.mixture import GaussianMixture

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "u2_rotulador"))
import gerar as G  # noqa: E402

KS = (0.25, 0.50, 0.75, 1.00); MECS = ("translacao", "escala", "rotacao", "bimodal", "curvatura", "caudas")
FAM_A = ("gauss", "t6"); REPS_A = 15; NULOS = 4; SEED_A = 20261014


# ------------------------------------------------------------------ medidas W
def w2_exato(X, Y):
    C = cdist(X, Y, "sqeuclidean"); r, c = linear_sum_assignment(C); return float(C[r, c].mean())


def hdr50(X, seed):
    g = GaussianMixture(n_components=2, covariance_type="full", reg_covar=1e-4, max_iter=100, n_init=2, random_state=seed).fit(G.lex(X))
    d = g.score_samples(X); return X[d >= np.median(d)][: len(X) // 2]


def medidas_w(A, B, seed):
    mA = A.mean(0); Li = np.linalg.inv(np.linalg.cholesky(np.cov(A, rowvar=False))).T
    Aw, Bw = (A - mA) @ Li, (B - mA) @ Li
    w2 = w2_exato(Aw, Bw)
    dmu = float(np.sum((Bw.mean(0) - Aw.mean(0)) ** 2))
    SA, SB = np.cov(Aw, rowvar=False), np.cov(Bw, rowvar=False); rA = np.real(sqrtm(SA))
    bures = float(np.trace(SA + SB - 2 * np.real(sqrtm(rA @ SB @ rA))))
    ha, hb = hdr50(A, seed), hdr50(B, seed); n = min(len(ha), len(hb))
    w2h = w2_exato((ha[:n] - mA) @ Li, (hb[:n] - mA) @ Li)
    return {"w_w2": w2, "w_media": dmu, "w_bures": bures, "w_forma": w2 - dmu - bures, "w_w2hdr": w2h}


# ------------------------------------------------------------------ parte A
def mecanismo(cls, k, z0, B0, CA, rng, obs):
    N = len(z0)
    if cls == "translacao":
        u = G.unit(rng); return B0 + k * rng.uniform(0.25, 0.5) * np.sqrt(u @ CA @ u) * u
    if cls == "escala":
        s = rng.uniform(1.15, 1.30); s = s if rng.random() < 0.5 else 1 / s; s = 1 + (s - 1) * k
        return B0.mean(0) + s * (B0 - B0.mean(0))
    if cls == "rotacao":
        ang = np.radians(k * rng.uniform(20, 40)); return B0.mean(0) + (B0 - B0.mean(0)) @ G.rodrigues(G.unit(rng), ang).T
    z = z0.copy()
    if cls == "bimodal":
        v = G.unit(rng); a = k * rng.uniform(0.75, 0.90); pj = z @ v
        z = z + np.outer(a * rng.choice([-1.0, 1.0], size=N) + np.sqrt(1 - a * a) * rng.standard_normal(N) - pj, v)
    elif cls == "curvatura":
        q = G.rot_aleatoria(rng); z = z + np.outer(k * rng.uniform(0.5, 0.8) * ((z @ q[:, 0]) ** 2 - 1) / np.sqrt(2), q[:, 1])
    elif cls == "caudas":
        z = z * np.where(rng.random((N, 1)) < 0.10, 1 + 1.5 * k, 1.0)
    return G.casar_momentos(B0, obs(z))


def replica_A(args):
    fam, rep = args
    cache = ROOT / "resultados" / "parciais" / f"A_{fam}_{rep:02d}.csv"
    if cache.exists():
        return pd.read_csv(cache).to_dict("records")
    rng = np.random.default_rng([SEED_A, FAM_A.index(fam), rep])
    L = G.rot_aleatoria(rng) @ np.diag(np.sqrt(rng.uniform(0.5, 2.0, 3))); m = rng.normal(0, 0.5, 3)
    obs = lambda z: z @ L.T + m  # noqa: E731
    A = obs(G.latente(fam, rng, G.N)); CA = np.cov(A, rowvar=False)
    p = A[rng.choice(G.N, 300, replace=False)]; d = cdist(p, p); bw2 = float(np.median(d[np.triu_indices(300, 1)]) ** 2)
    seed = SEED_A + rep
    try:
        sA = G.build_shell(G.lex(A), seed=seed, n=G.GRID)
    except Exception:  # noqa: BLE001
        sA = None
    casos = [("nulo", 0.0)] * NULOS + [(c, k) for c in MECS for k in KS]
    linhas = []
    for cls, k in casos:
        z0 = G.latente(fam, rng, G.N); B0 = obs(z0)
        B = B0 if cls == "nulo" else mecanismo(cls, k, z0, B0, CA, rng, obs)
        row = {"familia": fam, "rep": rep, "classe": cls, "k": k}
        try:
            if sA is None:
                raise ValueError("casca_A")
            sg = G.signature(sA, G.build_shell(G.lex(B), seed=seed, n=G.GRID), seed=seed)
            row["m11_dist"] = sg.get("distance_512"); row["m11_absdD"] = abs(sg["delta_D"]) if sg.get("delta_D") is not None else None
            row["m11_valida"] = bool(sg.get("valid"))
        except Exception:  # noqa: BLE001
            row["m11_valida"] = False
        row.update(medidas_w(A, B, seed))
        k_ = lambda X, Y: np.exp(-cdist(X, Y, "sqeuclidean") / (2 * bw2)).mean()  # noqa: E731
        row["mmd2"] = float(k_(A, A) + k_(B, B) - 2 * k_(A, B))
        linhas.append(row)
    cache.parent.mkdir(parents=True, exist_ok=True); pd.DataFrame(linhas).to_csv(cache, index=False)
    print(f"A {fam} {rep} pronta", flush=True)
    return linhas


# ------------------------------------------------------------------ parte B (regenera o U2 sem cascas)
_REP = {}


def replica_B(args):
    fam, rep = args
    G.build_shell = lambda *a, **k: None                          # o gerador do U2 não consome o RNG nas cascas
    G.signature = lambda *a, **k: {}
    G.ROOT = ROOT / "resultados" / "u2_regen"
    orig = getattr(G, "_painel_original", None) or G.painel_convencional
    G._painel_original = orig                                     # embrulha uma vez só por processo
    def painel(A, B, bw2):
        out = orig(A, B, bw2); out.update(medidas_w(A, B, G.SEED + rep)); return out
    G.painel_convencional = painel
    linhas = G.replica((fam, rep))
    print(f"B {fam} {rep} pronta", flush=True)
    return [{k: v for k, v in l.items() if k in ("familia", "rep", "classe") or k.startswith(("c_", "w_"))} for l in linhas]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--parte", required=True, choices=["A", "B"]); ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args(); (ROOT / "resultados").mkdir(exist_ok=True)
    if a.parte == "A":
        tarefas = [(f, r) for r in range(REPS_A) for f in FAM_A]
        with Pool(a.procs) as pool:
            res = pool.map(replica_A, tarefas, chunksize=1)
        pd.DataFrame([l for b in res for l in b]).to_csv(ROOT / "resultados" / "parteA.csv", index=False)
    else:
        tarefas = [(f, r) for r in range(30) for f in G.FAMILIAS]
        with Pool(a.procs) as pool:
            res = pool.map(replica_B, tarefas, chunksize=1)
        novo = pd.DataFrame([l for b in res for l in b])
        u2 = pd.read_csv(ROOT.parent / "u2_rotulador" / "resultados" / "variaveis.csv")
        chave = ["familia", "rep", "classe"]; mg = u2.merge(novo, on=chave, suffixes=("", "_regen"))
        cc = [c for c in u2.columns if c.startswith("c_")]
        dif = max(float(np.nanmax(np.abs(mg[c] - mg[c + "_regen"]))) for c in cc)
        print(f"conferência: {len(mg)} de {len(u2)} comparações casadas; diferença máxima nas variáveis convencionais = {dif:.2e}")
        assert len(mg) == len(u2) and dif < 1e-9, "a regeneração não reproduz o U2"
        novo[chave + [c for c in novo.columns if c.startswith("w_")]].to_csv(ROOT / "resultados" / "parteB_w.csv", index=False)


if __name__ == "__main__":
    main()
