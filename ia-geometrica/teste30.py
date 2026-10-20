"""Teste 30 (a seca silenciosa em Juara): o registro da v0 sobre o balanço de água da superfície acompanha a seca do solo profundo,
inclusive quando a superfície está molhada? Predição: PREDICAO_teste30_seca_silenciosa.md.

Dados: ia-geometrica/clima/dados/era5land_juara_horario.csv.gz (ERA5-Land + ERA5 via Open-Meteo, 2010–2025, ponto em Juara).

    python ia-geometrica/teste30.py --colunas   # só confere colunas e linhas; não lê valores
    python ia-geometrica/teste30.py             # o teste (exige a predição)
"""
import argparse, csv, gzip, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
DADOS = ROOT / "clima" / "dados" / "era5land_juara_horario.csv.gz"
CAL = (2010, 2017); MED = (2018, 2025)                  # calibração (climatologia, régua, escolhas) e medida
LIMIAR_SECA = -1.0                                      # dia de seca profunda: anomalia padronizada da camada 28–100 cm ≤ −1
JANELAS = (30, 90, 180)                                 # dias, para SPI e SPEI simplificados
BLOCO, NBOOT = 90, 1000


def ler_diario():
    """Agrega por dia local: chuva e ET0 somadas; umidades do solo em média."""
    with gzip.open(DADOS, "rt") as f:
        r = csv.reader(f); h = next(r); idx = {c: i for i, c in enumerate(h)}; dias = {}
        for row in r:
            d = row[0][:10]; v = dias.setdefault(d, {"P": 0.0, "ET0": 0.0, "s0": [], "s3": [], "n": 0})
            v["P"] += float(row[idx["precipitation"]]); v["ET0"] += float(row[idx["et0_fao_evapotranspiration"]])
            v["s0"].append(float(row[idx["soil_moisture_0_to_7cm"]])); v["s3"].append(float(row[idx["soil_moisture_28_to_100cm"]])); v["n"] += 1
    D = sorted(d for d in dias if dias[d]["n"] == 24)
    ano = np.array([int(d[:4]) for d in D]); doy = np.array([min(np.datetime64(d).astype("datetime64[D]").item().timetuple().tm_yday, 365) for d in D])
    P = np.array([dias[d]["P"] for d in D]); E = np.array([dias[d]["ET0"] for d in D])
    s0 = np.array([np.mean(dias[d]["s0"]) for d in D]); s3 = np.array([np.mean(dias[d]["s3"]) for d in D])
    return D, ano, doy, P, E, s0, s3


def climatologia(v, doy, cal):
    """Média e desvio por dia do ano na calibração, suavizados por média móvel circular de 31 dias."""
    m = np.array([v[cal & (doy == k)].mean() for k in range(1, 366)]); s = np.array([v[cal & (doy == k)].std() for k in range(1, 366)])
    k = np.ones(31) / 31; sm = lambda a: np.convolve(np.concatenate([a[-15:], a, a[:15]]), k, "valid")
    return sm(m)[doy - 1], np.maximum(sm(s), 1e-9)[doy - 1]


def auc(score, y):
    """AUC de `score` (maior = mais seco) para y = 1 (seca profunda); Mann–Whitney por postos."""
    y = np.asarray(y, bool); n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0: return float("nan")
    from scipy.stats import rankdata
    rk = rankdata(score); return float((rk[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def acumulado(u, k):
    return np.convolve(u, np.ones(k))[:len(u)]


def indices(P, E, cal, doy):
    """Nulos: SPI e SPEI simplificados (soma de k dias da anomalia de chuva, ou de chuva − ET0, padronizada por dia do ano na calibração)."""
    out = {}
    for nome, base in (("SPI", P), ("SPEI", P - E)):
        mb, _ = climatologia(base, doy, cal); u = base - mb
        for k in JANELAS:
            a = acumulado(u, k); m, s = climatologia(a, doy, cal); out[f"{nome}-{k}"] = (a - m) / s
    return out


def leituras_v0(P, E, cal, doy):
    """A v0 sem mudança (λ₁ = 0,15, b = 10; passo = 1 dia: τ ≈ 7 d, 67 d, 1,8 ano, 18 anos) sobre a anomalia diária de chuva − ET0."""
    base = P - E; mb, _ = climatologia(base, doy, cal); u = (base - mb)[:, None]
    obs = V.Observador(1); _, _, Rh = V.rodar(u, obs); R = Rh[:, :, 0]
    cand = {"R1": R[:, 0], "R2": R[:, 1], "R3": R[:, 2], "R1-R3": R[:, 0] - R[:, 2], "R2-R3": R[:, 1] - R[:, 2], "R2-R4": R[:, 1] - R[:, 3]}
    return cand, obs.lams


def bloco_boot(n, rng):
    nb = int(np.ceil(n / BLOCO)); ini = rng.integers(0, n - BLOCO + 1, nb)
    return np.concatenate([np.arange(i, i + BLOCO) for i in ini])[:n]


def colunas():
    with gzip.open(DADOS, "rt") as f:
        h = next(csv.reader(f)); n = sum(1 for _ in f)
    print("colunas:", h); print("linhas:", n); print("nenhum valor lido")


def main():
    assert (ROOT / "PREDICAO_teste30_seca_silenciosa.md").exists(), "sem predição, sem teste"
    D, ano, doy, P, E, s0, s3 = ler_diario()
    cal = (ano >= CAL[0]) & (ano <= CAL[1]); med = (ano >= MED[0]) & (ano <= MED[1])
    m3, d3 = climatologia(s3, doy, cal); m0, d0 = climatologia(s0, doy, cal)
    z3 = (s3 - m3) / d3; z0 = (s0 - m0) / d0; seca = z3 <= LIMIAR_SECA; silencio = z0 >= 0
    nulos = indices(P, E, cal, doy); cand, lams = leituras_v0(P, E, cal, doy)
    aquec = 365                                                   # o primeiro ano não entra na escolha (registros enchendo)
    calj = cal & (np.arange(len(D)) >= aquec)
    a_nulo_cal = {k: auc(-v[calj], seca[calj]) for k, v in nulos.items()}; a_v0_cal = {k: auc(-v[calj], seca[calj]) for k, v in cand.items()}
    k_nulo = max(a_nulo_cal, key=a_nulo_cal.get); k_v0 = max(a_v0_cal, key=a_v0_cal.get)
    sn = -nulos[k_nulo]; sv = -cand[k_v0]
    i_med = np.flatnonzero(med); i_sil = np.flatnonzero(med & silencio)
    res = {"dias": {"calibracao": int(cal.sum()), "medida": int(med.sum()), "seca_medida": int(seca[med].sum()),
                    "silenciosos_medida": int((med & silencio).sum()), "seca_silenciosa_medida": int((med & silencio & seca).sum())},
           "escolhas_na_calibracao": {"nulo": k_nulo, "v0": k_v0, "auc_cal_nulos": a_nulo_cal, "auc_cal_v0": a_v0_cal}, "lams": lams.tolist()}
    rng = np.random.default_rng(30)
    for nome, ii in (("todos", i_med), ("silenciosos", i_sil)):
        av, an = auc(sv[ii], seca[ii]), auc(sn[ii], seca[ii]); bv, bd = [], []
        for _ in range(NBOOT):
            j = ii[bloco_boot(len(ii), rng)]; x, y = auc(sv[j], seca[j]), auc(sn[j], seca[j]); bv.append(x); bd.append(x - y)
        res[nome] = {"auc_v0": av, "auc_nulo": an, "dif": av - an, "ic_v0": [float(np.nanquantile(bv, .025)), float(np.nanquantile(bv, .975))],
                     "ic_dif": [float(np.nanquantile(bd, .025)), float(np.nanquantile(bd, .975))]}
    sil_ok = res["dias"]["seca_silenciosa_medida"] >= 30 and (res["dias"]["silenciosos_medida"] - res["dias"]["seca_silenciosa_medida"]) >= 30
    j1 = bool(res["todos"]["auc_v0"] >= 0.80 and res["todos"]["ic_v0"][0] > 0.5)
    j2 = (bool(res["silenciosos"]["dif"] >= 0.03 and res["silenciosos"]["ic_dif"][0] > 0) if sil_ok else None)
    res["J1"] = j1; res["J2"] = j2 if j2 is not None else "INCONCLUSIVO"
    print(json.dumps(res["dias"], ensure_ascii=False)); print("escolhas:", k_nulo, k_v0)
    for nome in ("todos", "silenciosos"):
        r = res[nome]; print(f"== {nome}: AUC v0 {r['auc_v0']:.3f} (IC {r['ic_v0'][0]:.3f}–{r['ic_v0'][1]:.3f}) | nulo {r['auc_nulo']:.3f} | dif {r['dif']:+.3f} (IC {r['ic_dif'][0]:+.3f}; {r['ic_dif'][1]:+.3f})")
    print(f"   J1 {'PASSA' if j1 else 'REPROVA'} | J2 {res['J2'] if j2 is None else ('PASSA' if j2 else 'REPROVA')}")
    (ROOT / "resultados_teste30.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--colunas", action="store_true")
    colunas() if ap.parse_args().colunas else main()
