"""Teste 32 (a organização aprende o ano): uma organização ⋄ que aprende sozinha o ciclo anual do lugar (mínimos quadrados
recursivos, 5 coeficientes, sem esquecimento, começando fria) entrega à memória da v0 um desvio do normal que lê a seca
profunda tão bem quanto o SPEI-90 com 8 anos de climatologia? Predição: PREDICAO_teste32_organizacao_aprende_o_ano.md.

    python ia-geometrica/teste32.py        # o teste (exige a predição)
"""
import csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v0 as V
import teste30 as T30
from teste31 import fracao_anual

ROOT = Path(__file__).resolve().parent; LUG = ROOT / "clima" / "dados" / "lugares"
MT = ["sinop", "cuiaba", "barra_do_garcas", "alta_floresta", "rondonopolis"]
CAL = (2010, 2017); INICIO_FRIO = 2018; MED = (2019, 2025)
OMEGA = 2 * np.pi / 365.25; P0 = 1e3


# ---------------------------------------------------------------- a organização ⋄
class Organizacao:
    """Ciclo do ano em 5 coeficientes, aprendido por mínimos quadrados recursivos sem esquecimento. 20 números por grandeza."""

    def __init__(self):
        self.beta = np.zeros(5); self.P = P0 * np.eye(5)

    @staticmethod
    def base(t):
        return np.array([1.0, np.sin(OMEGA * t), np.cos(OMEGA * t), np.sin(2 * OMEGA * t), np.cos(2 * OMEGA * t)])

    def passo(self, t, x):
        """Prevê antes de olhar (u = x − normal esperado), depois aprende com x."""
        f = self.base(t); u = x - f @ self.beta
        Pf = self.P @ f; k = Pf / (1.0 + f @ Pf)
        self.beta = self.beta + k * u; self.P = self.P - np.outer(k, Pf)
        return u


def organizar(x, t):
    org = Organizacao(); return np.array([org.passo(t[i], x[i]) for i in range(len(x))]), org


def r2(u):
    obs = V.Observador(1); obs.R[:] = 0.0; _, _, Rh = V.rodar(np.asarray(u, float)[:, None], obs); return Rh[:, :, 0]


# ---------------------------------------------------------------- dados
def ler_lugar(nome):
    with open(LUG / f"{nome}.csv") as f:
        r = [x for x in csv.DictReader(f) if int(x["horas"]) == 24]
    D = [x["dia"] for x in r]; g = lambda k: np.array([float(x[k]) for x in r])
    return D, g("chuva_mm"), g("et0_mm"), g("solo_28_100")


def ler_juara():
    D, ano, doy, P, E, s0, s3 = T30.ler_diario(); return D, P, E, s3


# ---------------------------------------------------------------- o lugar
def lugar(D, P, E, S, rng):
    ano = np.array([int(d[:4]) for d in D]); t = np.array([np.datetime64(d, "D").astype(int) for d in D], float)
    doy = np.array([min(np.datetime64(d, "D").item().timetuple().tm_yday, 365) for d in D])
    cal = (ano >= CAL[0]) & (ano <= CAL[1]); med = (ano >= MED[0]) & (ano <= MED[1]); frio = ano >= INICIO_FRIO
    m3, d3 = T30.climatologia(S, doy, cal); seca = (S - m3) / d3 <= T30.LIMIAR_SECA
    x = P - E; n = len(x); i0 = int(np.flatnonzero(frio)[0])

    series = {}
    u_frio, org_frio = organizar(x[i0:], t[i0:]); R_org = r2(u_frio); R_cru = r2(x[i0:])
    s = np.full(n, np.nan); s[i0:] = R_org[:, 1]; series["v0+org fria"] = s
    s = np.full(n, np.nan); s[i0:] = R_cru[:, 1]; series["v0 crua fria"] = s
    series["SPEI-90"] = T30.indices(P, E, cal, doy)["SPEI-90"]
    mb, _ = T30.climatologia(x, doy, cal); series["v0 clim. fixa"] = r2(x - mb)[:, 1]
    u_morna, _ = organizar(x, t); series["v0+org morna"] = r2(u_morna)[:, 1]

    im = np.flatnonzero(med)
    out = {"dias_medida": int(med.sum()), "seca_medida": int(seca[med].sum()),
           "auc": {k: T30.auc(-v[im], seca[im]) for k, v in series.items()}}
    a = out["auc"]
    out["dif_org_menos_cru"] = a["v0+org fria"] - a["v0 crua fria"]
    out["dif_org_menos_spei"] = a["v0+org fria"] - a["SPEI-90"]
    out["dif_morna_menos_fixa"] = a["v0+org morna"] - a["v0 clim. fixa"]
    bd = []
    for _ in range(T30.NBOOT):
        j = im[T30.bloco_boot(len(im), rng)]
        bd.append(T30.auc(-series["v0+org fria"][j], seca[j]) - T30.auc(-series["SPEI-90"][j], seca[j]))
    out["ic_dif_org_menos_spei"] = [float(np.nanquantile(bd, .025)), float(np.nanquantile(bd, .975))]
    por_ano = {}
    for y in range(MED[0], MED[1] + 1):
        iy = np.flatnonzero(ano == y)
        if seca[iy].sum() >= 10 and (~seca[iy]).sum() >= 10:
            por_ano[y] = T30.auc(-series["v0+org fria"][iy], seca[iy]) - T30.auc(-series["SPEI-90"][iy], seca[iy])
        else:
            por_ano[y] = None
    out["dif_org_menos_spei_por_ano"] = por_ano
    mm = med[i0:]
    out["fracao_anual_andares_1_2"] = {"com_org": [fracao_anual(R_org[mm, j][:, None], t[i0:][mm]) for j in (0, 1)],
                                       "sem_org": [fracao_anual(R_cru[mm, j][:, None], t[i0:][mm]) for j in (0, 1)]}
    out["ciclo_aprendido_2025"] = org_frio.beta.tolist()
    return out


def main():
    assert (ROOT / "PREDICAO_teste32_organizacao_aprende_o_ano.md").exists(), "sem predição, sem teste"
    rng = np.random.default_rng(32); res = {}
    for nome in MT:
        res[nome] = lugar(*ler_lugar(nome), rng)
    res["juara (relatado)"] = lugar(*ler_juara(), rng)
    j1n = sum(res[n]["dif_org_menos_cru"] >= 0.05 for n in MT); j2n = sum(res[n]["dif_org_menos_spei"] >= -0.03 for n in MT)
    res["J1"] = {"lugares": int(j1n), "passa": bool(j1n >= 4)}; res["J2"] = {"lugares": int(j2n), "passa": bool(j2n >= 4)}
    ap1 = 0
    for n in MT:
        pa = res[n]["dif_org_menos_spei_por_ano"]; fim = [v for y, v in pa.items() if y >= 2023 and v is not None]
        ap1 += bool(pa.get(2019) is not None and fim and pa[2019] < np.mean(fim))
    res["aposta_2019_pior_que_2023_25"] = int(ap1)
    res["aposta_morna_vs_fixa_002"] = int(sum(abs(res[n]["dif_morna_menos_fixa"]) <= 0.02 for n in MT))
    for n in MT + ["juara (relatado)"]:
        o = res[n]; a = o["auc"]
        print(f"{n:18s} seca {o['seca_medida']:4d} | " + " | ".join(f"{k} {v:.3f}" for k, v in a.items())
              + f" | org−SPEI {o['dif_org_menos_spei']:+.3f} (IC {o['ic_dif_org_menos_spei'][0]:+.3f}; {o['ic_dif_org_menos_spei'][1]:+.3f})")
        print(f"{'':18s} por ano org−SPEI: " + " ".join(f"{y}:{'—' if v is None else f'{v:+.2f}'}" for y, v in o["dif_org_menos_spei_por_ano"].items())
              + f" | fração anual andares 1–2 com ⋄ {o['fracao_anual_andares_1_2']['com_org'][0]:.2f} {o['fracao_anual_andares_1_2']['com_org'][1]:.2f}"
              + f", sem ⋄ {o['fracao_anual_andares_1_2']['sem_org'][0]:.2f} {o['fracao_anual_andares_1_2']['sem_org'][1]:.2f}")
    print(f"== J1 {j1n}/5 → {'PASSA' if j1n >= 4 else 'REPROVA'} | J2 {j2n}/5 → {'PASSA' if j2n >= 4 else 'REPROVA'}"
          f" | aposta 2019 pior: {ap1}/5 | morna ≈ fixa (±0,02): {res['aposta_morna_vs_fixa_002']}/5")
    (ROOT / "resultados_teste32.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
