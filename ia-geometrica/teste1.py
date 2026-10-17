"""Teste 1 (deriva). Predição: PREDICAO_teste1.md. Roda só porque a predição existe."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste1.md").exists(), "sem predição, sem teste"
N, CAL, SEEDS, PHIS = 6000, 2000, range(1000, 1100), [0.0, 0.5, 0.9, 0.99]
GRID = np.arange(0.05, 1.0, 0.05)


def registros(x, lams):
    R = np.zeros((len(lams), x.shape[1])); H = np.zeros((len(x), len(lams), x.shape[1]))
    for t in range(len(x)):
        H[t] = R                                   # R_{t-1}: o que a mente tem ANTES de ver x_t
        R[0] = R[0] + lams[0] * (x[t] - R[0])
        for j in range(1, len(lams)): R[j] = R[j] + lams[j] * (R[j - 1] - R[j])
    return H


def erro_leitura(x, H):
    """Ajusta pesos por mínimos quadrados (por coordenada, mesmos pesos) na calibração; erro fora dela."""
    k = H.shape[1]; A = H[:CAL].reshape(-1, k); y = x[:CAL].reshape(-1)
    # H[:CAL] tem forma (CAL, k, d) → empilha as d coordenadas como linhas
    A = H[:CAL].transpose(0, 2, 1).reshape(-1, k); y = x[:CAL].reshape(-1)
    w = np.linalg.lstsq(A, y, rcond=None)[0]
    xhat = np.einsum("tkd,k->td", H[CAL:], w); return float(np.mean(np.linalg.norm(x[CAL:] - xhat, axis=1))), w


def main():
    out = {}
    for phi in PHIS:
        Vs = []; melhores = []; ws = []
        for s in SEEDS:
            x = V.mundo_deriva(N, s, phi); lams = 0.15 / 10.0 ** np.arange(4)
            e0, w = erro_leitura(x, registros(x, lams))
            e_un = {f"{lam:.2f}": erro_leitura(x, registros(x, [lam]))[0] for lam in GRID}
            lam_best = min(e_un, key=e_un.get); Vs.append(1 - e0 / e_un[lam_best]); melhores.append(lam_best); ws.append(w)
        Vs = np.array(Vs); out[str(phi)] = {"V_media": float(Vs.mean()), "V_env": [float(Vs.min()), float(Vs.max())], "lambda_unico_mais_frequente": max(set(melhores), key=melhores.count),
                                        "pesos_medios": [float(v) for v in np.mean(ws, 0)]}
        print(f"  φ {phi:<4}: V média {100*Vs.mean():+.2f} % (env {100*Vs.min():+.1f}; {100*Vs.max():+.1f}) | melhor λ único {out[str(phi)]['lambda_unico_mais_frequente']} | pesos {np.round(np.mean(ws,0),3)}", flush=True)
    Vm = [out[str(p)]["V_media"] for p in PHIS]
    a = all(v > 0 for v in Vm[1:]); b = all(Vm[i] < Vm[i + 1] for i in range(3)); c = abs(Vm[0]) < 0.02
    out["criterio"] = {"a_positiva": a, "b_monotonica": b, "c_nula_em_0": c, "passa": a and b and c}
    print(f"\n== teste 1: (a) {a} (b) {b} (c) {c} → {'PASSA' if a and b and c else 'REPROVA'}")
    (ROOT / "resultados_teste1.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
