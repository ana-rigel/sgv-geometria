"""Teste 47: a janela de sincronização parcial no limite contínuo (N → ∞), como função de β. Autoconsistência do teste 46
com médias em r ∈ [9, 14] (quadratura), parametrizada por u = Kρ. Comparada com as simulações de N = 48 do teste 44.
Predição: PREDICAO_teste47_limite_continuo.md (commit 40347dd), escrita antes deste arquivo.

    python ia-geometrica/teste47.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parent
NQ, NU, NOM = 1000, 2000, 300
BETAS = np.round(np.arange(-0.6, 0.9001, 0.1), 2)
KC = 2 / np.pi                                         # abertura das frequências normalizada a 1
KGF = np.round(np.arange(0.80, 1.40001, 0.0005), 4)    # K/K_c


def freqs(beta):
    r = 9 + 5 * (np.arange(NQ) + 0.5) / NQ; w = r ** (beta - 1.0); w = w - w.mean()
    return w / (9.0 ** (beta - 1) - 14.0 ** (beta - 1))


def s_med(x):
    a = np.abs(x); return np.where(a <= 1, x, x - np.sign(x) * np.sqrt(np.maximum(a * a - 1, 0)))


def ramo(dw):
    us = np.linspace(0.02, 1.6, NU); K, rho, f = np.full(NU, np.nan), np.full(NU, np.nan), np.full(NU, np.nan)
    for j, u in enumerate(us):
        om = np.linspace(dw.min() - u, dw.max() + u, NOM)
        G = s_med((dw[None, :] - om[:, None]) / u).mean(1); idx = np.flatnonzero(G[:-1] * G[1:] <= 0)
        best = (-1, None)
        for i in idx:
            a, b = om[i], om[i + 1]; ga = G[i]
            for _ in range(30):
                c = 0.5 * (a + b); gc = s_med((dw - c) / u).mean()
                if ga * gc > 0: a, ga = c, gc
                else: b = c
            o = 0.5 * (a + b); x = (dw - o) / u; lk = np.abs(x) <= 1
            R = np.mean(np.sqrt(np.clip(1 - x ** 2, 0, None)) * lk)
            if R > best[0]: best = (R, float(lk.mean()))
        if best[0] > 1e-6: rho[j], f[j] = best; K[j] = u / best[0] / KC
    return K, rho, f


def no_K(K, rho, f):
    """Para cada K da grade, o ramo de maior ρ entre os segmentos que o cruzam."""
    out_r, out_f = np.full(len(KGF), np.nan), np.full(len(KGF), np.nan)
    for j in range(len(K) - 1):
        a, b = K[j], K[j + 1]
        if not (np.isfinite(a) and np.isfinite(b)) or a == b: continue
        lo, hi = min(a, b), max(a, b); sel = (KGF >= lo) & (KGF <= hi)
        if not sel.any(): continue
        t = (KGF[sel] - a) / (b - a); rr = rho[j] + t * (rho[j + 1] - rho[j]); ff = np.where(t < 0.5, f[j], f[j + 1])
        cur = out_r[sel]; melhor = ~(cur >= rr)
        out_r[np.flatnonzero(sel)[melhor]] = rr[melhor]; out_f[np.flatnonzero(sel)[melhor]] = ff[melhor]
    return out_r, out_f


def KL_formula(dw):
    m = np.abs(dw).max()
    g = lambda u: u / np.mean(np.sqrt(np.clip(1 - (dw / u) ** 2, 0, None))) / KC
    return float(minimize_scalar(g, bounds=(m, 6 * m), method="bounded").fun)


def main():
    assert (ROOT / "PREDICAO_teste47_limite_continuo.md").exists(), "sem predição, sem teste"
    sim = json.loads((ROOT / "resultados_teste44.json").read_text()); res = {"beta": {}}
    for b in BETAS:
        dw = freqs(b); K, rho, f = ramo(dw); r_k, f_k = no_K(K, rho, f)
        jan = (f_k >= 0.5) & (f_k < 1 - 1e-12); trav = f_k >= 1 - 1e-12
        ini = float(KGF[jan][0]) if jan.any() else None; KL = float(KGF[trav][0]) if trav.any() else None
        larg = float(KL - ini) if (ini is not None and KL is not None) else 0.0
        d = {"inicio": ini, "K_L": KL, "K_L_formula": KL_formula(dw), "largura": larg,
             "rho_inicio": float(r_k[jan][0]) if jan.any() else None, "rho_K_L": float(r_k[trav][0]) if trav.any() else None}
        k = f"N48_b{b:+.1f}"
        if k in sim: d["N48_sim_largura"] = sim[k]["largura"]; d["N48_sim_K_L"] = sim[k]["K_L"]
        res["beta"][f"{b:+.1f}"] = d
        print(f"β {b:+.1f}: janela {ini}–{KL} largura {larg:.4f} | K_L fórmula {d['K_L_formula']:.4f} | ρ {d['rho_inicio']} → {d['rho_K_L']}"
              + (f" | N48 sim: largura {d['N48_sim_largura']:.3f} K_L {d['N48_sim_K_L']}" if 'N48_sim_largura' in d else ""), flush=True)
    B5 = ["-0.4", "-0.2", "+0.0", "+0.2", "+0.4"]; R = res["beta"]
    larg = [R[f"{b:+.1f}"]["largura"] for b in BETAS]
    J = {"J1": all(R[b]["K_L"] is not None and abs(R[b]["K_L"] - R[b]["N48_sim_K_L"]) <= 0.02 for b in B5),
         "J2": sum(abs(R[b]["largura"] - R[b]["N48_sim_largura"]) <= 0.02 for b in B5) >= 4,
         "J3": all(larg[i] > larg[i + 1] for i in range(len(larg) - 1)) and R["+0.9"]["largura"] <= 0.02,
         "J4": R["+0.0"]["largura"] >= 0.12}
    res["J"] = {k: bool(v) for k, v in J.items()}
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste47.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
