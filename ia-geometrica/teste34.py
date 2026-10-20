"""Teste 34 (a régua da organização): duas réguas para medir se um corpo segura o ciclo anual acima da sua sombra passiva.
Régua A, da sombra (ajustada, nominal, exata); régua B, do silêncio (o mundo perde as estações e mede-se o que fica).
Corpo: andar 3 da v0 sobre o campo do Cérebro de Juara; positivos com 𝒢 interno conhecido, negativos sem padrão guardado.
Predição: PREDICAO_teste34_regua_da_organizacao.md (commit 8e4d4fe), escrita antes deste arquivo.

    python ia-geometrica/teste34.py        # o teste (exige a predição)
"""
import csv, gzip, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import teste30 as T30

ROOT = Path(__file__).resolve().parent
NMUNDOS, SEMENTE = 100, 34
LAM = 0.15 / 10 ** np.arange(4)            # λ dos quatro andares da v0
L3 = LAM[2]                                # o corpo medido é o andar 3
OMEGA = 2 * np.pi / 365.25; P0 = 1e3
GAMAS = [0.05, 0.10, 0.25, 0.50, 1.00]
NEG = ["N0 v0 pura", "N1 ruído vermelho", "N2 memória mais curta", "N3 esquecimento não linear"]


# ---------------------------------------------------------------- o campo do cubo (como clima/cubo_juara.py)
def campo():
    D, ano, doy, P, E, s0, s3 = T30.ler_diario()
    vpd = {}
    with gzip.open(T30.DADOS, "rt") as f:
        r = csv.reader(f); h = next(r); iv = h.index("vapour_pressure_deficit")
        for row in r: vpd.setdefault(row[0][:10], []).append(float(row[iv]))
    vp = np.array([np.mean(vpd[d]) for d in D]); bal = np.convolve(P - E, np.ones(7) / 7)[:len(P)]
    cal = ano <= 2017; z = lambda v: (v - v[cal].mean()) / v[cal].std()
    return np.asarray(ano), np.asarray(doy), np.column_stack([z(s3), z(bal), z(vp)])


def mundo(ano, doy, x, perm, silencio):
    """História de 16 anos na ordem `perm`; com silêncio, os anos 9–16 viram x − climatologia dos anos 1–8."""
    blocos = [np.flatnonzero(ano == 2010 + k) for k in perm]
    idx = np.concatenate(blocos); pos = np.concatenate([np.full(len(b), i) for i, b in enumerate(blocos)])
    xw, dw = x[idx].copy(), doy[idx]
    if silencio:
        cal, med = pos <= 7, pos >= 8
        for a in range(3):
            m, _ = T30.climatologia(xw[:, a], dw, cal); xw[med, a] -= m[med]
    return xw, pos


# ---------------------------------------------------------------- a cascada, vetorizada nos mundos (W, N, 3)
def andar(u, lam):
    r = np.zeros_like(u); s = np.zeros((u.shape[0], u.shape[2]))
    for t in range(u.shape[1]):
        s = s + lam * (u[:, t] - s); r[:, t] = s
    return r


def ritmo(u):
    """⋄ por mundo e eixo: mínimos quadrados recursivos sem esquecimento (base 1, sen/cos 1 e 2 ciclos/ano), fria.
    Devolve ĉ(t), a parte periódica prevista antes de aprender o dia t."""
    W, N, A = u.shape; beta = np.zeros((W, A, 5)); Pm = np.broadcast_to(P0 * np.eye(5), (W, A, 5, 5)).copy()
    c = np.zeros_like(u)
    for t in range(N):
        f = np.array([1.0, np.sin(OMEGA * t), np.cos(OMEGA * t), np.sin(2 * OMEGA * t), np.cos(2 * OMEGA * t)])
        c[:, t] = beta[..., 1:] @ f[1:]
        e = u[:, t] - beta @ f; Pf = Pm @ f; k = Pf / (1.0 + Pf @ f)[..., None]
        beta = beta + k * e[..., None]; Pm = Pm - k[..., :, None] * Pf[..., None, :]
    return c


def corpo(u, lam, extra=None, nl_kappa=None):
    """Andar 3: r ← r + λ_t (u − r) + λ₃·extra(t). nl_kappa: λ_t = λ₃·clip(|u − r|/κ, 0,25; 4)."""
    r = np.zeros_like(u); s = np.zeros((u.shape[0], u.shape[2]))
    for t in range(u.shape[1]):
        d = u[:, t] - s
        lt = lam if nl_kappa is None else L3 * np.clip(np.abs(d) / nl_kappa, 0.25, 4.0)
        s = s + lt * d + (0.0 if extra is None else L3 * extra[:, t]); r[:, t] = s
    return r


def sombra(u, r, lam, i0):
    """Registro passivo de 1ª ordem, λ por mundo (W,), começando no valor do corpo no dia i0 de cada mundo (W,)."""
    W, N, A = r.shape; lam = np.asarray(lam, float).reshape(W, 1) * np.ones((W, 1)); out = np.zeros_like(r); s = np.zeros((W, A))
    for t in range(N):
        s = np.where((t == i0)[:, None], r[:, t], np.where((t > i0)[:, None], s + lam * (u[:, t] - s), s)); out[:, t] = s
    return out


def lambda_ajustado(u, r, cal):
    """λ̂ por mínimos quadrados de r(t) − r(t−1) contra u(t) − r(t−1), dias de calibração, eixos juntos."""
    ii = np.flatnonzero(cal); ii = ii[ii > 0]
    y = r[:, ii] - r[:, ii - 1]; z = u[:, ii] - r[:, ii - 1]
    return (y * z).sum(axis=(1, 2)) / (z * z).sum(axis=(1, 2))


# ---------------------------------------------------------------- harmônico anual
def harm(v, dias):
    """Coeficientes (cos, sen) do harmônico anual com nível e tendência, ajustados sobre `dias`. v: (W, N, 3) → (W, 3, 2)."""
    t = dias.astype(float); M = np.column_stack([np.ones_like(t), (t - t.mean()) / 365.25, np.cos(OMEGA * t), np.sin(OMEGA * t)])
    B = np.linalg.pinv(M) @ v[:, dias]                  # (W, 4, 3)
    return np.transpose(B[:, 2:4], (0, 2, 1))


def theta(r, s, pos):
    """Θ = log₂ Σ|Z_corpo|² / Σ|Z_sombra|², harmônico por ano nos 8 anos de medida. Também C_φ médio nos eixos."""
    pr = ps = 0.0; fr, fs = [], []
    for k in range(8, 16):
        dias = np.flatnonzero(pos == k); zr, zs = harm(r, dias), harm(s, dias)
        pr = pr + (zr ** 2).sum(axis=(1, 2)); ps = ps + (zs ** 2).sum(axis=(1, 2))
        fr.append(np.arctan2(zr[..., 1], zr[..., 0])); fs.append(np.arctan2(zs[..., 1], zs[..., 0]))
    C = lambda F: np.abs(np.mean(np.exp(1j * np.array(F)), axis=0)).mean(axis=1)
    return np.log2(pr / ps), C(fr) - C(fs)


def retencao(r, pos):
    """R = |Z anos 10–16| / |Z anos 2–8|, harmônico anual ajustado de uma vez em cada bloco, eixos em quadratura."""
    zm = harm(r, np.flatnonzero((pos >= 9) & (pos <= 15))); zc = harm(r, np.flatnonzero((pos >= 1) & (pos <= 7)))
    return np.sqrt((zm ** 2).sum(axis=(1, 2)) / (zc ** 2).sum(axis=(1, 2)))


# ---------------------------------------------------------------- uma variante (com estações ou com silêncio)
def rodar_variante(ano, doy, x, perms, silencio, semente_ruido):
    # anos têm 365 ou 366 dias; para vetorizar, cada mundo é rodado com o seu próprio comprimento cortado ao menor
    mundos = [mundo(ano, doy, x, p, silencio) for p in perms]
    N = min(len(m[0]) for m in mundos)
    X = np.stack([m[0][:N] for m in mundos]); POS = np.stack([m[1][:N] for m in mundos])
    u = andar(andar(X, LAM[0]), LAM[1])                                 # entrada do andar 3
    c = ritmo(u)
    cal = POS <= 7
    corpos = {}
    corpos["N0 v0 pura"] = corpo(u, L3)
    # N1: AR(1) τ = 180 d, desvio casado ao de 0,25·ĉ na calibração do mesmo mundo
    rng = np.random.default_rng(semente_ruido); phi = 1 - 1 / 180
    e = rng.normal(0, 1, u.shape) * np.sqrt(1 - phi ** 2); xi = np.zeros_like(u); xi[:, 0] = rng.normal(0, 1, (u.shape[0], 3))
    for t in range(1, u.shape[1]): xi[:, t] = phi * xi[:, t - 1] + e[:, t]
    alvo = np.stack([(0.25 * c[w][cal[w]]).std(axis=0) for w in range(len(perms))])
    corpos["N1 ruído vermelho"] = corpo(u, L3, extra=xi * alvo[:, None, :])
    corpos["N2 memória mais curta"] = corpo(u, 1.5 * L3)
    kap = np.stack([np.abs(u[w][cal[w]] - corpos["N0 v0 pura"][w][cal[w]]).mean(axis=0) for w in range(len(perms))])
    corpos["N3 esquecimento não linear"] = corpo(u, L3, nl_kappa=kap)
    for g in GAMAS:
        corpos[f"P({g:.2f})"] = corpo(u, L3, extra=g * c)
    return u, c, POS, corpos


def main():
    assert (ROOT / "PREDICAO_teste34_regua_da_organizacao.md").exists(), "sem predição, sem teste"
    ano, doy, x = campo()
    rng = np.random.default_rng(SEMENTE); perms = [rng.permutation(16) for _ in range(NMUNDOS)]
    res = {"mundos": NMUNDOS, "semente": SEMENTE, "gamas": GAMAS}

    # ---------------- régua A: com estações
    u, c, POS, corpos = rodar_variante(ano, doy, x, perms, False, SEMENTE + 1)
    W = NMUNDOS; i0 = np.array([np.flatnonzero(POS[w] == 8)[0] for w in range(W)])
    A = {}
    exato_ref = corpos["N0 v0 pura"]
    for nome, r in corpos.items():
        lh = np.array([lambda_ajustado(u[w:w + 1], r[w:w + 1], POS[w] <= 7)[0] for w in range(W)])
        s_aj = sombra(u, r, lh, i0); s_nom = sombra(u, r, np.full(W, L3), i0)
        th_aj, th_nom, th_ex, dC = [], [], [], []
        for w in range(W):
            rw = r[w:w + 1]
            t1, d1 = theta(rw, s_aj[w:w + 1], POS[w]); t2, _ = theta(rw, s_nom[w:w + 1], POS[w])
            th_aj.append(float(t1[0])); th_nom.append(float(t2[0])); dC.append(float(d1[0]))
            th_ex.append(0.0 if nome in NEG else float(theta(rw, exato_ref[w:w + 1], POS[w])[0][0]))
        A[nome] = {"theta_ajustada": th_aj, "theta_nominal": th_nom, "theta_exato": th_ex, "dC_phi_ajustada": dC,
                   "lambda_ajustado_sobre_l3": (lh / L3).tolist()}
    del corpos

    # ---------------- régua B: silêncio nos anos 9–16
    u2, c2, POS2, corpos2 = rodar_variante(ano, doy, x, perms, True, SEMENTE + 1)
    B = {nome: [float(retencao(r[w:w + 1], POS2[w])[0]) for w in range(W)] for nome, r in corpos2.items()}
    del corpos2

    # ---------------- limiares, pisos, julgamentos
    q95 = lambda v: float(np.quantile(v, 0.95))
    negA = np.concatenate([A[n]["theta_ajustada"] for n in NEG]); thA = q95(negA)
    negB = np.concatenate([B[n] for n in NEG]); thB = q95(negB)
    negN = np.concatenate([A[n]["theta_nominal"] for n in NEG[:2]]); thN = q95(negN)

    def piso(det):
        ok = [det[g] >= 90 for g in GAMAS]
        for i, g in enumerate(GAMAS):
            if all(ok[i:]): return g
        return None

    detA = {g: int(np.sum(np.array(A[f"P({g:.2f})"]["theta_ajustada"]) > thA)) for g in GAMAS}
    detB = {g: int(np.sum(np.array(B[f"P({g:.2f})"]) > thB)) for g in GAMAS}
    detN = {g: int(np.sum(np.array(A[f"P({g:.2f})"]["theta_nominal"]) > thN)) for g in GAMAS}
    pA, pB, pN = piso(detA), piso(detB), piso(detN)
    res["limiares"] = {"theta_A_ajustada_q95_neg": thA, "R_B_q95_neg": thB, "theta_nominal_q95_N0_N1": thN}
    res["deteccoes_em_100"] = {"A_ajustada": detA, "B_silencio": detB, "A_nominal": detN}
    res["pisos"] = {"A_ajustada": pA, "B_silencio": pB, "A_nominal": pN}
    res["J1"] = {"piso_B": pB, "passa": bool(pB is not None and pB <= 0.50)}
    res["J2"] = {"piso_A_ajustada": pA, "passa": bool(pA is not None and pA <= 0.50)}
    res["falso_positivo_nominal"] = {n: int(np.sum(np.array(A[n]["theta_nominal"]) > thN)) for n in NEG[2:]}
    med = lambda v: float(np.median(v))
    res["mediana_razao_aj_exato"] = {g: med(np.array(A[f"P({g:.2f})"]["theta_ajustada"]) / np.array(A[f"P({g:.2f})"]["theta_exato"])) for g in GAMAS}
    res["resumo"] = {n: {"theta_aj_med": med(A[n]["theta_ajustada"]), "theta_aj_q05_q95": [float(np.quantile(A[n]["theta_ajustada"], .05)), q95(A[n]["theta_ajustada"])],
                         "theta_nom_med": med(A[n]["theta_nominal"]), "theta_exato_med": med(A[n]["theta_exato"]),
                         "dC_phi_med": med(A[n]["dC_phi_ajustada"]), "lambda_aj_sobre_l3_med": med(A[n]["lambda_ajustado_sobre_l3"]),
                         "R_med": med(B[n]), "R_q05_q95": [float(np.quantile(B[n], .05)), q95(B[n])]} for n in A}
    rz = res["mediana_razao_aj_exato"][0.25]
    res["apostas"] = {"razao_025_entre_005_e_035": bool(0.05 <= rz <= 0.35),
                      "N2_nominal_ge90": bool(res["falso_positivo_nominal"]["N2 memória mais curta"] >= 90),
                      "N3_nominal_ge50": bool(res["falso_positivo_nominal"]["N3 esquecimento não linear"] >= 50)}

    for n, o in res["resumo"].items():
        print(f"{n:28s} Θaj {o['theta_aj_med']:+.3f} [{o['theta_aj_q05_q95'][0]:+.3f};{o['theta_aj_q05_q95'][1]:+.3f}]  Θnom {o['theta_nom_med']:+.3f}"
              f"  Θexato {o['theta_exato_med']:+.3f}  λ̂/λ₃ {o['lambda_aj_sobre_l3_med']:.3f}  ΔCφ {o['dC_phi_med']:+.3f}"
              f"  R {o['R_med']:.3f} [{o['R_q05_q95'][0]:.3f};{o['R_q05_q95'][1]:.3f}]")
    print("limiares", {k: round(v, 4) for k, v in res["limiares"].items()})
    print("detecções", res["deteccoes_em_100"]); print("pisos", res["pisos"])
    print("falso positivo nominal", res["falso_positivo_nominal"], "| razão aj/exato", {g: round(v, 3) for g, v in res["mediana_razao_aj_exato"].items()})
    print(f"== J1 piso B {pB} → {'PASSA' if res['J1']['passa'] else 'REPROVA'} | J2 piso A ajustada {pA} → {'PASSA' if res['J2']['passa'] else 'REPROVA'}"
          f" | apostas {res['apostas']}")
    (ROOT / "resultados_teste34.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
