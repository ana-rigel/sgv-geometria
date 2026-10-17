"""Experimentos 1 e 2 da mente geométrica (Teste B com regras da casa). Previsão: PREDICAO_mente_geometrica.md."""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
N, P, SIG_N, SEEDS = 4000, 20, 2.0, range(1000, 1100)   # Emenda 1: σ_n 0,3 → 2,0
LR_GRID = np.arange(0.05, 1.0, 0.05)


def mundo(seed, ritmo):
    rng = np.random.default_rng(seed); F = np.zeros((N, 2)); Fbar = np.zeros((N, 2)); saltos = []
    pos = rng.uniform(-8, 8, 2); prox = P if ritmo else 1 + rng.geometric(1 / P)
    for t in range(N):
        if t > 0 and t == prox:
            pos = rng.uniform(-8, 8, 2); saltos.append(t); prox = t + (P if ritmo else rng.geometric(1 / P))
        Fbar[t] = pos; F[t] = pos + rng.normal(0, SIG_N, 2)
    return F, Fbar, np.array(saltos)


def rodar(F, tipo, lr_fixo=0.15, pull=0.05):
    M = np.zeros(2); O = np.zeros(2); ema = None; T_hist = np.zeros(N); M_hist = np.zeros((N, 2))
    # relógio da organização (M1)
    P_hat = None; ultimo_salto = None; T_prev = 0.0
    for t in range(N):
        T = np.hypot(*(F[t] - M)); ema = T if ema is None else 0.92 * ema + 0.08 * T; E = (T - ema) / ema if ema > 1e-9 else 0.0
        if tipo == "M0": lr = lr_fixo
        elif tipo == "M2": lr = 0.05 + (0.8 - 0.05) / (1 + np.exp(-(E - 0.3) / 0.15))
        else:  # M1: detecta saltos, estima período, abre plasticidade na janela prevista
            if T - T_prev > 3 and (ultimo_salto is None or t - ultimo_salto > 3):   # Emenda 1: salto = degrau na tensão
                if ultimo_salto is not None:
                    d = t - ultimo_salto; P_hat = d if P_hat is None else 0.7 * P_hat + 0.3 * d
                ultimo_salto = t
            janela = P_hat is not None and ultimo_salto is not None and abs(((t - ultimo_salto) % round(P_hat)) - 0) <= 1 and (t - ultimo_salto) >= round(P_hat) - 1
            lr = 0.8 if janela else 0.15
        T_prev = T; M = M + lr * (F[t] - M); O = O + pull * (M - O); T_hist[t] = np.hypot(*(F[t] - M)); M_hist[t] = M
    return T_hist, M_hist


def custos(T_hist, M_hist, Fbar, saltos):
    js, jc = [], []
    for i, s in enumerate(saltos):
        fim = saltos[i + 1] if i + 1 < len(saltos) else N
        if s + 10 >= N: break
        js.append(T_hist[s:s + 10].sum())
        a, b = s + 11, min(s + 20, fim)
        if b > a: jc.append(np.hypot(*(M_hist[a:b] - Fbar[a:b]).T).mean())
    return float(np.mean(js)), float(np.mean(jc))


def main():
    out = {}
    for ritmo, nome in ((True, "W1"), (False, "W0")):
        res = {"M0": [], "M1": [], "M2": [], "fixo": {f"{lr:.2f}": [] for lr in LR_GRID}}
        for seed in SEEDS:
            F, Fbar, saltos = mundo(seed, ritmo)
            for tipo in ("M0", "M1", "M2"):
                Th, Mh = rodar(F, tipo); js, jc = custos(Th, Mh, Fbar, saltos); res[tipo].append((js, jc, js + 10 * jc))
            for lr in LR_GRID:
                Th, Mh = rodar(F, "M0", lr_fixo=float(lr)); js, jc = custos(Th, Mh, Fbar, saltos); res["fixo"][f"{lr:.2f}"].append((js, jc, js + 10 * jc))
        out[nome] = res; print(f"  {nome}: ok", flush=True)
    A = lambda v: np.array(v)
    # Experimento 1
    red = {}
    for w in ("W1", "W0"):
        m0 = A(out[w]["M0"])[:, 0]; m1 = A(out[w]["M1"])[:, 0]; red[w] = 100 * (1 - m1 / m0)
    calma_pior = 100 * (A(out["W1"]["M1"])[:, 1].mean() / A(out["W1"]["M0"])[:, 1].mean() - 1)
    e1_ritmo = (red["W1"].mean() - red["W0"].mean() >= 15) and (red["W1"].mean() > red["W0"].max())
    e1_custo = calma_pior <= 10
    # Experimento 2
    e2 = {}
    for w in ("W1", "W0"):
        J2 = A(out[w]["M2"])[:, 2]; Jfix = {k: A(v)[:, 2] for k, v in out[w]["fixo"].items()}
        melhor = min(Jfix, key=lambda k: Jfix[k].mean()); Jf = Jfix[melhor]
        e2[w] = {"J_M2": float(J2.mean()), "melhor_lr_fixo": melhor, "J_fixo": float(Jf.mean()), "env_fixo": [float(Jf.min()), float(Jf.max())],
                 "vence": bool(J2.mean() < Jf.mean()), "vence_env": bool(J2.mean() < Jf.min()),
                 "M2_salto_calma": [float(A(out[w]["M2"])[:, 0].mean()), float(A(out[w]["M2"])[:, 1].mean())],
                 "fixo_salto_calma": [float(A(out[w]["fixo"][melhor])[:, 0].mean()), float(A(out[w]["fixo"][melhor])[:, 1].mean())]}
    res = {"exp1": {"reducao_W1_pct": float(red["W1"].mean()), "reducao_W0_pct": float(red["W0"].mean()), "env_W0": [float(red["W0"].min()), float(red["W0"].max())],
                    "calma_pior_pct": float(calma_pior), "aprendeu_ritmo": bool(e1_ritmo), "custo_ok": bool(e1_custo),
                    "J_salto": {w: {k: float(A(out[w][k])[:, 0].mean()) for k in ("M0", "M1", "M2")} for w in ("W1", "W0")}},
           "exp2": e2}
    print("\n== mente geométrica")
    print(f"  exp1: redução de J_salto por M1: W1 {res['exp1']['reducao_W1_pct']:+.1f} % | W0 {res['exp1']['reducao_W0_pct']:+.1f} % (env W0 [{res['exp1']['env_W0'][0]:+.1f}; {res['exp1']['env_W0'][1]:+.1f}]) · calma piora {calma_pior:+.1f} % → aprendeu ritmo: {e1_ritmo}; custo ok: {e1_custo}")
    for w in ("W1", "W0"):
        e = e2[w]; print(f"  exp2 {w}: J(M2) {e['J_M2']:.2f} vs melhor fixo lr={e['melhor_lr_fixo']} J {e['J_fixo']:.2f} (env [{e['env_fixo'][0]:.2f}; {e['env_fixo'][1]:.2f}]) → vence {e['vence']}, acima do envelope {e['vence_env']} · salto/calma M2 {e['M2_salto_calma'][0]:.1f}/{e['M2_salto_calma'][1]:.2f} fixo {e['fixo_salto_calma'][0]:.1f}/{e['fixo_salto_calma'][1]:.2f}")
    print("  J_salto:", res["exp1"]["J_salto"])
    (ROOT / "resultados_mente.json").write_text(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
