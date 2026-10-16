"""Auto-similaridade temporal: o cubo em 1, 5 e 15 min, relativo ao sintético M. Previsão: PREDICAO_autosimilaridade_temporal.md.

    python pipeline/explora_autosimilaridade_temporal.py --periodo fumaca|junjul|agoset
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
import explora_volatilidade_multiescala as MS  # noqa: E402
import explora_fatias_volatilidade as F  # noqa: E402
import confirmatorio_4d as Q  # noqa: E402

E = GR.E
AGG = {1: 200, 5: 100, 15: 60}   # resolução em minutos → k dos vizinhos


def agregar(kl, agg):
    if agg == 1: return kl.reset_index(drop=True)
    n = (len(kl) // agg) * agg; g = np.arange(n) // agg; d = kl.iloc[:n]
    out = pd.DataFrame({"timestamp": d.timestamp.groupby(g).first(), "open": d.open.groupby(g).first(), "high": d.high.groupby(g).max(),
                        "low": d.low.groupby(g).min(), "close": d.close.groupby(g).last(), "volume": d.volume.groupby(g).sum(),
                        "taker_buy": d.taker_buy.groupby(g).sum()})
    return out.reset_index(drop=True)


def medir(k_, ts, may, wk, agg):
    GR.K = AGG[agg]; Q.N_MIN_FATIA = max(300 // agg, 20); Q.N_MIN_SEMANA_B = 2000 // agg
    G = GR.regua(E.coords_orig(k_), may)
    r = GR.p1(G, wk)
    sig = V.estimativas(k_)["har"]; lab = F.fatias(sig, may)
    c = F.teste1a_2(G, sig, lab, wk)
    w = Q.quarta(k_, may); lim = Q.limites(w, may); q = Q.resumo(Q.medir(G, w, lim, wk))
    return {"R": r["R"], "n_extremos": r["n_extremos"], "perfil": r["perfil"], "C": c["C"], "R_fatias": c["R_fatias"],
            "rho_forma": q.get("rho_forma"), "r2_tilt": q.get("r2_tilt"), "r2_quad": q.get("r2_quad"), "taxa_zoom": q.get("taxa_zoom"),
            "semanas_validas_a": q["semanas_validas_a"]}


def rodar(kl1, agg, ini, fim, may_fim):
    kl = agregar(kl1, agg); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp(may_fim, tz="UTC")).to_numpy(); i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    out = {"real": medir(kl, ts, may, wk, agg)}; print(f"  {agg:2d}m real: ok", flush=True)
    for s in MS.SEEDS_M:
        k_, _, _ = MS.gerar_m(kl, ts, i0, s); out[f"M_{s}"] = medir(k_, ts, may, wk, agg); print(f"  {agg:2d}m M_{s}: ok", flush=True)
    return out


def classe_R(res):
    real = res["real"]["R"]; Ms = [res[f"M_{s}"]["R"] for s in MS.SEEDS_M]
    if real is None or any(m is None for m in Ms) or res["real"]["n_extremos"] < 30: return "sem dados"
    return "acima" if real > max(Ms) else ("dentro" if real >= min(Ms) else "abaixo")


def classe_C(c):
    if c is None: return "sem dados"
    return "colapsa" if c >= 0.7 else ("em parte" if c >= 0.3 else "não colapsa")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = GR.PERIODOS[a.periodo]
    kl1 = E.carregar(meses, Path(a.dados)); ts1 = pd.to_datetime(kl1.timestamp, unit="ms", utc=True)
    assert ts1.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may_fim = "2026-06-01"
    if a.periodo == "fumaca":   # o aquecimento do instrumento é 1.441 barras (15 dias em 15 min): a fumaça usa maio até 17/05 como âncora
        may_fim, ini, fim = "2026-05-17", "2026-05-17", "2026-06-01"
    res = {agg: rodar(kl1, agg, ini, fim, may_fim) for agg in AGG}
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    cls = {agg: {"R": classe_R(r), "C": classe_C(r["real"]["C"])} for agg, r in res.items()}
    borda = "borda auto-similar" if len({c["R"] for c in cls.values()}) == 1 and "sem dados" not in {c["R"] for c in cls.values()} else "borda muda de escala"
    colapso = "colapso auto-similar" if all(c["C"] == "colapsa" for c in cls.values()) else "colapso muda de escala"
    print(f"\n== auto-similaridade temporal [{a.periodo}]")
    for agg, r in res.items():
        Ms = [r[f"M_{s}"] for s in MS.SEEDS_M]
        print(f"  {agg:2d}m real R {r['real']['R']:.2f} (n_ext {r['real']['n_extremos']}) M [{min(m['R'] for m in Ms):.2f}; {max(m['R'] for m in Ms):.2f}] → {cls[agg]['R']}"
              f" | C real {r['real']['C']:.2f} M [{min(m['C'] for m in Ms):.2f}; {max(m['C'] for m in Ms):.2f}] → {cls[agg]['C']}"
              f" | ρ_forma {r['real']['rho_forma']} zoom {r['real']['taxa_zoom']} R²q {r['real']['r2_quad']}", flush=True)
    print(f"  R(15)/R(1) real: {res[15]['real']['R'] / res[1]['real']['R']:.2f};  veredito: {borda}; {colapso}")
    out = {"periodo": a.periodo, "resolucoes": {str(k): v for k, v in res.items()}, "classes": {str(k): v for k, v in cls.items()}, "borda": borda, "colapso": colapso}
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"autosimilaridade_temporal_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
