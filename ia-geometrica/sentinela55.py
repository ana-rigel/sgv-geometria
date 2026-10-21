"""A sentinela do dia (teste 55): a sentinela do teste 54 (sentinela.py, intocada) com três parâmetros abertos e a
correção do defeito 75.

- ε (acoplamento do relógio ao seu andar) e η_w = ε/τ_aprender (aprender a frequência) passam a ser parâmetros. Com dado
  horário, o andar 1 tem ritmo próprio de 42 h e o dia (24 h) fica a 0,112 rad/h dele: com ε = 0,01 o relógio não alcança
  o dia (teste 52: trava se εA/2 ≥ |λ − Ω|).
- Defeito 75: além de Q ≥ q*, de ω estável e da sustentação por um período, o andar só declara se a frequência que ele
  GUARDA é a que ele OUVE: |ω_j − ν_j| ≤ 5 % de ν_j, onde ν_j é a média exponencial do passo realizado dφ_j na mesma
  janela τ_j. Um relógio arrastado pelo ritmo com ω errado (o controle do teste 54) ouve ν ≈ Ω e guarda ω ≠ Ω: não declara.
- O tempo é medido em passos (horas, aqui); a janela de cada andar continua sendo 3 períodos naturais (126 h, 52 d, 1,4 ano,
  14 anos).
- Entrada do relógio: a TENSÃO do andar, s_j = (R_j − R_{j+1})·u/√λ (o último andar ouve o próprio registro), e não o
  registro R_j. No piloto horário, o registro carrega o ano e a deriva lenta como "componente constante" e o relógio se
  prende a frequência zero (ω₁ → 0). A tensão é o que o andar recebe e não guarda (defeito 11 do teste 5): uma banda.
  u é o autovetor principal da covariância acumulada da tensão do andar 1, com o sinal do 1º sensor positivo.
Normalização e cascata online são as de sentinela.py.
"""
import numpy as np
from sentinela import LAM, C_OFF, normalizar_online, cascata  # noqa: F401  (reexportadas)

TAU = 3 * 2 * np.pi / LAM
DW = 0.05
DV = 0.05


def tensoes_online(R, inicio=30):
    """s (4, T): tensões dos andares projetadas no autovetor principal da covariância acumulada da tensão do andar 1."""
    _, T, d = R.shape
    TS = np.concatenate([R[:-1] - R[1:], R[-1:]], 0)
    s = np.zeros((4, T)); S1 = np.zeros(d); S2 = np.zeros((d, d))
    for i in range(T):
        x = TS[0, i]; S1 += x; S2 += np.outer(x, x)
        if i + 1 < inicio: continue
        n = i + 1; C = S2 / n - np.outer(S1 / n, S1 / n)
        lv, V = np.linalg.eigh(C); u = V[:, -1]; u = u if u[0] >= 0 else -u
        if lv[-1] > 0: s[:, i] = TS[:, i] @ u / np.sqrt(lv[-1])
    return s


def limiar(i, alfa, tau=TAU):
    n = np.maximum(1.0, (i + 1) / tau)
    p = np.asarray(alfa, float)[:, None] / n
    return np.sqrt(4 * (p ** -0.25 - 1))


def sentinela(s, ph0, eps, tau_aprender, alfas, aprende=True, exige_ouvida=True, guardar=0, janelas=3, silencia=True):
    """s (4, T); ph0 (nIC,); alfas: valores de α rodados juntos. Devolve o passo da declaração por (α, início, andar)
    (−1 = nunca), ω, ν e fase do andar `guardar` por passo (T, nα, nIC) e ω no fim (nα, nIC, 4).
    silencia=False (teste 56): depois de declarar, o andar continua ouvindo o campo; a declaração só fica registrada."""
    alfas = np.asarray(alfas, float); nq, nic, T = len(alfas), len(ph0), s.shape[1]
    sh = (nq, nic, 4); etaw = eps / tau_aprender if aprende else 0.0
    ph = np.broadcast_to(ph0[None, :, None], sh).copy(); w = np.broadcast_to(LAM, sh).copy()
    th = np.broadcast_to(ph[..., None], sh + (len(C_OFF),)).copy()
    Z = np.zeros(sh, complex); Zo = np.zeros(sh + (len(C_OFF),), complex); nu = w.copy()
    tau = janelas * 2 * np.pi / LAM
    cnt = np.zeros(sh, int); decl = np.full(sh, -1); a = 1.0 / tau
    WH = np.zeros((T,) + sh); WG = np.zeros((T, nq, nic)); NG = np.zeros((T, nq, nic)); PG = np.zeros((T, nq, nic))
    ii = (np.arange(nq)[:, None, None], np.arange(nic)[None, :, None], np.arange(4)[None, None, :])
    for i in range(T):
        ainda = decl < 0
        ouv = ainda if silencia else np.ones(sh, bool)
        si = np.where(ouv, s[:, i], 0.0)
        tq = -si * np.sin(ph)
        d = w + eps * tq
        w = w + etaw * tq
        ph = ph + d
        nu = nu + a * (d - nu)
        th = th + C_OFF * w[..., None]
        Z = np.where(ouv, Z + a * (s[:, i] * np.exp(-1j * ph) - Z), Z)
        Zo = np.where(ouv[..., None], Zo + a[:, None] * (s[:, i][:, None] * np.exp(-1j * th) - Zo), Zo)
        Q = np.abs(Z) / np.sqrt(np.mean(np.abs(Zo) ** 2, -1) + 1e-30)
        WH[i] = w
        P = np.rint(2 * np.pi / np.maximum(np.abs(w), 1e-9)).astype(np.int64)
        k = i - P
        wP = np.where(k >= 0, WH[(np.clip(k, 0, None),) + ii], np.nan)
        ok = ainda & (i >= tau) & (Q >= limiar(i, alfas, tau)[:, None, :]) & (np.abs(w - wP) <= DW * np.abs(w))
        if exige_ouvida: ok &= np.abs(w - nu) <= DV * np.abs(nu)
        cnt = np.where(ok, cnt + 1, 0)
        novo = ainda & (cnt >= P)
        decl = np.where(novo, i, decl)
        WG[i] = w[..., guardar]; NG[i] = nu[..., guardar]; PG[i] = ph[..., guardar]
    return {"decl": decl, "W": WG, "NU": NG, "PH": PG, "w_fim": w}
