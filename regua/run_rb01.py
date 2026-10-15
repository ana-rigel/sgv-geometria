"""Execução do RB-01 por família: python -m regua.run_rb01 F0 [F1 ...]  (saída em resultados/rb01/)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

from regua import rb01 as R

CANDS = ("A", "B", "C", "D", "E")
N_REP = 8
N_REFIT = 5
OUT = Path(__file__).resolve().parents[1] / "resultados" / "rb01"


def run_window(cand, x, truth, ev, key):
    try:
        return {"ok": True, **R.measure_window(cand, x, truth, ev, R.rng("mc", cand, *key))}
    except R.Invalid as e:
        return {"ok": False, "motivo": str(e)}
    except (np.linalg.LinAlgError, ValueError) as e:      # falha numérica conta como inválida
        return {"ok": False, "motivo": f"numerico:{e}"[:80]}


def run_family(fam: str) -> dict:
    t0 = time.time()
    S = R.build_family(fam)
    med, esc = S.ruler
    medf, madf = S.ruler_flow
    truth = {"A": R.truth_stats(S.A, (fam, "A"))}
    for case, B in S.cases.items():
        truth[case] = R.truth_stats(B, (fam, case))
    pairs, rel = [], []
    for case, B in S.cases.items():
        for rep in range(N_REP):
            xa = S.A.sample(R.N_WINDOW, R.rng(fam, case, rep, "janA"))
            xb = B.sample(R.N_WINDOW, R.rng(fam, case, rep, "janB"))
            eva = S.A.sample(R.N_TRUE_EVAL, R.rng(fam, case, rep, "evA"))
            evb = B.sample(R.N_TRUE_EVAL, R.rng(fam, case, rep, "evB"))
            rec = {"fam": fam, "case": case, "rep": rep, "cand": {}}
            for c in CANDS:
                rec["cand"][c] = {"A": run_window(c, xa, S.A, eva, (fam, case, rep, "A")),
                                  "B": run_window(c, xb, B, evb, (fam, case, rep, "B"))}
            # régua secundária flow_raw: só a validade do candidato A
            flow = {}
            for side, x in (("A", xa), ("B", xb)):
                xf = (x * esc + med - medf) / madf
                try:
                    flow[side] = R.flow_ruler_vendor_valid(R.GMMModel(xf, 2))
                except Exception as e:  # noqa: BLE001
                    flow[side] = f"numerico:{e}"[:80]
            rec["flow_A_invalid"] = flow
            pairs.append(rec)
            if rep == 0:                       # confiabilidade: 5 reajustes por reamostragem
                for r in range(N_REFIT):
                    ia = R.rng(fam, case, "boot", r, "A").integers(0, len(xa), len(xa))
                    ib = R.rng(fam, case, "boot", r, "B").integers(0, len(xb), len(xb))
                    rr = {"fam": fam, "case": case, "refit": r, "cand": {}}
                    for c in CANDS:
                        rr["cand"][c] = {"A": run_window(c, xa[ia], S.A, eva, (fam, case, "boot", r, "A")),
                                         "B": run_window(c, xb[ib], B, evb, (fam, case, "boot", r, "B"))}
                    rel.append(rr)
        print(f"[{time.time()-t0:6.0f}s] {fam} {case} ok", flush=True)
    return {"fam": fam, "truth": truth, "pairs": pairs, "refits": rel, "segundos": time.time() - t0}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fam in sys.argv[1:]:
        res = run_family(fam)
        (OUT / f"rb01_{fam}.json").write_text(json.dumps(res, separators=(",", ":")))
        print(f"{fam} gravado em {res['segundos']:.0f}s", flush=True)
