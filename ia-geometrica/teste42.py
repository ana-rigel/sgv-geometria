"""Teste 42 (42-A: a memória das interações e a largura da janela). Mapa do teste 41 com a memória do colaborador:
θ ← θ + Δω + K[(1 − α)S + αq], q ← q + (S − q)/τ, S = C sen(ψ − θ). Malha α × τ escolhida em condições de seleção e julgada
em condições de validação; larguras da faixa, da sincronização parcial e K_L; escala em N; controle com frequências uniformes.
Predição: PREDICAO_teste42_memoria_na_janela.md (commit 4b08c98), escrita antes deste arquivo.

    python ia-geometrica/teste42.py        # o teste (exige a predição)
"""
import json, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
M, V, KMS, SIG0 = 5, 200.0, 1.0227e-3, 0.15
T, T0, NJ = 20000, 4000, 4
KG = np.round(np.arange(0.90, 1.20001, 0.005), 3)
ALFAS, TAUS = [0.25, 0.5, 0.75, 1.0], [30.0, 100.0, 300.0, 1000.0]
FAIXA, TOL_W, PASSO = (0.527, 0.727), 1e-4, 0.005


def disco(N, uniforme=False):
    r = np.linspace(9.0, 14.0, N); w = M * (V / r) * KMS; dw = w - w.mean()
    kc = 2 * (w.max() - w.min()) / np.pi
    if uniforme:
        r12 = np.linspace(9.0, 14.0, 12); w12 = M * (V / r12) * KMS; d12 = w12 - w12.mean()
        dw = np.linspace(d12.max(), d12.min(), N); dw = dw - dw.mean(); kc = 2 * (dw.max() - dw.min()) / np.pi
    return dw, kc


def rodar(dw, Ks, al, ta, th0, Tt=T, lyap=False):
    th = th0.copy(); B, N = th.shape
    e = np.exp(1j * th); Z = e.mean(1); q = np.imag(np.conj(e) * Z[:, None]); unw = th.copy(); thA = None
    L = (Tt - T0) // NJ; Cw = np.zeros((B, NJ)); lam = np.zeros(B); lam_meio = None
    if lyap:
        g = np.random.default_rng(0); vt = g.normal(size=(B, N)); vq = g.normal(size=(B, N))
        vt -= vt.mean(1, keepdims=True); nrm = np.sqrt((vt ** 2).sum(1) + (vq ** 2).sum(1)); vt /= nrm[:, None]; vq /= nrm[:, None]
    Kc, a, tc = Ks[:, None], al[:, None], ta[:, None]
    for t in range(Tt):
        e = np.exp(1j * th); Ssum = e.sum(1); Z = Ssum / N
        S = np.imag(np.conj(e) * Z[:, None])
        if lyap:
            dS = (np.real(np.conj(e) * (e * vt).sum(1)[:, None]) - vt * np.real(np.conj(e) * Ssum[:, None])) / N
            vt2 = vt + Kc * ((1 - a) * dS + a * vq); vq = vq + (dS - vq) / tc; vt = vt2 - vt2.mean(1, keepdims=True)
            nrm = np.sqrt((vt ** 2).sum(1) + (vq ** 2).sum(1))
            if t >= T0: lam += np.log(nrm)
            vt /= nrm[:, None]; vq /= nrm[:, None]
            if t == T0 + (Tt - T0) // 2 - 1: lam_meio = lam / ((Tt - T0) // 2)
        passo = dw + Kc * ((1 - a) * S + a * q)
        q = q + (S - q) / tc
        th = th + passo; unw = unw + passo
        if t == T0 - 1: thA = unw.copy()
        if t >= T0: Cw[:, (t - T0) // L] += np.abs(np.exp(1j * th).mean(1))
    Cw /= L; Om = (unw - thA) / (Tt - T0)
    cont = (np.abs(Om[:, :, None] - Om[:, None, :]) < TOL_W).sum(2); agl = cont.max(1)
    out = {"Cb": Cw.mean(1), "deriva": Cw.max(1) - Cw.min(1), "agl": agl, "esc": N - agl}
    if lyap: out["lam"] = lam / (Tt - T0); out["lam_meio"] = lam_meio
    return out


def grade(dw, kc, alfa, tau, ths):
    """ths: (nIC, N). Devolve arrays (nIC, nK)."""
    nK, nI, N = len(KG), len(ths), ths.shape[1]
    th0 = np.repeat(ths, nK, axis=0); Ks = np.tile(KG * kc, nI)
    o = rodar(dw, Ks, np.full(nI * nK, alfa), np.full(nI * nK, tau), th0)
    return {k: v.reshape(nI, nK) for k, v in o.items()}


def larguras(o, N):
    medC = np.median(o["Cb"], 0); medD = np.median(o["deriva"], 0)
    faixa = (medC >= FAIXA[0]) & (medC <= FAIXA[1]) & (medD <= 0.02)
    parcial = np.mean((o["agl"] >= 6) & (o["esc"] >= 1), 0) > 0.5
    trav = np.all(o["agl"] == N, 0); KL = float(KG[np.argmax(trav)]) if trav.any() else None
    inc = None
    if faixa.sum() >= 3: inc = float(np.polyfit(KG[faixa], medC[faixa], 1)[0])
    return {"faixa": float(faixa.sum() * PASSO), "faixa_K": KG[faixa].tolist(), "parcial": float(parcial.sum() * PASSO),
            "K_L": KL, "inclinacao": inc, "_mask": faixa, "medC": medC.round(4).tolist()}


def main():
    assert (ROOT / "PREDICAO_teste42_memoria_na_janela.md").exists(), "sem predição, sem teste"
    t0 = time.time(); N = 12; dw, kc = disco(N)
    sel = SIG0 * np.random.default_rng(420).normal(size=(10, N)); val = SIG0 * np.random.default_rng(421).normal(size=(10, N))
    celulas = [(0.0, 1.0)] + [(a, t) for a in ALFAS for t in TAUS]
    tab = {}
    for a, t in celulas:
        w = larguras(grade(dw, kc, a, t, sel), N); w.pop("_mask"); tab[f"{a}_{t:g}"] = w
        print(f"seleção α {a} τ {t:g}: faixa {w['faixa']:.3f} {w['faixa_K'][:1]}…{w['faixa_K'][-1:]} | parcial {w['parcial']:.3f} | K_L {w['K_L']} | incl {w['inclinacao']}", flush=True)
    cand = [(tab[f"{a}_{t:g}"]["faixa"], -a, -t, a, t) for a, t in celulas[1:]]
    best = max(cand); ab, tb = best[3], best[4]
    print(f"célula escolhida: α {ab} τ {tb:g}  ({time.time()-t0:.0f} s)", flush=True)

    o0 = grade(dw, kc, 0.0, 1.0, val); ob = grade(dw, kc, ab, tb, val)
    w0, wb = larguras(o0, N), larguras(ob, N)
    j1 = bool(w0["faixa_K"] and 0.965 <= w0["faixa_K"][0] <= 0.975 and 1.030 <= w0["faixa_K"][-1] <= 1.040)
    j2 = bool(w0["faixa"] > 0 and wb["faixa"] >= 1.5 * w0["faixa"])
    mb = wb["_mask"]; espal = ob["Cb"].max(0) - ob["Cb"].min(0)
    j3 = bool(mb.any() and np.mean(espal[mb] <= 0.03) >= 0.8)
    j5 = bool(mb.any() and np.mean((np.median(ob["agl"], 0)[mb] >= 6) & (np.median(ob["esc"], 0)[mb] >= 1)) >= 0.8)

    escala = {}
    for n in (16, 24):
        dwn, kcn = disco(n); vn = SIG0 * np.random.default_rng(421 + n).normal(size=(5, n))
        a0 = larguras(grade(dwn, kcn, 0.0, 1.0, vn), n); ab_ = larguras(grade(dwn, kcn, ab, tb, vn), n)
        razao = ab_["faixa"] / a0["faixa"] if a0["faixa"] > 0 else (np.inf if ab_["faixa"] > 0 else 0.0)
        escala[n] = {"alfa0": a0["faixa"], "celula": ab_["faixa"], "razao": float(razao), "K_L_alfa0": a0["K_L"], "K_L_celula": ab_["K_L"]}
        print(f"N {n}: faixa α=0 {a0['faixa']:.3f} | célula {ab_['faixa']:.3f} | razão {razao:.2f}", flush=True)
    j4 = all(escala[n]["razao"] >= 1.5 for n in (16, 24))

    unif = {}
    for n in (12, 16, 24, 48):
        dwu, kcu = disco(n, uniforme=True); vu = SIG0 * np.random.default_rng(4200 + n).normal(size=(5, n))
        wu = larguras(grade(dwu, kcu, 0.0, 1.0, vu), n); unif[n] = {"parcial": wu["parcial"], "faixa": wu["faixa"], "K_L": wu["K_L"]}
        print(f"uniforme N {n}: parcial {wu['parcial']:.3f} | faixa {wu['faixa']:.3f} | K_L {wu['K_L']}", flush=True)
    pu = [unif[n]["parcial"] for n in (12, 16, 24, 48)]; j6 = all(pu[i] > pu[i + 1] for i in range(3))

    lyap = {}
    for nome, (a, t) in {"alfa0": (0.0, 1.0), "celula": (ab, tb)}.items():
        thc = np.tile(SIG0 * np.random.default_rng(422).normal(size=N), (len(KG), 1))
        o = rodar(dw, KG * kc, np.full(len(KG), a), np.full(len(KG), t), thc, Tt=T0 + 40000, lyap=True)
        lyap[nome] = {"lam_20Gyr": o["lam_meio"].tolist(), "lam_40Gyr": o["lam"].tolist()}

    for nome, w in (("alfa0", w0), ("celula", wb)): w.pop("_mask")
    res = {"celula": {"alfa": ab, "tau": tb}, "selecao": tab, "validacao": {"alfa0": w0, "celula": wb},
           "espalhamento_janela_celula": espal[mb].round(4).tolist(), "escala": escala, "uniforme": unif, "lyapunov": lyap,
           "aposta_mecanismo": bool(tb >= 100 and ab >= 0.5 and wb["K_L"] is not None and w0["K_L"] is not None and wb["K_L"] > w0["K_L"]),
           "J": {"J1": j1, "J2": j2, "J3": j3, "J4": bool(j4), "J5": j5, "J6": bool(j6)}}
    print(f"validação: α=0 faixa {w0['faixa']:.3f} {w0['faixa_K'][:1]}…{w0['faixa_K'][-1:]} K_L {w0['K_L']} incl {w0['inclinacao']} | "
          f"célula faixa {wb['faixa']:.3f} {wb['faixa_K'][:1]}…{wb['faixa_K'][-1:]} parcial {wb['parcial']:.3f} K_L {wb['K_L']} incl {wb['inclinacao']}")
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()) + f" | aposta mecanismo {res['aposta_mecanismo']} | {time.time()-t0:.0f} s")
    (ROOT / "resultados_teste42.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
