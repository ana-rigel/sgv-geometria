"""Teste 39 (a ordem líquida): o Laço III-a do teste 38 com C e |R₃| descontados do piso do acaso de cada um
(0,257 para o disco de 12 anéis; 0,088 para o andar 3, medido no modelo com K = 0). Dois sabores: cortada (max(0, ·)) e
sem corte. 5.000 Myr, 100 sementes, escuta no andar 3. Predição: PREDICAO_teste39_ordem_liquida.md (commit 6ce0122).

    python ia-geometrica/teste39.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste37 as T37

ROOT = Path(__file__).resolve().parent
T, NS, SEMENTE = 5000, 100, 39
DW, KC, NA, LAM = T37.DW, T37.KC, T37.NA, T37.LAM[:3]
FAIXA = T37.FAIXA; LOGG = (np.log(0.05), np.log(20.0))
PISO_C, PISO_R3, ETA = 0.257, 0.088, 0.05

rng = np.random.default_rng(SEMENTE)
TH0 = T37.SIG0 * rng.normal(size=(NS, NA))
XI = rng.normal(size=(T, NS, NA)) * np.sqrt(2 * T37.D)


def ordem(x, piso, corte):
    v = (x - piso) / (1.0 - piso)
    return np.maximum(0.0, v) if corte else v


def rodar(Kf, nasce="semeada", laco=None):
    K = Kf * KC; th = TH0.copy(); z0 = np.exp(1j * th).mean(1)
    R = np.tile(z0[:, None], (1, 3)) if nasce == "semeada" else np.zeros((NS, 3), complex)
    logg = np.zeros(NS); teto = np.full(NS, -1)
    C = np.zeros((T + 1, NS)); C[0] = np.abs(z0); traj = []; rel = np.zeros((1000, NS, NA))
    for t in range(T):
        z = np.exp(1j * th).mean(1); prev = z
        for k in range(3):
            R[:, k] = R[:, k] + LAM[k] * (prev - R[:, k]); prev = R[:, k]
        A = R[:, 2]; g = np.exp(logg) if laco else np.ones(NS); fase = np.angle(A)[:, None]
        th = th + DW + (K * g * np.abs(A))[:, None] * np.sin(fase - th) + XI[t]
        Cn = np.abs(np.exp(1j * th).mean(1)); C[t + 1] = Cn
        if t >= T - 1000: rel[t - (T - 1000)] = th - fase
        if laco:
            corte = laco == "cortada"
            logg = np.clip(logg + ETA * (ordem(Cn, PISO_C, corte) - ordem(np.abs(A), PISO_R3, corte)), *LOGG)
            teto[(teto < 0) & (logg >= LOGG[1] - 1e-9)] = t
        if t % 250 == 0: traj.append([t, float(np.mean(np.exp(logg) if laco else 1.0)), float(np.mean(np.abs(A))), float(np.mean(Cn))])
    dr = np.abs(np.unwrap(rel, axis=0)[-1] - np.unwrap(rel, axis=0)[0]); cb = C[3000:].mean(0)
    return {"cb": cb, "mediana": float(np.median(cb)), "na_faixa": int(np.sum((cb >= FAIXA[0]) & (cb <= FAIXA[1]))),
            "travados": float(np.mean(dr < np.pi)), "traj_t_g_R3_C": traj,
            "sementes_no_teto": int(np.sum(teto >= 0)), "t_teto_mediano": (float(np.median(teto[teto >= 0])) if np.any(teto >= 0) else None)}


def main():
    assert (ROOT / "PREDICAO_teste39_ordem_liquida.md").exists(), "sem predição, sem teste"
    res = {}
    for Kf in (0.7, 0.8, 0.9):
        res[f"ref_semeada_K{Kf}"] = rodar(Kf, "semeada", None)
        for s in ("cortada", "semcorte"):
            res[f"{s}_semeada_K{Kf}"] = rodar(Kf, "semeada", s)
    for s in ("cortada", "semcorte"):
        res[f"{s}_vazia_K0.8"] = rodar(0.8, "vazia", s)
    meds = [res[f"semcorte_semeada_K{k}"]["mediana"] for k in (0.7, 0.8, 0.9)]
    J = {"J1": res["cortada_vazia_K0.8"]["mediana"] <= 0.31, "J2": res["semcorte_vazia_K0.8"]["mediana"] <= 0.31,
         "J3": res["semcorte_semeada_K0.8"]["na_faixa"] >= 80, "J4": (max(meds) - min(meds) <= 0.05) and min(meds) >= 0.40}
    out = {k: {q: v for q, v in o.items() if q != "cb"} for k, o in res.items()}
    out["espalhamento_semcorte"] = max(meds) - min(meds); out["J"] = {k: bool(v) for k, v in J.items()}
    for k, o in res.items():
        print(f"{k:22s} C̄ {o['mediana']:.3f} | faixa {o['na_faixa']:3d} | travados {o['travados']:.2f} | teto {o['sementes_no_teto']:3d} (t {o['t_teto_mediano']}) | "
              + " ".join(f"[{int(a)}: g {b:.2f} |R| {c:.2f} C {d:.2f}]" for a, b, c, d in o["traj_t_g_R3_C"][::4]))
    print(f"espalhamento sem corte: {out['espalhamento_semcorte']:.3f}")
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in J.items()))
    (ROOT / "resultados_teste39.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
