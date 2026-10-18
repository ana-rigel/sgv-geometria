"""Teste 4 (escada livre). Predição: PREDICAO_teste4.md. Roda só porque a predição existe."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import lfilter
from scipy.optimize import minimize
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste4.md").exists(), "sem predição, sem teste"
N, CAL, SEEDS = 20000, 10000, range(1000, 1100)
MUNDOS = {"escada-2": ([7, 70], 2), "escada-3": ([7, 70, 700], 3), "escada-4": ([7, 70, 700, 7000], 4), "ciclico": (None, 4)}
FAIXA = (7.0, 13.0)


def registros(x, lams):
    """Cascata de EMAs (a recursão do v0 via lfilter). Devolve H[t] = R_{t-1}, forma (n, k, d)."""
    H = np.zeros((len(x), len(lams), x.shape[1])); R = x
    for j, lam in enumerate(lams):
        R = lfilter([lam], [1, -(1 - lam)], R, axis=0); H[1:, j] = R[:-1]
    return H


def erro_leitura(x, H):
    k = H.shape[1]; A = H[:CAL].transpose(0, 2, 1).reshape(-1, k); y = x[:CAL].reshape(-1)
    G = A.T @ A; w = np.linalg.solve(G + 1e-6 * np.trace(G) / k * np.eye(k), A.T @ y)
    xhat = np.einsum("tkd,k->td", H[CAL:], w); return float(np.mean(np.linalg.norm(x[CAL:] - xhat, axis=1))), w


def erro_calib(x, H):
    k = H.shape[1]; A = H[:CAL].transpose(0, 2, 1).reshape(-1, k); y = x[:CAL].reshape(-1)
    G = A.T @ A; w = np.linalg.solve(G + 1e-6 * np.trace(G) / k * np.eye(k), A.T @ y)
    return float(np.mean(np.linalg.norm(x[:CAL] - np.einsum("tkd,k->td", H[:CAL], w), axis=1)))


sig = lambda u: 1 / (1 + np.exp(-u)); logit = lambda p: np.log(p / (1 - p))


def ajustar(x, k):
    melhor = None
    for l1 in (0.5, 0.15, 0.05):
        u0 = logit(np.clip(l1 / 10.0 ** np.arange(k), 1e-5, 1 - 1e-5))
        r = minimize(lambda u: erro_calib(x, registros(x, sig(u))), u0, method="Nelder-Mead", options={"maxiter": 800, "xatol": 1e-3, "fatol": 1e-7})
        if melhor is None or r.fun < melhor.fun: melhor = r
    return np.sort(sig(melhor.x))[::-1]


def main():
    out = {}
    for nome, (taus, k) in MUNDOS.items():
        rec, fora, ganha, lt = [], [], [], []; lams_fixa = 0.15 / 10.0 ** np.arange(k); por = {}
        for s in SEEDS:
            x = V.mundo_escada(N, s, taus) if taus else V.mundo_ciclico(N, s)
            lam = ajustar(x, k); e_livre, _ = erro_leitura(x, registros(x, lam)); e_fixa, _ = erro_leitura(x, registros(x, lams_fixa))
            raz = lam[:-1] / lam[1:]; dentro = bool(np.all((raz >= FAIXA[0]) & (raz <= FAIXA[1])))
            rec.append(dentro); fora.append(not dentro); ganha.append(e_livre < e_fixa)
            if taus: lt.append(lam * np.array(taus))
            por[str(s)] = {"lambda": lam.tolist(), "razoes": raz.tolist(), "e_livre": e_livre, "e_fixa": e_fixa}
            if (s - 1000) % 25 == 0: print(f"  {nome} s{s}: λ {np.round(lam, 4)} razões {np.round(raz, 1)} | e livre {e_livre:.3f} fixa {e_fixa:.3f}", flush=True)
        out[nome] = {"recupera": int(sum(rec)), "fora_da_progressao": int(sum(fora)), "livre_ganha": int(sum(ganha)),
                     "lambda_medio": np.mean([por[str(s)]["lambda"] for s in SEEDS], 0).tolist(), "razoes_medianas": np.median([por[str(s)]["razoes"] for s in SEEDS], 0).tolist(),
                     "lambda_x_tau_mediano": (np.median(lt, 0).tolist() if lt else None), "sementes": por}
        print(f"== {nome}: recupera {sum(rec)}/100 | fora {sum(fora)}/100 | livre ganha {sum(ganha)}/100 | razões medianas {np.round(out[nome]['razoes_medianas'],1)} | λ·τ {None if not lt else np.round(np.median(lt,0),2)}", flush=True)
    a = all(out[m]["recupera"] >= 80 for m in ("escada-2", "escada-3", "escada-4")); b = out["ciclico"]["fora_da_progressao"] >= 80 and out["ciclico"]["livre_ganha"] >= 80
    out["criterio"] = {"a_escadas": bool(a), "b_ciclico": bool(b), "passa": bool(a and b)}
    print(f"\n== teste 4: (a) {a} (b) {b} → {'PASSA' if a and b else 'REPROVA'}")
    (ROOT / "resultados_teste4.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
