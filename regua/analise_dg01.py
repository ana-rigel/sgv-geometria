"""DG-01: ρ(f, referência) por construção, desenho e modo; paridade da A0; leitura combinada do protocolo."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

DIR = Path(__file__).resolve().parents[1] / "resultados" / "dg01"
CONS = ("A0", "B", "C", "D", "E")


def f_e_ref(A, B, c):
    if not A.get(c) or not B.get(c):
        return None
    f = (B[c][1] - A[c][1]) / 3 - (B[c][0] - A[c][0]) / 3
    ref = np.log((B["q999"] / B["med"]) / (A["q999"] / A["med"]))
    return f, ref


def pares(d):
    rel = {int(k): v for k, v in d["relatorio"].items()}
    P_rel = [(rel[k], rel[k + 7]) for k in rel if k + 7 in rel]
    dis = d["disjunto"]
    P_dis = list(zip(dis[0::2], dis[1::2]))
    return {"relatorio": P_rel, "disjunto": P_dis}


def resumo(d):
    out = {}
    for nome, P in pares(d).items():
        out[nome] = {}
        for c in CONS:
            v = [x for x in (f_e_ref(A, B, c) for A, B in P) if x]
            out[nome][c] = {"pares": len(v), "rho": float(spearmanr(*zip(*v))[0]) if len(v) > 5 else float("nan")}
        # concordância de f entre construções (pares válidos em todas)
        comuns = [(A, B) for A, B in P if all(A.get(c) and B.get(c) for c in CONS)]
        fa = [f_e_ref(A, B, "A0")[0] for A, B in comuns]
        out[nome]["concordancia_com_A0"] = {c: float(spearmanr(fa, [f_e_ref(A, B, c)[0] for A, B in comuns])[0])
                                             for c in CONS[1:]} if len(comuns) > 5 else {}
        out[nome]["pares_comuns"] = len(comuns)
    return out


def main():
    res = {m: resumo(json.loads((DIR / f"dg01_{m}.json").read_text())) for m in ("real", "nula")}
    r = res["real"]["relatorio"]
    res["paridade_A0"] = {"relatorio": r["A0"]["rho"], "disjunto": res["real"]["disjunto"]["A0"]["rho"],
                          "confere": abs(r["A0"]["rho"] - 0.638) < 0.01 and abs(res["real"]["disjunto"]["A0"]["rho"] - 0.656) < 0.01}
    cde = [r[c]["rho"] for c in "CDE"]; nul = [res["nula"]["relatorio"][c]["rho"] for c in "CDE"]
    if all(x >= 0.45 for x in cde) and all(x > n for x, n in zip(cde, nul)):
        leitura = "NÃO é artefato do GMM2"
    elif all(x < 0.30 for x in cde):
        leitura = "produto do GMM2"
    else:
        leitura = "ambíguo"
    res["leitura"] = leitura
    (DIR / "julgamento_dg01.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    for m in ("real", "nula"):
        for nome in ("relatorio", "disjunto"):
            v = res[m][nome]
            print(f"{m:5s} {nome:10s} " + "  ".join(f"{c}: ρ={v[c]['rho']:+.3f} (n={v[c]['pares']})" for c in CONS))
            print(f"{'':16s} concordância de f com A0: {v['concordancia_com_A0']} (n={v['pares_comuns']})")
    print("paridade A0:", res["paridade_A0"])
    print("LEITURA:", leitura)


if __name__ == "__main__":
    main()
