"""Painel de replay 4D: exporta o estado minuto a minuto dos meses abertos (maio–setembro/2026) com o pipeline atual.

    python painel/exportar_replay.py --meses 2026-05 2026-06 2026-07           # local
    python painel/exportar_replay.py --meses 2026-05 ... 2026-09              # Actions

Grava painel/dados/replay_<primeiro>_<ultimo>.npz com, por minuto: timestamp, close, x (3 coords na régua de caudas),
w (log σ̂ har na mesma régua), fatia (0/1/2 pelos tercis de maio), ext (extremidade), e os metadados da âncora.
Nunca lê outubro: assert explícito. O modo "ao vivo" não existe neste script.
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

E = GR.E


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--meses", nargs="+", required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); assert all(m < "2026-10" for m in a.meses), "nada de outubro"
    kl = E.carregar(a.meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    raw = E.coords_orig(kl); ok = np.isfinite(raw).all(1); anc = raw[may & ok]
    med = np.median(anc, 0); esc = np.quantile(np.abs(anc - med), 0.995, axis=0) / 3.0
    G = GR.regua(raw, may)
    sig = V.estimativas(kl)["har"]; lw = np.log(sig); okw = np.isfinite(lw) & may
    medw = float(np.median(lw[okw])); escw = float(np.quantile(np.abs(lw[okw] - medw), 0.995) / 3.0)
    w = (lw - medw) / escw; lim = Q.limites(w, may)
    fatia = np.full(len(w), -1, np.int8); fin = np.isfinite(w); fatia[fin] = np.digitize(w[fin], np.quantile(w[may & fin], [1 / 3, 2 / 3]))
    ext = np.nanmax(np.abs(G), axis=1)
    out = ROOT / "painel" / "dados"; out.mkdir(exist_ok=True)
    nome = out / f"replay_{a.meses[0]}_{a.meses[-1]}.npz"
    np.savez_compressed(nome, timestamp=kl.timestamp.values.astype(np.int64), close=kl.close.values.astype(np.float32),
                        x=G.astype(np.float32), w=w.astype(np.float32), fatia=fatia, ext=ext.astype(np.float32))
    meta = {"meses": a.meses, "ancora": "2026-05", "regua": {"mediana": med.tolist(), "escala": esc.tolist(), "w_mediana": medw, "w_escala": escw},
            "fatias_7_limites": lim.tolist(), "tercis_limites": np.quantile(w[may & fin], [1 / 3, 2 / 3]).tolist(),
            "n": int(len(kl)), "validos": int(np.isfinite(G).all(1).sum()), "primeiro": str(ts.iloc[0]), "ultimo": str(ts.iloc[-1]),
            "instrumento": "1 min; E_norm, jerk, memory_flux do sgv_original na régua de caudas (mediana e q99,5 de maio ÷ 3); σ̂ = har; sem direção",
            "ao_vivo": {"ligado": False, "motivo": "outubro reservado até 3/11/2026; novembro até 1/12/2026"}}
    (out / nome.name.replace(".npz", ".json")).write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(f"gravado {nome.name}: {meta['n']} minutos, {meta['validos']} válidos, {nome.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
