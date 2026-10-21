"""Teste 53: a entrada das águas lida na fase do relógio do andar 2 (teste 52, braço A), com a fase esperada ψ aprendida
pelo laço do relógio v1 (teste 36). Comparada com o calendário fixo e o v1 do 36b, nas mesmas 42 previsões (2019–2025).
Predição: PREDICAO_teste53_entrada_pela_fase.md (commit f22bd33), escrita antes deste arquivo.

    python ia-geometrica/teste53.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste35 as T35
import teste51 as T51
import teste52 as T52

ROOT = Path(__file__).resolve().parent
OM, EPS, ETAW, ETA = T51.OM, T51.EPS, T52.ETAW, 0.3
ANOS = list(range(2018, 2026)); AVAL = ANOS[1:]; NBOOT, SEMENTE = 10000, 53
emb = lambda x: (x + np.pi) % (2 * np.pi) - np.pi


def relogio2(s2, ano, ph0, silencio):
    """Só o andar 2 (com K = 0 os andares são independentes): fase contínua e ω por dia, para cada início."""
    i18 = int(np.argmax(ano >= 2018)); T = len(ano)
    ph = ph0.copy(); w = np.full_like(ph, T51.LAM[1]); PH = np.zeros((T, len(ph))); W = np.zeros_like(PH)
    for i in range(T):
        si = 0.0 if (silencio and i >= i18) else s2[i]
        tq = -si * np.sin(ph); d = w + EPS * tq; w = w + ETAW * tq; ph = ph + d
        PH[i], W[i] = ph, w
    return PH, W


def previsoes_fase(PH, W, t, idx, ent, aprende):
    """Por início: ψ₀ = média circular de φ₂ nas entradas de 2010–2017; a cada ano de 2018 a 2025, previsão em 1/09 e depois
    (se aprende) ψ ← ψ + η emb(φ₂(entrada) − ψ). Devolve a previsão (dia absoluto) por ano e início."""
    nic = PH.shape[1]; cal = [ent[y] for y in range(2010, 2018) if ent[y] is not None]
    psi = np.angle(np.exp(1j * PH[cal]).mean(0)); out = {}
    for y in ANOS:
        i0 = idx[f"{y}-09-01"]
        out[y] = t[i0] + emb(psi - PH[i0]) / W[i0]
        if aprende and ent[y] is not None:
            psi = psi + ETA * emb(PH[ent[y]] - psi)
    return out


def main():
    assert (ROOT / "PREDICAO_teste53_entrada_pela_fase.md").exists(), "sem predição, sem teste"
    ph0 = np.random.default_rng(T52.SEMENTE).uniform(0, 2 * np.pi, (T52.NIC, 4))[:, 1]
    r36 = json.loads((ROOT / "resultados_teste36.json").read_text())["real"]
    E = {k: [] for k in ("C", "V1", "F", "F0", "S")}; esp = {k: [] for k in ("F", "F0", "S")}; lugares = T35.LUGARES
    for n in lugares:
        D, P, *_ = T35.ler_juara() if n == "juara" else T35.ler_lugar(n)
        t, ano, cal, s = T51.sinais(n); idx = {d: i for i, d in enumerate(D)}; ent = T35.entradas(D, P)
        assert len(D) == len(t)
        ent_doy = np.array(r36[n]["entradas"]); prev_v1 = np.array(r36[n]["previsoes"]); mu0 = r36[n]["mu0"]
        e_c = (ent_doy - mu0)[1:]; e_v1 = (ent_doy - prev_v1)[1:]
        PHo, Wo = relogio2(s[1], ano, ph0, silencio=False); PHs, Ws = relogio2(s[1], ano, ph0, silencio=True)
        brac = {"F": previsoes_fase(PHo, Wo, t, idx, ent, True), "F0": previsoes_fase(PHo, Wo, t, idx, ent, False),
                "S": previsoes_fase(PHs, Ws, t, idx, ent, True)}
        linha = {"C": e_c, "V1": e_v1}
        for k, pv in brac.items():
            linha[k] = np.array([t[ent[y]] - np.median(pv[y]) for y in AVAL])
            esp[k].append(float(np.mean([np.quantile(pv[y], .9) - np.quantile(pv[y], .1) for y in AVAL])))
        for k in E: E[k].append(np.asarray(linha[k], float))
        print(f"{n:16s} " + " | ".join(f"{k} EAM {np.abs(linha[k]).mean():5.1f} viés {np.mean(linha[k]):+5.1f}" for k in E), flush=True)
    E = {k: np.array(v) for k, v in E.items()}                 # (6 lugares, 7 anos)
    eam = {k: float(np.abs(v).mean()) for k, v in E.items()}; vies = {k: float(v.mean()) for k, v in E.items()}
    rng = np.random.default_rng(SEMENTE); B = []
    for _ in range(NBOOT):
        j = rng.integers(0, len(AVAL), len(AVAL)); B.append(np.abs(E["F0"][:, j]).mean() - np.abs(E["C"][:, j]).mean())
    ic = [float(np.quantile(B, .025)), float(np.quantile(B, .975))]
    J = {"J1": eam["F"] <= eam["V1"] + 1.0, "J2": eam["F0"] - eam["C"] <= -2.0 and ic[1] < 0, "J3": eam["S"] <= eam["V1"] + 3.0}
    res = {"EAM": eam, "vies": vies, "ic_F0_menos_C": ic, "espalhamento_previsoes_p10_p90": {k: float(np.mean(v)) for k, v in esp.items()},
           "por_lugar": {n: {k: {"EAM": float(np.abs(E[k][i]).mean()), "vies": float(E[k][i].mean())} for k in E} for i, n in enumerate(lugares)},
           "dif_por_ano_F_menos_V1": {a: float((np.abs(E["F"][:, j]) - np.abs(E["V1"][:, j])).mean()) for j, a in enumerate(AVAL)},
           "erros": {k: v.round(1).tolist() for k, v in E.items()}, "J": {k: bool(v) for k, v in J.items()}}
    print("EAM " + " · ".join(f"{k} {v:.1f}" for k, v in eam.items()) + " | viés " + " · ".join(f"{k} {v:+.1f}" for k, v in vies.items()))
    print(f"F0 − C: {eam['F0'] - eam['C']:+.1f} d (IC {ic[0]:+.1f}; {ic[1]:+.1f}); espalhamento entre inícios {res['espalhamento_previsoes_p10_p90']}")
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste53.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
