"""Teste 44 (43-D): a forma da curva de rotação decide a janela de sincronização parcial? Curvas v ∝ r^β (Ω ∝ r^(β−1)),
frequências reescaladas para a abertura da curva plana; N = 12, 24, 48; mapa de Kuramoto dos testes 41–42 sem memória.
Predição: PREDICAO_teste44_forma_da_rotacao.md (commit 3f664ff), escrita antes deste arquivo.

    python ia-geometrica/teste44.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste42 as T42

ROOT = Path(__file__).resolve().parent
BETAS, NS = [-0.4, -0.2, 0.0, 0.2, 0.4], [12, 24, 48]
KG, PASSO, SIG0 = T42.KG, T42.PASSO, T42.SIG0


def disco_beta(N, beta):
    r = np.linspace(9.0, 14.0, N); w = r ** (beta - 1.0)
    dw_plano, kc = T42.disco(N)                                           # curva plana de referência
    w = (w - w.mean()) / (w.max() - w.min()) * (dw_plano.max() - dw_plano.min())
    return w, kc


def janela(o, N):
    parcial = np.mean((o["agl"] >= N / 2) & (o["esc"] >= 1), 0) > 0.5
    trav = np.all(o["agl"] == N, 0)
    return {"largura": float(parcial.sum() * PASSO), "K": KG[parcial].tolist(),
            "K_entrada": float(KG[parcial][0]) if parcial.any() else None,
            "K_L": float(KG[np.argmax(trav)]) if trav.any() else None,
            "C_mediana": np.median(o["Cb"], 0).round(4).tolist()}


def main():
    assert (ROOT / "PREDICAO_teste44_forma_da_rotacao.md").exists(), "sem predição, sem teste"
    res = {}
    for N in NS:
        ths = SIG0 * np.random.default_rng(440 + N).normal(size=(10, N))
        for b in BETAS:
            dw, kc = disco_beta(N, b)
            o = T42.grade(dw, kc, 0.0, 1.0, ths); j = janela(o, N)
            res[f"N{N}_b{b:+.1f}"] = j
            print(f"N {N:2d} β {b:+.1f}: largura {j['largura']:.3f} | entrada {j['K_entrada']} | K_L {j['K_L']}", flush=True)
    l12 = [res[f"N12_b{b:+.1f}"]["largura"] for b in BETAS]
    rho = spearmanr(BETAS, l12).correlation
    J = {"J1": abs(res["N12_b+0.0"]["largura"] - 0.14) <= 0.02,
         "J2": min(l12) > 0 and max(l12) >= 2 * min(l12) or (min(l12) == 0 and max(l12) > 0),
         "J3": bool(rho <= -0.9),
         "J4": all(res[f"N48_b{b:+.1f}"]["largura"] >= 0.5 * res[f"N12_b{b:+.1f}"]["largura"] for b in (-0.4, -0.2, 0.0))}
    res["spearman_N12"] = float(rho); res["warp_equivalente_graus"] = {f"{b:+.1f}": round(-b / 0.26, 2) for b in BETAS}
    res["J"] = {k: bool(v) for k, v in J.items()}
    print(f"Spearman(β, largura) N=12: {rho:.3f}")
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste44.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
