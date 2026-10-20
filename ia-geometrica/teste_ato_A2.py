"""Teste do ato A2 (o laço do ato com histerese): o órgão do teste do ato A só troca de marca quando a marca atual acumula,
em custo descontado, mais de δ acima da melhor. Mesmos mundos, marcas, h, mudança e controles do ato A.
Predição: PREDICAO_teste_ato_A2.md.

    python ia-geometrica/teste_ato_A2.py --fumaca    # sementes de desenho 5000–5009: escolha de δ pela regra da predição
    python ia-geometrica/teste_ato_A2.py             # o teste (exige a predição)
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sitio as S
import teste_ato_A as A

ROOT = Path(__file__).resolve().parent
DELTAS = (0, 50, 100, 200, 400, 800)


def orgao_h(conds, tcs_aprende, h_horas, L, Ct, ev, delta):
    """O órgão do ato A com histerese: troca da marca atual k para a melhor k* só se W[k] − W[k*] > δ."""
    gam = 0.5 ** (1.0 / h_horas)
    T = np.concatenate([tc[0] for tc in tcs_aprende]); Cc = np.concatenate([tc[1] for tc in tcs_aprende])
    Kx = np.concatenate([np.full(len(tc[0]), k) for k, tc in enumerate(tcs_aprende)])
    o = np.argsort(T, kind="stable"); T, Cc, Kx = T[o], Cc[o], Kx[o]
    C_ = np.array(conds); cand = np.flatnonzero(C_.any(axis=0))
    W = np.zeros(A.K); ult = 0; j = 0; desemp = A.centro() * 1e-9
    atual = int(np.argmin(desemp)); chamadas = []; prot_ate = -1; escolha = []; trocas = 0
    for t in cand:
        if t < prot_ate: continue
        while j < len(T) and T[j] < t:
            W *= gam ** (T[j] - ult); ult = T[j]; W[Kx[j]] += Cc[j]; j += 1
        W *= gam ** (t - ult); ult = t
        k = int(np.argmin(W + desemp))
        if k != atual and W[atual] - W[k] > delta:
            atual = k; trocas += 1
        if C_[atual, t]:
            chamadas.append(t); prot_ate = t + A.P; escolha.append((int(t), atual))
    return A.eventos_de_custo(ev, np.array(chamadas, dtype=int), Ct, L), escolha, trocas


def semente(args):
    s, L, C, mud, hh, deltas = args
    h, z_c, z_v = A.leituras(s)
    ev0, Ct0 = A.mundo(h, L, C, None); conds, tcs0 = A.especialistas(z_c, z_v, ev0, Ct0, L)
    evB, CtB = A.mundo(h, L, C, mud); _, tcsB = A.especialistas(z_c, z_v, evB, CtB, L)
    out = {}
    for d in deltas:
        o = {}
        tco, esc, tr = orgao_h(conds, tcs0, hh, L, Ct0, ev0, d); o["C_constante"] = A.resumo(tco, tcs0, esc); o["C_constante"]["trocas"] = tr
        tco, esc, tr = orgao_h(conds, tcsB, hh, L, CtB, evB, d); o["B_muda"] = A.resumo(tco, tcsB, esc); o["B_muda"]["trocas"] = tr
        tco, esc, tr = orgao_h(conds, tcs0, hh, L, CtB, evB, d); o["D_sem_mudanca"] = A.resumo(tco, tcsB, esc); o["D_sem_mudanca"]["trocas"] = tr
        out[d] = o
    return s, out


def fumaca(L, C, mud, h_anos):
    from multiprocessing import Pool
    print("fumaça do teste do ato A2 — sementes de desenho 5000–5009; nenhuma semente do teste")
    with Pool(2) as p: R = dict(p.map(semente, [(s, L, C, mud, h_anos * A.ANO, DELTAS) for s in A.DESENHO]))
    for d in DELTAS:
        c = [R[s][d]["C_constante"] for s in R]; b = [R[s][d]["B_muda"] for s in R]
        oc = np.array([sum(x["orgao"][2:8]) for x in c]); ac = np.array([sum(x["afinada"][2:8]) for x in c])
        g = lambda xs: 1 - sum(sum(x["orgao"][5:8]) for x in xs) / sum(sum(x["afinada"][5:8]) for x in xs)
        print(f"  δ {d:4d}: C mundos ≤ 1,05 da afinada {int((oc <= 1.05*ac).sum())}/10, razão total {oc.sum()/ac.sum():.3f}, trocas médias {np.mean([x['trocas'] for x in c]):.1f}"
              f" | ganho B anos 6–8 {g(b):.3f}, ganho C {g(c):.3f}")


def main(L, C, mud, h_anos, delta):
    assert (ROOT / "PREDICAO_teste_ato_A2.md").exists(), "sem predição, sem teste"
    from multiprocessing import Pool
    out = {"L": L, "C": C, "mudanca": mud, "h_anos": h_anos, "delta": delta, "C_constante": {}, "B_muda": {}, "D_sem_mudanca": {}}
    t0 = time.time()
    with Pool(2) as pool:
        for s, o in pool.imap_unordered(semente, [(s, L, C, mud, h_anos * A.ANO, (delta,)) for s in A.SEEDS]):
            for k, v in o[delta].items(): out[k][str(s)] = v
            print(f"  s{s} ({time.time()-t0:.0f} s)", flush=True)
    julgar(out)


def julgar(out):
    def soma(R, ch, a, b): return np.array([sum(R[s][ch][a:b]) for s in sorted(R)])
    def melhor(R, a, b): return np.array([min(sum(e[a:b]) for e in R[s]["especialistas"]) for s in sorted(R)])
    def ganho(R, a, b): o, f = soma(R, "orgao", a, b), soma(R, "afinada", a, b); return 1 - o.sum() / f.sum(), o, f
    Cc, B, Dd = out["C_constante"], out["B_muda"], out["D_sem_mudanca"]
    r1 = soma(Cc, "orgao", 1, 8) / melhor(Cc, 1, 8); j1n = int((r1 <= 1.10).sum())
    gB, oB, aB = ganho(B, 5, 8); gC, _, _ = ganho(Cc, 5, 8); wB = int((oB <= 0.90 * aB).sum())
    o3, a3 = soma(Cc, "orgao", 2, 8), soma(Cc, "afinada", 2, 8); g3 = o3.sum() / a3.sum(); n3 = int((o3 <= 1.05 * a3).sum())
    gD, oD, _ = ganho(Dd, 5, 8); bd = int((oB < oD).sum())
    res = {"J1": {"razao_mediana": float(np.median(r1)), "mundos_ate_1_10": j1n, "passa": bool(j1n >= 80)},
           "J2": {"ganho_B": float(gB), "ganho_C": float(gC), "mundos_10pct": wB, "passa": bool(gB >= 0.10 and gB - gC >= 0.10 and wB >= 60)},
           "J3": {"razao_total": float(g3), "mundos_ate_1_05": n3, "passa": bool(g3 <= 1.05 and n3 >= 70)},
           "J4": {"ganho_D": float(gD), "B_mais_barato_que_D": bd, "passa": bool((gD - gC) <= 0.5 * (gB - gC) and bd >= 70)},
           "relatado": {"trocas_medias": {c: float(np.mean([R[s]["trocas"] for s in R])) for c, R in (("C", Cc), ("B", B), ("D", Dd))},
                        "por_ano": {c: {"orgao": [float(np.sum([R[s]["orgao"][y] for s in R])) for y in range(A.ANOS)],
                                        "afinada": [float(np.sum([R[s]["afinada"][y] for s in R])) for y in range(A.ANOS)]} for c, R in (("C", Cc), ("B", B), ("D", Dd))},
                        "B_6_8_melhor_fixa": float(melhor(B, 5, 8).sum()), "B_6_8_orgao": float(oB.sum())}}
    out["julgamentos"] = res; print(json.dumps(res, ensure_ascii=False, indent=1))
    (ROOT / "resultados_teste_ato_A2.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--fumaca", action="store_true"); a = ap.parse_args()
    cfg = json.loads((ROOT / "PREDICAO_teste_ato_A_parametros.json").read_text())
    if a.fumaca: fumaca(cfg["L"], cfg["C"], cfg["mudanca"], cfg["h_anos"])
    else:
        d = json.loads((ROOT / "PREDICAO_teste_ato_A2_parametros.json").read_text())["delta"]
        main(cfg["L"], cfg["C"], cfg["mudanca"], cfg["h_anos"], d)
