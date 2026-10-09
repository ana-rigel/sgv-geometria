"""L2 — calibração sintética (PREREGISTRO_L2.md, seção 6.1). Não usa dado real.

Para cada escala (tamanho da série igual ao do confirmatório):
  - SF1 estacionário: o teste NÃO pode rejeitar (semente 0 é a checagem registrada;
    as demais estimam a taxa de falso positivo);
  - SF1 com regime plantado (impacto e persistência do fluxo mudam ANTES da
    volatilidade): o teste DEVE rejeitar (semente 0 registrada; demais estimam o poder).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from common import Timer, save_json
from sgvgeo.l2 import evaluations, run_primary, simulate_planted

ESCALAS = {
    "1m": {"W": 1440, "S": 60, "n_eval": 1464, "step_ms": 60_000, "season": "hora"},
    "1h": {"W": 1008, "S": 24, "n_eval": 610, "step_ms": 3_600_000, "season": "dia"},
}
NU = 4.0  # ν verdadeiro do gerador sintético
K_NULL = int(os.environ.get("L2_K_NULL", 20))
K_ALT = int(os.environ.get("L2_K_ALT", 10))
ALPHA = 0.025


def one(cfg, seed, planted):
    n = cfg["n_eval"] * cfg["S"] + cfg["W"] + 2 * cfg["S"] + 61
    df = simulate_planted(n, seed=seed, S=cfg["S"], step_ms=cfg["step_ms"], planted=planted)
    ev = evaluations(df, cfg["W"], cfg["S"], NU)
    return run_primary(ev, cfg["W"], cfg["S"], cfg["season"], seed=seed)


def main():
    res = {}
    for esc, cfg in ESCALAS.items():
        with Timer() as t:
            nul = [one(cfg, s, False) for s in range(K_NULL)]
            alt = [one(cfg, s, True) for s in range(K_ALT)]
        pn = np.array([r["p_unilateral"] for r in nul])
        pa = np.array([r["p_unilateral"] for r in alt])
        res[esc] = {
            "checagem_registrada": {
                "estacionario_semente0": nul[0], "estacionario_passa": nul[0]["p_unilateral"] > ALPHA,
                "plantado_semente0": alt[0], "plantado_passa": alt[0]["p_unilateral"] <= ALPHA},
            "taxa_falso_positivo": float((pn <= ALPHA).mean()), "k_nulo": K_NULL,
            "poder": float((pa <= ALPHA).mean()), "k_alt": K_ALT,
            "rho_medio_nulo": float(np.mean([r["rho_parcial"] for r in nul])),
            "rho_medio_alt": float(np.mean([r["rho_parcial"] for r in alt])),
            "n_avaliacoes": nul[0]["n"], "tempo_s": round(t.dt, 1)}
        print(esc, pd.Series({k: v for k, v in res[esc].items() if k != "checagem_registrada"}).to_string())
        print("  registrada:", {k: (v if isinstance(v, bool) else round(v["p_unilateral"], 4))
                                for k, v in res[esc]["checagem_registrada"].items()})
    save_json("l2_calibracao.json", res)


if __name__ == "__main__":
    main()
