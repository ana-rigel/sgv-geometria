"""Teste 48 (investigação 3): a janela de sincronização parcial com a rotação observada da NGC 628 (Aniyan et al. 2018,
Figura 13, extraída dos vetores do PDF), com a inclinação fixa (como publicado) e variando dentro das incertezas.
Teoria contínua do teste 47. Predição: PREDICAO_teste48_rotacao_observada.md (commit c908b25).

    python ia-geometrica/teste48.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste47 as T47
import teste46 as T46

ROOT = Path(__file__).resolve().parent
T47.NU = 800; T47.KGF = np.round(np.arange(0.55, 1.40001, 0.0005), 4)
R0, R1, NQ, NREAL, I_FIX = 254.0, 350.0, 300, 300, 8.5


def dados():
    f = json.loads((ROOT / "ngc628" / "aniyan2018_fig13.json").read_text())
    inc = np.array([p for p in f["incl_preto"] if 250 <= p[0] <= 351], float)
    v = np.array([p[:2] for p in f["rot_preto"] if 250 <= p[0] <= 351], float)
    red = dict((round(a), b) for a, b in f["rot_vermelho"]); blue = dict((round(a), b) for a, b in f["rot_azul"])
    sv = np.array([abs(red[round(r)] - blue[round(r)]) / 2 for r in v[:, 0]])
    return inc, v, sv


def janela(rq, vq):
    om = vq / rq; dw = om - om.mean(); dw = dw / (dw.max() - dw.min())
    K, rho, f = T47.ramo(dw); rk, fk = T47.no_K(K, rho, f)
    jan = (fk >= 0.5) & (fk < 1 - 1e-12); trav = fk >= 1 - 1e-12
    if not (jan.any() and trav.any()): return None
    ini, KL = float(T47.KGF[jan][0]), float(T47.KGF[trav][0]); meio = 0.5 * (ini + KL)
    _, _, lk = T46.resolver(dw, meio * T47.KC)
    beta = float(np.polyfit(np.log(rq), np.log(vq), 1)[0])
    rstar = float(rq[lk].min()) if lk is not None and lk.any() else None
    return {"inicio": ini, "K_L": KL, "largura": KL - ini, "beta": beta, "r_estrela_arcsec": rstar,
            "externo_travado": bool(lk is not None and lk[-1]), "interno_desliza": bool(lk is not None and not lk[0])}


def main():
    assert (ROOT / "PREDICAO_teste48_rotacao_observada.md").exists(), "sem predição, sem teste"
    inc, v, sv = dados(); rq = np.linspace(R0, R1, NQ)
    fixo = janela(rq, np.interp(rq, v[:, 0], v[:, 1]))
    fixo["lei_teste47"] = 0.056 * (2 - fixo["beta"]) ** 1.6
    print("inclinação fixa:", fixo, flush=True)
    rng = np.random.default_rng(48); reais = []
    for k in range(NREAL):
        ii = inc[:, 1] + rng.normal(size=len(inc)) * inc[:, 2]; w = 1 / inc[:, 2] ** 2
        A = np.c_[np.ones(len(inc)), inc[:, 0]]; c = np.linalg.solve(A.T @ (A * w[:, None]), A.T @ (w * ii))
        i_s = c[0] + c[1] * rq
        vv = v[:, 1] + rng.normal(size=len(v)) * sv
        vt = np.interp(rq, v[:, 0], vv) * np.sin(np.radians(I_FIX)) / np.sin(np.radians(i_s))
        o = janela(rq, vt)
        if o is not None:
            o["i_254"], o["i_350"] = float(i_s[0]), float(i_s[-1]); reais.append(o)
        if k % 50 == 0: print(f"  {k} realizações", flush=True)
    L = np.array([o["largura"] for o in reais]); B = np.array([o["beta"] for o in reais])
    q = lambda a, p: float(np.quantile(a, p))
    res = {"fixo": fixo, "n_validas": len(reais),
           "largura_q16_q50_q84": [q(L, .16), q(L, .5), q(L, .84)], "beta_q16_q50_q84": [q(B, .16), q(B, .5), q(B, .84)],
           "inicio_q50": q(np.array([o["inicio"] for o in reais]), .5), "K_L_q50": q(np.array([o["K_L"] for o in reais]), .5),
           "r_estrela_q50": q(np.array([o["r_estrela_arcsec"] for o in reais if o["r_estrela_arcsec"]]), .5),
           "i_254_q50": q(np.array([o["i_254"] for o in reais]), .5), "i_350_q50": q(np.array([o["i_350"] for o in reais]), .5),
           "frac_maior_que_fixo": float(np.mean(L > fixo["largura"])),
           "frac_externo_rigido": float(np.mean([o["externo_travado"] and o["interno_desliza"] for o in reais]))}
    J = {"J1": -0.3 <= fixo["beta"] <= 0 and abs(fixo["largura"] - fixo["lei_teste47"]) <= 0.02,
         "J2": res["frac_maior_que_fixo"] >= 0.84,
         "J3": res["largura_q16_q50_q84"][2] / res["largura_q16_q50_q84"][0] >= 1.5,
         "J4": res["frac_externo_rigido"] >= 0.95}
    res["J"] = {k: bool(v) for k, v in J.items()}; res["realizacoes"] = reais
    for k, val in res.items():
        if k not in ("realizacoes", "fixo", "J"): print(k, val)
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste48.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
