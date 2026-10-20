"""Teste 46: a janela de sincronização parcial prevista sem integrar. Autoconsistência do estado parcialmente travado de
Kuramoto (travados: sen = x, cos = √(1−x²); deslizantes: ⟨cos⟩ = 0, ⟨sen⟩ = x − sgn(x)√(x²−1)), resolvida em (r, Ω) para
cada K, comparada com as simulações do teste 44 (largura, K_L, C̄) e com uma simulação de quem desliza (N = 12).
Predição: PREDICAO_teste46_janela_sem_integrar.md (commit 9fe252a), escrita antes deste arquivo.

    python ia-geometrica/teste46.py        # o teste (exige a predição)
"""
import json, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste44 as T44
import teste41 as T41

ROOT = Path(__file__).resolve().parent
KG, PASSO = T44.KG, T44.PASSO
RG = np.linspace(0.005, 1.0, 200); NOM = 800


def s_med(x):
    a = np.abs(x); return np.where(a <= 1, x, x - np.sign(x) * np.sqrt(np.maximum(a * a - 1, 0)))


def resolver(dw, K):
    """Devolve (r, Ω, travados) do ramo de maior r, ou (0, None, None) se só há o incoerente."""
    N = len(dw); Rr = np.full(len(RG), -1.0); Om = np.full(len(RG), np.nan)
    for j, r in enumerate(RG):
        u = K * r; om = np.linspace(dw.min() - u, dw.max() + u, NOM)
        x = (dw[None, :] - om[:, None]) / u; G = s_med(x).sum(1)
        idx = np.flatnonzero(G[:-1] * G[1:] <= 0)
        best = -1.0
        for i in idx:
            o = om[i] - G[i] * (om[i + 1] - om[i]) / (G[i + 1] - G[i] if G[i + 1] != G[i] else 1e-30)
            xx = (dw - o) / u; R = np.sum(np.sqrt(np.clip(1 - xx ** 2, 0, None)) * (np.abs(xx) <= 1)) / N
            if R > best: best, Om[j] = R, o
        Rr[j] = best
    F = Rr - RG; ok = Rr >= 0
    raiz = None
    for j in range(len(RG) - 1, 0, -1):
        if ok[j] and ok[j - 1] and F[j - 1] >= 0 > F[j]:
            t = F[j - 1] / (F[j - 1] - F[j]); r = RG[j - 1] + t * (RG[j] - RG[j - 1]); o = Om[j - 1] + t * (Om[j] - Om[j - 1])
            raiz = (r, o); break
    if raiz is None: return 0.0, None, None
    r, o = raiz; trav = np.abs((dw - o) / (K * r)) <= 1
    return float(r), float(o), trav


def main():
    assert (ROOT / "PREDICAO_teste46_janela_sem_integrar.md").exists(), "sem predição, sem teste"
    sim = json.loads((ROOT / "resultados_teste44.json").read_text())
    res = {}; t0 = time.time(); okJ1 = okJ2 = okJ3 = 0
    teo_trav = {}
    for N in T44.NS:
        for b in T44.BETAS:
            dw, kc = T44.disco_beta(N, b); r_t, trav_n = [], []
            for k in KG:
                r, o, tr = resolver(dw, k * kc); r_t.append(r); trav_n.append(int(tr.sum()) if tr is not None else 0)
                if N == 12: teo_trav[(b, round(float(k), 3))] = tr
            r_t = np.array(r_t); trav_n = np.array(trav_n)
            jan = (trav_n >= N / 2) & (trav_n < N); larg = float(jan.sum() * PASSO)
            KL = float(KG[np.argmax(trav_n == N)]) if (trav_n == N).any() else None
            s = sim[f"N{N}_b{b:+.1f}"]; Kw = np.isin(KG, s["K"]); Cs = np.array(s["C_mediana"])
            mae = float(np.mean(np.abs(r_t[Kw] - Cs[Kw]))) if Kw.any() else None
            d = {"largura_teo": larg, "largura_sim": s["largura"], "K_teo": KG[jan].tolist(), "K_sim": s["K"],
                 "K_L_teo": KL, "K_L_sim": s["K_L"], "mae_C": mae, "r_teo": r_t.round(4).tolist(), "travados_teo": trav_n.tolist()}
            res[f"N{N}_b{b:+.1f}"] = d
            okJ1 += KL is not None and s["K_L"] is not None and abs(KL - s["K_L"]) <= 0.01 + 1e-9
            okJ2 += abs(larg - s["largura"]) <= 0.025 + 1e-9
            okJ3 += mae is not None and mae <= 0.05
            print(f"N {N:2d} β {b:+.1f}: largura teo {larg:.3f} sim {s['largura']:.3f} | janela teo {KG[jan].min() if jan.any() else '—'}–{KG[jan].max() if jan.any() else '—'} sim {s['K'][0] if s['K'] else '—'}–{s['K'][-1] if s['K'] else '—'} | K_L teo {KL} sim {s['K_L']} | EAM C {mae if mae is None else round(mae,3)}", flush=True)
    t_teo = time.time() - t0

    # quem desliza (N = 12): simulação coerente nos K da janela simulada
    acertos = tot = 0; detalhe = []
    for b in T44.BETAS:
        dw, kc = T44.disco_beta(12, b); Ks = np.array(sim[f"N12_b{b:+.1f}"]["K"])
        if len(Ks) == 0: continue
        th0 = np.tile(T44.SIG0 * np.random.default_rng(46).normal(size=12), (len(Ks), 1))
        _, _, Om, _ = T41.rodar(dw, Ks * kc, th0)
        for i, k in enumerate(Ks):
            om = Om[i]; cont = (np.abs(om[:, None] - om[None, :]) < 1e-4).sum(1); c = int(np.argmax(cont))
            desl_sim = set(np.flatnonzero(np.abs(om - om[c]) >= 1e-4).tolist())
            tr = teo_trav.get((b, round(float(k), 3)))
            desl_teo = set(np.flatnonzero(~tr).tolist()) if tr is not None else set(range(12))
            ok = desl_sim == desl_teo; acertos += ok; tot += 1
            detalhe.append({"beta": b, "K": float(k), "sim": sorted(desl_sim), "teo": sorted(desl_teo), "igual": bool(ok)})
    frac = acertos / tot if tot else 0.0
    res["quem_desliza"] = {"acertos": acertos, "total": tot, "fracao": frac, "detalhe": detalhe}
    res["tempo_teoria_s"] = t_teo
    res["J"] = {"J1": okJ1 >= 14, "J2": okJ2 >= 12, "J3": okJ3 >= 12, "J4": frac >= 0.8}
    res["contagens"] = {"J1": int(okJ1), "J2": int(okJ2), "J3": int(okJ3)}
    print(f"quem desliza: {acertos}/{tot} ({frac:.0%}) | tempo da teoria nas 15 combinações: {t_teo:.0f} s")
    print("contagens:", res["contagens"])
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste46.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
