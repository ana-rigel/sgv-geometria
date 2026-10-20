"""Teste 26 (o mundo sítio: cheia com custo e um ato de proteção). Predição: PREDICAO_teste26_mundo_sitio.md.

    python ia-geometrica/teste26.py --mecanica   # roda a cadeia inteira em 2 sementes de desenho; não imprime custos
    python ia-geometrica/teste26.py              # o teste (exige a predição)
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V; import sitio as S

ROOT = Path(__file__).resolve().parent
ANOS, AFIN = 4, 2 * S.H_ANO                       # anos 1–2: régua e afinação; anos 3–4: medida
N = ANOS * S.H_ANO; SEEDS = range(1000, 1100)
H_CRIT, D, C, L, P = 1.2, 100.0, 10.0, 6, 48      # cheia (m); perda; custo de chamar; antecedência (h); proteção (h)
G_NIVEL = np.round(np.arange(0.60, 1.401, 0.02), 2)          # N1 e N2: limiar de nível (m)
G_SUB = np.round(np.arange(0.02, 0.401, 0.02), 2)            # N2: subida em 3 h (m)
G_Z = np.arange(0.25, 8.001, 0.25)                           # v0: limiares na régua
INF = np.inf


def leituras(x):
    """O que a v0 lê: surpresa com direção no andar 1 (x − R1 antes de atualizar) e o vinco (R1 − R4), ambos na régua dos anos 1–2."""
    obs = V.Observador(1); obs.R[:] = x[0]
    _, _, Rh = V.rodar(x, obs)
    R1, R4 = Rh[:, 0, 0], Rh[:, 3, 0]
    s0 = x[:, 0] - np.concatenate([[x[0, 0]], R1[:-1]]); vinco = R1 - R4
    regua = V.calibrar_regua(np.column_stack([s0[:AFIN], vinco[:AFIN]]))
    z_s = (s0 - regua[0][0]) / regua[0][1]; z_v = (vinco - regua[1][0]) / regua[1][1]
    return z_s, z_v, regua, obs.lams


def avaliar(cond, ev, ini, fim):
    ch = S.chamadas(cond, P); return S.custo(ev, ch, ini, fim, D, C, L, P)


def afinar(a, b, ga, gb, ev):
    """Melhor (θa, θb) pelo custo nos anos 1–2; cond = (a ≥ θa) ou (b ≥ θb). θ = ∞ desliga aquela leitura."""
    melhor = None
    for ta in list(ga) + [INF]:
        ca = a >= ta
        for tb in (list(gb) + [INF]) if b is not None else [INF]:
            cond = ca | (b >= tb) if b is not None and tb < INF else ca
            c = avaliar(cond, ev, 0, AFIN)[0]
            if melhor is None or c < melhor[0]: melhor = (c, ta, tb)
    return melhor[1], melhor[2]


def semente(s):
    r, h, xs = S.mundo_sitio(N, s); x = xs[:, None]; ev = S.eventos_de_cheia(h, H_CRIT)
    z_s, z_v, regua, lams = leituras(x)
    sub = np.concatenate([np.zeros(3), xs[3:] - xs[:-3]])
    out = {"cheias_afin": int(((ev >= 0) & (ev < AFIN)).sum()), "cheias_medida": int((ev >= AFIN).sum()), "regua": regua}
    pol = {}
    th = afinar(xs, None, G_NIVEL, None, ev)[0]; pol["N1_nivel"] = (xs >= th, {"nivel": th})
    t1, t2 = afinar(xs, sub, G_NIVEL, G_SUB, ev); pol["N2_nivel_subida"] = (((xs >= t1) | (sub >= t2)), {"nivel": t1, "subida": t2})
    u1, u2 = afinar(z_s, z_v, G_Z, G_Z, ev); pol["v0"] = (((z_s >= u1) | (z_v >= u2)), {"surpresa": u1, "vinco": u2})
    pol["v0_crua"] = (((z_s >= 3) | (z_v >= 3)), {"surpresa": 3, "vinco": 3})
    pol["nunca"] = (np.zeros(N, dtype=bool), {})
    for k, (cond, par) in pol.items():
        c, perdas, nch, nev = avaliar(cond, ev, AFIN, N)
        out[k] = {"param": {a: (None if b == INF else float(b)) for a, b in par.items()}, "custo": c, "perdas": perdas, "chamadas": nch}
    cho = S.oraculo(ev, L, P); c, perdas, nch, nev = S.custo(ev, cho, AFIN, N, D, C, L, P)
    out["oraculo"] = {"custo": c, "perdas": perdas, "chamadas": nch}
    return s, out


def mecanica():
    for s in (5000, 5001):
        t0 = time.time(); _, o = semente(s)
        print(f"  s{s}: cadeia rodou em {time.time()-t0:.1f} s | cheias {o['cheias_afin']} (afinação) {o['cheias_medida']} (medida) | chaves {sorted(k for k in o if isinstance(o[k], dict))}")
    print("mecânica: nenhum custo impresso")


def main():
    assert (ROOT / "PREDICAO_teste26_mundo_sitio.md").exists(), "sem predição, sem teste"
    from multiprocessing import Pool
    out = {"sementes": {}}
    with Pool(2) as pool:
        for s, o in pool.imap_unordered(semente, list(SEEDS)):
            out["sementes"][str(s)] = o
            if (s - 1000) % 10 == 0: print(f"  s{s}: cheias {o['cheias_medida']} | custo N1 {o['N1_nivel']['custo']:.0f} N2 {o['N2_nivel_subida']['custo']:.0f} v0 {o['v0']['custo']:.0f} orac {o['oraculo']['custo']:.0f} nunca {o['nunca']['custo']:.0f}", flush=True)
    A = [out["sementes"][str(s)] for s in SEEDS]
    cs = {k: np.array([a[k]["custo"] for a in A]) for k in ("N1_nivel", "N2_nivel_subida", "v0", "v0_crua", "nunca", "oraculo")}
    Vorac = 1 - cs["oraculo"] / cs["N1_nivel"]
    j1 = bool(np.median(Vorac) >= 0.20 and (Vorac > 0.05).sum() >= 95)
    tot = {k: float(v.sum()) for k, v in cs.items()}
    ganho_N2 = 1 - tot["v0"] / tot["N2_nivel_subida"]; venc_N2 = int((cs["v0"] < cs["N2_nivel_subida"]).sum()); emp_N2 = int((cs["v0"] == cs["N2_nivel_subida"]).sum())
    j2 = bool(ganho_N2 >= 0.10 and venc_N2 >= 60)
    ganho_N1 = 1 - tot["v0"] / tot["N1_nivel"]; venc_N1 = int((cs["v0"] < cs["N1_nivel"]).sum())
    teto = tot["N1_nivel"] - tot["oraculo"]
    out["resumo"] = {
        "custo_total_medida": tot, "V_orac_mediana": float(np.median(Vorac)), "V_orac_acima_5pc": int((Vorac > 0.05).sum()),
        "v0_vs_N2": {"ganho_total": ganho_N2, "v0_mais_barata_em": venc_N2, "empates": emp_N2},
        "v0_vs_N1": {"ganho_total": ganho_N1, "v0_mais_barata_em": venc_N1},
        "N2_vs_N1_ganho_total": 1 - tot["N2_nivel_subida"] / tot["N1_nivel"],
        "fracao_do_teto_capturada": {k: (tot["N1_nivel"] - tot[k]) / teto for k in ("N2_nivel_subida", "v0", "v0_crua")},
        "perdas_totais": {k: int(sum(a[k]["perdas"] for a in A)) for k in cs}, "chamadas_totais": {k: int(sum(a[k]["chamadas"] for a in A)) for k in cs},
        "cheias_medida_total": int(sum(a["cheias_medida"] for a in A)),
        "J1_teto_existe": j1, "J2_v0_ve_o_que_o_sensor_comum_nao_ve": j2}
    R = out["resumo"]
    print(f"\n== teste 26: custo total (anos 3–4, 100 sementes) nunca {tot['nunca']:.0f} | N1 {tot['N1_nivel']:.0f} | N2 {tot['N2_nivel_subida']:.0f} | v0 {tot['v0']:.0f} | v0 crua {tot['v0_crua']:.0f} | oráculo {tot['oraculo']:.0f}")
    print(f"   J1 teto: V_orac mediana {100*R['V_orac_mediana']:.1f} %, > 5 % em {R['V_orac_acima_5pc']} → {'PASSA' if j1 else 'REPROVA'}")
    print(f"   J2 v0 vs N2: ganho total {100*ganho_N2:+.1f} %, v0 mais barata em {venc_N2} (empates {emp_N2}) → {'PASSA' if j2 else 'REPROVA'}")
    print(f"   relatado: v0 vs N1 {100*ganho_N1:+.1f} % (mais barata em {venc_N1}); N2 vs N1 {100*R['N2_vs_N1_ganho_total']:+.1f} %; fração do teto: {R['fracao_do_teto_capturada']}")
    (ROOT / "resultados_teste26.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mecanica", action="store_true")
    mecanica() if ap.parse_args().mecanica else main()
