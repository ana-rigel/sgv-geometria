"""Teste 27 (o mundo sítio com dois sensores: córrego e chuva). Predição: PREDICAO_teste27_chuva.md.

Mesmo mundo, mesmas sementes e mesmos custos do teste 26; muda só o que se observa.

    python ia-geometrica/teste27.py --mecanica   # cadeia em 2 sementes de desenho; não imprime custos
    python ia-geometrica/teste27.py              # o teste (exige a predição)
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V; import sitio as S; import teste26 as T26

ROOT = Path(__file__).resolve().parent
N, AFIN, SEEDS = T26.N, T26.AFIN, T26.SEEDS
H_CRIT, D, C, L, P = T26.H_CRIT, T26.D, T26.C, T26.L, T26.P
G_CHUVA = np.arange(1.0, 40.01, 1.0)                         # N3: chuva nas últimas 3 h (mm)
G_NIVEL = T26.G_NIVEL                                        # N3: nível (m)
G_ZC = np.arange(0.25, 8.001, 0.25)                          # v0: surpresa da chuva na régua
G_ZV = np.arange(-2.0, 8.001, 0.25)                          # v0: vinco do córrego na régua (pode ser negativo: base abaixo do normal)
INF = np.inf


def surpresa_chuva(p):
    """Uma v0 sobre o pluviômetro: surpresa com direção no andar 1, na régua dos anos 1–2."""
    obs = V.Observador(1); obs.R[:] = p[0]; x = p[:, None]
    _, _, Rh = V.rodar(x, obs); R1 = Rh[:, 0, 0]
    s = p - np.concatenate([[p[0]], R1[:-1]]); (med, esc), = V.calibrar_regua(s[:AFIN, None])
    return (s - med) / esc, (med, esc)


def afinar2(a, b, ga, gb, ev):
    """Melhor regra nos anos 1–2 entre duas formas: OU (a ≥ θa ou b ≥ θb) e E (a ≥ θa e b ≥ θb). ±∞ desliga uma leitura."""
    melhor = None
    for forma in ("ou", "e"):
        for ta in list(ga) + [INF]:
            ca = a >= ta
            for tb in list(gb) + [INF if forma == "ou" else -INF]:
                cb = b >= tb
                cond = (ca | cb) if forma == "ou" else (ca & cb)
                c = T26.avaliar(cond, ev, 0, AFIN)[0]
                if melhor is None or c < melhor[0]: melhor = (c, forma, ta, tb, cond)
    return melhor[1:]


def semente(s):
    r, h, xs = S.mundo_sitio(N, s); p = S.pluviometro(r); ev = S.eventos_de_cheia(h, H_CRIT)
    _, z_v, _, _ = T26.leituras(xs[:, None]); z_c, regua_c = surpresa_chuva(p)
    chuva3 = np.convolve(p, np.ones(3))[:N]
    out = {"cheias_medida": int((ev >= AFIN).sum()), "regua_chuva": regua_c}
    pol = {}
    f, a, b, cond = afinar2(chuva3, xs, G_CHUVA, G_NIVEL, ev); pol["N3_chuva_nivel"] = (cond, {"forma": f, "chuva3h": a, "nivel": b})
    f, a, b, cond = afinar2(z_c, z_v, G_ZC, G_ZV, ev); pol["v0_dois_sensores"] = (cond, {"forma": f, "surpresa_chuva": a, "vinco_corrego": b})
    pol["v0_crua"] = (((z_c >= 3) | (z_v >= 3)), {"forma": "ou", "surpresa_chuva": 3, "vinco_corrego": 3})
    for k, (cond, par) in pol.items():
        c, perdas, nch, _ = T26.avaliar(cond, ev, AFIN, N)
        out[k] = {"param": {q: (w if isinstance(w, str) else (None if abs(w) == INF else float(w))) for q, w in par.items()}, "custo": c, "perdas": perdas, "chamadas": nch}
    c, perdas, nch, _ = S.teto_chuva(r, ev, AFIN, N, D, C, L, P); out["teto_chuva"] = {"custo": c, "perdas": perdas, "chamadas": nch}
    return s, out


def mecanica():
    for s in (5000, 5001):
        t0 = time.time(); _, o = semente(s)
        print(f"  s{s}: cadeia rodou em {time.time()-t0:.1f} s | chaves {sorted(k for k in o if isinstance(o[k], dict))}")
    print("mecânica: nenhum custo impresso")


def main():
    assert (ROOT / "PREDICAO_teste27_chuva.md").exists(), "sem predição, sem teste"
    r26 = json.loads((ROOT / "resultados_teste26.json").read_text())["sementes"]
    from multiprocessing import Pool
    out = {"sementes": {}}
    with Pool(2) as pool:
        for s, o in pool.imap_unordered(semente, list(SEEDS)):
            for k in ("N2_nivel_subida", "v0", "nunca", "oraculo"): o[k + "_t26"] = r26[str(s)][k]
            out["sementes"][str(s)] = o
            if (s - 1000) % 10 == 0: print(f"  s{s}: N2 {o['N2_nivel_subida_t26']['custo']:.0f} | N3 {o['N3_chuva_nivel']['custo']:.0f} v0 {o['v0_dois_sensores']['custo']:.0f} teto chuva {o['teto_chuva']['custo']:.0f} nunca {o['nunca_t26']['custo']:.0f}", flush=True)
    A = [out["sementes"][str(s)] for s in SEEDS]
    cs = {k: np.array([a[k]["custo"] for a in A]) for k in ("N3_chuva_nivel", "v0_dois_sensores", "v0_crua", "teto_chuva", "N2_nivel_subida_t26", "v0_t26", "nunca_t26", "oraculo_t26")}
    tot = {k: float(v.sum()) for k, v in cs.items()}
    g1 = 1 - tot["N3_chuva_nivel"] / tot["N2_nivel_subida_t26"]; w1 = int((cs["N3_chuva_nivel"] < cs["N2_nivel_subida_t26"]).sum())
    g2 = 1 - tot["v0_dois_sensores"] / tot["N3_chuva_nivel"]; w2 = int((cs["v0_dois_sensores"] < cs["N3_chuva_nivel"]).sum()); e2 = int((cs["v0_dois_sensores"] == cs["N3_chuva_nivel"]).sum())
    j1 = bool(g1 >= 0.10 and w1 >= 60); j2 = bool(g2 >= 0.10 and w2 >= 60)
    nunca = tot["nunca_t26"]; frac = {k: (nunca - tot[k]) / (nunca - tot["teto_chuva"]) for k in ("N2_nivel_subida_t26", "N3_chuva_nivel", "v0_dois_sensores", "v0_crua")}
    formas = {k: {f: sum(a[k]["param"]["forma"] == f for a in A) for f in ("ou", "e")} for k in ("N3_chuva_nivel", "v0_dois_sensores")}
    out["resumo"] = {"custo_total_medida": tot, "J1": {"ganho_N3_vs_N2": g1, "N3_mais_barata_em": w1, "passa": j1},
                     "J2": {"ganho_v0_vs_N3": g2, "v0_mais_barata_em": w2, "empates": e2, "passa": j2},
                     "fracao_do_teto_da_chuva": frac, "formas_escolhidas": formas,
                     "perdas_totais": {k: int(sum(a[k]["perdas"] for a in A)) for k in cs}, "chamadas_totais": {k: int(sum(a[k]["chamadas"] for a in A)) for k in cs}}
    print(f"\n== teste 27: custo total (anos 3–4) nunca {nunca:.0f} | N2 (só córrego) {tot['N2_nivel_subida_t26']:.0f} | N3 {tot['N3_chuva_nivel']:.0f} | v0 dois sensores {tot['v0_dois_sensores']:.0f} | v0 crua {tot['v0_crua']:.0f} | teto da chuva {tot['teto_chuva']:.0f} | oráculo {tot['oraculo_t26']:.0f}")
    print(f"   J1 chuva compra antecedência: N3 vs N2 {100*g1:+.1f} %, mais barata em {w1} → {'PASSA' if j1 else 'REPROVA'}")
    print(f"   J2 v0 vs N3: {100*g2:+.1f} %, mais barata em {w2} (empates {e2}) → {'PASSA' if j2 else 'REPROVA'}")
    print(f"   relatado: fração do teto da chuva {frac}; formas {formas}")
    (ROOT / "resultados_teste27.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mecanica", action="store_true")
    mecanica() if ap.parse_args().mecanica else main()
