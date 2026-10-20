"""Teste 36b (adendo ao 36): no mundo real, as previsões do relógio que aprende (μ ← μ + 0,3 e) erram menos que o calendário
fixo (μ₀ = média de 2010–2017)? Predição: PREDICAO_teste36b_previsao_real.md. Dados: resultados_teste36.json (sem rodar o laço de novo).

    python ia-geometrica/teste36b.py
"""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
ANOS = list(range(2018, 2026)); USA = slice(1, None)          # 2019–2025: em 2018 a previsão do relógio é o próprio μ₀


def main():
    assert (ROOT / "PREDICAO_teste36b_previsao_real.md").exists(), "sem predição, sem teste"
    real = json.loads((ROOT / "resultados_teste36.json").read_text())["real"]; lugares = list(real)
    E = np.array([np.array(real[n]["entradas"])[USA] - np.array(real[n]["previsoes"])[USA] for n in lugares])   # relógio
    C = np.array([np.array(real[n]["entradas"])[USA] - real[n]["mu0"] for n in lugares])                       # calendário
    anos = ANOS[USA]
    dif = np.abs(E).mean() - np.abs(C).mean()
    rng = np.random.default_rng(361); B = []
    for _ in range(10000):
        j = rng.integers(0, len(anos), len(anos)); B.append(np.abs(E[:, j]).mean() - np.abs(C[:, j]).mean())
    ic = [float(np.quantile(B, .025)), float(np.quantile(B, .975))]
    por_lugar = {n: {"EAM_relogio": float(np.abs(E[i]).mean()), "EAM_calendario": float(np.abs(C[i]).mean()),
                     "vies_relogio": float(E[i].mean()), "vies_calendario": float(C[i].mean())} for i, n in enumerate(lugares)}
    por_ano = {a: float((np.abs(E[:, k]) - np.abs(C[:, k])).mean()) for k, a in enumerate(anos)}
    j1 = bool(dif <= -2 and ic[1] < 0); n2 = sum(v["EAM_relogio"] < v["EAM_calendario"] for v in por_lugar.values()); j2 = n2 >= 4
    res = {"EAM_relogio": float(np.abs(E).mean()), "EAM_calendario": float(np.abs(C).mean()), "dif": float(dif), "ic_dif": ic,
           "vies_relogio": float(E.mean()), "vies_calendario": float(C.mean()), "por_lugar": por_lugar, "dif_por_ano": por_ano,
           "J1": j1, "J2": {"lugares": int(n2), "passa": bool(j2)}}
    for n, v in por_lugar.items():
        print(f"  {n:16s} EAM relógio {v['EAM_relogio']:5.1f} · calendário {v['EAM_calendario']:5.1f} | viés {v['vies_relogio']:+5.1f} · {v['vies_calendario']:+5.1f}")
    print("  por ano (relógio − calendário, média |erro|): " + " ".join(f"{a}:{d:+.1f}" for a, d in por_ano.items()))
    print(f"== EAM {res['EAM_relogio']:.1f} contra {res['EAM_calendario']:.1f}: dif {dif:+.1f} d (IC {ic[0]:+.1f}; {ic[1]:+.1f}) → J1 {'PASSA' if j1 else 'REPROVA'}"
          f" | J2 {n2}/6 → {'PASSA' if j2 else 'REPROVA'} | viés {res['vies_relogio']:+.1f} contra {res['vies_calendario']:+.1f}")
    (ROOT / "resultados_teste36b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
