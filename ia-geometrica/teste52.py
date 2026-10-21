"""Teste 52: o erro contra o mundo. Relógios por andar (os do teste 51) com frequência adaptativa pelo torque da forçante,
ω_j ← ω_j − η_w s_j sen φ_j, η_w = ε/365; braço A desacoplado (K = 0), braço B acoplado (K = 0,1); silêncio a partir de
2018; nulo sem estações. Predição: PREDICAO_teste52_erro_contra_o_mundo.md (commit c4cac8c), escrita antes deste arquivo.

    python ia-geometrica/teste52.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste35 as T35
import teste51 as T51

ROOT = Path(__file__).resolve().parent
OM, LAM, EPS = T51.OM, T51.LAM, T51.EPS
ETAW, KB, NIC, SEMENTE = EPS / 365, 0.1, 20, 51


def simular(s, ano, K, etaw, ph0, silencio=True):
    """Devolve ω ao fim de 2017 (nIC, 4), frequência realizada média em 2018–2025 (nIC, 4) e o 1º dia em que a mediana
    de ω₂ entra e fica em ±5 % de Ω até o fim de 2017."""
    i18 = int(np.argmax(ano >= 2018)); T = len(ano)
    ph = ph0.copy(); w = np.broadcast_to(LAM, ph.shape).copy(); acc = np.zeros_like(ph); w17 = None; dentro = np.zeros(i18, bool)
    for i in range(T):
        si = s[:, i] if (not silencio or i < i18) else 0.0 * s[:, i]
        Z = np.exp(1j * ph).mean(-1, keepdims=True); tq = -si * np.sin(ph)
        d = w + EPS * tq + K * np.imag(Z * np.exp(-1j * ph))
        w = w + etaw * tq; ph = ph + d
        if i < i18: dentro[i] = abs(np.median(w[:, 1]) - OM) <= 0.05 * OM
        if i == i18 - 1: w17 = w.copy()
        if i >= i18: acc += d
    fora = np.flatnonzero(~dentro)
    t_apr = None if not dentro[-1] else int(fora[-1] + 1 if len(fora) else 0)
    return w17, acc / (T - i18), t_apr


def piloto(ph0):
    """O mundo sintético da predição (A_j, δ_j e desvio do resíduo de Juara na calibração; ruído AR(1) por andar)."""
    t, ano, cal, s = T51.sinais("juara"); a = [T51.anual(t, cal, s[j]) for j in range(4)]
    rng = np.random.default_rng(0); TT = len(t); tt = np.arange(TT); out = {}
    def mundo(com_ano):
        m = []
        for j in range(4):
            A, d = a[j]; sd = np.std(s[j][cal] - A * np.cos(OM * t[cal] + d)); r = np.exp(-LAM[j]); x = 0.0; e = np.zeros(TT)
            for i in range(TT): x = r * x + np.sqrt(1 - r * r) * rng.normal(); e[i] = x
            m.append((A * np.cos(OM * tt + d) if com_ano else 0.0) + sd * e)
        return np.array(m)
    for nome, ca in (("com_ano", True), ("sem_ano", False)):
        S = mundo(ca)
        for K in (0.0, KB):
            w17, fs, _ = simular(S, ano, K, ETAW, ph0)
            out[f"{nome}_K{K}"] = {"w_fim_2017_sobre_Omega": (np.median(w17, 0) / OM).round(3).tolist(),
                                   "periodo_silencio": (2 * np.pi / np.median(fs, 0)).round(1).tolist()}
    return out


def main():
    assert (ROOT / "PREDICAO_teste52_erro_contra_o_mundo.md").exists(), "sem predição, sem teste"
    ph0 = np.random.default_rng(SEMENTE).uniform(0, 2 * np.pi, (NIC, 4))
    res = {"piloto_sintetico": piloto(ph0), "lugares": {}}
    print("piloto:", json.dumps(res["piloto_sintetico"], ensure_ascii=False), flush=True)
    for n in T35.LUGARES:
        t, ano, cal, s = T51.sinais(n); tn, anon, caln, sn = T51.sinais(n, nulo=True); o = {}
        for braco, K in (("A", 0.0), ("B", KB)):
            w17, fs, tap = simular(s, ano, K, ETAW, ph0)
            w17c, fsc, _ = simular(s, ano, K, 0.0, ph0)
            w17n, fsn, _ = simular(sn, anon, K, ETAW, ph0)
            o[braco] = {"w_fim_2017_sobre_Omega": (np.median(w17, 0) / OM).tolist(),
                        "periodo_silencio": (2 * np.pi / np.median(fs, 0)).tolist(),
                        "periodo_silencio_controle": (2 * np.pi / np.median(fsc, 0)).tolist(),
                        "w_fim_2017_nulo_sobre_Omega": (np.median(w17n, 0) / OM).tolist(),
                        "periodo_silencio_nulo": (2 * np.pi / np.median(fsn, 0)).tolist(),
                        "dias_ate_aprender_andar2": tap,
                        "deriva_silencio_dias_por_ano": float((np.median(fs, 0)[1] - OM) / OM * 365.25)}
            print(f"{n:16s} {braco}: ω/Ω fim17 {np.round(o[braco]['w_fim_2017_sobre_Omega'], 3)} | P₂ silêncio {o[braco]['periodo_silencio'][1]:.1f}"
                  f" (controle {o[braco]['periodo_silencio_controle'][1]:.1f}; nulo {o[braco]['periodo_silencio_nulo'][1]:.1f}) | nulo ω₂/Ω "
                  f"{o[braco]['w_fim_2017_nulo_sobre_Omega'][1]:.3f} | aprende em {tap} d", flush=True)
        res["lugares"][n] = o
    L = list(res["lugares"].values()); dentro = lambda x, tol: abs(x - 1) <= tol
    j1 = sum(dentro(o["A"]["w_fim_2017_sobre_Omega"][1], 0.05) for o in L) >= 5
    J = {"J1": j1,
         "J2": sum(all(abs(o["A"]["w_fim_2017_sobre_Omega"][k] - 1) > 0.5 for k in (0, 2, 3)) for o in L) >= 5,
         "J3": sum(dentro(o["A"]["periodo_silencio"][1] / 365.25, 0.05) for o in L) >= 5
               and sum(not dentro(o["A"]["periodo_silencio_controle"][1] / 365.25, 0.05) for o in L) >= 5,
         "J4": j1 and sum(not dentro(o["A"]["w_fim_2017_nulo_sobre_Omega"][1], 0.10) for o in L) >= 5,
         "J5": sum(dentro(o["B"]["periodo_silencio"][1] / 365.25, 0.05) and not dentro(o["B"]["periodo_silencio_nulo"][1] / 365.25, 0.10)
                   for o in L) >= 5}
    res["J"] = {k: bool(v) for k, v in J.items()}
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste52.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
