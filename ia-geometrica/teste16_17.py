"""Testes 16 e 17 (identidade e composta). Predição: PREDICAO_teste16_17_identidade_e_composta.md. Roda só porque a predição existe."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import lfilter
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste16_17_identidade_e_composta.md").exists(), "sem predição, sem teste"
N, CAL, SEEDS, K = 400000, 200000, range(1000, 1100), 4
LAMS = 0.15 / 10.0 ** np.arange(K); FC = LAMS / (2 * np.pi)
MUNDOS = {"lento-a": lambda s: mundo_lento(N, s, 20000.0, 0.3), "lento-b": lambda s: mundo_lento(N, s, 50000.0, 0.3), "lento-c": lambda s: mundo_lento(N, s, 100000.0, 1.0),
          "escada-3": lambda s: V.mundo_escada(N, s, [7, 70, 700]), "ciclico": lambda s: V.mundo_ciclico(N, s)}
TREINO = "deriva"; DESTINOS = []


def mundo_lento(n, seed, tau=50000.0, sig_b=0.3):
    """AR(1) com constante de tempo tau (mais lento que a identidade) mais ruído branco."""
    rng = np.random.default_rng(seed + 7); phi = 1 - 1 / tau; e = rng.normal(0, 1.0, (n, 2)) * np.sqrt(1 - phi ** 2)
    x = lfilter([1.0], [1, -phi], e, axis=0); return x + rng.normal(0, sig_b, (n, 2))
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


def ganho2(lam, f):
    return lam ** 2 / (1 - 2 * (1 - lam) * np.cos(2 * np.pi * f) + (1 - lam) ** 2)


def declarada(T, ini, fim, x=None, R=None):   # δ̂_j com ganho real: Σ S_entrada(f)·(1 − |H_j(f)|²) / Σ S_entrada(f)
    out = []
    for j in range(K):
        ent = x[ini:fim] if j == 0 else R[ini:fim, j - 1]; v = ent - ent.mean(0)
        P = (np.abs(np.fft.rfft(v, axis=0)) ** 2).sum(1); f = np.fft.rfftfreq(len(v)); tot = P[1:].sum()
        out.append(float((P[1:] * (1 - ganho2(LAMS[j], f[1:]))).sum() / tot) if tot > 0 else 0.0)
    return np.array(out)


def real(x, R, ini, fim):            # β_j: fração da variância do mundo que o registro j não representa
    num = np.mean(np.sum((x[ini:fim, None, :] - R[ini:fim]) ** 2, axis=2), axis=0); den = np.mean(np.sum((x[ini:fim] - x[ini:fim].mean(0)) ** 2, axis=1))
    return num / den


def pesos(x, H, ini, fim):
    A = H[ini:fim].transpose(0, 2, 1).reshape(-1, K); y = x[ini:fim].reshape(-1); G = A.T @ A
    return np.linalg.solve(G + 1e-6 * np.trace(G) / K * np.eye(K), A.T @ y)


def erro(x, H, w, ini, fim):
    return float(np.mean(np.linalg.norm(x[ini:fim] - np.einsum("tkd,k->td", H[ini:fim], w), axis=1)))


def main():
    # memória: por semente, gera os quatro mundos, calcula tudo e descarta (séries de 130 mil passos)
    decl = {m: [] for m in MUNDOS}; beta = {m: [] for m in MUNDOS}; Bs = {d: {"U": [], "e_sem": [], "e_com": [], "e_teto": []} for d in DESTINOS}
    for s in SEEDS:
        o = {}
        for m, gen in MUNDOS.items():
            x = gen(s); R, H, T = observar(x)
            o[m] = {"x": x, "H": H, "d_cal": declarada(T, 0, CAL, x, R), "d_med": declarada(T, CAL, N, x, R), "beta": real(x, R, CAL, N)}
            decl[m].append(o[m]["d_med"]); beta[m].append(o[m]["beta"])
        if (s - 1000) % 10 == 0: print(f"  s{s} ok", flush=True)
    for m in MUNDOS: print(f"  {m}: δ̂ médio (medida) {np.round(np.mean(decl[m], 0), 3)} | β médio {np.round(np.mean(beta[m], 0), 3)}", flush=True)
    # ---- teste 16: andar 4
    rhos = {}; A = {}
    for j in range(K):
        dj = np.array([v[j] for m in MUNDOS for v in decl[m]]); bj = np.array([v[j] for m in MUNDOS for v in beta[m]])
        rho = float(spearmanr(dj, bj).correlation); perm = np.array([spearmanr(rng.permutation(dj), bj).correlation for _ in range(1000)])
        A[f"andar{j+1}"] = {"rho": rho, "perm_env": [float(perm.min()), float(perm.max())], "erro_abs_mediano": float(np.median(np.abs(dj - bj)))}
        print(f"  16 andar {j+1}: ρ {rho:+.3f} (perm env {perm.min():+.3f}; {perm.max():+.3f}) | |δ̂−β| mediano {A[f'andar{j+1}']['erro_abs_mediano']:.3f}", flush=True)
    A["passa"] = bool(A["andar4"]["rho"] >= 0.7 and A["andar4"]["rho"] > A["andar4"]["perm_env"][1])
    # ---- teste 17: composta
    C = {}
    for j in range(K):
        dc = np.array([1 - np.prod(1 - np.array(v[:j + 1])) for m in MUNDOS for v in decl[m]]); bj = np.array([v[j] for m in MUNDOS for v in beta[m]]); ds = np.array([v[j] for m in MUNDOS for v in decl[m]])
        C[f"andar{j+1}"] = {"erro_abs_mediano_composta": float(np.median(np.abs(dc - bj))), "erro_abs_mediano_simples": float(np.median(np.abs(ds - bj))), "vies_mediano_composta": float(np.median(dc - bj)),
                            "rho_composta": float(spearmanr(dc, bj).correlation)}
        print(f"  17 andar {j+1}: |δ̂c−β| mediano {C[f'andar{j+1}']['erro_abs_mediano_composta']:.3f} (simples {C[f'andar{j+1}']['erro_abs_mediano_simples']:.3f}) | viés {C[f'andar{j+1}']['vies_mediano_composta']:+.3f} | ρ composta {C[f'andar{j+1}']['rho_composta']:+.3f}", flush=True)
    C["passa"] = bool(all(C[f"andar{j+1}"]["erro_abs_mediano_composta"] <= 0.05 for j in range(3)))
    out = {"teste16": A, "teste17": C, "medias": {m: {"d_med": np.mean(decl[m], 0).tolist(), "beta": np.mean(beta[m], 0).tolist()} for m in MUNDOS}}
    print(f"\n== teste 16 (andar 4): {'PASSA' if A['passa'] else 'REPROVA'} | teste 17 (composta): {'PASSA' if C['passa'] else 'REPROVA'}")
    (ROOT / "resultados_teste16_17.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
