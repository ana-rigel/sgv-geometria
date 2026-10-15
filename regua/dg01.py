"""DG-01: a feature de caudas do BTC com a régua atual (A0) e com as construções B–E do RB-01, real e nula.

python -m regua.dg01 real|nula   (grava resultados/dg01/dg01_<modo>.json)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import confirmatorio_casca as cc  # noqa: E402  (vendor, régua, dados, nula: sem mudança)

from regua import rb01 as R  # noqa: E402

CANDS = ("B", "C", "D", "E")
OUT = ROOT / "resultados" / "dg01"


def logvols(cand, X, key):
    try:
        g = R.rng("dg01", cand, *key)
        m = R.fit_candidate(cand, X)
        return [R.region_stats(m, R.tau_hyndman(m, a, g), g)["logV"] for a in R.ALPHAS]
    except (R.Invalid, np.linalg.LinAlgError, ValueError):
        return None


def mapa_completo(G, absr, a, key):
    m = cc.mapa(G, absr, a)                       # A0 (malhas do vendor) + referências
    X = G[a:a + cc.W]; X = X[np.isfinite(X).all(1)]
    m["A0"] = None if not m["v"][0] else [float(np.log(m["v"][0][0])), float(np.log(m["v"][0][1]))]
    if len(X) >= 0.95 * cc.W:
        for c in CANDS:
            m[c] = logvols(c, X, key)
    else:
        for c in CANDS:
            m[c] = None
    m.pop("v")
    return m


def main(modo):
    kl = cc.carregar("BTCUSDT", ["2026-05", "2026-06", "2026-07"])
    ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    if modo == "nula":
        i0 = int(np.argmax((ts >= pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()))
        kl = cc.nula(kl, ts, i0)
    G, absr, ts, i0, inicios, _, _ = cc.preparar(kl, "2026-08-01")
    t0 = time.time()
    snaps = list(range(i0, len(G), 240))
    rel = {}
    for k, s in enumerate(snaps):
        rel[k] = mapa_completo(G, absr, s - cc.W, (modo, "rel", k))
        if k % 30 == 0:
            print(f"[{time.time()-t0:5.0f}s] {modo} relatório {k}/{len(snaps)}", flush=True)
    dis = [mapa_completo(G, absr, a, (modo, "dis", i)) for i, a in enumerate(inicios)]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"dg01_{modo}.json").write_text(json.dumps({"modo": modo, "relatorio": rel, "disjunto": dis}))
    print(f"{modo} gravado em {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
