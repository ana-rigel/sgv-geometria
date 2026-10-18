"""Teste 8 (escada pela tensão). Predição: PREDICAO_teste8_escada_pela_tensao.md. Roda só porque a predição existe."""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import lfilter
from scipy.optimize import minimize
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V
sys.path.insert(0, str(Path(__file__).resolve().parent)); import teste4 as T4   # registros, erro_leitura (mesma leitura do teste 4)

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste8_escada_pela_tensao.md").exists(), "sem predição, sem teste"
N, CAL, SEEDS = 20000, 10000, range(1000, 1100)
MUNDOS = {"escada-2": ([7, 70], 2), "escada-3": ([7, 70, 700], 3), "escada-4": ([7, 70, 700, 7000], 4), "ciclico": (None, 4)}
FAIXA = (7.0, 13.0); LMIN, LMAX = 1e-4, 0.99
sig = lambda u: LMIN + (LMAX - LMIN) / (1 + np.exp(-u)); logit = lambda l: np.log((l - LMIN) / (LMAX - l))


def fatias(x, lams):
    """Tensões lineares D_0 = x − R_1, D_j = R_j − R_{j+1}; devolve as variâncias (soma das coordenadas) na calibração."""
    R = [x]
    for lam in lams: R.append(lfilter([lam], [1, -(1 - lam)], R[-1], axis=0))
    return np.array([np.sum(np.var(R[j][:CAL] - R[j + 1][:CAL], axis=0)) for j in range(len(lams))])


def objetivo(x, lams):
    v = fatias(x, lams); return float(np.std(np.log(np.maximum(v, 1e-18))))


def ajustar(x, k):
    melhor = None
    for l1 in (0.5, 0.15, 0.05):
        u0 = logit(np.clip(l1 / 10.0 ** np.arange(k), LMIN * 1.01, LMAX * 0.99))
        r = minimize(lambda u: objetivo(x, sig(u)), u0, method="Nelder-Mead", options={"maxiter": 800, "xatol": 1e-3, "fatol": 1e-8})
        if melhor is None or r.fun < melhor.fun: melhor = r
    return np.sort(sig(melhor.x))[::-1], melhor.fun


def main():
    out = {}; t4 = json.loads((ROOT / "resultados_teste4.json").read_text())
    for nome, (taus, k) in MUNDOS.items():
        rec, fora, ganha, lt, por = [], [], [], [], {}; lams_fixa = 0.15 / 10.0 ** np.arange(k)
        for s in SEEDS:
            x = V.mundo_escada(N, s, taus) if taus else V.mundo_ciclico(N, s)
            lam, obj = ajustar(x, k); e_ten, _ = T4.erro_leitura(x, T4.registros(x, lam)); e_fixa, _ = T4.erro_leitura(x, T4.registros(x, lams_fixa))
            e_t4 = t4[nome]["sementes"][str(s)]["e_livre"]; raz = lam[:-1] / lam[1:]; dentro = bool(np.all((raz >= FAIXA[0]) & (raz <= FAIXA[1])))
            rec.append(dentro); fora.append(not dentro); ganha.append(e_ten < e_fixa)
            if taus: lt.append(lam * np.array(taus))
            por[str(s)] = {"lambda": lam.tolist(), "razoes": raz.tolist(), "objetivo": obj, "e_tensao": e_ten, "e_fixa": e_fixa, "e_teste4": e_t4}
            if (s - 1000) % 25 == 0: print(f"  {nome} s{s}: λ {np.round(lam, 4)} razões {np.round(raz, 1)} | obj {obj:.3f} | e tensão {e_ten:.3f} fixa {e_fixa:.3f} t4 {e_t4:.3f}", flush=True)
        out[nome] = {"recupera": int(sum(rec)), "fora_da_progressao": int(sum(fora)), "ganha_da_fixa": int(sum(ganha)), "lambda_medio": np.mean([por[s]["lambda"] for s in por], 0).tolist(),
                     "razoes_medianas": np.median([por[s]["razoes"] for s in por], 0).tolist(), "lambda_x_tau_mediano": (np.median(lt, 0).tolist() if lt else None),
                     "e_medios": {c: float(np.mean([por[s][c] for s in por])) for c in ("e_tensao", "e_fixa", "e_teste4")}, "sementes": por}
        print(f"== {nome}: recupera {sum(rec)}/100 | fora {sum(fora)}/100 | ganha da fixa {sum(ganha)}/100 | razões medianas {np.round(out[nome]['razoes_medianas'],1)} | λ·τ {None if not lt else np.round(np.median(lt,0),2)} | e {out[nome]['e_medios']}", flush=True)
    a = all(out[m]["recupera"] >= 80 for m in ("escada-2", "escada-3", "escada-4")); b = out["ciclico"]["fora_da_progressao"] >= 80 and out["ciclico"]["ganha_da_fixa"] >= 80
    out["criterio"] = {"a_escadas": bool(a), "b_ciclico": bool(b), "passa": bool(a and b)}
    print(f"\n== teste 8: (a) {a} (b) {b} → {'PASSA' if a and b else 'REPROVA'}")
    (ROOT / "resultados_teste8.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
