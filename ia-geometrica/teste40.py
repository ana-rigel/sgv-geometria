"""Teste 40 (etapa 40-A): os ramos de equilíbrio do disco de 12 anéis, sem memória e sem controlador. Equilíbrios travados
pela autoconsistência de Kuramoto (u = KC), estabilidade pelo jacobiano no referencial girante, e média de C no tempo abaixo
do travamento, partindo coerente e sorteado, com e sem ruído.
Predição: PREDICAO_teste40_ramos_do_disco.md (commit 09b9de4), escrita antes deste arquivo.

    python ia-geometrica/teste40.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste37 as T37

ROOT = Path(__file__).resolve().parent
DW, KC, N, FAIXA = T37.DW, T37.KC, T37.NA, T37.FAIXA
MX = np.max(np.abs(DW))
KGRADE = np.round(np.arange(0.50, 1.6001, 0.01), 2)


# ---------------------------------------------------------------- ramos travados
def C_de_u(u, s):
    return float(np.mean(s * np.sqrt(np.clip(1 - (DW / u) ** 2, 0, None))))


def K_de_u(u, s):
    c = C_de_u(u, s); return u / c if c > 1e-9 else np.inf


def estado(u, s):
    a = np.arcsin(np.clip(DW / u, -1, 1)); return np.where(s > 0, a, np.pi - a)


def autovalores(th, K):
    J = (K / N) * np.cos(th[None, :] - th[:, None]); np.fill_diagonal(J, 0.0); np.fill_diagonal(J, -J.sum(1))
    ev = np.sort(np.linalg.eigvals(J).real)
    i0 = int(np.argmin(np.abs(ev))); return np.delete(ev, i0)          # tira o nulo da fase global


def raizes(s, Kalvo, us):
    Ks = np.array([K_de_u(u, s) for u in us]); out = []
    for i in range(len(us) - 1):
        a, b = Ks[i] - Kalvo, Ks[i + 1] - Kalvo
        if np.isfinite(a) and np.isfinite(b) and a * b < 0:
            out.append(brentq(lambda u: K_de_u(u, s) - Kalvo, us[i], us[i + 1]))
    return out


# ---------------------------------------------------------------- média no tempo
def media_C(Ks, th0, D, rng, T=3000, ini=1000):
    th = th0.copy(); acc = np.zeros(len(th))
    for t in range(T):
        z = np.exp(1j * th).mean(1); C = np.abs(z); psi = np.angle(z)
        th = th + DW + (Ks * C)[:, None] * np.sin(psi[:, None] - th)
        if D > 0: th = th + rng.normal(size=th.shape) * np.sqrt(2 * D)
        if t >= ini: acc += np.abs(np.exp(1j * th).mean(1))
    return acc / (T - ini)


def main():
    assert (ROOT / "PREDICAO_teste40_ramos_do_disco.md").exists(), "sem predição, sem teste"
    res = {"Kc_mrad": KC * 1e3, "max_abs_dw_mrad": MX * 1e3, "dw_mrad": (DW * 1e3).round(3).tolist()}
    us = MX * (1 + np.logspace(-6, 1.5, 4000))
    smais = np.ones(N)
    Kp = np.array([K_de_u(u, smais) for u in us]); iL = int(np.argmin(Kp))
    KL, uL = Kp[iL], us[iL]; CL = C_de_u(uL, smais)
    res["K_L_sobre_Kc"] = KL / KC; res["C_L"] = CL; res["u_L_sobre_max_dw"] = uL / MX
    res["ramo_positivo_amostra"] = [[round(K_de_u(u, smais) / KC, 4), round(C_de_u(u, smais), 4)] for u in us[::200]]

    # J2: estabilidade em cada K ≥ K_L da grade
    j2_ok = True; tab = []
    for k in KGRADE:
        K = k * KC
        if K < KL: continue
        rp = raizes(smais, K, us)
        linha = {"K": float(k), "positivo": []}
        for u in rp:
            ev = autovalores(estado(u, smais), K); linha["positivo"].append({"C": C_de_u(u, smais), "max_autovalor": float(ev.max())})
        if linha["positivo"]:
            alto = max(linha["positivo"], key=lambda d: d["C"])
            if alto["max_autovalor"] >= 0: j2_ok = False
        selas = []
        for k_neg in range(N):
            s = smais.copy(); s[k_neg] = -1
            for u in raizes(s, K, us):
                ev = autovalores(estado(u, s), K); selas.append({"anel": k_neg, "C": C_de_u(u, s), "max_autovalor": float(ev.max())})
                if ev.max() <= 0: j2_ok = False
        linha["selas"] = selas; tab.append(linha)
    res["estabilidade"] = tab

    # médias no tempo
    rng = np.random.default_rng(40); Ks = KGRADE * KC; nK = len(KGRADE)
    th_coh = np.tile(T37.SIG0 * rng.normal(size=N), (nK, 1))
    sorteios = rng.uniform(0, 2 * np.pi, (20, N))
    Cc = media_C(Ks, th_coh, 0.0, rng)
    Cr = np.mean([media_C(Ks, np.tile(s0, (nK, 1)), 0.0, rng) for s0 in sorteios], axis=0)
    Ccn = np.mean([media_C(Ks, np.tile(T37.SIG0 * rng.normal(size=N), (nK, 1)), T37.D, rng) for _ in range(20)], axis=0)
    Crn = np.mean([media_C(Ks, np.tile(rng.uniform(0, 2 * np.pi, N), (nK, 1)), T37.D, rng) for _ in range(20)], axis=0)
    na = lambda c: (c >= FAIXA[0]) & (c <= FAIXA[1])
    larg = float(np.sum(na(Cc)) * 0.01); larg_n = float(np.sum(na(Ccn)) * 0.01)
    hist = float(np.max(np.abs(Cc - Cr)))
    res["curvas"] = {"K": KGRADE.tolist(), "coerente": Cc.round(4).tolist(), "sorteado": Cr.round(4).tolist(),
                     "coerente_ruido": Ccn.round(4).tolist(), "sorteado_ruido": Crn.round(4).tolist()}
    res["janela"] = {"largura_sem_ruido": larg, "K_na_faixa_sem_ruido": KGRADE[na(Cc)].tolist(),
                     "largura_com_ruido": larg_n, "K_na_faixa_com_ruido": KGRADE[na(Ccn)].tolist()}
    res["histerese_max"] = hist; res["K_da_histerese_max"] = float(KGRADE[int(np.argmax(np.abs(Cc - Cr)))])
    J = {"J1": CL >= 0.70, "J2": j2_ok, "J3": larg < 0.10, "J4": hist > 0.2}
    res["J"] = {k: bool(v) for k, v in J.items()}

    print(f"K_c {KC*1e3:.2f} mrad/Myr | max|Δω| {MX*1e3:.2f} | K_L/K_c {KL/KC:.4f} | C_L {CL:.4f} | u_L/max|Δω| {uL/MX:.4f}")
    for l in tab[:4] + tab[-2:]:
        print(f"  K/K_c {l['K']:.2f}: positivo " + ", ".join(f"C {d['C']:.3f} λmax {d['max_autovalor']:+.2e}" for d in l["positivo"])
              + f" | selas {len(l['selas'])}, λmax mín {min([d['max_autovalor'] for d in l['selas']], default=float('nan')):+.2e}")
    for k in [0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0, 1.02, 1.05, 1.1, 1.2, 1.4, 1.6]:
        i = int(np.argmin(np.abs(KGRADE - k)))
        print(f"  K/K_c {k:.2f}: C̄ coerente {Cc[i]:.3f} sorteado {Cr[i]:.3f} | com ruído {Ccn[i]:.3f} / {Crn[i]:.3f}")
    print(f"janela sem ruído {larg:.2f} K_c em {res['janela']['K_na_faixa_sem_ruido']} | com ruído {larg_n:.2f} K_c | histerese máx {hist:.3f} em K/K_c {res['K_da_histerese_max']}")
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in J.items()))
    (ROOT / "resultados_teste40.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
