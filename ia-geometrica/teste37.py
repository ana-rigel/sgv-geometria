"""Teste 37 (a galáxia no cubo: o laço que segura o modo). Modelo ilustrativo da página "NGC 628 no cubo": 12 anéis com o modo
m=5 sob cisalhamento (curva plana, 200 km/s), turbulência e acoplamento de Kuramoto, com a v0 dentro do disco.
A: K = 0 contra a fórmula exata do enrolamento. B: K = 1,2 K_c fixo. Laço I: K corrigido até C̄ = 0,627 (com alvo).
Laço II: K = 0,8 K_c, escuta o andar j, rigidez modulada pela tensão |R_j| − C (sem alvo).
Predição: PREDICAO_teste37_galaxia_laco.md (commit 62de4b3), escrita antes deste arquivo.

    python ia-geometrica/teste37.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
M, NA, R0, R1, V, KMS = 5, 12, 9.0, 14.0, 200.0, 1.0227e-3
T, D, SIG0, NS, SEMENTE = 1000, 2.5e-4, 0.15, 100, 37
LAM = 0.15 / 10 ** np.arange(4)
ALVO, FAIXA = 0.627, (0.527, 0.727)

r = np.linspace(R0, R1, NA)
w = M * (V / r) * KMS; DW = w - w.mean(); KC = 2 * (w.max() - w.min()) / np.pi

rng = np.random.default_rng(SEMENTE)
TH0 = SIG0 * rng.normal(size=(NS, NA))
XI = rng.normal(size=(T, NS, NA)) * np.sqrt(2 * D)          # a mesma sequência de ruído em todos os cenários


def rodar(K, escuta=None, nasce="vazia", beta=0.0, laco1=False):
    """escuta: None = instantânea; j ∈ {1,2,3,4} = andar j. Devolve C(t) (T+1, NS), K(t), λ_j(t), |R_j|(t), fração travada."""
    th = TH0.copy(); z0 = np.exp(1j * th).mean(1)
    R = np.tile(z0[:, None], (1, 4)) if nasce == "semeada" else np.zeros((NS, 4), complex)
    Kv = np.full(NS, 0.0 if laco1 else K, float); Cb = np.abs(z0)
    C = np.zeros((T + 1, NS)); C[0] = np.abs(z0); Kh = np.zeros(T); Lh = np.zeros(T); Rh = np.zeros(T)
    rel = np.zeros((T, NS, NA)); Ksum = np.zeros(NS)
    for t in range(T):
        z = np.exp(1j * th).mean(1); Cn = np.abs(z); prev = z
        for k in range(4):
            lam = LAM[k]
            if escuta is not None and k == escuta - 1 and beta > 0:
                lam = LAM[k] * np.exp(-beta * np.maximum(0.0, np.abs(R[:, k]) - Cn))
            R[:, k] = R[:, k] + lam * (prev - R[:, k]); prev = R[:, k]
            if escuta is not None and k == escuta - 1: Lh[t] = float(np.mean(lam))
        A = z if escuta is None else R[:, escuta - 1]
        if escuta is not None: Rh[t] = float(np.mean(np.abs(A)))
        alvo_fase = np.angle(A)[:, None]
        th = th + DW + Kv[:, None] * np.abs(A)[:, None] * np.sin(alvo_fase - th) + XI[t]
        rel[t] = th - alvo_fase
        C[t + 1] = np.abs(np.exp(1j * th).mean(1))
        if laco1:
            Cb = Cb + (C[t + 1] - Cb) / 50.0
            Kv = np.clip(Kv + 0.02 * KC * (ALVO - Cb), 0.0, 3 * KC)
        Kh[t] = float(np.mean(Kv))
        if t >= 600: Ksum += Kv
    # fração de anéis travados: fase relativa ao alvo varia menos que π entre 600 e 1.000 Myr
    dr = np.abs(np.unwrap(rel[600:], axis=0)[-1] - np.unwrap(rel[600:], axis=0)[0])
    return {"C": C, "K": Kh, "lam": Lh, "R": Rh, "travados": float(np.mean(dr < np.pi)), "Kinf": Ksum / (T - 600)}


def cbar(C, a=300, b=1000):
    return C[a:b + 1].mean(0)


def main():
    assert (ROOT / "PREDICAO_teste37_galaxia_laco.md").exists(), "sem predição, sem teste"
    res = {"Kc_mrad_por_Myr": KC * 1e3, "faixa": FAIXA}
    t = np.arange(T + 1)

    # A — enrolamento contra a fórmula exata
    A = rodar(0.0)
    CA = np.abs(np.exp(1j * np.outer(t, DW)).mean(1)) * np.exp(-SIG0 ** 2 / 2) * np.exp(-D * t)
    mA = A["C"].mean(1); dev = float(np.max(np.abs(mA[:301] - CA[:301])))
    t05 = int(np.argmax(mA < 0.5)); t05f = float(t[np.argmax(CA < 0.5)])
    j1 = dev <= 0.05 and abs(t05 - 87.5) <= 5
    res["A"] = {"desvio_max_0_300": dev, "t_C_menor_0_5_sim": t05, "t_C_menor_0_5_formula": t05f,
                "C_medio_300_1000": float(cbar(A["C"]).mean()), "curva_media_cada_50": mA[::50].round(3).tolist(),
                "formula_cada_50": CA[::50].round(3).tolist()}

    # B — travamento fixo
    B = rodar(1.2 * KC); cb = cbar(B["C"])
    nB = int(np.sum((cb >= FAIXA[0]) & (cb <= FAIXA[1]))); j2 = nB >= 80
    res["B"] = {"C_barra_mediana": float(np.median(cb)), "na_faixa": nB, "travados": B["travados"]}

    # Laço I — com alvo
    L1 = rodar(0.0, laco1=True); Kinf = L1["K"][600:].mean() / KC
    cb1 = cbar(L1["C"], 600, 1000)
    kfs = L1["Kinf"] / KC                                   # K∞ por semente: média de K/K_c entre 600 e 1.000 Myr
    nL1 = int(np.sum((kfs >= 0.9) & (kfs <= 1.1) & (np.abs(cb1 - ALVO) <= 0.05))); j3 = nL1 >= 80
    L1b = rodar(0.0, escuta=4, nasce="semeada", laco1=True)
    res["laco_I"] = {"K_inf_sobre_Kc_medio": float(Kinf), "K_inf_sobre_Kc_mediana": float(np.median(kfs)),
                     "C_barra_600_1000_mediana": float(np.median(cb1)), "sementes_ok": nL1,
                     "K_curva_cada_100": (L1["K"][::100] / KC).round(3).tolist(),
                     "andar4_semeado": {"K_inf_sobre_Kc_mediana": float(np.median(L1b["Kinf"] / KC)),
                                        "C_barra_600_1000_mediana": float(np.median(cbar(L1b["C"], 600, 1000)))}}

    # Laço II — sem alvo
    L2 = {}
    for j in (2, 3, 4):
        for nasce in ("vazia", "semeada"):
            for beta in (0.0, 2.0, 5.0, 10.0):
                o = rodar(0.8 * KC, escuta=j, nasce=nasce, beta=beta); cbv = cbar(o["C"])
                L2[f"andar{j}_{nasce}_beta{beta:g}"] = {"cb": cbv, "travados": o["travados"],
                                                       "lam_sobre_lam0_cada_100": (o["lam"][::100] / LAM[j - 1]).round(4).tolist(),
                                                       "R_cada_100": o["R"][::100].round(3).tolist()}
    a2 = L2["andar2_vazia_beta5"]["cb"]; a2b0 = L2["andar2_vazia_beta0"]["cb"]
    n4 = int(np.sum((a2 >= FAIXA[0]) & (a2 <= FAIXA[1]))); efeito = float(np.median(a2 - a2b0))
    j4 = n4 >= 80 and efeito >= 0.10
    med = {j: float(np.median(L2[f"andar{j}_semeada_beta5"]["cb"])) for j in (2, 3, 4)}
    j5 = med[2] < med[3] and med[2] < med[4]
    res["laco_II"] = {k: {"C_barra_mediana": float(np.median(v["cb"])), "na_faixa": int(np.sum((v["cb"] >= FAIXA[0]) & (v["cb"] <= FAIXA[1]))),
                          "travados": v["travados"], "lam_sobre_lam0_cada_100": v["lam_sobre_lam0_cada_100"], "R_cada_100": v["R_cada_100"]}
                      for k, v in L2.items()}
    res["J4_detalhe"] = {"na_faixa": n4, "efeito_mediano_vs_beta0": efeito}
    res["J5_detalhe"] = med
    res["J"] = {"J1": bool(j1), "J2": bool(j2), "J3": bool(j3), "J4": bool(j4), "J5": bool(j5)}

    print(f"K_c = {KC * 1e3:.1f} mrad/Myr")
    print(f"A: desvio máx 0–300 {dev:.3f} | t(C<0,5) sim {t05} fórmula {t05f} | C̄ 300–1000 {res['A']['C_medio_300_1000']:.3f}")
    print(f"   sim     cada 50 Myr: {res['A']['curva_media_cada_50'][:12]}")
    print(f"   fórmula cada 50 Myr: {res['A']['formula_cada_50'][:12]}")
    print(f"B: C̄ mediana {res['B']['C_barra_mediana']:.3f} | na faixa {nB}/100 | travados {B['travados']:.2f}")
    print(f"Laço I: K∞/K_c {Kinf:.3f} (mediana por semente {np.median(kfs):.3f}) | C̄ 600–1000 {np.median(cb1):.3f} | sementes ok {nL1} | K/K_c cada 100: {res['laco_I']['K_curva_cada_100']}")
    print(f"        andar 4 semeado: K/K_c {res['laco_I']['andar4_semeado']['K_inf_sobre_Kc_mediana']:.3f} | C̄ {res['laco_I']['andar4_semeado']['C_barra_600_1000_mediana']:.3f}")
    for k, v in res["laco_II"].items():
        print(f"Laço II {k:24s} C̄ {v['C_barra_mediana']:.3f} | na faixa {v['na_faixa']:3d} | travados {v['travados']:.2f} | |R| {v['R_cada_100'][:6]} | λ/λ₀ {v['lam_sobre_lam0_cada_100'][:6]}")
    print(f"J4: na faixa {n4}/100, efeito vs β=0 {efeito:+.3f} | J5 medianas {med}")
    print(f"== J1 {'PASSA' if j1 else 'REPROVA'} | J2 {'PASSA' if j2 else 'REPROVA'} | J3 {'PASSA' if j3 else 'REPROVA'} | J4 {'PASSA' if j4 else 'REPROVA'} | J5 {'PASSA' if j5 else 'REPROVA'}")
    (ROOT / "resultados_teste37.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
