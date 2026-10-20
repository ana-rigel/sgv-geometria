"""Teste 28 (o sítio com ato automático: rápido e barato). Predição: PREDICAO_teste28_ato_automatico.md.

Mesmo mundo e sementes dos testes 26–27; muda só o ato. Ponto julgado: L = 1 h, C = 1. Mapa relatado: L ∈ {1, 3, 6} × C ∈ {1, 3, 10} em 30 sementes.

    python ia-geometrica/teste28.py --mecanica
    python ia-geometrica/teste28.py
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import sitio as S; import teste26 as T26; import teste27 as T27

ROOT = Path(__file__).resolve().parent
N, AFIN, SEEDS = T26.N, T26.AFIN, T26.SEEDS
H_CRIT, D, P = T26.H_CRIT, T26.D, T26.P
L_J, C_J = 1, 1.0
MAPA_L, MAPA_C, MAPA_SEEDS = (1, 3, 6), (1.0, 3.0, 10.0), range(1000, 1030)
INF = np.inf


def avaliar(cond, ev, ini, fim, L, C):
    return S.custo(ev, S.chamadas(cond, P), ini, fim, D, C, L, P)


def afinar(a, b, ga, gb, ev, L, C):
    """Melhor regra nos anos 1–2 entre OU e E; ±∞ desliga uma leitura. Devolve (forma, θa, θb, cond)."""
    melhor = None
    for forma in ("ou", "e"):
        for ta in list(ga) + [INF]:
            ca = a >= ta
            for tb in list(gb) + [INF if forma == "ou" else -INF]:
                cond = (ca | (b >= tb)) if forma == "ou" else (ca & (b >= tb))
                c = avaliar(cond, ev, 0, AFIN, L, C)[0]
                if melhor is None or c < melhor[0]: melhor = (c, forma, ta, tb, cond)
    return melhor[1:]


def inicio_de_chuva(p, seco=12):
    """Verdadeiro na primeira hora de cada episódio de chuva (≥ 12 h secas antes), lido no pluviômetro."""
    out = np.zeros(len(p), dtype=bool); ultima = -10 ** 9
    for t in np.flatnonzero(p > 0):
        if t - ultima > seco: out[t] = True
        ultima = t
    return out


def leituras(s):
    r, h, xs = S.mundo_sitio(N, s); p = S.pluviometro(r); ev = S.eventos_de_cheia(h, H_CRIT)
    z_s, z_v, _, _ = T26.leituras(xs[:, None]); z_c, _ = T27.surpresa_chuva(p)
    sub = np.concatenate([np.zeros(3), xs[3:] - xs[:-3]]); chuva3 = np.convolve(p, np.ones(3))[:N]
    fam = {"N2_nivel_subida": (xs, sub, T26.G_NIVEL, T26.G_SUB), "N3_chuva_nivel": (chuva3, xs, T27.G_CHUVA, T27.G_NIVEL),
           "v0_corrego": (z_s, z_v, T26.G_Z, T27.G_ZV), "v0_dois_sensores": (z_c, z_v, T27.G_ZC, T27.G_ZV)}
    return r, ev, fam, inicio_de_chuva(p)


def celula(r, ev, fam, ini_chuva, L, C, nomes):
    out = {}
    for k in nomes:
        a, b, ga, gb = fam[k]; f, ta, tb, cond = afinar(a, b, ga, gb, ev, L, C)
        c, perdas, nch, _ = avaliar(cond, ev, AFIN, N, L, C)
        out[k] = {"forma": f, "theta": [None if abs(ta) == INF else float(ta), None if abs(tb) == INF else float(tb)], "custo": c, "perdas": perdas, "chamadas": nch}
    c, perdas, nch, nev = avaliar(ini_chuva, ev, AFIN, N, L, C); out["cada_chuva"] = {"custo": c, "perdas": perdas, "chamadas": nch}
    out["nunca"] = {"custo": D * nev, "perdas": nev, "chamadas": 0}
    c, perdas, nch, _ = S.custo(ev, S.oraculo(ev, L, P), AFIN, N, D, C, L, P); out["oraculo"] = {"custo": c, "perdas": perdas, "chamadas": nch}
    c, perdas, nch, _ = S.teto_chuva(r, ev, AFIN, N, D, C, L, P); out["teto_chuva"] = {"custo": c, "perdas": perdas, "chamadas": nch}
    return out


def semente(s):
    r, ev, fam, ini = leituras(s)
    o = {"julgado": celula(r, ev, fam, ini, L_J, C_J, list(fam))}
    if s in MAPA_SEEDS:
        o["mapa"] = {f"L{L}_C{int(C)}": celula(r, ev, fam, ini, L, C, ["N3_chuva_nivel", "v0_dois_sensores"]) for L in MAPA_L for C in MAPA_C}
    return s, o


def mecanica():
    t0 = time.time(); r, ev, fam, ini = leituras(5000); o = celula(r, ev, fam, ini, L_J, C_J, list(fam))
    print(f"  s5000: célula julgada em {time.time()-t0:.1f} s | chaves {sorted(o)}"); print("mecânica: nenhum custo impresso")


def main():
    assert (ROOT / "PREDICAO_teste28_ato_automatico.md").exists(), "sem predição, sem teste"
    from multiprocessing import Pool
    out = {"sementes": {}}
    with Pool(2) as pool:
        for s, o in pool.imap_unordered(semente, list(SEEDS)):
            out["sementes"][str(s)] = o; j = o["julgado"]
            print(f"  s{s}: nunca {j['nunca']['custo']:.0f} N3 {j['N3_chuva_nivel']['custo']:.0f} v0 dois {j['v0_dois_sensores']['custo']:.0f} cada chuva {j['cada_chuva']['custo']:.0f} orac {j['oraculo']['custo']:.0f}", flush=True)
    A = [out["sementes"][str(s)]["julgado"] for s in SEEDS]
    nomes = ["nunca", "N2_nivel_subida", "N3_chuva_nivel", "v0_corrego", "v0_dois_sensores", "cada_chuva", "teto_chuva", "oraculo"]
    cs = {k: np.array([a[k]["custo"] for a in A]) for k in nomes}; tot = {k: float(v.sum()) for k, v in cs.items()}
    teto = tot["nunca"] - tot["oraculo"]; frac = {k: (tot["nunca"] - tot[k]) / teto for k in nomes}
    j1 = bool(frac["N3_chuva_nivel"] >= 0.70 and (cs["N3_chuva_nivel"] < cs["nunca"]).sum() >= 95)
    g2 = 1 - tot["v0_dois_sensores"] / tot["N3_chuva_nivel"]; w2 = int((cs["v0_dois_sensores"] < cs["N3_chuva_nivel"]).sum()); e2 = int((cs["v0_dois_sensores"] == cs["N3_chuva_nivel"]).sum())
    j2 = bool(g2 >= 0.10 and w2 >= 60)
    M = [out["sementes"][str(s)]["mapa"] for s in MAPA_SEEDS]; mapa = {}
    for cel in M[0]:
        t = {k: sum(m[cel][k]["custo"] for m in M) for k in ("nunca", "oraculo", "teto_chuva", "N3_chuva_nivel", "v0_dois_sensores", "cada_chuva")}
        mapa[cel] = {k: (t["nunca"] - t[k]) / (t["nunca"] - t["oraculo"]) for k in ("teto_chuva", "N3_chuva_nivel", "v0_dois_sensores", "cada_chuva")}
    out["resumo"] = {"custo_total": tot, "fracao_do_teto": frac, "N3_abaixo_de_nunca_em": int((cs["N3_chuva_nivel"] < cs["nunca"]).sum()),
                     "J1": {"fracao_N3": frac["N3_chuva_nivel"], "passa": j1}, "J2": {"ganho_v0_vs_N3": g2, "v0_mais_barata_em": w2, "empates": e2, "passa": j2},
                     "perdas": {k: int(sum(a[k]["perdas"] for a in A)) for k in nomes}, "chamadas": {k: int(sum(a[k]["chamadas"] for a in A)) for k in nomes},
                     "mapa_fracao_do_teto_30_sementes": mapa}
    print(f"\n== teste 28 (L = 1 h, C = 1): fração do teto {{{', '.join(f'{k}: {100*v:.1f} %' for k, v in frac.items())}}}")
    print(f"   J1 o sítio fica resolvível: N3 captura {100*frac['N3_chuva_nivel']:.1f} % do teto, abaixo de nunca em {out['resumo']['N3_abaixo_de_nunca_em']} → {'PASSA' if j1 else 'REPROVA'}")
    print(f"   J2 v0 vs N3: {100*g2:+.1f} %, mais barata em {w2} (empates {e2}) → {'PASSA' if j2 else 'REPROVA'}")
    for cel, v in mapa.items(): print(f"   mapa {cel}: " + " | ".join(f"{k} {100*x:.0f} %" for k, x in v.items()))
    (ROOT / "resultados_teste28.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mecanica", action="store_true")
    mecanica() if ap.parse_args().mecanica else main()
