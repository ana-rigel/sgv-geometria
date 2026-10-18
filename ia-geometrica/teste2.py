"""Teste 2 (custo de olhar). Predição: PREDICAO_teste2.md. Roda só porque a predição existe."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste2.md").exists(), "sem predição, sem teste"
N, CAL, AFIN, SEEDS, PHI = 8000, 2000, 4000, range(1000, 1100), 0.9
LAMS = 0.15 / 10.0 ** np.arange(4); N_MAX = 8; ALVO = 0.25


def rodar_politica(x, regua, politica, theta=None, ate=None):
    """politica: 'v0' | 'periodico' | 'sempre'. Devolve erro de predição por passo e vetor olhou."""
    ate = ate or len(x); obs = V.Observador(x.shape[1], lams=LAMS, regua=regua, theta=theta if politica == "v0" else None, n_max=N_MAX)
    e = np.zeros(ate); olhou = np.zeros(ate, dtype=bool)
    for t in range(ate):
        e[t] = np.linalg.norm(x[t] - obs.R[0])          # memória ANTES de ver x_t
        ver = {"v0": obs.quer_olhar, "periodico": lambda: t % 4 == 0, "sempre": lambda: True}[politica]()
        olhou[t] = ver; obs.passo(x[t] if ver else None)
    return e, olhou


def regua_de(x):
    obs = V.Observador(x.shape[1], lams=LAMS); Ts = np.array([obs.passo(x[t]) for t in range(CAL)]); return V.calibrar_regua(Ts)


def afinar_theta(x, regua):
    lo, hi = 0.0, 20.0
    for _ in range(14):
        th = (lo + hi) / 2; _, olhou = rodar_politica(x, regua, "v0", th, ate=AFIN); f = olhou[CAL:AFIN].mean()
        if abs(f - ALVO) <= 0.01: return th, f
        lo, hi = (th, hi) if f > ALVO else (lo, th)
    return th, f


def main():
    out = {"sementes": {}}; Vs, fr, ok = [], [], []
    for s in SEEDS:
        x = V.mundo_deriva(N, s, PHI); regua = regua_de(x); th, _ = afinar_theta(x, regua)
        e0, o0 = rodar_politica(x, regua, "v0", th); e1, _ = rodar_politica(x, regua, "periodico"); e2, _ = rodar_politica(x, regua, "sempre")
        ev0, ep, es = e0[AFIN:].mean(), e1[AFIN:].mean(), e2[AFIN:].mean(); f = o0[AFIN:].mean(); valido = abs(f - ALVO) <= 0.03
        Vv = 1 - ev0 / ep; Vs.append(Vv); fr.append(f); ok.append(valido)
        out["sementes"][str(s)] = {"theta": float(th), "fracao": float(f), "valido": bool(valido), "e_v0": float(ev0), "e_periodico": float(ep), "e_sempre": float(es), "V": float(Vv)}
        if (s - 1000) % 10 == 0: print(f"  s{s}: θ {th:.2f} fração {f:.3f} | e v0 {ev0:.3f} per {ep:.3f} sempre {es:.3f} | V {100*Vv:+.1f} %", flush=True)
    Vs, fr, ok = np.array(Vs), np.array(fr), np.array(ok); Vv = Vs[ok]
    a = bool(ok.sum() >= 95); b = bool(Vv.min() > 0) if len(Vv) else False
    teto = bool(np.mean([out["sementes"][str(s)]["e_sempre"] < min(out["sementes"][str(s)]["e_v0"], out["sementes"][str(s)]["e_periodico"]) for s in SEEDS]) == 1.0)
    out["resumo"] = {"validas": int(ok.sum()), "V_media": float(Vv.mean()), "V_env": [float(Vv.min()), float(Vv.max())], "fracao_media": float(fr.mean()),
                     "e_medios": {k: float(np.mean([out["sementes"][str(s)][k] for s in SEEDS])) for k in ("e_v0", "e_periodico", "e_sempre")},
                     "criterio": {"a_fracao_ok": a, "b_envelope_acima_de_zero": b, "sanidade_teto": teto, "passa": a and b}}
    print(f"\n== teste 2: válidas {ok.sum()} | V média {100*Vv.mean():+.2f} % env ({100*Vv.min():+.1f}; {100*Vv.max():+.1f}) | teto {teto} → {'PASSA' if a and b else 'REPROVA'}")
    (ROOT / "resultados_teste2.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
