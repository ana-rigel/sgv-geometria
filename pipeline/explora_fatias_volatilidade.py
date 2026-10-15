"""Volatilidade como 4ª dimensão na geometria: (1a) borda agitada por fatia de temperatura, (1b) cascas por fatia,
(2) colapso de escala do campo em unidades de volatilidade. Previsão: PREDICAO_fatias_volatilidade.md.

    python pipeline/explora_fatias_volatilidade.py --periodo fumaca|junjul|agoset
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import explora_geometria_residual as GR  # noqa: E402  (regua, semanas, campo_ll, p1, axes, angulo, build_shell)
import explora_volatilidade_escondida as V  # noqa: E402  (estimativas)
import explora_volatilidade_multiescala as MS  # noqa: E402  (gerar_m)

E = GR.E
BANDAS = {"nucleo": (0, 1), "meio": (1, 3), "extremos": (3, 10)}
SEEDS_REF = [4026, 4027]


def fatias(sig, may):
    ls = np.log(sig); q = np.nanquantile(ls[may & np.isfinite(ls)], [1 / 3, 2 / 3])
    lab = np.full(len(sig), -1); ok = np.isfinite(ls)
    lab[ok] = np.digitize(ls[ok], q)
    return lab


def campos_por_fatia(G, sig, lab, wk):
    rng = np.random.default_rng(20261019); acc = {j: {"Draw": [], "Dstd": [], "ext": []} for j in range(3)}
    for k in range(1, len(wk)):
        tr, te = wk[k - 1], wk[k]
        a, b = tr[:-1], tr[1:]
        X = G[a]; S = G[b] - G[a]; sc = sig[a]
        okt = np.isfinite(X).all(1) & np.isfinite(S).all(1) & np.isfinite(sc)
        P = G[te]; okp = np.isfinite(P).all(1)
        for j in range(3):
            mt = okt & (lab[a] == j)
            if mt.sum() < 2 * GR.K: continue
            idx = np.where(okp & (lab[te] == j))[0]
            if not len(idx): continue
            ext = np.abs(P[idx]).max(1); core = idx[ext < 1]; core = rng.choice(core, min(3000, len(core)), replace=False)
            sel = np.r_[core, idx[ext >= 1]]; P0 = P[sel]
            for c in range(0, len(sel), 2000):
                acc[j]["Draw"].append(GR.campo_ll(X[mt], S[mt], P0[c:c + 2000]))
                acc[j]["Dstd"].append(GR.campo_ll(X[mt], S[mt] / sc[mt][:, None], P0[c:c + 2000]))
                acc[j]["ext"].append(np.abs(P0[c:c + 2000]).max(1))
    return {j: {k: np.concatenate(v) if v else np.array([]) for k, v in d.items()} for j, d in acc.items()}


def teste1a_2(G, sig, lab, wk):
    todos = GR.p1(G, wk)  # mesma função da geometria residual (paridade: R jun–jul real = 6,83)
    F = campos_por_fatia(G, sig, lab, wk); out = {"R_todos": todos["R"], "fatias": {}}
    Rs = []
    for j, d in F.items():
        e = d["ext"]; fj = {"n_extremos": int(((e >= 3) & (e < 10)).sum())}
        for nome, (lo, hi) in BANDAS.items():
            m = (e >= lo) & (e < hi)
            fj[f"Draw_{nome}"] = float(np.median(d["Draw"][m])) if m.sum() >= 30 else None
            fj[f"Dstd_{nome}"] = float(np.median(d["Dstd"][m])) if m.sum() >= 30 else None
        if fj["Draw_extremos"] and fj["Draw_nucleo"]:
            fj["R"] = fj["Draw_extremos"] / fj["Draw_nucleo"]; Rs.append(fj["R"])
        out["fatias"][str(j)] = fj
    out["R_fatias"] = float(np.mean(Rs)) if Rs else None
    disp_b, disp_p = [], []
    for nome in BANDAS:
        vb = [out["fatias"][str(j)][f"Draw_{nome}"] for j in range(3)]; vp = [out["fatias"][str(j)][f"Dstd_{nome}"] for j in range(3)]
        if all(v is not None for v in vb + vp):
            disp_b.append(np.ptp(np.log(vb))); disp_p.append(np.ptp(np.log(vp)))
    out["Disp_bruto"] = float(np.mean(disp_b)) if disp_b else None; out["Disp_padr"] = float(np.mean(disp_p)) if disp_p else None
    out["C"] = float(1 - out["Disp_padr"] / out["Disp_bruto"]) if disp_b else None
    return out


def teste1b(G, lab, i_ini, i_fim):
    M = {"todos": {}, 0: {}, 1: {}, 2: {}}
    for k, s in enumerate(range(i_ini, i_fim + 1, GR.SNAP)):
        Xw = G[s - GR.W:s]; Lw = lab[s - GR.W:s]; ok = np.isfinite(Xw).all(1)
        grupos = {"todos": ok, 0: ok & (Lw == 0), 1: ok & (Lw == 1), 2: ok & (Lw == 2)}
        for g, m in grupos.items():
            if (g == "todos" and m.sum() < 0.95 * GR.W) or (g != "todos" and m.sum() < 300): continue
            try:
                M[g][k] = GR.axes(GR.build_shell(Xw[m], seed=20261009, n=25).mesh)
            except Exception:
                continue
    rot = {}
    for g, mp in M.items():
        r = [GR.angulo(mp[k], mp[k + GR.LAG]) for k in mp if k + GR.LAG in mp]
        rot[str(g)] = {"rot_mediana": float(np.median(r)) if r else None, "pares": len(r)}
    fs = [rot[str(j)]["rot_mediana"] for j in range(3) if rot[str(j)]["rot_mediana"] is not None]
    return {"rot_todos": rot["todos"]["rot_mediana"], "rot_fatias": float(np.mean(fs)) if fs else None, "detalhe": rot}


def medir(kl, may, wk, i_ini, i_fim):
    G = GR.regua(E.coords_orig(kl), may); sig = V.estimativas(kl)["har"]; lab = fatias(sig, may)
    return {"T1a_T2": teste1a_2(G, sig, lab, wk), "T1b": teste1b(G, lab, i_ini, i_fim)}


def classes(r):
    t = r["T1a_T2"]; razao = t["R_fatias"] / t["R_todos"]
    c1a = "explica" if razao <= 0.5 else ("explica em parte" if razao <= 0.8 else "não explica")
    c2 = "colapsa" if t["C"] >= 0.7 else ("colapsa em parte" if t["C"] >= 0.3 else "não colapsa")
    return {"1a": c1a, "razao_R": razao, "1b_mais_estaveis": r["T1b"]["rot_fatias"] < r["T1b"]["rot_todos"], "2": c2, "C": t["C"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--periodo", choices=list(GR.PERIODOS), required=True); ap.add_argument("--dados", default=str(ROOT / "dados"))
    a = ap.parse_args(); meses, ini, fim = GR.PERIODOS[a.periodo]
    kl = E.carregar(meses, Path(a.dados)); ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
    assert ts.iloc[-1] < pd.Timestamp("2026-10-01", tz="UTC"), "nada de outubro"
    may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
    if a.periodo == "fumaca":
        may = (ts < pd.Timestamp("2026-05-03", tz="UTC")).to_numpy()
    i0 = int(np.argmax(~may)); wk = GR.semanas(ts, ini, fim)
    i_ini = int(np.searchsorted(ts.values, pd.Timestamp(ini, tz="UTC").to_datetime64())); i_fim = int(np.searchsorted(ts.values, pd.Timestamp(fim, tz="UTC").to_datetime64()))
    res = {"real": medir(kl, may, wk, i_ini, i_fim)}; print("  real: ok", flush=True)
    for s in SEEDS_REF:
        k_, _, _ = MS.gerar_m(kl, ts, i0, s); res[f"M_{s}"] = medir(k_, may, wk, i_ini, i_fim); print(f"  M_{s}: ok", flush=True)
    if a.periodo == "fumaca":
        print("fumaça: código rodou; estatísticas não impressas", flush=True); return
    out = {"periodo": a.periodo, "series": res, "classificacao_real": classes(res["real"]), "referencia_M": {k: classes(v) for k, v in res.items() if k != "real"}}
    print(f"\n== fatias de volatilidade [{a.periodo}]")
    for nome, r in res.items():
        t = r["T1a_T2"]; c = classes(r)
        print(f"  {nome:7s} 1a: R_todos {t['R_todos']:.2f} R_fatias {t['R_fatias']:.2f} (razão {c['razao_R']:.2f}, R por fatia "
              f"{[round(t['fatias'][str(j)].get('R', float('nan')), 2) for j in range(3)]})"
              f" | 1b: rot todos {r['T1b']['rot_todos']:.1f}° fatias {r['T1b']['rot_fatias']:.1f}° {[r['T1b']['detalhe'][str(j)]['rot_mediana'] for j in range(3)]}"
              f" | 2: Disp bruto {t['Disp_bruto']:.2f} padr {t['Disp_padr']:.2f} C {t['C']:.2f}", flush=True)
    print("  classificação (real):", out["classificacao_real"])
    (ROOT / "resultados").mkdir(exist_ok=True)
    (ROOT / "resultados" / f"fatias_volatilidade_{a.periodo}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
