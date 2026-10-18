"""Teste 7 (política de expectativa). Predição: PREDICAO_teste7_expectativa.md. Roda só porque a predição existe."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste7_expectativa.md").exists(), "sem predição, sem teste"
N, CAL, AFIN, SEEDS, PHI = 8000, 2000, 4000, range(1000, 1100), 0.9
LAMS = 0.15 / 10.0 ** np.arange(4); N_MAX = 16; ALVO = 0.25


def calibrar(x):
    """Régua de T0 e expectativa a_n + b_n·T0 do erro da memória congelada por n passos, em [0, CAL) olhando sempre."""
    obs = V.Observador(2, lams=LAMS); T0 = np.zeros(CAL); R1 = np.zeros((CAL, 2))
    for t in range(CAL):
        T0[t] = np.linalg.norm(x[t] - obs.R[0]); obs.passo(x[t]); R1[t] = obs.R[0]
    med = np.median(T0); esc = max(np.quantile(np.abs(T0 - med), 0.995) / 3, 1e-12); ab = np.zeros((N_MAX + 1, 2))
    for n in range(1, N_MAX + 1):
        y = np.linalg.norm(x[n:CAL] - R1[:CAL - n], axis=1); A = np.c_[np.ones(CAL - n), T0[:CAL - n]]; ab[n] = np.linalg.lstsq(A, y, rcond=None)[0]
    return (med, esc), ab


def rodar(x, regua, ab, politica, theta=None, ate=None):
    ate = ate or len(x); obs = V.Observador(2, lams=LAMS); med, esc = regua; e = np.zeros(ate); olhou = np.zeros(ate, dtype=bool); n = 0; T_ult = med
    for t in range(ate):
        e[t] = np.linalg.norm(x[t] - obs.R[0]); n += 1
        if politica == "sempre": ver = True
        elif politica == "periodico": ver = t % 4 == 0
        else: ver = n >= N_MAX or (ab[n, 0] + ab[n, 1] * T_ult - med) / esc >= theta
        olhou[t] = ver
        if ver: T_ult = np.linalg.norm(x[t] - obs.R[0]); n = 0; obs.passo(x[t])
        else: obs.passo(None)
    return e, olhou


def afinar_theta(x, regua, ab):
    lo, hi = -5.0, 30.0
    for _ in range(16):
        th = (lo + hi) / 2; _, o = rodar(x, regua, ab, "v0", th, ate=AFIN); f = o[CAL:AFIN].mean()
        if abs(f - ALVO) <= 0.01: return th, f
        lo, hi = (th, hi) if f > ALVO else (lo, th)
    return th, f


def main():
    out = {"sementes": {}}; Vs, ok, bs = [], [], []
    for s in SEEDS:
        x = V.mundo_deriva(N, s, PHI); regua, ab = calibrar(x); th, _ = afinar_theta(x, regua, ab); bs.append(ab[1:, 1])
        e0, o0 = rodar(x, regua, ab, "v0", th); e1, _ = rodar(x, regua, ab, "periodico"); e2, _ = rodar(x, regua, ab, "sempre")
        ev0, ep, es = e0[AFIN:].mean(), e1[AFIN:].mean(), e2[AFIN:].mean(); f = o0[AFIN:].mean(); valido = abs(f - ALVO) <= 0.03; Vv = 1 - ev0 / ep
        Vs.append(Vv); ok.append(valido)
        out["sementes"][str(s)] = {"theta": float(th), "fracao": float(f), "valido": bool(valido), "e_v0": float(ev0), "e_periodico": float(ep), "e_sempre": float(es), "V": float(Vv)}
        if (s - 1000) % 10 == 0: print(f"  s{s}: θ {th:.2f} fração {f:.3f} | e v0 {ev0:.3f} per {ep:.3f} sempre {es:.3f} | V {100*Vv:+.1f} % | b_n {np.round(ab[1:6,1],2)}", flush=True)
    Vs, ok = np.array(Vs), np.array(ok); Vv = Vs[ok]; a = bool(ok.sum() >= 95); b = bool(Vv.min() > 0) if len(Vv) else False
    out["resumo"] = {"validas": int(ok.sum()), "V_media": float(Vv.mean()), "V_env": [float(Vv.min()), float(Vv.max())], "V_pos": int((Vv > 0).sum()), "b_n_medio": np.mean(bs, 0).tolist(),
                     "e_medios": {k: float(np.mean([out["sementes"][str(s)][k] for s in SEEDS])) for k in ("e_v0", "e_periodico", "e_sempre")}, "criterio": {"a_fracao_ok": a, "b_envelope_acima_de_zero": b, "passa": a and b}}
    print(f"\n== teste 7: válidas {ok.sum()} | V média {100*Vv.mean():+.2f} % env ({100*Vv.min():+.1f}; {100*Vv.max():+.1f}) | V>0 em {(Vv>0).sum()} | b_n médio {np.round(np.mean(bs,0),3)} → {'PASSA' if a and b else 'REPROVA'}")
    (ROOT / "resultados_teste7.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
