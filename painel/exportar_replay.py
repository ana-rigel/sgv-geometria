"""Painel de replay 4D: exporta o estado minuto a minuto dos meses abertos com o pipeline atual, em 1, 5 e 15 min.

    python painel/exportar_replay.py --meses 2026-05 2026-06 2026-07           # local
    python painel/exportar_replay.py --meses 2026-05 ... 2026-09              # Actions

Para cada resolução r ∈ {1, 5, 15}: timestamp, close, x (3 coords na régua de caudas da resolução), w (log σ̂ har na régua),
fatia (tercis de maio), ext (extremidade) e D (campo localmente linear, treinado na semana anterior, k = 200/100/60, como na
auto-similaridade temporal; NaN em maio, que é só âncora). Nunca lê outubro.
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
import explora_volatilidade_escondida as V  # noqa: E402
import confirmatorio_4d as Q  # noqa: E402
import explora_autosimilaridade_temporal as AS  # noqa: E402  (agregar, AGG)

E = GR.E


def campo_por_minuto(G, ts, ini, fim, k):
    """D(x) de cada minuto da semana k, com o campo treinado na semana k−1 (mesmo estimador das rodadas)."""
    GR.K = k; D = np.full(len(G), np.nan, np.float32); wk = GR.semanas(ts, ini, fim)
    for j in range(1, len(wk)):
        tr, te = wk[j - 1], wk[j]
        Xa = G[tr[:-1]]; S = G[tr[1:]] - G[tr[:-1]]; ok = np.isfinite(Xa).all(1) & np.isfinite(S).all(1)
        if ok.sum() < 2 * k: continue
        idx = te[np.isfinite(G[te]).all(1)]
        for a in range(0, len(idx), 2000):
            s = idx[a:a + 2000]; D[s] = GR.campo_ll(Xa[ok], S[ok], G[s])
    return D


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--meses", nargs="+", required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); assert all(m < "2026-10" for m in a.meses), "nada de outubro"
    kl1 = E.carregar(a.meses, Path(a.dados)); ts1 = pd.to_datetime(kl1.timestamp, unit="ms", utc=True)
    assert ts1.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    arrays, meta = {}, {"meses": a.meses, "ancora": "2026-05", "resolucoes": {}}
    for agg, k in AS.AGG.items():
        kl = AS.agregar(kl1, agg); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True); may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
        raw = E.coords_orig(kl); ok = np.isfinite(raw).all(1); anc = raw[may & ok]
        med = np.median(anc, 0); esc = np.quantile(np.abs(anc - med), 0.995, axis=0) / 3.0; G = GR.regua(raw, may)
        lw = np.log(V.estimativas(kl)["har"]); okw = np.isfinite(lw) & may
        medw = float(np.median(lw[okw])); escw = float(np.quantile(np.abs(lw[okw] - medw), 0.995) / 3.0); w = (lw - medw) / escw
        fin = np.isfinite(w); terc = np.quantile(w[may & fin], [1 / 3, 2 / 3]); fatia = np.full(len(w), -1, np.int8); fatia[fin] = np.digitize(w[fin], terc)
        ext = np.nanmax(np.abs(G), axis=1)
        D = campo_por_minuto(G, ts, "2026-05-25", str(ts.iloc[-1] + pd.Timedelta(minutes=1)), k)
        t = f"r{agg}"
        arrays.update({f"{t}_timestamp": kl.timestamp.values.astype(np.int64), f"{t}_close": kl.close.values.astype(np.float32), f"{t}_x": G.astype(np.float32),
                       f"{t}_w": w.astype(np.float32), f"{t}_fatia": fatia, f"{t}_ext": ext.astype(np.float32), f"{t}_D": D})
        meta["resolucoes"][str(agg)] = {"k": k, "n": int(len(kl)), "validos": int(np.isfinite(G).all(1).sum()), "regua": {"mediana": med.tolist(), "escala": esc.tolist(), "w_mediana": medw, "w_escala": escw},
                                        "tercis_limites": terc.tolist(), "fatias_7_limites": Q.limites(w, may).tolist(), "primeiro": str(ts.iloc[0]), "ultimo": str(ts.iloc[-1])}
        print(f"  {agg:2d} min: {len(kl)} barras, campo em {int(np.isfinite(D).sum())}", flush=True)
    meta.update({"n": meta["resolucoes"]["1"]["n"], "validos": meta["resolucoes"]["1"]["validos"], "regua": meta["resolucoes"]["1"]["regua"], "tercis_limites": meta["resolucoes"]["1"]["tercis_limites"],
                 "primeiro": meta["resolucoes"]["1"]["primeiro"], "ultimo": meta["resolucoes"]["1"]["ultimo"],
                 "instrumento": "1 min; E_norm, jerk, memory_flux do sgv_original na régua de caudas (mediana e q99,5 de maio ÷ 3); σ̂ = har; campo D(x) localmente linear treinado na semana anterior; sem direção",
                 "medido": {"R_borda": {"1": [6.83, 6.48], "5": [5.52, 6.04], "15": [4.60, 2.41]}, "C_colapso": {"1": [0.88, 0.92], "5": [0.93, 0.84], "15": [0.80, 0.70]},
                            "R_M": {"1": [[6.53, 7.14], [12.05, 15.03]], "5": [[4.00, 5.47], [3.29, 4.75]], "15": [[2.05, 5.25], [1.57, 3.11]]},
                            "periodos": ["jun–jul", "ago–set"], "fonte": "exploracao/autosimilaridade-temporal (16/10/2026)"},
                 "ao_vivo": {"ligado": False, "motivo": "outubro reservado até 3/11/2026; novembro até 1/12/2026"}})
    out = ROOT / "painel" / "dados"; out.mkdir(exist_ok=True); nome = out / f"replay_{a.meses[0]}_{a.meses[-1]}.npz"
    np.savez_compressed(nome, **arrays); (out / nome.name.replace(".npz", ".json")).write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(f"gravado {nome.name}: {nome.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
