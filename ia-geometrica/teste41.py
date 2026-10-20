"""Teste 41 (41-B/C/D: o atlas dos regimes em movimento). Disco de N anéis (Kuramoto, campo médio, mapa de passo 1 Myr),
sem memória e sem controlador. Para K/K_c de 0,90 a 1,12: média de C em quatro janelas de 4 Gyr, frequência efetiva de
cada anel e aglomerado travado, maior expoente de Lyapunov, espalhamento entre 21 condições iniciais; janela em N = 8–24.
Predição: PREDICAO_teste41_atlas_dos_regimes.md (commit 0748915), escrita antes deste arquivo.

    python ia-geometrica/teste41.py        # o teste (exige a predição)
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
M, V, KMS, SIG0, D = 5, 200.0, 1.0227e-3, 0.15, 2.5e-4
T, T0, NJ = 20000, 4000, 4
KG = np.round(np.arange(0.90, 1.12001, 0.005), 3)
FAIXA = (0.527, 0.727); TOL_W = 1e-4; LYAP_MIN = 5e-4


def disco(N):
    r = np.linspace(9.0, 14.0, N); w = M * (V / r) * KMS; dw = w - w.mean()
    return dw, 2 * (w.max() - w.min()) / np.pi


def rodar(dw, Ks, th0, ruido=None, lyap=False):
    """Ks: (B,), th0: (B, N). Devolve C̄ por janela (B, NJ), C̄ total, Ω efetivas (B, N) e λ_max (B,) se pedido."""
    th = th0.copy(); B, N = th.shape; Cw = np.zeros((B, NJ)); thA = None; lam = np.zeros(B)
    v = np.random.default_rng(0).normal(size=(B, N)); v -= v.mean(1, keepdims=True); v /= np.linalg.norm(v, axis=1, keepdims=True)
    unw = th.copy()
    L = (T - T0) // NJ
    for t in range(T):
        e = np.exp(1j * th); S = e.sum(1); Z = S / N; C = np.abs(Z); psi = np.angle(Z)
        if lyap:
            Sv = (e * v).sum(1)
            Jv = (Ks / N)[:, None] * (np.real(np.conj(e) * Sv[:, None]) - v * np.real(np.conj(e) * S[:, None]))
            v = v + Jv; v -= v.mean(1, keepdims=True); nv = np.linalg.norm(v, axis=1)
            if t >= T0: lam += np.log(nv)
            v /= nv[:, None]
        passo = dw + (Ks * C)[:, None] * np.sin(psi[:, None] - th)
        if ruido is not None: passo = passo + ruido.normal(size=th.shape) * np.sqrt(2 * D)
        th = th + passo; unw = unw + passo
        if t == T0 - 1: thA = unw.copy()
        if t >= T0: Cw[:, (t - T0) // L] += np.abs(np.exp(1j * th).mean(1))
    Cw /= L; Om = (unw - thA) / (T - T0)
    return Cw, Cw.mean(1), Om, lam / (T - T0)


def aglomerado(om):
    cont = (np.abs(om[:, None] - om[None, :]) < TOL_W).sum(1); i = int(np.argmax(cont))
    membros = np.abs(om - om[i]) < TOL_W
    return int(membros.sum()), int((~membros).sum())


def main():
    assert (ROOT / "PREDICAO_teste41_atlas_dos_regimes.md").exists(), "sem predição, sem teste"
    rng = np.random.default_rng(41); res = {"K_grade": KG.tolist()}
    N = 12; dw, kc = disco(N); nK = len(KG)
    th_c = SIG0 * rng.normal(size=N); sort = rng.uniform(0, 2 * np.pi, (20, N))
    th0 = np.vstack([np.tile(th_c, (nK, 1))] + [np.tile(s, (nK, 1)) for s in sort])
    Ks = np.tile(KG * kc, 21)
    Cw, Cb, Om, _ = rodar(dw, Ks, th0)
    _, _, _, lam = rodar(dw, KG * kc, np.tile(th_c, (nK, 1)), lyap=True)
    Cb = Cb.reshape(21, nK); Cw = Cw.reshape(21, nK, NJ); Om = Om.reshape(21, nK, N)
    Cc = Cb[0]; jan = (Cc >= FAIXA[0]) & (Cc <= FAIXA[1]); iw = np.flatnonzero(jan)
    deriva = Cw[0].max(1) - Cw[0].min(1); espal = Cb.max(0) - Cb.min(0)
    agl = [aglomerado(Om[0, k]) for k in range(nK)]
    res["N12"] = {"K_c_mrad": kc * 1e3, "C_coerente": Cc.round(4).tolist(), "C_sorteadas_min_max": [Cb.min(0).round(4).tolist(), Cb.max(0).round(4).tolist()],
                  "deriva": deriva.round(4).tolist(), "espalhamento": espal.round(4).tolist(), "lyap": lam.tolist(),
                  "aglomerado_e_escorregando": agl, "Omega_coerente": (Om[0] * 1e3).round(3).tolist(),
                  "janela_K": KG[jan].tolist()}
    J1 = np.mean(deriva[iw] <= 0.02) >= 0.8 if len(iw) else False
    J2 = np.mean([agl[k][0] >= 6 and agl[k][1] >= 1 for k in iw]) >= 0.8 if len(iw) else False
    J3 = np.mean(lam[iw] > LYAP_MIN) >= 0.5 if len(iw) else False
    J4 = np.mean(espal[iw] <= 0.03) >= 0.8 if len(iw) else False

    largura = {}
    for n in (8, 12, 16, 24):
        dwn, kcn = disco(n); r2 = np.random.default_rng(410 + n); thn = SIG0 * r2.normal(size=n)
        _, cbn, _, _ = rodar(dwn, KG * kcn, np.tile(thn, (nK, 1)))
        jn = (cbn >= FAIXA[0]) & (cbn <= FAIXA[1]); largura[n] = {"largura": float(jn.sum() * 0.005), "K": KG[jn].tolist(), "C": cbn.round(4).tolist()}
    ws = [largura[n]["largura"] for n in (8, 12, 16, 24)]
    J5 = all(ws[i] > ws[i + 1] for i in range(3))
    res["robustez_N"] = largura
    cr = np.mean([rodar(dw, KG * kc, np.tile(SIG0 * np.random.default_rng(4100 + s).normal(size=N), (nK, 1)), ruido=np.random.default_rng(4200 + s))[1] for s in range(5)], axis=0)
    jr = (cr >= FAIXA[0]) & (cr <= FAIXA[1])
    res["com_ruido"] = {"C": cr.round(4).tolist(), "largura": float(jr.sum() * 0.005), "K": KG[jr].tolist()}
    res["J"] = {"J1": bool(J1), "J2": bool(J2), "J3": bool(J3), "J4": bool(J4), "J5": bool(J5)}
    res["resumo_janela"] = {"n_K": int(len(iw)), "frac_deriva_ok": float(np.mean(deriva[iw] <= 0.02)) if len(iw) else None,
                            "frac_aglomerado_ok": float(np.mean([agl[k][0] >= 6 and agl[k][1] >= 1 for k in iw])) if len(iw) else None,
                            "frac_caos": float(np.mean(lam[iw] > LYAP_MIN)) if len(iw) else None,
                            "frac_espalhamento_ok": float(np.mean(espal[iw] <= 0.03)) if len(iw) else None}

    print(f"N = 12, K_c = {kc*1e3:.2f} mrad/Myr; janela {KG[jan].min() if len(iw) else '—'}–{KG[jan].max() if len(iw) else '—'} ({len(iw)} pontos)")
    for k in range(nK):
        print(f"  K/K_c {KG[k]:.3f}: C̄ {Cc[k]:.3f} [{Cb.min(0)[k]:.3f}; {Cb.max(0)[k]:.3f}] deriva {deriva[k]:.3f} | aglomerado {agl[k][0]:2d}, escorregam {agl[k][1]:2d} | λ {lam[k]:+.2e}{' ← janela' if jan[k] else ''}")
    print("resumo da janela:", res["resumo_janela"])
    print("larguras por N:", {n: largura[n]["largura"] for n in largura}, "| com ruído (N=12):", res["com_ruido"]["largura"])
    print("== " + " | ".join(f"{k} {'PASSA' if v else 'REPROVA'}" for k, v in res["J"].items()))
    (ROOT / "resultados_teste41.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
