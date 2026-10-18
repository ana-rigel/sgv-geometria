"""Teste 15 (ritmo por regime com orçamento de 5 %). Predição: PREDICAO_teste15_orcamento_5.md."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste15_orcamento_5.md").exists(), "sem predição, sem teste"
N, CAL, AFIN, SEEDS, PHI = 8000, 2000, 4000, range(1000, 1100), 0.9
GRID = np.arange(0.05, 1.0, 0.05); ALVO = 0.05; RUPT = 3.0; PQ = range(1, 21); PF = range(10, 121, 2); NULO = 20


def mundo_cachos(n, seed, phi=0.9, amp=12.0, p_fora=1 / 300, p_cacho=1 / 20, dur=30, d=2):
    rng = np.random.default_rng(seed); x = np.zeros((n, d)); e = rng.normal(0, 1, (n, d)); cacho = np.zeros(n, dtype=bool); fim = -1; saltos = []
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
        if t <= fim: cacho[t] = True
        if rng.random() < (p_cacho if t <= fim else p_fora):
            x[t:] += rng.uniform(-amp, amp, d); fim = t + dur; saltos.append(t); cacho[t] = True
    return x, cacho, np.array(saltos)


def lambda_do_mundo(x):
    melhor = None
    for lam in GRID:
        R = np.zeros(2); e = 0.0
        for t in range(CAL): e += np.linalg.norm(x[t] - R); R = R + lam * (x[t] - R)
        if melhor is None or e < melhor[0]: melhor = (e, lam)
    return float(melhor[1])


def calibrar(x, lams):
    obs = V.Observador(2, lams=lams); T0 = np.zeros(CAL)
    for t in range(CAL): T0[t] = np.linalg.norm(x[t] - obs.R[0]); obs.passo(x[t])
    med = np.median(T0); esc = max(np.quantile(np.abs(T0 - med), 0.995) / 3, 1e-12)
    rup = np.where((T0 - med) / esc >= RUPT)[0]; gaps = np.diff(rup); gaps = gaps[gaps < 200]
    H = int(np.clip(np.median(gaps) if len(gaps) else 60, 10, 200))
    return (med, esc), H


def rodar(x, lams, regua, H, politica, pq=None, pf=None, cacho_real=None, ate=None):
    """Laço enxuto: só o andar 1 entra na política e no erro (os andares 2–4 não são lidos aqui); mesma recursão R1 += λ₁(x − R1)."""
    ate = ate or len(x); lam = lams[0]; R = np.zeros(2); med, esc = regua; e = np.zeros(ate); olhou = np.zeros(ate, dtype=bool); prox = 0; fim_cacho = -1
    for t in range(ate):
        d = x[t] - R; e[t] = (d[0] * d[0] + d[1] * d[1]) ** 0.5
        if politica == "sempre": ver = True
        elif politica == "periodico": ver = t % NULO == 0
        else: ver = t >= prox
        if ver:
            olhou[t] = True
            if politica == "ritmo":
                if (e[t] - med) / esc >= RUPT: fim_cacho = t + H
                prox = t + (pq if t <= fim_cacho else pf)
            elif politica == "oraculo": prox = t + (pq if cacho_real[t] else pf)
            R = R + lam * d
    return e, olhou


def afinar(x, lams, regua, H, politica, cacho_real, occ):
    melhor = None
    for pq in PQ:
        for pf in PF:
            if abs(occ / pq + (1 - occ) / pf - ALVO) > 0.015: continue
            e, o = rodar(x, lams, regua, H, politica, pq, pf, cacho_real, ate=AFIN); f = o[CAL:AFIN].mean()
            if abs(f - ALVO) <= 0.005 and (melhor is None or e[CAL:AFIN].mean() < melhor[0]): melhor = (e[CAL:AFIN].mean(), pq, pf)
    return (melhor[1], melhor[2]) if melhor else (NULO, NULO)


def semente(s):
    x, cacho, saltos = mundo_cachos(N, s, PHI); lam1 = lambda_do_mundo(x); lams = lam1 / 10.0 ** np.arange(4); regua, H = calibrar(x, lams)
    occ = float(cacho[CAL:AFIN].mean())
    pq, pf = afinar(x, lams, regua, H, "ritmo", cacho, max(occ, 0.02)); pqo, pfo = afinar(x, lams, regua, H, "oraculo", cacho, max(occ, 0.02))
    e0, o0 = rodar(x, lams, regua, H, "ritmo", pq, pf); eo, oo = rodar(x, lams, regua, H, "oraculo", pqo, pfo, cacho); e1, _ = rodar(x, lams, regua, H, "periodico"); e2, _ = rodar(x, lams, regua, H, "sempre")
    ev0, eor, ep, es = e0[AFIN:].mean(), eo[AFIN:].mean(), e1[AFIN:].mean(), e2[AFIN:].mean(); f = o0[AFIN:].mean(); valido = abs(f - ALVO) <= 0.01
    return s, {"lambda1": lam1, "H": H, "pq": pq, "pf": pf, "pq_orac": pqo, "pf_orac": pfo, "fracao": float(f), "fracao_orac": float(oo[AFIN:].mean()), "valido": bool(valido),
               "saltos_medida": int((saltos >= AFIN).sum()), "ocupacao_cacho_medida": float(cacho[AFIN:].mean()), "e_v0": float(ev0), "e_oraculo": float(eor), "e_periodico": float(ep), "e_sempre": float(es), "V": float(1 - ev0 / ep), "V_orac": float(1 - eor / ep)}


def main():
    from multiprocessing import Pool
    out = {"sementes": {}}
    with Pool(2) as pool:
        for s, r in pool.imap_unordered(semente, list(SEEDS)):
            out["sementes"][str(s)] = r
            if (s - 1000) % 10 == 0: print(f"  s{s}: λ₁ {r['lambda1']:.2f} H {r['H']} ritmo ({r['pq']},{r['pf']}) orac ({r['pq_orac']},{r['pf_orac']}) fração {r['fracao']:.3f} | e v0 {r['e_v0']:.2f} orac {r['e_oraculo']:.2f} per {r['e_periodico']:.2f} sempre {r['e_sempre']:.2f} | V {100*r['V']:+.1f} % orac {100*r['V_orac']:+.1f} %", flush=True)
    S = [out["sementes"][str(s)] for s in SEEDS]; Vs = np.array([r["V"] for r in S]); Vo = np.array([r["V_orac"] for r in S]); ok = np.array([r["valido"] for r in S]); Hs = [r["H"] for r in S]
    pares = [(r["pq"], r["pf"]) for r in S]; Vv = Vs[ok]; a = bool(ok.sum() >= 95); b = bool(Vv.min() > 0) if len(Vv) else False; freq = max(set(pares), key=pares.count)
    out["resumo"] = {"validas": int(ok.sum()), "V_media": float(Vv.mean()), "V_env": [float(Vv.min()), float(Vv.max())], "V_pos": int((Vv > 0).sum()), "V_orac_media": float(Vo.mean()), "V_orac_env": [float(Vo.min()), float(Vo.max())],
                     "par_mais_frequente": list(freq), "H_mediano": float(np.median(Hs)), "e_medios": {k: float(np.mean([r[k] for r in S])) for k in ("e_v0", "e_oraculo", "e_periodico", "e_sempre")},
                     "criterio": {"a_fracao_ok": a, "b_envelope_acima_de_zero": b, "passa": a and b}}
    print(f"\n== teste 15: válidas {ok.sum()} | V média {100*Vv.mean():+.2f} % env ({100*Vv.min():+.1f}; {100*Vv.max():+.1f}) V>0 em {(Vv>0).sum()} | oráculo {100*Vo.mean():+.2f} % env ({100*Vo.min():+.1f}; {100*Vo.max():+.1f}) | par {freq} H mediano {np.median(Hs):.0f} → {'PASSA' if a and b else 'REPROVA'}")
    (ROOT / "resultados_teste15.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
