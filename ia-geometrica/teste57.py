"""Teste 57: a hipótese do regime crítico, de novo. O relógio do andar 2 (testes 52–53, braço F do 53) com acoplamento ε
varrido em torno da borda do travamento ε_c = 2|λ₂ − Ω|/A₂: o EAM das águas e o ruído da fase em 1/09 são mínimos perto da
borda? Predição: PREDICAO_teste57_borda_critica.md (commit adf59ee), escrita antes deste arquivo.

    python ia-geometrica/teste57.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste35 as T35
import teste51 as T51
import teste52 as T52
import teste53 as T53

ROOT = Path(__file__).resolve().parent
OM, L2 = T51.OM, T51.LAM[1]
GR = np.array([0.2, 0.3, 0.4, 0.5, 0.7, 1, 1.5, 2, 3, 5, 10])
ANOS, AVAL, ETA_PSI = list(range(2018, 2026)), list(range(2019, 2026)), 0.3
emb = T53.emb


def relogios(s2, eps, ph0):
    """eps: (nG,); ph0: (nIC,). Fase contínua e ω por dia: (T, nG, nIC)."""
    T = len(s2); ph = np.broadcast_to(ph0, (len(eps), len(ph0))).copy(); w = np.full_like(ph, L2)
    e = eps[:, None]; eta = e / 365; PH = np.zeros((T,) + ph.shape); W = np.zeros_like(PH)
    for i in range(T):
        tq = -s2[i] * np.sin(ph); d = w + e * tq; w = w + eta * tq; ph = ph + d; PH[i], W[i] = ph, w
    return PH, W


def piloto57():
    t, ano, cal, s = T51.sinais("juara"); s2 = s[1]; A, dl = T51.anual(t, cal, s2); ec = 2 * abs(L2 - OM) / A
    res = s2[cal] - A * np.cos(OM * t[cal] + dl); TT = len(t); blocos = {y: res[ano[cal] == y] for y in range(2010, 2018)}
    ph0 = np.random.default_rng(51).uniform(0, 2 * np.pi, 20); out = {}
    idx01 = [int(np.argmax((ano == y) & (np.arange(TT) >= np.argmax(ano == y) + 243))) for y in ANOS]
    for modelo in ("AR1", "anos_embaralhados"):
        rng = np.random.default_rng(57); base = A * np.cos(OM * t + dl)
        if modelo == "AR1":
            r = np.exp(-L2); x = 0.0; e = np.zeros(TT)
            for i in range(TT): x = r * x + np.sqrt(1 - r * r) * rng.normal(); e[i] = x
            sig = base + res.std() * e
        else:
            sig = base + np.concatenate([np.resize(blocos[int(rng.integers(2010, 2018))], int((ano == y).sum())) for y in range(2010, 2026)])
        PH, W = relogios(sig, GR * ec, ph0); i17 = int(np.argmax(ano >= 2018)) - 1
        dp = [float(np.std([np.median(emb(PH[k, g] - OM * t[k])) / OM for k in idx01])) for g in range(len(GR))]
        out[modelo] = {"dp_fase": np.round(dp, 1).tolist(), "w2_fim2017": np.round(np.median(W[i17], 1) / OM, 3).tolist()}
    return out


def main():
    assert (ROOT / "PREDICAO_teste57_borda_critica.md").exists(), "sem predição, sem teste"
    res = {"grade_eps_sobre_eps_c": GR.tolist(), "piloto": piloto57(), "lugares": {}}
    print("piloto:", json.dumps(res["piloto"]), flush=True)
    ph0 = np.random.default_rng(T52.SEMENTE).uniform(0, 2 * np.pi, (T52.NIC, 4))[:, 1]
    ERR = []; DP = []
    for n in T35.LUGARES:
        D, P, *_ = T35.ler_juara() if n == "juara" else T35.ler_lugar(n)
        t, ano, cal, s = T51.sinais(n); idx = {d: i for i, d in enumerate(D)}; ent = T35.entradas(D, P)
        A, _ = T51.anual(t, cal, s[1]); ec = 2 * abs(L2 - OM) / A
        PH, W = relogios(s[1], GR * ec, ph0); i17 = int(np.argmax(ano >= 2018)) - 1
        erros, dps = [], []
        for g in range(len(GR)):
            pv = T53.previsoes_fase(PH[:, g], W[:, g], t, idx, ent, True)
            erros.append([float(t[ent[y]] - np.median(pv[y])) for y in AVAL])
            an = [np.median(emb(PH[idx[f"{y}-09-01"], g] - OM * t[idx[f"{y}-09-01"]])) / OM for y in ANOS]
            dps.append(float(np.std(an)))
        ERR.append(erros); DP.append(dps)
        res["lugares"][n] = {"A2": float(A), "eps_c": float(ec), "EAM": [float(np.mean(np.abs(e))) for e in erros], "dp_fase": dps,
                             "w2_fim2017": (np.median(W[i17], 1) / OM).tolist()}
        print(f"{n:16s} ε_c {ec:.5f} | EAM " + " ".join(f"{g}:{v:.0f}" for g, v in zip(GR, res['lugares'][n]['EAM']))
              + " | dp " + " ".join(f"{v:.0f}" for v in dps), flush=True)
    ERR = np.array(ERR); DP = np.array(DP)                 # (6, nG, 7), (6, nG)
    eam = np.abs(ERR).mean(axis=(0, 2)); dpm = np.median(DP, 0)
    gs = int(np.argmin(eam)); gd = int(np.argmin(dpm)); i1 = int(np.where(GR == 1)[0][0])
    J = {"J1": 0.5 <= GR[gs] <= 2, "J2": eam[gs] <= min(eam[0], eam[-1]) - 5, "J3": 0.5 <= GR[gd] <= 2, "J4": eam[i1] <= 20.0}
    res.update({"EAM_total": eam.tolist(), "dp_fase_mediana": dpm.tolist(), "eps_otimo_EAM": float(GR[gs]), "eps_otimo_dp": float(GR[gd]),
                "EAM_em_2eps_c": float(eam[int(np.where(GR == 2)[0][0])]), "J": {k: bool(v) for k, v in J.items()}})
    print("EAM total " + " ".join(f"{g}:{v:.1f}" for g, v in zip(GR, eam)))
    print("dp fase   " + " ".join(f"{g}:{v:.0f}" for g, v in zip(GR, dpm)))
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste57.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
