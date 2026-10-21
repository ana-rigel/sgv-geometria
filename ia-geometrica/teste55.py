"""Teste 55: a sentinela do dia. Dado horário de Juara (ERA5-Land), 15 instalações a frio de um ano (2010–2024, meses
espalhados); sentinela55 com ε = 0,4, η_w = ε/365, janela de 3 períodos, α = 0,001 e a correção do defeito 75.
Predição: PREDICAO_teste55_sentinela_do_dia.md (commit a0f1e2a), escrita antes deste arquivo; a sentinela está em
sentinela55.py (mesmo commit).

    python ia-geometrica/teste55.py        # o teste (exige a predição)
"""
import csv, gzip, json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sentinela55 as S5

ROOT = Path(__file__).resolve().parent
DADOS = ROOT / "clima" / "dados" / "era5land_juara_horario.csv.gz"
SENSORES = ("temperature_2m", "relative_humidity_2m", "soil_moisture_0_to_7cm")
OMD = 2 * np.pi / 24; EPS, TAU_APR, ALFA = 0.4, 365.0, 0.001
H = 8760; NIC, SEMENTE = 20, 51; NUNCA = 10 ** 9; PRAZO = 180 * 24


def ler():
    with gzip.open(DADOS, "rt") as f:
        r = csv.DictReader(f); tempo, X = [], []
        for x in r:
            tempo.append(x["tempo_local"]); X.append([float(x[k]) for k in SENSORES])
    X = np.array(X); assert np.isfinite(X).all()
    mes = np.array([int(t[5:7]) for t in tempo]); hora = np.array([int(t[11:13]) for t in tempo])
    clim = np.zeros_like(X)
    for m in range(1, 13):
        for h in range(24):
            k = (mes == m) & (hora == h); clim[k] = X[k].mean(0)
    return tempo, X, X - clim


def rodar(X, ph0, **kw):
    s = S5.tensoes_online(S5.cascata(S5.normalizar_online(X)))
    return S5.sentinela(s, ph0, EPS, TAU_APR, [ALFA], **kw)


def resumo(r):
    dec = r["decl"][0]; dm = np.median(np.where(dec < 0, NUNCA, dec), 0); ok = dec[:, 0] >= 0
    wd = float(np.median(r["W"][dec[ok, 0], 0, np.flatnonzero(ok)]) / OMD) if ok.any() else None
    return {"declaracao_dias_por_andar": [None if x >= NUNCA else round(float(x) / 24, 1) for x in dm],
            "fracao_inicios_declarou": (dec >= 0).mean(0).tolist(), "w1_na_declaracao_sobre_Omega": wd,
            "w1_fim_sobre_Omega": float(np.median(r["w_fim"][0, :, 0]) / OMD), "_dm": dm}


def piloto(ph0):
    """As linhas ε = 0,4 da tabela da predição (mesmas sementes do piloto)."""
    T = H; tt = np.arange(T); out = {}
    def ar(rng, tau):
        q = np.exp(-1 / tau); e = np.zeros(T); x = 0.0; n = rng.normal(size=T)
        for i in range(T): x = q * x + np.sqrt(1 - q * q) * n[i]; e[i] = x
        return e
    def mundo(rng, A, lento):
        fase_ano = rng.uniform(0, 2 * np.pi); mod = 1 + 0.3 * np.cos(2 * np.pi * tt / 8766 + fase_ano)
        z = A * mod * np.cos(OMD * tt + rng.uniform(0, 2 * np.pi)) + ar(rng, 24.0) + (ar(rng, 24 * 7.0) if lento else 0)
        z = z + 0.5 * np.cos(2 * np.pi * tt / 8766 + 1.0)
        return S5.tensoes_online(S5.cascata(S5.normalizar_online(z[:, None])))
    for nome, A, lento in (("dia realista", 2.7, False), ("dia realista lento", 2.7, True), ("dia forte", 4.0, False),
                           ("sem dia", 0.0, False), ("sem dia lento", 0.0, True)):
        rng = np.random.default_rng(int(EPS * 1000) + int(A * 10) + 7 * lento); R = []
        for _ in range(8):
            s = mundo(rng, A, lento)
            a = resumo(S5.sentinela(s, ph0, EPS, TAU_APR, [ALFA]))
            c = resumo(S5.sentinela(s, ph0, EPS, TAU_APR, [ALFA], aprende=False))
            c2 = resumo(S5.sentinela(s, ph0, EPS, TAU_APR, [ALFA], aprende=False, exige_ouvida=False))
            R.append((a, c, c2))
        d1 = np.array([x[0]["_dm"][0] for x in R])
        out[nome] = {"andar1_declara": float((d1 < NUNCA).mean()), "andar1_em_90d": float((d1 < 90 * 24).mean()),
                     "w1_decl_mediana": float(np.nanmedian([np.nan if x[0]["w1_na_declaracao_sobre_Omega"] is None
                                                            else x[0]["w1_na_declaracao_sobre_Omega"] for x in R])),
                     "algum_andar": float(np.mean([(x[0]["_dm"] < NUNCA).any() for x in R])),
                     "controle_com_correcao": float(np.mean([(x[1]["_dm"] < NUNCA).any() for x in R])),
                     "controle_sem_correcao": float(np.mean([(x[2]["_dm"] < NUNCA).any() for x in R]))}
        print("piloto", nome, out[nome], flush=True)
    return out


def main():
    assert (ROOT / "PREDICAO_teste55_sentinela_do_dia.md").exists(), "sem predição, sem teste"
    ph0 = np.random.default_rng(SEMENTE).uniform(0, 2 * np.pi, (NIC, 4))[:, 1]
    t0 = time.time(); res = {"piloto_sintetico": piloto(ph0), "instalacoes": {}}
    print(f"piloto em {time.time() - t0:.0f} s", flush=True)
    tempo, X, Xn = ler(); idx = {t: i for i, t in enumerate(tempo)}
    for y in range(2010, 2025):
        m = (y - 2010) % 12 + 1; i0 = idx[f"{y}-{m:02d}-01T00:00"]; sl = slice(i0, i0 + H)
        assert sl.stop <= len(tempo)
        o = {"inicio": tempo[i0], "sentinela": resumo(rodar(X[sl], ph0)),
             "controle_com_correcao": resumo(rodar(X[sl], ph0, aprende=False)),
             "controle_sem_correcao": resumo(rodar(X[sl], ph0, aprende=False, exige_ouvida=False)),
             "nulo": resumo(rodar(Xn[sl], ph0))}
        sd = o["sentinela"]; w = sd["w1_na_declaracao_sobre_Omega"]
        o["J1"] = bool(sd["_dm"][0] < PRAZO and w is not None and abs(w - 1) <= 0.05)
        o["J2"] = bool((o["nulo"]["_dm"] >= NUNCA).all())
        o["J3"] = bool((o["controle_com_correcao"]["_dm"] >= NUNCA).all())
        o["controle_sem_correcao_declara"] = bool((o["controle_sem_correcao"]["_dm"] < NUNCA).any())
        for k in ("sentinela", "controle_com_correcao", "controle_sem_correcao", "nulo"): o[k].pop("_dm")
        res["instalacoes"][str(y)] = o
        print(f"{y} ({o['inicio'][:7]}): andar 1 declara em {sd['declaracao_dias_por_andar'][0]} d, ω₁/Ω "
              f"{w if w is None else round(w, 3)} (fim {sd['w1_fim_sobre_Omega']:.3f}; inícios {sd['fracao_inicios_declarou'][0]:.2f}); "
              f"andares {sd['declaracao_dias_por_andar']} | nulo {o['nulo']['declaracao_dias_por_andar']} | controle c/ corr. "
              f"{o['controle_com_correcao']['declaracao_dias_por_andar']} | s/ corr. {o['controle_sem_correcao']['declaracao_dias_por_andar']}"
              f" | J1 {o['J1']} J2 {o['J2']} J3 {o['J3']}", flush=True)
    I = res["instalacoes"].values()
    cont = {k: sum(o[k] for o in I) for k in ("J1", "J2", "J3", "controle_sem_correcao_declara")}
    J = {"J1": cont["J1"] >= 12, "J2": cont["J2"] >= 13, "J3": cont["J3"] >= 13}
    res.update({"contagens": cont, "J": {k: bool(v) for k, v in J.items()}})
    print("contagens", cont)
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste55.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
