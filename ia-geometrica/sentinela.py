"""A sentinela v0 (teste 54): a v0 instalada a frio, que decide sozinha quando aprendeu um ritmo e para de ouvir o campo.

Tudo é causal: no dia t ela só usa o que já viu até t. Nada vem do futuro, nem a normalização.

1. Normalização online: média e variância acumuladas de cada sensor (Welford); z_t usa só o passado.
2. Cascata da v0 intacta (λ₁ = 0,15, b = 10, k = 4) sobre z.
3. Projeção online: autovetor principal da covariância acumulada do andar 1 (sinal fixado pelo 1º sensor positivo);
   s_j = R_j · u / √λ_max.
4. Relógios do teste 52, braço A (K = 0): φ_j ← φ_j + ω_j − ε s_j sen φ_j; ω_j ← ω_j − η_w s_j sen φ_j, η_w = ε/365.
5. Declaração por andar (nova):
   - Z_j = EMA de s_j e^{−iφ_j} (o que o relógio ouve na própria fase), janela τ_j = 3 períodos próprios naturais;
   - Z_jk = o mesmo, em quatro demoduladores livres a c_k·ω_j (c_k = 0,5; 0,7; 1,4; 2,0): a régua do próprio andar;
   - Q_j = |Z_j| / √(média_k |Z_jk|²);
   - régua sequencial: sem ritmo, Z_j e os Z_jk são ruído do mesmo tamanho e Q_j² segue F(2, 8), com cauda
     P(Q² > x) = (1 + x/4)^−4. Quem já viveu n_j = t/τ_j janelas paga por ter olhado n_j vezes:
     q*_j(t)² = 4[(α/n_j)^−1/4 − 1], α = 0,01 (Bonferroni pelas janelas vividas; α escolhido no piloto sintético,
     onde a cauda real ficou ≈ 4–5 vezes mais pesada que a da F(2, 8));
   - o andar declara "aprendi um ritmo" quando, já maduro (t ≥ τ_j), Q_j ≥ q*_j(t) e ω_j variou ≤ 5 % em um período
     próprio, as duas coisas sem interrupção durante um período próprio inteiro.
   - Ao declarar, o andar para de ouvir o campo (s_j = 0 no relógio): é o segundo tempo do teste 53.
6. A fase esperada da entrada das águas, ψ (laço do relógio v1, η = 0,3), começa na 1ª entrada vivida e é corrigida a cada
   entrada; a previsão em 1/09 é t₀ + emb(ψ − φ₂(t₀))/ω₂(t₀).
"""
import numpy as np

OM = 2 * np.pi / 365.25
LAM = 0.15 * 10.0 ** -np.arange(4)
EPS = 0.01
ETAW = EPS / 365
C_OFF = np.array([0.5, 0.7, 1.4, 2.0])
TAU = 3 * 2 * np.pi / LAM                 # 126 d, 1.257 d (3,4 anos), 34 anos, 344 anos
DW = 0.05
ALFA = 0.01
ETA_PSI = 0.3
emb = lambda x: (x + np.pi) % (2 * np.pi) - np.pi


def normalizar_online(X):
    """X (T, d) bruto -> z (T, d) com média e desvio acumulados até t − 1 (z = 0 nos dois primeiros dias)."""
    T, d = X.shape; z = np.zeros_like(X, dtype=float); m = np.zeros(d); M2 = np.zeros(d)
    for i in range(T):
        if i >= 2:
            sd = np.sqrt(M2 / (i - 1)); z[i] = np.divide(X[i] - m, sd, out=np.zeros(d), where=sd > 0)
        dlt = X[i] - m; m = m + dlt / (i + 1); M2 = M2 + dlt * (X[i] - m)
    return z


def cascata(z):
    T, d = z.shape; R = np.zeros((4, T, d)); r = np.zeros((4, d))
    for i in range(T):
        r[0] += LAM[0] * (z[i] - r[0])
        for j in range(1, 4): r[j] += LAM[j] * (r[j - 1] - r[j])
        R[:, i] = r
    return R


def projetar_online(R, inicio=30):
    """s (4, T): projeção de cada andar no autovetor principal da covariância acumulada do andar 1 até t."""
    _, T, d = R.shape; s = np.zeros((4, T)); S1 = np.zeros(d); S2 = np.zeros((d, d))
    for i in range(T):
        x = R[0, i]; S1 += x; S2 += np.outer(x, x)
        if i + 1 < inicio: continue
        n = i + 1; C = S2 / n - np.outer(S1 / n, S1 / n)
        lv, V = np.linalg.eigh(C); u = V[:, -1]; u = u if u[0] >= 0 else -u
        if lv[-1] > 0: s[:, i] = R[:, i] @ u / np.sqrt(lv[-1])
    return s


def limiar(i, alfa):
    """q*_j(t) por andar, (len(alfa), 4)."""
    n = np.maximum(1.0, (i + 1) / TAU)
    p = np.asarray(alfa, float)[:, None] / n
    return np.sqrt(4 * (p ** -0.25 - 1))


def sentinela(s, ph0, qs=(ALFA,), aprende=True, guardar_fase=1):
    """s (4, T); ph0 (nIC,); qs: valores de α a rodar juntos (a régua sequencial de cada um).
    Devolve: dia da declaração por (q, início, andar) (−1 = nunca), fase e ω do andar `guardar_fase` por dia (T, q, nIC),
    ω no fim (q, nIC, 4) e Q por dia do andar `guardar_fase` (mediana dos inícios) para o relato."""
    qs = np.asarray(qs, float); nq, nic, T = len(qs), len(ph0), s.shape[1]
    sh = (nq, nic, 4)
    ph = np.broadcast_to(ph0[None, :, None], sh).copy(); w = np.broadcast_to(LAM, sh).copy()
    th = np.broadcast_to(ph[..., None], sh + (len(C_OFF),)).copy()
    Z = np.zeros(sh, complex); Zo = np.zeros(sh + (len(C_OFF),), complex)
    cnt = np.zeros(sh, int); decl = np.full(sh, -1); a = 1.0 / TAU
    WH = np.zeros((T,) + sh); PH = np.zeros((T, nq, nic)); WF = np.zeros((T, nq, nic)); QH = np.zeros((T, nq))
    for i in range(T):
        ouv = decl < 0
        si = np.where(ouv, s[:, i], 0.0)
        tq = -si * np.sin(ph)
        d = w + EPS * tq
        if aprende: w = w + ETAW * tq
        ph = ph + d
        th = th + C_OFF * w[..., None]
        Z = np.where(ouv, Z + a * (s[:, i] * np.exp(-1j * ph) - Z), Z)
        Zo = np.where(ouv[..., None], Zo + a[:, None] * (s[:, i][:, None] * np.exp(-1j * th) - Zo), Zo)
        Q = np.abs(Z) / np.sqrt(np.mean(np.abs(Zo) ** 2, -1) + 1e-30)
        WH[i] = w
        P = np.rint(2 * np.pi / np.abs(w)).astype(int)
        k = i - P
        wP = np.where(k >= 0, WH[np.clip(k, 0, None), np.arange(nq)[:, None, None], np.arange(nic)[None, :, None],
                                  np.arange(4)[None, None, :]], np.nan)
        estavel = np.abs(w - wP) <= DW * np.abs(w)
        q = limiar(i, qs)[:, None, :]
        ok = ouv & (i >= TAU) & (Q >= q) & estavel
        cnt = np.where(ok, cnt + 1, 0)
        novo = ouv & (cnt >= P)
        decl = np.where(novo, i, decl)
        PH[i] = ph[..., guardar_fase]; WF[i] = w[..., guardar_fase]; QH[i] = np.median(Q[..., guardar_fase], 1)
    return {"decl": decl, "PH": PH, "W": WF, "w_fim": w, "Q": QH}


def previsoes(PH, W, t, idx, ent, anos):
    """Por (q, início): ψ começa na 1ª entrada vivida e é corrigida a cada entrada (η = 0,3), em todos os anos desde a
    instalação; a previsão do ano y é feita em 1/09 com a fase e o ω daquele dia. Devolve {ano: (q, nIC)}."""
    psi = None; out = {}
    for y in sorted(ent):
        if y in anos:
            i0 = idx[f"{y}-09-01"]
            out[y] = t[i0] + emb(psi - PH[i0]) / W[i0]
        if ent[y] is not None:
            psi = PH[ent[y]].copy() if psi is None else psi + ETA_PSI * emb(PH[ent[y]] - psi)
    return out
