"""SGV-U2 — gera as 630 comparações (3 famílias × 30 réplicas × 7 mecanismos) e as variáveis dos dois painéis.

    OPENBLAS_NUM_THREADS=1 python u2_rotulador/gerar.py [--reps 30] [--procs 2]

Desenho congelado em PREREGISTRO_U2.md (commit f1dcdb3). Saída: u2_rotulador/resultados/variaveis.csv
"""
import argparse
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from sgv_m11i.instrument import build_shell, signature  # noqa: E402

N, GRID, SEED = 750, 25, 20261013
FAMILIAS = ("gauss", "t6", "assimetrica")
CLASSES = ("nenhum", "translacao", "escala", "rotacao", "bimodal", "curvatura", "caudas")


# ------------------------------------------------------------------ geradores
def latente(fam, rng, n):
    z = rng.standard_normal((n, 3))
    if fam == "t6":
        return z / np.sqrt(rng.chisquare(6, size=(n, 1)) / 6) / np.sqrt(1.5)
    if fam == "assimetrica":
        x = np.exp(0.5 * z); mu = np.exp(0.125); sd = np.sqrt((np.exp(0.25) - 1) * np.exp(0.25))
        return (x - mu) / sd
    return z


def unit(rng, k=3):
    v = rng.standard_normal(k); return v / np.linalg.norm(v)


def rot_aleatoria(rng):
    q, r = np.linalg.qr(rng.standard_normal((3, 3))); return q * np.sign(np.diag(r))


def rodrigues(eixo, ang):
    k = np.array([[0, -eixo[2], eixo[1]], [eixo[2], 0, -eixo[0]], [-eixo[1], eixo[0], 0]])
    return np.eye(3) + np.sin(ang) * k + (1 - np.cos(ang)) * k @ k


def casar_momentos(alvo, B):
    """B transformado linearmente para ter a média e a covariância amostrais de `alvo`."""
    Lb = np.linalg.cholesky(np.cov(B, rowvar=False)); La = np.linalg.cholesky(np.cov(alvo, rowvar=False))
    v = (B - B.mean(0)) @ np.linalg.inv(Lb.T) @ La.T + alvo.mean(0)
    assert np.allclose(np.cov(v, rowvar=False), np.cov(alvo, rowvar=False), atol=1e-9)
    return v


def lex(A):
    return A[np.lexsort((A[:, 2], A[:, 1], A[:, 0]))].copy()


# ------------------------------------------------------------------ painel convencional
def branquear_sim(X):
    C = np.cov(X, rowvar=False); w, V = np.linalg.eigh(C)
    return (X - X.mean(0)) @ V @ np.diag(w ** -0.5) @ V.T


def tensores(Z):
    m3 = np.einsum("ni,nj,nk->ijk", Z, Z, Z) / len(Z)
    m4 = np.einsum("ni,nj,nk,nl->ijkl", Z, Z, Z, Z) / len(Z)
    return m3, m4


def painel_convencional(A, B, bw2):
    mA = A.mean(0); CA = np.cov(A, rowvar=False); Lc = np.linalg.cholesky(CA); Wi = np.linalg.inv(Lc).T
    Aw = (A - mA) @ Wi; Bw = (B - mA) @ Wi
    out = {"c_dmedia": float(np.linalg.norm(Bw.mean(0)))}
    ge = np.sort(np.log(np.linalg.eigvalsh(np.cov(Bw, rowvar=False))))
    out.update({f"c_logeig{i}": float(ge[i]) for i in range(3)})
    va = np.linalg.eigh(CA)[1][:, -1]; vb = np.linalg.eigh(np.cov(B, rowvar=False))[1][:, -1]
    out["c_ang_principal"] = float(np.degrees(np.arccos(min(1.0, abs(va @ vb)))))
    ka = ((Aw / Aw.std(0)) ** 4).mean(0); Bs = (Bw - Bw.mean(0)) / Bw.std(0); kb = (Bs ** 4).mean(0)
    dk = np.sort(kb - ka); out.update({f"c_dcurt{i}": float(dk[i]) for i in range(3)})
    a3, a4 = tensores(branquear_sim(A)); b3, b4 = tensores(branquear_sim(B))
    out["c_dcoassim"] = float(np.linalg.norm(b3 - a3)); out["c_dcocurt"] = float(np.linalg.norm(b4 - a4))
    k = lambda X, Y: np.exp(-cdist(X, Y, "sqeuclidean") / (2 * bw2)).mean()  # noqa: E731
    out["c_mmd2"] = float(k(A, A) + k(B, B) - 2 * k(A, B))
    return out


# ------------------------------------------------------------------ uma réplica
def replica(args):
    fam, rep = args
    parcial = ROOT / "resultados" / "parciais" / f"{fam}_{rep:02d}.csv"
    if parcial.exists():
        return pd.read_csv(parcial).to_dict("records")
    rng = np.random.default_rng([SEED, FAMILIAS.index(fam), rep])
    L = rot_aleatoria(rng) @ np.diag(np.sqrt(rng.uniform(0.5, 2.0, 3))); m = rng.normal(0, 0.5, 3)
    obs = lambda z: z @ L.T + m  # noqa: E731
    A = obs(latente(fam, rng, N)); CA = np.cov(A, rowvar=False)
    p = A[rng.choice(N, 300, replace=False)]; d = cdist(p, p); bw2 = float(np.median(d[np.triu_indices(300, 1)]) ** 2)
    try:
        sA = build_shell(lex(A), seed=SEED + rep, n=GRID); erro_A = None
    except Exception as exc:  # noqa: BLE001  (casca de A inválida: as 7 comparações ficam inválidas no M11-I)
        sA = None; erro_A = "casca_A:" + str(exc)[:150]
    linhas = []
    for cls in CLASSES:
        z0 = latente(fam, rng, N); B0 = obs(z0); par = {}
        if cls == "nenhum":
            B = B0
        elif cls == "translacao":
            u = unit(rng); delta = rng.uniform(0.25, 0.5); B = B0 + delta * np.sqrt(u @ CA @ u) * u; par["delta"] = delta
        elif cls == "escala":
            s = rng.uniform(1.15, 1.30); s = s if rng.random() < 0.5 else 1 / s
            B = B0.mean(0) + s * (B0 - B0.mean(0)); par["s"] = s
        elif cls == "rotacao":
            ang = np.radians(rng.uniform(20, 40)); B = B0.mean(0) + (B0 - B0.mean(0)) @ rodrigues(unit(rng), ang).T; par["ang"] = np.degrees(ang)
        else:
            z = z0.copy()
            if cls == "bimodal":
                v = unit(rng); a = rng.uniform(0.75, 0.90); pj = z @ v
                novo = a * rng.choice([-1.0, 1.0], size=N) + np.sqrt(1 - a * a) * rng.standard_normal(N)
                z = z + np.outer(novo - pj, v); par["a"] = a
            elif cls == "curvatura":
                q = rot_aleatoria(rng); v1, v2 = q[:, 0], q[:, 1]; c = rng.uniform(0.5, 0.8)
                z = z + np.outer(c * ((z @ v1) ** 2 - 1) / np.sqrt(2), v2); par["c"] = c
            elif cls == "caudas":
                z = z * np.where(rng.random((N, 1)) < 0.10, 2.5, 1.0)
            B = casar_momentos(B0, obs(z))
        t0 = time.time(); row = {"familia": fam, "rep": rep, "classe": cls, **{f"par_{k}": v for k, v in par.items()}}
        try:
            if sA is None:
                raise ValueError(erro_A)
            sg = signature(sA, build_shell(lex(B), seed=SEED + rep, n=GRID), seed=SEED + rep)
            for k in ("translation_norm", "delta_log_volume", "theta_deg", "distance_512", "delta_D", "valid", "signature_complete"):
                row["m_" + k] = sg.get(k)
            row["m_erros"] = ";".join(map(str, sg.get("errors", [])))[:200]
        except Exception as exc:  # noqa: BLE001
            row["m_valid"] = False; row["m_erros"] = str(exc)[:200]
        row["t_m11"] = round(time.time() - t0, 2)
        row.update(painel_convencional(A, B, bw2))
        linhas.append(row)
    cache = ROOT / "resultados" / "parciais"; cache.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(linhas).to_csv(cache / f"{fam}_{rep:02d}.csv", index=False)
    print(f"{fam} réplica {rep} pronta", flush=True)
    return linhas


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=30); ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    tarefas = [(f, r) for r in range(a.reps) for f in FAMILIAS]
    with Pool(a.procs) as pool:
        res = pool.map(replica, tarefas, chunksize=1)
    df = pd.DataFrame([l for bloco in res for l in bloco])
    (ROOT / "resultados").mkdir(exist_ok=True); df.to_csv(ROOT / "resultados" / "variaveis.csv", index=False)
    print(df.groupby("classe")[["m_valid"]].mean(), "\n", df.shape)
