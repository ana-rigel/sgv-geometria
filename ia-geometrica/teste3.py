"""Teste 3 (salto sobre deriva). Predição: PREDICAO_teste3.md. Roda só porque a predição existe."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import v0 as V

ROOT = Path(__file__).resolve().parent
assert (ROOT / "PREDICAO_teste3.md").exists(), "sem predição, sem teste"
N, CAL, SEEDS, W = 10000, 2000, range(1000, 1100), 20
LAMS = 0.15 / 10.0 ** np.arange(4)


def tensao_T0(x):
    obs = V.Observador(x.shape[1], lams=LAMS); T0 = np.zeros(len(x))
    for t in range(len(x)):
        T0[t] = np.linalg.norm(x[t] - obs.R[0]); obs.passo(x[t])
    return T0


def avaliar(reg, saltos):
    """Entradas em ruptura na janela de medida; atraso por salto, falsos alarmes por 1000 passos, detecção."""
    entradas = np.where((reg[1:] == 2) & (reg[:-1] != 2))[0] + 1; entradas = entradas[entradas >= CAL]
    saltos = saltos[saltos >= CAL]; atrasos = []; usadas = np.zeros(len(entradas), dtype=bool)
    for s in saltos:
        m = np.where((entradas >= s) & (entradas <= s + W))[0]
        if len(m): atrasos.append(int(entradas[m[0]] - s)); usadas[m] = True
    fa = int((~usadas).sum()) / ((N - CAL) / 1000.0)
    return (float(np.median(atrasos)) if atrasos else float("nan")), fa, (len(atrasos) / len(saltos) if len(saltos) else float("nan"))


def main():
    out = {"sementes": {}}; dA, dFA, dD = [], [], []
    for s in SEEDS:
        x, saltos = V.mundo_salto(N, s); T0 = tensao_T0(x)
        med = np.median(T0[:CAL]); esc = max(np.quantile(np.abs(T0[:CAL] - med), 0.995) / 3, 1e-12)
        rg = V.regime((T0 - med) / esc); rr = V.regime_relativo(T0)
        a_g, fa_g, d_g = avaliar(rg, saltos); a_r, fa_r, d_r = avaliar(rr, saltos)
        dA.append(a_r - a_g); dFA.append(fa_r - fa_g); dD.append(d_g - d_r)
        out["sementes"][str(s)] = {"saltos_medida": int((saltos >= CAL).sum()), "regua": {"atraso_mediano": a_g, "fa_por_1000": fa_g, "deteccao": d_g},
                                   "relativo": {"atraso_mediano": a_r, "fa_por_1000": fa_r, "deteccao": d_r}}
        if (s - 1000) % 10 == 0: print(f"  s{s}: régua atraso {a_g:.0f} FA {fa_g:.1f} det {d_g:.2f} | relativo atraso {a_r:.0f} FA {fa_r:.1f} det {d_r:.2f}", flush=True)
    dA, dFA, dD = np.array(dA), np.array(dFA), np.array(dD)
    a = bool(np.nanmin(dFA) > 0); b = bool(np.nanmin(dA) >= 0 and np.nanmedian(dA) > 0); c = bool((dD >= 0).sum() >= 95)
    out["resumo"] = {"dFA_env": [float(np.nanmin(dFA)), float(np.nanmax(dFA))], "dFA_mediana": float(np.nanmedian(dFA)),
                     "dAtraso_env": [float(np.nanmin(dA)), float(np.nanmax(dA))], "dAtraso_mediana": float(np.nanmedian(dA)), "dDet_ge0": int((dD >= 0).sum()),
                     "medias": {k: {m: float(np.nanmean([out["sementes"][str(s)][k][m] for s in SEEDS])) for m in ("atraso_mediano", "fa_por_1000", "deteccao")} for k in ("regua", "relativo")},
                     "criterio": {"a_FA": a, "b_atraso": b, "c_deteccao": c, "passa": a and b and c}}
    print(f"\n== teste 3: ΔFA env ({np.nanmin(dFA):.1f}; {np.nanmax(dFA):.1f}) | Δatraso env ({np.nanmin(dA):.0f}; {np.nanmax(dA):.0f}) mediana {np.nanmedian(dA):.0f} | Δdet≥0 em {(dD>=0).sum()} → (a) {a} (b) {b} (c) {c} → {'PASSA' if a and b and c else 'REPROVA'}")
    print("   médias:", json.dumps(out["resumo"]["medias"]))
    (ROOT / "resultados_teste3.json").write_text(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
