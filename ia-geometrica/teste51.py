"""Teste 51: andares com ritmo. Cada andar da v0 ganha um relógio de fase (frequência natural = λ_j, a de corte do próprio
registro) que escuta o seu registro e os outros relógios e corrige a frequência pelo erro (regra do teste 36). A teoria da
janela (autoconsistência do teste 46 com forçante) prevê quem trava no ano; o aprendizado guarda o ano no silêncio?
Predição: PREDICAO_teste51_andares_com_ritmo.md (commit 8d9b5c5), escrita antes deste arquivo.

    python ia-geometrica/teste51.py        # o teste (exige a predição)
"""
import json, sys
from datetime import date
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste35 as T35

ROOT = Path(__file__).resolve().parent
LAM = 0.15 * 10.0 ** -np.arange(4); OM = 2 * np.pi / 365.25; EPS = 0.01; ETA = 1 / 365; KB = 0.1
KS = np.array([0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 0.8])
NIC, SEMENTE = 20, 51


# ---------------------------------------------------------------- o mundo e a cascata da v0
def climatologia(v, doy, cal):
    m = np.array([v[cal & (doy == k)].mean() for k in range(1, 366)])
    sm = np.convolve(np.concatenate([m[-15:], m, m[:15]]), np.ones(31) / 31, "valid")
    return sm[doy - 1]


def sinais(n, nulo=False):
    D, P, E, S, V = T35.ler_juara() if n == "juara" else T35.ler_lugar(n)
    ano = np.array([int(d[:4]) for d in D]); cal = (ano >= 2010) & (ano <= 2017)
    doy = np.array([min(date.fromisoformat(d).timetuple().tm_yday, 365) for d in D])
    t = np.array([np.datetime64(d, "D").astype(int) for d in D], float)
    bal = np.convolve(P - E, np.ones(7) / 7)[:len(P)]
    brutas = [S, bal, V]
    if nulo: brutas = [v - climatologia(v, doy, cal) for v in brutas]
    z = lambda v: (v - v[cal].mean()) / v[cal].std()
    x = np.column_stack([z(v) for v in brutas])
    R = np.zeros((4,) + x.shape); r = np.zeros((4, 3))
    for i in range(len(x)):
        r[0] += LAM[0] * (x[i] - r[0])
        for j in range(1, 4): r[j] += LAM[j] * (r[j - 1] - r[j])
        R[:, i] = r
    w, v = np.linalg.eigh(np.cov(R[0][cal].T)); u = v[:, -1]; sd = (R[0][cal] @ u).std()
    return t, ano, cal, np.array([R[j] @ u / sd for j in range(4)])


# ---------------------------------------------------------------- a teoria (sem simular)
def anual(t, cal, sj):
    X = np.column_stack([np.ones(cal.sum()), np.cos(OM * t[cal]), np.sin(OM * t[cal])])
    c = np.linalg.lstsq(X, sj[cal], rcond=None)[0]
    return float(np.hypot(c[1], c[2])), float(np.arctan2(-c[2], c[1]))


def teoria(F, dl, K, w=LAM, it=2000):
    dw = w - OM; Z = np.exp(1j * dl[1])
    for _ in range(it):
        H = F * np.exp(1j * dl) + K * Z; x = dw / np.maximum(np.abs(H), 1e-12)
        ph = np.where(np.abs(x) <= 1, np.sqrt(np.clip(1 - x * x, 0, None)) + 1j * x,
                      1j * (x - np.sign(x) * np.sqrt(np.maximum(x * x - 1, 0))))
        Zn = np.mean(ph * np.exp(1j * np.angle(H)))
        if abs(Zn - Z) < 1e-12: break
        Z = 0.5 * Z + 0.5 * Zn
    return np.abs(x) <= 1, Z


# ---------------------------------------------------------------- os relógios
def simular(s, K, eta, ph0, ate=None, janelas=()):
    """s: (4, T); K: (nK,); ph0: (nIC, 4). Fase e frequência por (K, IC, andar). Silêncio (s = 0) a partir de `ate`.
    Devolve, por janela (i0, i1), a frequência média realizada, e a frequência ω no fim de cada janela."""
    nK = len(K); phi = np.broadcast_to(ph0, (nK,) + ph0.shape).copy(); w = np.broadcast_to(LAM, phi.shape).copy()
    Kc = K[:, None, None]; T = s.shape[1]; soma = {j: np.zeros_like(phi) for j in range(len(janelas))}; wfim = {}
    for i in range(T):
        si = s[:, i] if (ate is None or i < ate) else 0.0 * s[:, i]
        Z = np.exp(1j * phi).mean(-1, keepdims=True)
        d = w - EPS * si * np.sin(phi) + Kc * np.imag(Z * np.exp(-1j * phi))
        phi += d
        if eta: w += eta * (d - w)
        for j, (a, b) in enumerate(janelas):
            if a <= i < b: soma[j] += d
            if i == b - 1: wfim[j] = w.copy()
    return {j: soma[j] / (b - a) for j, (a, b) in enumerate(janelas)}, wfim


def main():
    assert (ROOT / "PREDICAO_teste51_andares_com_ritmo.md").exists(), "sem predição, sem teste"
    rng = np.random.default_rng(SEMENTE); ph0 = rng.uniform(0, 2 * np.pi, (NIC, 4))
    res = {"lugares": {}}; acordo = []
    for n in T35.LUGARES:
        t, ano, cal, s = sinais(n); a = [anual(t, cal, s[j]) for j in range(4)]
        F = np.array([EPS * x[0] / 2 for x in a]); dl = np.array([x[1] for x in a])
        teo = {float(K): teoria(F, dl, K)[0] for K in KS}
        i12 = int(np.argmax(ano >= 2012)); i18 = int(np.argmax(ano >= 2018)); T = len(ano)
        # J1: sem aprendizado, mundo com estações
        fr, _ = simular(s, KS, 0.0, ph0, janelas=[(i12, T)])
        trav = np.abs(fr[0] - OM) <= 0.03 * OM                                  # (nK, nIC, 4)
        maioria = trav.mean(1) > 0.5
        iguais = [bool(np.all(maioria[k] == teo[float(K)])) for k, K in enumerate(KS)]; acordo += iguais
        # J2, J3: aprendizado em K_B; silêncio a partir de 2018; controle sem aprendizado
        L = {}
        for nome, eta in (("aprende", ETA), ("controle", 0.0)):
            fr2, wf = simular(s, np.array([KB]), eta, ph0, ate=i18, janelas=[(int(np.argmax(ano >= 2010)), i18), (i18, T)])
            L[nome] = {"w_fim_2017_mediana": np.median(wf[0][0], 0).tolist(),
                       "periodo_silencio_andar2_mediana": float(np.median(2 * np.pi / fr2[1][0][:, 1])),
                       "periodos_silencio_por_andar": np.median(2 * np.pi / fr2[1][0], 0).tolist(),
                       "deriva_dias_por_ano": float((np.median(fr2[1][0][:, 1]) - OM) / OM * 365.25)}
        # recrutamento do andar 1 (ano em que ω₁ entra em ±5 % de Ω), com aprendizado
        rec = None
        for y in range(2010, 2018):
            iy = int(np.argmax(ano >= y + 1)) if y < 2017 else i18
            _, wf = simular(s[:, :iy], np.array([KB]), ETA, ph0, janelas=[(0, iy)])
            if abs(np.median(wf[0][0][:, 0]) - OM) <= 0.05 * OM: rec = y; break
        # J4: o mundo sem estações
        tn, anon, caln, sn = sinais(n, nulo=True)
        _, wfn = simular(sn, np.array([KB]), ETA, ph0, ate=None, janelas=[(0, int(np.argmax(anon >= 2018)))])
        per_nulo = float(np.median(2 * np.pi / wfn[0][0][:, 1]))
        res["lugares"][n] = {"A": [x[0] for x in a], "delta": [x[1] for x in a],
                             "teoria": {str(K): "".join("1" if l else "·" for l in v) for K, v in teo.items()},
                             "simulado": {str(float(K)): "".join("1" if l else "·" for l in maioria[k]) for k, K in enumerate(KS)},
                             "fracao_travada": {str(float(K)): trav.mean(1)[k].round(2).tolist() for k, K in enumerate(KS)},
                             "acordo": int(sum(iguais)), **L, "ano_recrutamento_andar1": rec, "periodo_nulo_andar2": per_nulo,
                             "w_fim_2017_nulo": np.median(wfn[0][0], 0).tolist()}
        o = res["lugares"][n]
        print(f"{n:16s} acordo {o['acordo']}/15 | aprende: ω/Ω fim 2017 {np.round(np.array(L['aprende']['w_fim_2017_mediana']) / OM, 3)} "
              f"silêncio P₂ {L['aprende']['periodo_silencio_andar2_mediana']:.1f} d | controle P₂ {L['controle']['periodo_silencio_andar2_mediana']:.1f} d"
              f" | andar 1 recrutado em {rec} | nulo P₂ {per_nulo:.1f} d", flush=True)
        print("   teoria  " + " ".join(f"{K}:{v}" for K, v in o["teoria"].items()))
        print("   simul.  " + " ".join(f"{K}:{v}" for K, v in o["simulado"].items()), flush=True)
    lg = res["lugares"].values()
    J = {"J1": float(np.mean(acordo)) >= 0.85,
         "J2": sum(all(abs(w - OM) <= 0.05 * OM for w in o["aprende"]["w_fim_2017_mediana"]) for o in lg) >= 5,
         "J3": sum(abs(o["aprende"]["periodo_silencio_andar2_mediana"] - 365.25) <= 0.05 * 365.25 for o in lg) >= 5
               and sum(abs(o["controle"]["periodo_silencio_andar2_mediana"] - 365.25) > 0.05 * 365.25 for o in lg) >= 5,
         "J4": sum(abs(o["periodo_nulo_andar2"] - 365.25) > 0.10 * 365.25 for o in lg) >= 5}
    res["acordo_total"] = float(np.mean(acordo)); res["J"] = {k: bool(v) for k, v in J.items()}
    print(f"acordo teoria × simulação: {np.mean(acordo):.3f}")
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste51.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
