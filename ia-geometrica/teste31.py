"""Teste 31 (onde a samambaia quebra): em lugares não vistos, a fração anual cai abaixo de ½ entre os andares 2 e 3?
Predição: PREDICAO_teste31_quebra_da_samambaia.md. Dados: clima/dados/lugares/*.csv (baixar_lugares.py)."""
import csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent; DADOS = ROOT / "clima" / "dados" / "lugares"
MT = ["sinop", "cuiaba", "barra_do_garcas", "alta_floresta", "rondonopolis"]
CONTRASTE = ["porto_alegre", "curitiba", "petrolina", "manaus", "belem"]
SUL = ["porto_alegre", "curitiba"]


def ler(nome):
    with open(DADOS / f"{nome}.csv") as f:
        r = list(csv.DictReader(f))
    r = [x for x in r if int(x["horas"]) == 24]
    dias = [x["dia"] for x in r]; f_ = lambda k: np.array([float(x[k]) for x in r])
    return dias, f_("chuva_mm"), f_("et0_mm"), f_("solo_28_100"), f_("vpd_kpa")


def fracao_anual(R, t):
    """1 − variância residual / variância, somadas nas três componentes, depois de ajustar o ciclo anual (1º e 2º harmônicos)."""
    A = np.column_stack([np.ones_like(t), np.sin(2 * np.pi * t / 365.25), np.cos(2 * np.pi * t / 365.25), np.sin(4 * np.pi * t / 365.25), np.cos(4 * np.pi * t / 365.25)])
    res = tot = 0.0
    for k in range(R.shape[1]):
        v = R[:, k]; b, *_ = np.linalg.lstsq(A, v, rcond=None); res += np.var(v - A @ b); tot += np.var(v)
    return float(1 - res / tot) if tot > 0 else 0.0


def quebra(fr):
    if fr[0] < 0.5: return "antes do andar 1"
    for j in range(3):
        if fr[j] >= 0.5 and fr[j + 1] < 0.5: return f"entre {j+1} e {j+2}"
    return "sem quebra"


def lugar(nome):
    dias, P, E, S, Vp = ler(nome); ano = np.array([int(d[:4]) for d in dias]); t = np.array([np.datetime64(d, "D").astype(int) for d in dias], float)
    bal = np.convolve(P - E, np.ones(7) / 7)[:len(P)]; cal = ano <= 2017
    z = lambda v: (v - v[cal].mean()) / v[cal].std()
    x = np.column_stack([z(S), z(bal), z(Vp)])
    obs = V.Observador(3); obs.R[:] = 0.0; _, _, Rh = V.rodar(x, obs)
    m = ano >= 2012
    fr = [fracao_anual(Rh[m, j], t[m]) for j in range(4)]
    return {"dias": len(dias), "fracao_anual_campo": fracao_anual(x[m], t[m]), "fracao_anual": fr, "quebra": quebra(fr)}


def main():
    assert (ROOT / "PREDICAO_teste31_quebra_da_samambaia.md").exists(), "sem predição, sem teste"
    out = {n: lugar(n) for n in MT + CONTRASTE}
    q23 = sum(out[n]["quebra"] == "entre 2 e 3" for n in MT)
    j1 = q23 >= 4
    j2 = all(out[n]["fracao_anual"][1] < 0.5 for n in SUL)
    out["resumo"] = {"MT_quebra_2_3": q23, "J1": bool(j1), "J2": bool(j2)}
    for n in MT + CONTRASTE:
        o = out[n]; print(f"  {n:16s} campo {o['fracao_anual_campo']:.2f} | andares " + " ".join(f"{v:.2f}" for v in o["fracao_anual"]) + f" | quebra {o['quebra']}")
    print(f"== teste 31: MT com quebra entre 2 e 3: {q23}/5 → J1 {'PASSA' if j1 else 'REPROVA'} | sul com andar 2 abaixo de ½: {[round(out[n]['fracao_anual'][1], 2) for n in SUL]} → J2 {'PASSA' if j2 else 'REPROVA'}")
    (ROOT / "resultados_teste31.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
