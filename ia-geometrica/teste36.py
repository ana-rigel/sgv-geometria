"""Teste 36 (ela aprende com o erro?): o relógio v1 guarda μ, o dia esperado da entrada das águas, e a cada entrada vivida
corrige μ ← μ + η(o − μ). Verifica se aprende (semente errada), readapta (degrau; e o atraso real de 2018–25), não aprende
ruído (sem mudança) e depende do erro e da sua ordem (ordem embaralhada; erro invertido). Nada é comparado com o calendário.
Predição: PREDICAO_teste36_aprende_com_o_erro.md (commit 09145f4), escrita antes deste arquivo.

    python ia-geometrica/teste36.py        # o teste (exige a predição)
"""
import json, sys
from datetime import date
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste35 as T35

ROOT = Path(__file__).resolve().parent
ETA, ETAS_REL = 0.3, [0.1, 0.2, 0.5]
NMUNDOS, NEST, BASE, DEGRAU, I_DEGRAU, SEMENTE = 100, 24, 280.0, 20.0, 12, 36   # degrau a partir da 13ª estação (índice 12)


def entradas_reais():
    out = {}
    for n in T35.LUGARES:
        D, P, *_ = T35.ler_juara() if n == "juara" else T35.ler_lugar(n)
        ent = T35.entradas(D, P)
        out[n] = {y: date.fromisoformat(D[d]).timetuple().tm_yday for y, d in ent.items() if d is not None}
    return out


def laco(o, mu0, eta, invertido=False):
    """Previsões p[y] (μ antes de ver a entrada y) e erros o − p."""
    mu = mu0; p = np.zeros(len(o))
    for y, oy in enumerate(o):
        p[y] = mu; e = oy - mu; mu = mu - eta * e if invertido else mu + eta * e
    return p, o - p


def condicoes(pool, eta, rng):
    R = {k: {"p": [], "e": []} for k in "ABCDE"}
    for _ in range(NMUNDOS):
        eps = rng.choice(pool, NEST, replace=True); degrau = DEGRAU * (np.arange(NEST) >= I_DEGRAU)
        oA = BASE + eps; oB = BASE + eps + degrau; oD = oB[rng.permutation(NEST)]
        for k, (o, mu0, inv) in {"A": (oA, BASE - 30, False), "B": (oB, BASE, False), "C": (oA, BASE, False),
                                 "D": (oD, BASE, False), "E": (oB, BASE, True)}.items():
            p, e = laco(o, mu0, eta, inv); R[k]["p"].append(p); R[k]["e"].append(e)
    return {k: {q: np.array(v) for q, v in d.items()} for k, d in R.items()}


def medidas(R):
    pp = lambda k: R[k]["p"]
    pos_pre = lambda k: pp(k)[:, 16:19].mean(1) - pp(k)[:, 10:13].mean(1)
    p7 = pp("A")[:, 6]; fimC = pp("C")[:, 21:24].mean(1) - BASE
    m = {
        "A_media_abs_p7_menos_base": float(np.mean(np.abs(p7 - BASE))), "A_mundos_mais_perto_que_semente": int(np.sum(np.abs(p7 - BASE) < 30)),
        "B_pos_menos_pre_mediana": float(np.median(pos_pre("B"))), "B_mundos_ge10": int(np.sum(pos_pre("B") >= 10)),
        "C_deriva_media": float(np.mean(fimC)), "C_mundos_dentro_15": int(np.sum(np.abs(fimC) < 15)),
        "D_pos_menos_pre_mediana": float(np.median(pos_pre("D"))), "D_mundos_ge10": int(np.sum(pos_pre("D") >= 10)),
        "E_pos_menos_pre_mediana": float(np.median(pos_pre("E"))), "E_mundos_negativos": int(np.sum(pos_pre("E") < 0)),
        "curvas_erro_abs_medio": {k: np.mean(np.abs(R[k]["e"]), axis=0).round(2).tolist() for k in "ABCD"},
    }
    return m


def main():
    assert (ROOT / "PREDICAO_teste36_aprende_com_o_erro.md").exists(), "sem predição, sem teste"
    reais = entradas_reais()
    pool = np.concatenate([[reais[n][y] - np.mean([reais[n][z] for z in range(2010, 2018)]) for y in range(2010, 2018)] for n in T35.LUGARES])
    rng = np.random.default_rng(SEMENTE)
    M = medidas(condicoes(pool, ETA, rng))
    res = {"eta": ETA, "pool_anomalias": {"n": int(len(pool)), "dp": float(np.std(pool))}, "sinteticos": M}

    j1 = M["A_media_abs_p7_menos_base"] <= 10 and M["A_mundos_mais_perto_que_semente"] >= 90
    j2 = M["B_mundos_ge10"] >= 80
    j4 = -3 <= M["C_deriva_media"] <= 3 and M["C_mundos_dentro_15"] >= 95
    j5 = M["D_mundos_ge10"] <= 20 and M["E_mundos_negativos"] >= 90

    real = {}
    for n in T35.LUGARES:
        mu0 = float(np.mean([reais[n][y] for y in range(2010, 2018)])); o = np.array([reais[n][y] for y in range(2018, 2026)], float)
        p, e = laco(o, mu0, ETA); mu_fim = p[-1] + ETA * e[-1]
        real[n] = {"mu0": mu0, "previsoes": p.round(1).tolist(), "entradas": o.tolist(), "erros": e.round(1).tolist(),
                   "mu_fim": float(mu_fim), "andou": float(mu_fim - mu0)}
    j3n = sum(real[n]["andou"] >= 6 for n in T35.LUGARES); j3 = j3n >= 4
    res["real"] = real
    res["J"] = {"J1": bool(j1), "J2": bool(j2), "J3": {"lugares": int(j3n), "passa": bool(j3)}, "J4": bool(j4), "J5": bool(j5)}
    res["eta_relatado"] = {}
    for eta in ETAS_REL:
        Mr = medidas(condicoes(pool, eta, np.random.default_rng(SEMENTE)))
        Mr.pop("curvas_erro_abs_medio")
        andou = {n: float(laco(np.array([reais[n][y] for y in range(2018, 2026)], float), np.mean([reais[n][y] for y in range(2010, 2018)]), eta)[0][-1]
                          + eta * laco(np.array([reais[n][y] for y in range(2018, 2026)], float), np.mean([reais[n][y] for y in range(2010, 2018)]), eta)[1][-1]
                          - np.mean([reais[n][y] for y in range(2010, 2018)])) for n in T35.LUGARES}
        res["eta_relatado"][eta] = {**Mr, "real_andou": andou}

    print(f"pool de anomalias: n {len(pool)}, dp {np.std(pool):.1f} d")
    for k, v in M.items():
        if k != "curvas_erro_abs_medio": print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
    for k, c in M["curvas_erro_abs_medio"].items():
        print(f"  erro |médio| {k}: " + " ".join(f"{x:.0f}" for x in c))
    for n, o in real.items():
        print(f"  real {n:16s} μ₀ {o['mu0']:.1f} → {o['mu_fim']:.1f} (andou {o['andou']:+.1f}) | erros {o['erros']}")
    for eta, o in res["eta_relatado"].items():
        print(f"  η {eta}: A {o['A_media_abs_p7_menos_base']:.1f}/{o['A_mundos_mais_perto_que_semente']} | B ≥10 {o['B_mundos_ge10']} | C {o['C_deriva_media']:+.1f}/{o['C_mundos_dentro_15']}"
              f" | D ≥10 {o['D_mundos_ge10']} | E <0 {o['E_mundos_negativos']} | real andou " + " ".join(f"{v:+.0f}" for v in o["real_andou"].values()))
    print(f"== J1 {'PASSA' if j1 else 'REPROVA'} | J2 {'PASSA' if j2 else 'REPROVA'} | J3 {j3n}/6 {'PASSA' if j3 else 'REPROVA'}"
          f" | J4 {'PASSA' if j4 else 'REPROVA'} | J5 {'PASSA' if j5 else 'REPROVA'}")
    (ROOT / "resultados_teste36.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


def diagnostico():
    """Depois da rodada, NÃO julgado: no erro invertido (E), separa o efeito do degrau da explosão do laço instável,
    comparando o mesmo laço invertido no mundo com degrau e no mesmo mundo sem degrau (mesmos ε)."""
    reais = entradas_reais()
    pool = np.concatenate([[reais[n][y] - np.mean([reais[n][z] for z in range(2010, 2018)]) for y in range(2010, 2018)] for n in T35.LUGARES])
    rng = np.random.default_rng(SEMENTE); dif, expl, sinal = [], [], 0
    for _ in range(NMUNDOS):
        eps = rng.choice(pool, NEST, replace=True); degrau = DEGRAU * (np.arange(NEST) >= I_DEGRAU)
        pB, _ = laco(BASE + eps + degrau, BASE, ETA, True); pC, _ = laco(BASE + eps, BASE, ETA, True)
        d = (pB[16:19].mean() - pB[10:13].mean()) - (pC[16:19].mean() - pC[10:13].mean())
        dif.append(d); expl.append(abs(pC[16:19].mean() - BASE)); sinal += int(d < 0)
    out = {"efeito_do_degrau_mediana": float(np.median(dif)), "efeito_do_degrau_negativo_em": sinal,
           "tamanho_da_explosao_sem_degrau_mediana": float(np.median(expl))}
    print(out); (ROOT / "diagnostico_teste36.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    diagnostico() if "--diagnostico" in sys.argv else main()
