"""Teste 58 (calibração da lente, etapa 2): a cascata da v0, só leitura e sem laço, recebe uma coluna anônima Z(t) por mundo
e devolve κ = coerência média de fase entre os três andares (campo, memória, organização). Cinco mundos de resposta
conhecida: Kuramoto varrido (M1), ruído branco (M2), passeio aleatório (M3), travado (M4), Kuramoto embaralhado (M5).
Predição: PREDICAO_teste58_calibracao_lente.md, escrita antes deste arquivo.

    python ia-geometrica/teste58.py --fumaca   # só o M4, confirma que o pipeline fecha
    python ia-geometrica/teste58.py            # o teste (exige a predição); grava resultados_teste58.json
"""
import json, sys, time
from pathlib import Path
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr

ROOT = Path(__file__).resolve().parent
SEMENTE, NS, N, T, DT = 58, 30, 100, 10_000, 0.01
D_KURA, D_PASSEIO = 0.01, 0.005                       # D′ = 0,005: a fase se perde em ~1/(2D′) = 100 passos
SIGMA, OMEGA0 = 1.0, 1.0                              # rotação média comum a M1, M3 e M4 (a nula de pipeline precisa de tempo para destruir)
KC = 2 * SIGMA * np.sqrt(2 / np.pi)                   # K_c da gaussiana (Kuramoto): 2/(π g(0)), g(0) = 1/(σ√2π)
K_GRID = np.linspace(0.0, 2 * KC, 20)
LAM = 0.15 / 10 ** np.arange(3)                       # campo, memória, organização
AQUECIMENTO, NPERM = 50, 200
FUMACA = "--fumaca" in sys.argv


def lente(Z):
    """Z: (T, NS) complexo. Devolve κ por semente e as coerências de par. Só leitura, nascimento vazio."""
    T_, NS_ = Z.shape
    R = np.zeros((3, NS_), complex)
    fases = np.zeros((3, T_, NS_))
    for t in range(T_):
        prev = Z[t]
        for k in range(3):
            R[k] = R[k] + LAM[k] * (prev - R[k]); prev = R[k]
        fases[:, t] = np.angle(R)
    a, b = T_ // 2 + AQUECIMENTO, T_
    pares = {}
    for (i, j), nome in zip([(0, 1), (0, 2), (1, 2)], ["campo_memoria", "campo_organizacao", "memoria_organizacao"]):
        pares[nome] = np.abs(np.exp(1j * (fases[i, a:b] - fases[j, a:b])).mean(0))
    kappa = np.mean([pares[p] for p in pares], axis=0)
    return kappa, pares


def r_classico(Z):
    return np.abs(Z[T // 2 + AQUECIMENTO:]).mean(0)


def mundo_kuramoto(K, rng):
    om = rng.normal(OMEGA0, SIGMA, size=(NS, N)); th = rng.uniform(0, 2 * np.pi, size=(NS, N))
    Z = np.zeros((T, NS), complex)
    for t in range(T):
        z = np.exp(1j * th).mean(1); Z[t] = z
        th = th + DT * (om + K * np.abs(z)[:, None] * np.sin(np.angle(z)[:, None] - th)) + np.sqrt(2 * D_KURA * DT) * rng.normal(size=(NS, N))
    return Z


def mundo_branco(rng):
    return np.exp(1j * rng.uniform(0, 2 * np.pi, size=(T, NS, N))).mean(2)


def mundo_passeio(rng):
    th = rng.uniform(0, 2 * np.pi, size=(NS, N)); Z = np.zeros((T, NS), complex)
    for t in range(T):
        Z[t] = np.exp(1j * th).mean(1); th = th + OMEGA0 * DT + np.sqrt(2 * D_PASSEIO) * rng.normal(size=(NS, N))
    return Z


def mundo_travado(rng):
    th0 = rng.uniform(0, 2 * np.pi, size=NS)
    t = np.arange(T)[:, None]
    return np.exp(1j * (th0[None, :] + OMEGA0 * DT * t))


def embaralhar(Z, rng):
    return np.stack([Z[rng.permutation(T), s] for s in range(Z.shape[1])], 1)


def resumo(k):
    return {"mediana": float(np.median(k)), "media": float(np.mean(k)), "dp": float(np.std(k)), "min": float(np.min(k)), "max": float(np.max(k))}


def main():
    assert (ROOT / "PREDICAO_teste58_calibracao_lente.md").exists(), "sem predição, sem teste"
    rng = np.random.default_rng(SEMENTE); t0 = time.time()
    res = {"Kc": float(KC), "K_grid_sobre_Kc": (K_GRID / KC).round(3).tolist(), "NS": NS, "N": N, "T": T}

    Z4 = mundo_travado(rng); k4, p4 = lente(Z4)
    res["M4_travado"] = {"kappa": resumo(k4), "pares": {p: resumo(v) for p, v in p4.items()}, "R_classico": resumo(r_classico(Z4))}
    print(f"M4 travado: κ {np.median(k4):.3f} | R_K {np.median(r_classico(Z4)):.3f} | {time.time()-t0:.0f}s")
    if FUMACA:
        print("fumaça: só o M4; nenhum critério avaliado"); return

    Z2 = mundo_branco(rng); k2, p2 = lente(Z2)
    piso = np.array([np.median(lente(embaralhar(Z2, rng))[0]) for _ in range(NPERM)])
    PISO = float(np.percentile(piso, 95))
    res["M2_branco"] = {"kappa": resumo(k2), "pares": {p: resumo(v) for p, v in p2.items()}, "R_classico": resumo(r_classico(Z2)),
                        "piso_permutacao_p95": PISO, "piso_permutacao_mediana": float(np.median(piso))}
    print(f"M2 branco: κ {np.median(k2):.3f} | piso p95 {PISO:.3f} | {time.time()-t0:.0f}s")

    Z3 = mundo_passeio(rng); k3, p3 = lente(Z3)
    res["M3_passeio"] = {"kappa": resumo(k3), "pares": {p: resumo(v) for p, v in p3.items()}, "R_classico": resumo(r_classico(Z3))}
    print(f"M3 passeio: κ {np.median(k3):.3f} | R_K {np.median(r_classico(Z3)):.3f} | {time.time()-t0:.0f}s")

    kap, rk, pares1 = [], [], []
    Z15 = None
    for i, K in enumerate(K_GRID):
        Z1 = mundo_kuramoto(K, rng); k1, p1 = lente(Z1)
        kap.append(k1); rk.append(r_classico(Z1)); pares1.append({p: resumo(v) for p, v in p1.items()})
        if abs(K / KC - 1.5) < 1e-9 or (Z15 is None and K / KC >= 1.5): Z15 = Z1
        print(f"M1 K/Kc {K/KC:.2f}: κ {np.median(k1):.3f} | R_K {np.median(r_classico(Z1)):.3f} | {time.time()-t0:.0f}s")
    kap, rk = np.array(kap), np.array(rk)                 # (20, NS)
    res["M1_kuramoto"] = {"kappa_mediana": np.median(kap, 1).round(4).tolist(), "kappa_media": kap.mean(1).round(4).tolist(),
                          "R_classico_mediana": np.median(rk, 1).round(4).tolist(), "pares_por_K": pares1}

    k5, p5 = lente(embaralhar(Z15, rng))
    res["M5_embaralhado"] = {"kappa": resumo(k5), "pares": {p: resumo(v) for p, v in p5.items()}}
    print(f"M5 embaralhado (1,5 Kc): κ {np.median(k5):.3f}")

    # T1 — cruzamento de 0,5 na média das sementes, interpolado; bootstrap por sementes
    def cruza(curva):
        if curva.max() < 0.5 or curva[0] >= 0.5: return float("nan")
        i = int(np.argmax(curva >= 0.5)); x0, x1, y0, y1 = K_GRID[i - 1], K_GRID[i], curva[i - 1], curva[i]
        return float(x0 + (0.5 - y0) * (x1 - x0) / (y1 - y0))
    kx = cruza(kap.mean(1))
    boot = np.array([cruza(kap[:, rng.integers(0, NS, NS)].mean(1)) for _ in range(1000)])
    bq = np.nanpercentile(boot, [2.5, 97.5]) if np.isfinite(boot).sum() > 50 else [float("nan")] * 2
    T1 = bool(np.isfinite(kx) and abs(kx / KC - 1) <= 0.2 and bq[0] <= KC <= bq[1])
    res["T1"] = {"K_cruza_0_5_sobre_Kc": kx / KC if np.isfinite(kx) else None, "IC95_sobre_Kc": [float(b) / KC for b in bq],
                 "contem_Kc": bool(bq[0] <= KC <= bq[1]) if np.isfinite(bq[0]) else False, "passa": T1}

    # T2 — ordem por semente
    ordem = (k4 > kap[-1]) & (kap[-1] > kap[0]) & (np.abs(kap[0] - k2) <= 0.1) & (np.abs(k2 - k3) <= 0.1)
    T2 = bool(ordem.sum() >= 27)
    res["T2"] = {"sementes_na_ordem": int(ordem.sum()), "passa": T2,
                 "kappa_M4_M1_2Kc_M1_0_M2_M3": [float(np.median(x)) for x in (k4, kap[-1], kap[0], k2, k3)]}

    # T3 — ruído no piso; M2 vs M3 indistinguíveis
    p23 = float(mannwhitneyu(k2, k3, alternative="two-sided").pvalue)
    T3 = bool(np.median(k2) <= PISO and np.median(k3) <= PISO and p23 > 0.05)
    res["T3"] = {"kappa_M2_mediana": float(np.median(k2)), "kappa_M3_mediana": float(np.median(k3)), "piso": PISO, "p_M2_vs_M3": p23, "passa": T3}

    # T4 — nula de pipeline
    p52 = float(mannwhitneyu(k5, k2, alternative="two-sided").pvalue)
    T4 = bool(np.median(k5) <= PISO and p52 > 0.05)
    res["T4"] = {"kappa_M5_mediana": float(np.median(k5)), "piso": PISO, "p_M5_vs_M2": p52, "passa": T4}

    # referência clássica
    rho = float(spearmanr(kap.mean(1), rk.mean(1)).correlation)
    res["referencia_classica"] = {"spearman_kappa_vs_RK_na_varredura": rho, "lente_so_le_RK": bool(rho > 0.95)}

    res["veredito"] = {"aprovada": bool(T1 and T2 and T3 and T4), "ordena_nao_mede": bool((not T1) and T2 and T3 and T4),
                       "linha_fechada": bool((not T3) or (not T2 and not T4))}
    (ROOT / "resultados_teste58.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps({k: res[k] for k in ("T1", "T2", "T3", "T4", "referencia_classica", "veredito")}, indent=1, ensure_ascii=False))
    print(f"tempo total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
