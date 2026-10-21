"""Teste 56: ela acompanha o dia na língua dela? A sentinela do teste 55 continua ouvindo depois de declarar; mede-se a
estabilidade da fase do relógio do andar 1 na hora da temperatura máxima de cada dia (R em 30 dias, mediana dos 20 inícios).
Predição: PREDICAO_teste56_acompanha_o_dia.md (commit 77d1bc5), escrita antes deste arquivo.

    python ia-geometrica/teste56.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sentinela55 as S5
import teste55 as T55

ROOT = Path(__file__).resolve().parent
CERTAS = [2010, 2012, 2013, 2016, 2019, 2021, 2023, 2024]; ERRADAS = [2011, 2015, 2018, 2020, 2022]; NAO = [2014, 2017]


def R(ph, horas):
    """ph (T, nIC); horas: índices das máximas -> R por início, mediana."""
    return float(np.median(np.abs(np.exp(1j * ph[horas]).mean(0))))


def main():
    assert (ROOT / "PREDICAO_teste56_acompanha_o_dia.md").exists(), "sem predição, sem teste"
    ph0 = np.random.default_rng(T55.SEMENTE).uniform(0, 2 * np.pi, (T55.NIC, 4))[:, 1]
    r55 = json.loads((ROOT / "resultados_teste55.json").read_text())["instalacoes"]
    tempo, X, _ = T55.ler(); idx = {t: i for i, t in enumerate(tempo)}; res = {"instalacoes": {}}
    for y in range(2010, 2025):
        m = (y - 2010) % 12 + 1; i0 = idx[f"{y}-{m:02d}-01T00:00"]; Xs = X[i0:i0 + T55.H]
        hmax = np.array([d * 24 + int(np.argmax(Xs[d * 24:(d + 1) * 24, 0])) for d in range(365)])
        s = S5.tensoes_online(S5.cascata(S5.normalizar_online(Xs)))
        a = S5.sentinela(s, ph0, T55.EPS, T55.TAU_APR, [T55.ALFA], silencia=False)
        c = S5.sentinela(s, ph0, T55.EPS, T55.TAU_APR, [T55.ALFA], aprende=False, silencia=False)
        dec = a["decl"][0]; dm = np.median(np.where(dec < 0, T55.NUNCA, dec), 0)
        dd = None if dm[0] >= T55.NUNCA else round(float(dm[0]) / 24, 1)
        assert dd == r55[str(y)]["sentinela"]["declaracao_dias_por_andar"][0], (y, dd)     # mesma dinâmica até declarar
        ph, phc = a["PH"][:, 0, :], c["PH"][:, 0, :]
        fim = hmax[335:365]
        o = {"inicio": tempo[i0], "declaracao_dias": dd,
             "R_pos_declaracao": None if dd is None else R(ph, hmax[int(dd) + 1:int(dd) + 31]),
             "R_fim": R(ph, fim), "R_controle_fim": R(phc, fim),
             "R_relogio_24h_fim": float(abs(np.exp(2j * np.pi * (fim % 24) / 24).mean())),
             "w1_fim_sobre_Omega": float(np.median(a["w_fim"][0, :, 0]) / T55.OMD),
             "controle_w1_fim_sobre_Omega": float(np.median(c["w_fim"][0, :, 0]) / T55.OMD),
             "nu1_fim_sobre_Omega": float(np.median(a["NU"][-1, 0]) / T55.OMD),
             "controle_nu1_fim_sobre_Omega": float(np.median(c["NU"][-1, 0]) / T55.OMD)}
        o["grupo"] = "certa" if y in CERTAS else "errada" if y in ERRADAS else "nao_declarou"
        res["instalacoes"][str(y)] = o
        print(f"{y} {o['grupo']:12s} decl {dd} d | R pós-decl {o['R_pos_declaracao'] if dd is None else round(o['R_pos_declaracao'], 2)}"
              f" | R fim {o['R_fim']:.2f} (ν/Ω {o['nu1_fim_sobre_Omega']:.3f}, ω/Ω {o['w1_fim_sobre_Omega']:.3f}) | controle R fim "
              f"{o['R_controle_fim']:.2f} (ν/Ω {o['controle_nu1_fim_sobre_Omega']:.3f}) | teto 24 h {o['R_relogio_24h_fim']:.2f}", flush=True)
    I = res["instalacoes"]
    cont = {"J1": sum(I[str(y)]["R_pos_declaracao"] >= 0.7 for y in CERTAS),
            "J2": sum(I[str(y)]["R_pos_declaracao"] < 0.4 for y in ERRADAS),
            "J3": sum(o["R_fim"] >= 0.7 for o in I.values()),
            "controle_arrastado_fim": sum(o["R_controle_fim"] >= 0.7 for o in I.values())}
    J = {"J1": cont["J1"] >= 7, "J2": cont["J2"] >= 4, "J3": cont["J3"] >= 12}
    res.update({"contagens": cont, "J": {k: bool(v) for k, v in J.items()}})
    print("contagens", cont)
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste56.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
