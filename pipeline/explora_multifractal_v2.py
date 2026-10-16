"""Multifractal v2: concavidade em q baixo (κ₁) e espectro dos retornos padronizados por σ̂ causal. Previsão: PREDICAO_multifractal_v2.md.

    python pipeline/explora_multifractal_v2.py --periodo fumaca|junjul|agoset
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
import explora_volatilidade_escondida as V  # noqa: E402
import explora_multifractal as M1  # noqa: E402  (espectro, TAU_MAX, SEEDS_EMB)

E = GR.E


def espectro(r):
    f = M1.espectro(r, M1.TAU_MAX); z = f["zeta"]; f["kappa1"] = 2 * z[1.0] - z[2.0]; del f["S"]; return f


def series(kl, idx):
    lc = np.log(kl.close.values.astype(float)); r = np.diff(lc, prepend=np.nan)
    sig = V.estimativas(kl)["har"]; sig1 = np.r_[np.nan, sig[:-1]]          # σ̂ atrasado em 1 min
    rr = r[idx][1:]; zz = (r / sig1)[idx][1:]; zz = zz[np.isfinite(zz)]
    return rr[np.isfinite(rr)], zz


def cls1(real, Ms, Es):
    k = real["kappa1"]; km = [m["kappa1"] for m in Ms]; ke = [e["kappa1"] for e in Es]
    if k <= max(ke): return "sem cascata além da cauda"
    if k > max(km): return "cascata além do M"
    if k >= min(km): return "cascata como o M"
    return "abaixo do M"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-05-03" if a.periodo == "fumaca" else "2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may))
    idx = np.concatenate(GR.semanas(ts, ini, fim)); r, z = series(kl, idx)
    res = {"real": {"r": espectro(r), "z": espectro(z)}}; print("  real: ok", flush=True)
    for s in MS.SEEDS_M:
        k_, _, _ = MS.gerar_m(kl, ts, i0, s); rm, zm = series(k_, idx); res[f"M_{s}"] = {"r": espectro(rm), "z": espectro(zm)}; print(f"  M_{s}: ok", flush=True)
    for s in M1.SEEDS_EMB:
        rng = np.random.default_rng(s); res[f"EMB_{s}"] = {"r": espectro(rng.permutation(r)), "z": espectro(rng.permutation(z))}; print(f"  EMB_{s}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    Ms = [res[f"M_{s}"] for s in MS.SEEDS_M]; Es = [res[f"EMB_{s}"] for s in M1.SEEDS_EMB]; real = res["real"]
    c1 = cls1(real["r"], [m["r"] for m in Ms], [e["r"] for e in Es])
    kz = real["z"]["kappa1"]; kze = [e["z"]["kappa1"] for e in Es]; c2 = "resíduo de cascata" if kz > max(kze) else "σ̂ absorve a cascata"
    env = lambda key, sub: [min(x[sub][key] for x in Es), max(x[sub][key] for x in Es)]
    envM = lambda key, sub: [min(x[sub][key] for x in Ms), max(x[sub][key] for x in Ms)]
    out = {"periodo": a.periodo, "classe_cascata": c1, "classe_residuo": c2, "series": res,
           "envelopes": {"kappa1_r_M": envM("kappa1", "r"), "kappa1_r_EMB": env("kappa1", "r"), "kappa1_z_EMB": env("kappa1", "z"), "kappa1_z_M": envM("kappa1", "z"), "kappa_z_EMB": env("kappa", "z")}}
    e = out["envelopes"]
    print(f"\n== multifractal v2 [{a.periodo}] (ajuste até {M1.TAU_MAX} min)")
    print(f"  (1) κ₁ bruto: real {real['r']['kappa1']:+.4f} | M [{e['kappa1_r_M'][0]:+.4f}; {e['kappa1_r_M'][1]:+.4f}] | emb [{e['kappa1_r_EMB'][0]:+.4f}; {e['kappa1_r_EMB'][1]:+.4f}] → {c1}")
    print(f"  (2) κ₁(z):    real {kz:+.4f} | M [{e['kappa1_z_M'][0]:+.4f}; {e['kappa1_z_M'][1]:+.4f}] | emb [{e['kappa1_z_EMB'][0]:+.4f}; {e['kappa1_z_EMB'][1]:+.4f}] → {c2}")
    print(f"  descritivo: κ(z) real {real['z']['kappa']:+.3f} | emb(z) [{e['kappa_z_EMB'][0]:+.3f}; {e['kappa_z_EMB'][1]:+.3f}] · κ bruto real (v1) {real['r']['kappa']:+.3f} · H real {real['r']['H']:.3f}, H(z) {real['z']['H']:.3f}")
    print("  ζ(q) z real:", {q: round(v, 3) for q, v in real["z"]["zeta"].items()}, "| z emb médio:", {q: round(float(np.mean([x["z"]["zeta"][q] for x in Es])), 3) for q in M1.QS})
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"multifractal_v2_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
