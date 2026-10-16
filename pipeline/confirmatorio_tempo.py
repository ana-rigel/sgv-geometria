"""H-TEMPO-01 — memória da volatilidade em lei de potência (a) e reversão na borda do cubo (b).
Definições congeladas em PREREGISTRO_H-TEMPO-01.md.

    python pipeline/confirmatorio_tempo.py --periodo fumaca|junjul|agoset   # meses abertos
    python pipeline/confirmatorio_tempo.py --paridade                        # reproduz resultados/H-TEMPO-01_exploracao_junjul.json
    python pipeline/confirmatorio_tempo.py --julgamento                      # outubro/2026, uma única vez
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

E = GR.E
LAGS = [1, 2, 3, 4, 6, 8, 11, 16, 23, 32, 45, 64, 91, 128, 181, 256, 362, 512, 724, 1024, 1440]
LAGS_MIN_POS, BETA_MIN, BETA_MAX = 15, 0.1, 0.6
BORDA, NUCLEO, N_MIN_BORDA, SEMANAS_MIN = 3.0, 1.0, 100, 3
MODOS = {"paridade": (["2026-05", "2026-06", "2026-07"], "2026-06-01", "2026-08-01"),
         "julgamento": (["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"], "2026-10-01", "2026-10-29")}


def retornos(kl):
    return np.diff(np.log(kl.close.values.astype(float)), prepend=np.nan)


def perfil_dia(r, ts, may):
    """s(h): mediana de |r| por minuto do dia, estimada em maio."""
    h = (ts.dt.hour * 60 + ts.dt.minute).to_numpy(); a = np.abs(r)
    s = np.full(1440, np.nan)
    for k in range(1440):
        m = may & (h == k) & np.isfinite(a)
        if m.any(): s[k] = np.median(a[m])
    s = np.where(np.isfinite(s) & (s > 0), s, np.nanmedian(s))
    return s[h]


def acf(a, idx, lags):
    """Autocorrelação de a nos índices idx (um bloco contíguo por semana); pares dentro do mesmo bloco."""
    out = []
    for tau in lags:
        num = den = 0.0; n = 0; mu_parts = []
        for blk in idx:
            x = a[blk]; x = x[np.isfinite(x)]
            if len(x) <= tau + 10: continue
            mu_parts.append(x)
        if not mu_parts: out.append(np.nan); continue
        allx = np.concatenate(mu_parts); mu = allx.mean(); var = allx.var()
        for blk in idx:
            x = a[blk]; x = x[np.isfinite(x)]
            if len(x) <= tau + 10: continue
            num += np.sum((x[:-tau] - mu) * (x[tau:] - mu)); n += len(x) - tau
        out.append(float(num / n / var) if n and var > 0 else np.nan)
    return np.array(out)


def ajustes(rho):
    tau = np.array(LAGS, float); ok = np.isfinite(rho) & (rho > 0)
    res = {"n_pos": int(ok.sum())}
    if ok.sum() < 3: return res
    y = np.log(rho[ok]); t = tau[ok]
    b1, a1 = np.polyfit(np.log(t), y, 1); yh = a1 + b1 * np.log(t)
    res["beta"] = float(-b1); res["r2_pot"] = float(1 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2))
    b2, a2 = np.polyfit(t, y, 1); yh2 = a2 + b2 * t
    res["theta"] = float(-1 / b2) if b2 < 0 else float("inf"); res["r2_exp"] = float(1 - np.sum((y - yh2) ** 2) / np.sum((y - y.mean()) ** 2))
    res["delta_r2"] = res["r2_pot"] - res["r2_exp"]
    return res


def medir_a(kl, ts, may, wk, s_dia):
    r = retornos(kl); a = np.abs(r) / s_dia
    blk = [np.concatenate(wk)]   # período inteiro agrupado (as semanas são contíguas)
    rho = acf(a, blk, LAGS); out = {"rho": [None if not np.isfinite(v) else float(v) for v in rho], **ajustes(rho)}
    out["valido"] = out["n_pos"] >= LAGS_MIN_POS
    lh = np.log(V.estimativas(kl)["har"]); rho_h = acf(lh, blk, LAGS); out["har"] = ajustes(rho_h)
    return out


def medir_b(kl, may, wk):
    r = retornos(kl); G = GR.regua(E.coords_orig(kl), may); ext = np.nanmax(np.abs(G), axis=1)
    sem = []
    for idx in wk:
        i = idx[:-1]; t1 = i + 1
        ok = np.isfinite(r[i]) & np.isfinite(r[t1]) & np.isfinite(ext[i])
        i, t1 = i[ok], t1[ok]; e = ext[i]
        g = {"borda": e >= BORDA, "borda5": e >= 5.0, "nucleo": e < NUCLEO}
        s = {"n_borda": int(g["borda"].sum()), "n_nucleo": int(g["nucleo"].sum())}
        for nome, m in g.items():
            if m.sum() < 20: continue
            rt, r1 = r[i[m]], r[t1[m]]
            s[f"phi_{nome}"] = float(np.sum(rt * r1) / np.sum(rt ** 2))
            s[f"flip_{nome}"] = float(np.mean(np.sign(rt) != np.sign(r1)))
            j = i[m]; j = j[j + 5 < len(r)]
            R5 = np.array([np.nansum(r[k + 1:k + 6]) for k in j])
            s[f"phi5_{nome}"] = float(np.sum(r[j] * R5) / np.sum(r[j] ** 2))
        s["valida"] = s["n_borda"] >= N_MIN_BORDA and "phi_nucleo" in s
        if s["valida"]: s["delta_phi"] = s["phi_borda"] - s["phi_nucleo"]
        sem.append(s)
    va = [s for s in sem if s["valida"]]
    out = {"semanas": sem, "semanas_validas": len(va), "valido": len(va) >= SEMANAS_MIN}
    if out["valido"]:
        w = np.array([s["n_borda"] for s in va], float)
        for k in ("phi_borda", "phi_nucleo", "delta_phi", "flip_borda", "flip_nucleo"):
            out[k] = float(np.sum(w * np.array([s[k] for s in va])) / w.sum())
        for k in ("phi_borda5", "phi5_borda", "phi5_nucleo"):
            v = [s[k] for s in va if k in s]
            if v: out[k] = float(np.mean(v))
    return out


def rodar(meses, ini, fim, may_fim="2026-06-01"):
    kl = E.carregar(meses, ROOT / "dados"); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    may = (ts < pd.Timestamp(may_fim, tz="UTC")).to_numpy(); i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    s_dia = perfil_dia(retornos(kl), ts, may)   # s(h) de maio, do real, usada em todas as séries
    series = {"real": {"a": medir_a(kl, ts, may, wk, s_dia), "b": medir_b(kl, may, wk)}}; print("  real: ok", flush=True)
    for s in MS.SEEDS_M:
        k_, _, _ = MS.gerar_m(kl, ts, i0, s); series[f"M_{s}"] = {"a": medir_a(k_, ts, may, wk, s_dia), "b": medir_b(k_, may, wk)}; print(f"  M_{s}: ok", flush=True)
    return {"semanas": [str(ts.iloc[w[0]].date()) for w in wk], "series": series}


def classes(res):
    S = res["series"]; real = S["real"]; Ms = [S[f"M_{s}"] for s in MS.SEEDS_M]; out = {}
    if real["a"]["valido"] and all(m["a"]["valido"] for m in Ms):
        mx = max(m["a"]["delta_r2"] for m in Ms); b = real["a"]["beta"]; d = real["a"]["delta_r2"]
        c1, c2 = d > mx, BETA_MIN <= b <= BETA_MAX
        rr = np.array([v if v is not None else np.nan for v in real["a"]["rho"]])
        rm = np.array([[v if v is not None else np.nan for v in m["a"]["rho"]] for m in Ms])
        fora = [LAGS[i] for i in range(len(LAGS)) if np.isfinite(rr[i]) and (rr[i] > np.nanmax(rm[:, i]) or rr[i] < np.nanmin(rm[:, i]))]
        out["a"] = {"delta_r2_real": d, "M_max": mx, "beta_real": b, "cond_envelope": bool(c1), "cond_beta": bool(c2),
                    "veredito": "CONFIRMADA" if c1 and c2 else "NÃO CONFIRMADA", "descola_em": fora[0] if fora else None}
    else:
        out["a"] = {"veredito": "INCONCLUSIVO"}
    if real["b"]["valido"] and all(m["b"]["valido"] for m in Ms):
        mn = min(m["b"]["delta_phi"] for m in Ms); mx = max(m["b"]["delta_phi"] for m in Ms); d = real["b"]["delta_phi"]
        out["b"] = {"delta_phi_real": d, "M_min": mn, "M_max": mx, "veredito": "CONFIRMADA" if d < mn else "NÃO CONFIRMADA",
                    "classe": "abaixo do M" if d < mn else ("dentro do M" if d <= mx else "acima do M")}
    else:
        out["b"] = {"veredito": "INCONCLUSIVO"}
    return out


def imprimir(res, titulo):
    print(f"\n== H-TEMPO-01 [{titulo}]")
    for nome, s in res["series"].items():
        a, b = s["a"], s["b"]
        print(f"  {nome:7s} a: β {a.get('beta', float('nan')):.3f} R²pot {a.get('r2_pot', float('nan')):.3f} R²exp {a.get('r2_exp', float('nan')):.3f} ΔR² {a.get('delta_r2', float('nan')):+.3f} "
              f"(n_pos {a['n_pos']}; har β {a['har'].get('beta', float('nan')):.2f} ΔR² {a['har'].get('delta_r2', float('nan')):+.2f})"
              f" | b: φ_borda {b.get('phi_borda', float('nan')):+.3f} φ_núcleo {b.get('phi_nucleo', float('nan')):+.3f} Δφ {b.get('delta_phi', float('nan')):+.3f} "
              f"φ5_borda {b.get('phi5_borda', float('nan')):+.3f} flips {b.get('flip_borda', float('nan')):.2f}/{b.get('flip_nucleo', float('nan')):.2f} sem {b['semanas_validas']}", flush=True)
    rr = res["series"]["real"]["a"]["rho"]; print("  ρ(τ) real:", [round(v, 3) if v is not None else None for v in rr])
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
        (out_dir / f"H-TEMPO-01_exploracao_{a.periodo}.json").write_text(json.dumps(res, ensure_ascii=False)); return
    if a.paridade:
        meses, ini, fim = MODOS["paridade"]; res = rodar(meses, ini, fim)
        ref = json.loads((out_dir / "H-TEMPO-01_exploracao_junjul.json").read_text())["series"]
        dif = max(abs(res["series"][s]["a"][k] - ref[s]["a"][k]) for s in ref for k in ("delta_r2", "beta")) if all("delta_r2" in ref[s]["a"] for s in ref) else float("inf")
        dif = max(dif, max(abs(res["series"][s]["b"]["delta_phi"] - ref[s]["b"]["delta_phi"]) for s in ref if "delta_phi" in ref[s]["b"]))
        print(f"paridade: diferença máxima contra a exploração = {dif:.2e}")
        (out_dir / "H-TEMPO-01_paridade.json").write_text(json.dumps({"diferenca_maxima": dif}, ensure_ascii=False))
        sys.exit(0 if dif < 1e-9 else "Paridade falhou")
    alvo = out_dir / "H-TEMPO-01_julgamento.json"
    if alvo.exists():
        sys.exit("H-TEMPO-01 já julgado: julgamento único")
    meses, ini, fim = MODOS["julgamento"]; res = rodar(meses, ini, fim)
    imprimir(res, "julgamento outubro/2026"); res["hipotese"] = "H-TEMPO-01"; res["classificacao"] = classes(res)
    alvo.write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
