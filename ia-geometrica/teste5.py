"""Teste 5 (a régua de cegueira). Predição: PREDICAO_teste5_cegueira.md. Roda só porque a predição existe."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import lfilter
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste5_cegueira.md").exists(), "sem predição, sem teste"
N, CAL, SEEDS, K = 20000, 10000, range(1000, 1100), 4
LAMS = 0.15 / 10.0 ** np.arange(K); FC = LAMS / (2 * np.pi)
MUNDOS = {"branco": lambda s: V.mundo_deriva(N, s, 0.0), "deriva": lambda s: V.mundo_deriva(N, s, 0.9),
          "escada-3": lambda s: V.mundo_escada(N, s, [7, 70, 700]), "ciclico": lambda s: V.mundo_ciclico(N, s)}
TREINO = "deriva"; DESTINOS = ["branco", "escada-3", "ciclico"]
rng = np.random.default_rng(5)


def observar(x):
    """Registros R_j (pós-atualização), H = R_{t-1}, tensões T_0..T_{k-1} como no v0."""
    R = np.zeros((N, K, 2)); r = x
    for j, lam in enumerate(LAMS):
        r = lfilter([lam], [1, -(1 - lam)], r, axis=0); R[:, j] = r
    H = np.zeros_like(R); H[1:] = R[:-1]
    T = np.zeros((N, K)); T[:, 0] = np.linalg.norm(x - H[:, 0], axis=1)
    for j in range(1, K): T[:, j] = np.linalg.norm(R[:, j - 1] - R[:, j], axis=1)
    return R, H, T


def declarada(T, ini, fim):          # δ̂_j: potência de T_{j-1} acima de f_j, só com o que a v0 tem
    return np.array([V.cegueira(T[ini:fim, j], LAMS[j]) for j in range(K)])   # andar j+1 lê T_j (0-indexado) contra o seu próprio corte


def real(x, R, ini, fim):            # β_j: fração da variância do mundo que o registro j não representa
    num = np.mean(np.sum((x[ini:fim] - R[ini:fim]) ** 2, axis=2), axis=0); den = np.mean(np.sum((x[ini:fim] - x[ini:fim].mean(0)) ** 2, axis=1))
    return num / den


def pesos(x, H, ini, fim):
    A = H[ini:fim].transpose(0, 2, 1).reshape(-1, K); y = x[ini:fim].reshape(-1); G = A.T @ A
    return np.linalg.solve(G + 1e-6 * np.trace(G) / K * np.eye(K), A.T @ y)


def erro(x, H, w, ini, fim):
    return float(np.mean(np.linalg.norm(x[ini:fim] - np.einsum("tkd,k->td", H[ini:fim], w), axis=1)))


def main():
    # ---- observação de todos os mundos
    obs = {m: {} for m in MUNDOS}
    for m, gen in MUNDOS.items():
        for s in SEEDS:
            x = gen(s); R, H, T = observar(x)
            obs[m][s] = {"x": x, "R": R, "H": H, "T": T, "d_cal": declarada(T, 0, CAL), "d_med": declarada(T, CAL, N), "beta": real(x, R, CAL, N)}
        print(f"  {m}: δ̂ médio (medida) {np.round(np.mean([obs[m][s]['d_med'] for s in SEEDS], 0), 3)} | β médio {np.round(np.mean([obs[m][s]['beta'] for s in SEEDS], 0), 3)}", flush=True)
    # ---- A: verdadeira?
    d_nom = 1 - 2 * FC; A = {}
    for j in range(K):
        dj = np.array([obs[m][s]["d_med"][j] for m in MUNDOS for s in SEEDS]); bj = np.array([obs[m][s]["beta"][j] for m in MUNDOS for s in SEEDS])
        rho = float(spearmanr(dj, bj).correlation); perm = np.array([spearmanr(rng.permutation(dj), bj).correlation for _ in range(1000)])
        A[f"andar{j+1}"] = {"rho": rho, "perm_env": [float(perm.min()), float(perm.max())], "erro_abs_mediano": float(np.median(np.abs(dj - bj))), "delta_nominal": float(d_nom[j]),
                            "passa": bool(rho >= 0.7 and rho > perm.max())}
        print(f"  A andar {j+1}: ρ {rho:+.3f} (perm env {perm.min():+.3f}; {perm.max():+.3f}) | |δ̂−β| mediano {A[f'andar{j+1}']['erro_abs_mediano']:.3f} | δ_nom {d_nom[j]:.3f} → {A[f'andar{j+1}']['passa']}", flush=True)
    A["passa"] = all(A[f"andar{j+1}"]["passa"] for j in range(K))
    # ---- B: útil?
    B = {}
    for dest in DESTINOS:
        U, e_sem, e_com, e_teto = [], [], [], []
        for s in SEEDS:
            tr, de = obs[TREINO][s], obs[dest][s]; w = pesos(tr["x"], tr["H"], 0, CAL)
            vis = (1 - de["d_cal"]) / np.maximum(1 - tr["d_cal"], 1e-9); w2 = w * vis; w2 *= w.sum() / w2.sum() if abs(w2.sum()) > 1e-12 else 1.0
            es, ec = erro(de["x"], de["H"], w, CAL, N), erro(de["x"], de["H"], w2, CAL, N); et = erro(de["x"], de["H"], pesos(de["x"], de["H"], 0, CAL), CAL, N)
            e_sem.append(es); e_com.append(ec); e_teto.append(et); U.append(1 - ec / es)
        U = np.array(U); B[dest] = {"U_media": float(U.mean()), "U_env": [float(U.min()), float(U.max())], "U_pos": int((U > 0).sum()),
                                    "e_sem": float(np.mean(e_sem)), "e_com": float(np.mean(e_com)), "e_teto": float(np.mean(e_teto)), "passa": bool((U > 0).sum() >= 80)}
        print(f"  B → {dest}: U média {100*U.mean():+.1f} % (env {100*U.min():+.1f}; {100*U.max():+.1f}) | U>0 em {(U>0).sum()} | e sem {np.mean(e_sem):.3f} com {np.mean(e_com):.3f} teto {np.mean(e_teto):.3f} → {B[dest]['passa']}", flush=True)
    B["passa"] = all(B[d]["passa"] for d in DESTINOS)
    out = {"A": A, "B": B, "medias": {m: {"d_med": np.mean([obs[m][s]["d_med"] for s in SEEDS], 0).tolist(), "beta": np.mean([obs[m][s]["beta"] for s in SEEDS], 0).tolist()} for m in MUNDOS}}
    print(f"\n== teste 5: A (verdadeira) {'PASSA' if A['passa'] else 'REPROVA'} | B (útil) {'PASSA' if B['passa'] else 'REPROVA'}")
    (ROOT / "resultados_teste5.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
