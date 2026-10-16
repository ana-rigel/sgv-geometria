"""H-4D-01 — a temperatura como quarta coordenada: forma da fatia (a) e inclinação da nuvem (b).
Definições congeladas em PREREGISTRO_H-4D-01.md.

    python pipeline/confirmatorio_4d.py --periodo fumaca|junjul|agoset   # meses abertos (exploração/aquecimento)
    python pipeline/confirmatorio_4d.py --paridade                        # reproduz exatamente resultados/H-4D-01_exploracao_junjul.json
    python pipeline/confirmatorio_4d.py --julgamento                      # outubro/2026, uma única vez
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402  (E, regua, semanas, PERIODOS)
import explora_volatilidade_escondida as V  # noqa: E402  (estimativas)
import explora_volatilidade_multiescala as MS  # noqa: E402  (gerar_m, SEEDS_M)

E = GR.E
NFATIAS, N_MIN_FATIA, N_MIN_SEMANA_B, FATIAS_MIN_SEMANA, SEMANAS_MIN = 7, 300, 2000, 5, 3
MODOS = {"paridade": (["2026-05", "2026-06", "2026-07"], "2026-06-01", "2026-08-01"),
         "julgamento": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"], "2026-10-01", "2026-10-29")}


def quarta(kl, may, est="har"):
    """w = log σ̂ na régua de caudas (mediana e q99,5 de maio ÷ 3)."""
    w = np.log(V.estimativas(kl)[est]); ok = np.isfinite(w) & may
    med = np.median(w[ok]); esc = np.quantile(np.abs(w[ok] - med), 0.995) / 3.0
    return (w - med) / esc


def limites(w, may):
    return np.quantile(w[may & np.isfinite(w)], np.arange(1, NFATIAS) / NFATIAS)


def medir(G, w, lim, wk, w2=None):
    """Por semana: forma por fatia (a) e inclinação (b). Nada atravessa semanas."""
    sem = []
    for idx in wk:
        X = G[idx]; ww = w[idx]; ok = np.isfinite(X).all(1) & np.isfinite(ww); X, ww = X[ok], ww[ok]
        fat = np.digitize(ww, lim)
        s = {"fatias": []}
        for j in range(NFATIAS):
            m = fat == j; n = int(m.sum())
            if n < N_MIN_FATIA:
                s["fatias"].append({"j": j + 1, "n": n}); continue
            C = np.cov(X[m].T); lam, vec = np.linalg.eigh(C); lam = lam[::-1]; vec = vec[:, ::-1]
            lam = np.maximum(lam, 1e-12)
            s["fatias"].append({"j": j + 1, "n": n, "w_medio": float(ww[m].mean()),
                                "s13": float(np.log(lam[0] / lam[2])), "s12": float(np.log(lam[0] / lam[1])), "s23": float(np.log(lam[1] / lam[2])),
                                "meio_logdet": float(0.5 * np.sum(np.log(lam))), "cos_eixo": [float(abs(v)) for v in vec[:, 0]]})
        s["valida_a"] = sum("s13" in f for f in s["fatias"]) >= FATIAS_MIN_SEMANA
        # (b) inclinação
        if len(ww) >= N_MIN_SEMANA_B:
            A = np.column_stack([X, np.ones(len(X))]); b = np.linalg.lstsq(A, ww, rcond=None)[0]
            r2 = 1 - np.sum((ww - A @ b) ** 2) / np.sum((ww - ww.mean()) ** 2)
            Q = np.column_stack([X, X ** 2, X[:, [0]] * X[:, [1]], X[:, [0]] * X[:, [2]], X[:, [1]] * X[:, [2]], np.ones(len(X))])
            bq = np.linalg.lstsq(Q, ww, rcond=None)[0]
            r2q = 1 - np.sum((ww - Q @ bq) ** 2) / np.sum((ww - ww.mean()) ** 2)
            s.update({"n": int(len(ww)), "r2": float(r2), "r2_quad": float(r2q), "rho_eixos": [float(spearmanr(ww, X[:, i]).correlation) for i in range(3)]})
            if w2 is not None:
                w2w = w2[idx][ok]; ok2 = np.isfinite(w2w)
                if ok2.sum() >= N_MIN_SEMANA_B:
                    b2 = np.linalg.lstsq(A[ok2], w2w[ok2], rcond=None)[0]
                    s["r2_ew10"] = float(1 - np.sum((w2w[ok2] - A[ok2] @ b2) ** 2) / np.sum((w2w[ok2] - w2w[ok2].mean()) ** 2))
        s["valida_b"] = "r2" in s
        sem.append(s)
    return sem


def resumo(sem):
    """Estatísticas do período a partir das semanas (sem acesso a nada além delas)."""
    va = [s for s in sem if s["valida_a"]]; vb = [s for s in sem if s["valida_b"]]
    out = {"semanas_validas_a": len(va), "semanas_validas_b": len(vb), "valido_a": len(va) >= SEMANAS_MIN, "valido_b": len(vb) >= SEMANAS_MIN}
    if out["valido_a"]:
        pares = [(f["j"], f) for s in va for f in s["fatias"] if "s13" in f]
        j = np.array([p[0] for p in pares]); F = [p[1] for p in pares]
        out["rho_forma"] = float(spearmanr(j, [f["s13"] for f in F]).correlation)
        out["rho_forma_s12"] = float(spearmanr(j, [f["s12"] for f in F]).correlation)
        out["rho_forma_s23"] = float(spearmanr(j, [f["s23"] for f in F]).correlation)
        wm = np.array([f["w_medio"] for f in F]); ld = np.array([f["meio_logdet"] for f in F])
        out["taxa_zoom"] = float(np.polyfit(wm, ld, 1)[0])
        out["cos_eixo_por_fatia"] = [[float(np.mean([f["cos_eixo"][i] for f in F if f["j"] == jj])) for i in range(3)] for jj in range(1, NFATIAS + 1)
                                     if any(f["j"] == jj for f in F)]
        out["s13_por_fatia"] = [float(np.mean([f["s13"] for f in F if f["j"] == jj])) for jj in range(1, NFATIAS + 1) if any(f["j"] == jj for f in F)]
    if out["valido_b"]:
        out["r2_tilt"] = float(np.mean([s["r2"] for s in vb])); out["r2_quad"] = float(np.mean([s["r2_quad"] for s in vb]))
        out["rho_eixos"] = [float(np.mean([s["rho_eixos"][i] for s in vb])) for i in range(3)]
        e = [s["r2_ew10"] for s in vb if "r2_ew10" in s]
        if e: out["r2_tilt_ew10"] = float(np.mean(e))
    return out


def rodar(meses, ini, fim, may_fim="2026-06-01"):
    kl = E.carregar(meses, ROOT / "dados"); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp(may_fim, tz="UTC")).to_numpy(); i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)

    def serie(k_):
        G = GR.regua(E.coords_orig(k_), may); w = quarta(k_, may); lim = limites(w, may)
        return medir(G, w, lim, wk, quarta(k_, may, "ew10"))
    series = {"real": serie(kl)}; print("  real: ok", flush=True)
    for s in MS.SEEDS_M:
        k_, _, _ = MS.gerar_m(kl, ts, i0, s); series[f"M_{s}"] = serie(k_); print(f"  M_{s}: ok", flush=True)
    return {"semanas": [str(ts.iloc[w[0]].date()) for w in wk], "series": series, "resumo": {k: resumo(v) for k, v in series.items()}}


def classes(res):
    R = res["resumo"]; real = R["real"]; Ms = [R[f"M_{s}"] for s in MS.SEEDS_M]
    out = {}
    if real.get("valido_a") and all(m.get("valido_a") for m in Ms):
        mx = max(m["rho_forma"] for m in Ms); mn = min(m["rho_forma"] for m in Ms)
        out["a"] = {"rho_real": real["rho_forma"], "M_min": mn, "M_max": mx,
                    "veredito": "CONFIRMADA" if real["rho_forma"] > mx else "NÃO CONFIRMADA",
                    "classe": "acima do M" if real["rho_forma"] > mx else ("dentro do M" if real["rho_forma"] >= mn else "abaixo do M")}
    else:
        out["a"] = {"veredito": "INCONCLUSIVO"}
    if real.get("valido_b") and all(m.get("valido_b") for m in Ms):
        mx = max(m["r2_tilt"] for m in Ms); mn = min(m["r2_tilt"] for m in Ms); r = real["r2_tilt"]
        out["b"] = {"r2_real": r, "M_min": mn, "M_max": mx,
                    "veredito": "CONFIRMADA" if mn <= r <= mx else ("NÃO CONFIRMADA, mais entrelaçada" if r > mx else "NÃO CONFIRMADA, menos entrelaçada")}
    else:
        out["b"] = {"veredito": "INCONCLUSIVO"}
    return out


def imprimir(res, titulo):
    print(f"\n== H-4D-01 [{titulo}]")
    for nome, r in res["resumo"].items():
        print(f"  {nome:7s} a: ρ_forma {r.get('rho_forma', float('nan')):+.3f} (s12 {r.get('rho_forma_s12', float('nan')):+.3f}, s23 {r.get('rho_forma_s23', float('nan')):+.3f}) "
              f"zoom {r.get('taxa_zoom', float('nan')):.2f} sem {r['semanas_validas_a']} | b: R² {r.get('r2_tilt', float('nan')):.3f} quad {r.get('r2_quad', float('nan')):.3f} "
              f"ew10 {r.get('r2_tilt_ew10', float('nan')):.3f} ρ_eixos {[round(x, 2) for x in r.get('rho_eixos', [])]}", flush=True)
    print("  s13 por fatia (real):", [round(x, 2) for x in res["resumo"]["real"].get("s13_por_fatia", [])])
    print("  classificação:", json.dumps(classes(res), ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--periodo", choices=list(GR.PERIODOS)); g.add_argument("--paridade", action="store_true"); g.add_argument("--julgamento", action="store_true")
    a = ap.parse_args(); out_dir = ROOT / "resultados"; out_dir.mkdir(exist_ok=True)
    if a.periodo:
        meses, ini, fim = GR.PERIODOS[a.periodo]
        res = rodar(meses, ini, fim, "2026-05-03" if a.periodo == "fumaca" else "2026-06-01")
        if a.periodo == "fumaca":
            print("fumaça: código rodou; estatísticas não impressas", flush=True); return
        imprimir(res, a.periodo); res["classificacao"] = classes(res)
        (out_dir / f"H-4D-01_exploracao_{a.periodo}.json").write_text(json.dumps(res, ensure_ascii=False)); return
    if a.paridade:
        meses, ini, fim = MODOS["paridade"]; res = rodar(meses, ini, fim)
        ref = json.loads((out_dir / "H-4D-01_exploracao_junjul.json").read_text())["resumo"]
        dif = max(abs(res["resumo"][s][k] - ref[s][k]) for s in ref for k in ("rho_forma", "r2_tilt", "taxa_zoom", "r2_quad"))
        print(f"paridade: diferença máxima contra a exploração = {dif:.2e}")
        (out_dir / "H-4D-01_paridade.json").write_text(json.dumps({"diferenca_maxima": dif, "resumo": res["resumo"]}, ensure_ascii=False))
        sys.exit(0 if dif < 1e-9 else "Paridade falhou")
    alvo = out_dir / "H-4D-01_julgamento.json"
    if alvo.exists():
        sys.exit("H-4D-01 já julgado: julgamento único")
    meses, ini, fim = MODOS["julgamento"]; res = rodar(meses, ini, fim)
    imprimir(res, "julgamento outubro/2026"); res["hipotese"] = "H-4D-01"; res["classificacao"] = classes(res)
    alvo.write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
