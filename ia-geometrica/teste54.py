"""Teste 54: a sentinela sabe quando aprendeu? A v0 instalada a frio (normalização, projeção e ψ online, nada do futuro)
decide sozinha quando o andar aprendeu um ritmo (régua sequencial, α = 0,01), para de ouvir o campo e passa a olhar só a
entrada das águas. Predição: PREDICAO_teste54_sabe_quando_aprendeu.md (commit 310e0c3), escrita antes deste arquivo;
a sentinela está em sentinela.py (mesmo commit).

    python ia-geometrica/teste54.py        # o teste (exige a predição)
"""
import json, sys, time, zlib
from datetime import date
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sentinela as SN
import teste35 as T35
import teste51 as T51

ROOT = Path(__file__).resolve().parent
AVAL = list(range(2019, 2026)); NIC, SEMENTE, NR = 20, 51, 20
NUNCA = 10 ** 9


def brutos(n, nulo=False):
    """Os três sensores brutos do teste 51 (umidade do solo 28–100 cm, balanço P − ET0 em 7 dias, VPD). O nulo tira a
    climatologia de 2010–2017: é construção do mundo, a sentinela não a recebe."""
    D, P, E, S, V = T35.ler_juara() if n == "juara" else T35.ler_lugar(n)
    ano = np.array([int(d[:4]) for d in D]); cal = (ano >= 2010) & (ano <= 2017)
    doy = np.array([min(date.fromisoformat(d).timetuple().tm_yday, 365) for d in D])
    t = np.array([np.datetime64(d, "D").astype(int) for d in D], float)
    bal = np.convolve(P - E, np.ones(7) / 7)[:len(P)]
    X = [S, bal, V]
    if nulo: X = [v - T51.climatologia(v, doy, cal) for v in X]
    return D, P, t, np.column_stack(X)


def decl_mediana(decl):
    """decl (nIC, 4) -> mediana dos inícios por andar (NUNCA se a maioria não declarou)."""
    return np.median(np.where(decl < 0, NUNCA, decl), 0)


def piloto(ph0):
    """O piloto sintético da predição, com sementes determinísticas (o da predição usou hash() de Python, não reprodutível)."""
    t, ano, cal, s = T51.sinais("juara"); a = [T51.anual(t, cal, s[j]) for j in range(4)]
    sdr = [np.std(s[j][cal] - a[j][0] * np.cos(SN.OM * t[cal] + a[j][1])) for j in range(4)]
    TT = len(t); tt = np.arange(TT); D = [str(np.datetime64(int(x), "D")) for x in t]; i19 = D.index("2019-09-01"); out = {}
    for nome, com_ano, longo in (("com_ano", True, False), ("sem_ano", False, False), ("sem_ano_longo", False, True),
                                 ("com_ano_longo", True, True)):
        rng = np.random.default_rng(54 + zlib.crc32(nome.encode()) % 1000); dec = []
        for _ in range(NR):
            m = []
            for j in range(4):
                A, d = a[j]; tau = max(1 / SN.LAM[j], 365.0) if longo else 1 / SN.LAM[j]; r = np.exp(-1 / tau)
                e = np.zeros(TT); x = 0.0; nz = rng.normal(size=TT)
                for i in range(TT): x = r * x + np.sqrt(1 - r * r) * nz[i]; e[i] = x
                m.append((A * np.cos(SN.OM * tt + d) if com_ano else 0.0) + sdr[j] * e)
            dec.append(decl_mediana(SN.sentinela(np.array(m), ph0)["decl"][0]))
        dec = np.array(dec)
        out[nome] = {"algum_andar": float((dec < NUNCA).any(-1).mean()), "andar1": float((dec[:, 0] < NUNCA).mean()),
                     "andar2": float((dec[:, 1] < NUNCA).mean()), "andar2_antes_1set2019": float((dec[:, 1] < i19).mean()),
                     "mediana_declaracao_andar2_anos": (float(np.median(dec[:, 1][dec[:, 1] < NUNCA]) / 365.25)
                                                        if (dec[:, 1] < NUNCA).any() else None)}
        print("piloto", nome, out[nome], flush=True)
    return out


def rodar(s, ph0, aprende=True):
    r = SN.sentinela(s, ph0, aprende=aprende)
    return r["decl"][0], r["PH"][:, 0, :], r["W"][:, 0, :]


def main():
    assert (ROOT / "PREDICAO_teste54_sabe_quando_aprendeu.md").exists(), "sem predição, sem teste"
    ph0 = np.random.default_rng(SEMENTE).uniform(0, 2 * np.pi, (NIC, 4))[:, 1]
    r36 = json.loads((ROOT / "resultados_teste36.json").read_text())["real"]
    r53 = json.loads((ROOT / "resultados_teste53.json").read_text())
    t0 = time.time(); res = {"piloto_sintetico": piloto(ph0), "lugares": {}}
    print(f"piloto em {time.time() - t0:.0f} s", flush=True)
    mu_reg = float(np.mean([r36[n]["mu0"] for n in T35.LUGARES]))
    E = {k: [] for k in ("sentinela", "controle", "C", "V1", "C_regional")}
    for n in T35.LUGARES:
        D, P, t, X = brutos(n); idx = {d: i for i, d in enumerate(D)}; ent = T35.entradas(D, P)
        i19 = idx["2019-09-01"]
        s = SN.projetar_online(SN.cascata(SN.normalizar_online(X)))
        dec, PH, W = rodar(s, ph0); decc, PHc, Wc = rodar(s, ph0, aprende=False)
        Dn, Pn, tn, Xn = brutos(n, nulo=True)
        decn, _, _ = rodar(SN.projetar_online(SN.cascata(SN.normalizar_online(Xn))), ph0)
        dm, dmc, dmn = decl_mediana(dec), decl_mediana(decc), decl_mediana(decn)
        ok2 = dec[:, 1] >= 0
        w_decl = float(np.median(W[dec[ok2, 1], np.flatnonzero(ok2)]) / SN.OM) if ok2.any() else None
        ent_doy = np.array(r36[n]["entradas"]); mu0 = r36[n]["mu0"]
        linha = {"C": (ent_doy - mu0)[1:], "V1": (ent_doy - np.array(r36[n]["previsoes"]))[1:], "C_regional": (ent_doy - mu_reg)[1:]}
        for k, (ph, w) in (("sentinela", (PH, W)), ("controle", (PHc, Wc))):
            pv = SN.previsoes(ph, w, t, idx, ent, AVAL)
            linha[k] = np.array([t[ent[y]] - np.median(pv[y]) for y in AVAL])
            if k == "sentinela":
                esp = float(np.mean([np.quantile(pv[y], .9) - np.quantile(pv[y], .1) for y in AVAL]))
        for k in E: E[k].append(np.asarray(linha[k], float))
        anos = lambda d: [None if x >= NUNCA else round(float(x) / 365.25, 2) for x in d]
        res["lugares"][n] = {
            "declaracao_anos_por_andar": anos(dm), "declaracao_data_andar2": None if dm[1] >= NUNCA else D[int(dm[1])],
            "fracao_inicios_declarou_por_andar": (dec >= 0).mean(0).tolist(), "w2_na_declaracao_sobre_Omega": w_decl,
            "w2_fim_sobre_Omega": float(np.median(W[-1]) / SN.OM), "dias_ouvindo_andar2": None if dm[1] >= NUNCA else int(dm[1]),
            "controle_declaracao_anos": anos(dmc), "controle_w2_fim_sobre_Omega": float(np.median(Wc[-1]) / SN.OM),
            "nulo_declaracao_anos": anos(dmn), "nulo_fracao_inicios_declarou": (decn >= 0).mean(0).tolist(),
            "J1_lugar": bool(dm[1] < i19 and w_decl is not None and abs(w_decl - 1) <= 0.05),
            "J2_lugar": bool((dmn >= NUNCA).all()),
            "EAM": {k: float(np.abs(linha[k]).mean()) for k in E}, "vies": {k: float(np.mean(linha[k])) for k in E},
            "erros_sentinela": np.round(linha["sentinela"], 1).tolist(), "espalhamento_p10_p90": esp}
        o = res["lugares"][n]
        print(f"{n:16s} declara (anos, andares 1–4) {o['declaracao_anos_por_andar']} em {o['declaracao_data_andar2']}, ω₂/Ω "
              f"{w_decl if w_decl is None else round(w_decl, 3)} | nulo {o['nulo_declaracao_anos']} | controle {o['controle_declaracao_anos']}"
              f" | EAM " + " · ".join(f"{k} {v:.1f}" for k, v in o["EAM"].items()), flush=True)
    E = {k: np.array(v) for k, v in E.items()}
    eam = {k: float(np.abs(v).mean()) for k, v in E.items()}; vies = {k: float(v.mean()) for k, v in E.items()}
    eam["S_teste53"] = r53["EAM"]["S"]
    L = res["lugares"].values()
    J = {"J1": sum(o["J1_lugar"] for o in L) >= 5, "J2": sum(o["J2_lugar"] for o in L) >= 5,
         "J3": eam["sentinela"] <= eam["C"] + 3.0}
    res.update({"EAM": eam, "vies": vies, "mu_regional": mu_reg, "J": {k: bool(v) for k, v in J.items()}})
    print("EAM " + " · ".join(f"{k} {v:.1f}" for k, v in eam.items()) + " | viés " + " · ".join(f"{k} {v:+.1f}" for k, v in vies.items()))
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste54.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
