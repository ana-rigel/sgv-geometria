"""Teste 33 (a organização nasce sabendo o clima): a organização ⋄ semeada com 5 coeficientes de 2010–2017 deixa a v0 ler a
seca profunda como o SPEI-90, com a AUC calculada dentro de cada mês? E aprender depois de semeada atrapalha?
Predição: PREDICAO_teste33_organizacao_semeada.md.

    python ia-geometrica/teste33.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste30 as T30
import teste32 as T32
from teste32 import Organizacao, r2, organizar, ler_lugar, ler_juara, MT

ROOT = Path(__file__).resolve().parent
CAL = (2010, 2017); INICIO = 2018; MED = (2019, 2025)


def semear(x, t, cal):
    """Os 5 coeficientes do ano e a matriz dos mínimos quadrados de 2010–2017 (o que a placa grava ao nascer)."""
    A = np.array([Organizacao.base(ti) for ti in t[cal]]); org = Organizacao()
    org.P = np.linalg.inv(A.T @ A + np.eye(5) / T32.P0); org.beta = org.P @ (A.T @ x[cal]); return org


def correr(org, x, t, aprende=True):
    u = np.empty(len(x))
    for i in range(len(x)):
        if aprende: u[i] = org.passo(t[i], x[i])
        else: u[i] = x[i] - Organizacao.base(t[i]) @ org.beta
    return u


def auc_mes(score, y, mes):
    """AUC dentro de cada mês do ano, combinada pelo número de pares positivo–negativo de cada mês."""
    num = den = 0.0
    for m in range(1, 13):
        k = mes == m; n1 = y[k].sum(); n0 = (~y[k]).sum()
        if n1 and n0:
            num += T30.auc(score[k], y[k]) * n1 * n0; den += n1 * n0
    return num / den if den else float("nan")


def lugar(D, P, E, S, rng):
    ano = np.array([int(d[:4]) for d in D]); mes = np.array([int(d[5:7]) for d in D])
    t = np.array([np.datetime64(d, "D").astype(int) for d in D], float)
    doy = np.array([min(np.datetime64(d, "D").item().timetuple().tm_yday, 365) for d in D])
    cal = (ano >= CAL[0]) & (ano <= CAL[1]); med = (ano >= MED[0]) & (ano <= MED[1]); i0 = int(np.flatnonzero(ano >= INICIO)[0])
    m3, d3 = T30.climatologia(S, doy, cal); seca = (S - m3) / d3 <= T30.LIMIAR_SECA
    x = P - E; n = len(x); mb, _ = T30.climatologia(x, doy, cal)

    def desde(v):
        s = np.full(n, np.nan); s[i0:] = v; return s

    org_s = semear(x, t, cal); beta_semente = org_s.beta.copy()
    u_s = correr(org_s, x[i0:], t[i0:], aprende=True)
    org_c = semear(x, t, cal); u_c = correr(org_c, x[i0:], t[i0:], aprende=False)
    u_f, _ = organizar(x[i0:], t[i0:])
    S_ = {"v0+org semeada": desde(r2(u_s)[:, 1]), "v0+org semeada congelada": desde(r2(u_c)[:, 1]),
          "SPEI-90": T30.indices(P, E, cal, doy)["SPEI-90"], "v0+org fria": desde(r2(u_f)[:, 1]),
          "v0 crua": desde(r2(x[i0:])[:, 1]), "v0 clim. fixa": desde(r2((x - mb)[i0:])[:, 1]), "calendario": desde(r2(mb[i0:])[:, 1])}

    im = np.flatnonzero(med); y = seca[im]; mm = mes[im]
    out = {"seca_medida": int(y.sum()),
           "auc_por_mes": {k: auc_mes(-v[im], y, mm) for k, v in S_.items()},
           "auc_comum": {k: T30.auc(-v[im], y) for k, v in S_.items()}}
    a = out["auc_por_mes"]
    out["d_J1_semeada_menos_spei"] = a["v0+org semeada"] - a["SPEI-90"]
    out["d_J2_semeada_menos_congelada"] = a["v0+org semeada"] - a["v0+org semeada congelada"]
    b1, b2 = [], []
    for _ in range(T30.NBOOT):
        j = im[T30.bloco_boot(len(im), rng)]; yj = seca[j]; mj = mes[j]
        s = auc_mes(-S_["v0+org semeada"][j], yj, mj)
        b1.append(s - auc_mes(-S_["SPEI-90"][j], yj, mj)); b2.append(s - auc_mes(-S_["v0+org semeada congelada"][j], yj, mj))
    q = lambda b: [float(np.nanquantile(b, .025)), float(np.nanquantile(b, .975))]
    out["ic_J1"] = q(b1); out["ic_J2"] = q(b2)
    out["normal_medio_mm_dia"] = {"semente_2010_17": float(beta_semente[0]), "semeada_fim_2025": float(org_s.beta[0])}
    return out


def main():
    assert (ROOT / "PREDICAO_teste33_organizacao_semeada.md").exists(), "sem predição, sem teste"
    rng = np.random.default_rng(33); res = {n: lugar(*ler_lugar(n), rng) for n in MT}
    res["juara (relatado)"] = lugar(*ler_juara(), rng)
    portao = all(0.40 <= res[n]["auc_por_mes"]["calendario"] <= 0.60 for n in MT)
    j1 = sum(res[n]["d_J1_semeada_menos_spei"] >= -0.03 for n in MT); j2 = sum(res[n]["d_J2_semeada_menos_congelada"] >= -0.02 for n in MT)
    crua = sum(res[n]["auc_por_mes"]["v0 crua"] < res[n]["auc_por_mes"]["v0+org fria"] for n in MT)
    res["portao"] = bool(portao)
    res["J1"] = {"lugares": int(j1), "veredito": ("PASSA" if j1 >= 4 else "REPROVA") if portao else "INCONCLUSIVO"}
    res["J2"] = {"lugares": int(j2), "veredito": ("PASSA" if j2 >= 4 else "REPROVA") if portao else "INCONCLUSIVO"}
    res["aposta_crua_abaixo_da_fria"] = int(crua)
    for n in MT + ["juara (relatado)"]:
        o = res[n]; a = o["auc_por_mes"]
        print(f"{n:18s} seca {o['seca_medida']:4d} | " + " | ".join(f"{k} {v:.3f}" for k, v in a.items()))
        print(f"{'':18s} J1 {o['d_J1_semeada_menos_spei']:+.3f} (IC {o['ic_J1'][0]:+.3f}; {o['ic_J1'][1]:+.3f}) | J2 {o['d_J2_semeada_menos_congelada']:+.3f} "
              f"(IC {o['ic_J2'][0]:+.3f}; {o['ic_J2'][1]:+.3f}) | normal {o['normal_medio_mm_dia']['semente_2010_17']:+.2f} → {o['normal_medio_mm_dia']['semeada_fim_2025']:+.2f}"
              f" | comum: semeada {o['auc_comum']['v0+org semeada']:.3f} SPEI {o['auc_comum']['SPEI-90']:.3f}")
    print(f"== portão {'OK' if portao else 'FALHOU'} | J1 {j1}/5 → {res['J1']['veredito']} | J2 {j2}/5 → {res['J2']['veredito']} | crua abaixo da fria {crua}/5")
    (ROOT / "resultados_teste33.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
