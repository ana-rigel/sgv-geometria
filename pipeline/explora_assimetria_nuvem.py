"""Assimetria da nuvem do cubo (terceiro momento) por eixo, real vs. réplicas M. Previsão: PREDICAO_assimetria_nuvem.md.

    python pipeline/explora_assimetria_nuvem.py --periodo fumaca|junjul|agoset
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
import confirmatorio_4d as Q  # noqa: E402

E = GR.E
EIXOS = ["E_norm", "jerk", "memory_flux"]
BORDA, N_MIN_BORDA, N_MIN_QUENTE = 3.0, 30, 300


def g1(x):
    x = x[np.isfinite(x)]
    if len(x) < 30: return None
    d = x - x.mean(); m2 = np.mean(d ** 2)
    return float(np.mean(d ** 3) / m2 ** 1.5) if m2 > 0 else None


def medir(kl, may, wk):
    G = GR.regua(E.coords_orig(kl), may); w = Q.quarta(kl, may); lim = Q.limites(w, may)
    quente = w >= lim[-1]   # último dos NFATIAS−1 cortes = tercil/septil superior, conforme NFATIAS
    ext = np.nanmax(np.abs(G), axis=1)
    sem = []
    for idx in wk:
        X = G[idx]; ok = np.isfinite(X).all(1); X = X[ok]; e = ext[idx][ok]; q = quente[idx][ok]
        s = {"inicio": None, "n": int(len(X)), "g1": {}, "p_pos_borda": {}, "n_borda": int((e >= BORDA).sum()), "g1_quente": {}, "n_quente": int(q.sum())}
        for j, nome in enumerate(EIXOS):
            s["g1"][nome] = g1(X[:, j])
            b = X[e >= BORDA, j]; s["p_pos_borda"][nome] = float((b > 0).mean()) if len(b) >= N_MIN_BORDA else None
            s["g1_quente"][nome] = g1(X[q, j]) if q.sum() >= N_MIN_QUENTE else None
        sem.append(s)
    return sem


def classe(real, Ms):
    """Por eixo: 'torta' (fora do envelope M em ≥ 2/3 das semanas, mesmo sinal), 'torta sem lado', 'simétrica dentro do ruído'."""
    out = {}
    for nome in EIXOS:
        fora = []; validas = 0
        for i, s in enumerate(real):
            r = s["g1"][nome]; ms = [m[i]["g1"][nome] for m in Ms]
            if r is None or any(v is None for v in ms): continue
            validas += 1
            if r > max(ms): fora.append(+1)
            elif r < min(ms): fora.append(-1)
        if validas < 3: out[nome] = {"classe": "sem dados", "semanas_validas": validas, "fora": len(fora)}; continue
        if len(fora) * 3 >= 2 * validas:
            cls = "torta" if len(set(fora)) == 1 else "torta sem lado"
        else:
            cls = "simétrica dentro do ruído"
        out[nome] = {"classe": cls, "semanas_validas": validas, "fora": len(fora), "lado": (fora[0] if cls == "torta" else None)}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-05-03" if a.periodo == "fumaca" else "2026-06-01", tz="UTC")).to_numpy(); i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    real = medir(kl, may, wk); print("  real: ok", flush=True)
    for s, idx in zip(real, wk): s["inicio"] = str(ts.iloc[idx[0]].date())
    Ms = {}
    for sd in MS.SEEDS_M:
        k_, _, _ = MS.gerar_m(kl, ts, i0, sd); Ms[f"M_{sd}"] = medir(k_, may, wk); print(f"  M_{sd}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    cls = classe(real, list(Ms.values()))
    def med(sem, chave, nome): return float(np.nanmedian([s[chave][nome] if s[chave][nome] is not None else np.nan for s in sem]))
    desc = {nome: {"g1_real_mediana": med(real, "g1", nome), "g1_M_mediana": float(np.nanmedian([med(m, "g1", nome) for m in Ms.values()])),
                   "p_pos_borda_real": med(real, "p_pos_borda", nome), "p_pos_borda_M": float(np.nanmedian([med(m, "p_pos_borda", nome) for m in Ms.values()])),
                   "g1_quente_real": med(real, "g1_quente", nome), "g1_quente_M": float(np.nanmedian([med(m, "g1_quente", nome) for m in Ms.values()]))} for nome in EIXOS}
    out = {"periodo": a.periodo, "classes": cls, "descritivo": desc, "semanas": {"real": real, **Ms}}
    print(f"\n== assimetria da nuvem [{a.periodo}]")
    for nome in EIXOS:
        c = cls[nome]; d = desc[nome]
        print(f"  {nome:12s} g1 real {d['g1_real_mediana']:+.3f} | M {d['g1_M_mediana']:+.3f} · p+ borda real {d['p_pos_borda_real']:.2f} | M {d['p_pos_borda_M']:.2f} "
              f"· g1 quente real {d['g1_quente_real']:+.3f} | M {d['g1_quente_M']:+.3f} → {c['classe']} (fora {c['fora']}/{c['semanas_validas']})", flush=True)
    print("  g1 real por semana:", {nome: [round(s["g1"][nome], 2) if s["g1"][nome] is not None else None for s in real] for nome in EIXOS})
    print("  envelope M por semana (min,max):", {nome: [(round(min(m[i]["g1"][nome] for m in Ms.values()), 2), round(max(m[i]["g1"][nome] for m in Ms.values()), 2)) for i in range(len(real))] for nome in EIXOS})
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"assimetria_nuvem_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
