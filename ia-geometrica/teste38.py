"""Teste 38 (o laço que apara): o modelo do teste 37, escuta no andar 3, 5.000 Myr. A voz g da memória se ajusta sem alvo
externo: III-a pela autoconsistência (log g ← log g + η(C − |R₃|)); III-b pela criticidade (busca do máximo da flutuação de C
com sondagem de 100 Myr). Referência: g = 1. 0,627 só no julgamento.
Predição: PREDICAO_teste38_laco_que_apara.md (commit ff8cc2f), escrita antes deste arquivo.

    python ia-geometrica/teste38.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste37 as T37

ROOT = Path(__file__).resolve().parent
T, NS, SEMENTE = 5000, 100, 38
LAM3 = T37.LAM[2]; DW, KC, NA = T37.DW, T37.KC, T37.NA
FAIXA = T37.FAIXA; LOGG = (np.log(0.05), np.log(20.0))

rng = np.random.default_rng(SEMENTE)
TH0 = T37.SIG0 * rng.normal(size=(NS, NA))
XI = rng.normal(size=(T, NS, NA)) * np.sqrt(2 * T37.D)


def rodar(Kf, nasce="semeada", laco=None):
    K = Kf * KC; th = TH0.copy(); z0 = np.exp(1j * th).mean(1)
    R = np.tile(z0[:, None], (1, 3)) if nasce == "semeada" else np.zeros((NS, 3), complex)   # andares 1–3
    lam = T37.LAM[:3]
    logg = np.zeros(NS); logg0 = np.zeros(NS)
    mC = np.abs(z0); mC2 = mC ** 2; chib = np.zeros(NS); G = np.zeros(NS); chis = []
    C = np.zeros((T + 1, NS)); C[0] = np.abs(z0); traj = []; rel = np.zeros((1000, NS, NA))
    for t in range(T):
        z = np.exp(1j * th).mean(1); prev = z
        for k in range(3):
            R[:, k] = R[:, k] + lam[k] * (prev - R[:, k]); prev = R[:, k]
        A = R[:, 2]; s = np.sin(2 * np.pi * t / 100.0)
        if laco == "b": g = np.exp(logg0 + 0.2 * s)
        elif laco == "a": g = np.exp(logg)
        else: g = np.ones(NS)
        fase = np.angle(A)[:, None]
        th = th + DW + (K * g * np.abs(A))[:, None] * np.sin(fase - th) + XI[t]
        Cn = np.abs(np.exp(1j * th).mean(1)); C[t + 1] = Cn
        if t >= T - 1000: rel[t - (T - 1000)] = th - fase
        if laco == "a":
            logg = np.clip(logg + 0.05 * (Cn - np.abs(A)), *LOGG)
        if laco == "b":
            mC = mC + (Cn - mC) / 50.0; mC2 = mC2 + (Cn ** 2 - mC2) / 50.0; chi = np.maximum(mC2 - mC ** 2, 0.0)
            chib = chib + (chi - chib) / 200.0; G = G + ((chi - chib) * s - G) / 200.0
            logg0 = np.clip(logg0 + 0.01 * G / (chib + 1e-4), *LOGG)
            if t % 250 == 0: chis.append(float(np.mean(chib)))
        if t % 250 == 0:
            traj.append([t, float(np.mean(g)), float(np.mean(np.abs(A))), float(np.mean(Cn))])
    dr = np.abs(np.unwrap(rel, axis=0)[-1] - np.unwrap(rel, axis=0)[0])
    cb = C[3000:].mean(0)
    return {"cb": cb, "mediana": float(np.median(cb)), "na_faixa": int(np.sum((cb >= FAIXA[0]) & (cb <= FAIXA[1]))),
            "travados": float(np.mean(dr < np.pi)), "traj_t_g_R3_C": traj, "chi_medio": chis}


def main():
    assert (ROOT / "PREDICAO_teste38_laco_que_apara.md").exists(), "sem predição, sem teste"
    res = {}
    for Kf in (0.7, 0.8, 0.9):
        for nome, laco in (("ref", None), ("IIIa", "a"), ("IIIb", "b")):
            res[f"{nome}_semeada_K{Kf}"] = rodar(Kf, "semeada", laco)
    for nome, laco in (("IIIa", "a"), ("IIIb", "b")):
        res[f"{nome}_vazia_K0.8"] = rodar(0.8, "vazia", laco)

    spread = lambda nome: max(res[f"{nome}_semeada_K{k}"]["mediana"] for k in (0.7, 0.8, 0.9)) - min(res[f"{nome}_semeada_K{k}"]["mediana"] for k in (0.7, 0.8, 0.9))
    J = {"J1": res["IIIa_semeada_K0.8"]["na_faixa"] >= 80, "J2": spread("IIIa") <= 0.05,
         "J3": res["IIIb_semeada_K0.8"]["na_faixa"] >= 80, "J4": spread("IIIb") <= 0.05,
         "J5": res["IIIa_vazia_K0.8"]["mediana"] <= 0.25 and res["IIIb_vazia_K0.8"]["mediana"] <= 0.25}
    out = {k: {q: v for q, v in o.items() if q != "cb"} for k, o in res.items()}
    out["espalhamento_entre_K"] = {"IIIa": spread("IIIa"), "IIIb": spread("IIIb"), "ref": spread("ref")}
    out["J"] = {k: bool(v) for k, v in J.items()}
    for k, o in res.items():
        tr = o["traj_t_g_R3_C"]
        print(f"{k:22s} C̄ {o['mediana']:.3f} | faixa {o['na_faixa']:3d} | travados {o['travados']:.2f} | "
              + " ".join(f"[{int(a)}: g {b:.2f} |R| {c:.2f} C {d:.2f}]" for a, b, c, d in tr[::4]))
    print("espalhamento entre K:", {k: round(v, 3) for k, v in out["espalhamento_entre_K"].items()})
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in J.items()))
    (ROOT / "resultados_teste38.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
