"""Teste 35 (o relógio v2): um oscilador de fase que nunca se reinicia, semeado com o laço do ano e acoplado com força K à fase
que o mundo mostra no andar 1 da v0, antecipa a entrada das águas melhor que o calendário (K = 0)? Ótimo em K interior?
Predição: PREDICAO_teste35_relogio_v2.md (commit bb0b920), escrita antes deste arquivo.

    python ia-geometrica/teste35.py        # o teste (exige a predição)
"""
import csv, gzip, json, sys
from datetime import date
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste30 as T30

ROOT = Path(__file__).resolve().parent; LUG = ROOT / "clima" / "dados" / "lugares"
LUGARES = ["juara", "sinop", "cuiaba", "barra_do_garcas", "alta_floresta", "rondonopolis"]
CAL, MED = (2010, 2017), (2018, 2025)
OMEGA = 2 * np.pi / 365.25; LAM1 = 0.15
KS = [0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.2, 0.5]
LEADS = {"01/09": (9, 1), "15/08": (8, 15), "15/09": (9, 15)}
NBOOT, SEMENTE = 1000, 35


# ---------------------------------------------------------------- dados
def ler_lugar(nome):
    with open(LUG / f"{nome}.csv") as f:
        r = [x for x in csv.DictReader(f) if int(x["horas"]) == 24]
    g = lambda k: np.array([float(x[k]) for x in r])
    return [x["dia"] for x in r], g("chuva_mm"), g("et0_mm"), g("solo_28_100"), g("vpd_kpa")


def ler_juara():
    D, ano, doy, P, E, s0, s3 = T30.ler_diario(); vpd = {}
    with gzip.open(T30.DADOS, "rt") as f:
        r = csv.reader(f); h = next(r); iv = h.index("vapour_pressure_deficit")
        for row in r: vpd.setdefault(row[0][:10], []).append(float(row[iv]))
    return D, P, E, s3, np.array([np.mean(vpd[d]) for d in D])


# ---------------------------------------------------------------- o relógio
def base(t):
    return np.column_stack([np.ones_like(t), np.sin(OMEGA * t), np.cos(OMEGA * t), np.sin(2 * OMEGA * t), np.cos(2 * OMEGA * t)])


def preparar(D, P, E, S, V):
    t = np.array([np.datetime64(d, "D").astype(int) for d in D], float); ano = np.array([int(d[:4]) for d in D])
    cal = (ano >= CAL[0]) & (ano <= CAL[1])
    bal = np.convolve(P - E, np.ones(7) / 7)[:len(P)]
    z = lambda v: (v - v[cal].mean()) / v[cal].std()
    x = np.column_stack([z(S), z(bal), z(V)])
    R1 = np.zeros_like(x); r = np.zeros(3)                      # andar 1 da v0, começa no normal
    for i in range(len(x)): r = r + LAM1 * (x[i] - r); R1[i] = r
    beta = np.linalg.lstsq(base(t[cal]), R1[cal], rcond=None)[0]   # laço semeado (5 × 3), congelado
    Bm = np.column_stack([beta[2], beta[1]])                    # colunas cos, sen
    v = (np.linalg.pinv(Bm) @ (R1 - beta[0]).T).T
    theta = np.arctan2(v[:, 1], v[:, 0])
    return t, ano, theta


def relogio(t, theta, K):
    phi = np.zeros(len(t)); phi[0] = OMEGA * t[0]
    for i in range(1, len(t)):
        phi[i] = phi[i - 1] + OMEGA * (t[i] - t[i - 1]) + K * np.sin(theta[i] - phi[i - 1])
    return phi


# ---------------------------------------------------------------- a entrada das águas
def entradas(D, P):
    idx = {d: i for i, d in enumerate(D)}; out = {}
    for y in range(CAL[0], MED[1] + 1):
        i0 = idx.get(f"{y}-08-01"); fim = idx.get(f"{y}-12-31", len(D) - 1)
        out[y] = None
        if i0 is None: continue
        for d in range(i0, fim + 1):
            if d + 4 >= len(P) or P[d:d + 5].sum() < 25: continue
            seco, ok = 0, True
            for k in range(d + 1, min(d + 31, len(P))):
                seco = seco + 1 if P[k] < 1 else 0
                if seco >= 10: ok = False; break
            if ok: out[y] = d; break
    return out


def circ_media(a):
    return float(np.angle(np.mean(np.exp(1j * np.asarray(a)))))


def previsoes(D, t, ano, theta, ent, K, lead):
    """Erro com sinal (previsto − real, dias) por ano; φ_entrada da calibração com o mesmo K."""
    phi = relogio(t, theta, K); idx = {d: i for i, d in enumerate(D)}
    phis_cal = [phi[ent[y]] for y in range(CAL[0], CAL[1] + 1) if ent[y] is not None]
    phi_on = circ_media(np.mod(phis_cal, 2 * np.pi))
    err, anom = {}, {}
    for y in range(CAL[0], MED[1] + 1):
        i0 = idx.get(f"{y}-{lead[0]:02d}-{lead[1]:02d}")
        if ent[y] is None or i0 is None: err[y] = None; continue
        prev = t[i0] + np.mod(phi_on - phi[i0], 2 * np.pi) / OMEGA
        err[y] = float(prev - t[ent[y]])
        anom[y] = float(np.angle(np.exp(1j * (phi[i0] - OMEGA * t[i0]))) / OMEGA)   # φ(t₀) − ωt₀, em dias
    return err, anom


# ---------------------------------------------------------------- main
def main():
    assert (ROOT / "PREDICAO_teste35_relogio_v2.md").exists(), "sem predição, sem teste"
    dados = {}
    for n in LUGARES:
        D, P, E, S, V = ler_juara() if n == "juara" else ler_lugar(n)
        t, ano, theta = preparar(D, P, E, S, V); dados[n] = (D, P, t, ano, theta, entradas(D, P))
    res = {"K_grade": KS, "entradas": {n: {y: (None if d is None else dados[n][0][d]) for y, d in dados[n][5].items()} for n in LUGARES}}

    def tabela(lead):
        E = {}   # E[K][(lugar, ano)] = erro
        A = {}
        for K in KS:
            E[K] = {}; A[K] = {}
            for n in LUGARES:
                D, P, t, ano, theta, ent = dados[n]; err, anom = previsoes(D, t, ano, theta, ent, K, LEADS[lead])
                for y, e in err.items():
                    if e is not None: E[K][(n, y)] = e; A[K][(n, y)] = anom.get(y)
        return E, A

    E, A = tabela("01/09")
    chaves_cal = [k for k in E[0] if CAL[0] <= k[1] <= CAL[1]]; chaves_med = [k for k in E[0] if MED[0] <= k[1] <= MED[1]]
    eam = lambda K, ch: float(np.mean([abs(E[K][k]) for k in ch]))
    vies = lambda K, ch: float(np.mean([E[K][k] for k in ch]))
    eam_cal = {K: eam(K, chaves_cal) for K in KS}; Kst = min(KS, key=lambda K: eam_cal[K])
    eam_med = {K: eam(K, chaves_med) for K in KS}
    dif = eam_med[Kst] - eam_med[0]
    rng = np.random.default_rng(SEMENTE); bd = []
    for _ in range(NBOOT):
        s = [chaves_med[i] for i in rng.integers(0, len(chaves_med), len(chaves_med))]
        bd.append(np.mean([abs(E[Kst][k]) for k in s]) - np.mean([abs(E[0][k]) for k in s]))
    ic = [float(np.quantile(bd, .025)), float(np.quantile(bd, .975))]
    j1 = bool(dif <= -3 and ic[1] < 0)
    imin = int(np.argmin([eam_med[K] for K in KS])); Kmin = KS[imin]
    j2 = bool(0 < imin < len(KS) - 1 and eam_med[Kmin] <= min(eam_med[0], eam_med[KS[-1]]) - 2)

    # correlação anomalia de fase (K*) × anomalia da entrada, na medida
    media_cal = {n: circ_media([2 * np.pi * (date.fromisoformat(dados[n][0][dados[n][5][y]]).timetuple().tm_yday) / 365.25
                                 for y in range(CAL[0], CAL[1] + 1) if dados[n][5][y] is not None]) * 365.25 / (2 * np.pi) for n in LUGARES}
    pa, po = [], []
    for k in chaves_med:
        n, y = k; doy = date.fromisoformat(dados[n][0][dados[n][5][y]]).timetuple().tm_yday
        pa.append(A[Kst][k]); po.append(doy - media_cal[n])
    rho = float(np.corrcoef(pa, po)[0, 1])
    doys = [date.fromisoformat(v).timetuple().tm_yday for n in LUGARES for y, v in res["entradas"][n].items() if v]
    res.update({
        "K_estrela": Kst, "EAM_cal": eam_cal, "EAM_med": eam_med, "dif_Kst_menos_0": dif, "ic_dif": ic,
        "vies_med": {"K0": vies(0, chaves_med), "Kst": vies(Kst, chaves_med)},
        "n_previsoes": {"cal": len(chaves_cal), "med": len(chaves_med)},
        "anos_sem_entrada": {n: [y for y, d in dados[n][5].items() if d is None] for n in LUGARES},
        "por_lugar_med": {n: {"EAM_K0": float(np.mean([abs(E[0][k]) for k in chaves_med if k[0] == n])),
                              "EAM_Kst": float(np.mean([abs(E[Kst][k]) for k in chaves_med if k[0] == n])),
                              "vies_K0": float(np.mean([E[0][k] for k in chaves_med if k[0] == n])),
                              "vies_Kst": float(np.mean([E[Kst][k] for k in chaves_med if k[0] == n]))} for n in LUGARES},
        "corr_fase_entrada_med": rho, "dp_entrada_doy_todos": float(np.std(doys)),
        "J1": {"passa": j1}, "J2": {"K_min_med": Kmin, "passa": j2},
    })
    for lead in ["15/08", "15/09"]:
        El, _ = tabela(lead); cm = [k for k in El[0] if MED[0] <= k[1] <= MED[1]]
        res[f"EAM_med_{lead}"] = {K: float(np.mean([abs(El[K][k]) for k in cm])) for K in KS}
    res["apostas"] = {"corr_atraso_anuncia_atraso_(phi−ωt ≤ −0,3)": bool(rho <= -0.3),
                      "EAM_calendario_10_20": bool(10 <= eam_med[0] <= 20)}

    print("entradas (dia do ano) por lugar:")
    for n in LUGARES:
        print(f"  {n:16s} " + " ".join(f"{y % 100:02d}:{'—' if v is None else date.fromisoformat(v).timetuple().tm_yday}" for y, v in res["entradas"][n].items()))
    print("EAM cal  " + " ".join(f"{K}:{v:.1f}" for K, v in eam_cal.items()))
    print("EAM med  " + " ".join(f"{K}:{v:.1f}" for K, v in eam_med.items()))
    for lead in ["15/08", "15/09"]:
        print(f"EAM med {lead} " + " ".join(f"{K}:{v:.1f}" for K, v in res[f'EAM_med_{lead}'].items()))
    print(f"K* {Kst} | dif {dif:+.2f} d (IC {ic[0]:+.2f}; {ic[1]:+.2f}) | viés med K0 {res['vies_med']['K0']:+.1f} K* {res['vies_med']['Kst']:+.1f}"
          f" | n {res['n_previsoes']} | corr(φ−ωt, entrada) {rho:+.3f} | dp entrada {res['dp_entrada_doy_todos']:.1f} d")
    for n, o in res["por_lugar_med"].items():
        print(f"  {n:16s} EAM K0 {o['EAM_K0']:.1f} K* {o['EAM_Kst']:.1f} | viés K0 {o['vies_K0']:+.1f} K* {o['vies_Kst']:+.1f}")
    print(f"== J1 → {'PASSA' if j1 else 'REPROVA'} | J2 (mínimo em K = {Kmin}) → {'PASSA' if j2 else 'REPROVA'} | apostas {res['apostas']}")
    (ROOT / "resultados_teste35.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))


def diagnostico():
    """Depois da rodada, NÃO julgado: (a) quantas previsões a regra mod 2π jogou um ano para frente; (b) o EAM com a fase
    embrulhada em (−π, π], que deixa o relógio dizer "a entrada já passou"; (c) a correlação φ(t₀) − ωt₀ × anomalia da
    entrada para K > 0 (com K* = 0 ela é degenerada: φ − ωt ≡ 0 a menos de arredondamento)."""
    out = {}
    dados = {}
    for n in LUGARES:
        D, P, E, S, V = ler_juara() if n == "juara" else ler_lugar(n)
        t, ano, theta = preparar(D, P, E, S, V); dados[n] = (D, t, theta, entradas(D, P))
    for K in KS:
        salto, ae_mod, ae_emb, pa, po = 0, [], [], [], []
        for n in LUGARES:
            D, t, theta, ent = dados[n]; phi = relogio(t, theta, K); idx = {d: i for i, d in enumerate(D)}
            pc = [phi[ent[y]] for y in range(CAL[0], CAL[1] + 1) if ent[y] is not None]; phi_on = circ_media(np.mod(pc, 2 * np.pi))
            doys = [date.fromisoformat(D[ent[y]]).timetuple().tm_yday for y in range(CAL[0], CAL[1] + 1) if ent[y] is not None]
            for y in range(MED[0], MED[1] + 1):
                i0 = idx[f"{y}-09-01"]
                if ent[y] is None: continue
                e_mod = t[i0] + np.mod(phi_on - phi[i0], 2 * np.pi) / OMEGA - t[ent[y]]
                e_emb = t[i0] + np.angle(np.exp(1j * (phi_on - phi[i0]))) / OMEGA - t[ent[y]]
                salto += int(abs(e_mod - e_emb) > 300); ae_mod.append(abs(e_mod)); ae_emb.append(abs(e_emb))
                pa.append(np.angle(np.exp(1j * (phi[i0] - OMEGA * t[i0]))) / OMEGA)
                po.append(date.fromisoformat(D[ent[y]]).timetuple().tm_yday - np.mean(doys))
        r = float(np.corrcoef(pa, po)[0, 1]) if np.std(pa) > 1e-6 else None
        out[K] = {"saltos_de_um_ano": salto, "EAM_mod": float(np.mean(ae_mod)), "EAM_embrulhado": float(np.mean(ae_emb)), "corr_fase_entrada": r}
        print(f"K {K:<6} saltos {salto:2d} | EAM mod {np.mean(ae_mod):5.1f} | EAM embrulhado {np.mean(ae_emb):5.1f} | corr(φ−ωt, entrada) {'—' if r is None else f'{r:+.3f}'}")
    (ROOT / "diagnostico_teste35.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    diagnostico() if "--diagnostico" in sys.argv else main()
