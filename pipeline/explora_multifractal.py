"""Espectro de escala ζ(q) dos retornos agregados: real vs. M vs. embaralhado. Previsão: PREDICAO_multifractal.md.

    python pipeline/explora_multifractal.py --periodo fumaca|junjul|agoset
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402
import explora_volatilidade_multiescala as MS  # noqa: E402

E = GR.E
TAUS = [1, 2, 3, 5, 8, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360, 480, 720, 1440]
QS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
TAU_MAX, SEEDS_EMB = 240, [7026, 7027, 7028, 7029, 7030]


def retornos_periodo(kl, idx):
    lc = np.log(kl.close.values.astype(float)[idx]); return np.diff(lc)


def espectro(r, tau_max):
    S = {}
    for tau in TAUS:
        n = (len(r) // tau) * tau
        if n < 50 * tau: continue
        rt = r[:n].reshape(-1, tau).sum(1); a = np.abs(rt); a = a[a > 0]
        S[tau] = {q: float(np.mean(a ** q)) for q in QS}
    def zeta(tmax):
        ts = [t for t in S if t <= tmax]; lt = np.log(ts); out = {}
        for q in QS:
            ls = np.log([S[t][q] for t in ts]); out[q] = float(np.polyfit(lt, ls, 1)[0])
        return out
    z = zeta(tau_max); z_dia = zeta(1440)
    return {"zeta": z, "zeta_1440": z_dia, "kappa": 2 * z[2.0] - z[4.0], "kappa_1440": 2 * z_dia[2.0] - z_dia[4.0], "H": z[2.0] / 2, "n_tau": len(S),
            "S": {str(t): {str(q): v for q, v in d.items()} for t, d in S.items()}}


def classe(real, Ms, Es):
    k = real["kappa"]; km = [m["kappa"] for m in Ms]; ke = [e["kappa"] for e in Es]
    if k <= max(ke): return "monofractal dentro do ruído"
    if k > max(km): return "multifractal além do M"
    if k >= min(km): return "multifractal como o M"
    return "abaixo do M"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-05-03" if a.periodo == "fumaca" else "2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may))
    idx = np.concatenate(GR.semanas(ts, ini, fim)); r = retornos_periodo(kl, idx)
    res = {"real": espectro(r, TAU_MAX)}; print("  real: ok", flush=True)
    for s in MS.SEEDS_M:
        k_, _, _ = MS.gerar_m(kl, ts, i0, s); res[f"M_{s}"] = espectro(retornos_periodo(k_, idx), TAU_MAX); print(f"  M_{s}: ok", flush=True)
    for s in SEEDS_EMB:
        rng = np.random.default_rng(s); res[f"EMB_{s}"] = espectro(rng.permutation(r), TAU_MAX); print(f"  EMB_{s}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    Ms = [res[f"M_{s}"] for s in MS.SEEDS_M]; Es = [res[f"EMB_{s}"] for s in SEEDS_EMB]; real = res["real"]
    out = {"periodo": a.periodo, "classe": classe(real, Ms, Es), "tau_max": TAU_MAX, "series": res,
           "envelope": {"M": [min(m["kappa"] for m in Ms), max(m["kappa"] for m in Ms)], "EMB": [min(e["kappa"] for e in Es), max(e["kappa"] for e in Es)]}}
    print(f"\n== espectro de escala ζ(q) [{a.periodo}] (ajuste até {TAU_MAX} min; n retornos {len(r)})")
    print(f"  κ real {real['kappa']:+.3f} | M [{out['envelope']['M'][0]:+.3f}; {out['envelope']['M'][1]:+.3f}] | embaralhado [{out['envelope']['EMB'][0]:+.3f}; {out['envelope']['EMB'][1]:+.3f}] → {out['classe']}")
    print(f"  H real {real['H']:.3f} | M {np.mean([m['H'] for m in Ms]):.3f} | emb {np.mean([e['H'] for e in Es]):.3f} · κ até 1440: real {real['kappa_1440']:+.3f} | M [{min(m['kappa_1440'] for m in Ms):+.3f}; {max(m['kappa_1440'] for m in Ms):+.3f}]")
    print("  ζ(q) real:", {q: round(v, 3) for q, v in real["zeta"].items()}, "| qH:", {q: round(q * real["H"], 3) for q in QS})
    print("  ζ(q) M médio:", {q: round(float(np.mean([m["zeta"][q] for m in Ms])), 3) for q in QS}, "| emb médio:", {q: round(float(np.mean([e["zeta"][q] for e in Es])), 3) for q in QS})
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"multifractal_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
