"""Teste do ato A (o laço do ato): a organização ⋄ aprende com a consequência do que faz, no mundo sítio de cheias.
Desenho: DESENHO_laco_do_ato.md. Predição: PREDICAO_teste_ato_A.md.

O órgão: marcas de decisão (θc, θv) sobre a régua fixa da v0 (surpresa da chuva z_c, vinco do córrego z_v); age pela marca
de menor custo descontado (meia-vida h), sabendo o custo que cada marca teria pago (a cheia vem quer se aja, quer não).

    python ia-geometrica/teste_ato_A.py --fumaca     # sementes de desenho 5000–5009: regime, mudança e h (antes da predição)
    python ia-geometrica/teste_ato_A.py              # o teste (exige a predição)
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sitio as S
import teste26 as T26
import teste27 as T27

ROOT = Path(__file__).resolve().parent
ANO = S.H_ANO; ANOS = 8; N = ANOS * ANO; AFIN = 2 * ANO; T_MUD = 4 * ANO        # mudança no começo do 5º ano
D, P = T26.D, T26.P
TC = [1.0, 2.0, 3.0, 4.0, 6.0, np.inf]; TV = [0.5, 1.0, 2.0, 3.0, 4.0, np.inf]
MARCAS = [(a, b) for a in TC for b in TV]; K = len(MARCAS)
NUNCA = MARCAS.index((np.inf, np.inf))
SEEDS = range(1000, 1100); DESENHO = range(5000, 5010)


# ---------------------------------------------------------------- o mundo
def leituras(seed):
    r, h, xs = S.mundo_sitio(N, seed); p = S.pluviometro(r)
    z_c, _ = T27.surpresa_chuva(p); _, z_v, _, _ = T26.leituras(xs[:, None])
    return h, z_c, z_v


def mundo(h, L, C, mudanca):
    """Eventos de cheia e custo de chamar por hora. mudanca: None, 'assoreia' (cheia a 1,0 m do 5º ano) ou 'encarece' (C × 2)."""
    ev1 = S.eventos_de_cheia(h, T26.H_CRIT)
    if mudanca == "assoreia":
        ev2 = S.eventos_de_cheia(h, 1.0); ev = np.concatenate([ev1[ev1 < T_MUD], ev2[ev2 >= T_MUD]])
    else:
        ev = ev1
    Ct = np.full(N, float(C))
    if mudanca == "encarece": Ct[T_MUD:] = 2 * C
    return np.unique(ev), Ct


def protegidas(ev, ch, L):
    if len(ch) == 0: return np.zeros(len(ev), bool)
    i = np.searchsorted(ch, ev - L, side="right") - 1          # última chamada com a + L ≤ t
    ok = i >= 0; out = np.zeros(len(ev), bool)
    out[ok] = ev[ok] <= ch[i[ok]] + L + P
    return out


def eventos_de_custo(ev, ch, Ct, L):
    """(tempo, custo) de uma trajetória: C(t) em cada chamada; D em cada cheia sem proteção, no instante da cheia."""
    perdas = ev[~protegidas(ev, ch, L)]
    t = np.concatenate([ch, perdas]); c = np.concatenate([Ct[ch], np.full(len(perdas), D)])
    o = np.argsort(t, kind="stable"); return t[o], c[o]


def custo_janela(tc, ini, fim):
    t, c = tc; return float(c[(t >= ini) & (t < fim)].sum())


def especialistas(z_c, z_v, ev, Ct, L):
    conds = [(z_c >= a) | (z_v >= b) for a, b in MARCAS]
    tcs = [eventos_de_custo(ev, S.chamadas(c, P), Ct, L) for c in conds]
    return conds, tcs


# ---------------------------------------------------------------- o órgão
def centro():
    """Desempate: a marca mais perto do meio da grade."""
    return np.array([abs(TC.index(a) - 2.5) + abs(TV.index(b) - 2.5) for a, b in MARCAS])


def orgao(conds, tcs_aprende, h_horas, L, Ct, ev):
    """Age pela marca de menor custo descontado até t − 1. Aprende com tcs_aprende (as consequências que recebe)."""
    gam = 0.5 ** (1.0 / h_horas)
    T = np.concatenate([tc[0] for tc in tcs_aprende]); Cc = np.concatenate([tc[1] for tc in tcs_aprende])
    Kx = np.concatenate([np.full(len(tc[0]), k) for k, tc in enumerate(tcs_aprende)])
    o = np.argsort(T, kind="stable"); T, Cc, Kx = T[o], Cc[o], Kx[o]
    C_ = np.array(conds); qualquer = C_.any(axis=0); cand = np.flatnonzero(qualquer)
    W = np.zeros(K); ult = 0; j = 0; desemp = centro() * 1e-9
    chamadas = []; prot_ate = -1; escolha = []
    for t in cand:
        if t < prot_ate: continue
        while j < len(T) and T[j] < t:
            W *= gam ** (T[j] - ult); ult = T[j]; W[Kx[j]] += Cc[j]; j += 1
        W *= gam ** (t - ult); ult = t
        k = int(np.argmin(W + desemp))
        if C_[k, t]:
            chamadas.append(t); prot_ate = t + P; escolha.append((int(t), k))
    ch = np.array(chamadas, dtype=int)
    return eventos_de_custo(ev, ch, Ct, L), escolha


def anual(tc):
    return [custo_janela(tc, y * ANO, (y + 1) * ANO) for y in range(ANOS)]


# ---------------------------------------------------------------- fumaça (sementes de desenho)
def fumaca():
    print("fumaça do teste do ato A — sementes de desenho 5000–5009; nenhuma semente do teste")
    t0 = time.time(); W = {s: leituras(s) for s in DESENHO}; print(f"  leituras em {time.time()-t0:.0f} s")
    for (L, C) in ((1, 10.0), (3, 10.0), (1, 3.0), (3, 3.0)):
        linhas = []
        for s, (h, z_c, z_v) in W.items():
            ev, Ct = mundo(h, L, C, None); conds, tcs = especialistas(z_c, z_v, ev, Ct, L)
            tot = np.array([custo_janela(tc, AFIN, N) for tc in tcs])
            linhas.append((tot, len(ev) / ANOS))
        tot = np.array([l[0] for l in linhas]).sum(0); best = int(np.argmin(tot))
        print(f"  L{L} C{C:g}: cheias/ano {np.mean([l[1] for l in linhas]):.1f} | nunca {tot[NUNCA]:.0f} | melhor fixa {MARCAS[best]} {tot[best]:.0f}"
              f" ({100*(1-tot[best]/tot[NUNCA]):.0f} % abaixo de nunca) | mais nervosa {MARCAS[0]} {tot[0]:.0f}")
    print("fumaça: escolha do regime pela regra do desenho fica para a leitura desta saída")


def fumaca_mudanca(L, C):
    print(f"fumaça da mudança e de h — L{L} C{C:g}, sementes de desenho")
    W = {s: leituras(s) for s in DESENHO}
    for mud in ("assoreia", "encarece"):
        pre = np.zeros(K); pos = np.zeros(K); org = {hh: 0.0 for hh in (0.25, 0.5, 1, 2, 4)}; afin_pos = 0.0
        for s, (h, z_c, z_v) in W.items():
            ev, Ct = mundo(h, L, C, mud); conds, tcs = especialistas(z_c, z_v, ev, Ct, L)
            pre += [custo_janela(tc, 0, T_MUD) for tc in tcs]; p = np.array([custo_janela(tc, 5 * ANO, N) for tc in tcs]); pos += p
            ka = int(np.argmin([custo_janela(tc, 0, AFIN) for tc in tcs])); afin_pos += p[ka]
            for hh in org:
                tco, _ = orgao(conds, tcs, hh * ANO, L, Ct, ev); org[hh] += custo_janela(tco, 5 * ANO, N)
        bp, bq = int(np.argmin(pre)), int(np.argmin(pos))
        print(f"  {mud}: melhor antes {MARCAS[bp]}, depois {MARCAS[bq]} | anos 6–8: antiga melhor {pos[bp]:.0f}, nova melhor {pos[bq]:.0f} "
              f"(+{100*(pos[bp]/pos[bq]-1):.0f} %), afinada nos anos 1–2 {afin_pos:.0f} | órgão por h (anos): "
              + " ".join(f"{hh}:{v:.0f}" for hh, v in org.items()))


# ---------------------------------------------------------------- o teste
def resumo(tco, tcs, esc):
    ka = int(np.argmin([custo_janela(tc, 0, AFIN) for tc in tcs]))
    return {"orgao": anual(tco), "afinada": anual(tcs[ka]), "marca_afinada": ka, "nunca": anual(tcs[NUNCA]),
            "especialistas": [anual(tc) for tc in tcs],
            "escolhas_por_ano": [np.bincount([k for t, k in esc if y * ANO <= t < (y + 1) * ANO], minlength=K).tolist() for y in range(ANOS)]}


def semente(args):
    """As quatro condições num mundo. C: nada muda. B: o córrego assoreia no 5º ano. D (controle julgado): age no mundo de B,
    mas aprende com as consequências do mesmo mundo sem a mudança. E (relatado): age no mundo de B e aprende com as
    consequências de outro sítio igual (semente + 1000) que também assoreou."""
    s, L, C, mud, hh = args
    h, z_c, z_v = leituras(s)
    ev0, Ct0 = mundo(h, L, C, None); conds, tcs0 = especialistas(z_c, z_v, ev0, Ct0, L)
    evB, CtB = mundo(h, L, C, mud); _, tcsB = especialistas(z_c, z_v, evB, CtB, L)
    h2, zc2, zv2 = leituras(s + 1000); ev2, Ct2 = mundo(h2, L, C, mud); _, tcs2 = especialistas(zc2, zv2, ev2, Ct2, L)
    o = {}
    tco, esc = orgao(conds, tcs0, hh, L, Ct0, ev0); o["C_constante"] = resumo(tco, tcs0, esc)
    tco, esc = orgao(conds, tcsB, hh, L, CtB, evB); o["B_muda"] = resumo(tco, tcsB, esc)
    tco, esc = orgao(conds, tcs0, hh, L, CtB, evB); o["D_sem_mudanca"] = resumo(tco, tcsB, esc)
    tco, esc = orgao(conds, tcs2, hh, L, CtB, evB); o["E_outro_sitio"] = resumo(tco, tcsB, esc)
    return s, o


def main(L, C, mud, h_anos):
    assert (ROOT / "PREDICAO_teste_ato_A.md").exists(), "sem predição, sem teste"
    from multiprocessing import Pool
    out = {"L": L, "C": C, "mudanca": mud, "h_anos": h_anos, "marcas": [[float(a), float(b)] for a, b in MARCAS],
           "C_constante": {}, "B_muda": {}, "D_sem_mudanca": {}, "E_outro_sitio": {}}
    t0 = time.time()
    with Pool(2) as pool:
        for s, o in pool.imap_unordered(semente, [(s, L, C, mud, h_anos * ANO) for s in SEEDS]):
            for k, v in o.items(): out[k][str(s)] = v
            print(f"  s{s} ({time.time()-t0:.0f} s)", flush=True)
    julgar(out)


def julgar(out):
    def soma(R, chave, a, b): return np.array([sum(R[s][chave][a:b]) for s in sorted(R)])
    def melhor_fixa(R, a, b): return np.array([min(sum(e[a:b]) for e in R[s]["especialistas"]) for s in sorted(R)])
    def ganho(R, a, b): o, f = soma(R, "orgao", a, b), soma(R, "afinada", a, b); return 1 - o.sum() / f.sum(), o, f
    Cc, B, Dd, E = out["C_constante"], out["B_muda"], out["D_sem_mudanca"], out["E_outro_sitio"]
    o1, m1 = soma(Cc, "orgao", 1, 8), melhor_fixa(Cc, 1, 8); r1 = o1 / m1; j1n = int((r1 <= 1.10).sum())
    gB, oB, aB = ganho(B, 5, 8); gC, _, _ = ganho(Cc, 5, 8); wB = int((oB <= 0.90 * aB).sum())
    j2 = bool(gB >= 0.10 and gB - gC >= 0.10 and wB >= 60)
    o3, a3 = soma(Cc, "orgao", 2, 8), soma(Cc, "afinada", 2, 8); g3 = o3.sum() / a3.sum(); n3 = int((o3 <= 1.05 * a3).sum())
    j3 = bool(g3 <= 1.05 and n3 >= 70)
    gD, oD, _ = ganho(Dd, 5, 8); gE, _, _ = ganho(E, 5, 8)
    melhorBD = int((oB < oD).sum())
    j4 = bool((gD - gC) <= 0.5 * (gB - gC) and melhorBD >= 70)
    ano = lambda R, ch: [float(np.sum([R[s][ch][y] for s in R])) for y in range(ANOS)]
    res = {"J1": {"razao_mediana": float(np.median(r1)), "mundos_ate_1_10": j1n, "passa": bool(j1n >= 80)},
           "J2": {"ganho_B": float(gB), "ganho_C": float(gC), "mundos_10pct": wB, "passa": j2},
           "J3": {"razao_total": float(g3), "mundos_ate_1_05": n3, "passa": j3},
           "J4": {"ganho_D": float(gD), "ganho_B": float(gB), "ganho_C": float(gC), "B_mais_barato_que_D": melhorBD, "passa": j4},
           "relatado": {"ganho_E_outro_sitio": float(gE),
                        "B_6_8": {"orgao": float(oB.sum()), "afinada": float(aB.sum()), "melhor_fixa": float(melhor_fixa(B, 5, 8).sum()), "nunca": float(soma(B, "nunca", 5, 8).sum())},
                        "por_ano": {c: {"orgao": ano(R, "orgao"), "afinada": ano(R, "afinada")} for c, R in (("C", Cc), ("B", B), ("D", Dd), ("E", E))}}}
    out["julgamentos"] = res
    print(json.dumps(res, ensure_ascii=False, indent=1))
    (ROOT / "resultados_teste_ato_A.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--fumaca", action="store_true"); ap.add_argument("--fumaca-mudanca", nargs=2, type=float)
    a = ap.parse_args()
    if a.fumaca: fumaca()
    elif a.fumaca_mudanca: fumaca_mudanca(int(a.fumaca_mudanca[0]), a.fumaca_mudanca[1])
    else:
        cfg = json.loads((ROOT / "PREDICAO_teste_ato_A_parametros.json").read_text()); main(cfg["L"], cfg["C"], cfg["mudanca"], cfg["h_anos"])
