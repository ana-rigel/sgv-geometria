"""IA geométrica v0: instrumento (registros em escada, régua, cegueira, política de olhar) e os quatro mundos. Registro: PROJETO_v0.md.

    python ia-geometrica/v0.py --fumaca          # roda tudo com poucas sementes; não imprime estatísticas de julgamento
    python ia-geometrica/v0.py --teste 1..4      # só depois da predição própria de cada teste (ainda não escrita)
"""
import argparse, json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent


# ---------------------------------------------------------------- o observador
class Observador:
    """k registros em escada geométrica. Tensões por andar na régua. Cegueira declarada. Olhar ou lembrar."""

    def __init__(self, d, k=4, lam1=0.15, b=10.0, lams=None, regua=None, theta=None, n_max=None):
        self.k = k; self.lams = np.array(lams) if lams is not None else lam1 / b ** np.arange(k)
        self.R = np.zeros((k, d)); self.regua = regua; self.theta = theta; self.n_max = n_max
        self.desde = 0; self.ultima_T0 = 0.0; self.hist_T = []

    @property
    def f_corte(self):  # frequência de corte de cada andar (filtro de 1ª ordem), em ciclos/passo
        return self.lams / (2 * np.pi)

    def quer_olhar(self):
        if self.theta is None: return True                       # filtro: olha sempre
        if self.n_max is not None and self.desde >= self.n_max: return True
        return self.ler(self.ultima_T0, 0) >= self.theta

    def ler(self, T, j):   # tensão do andar j na régua (mediana, escala); sem régua, bruta
        if self.regua is None: return T
        med, esc = self.regua[j]; return (T - med) / esc

    def passo(self, x=None):
        """x=None → não olhou: o andar 1 fica; os demais seguem como antes."""
        if x is not None:
            self.ultima_T0 = float(np.linalg.norm(x - self.R[0])); self.desde = 0
            self.R[0] += self.lams[0] * (x - self.R[0])
        else:
            self.desde += 1
        for j in range(1, self.k):
            self.R[j] += self.lams[j] * (self.R[j - 1] - self.R[j])
        T = [self.ultima_T0] + [float(np.linalg.norm(self.R[j] - self.R[j + 1])) for j in range(self.k - 1)]
        self.hist_T.append(T); return np.array(T)


def calibrar_regua(Ts):
    """Régua por andar a partir de um período de calibração: mediana e q99,5 do desvio ÷ 3 (como a régua de maio)."""
    Ts = np.asarray(Ts); out = []
    for j in range(Ts.shape[1]):
        v = Ts[:, j]; med = np.median(v); esc = np.quantile(np.abs(v - med), 0.995) / 3.0
        out.append((float(med), float(max(esc, 1e-12))))
    return out


def regime(T_regua, hist=3):
    """Núcleo < 1, transição 1–3, ruptura ≥ 3, com histerese de `hist` passos. Recebe a série de tensões na régua."""
    reg = np.zeros(len(T_regua), dtype=int); atual, cand, n = 0, 0, 0
    for t, v in enumerate(T_regua):
        alvo = 2 if v >= 3 else (1 if v >= 1 else 0)
        if alvo == cand: n += 1
        else: cand, n = alvo, 1
        if n >= hist: atual = cand
        reg[t] = atual
    return reg


def regime_relativo(T, alpha=0.08, hist=3):
    """O detector da mente de março: E_norm = (T − EMA)/EMA; RUPTURE > 0,15, STABLE < −0,12."""
    reg = np.zeros(len(T), dtype=int); ema = None; atual, cand, n = 0, 0, 0
    for t, v in enumerate(T):
        ema = v if ema is None else (1 - alpha) * ema + alpha * v; E = (v - ema) / ema if ema > 1e-12 else 0.0
        alvo = 2 if E > 0.15 else (0 if E < -0.12 else 1)
        if alvo == cand: n += 1
        else: cand, n = alvo, 1
        if n >= hist: atual = cand
        reg[t] = atual
    return reg


def cegueira(T_serie, lam):
    """Fração da potência de uma tensão acima da frequência de corte lam/2π (o que o andar seguinte não representa)."""
    v = np.asarray(T_serie) - np.mean(T_serie); P = np.abs(np.fft.rfft(v)) ** 2; f = np.fft.rfftfreq(len(v))
    tot = P[1:].sum(); return float(P[1:][f[1:] > lam / (2 * np.pi)].sum() / tot) if tot > 0 else 0.0


def colapso(Tj, Tj1):
    """C_j = 1 − disp(T_j padronizada pela escala do andar j+1) / disp(T_j bruta); escala = média móvel de T_{j+1} (como σ̂)."""
    Tj, Tj1 = np.asarray(Tj), np.asarray(Tj1); esc = np.maximum(Tj1, 1e-12)
    return float(1 - np.std(Tj / esc) / np.std(Tj)) if np.std(Tj) > 0 else 0.0


# ---------------------------------------------------------------- os mundos
def mundo_deriva(n, seed, phi, d=2, sig=1.0):
    """1. Deriva: campo = AR(1) com coeficiente phi (0 = ruído branco), sem saltos."""
    rng = np.random.default_rng(seed); x = np.zeros((n, d)); e = rng.normal(0, sig, (n, d))
    for t in range(1, n): x[t] = phi * x[t - 1] + e[t]
    return x


def mundo_custo(n, seed, phi=0.9, d=2):
    """2. Custo de olhar: o mundo 1 com phi = 0,9; o custo entra na política, não no mundo."""
    return mundo_deriva(n, seed, phi, d)


def mundo_salto(n, seed, phi=0.9, d=2, media_salto=200, amp=8.0):
    """3. Salto sobre deriva: mundo 1 com teleportes geométricos (média 200 passos) de amplitude ±amp."""
    rng = np.random.default_rng(seed); x = mundo_deriva(n, seed, phi, d); saltos = []
    t = rng.geometric(1 / media_salto)
    while t < n:
        x[t:] += rng.uniform(-amp, amp, d); saltos.append(int(t)); t += rng.geometric(1 / media_salto)
    return x, np.array(saltos)


def mundo_escada(n, seed, taus, d=2):
    """4a. Escada conhecida: campo = soma de AR(1) com constantes de tempo `taus` (razão 10)."""
    rng = np.random.default_rng(seed); x = np.zeros((n, d))
    for tau in taus:
        phi = 1 - 1 / tau; comp = np.zeros((n, d)); e = rng.normal(0, 1.0, (n, d)) * np.sqrt(1 - phi ** 2)
        for t in range(1, n): comp[t] = phi * comp[t - 1] + e[t]
        x += comp
    return x


def mundo_ciclico(n, seed, periodo=300, d=2):
    """4b. Uma escala só: senoide forte de período `periodo` mais ruído branco fraco."""
    rng = np.random.default_rng(seed); t = np.arange(n)[:, None]; fase = rng.uniform(0, 2 * np.pi, (1, d))
    return 3.0 * np.sin(2 * np.pi * t / periodo + fase) + rng.normal(0, 0.3, (n, d))


# ---------------------------------------------------------------- rodar um observador num mundo
def rodar(x, obs, calib=None):
    """Roda o observador sobre x. calib = nº de passos iniciais usados para calibrar a régua (se obs.regua é None e theta é dado)."""
    n = len(x); Ts = []; olhou = np.zeros(n, dtype=bool); Rh = np.zeros((n, obs.k, x.shape[1]))
    for t in range(n):
        if obs.theta is not None and obs.regua is None and calib is not None and t == calib:
            obs.regua = calibrar_regua(Ts)
        ver = obs.quer_olhar(); olhou[t] = ver
        Ts.append(obs.passo(x[t] if ver else None)); Rh[t] = obs.R
    return np.array(Ts), olhou, Rh


def erro_rastreamento(x, Rh, j=0):
    return float(np.mean(np.linalg.norm(x - Rh[:, j], axis=1)))


# ---------------------------------------------------------------- fumaça
def fumaca():
    n, seeds = 3000, range(1000, 1003); print("fumaça: instrumento e mundos")
    for s in seeds:
        x = mundo_deriva(n, s, 0.9); obs = Observador(2); Ts, olhou, Rh = rodar(x, obs)
        reg = regime(Ts[:, 0] / (np.median(Ts[:, 0]) + 1e-9)); c = [cegueira(Ts[:, j], obs.lams[j + 1]) for j in range(obs.k - 1)]
        C = [colapso(Ts[:, j], Ts[:, j + 1]) for j in range(obs.k - 1)]
        print(f"  deriva s{s}: erro R1 {erro_rastreamento(x, Rh):.3f} | cegueira por andar {np.round(c, 2)} | colapso {np.round(C, 2)} | olhou {olhou.mean():.2f}")
        x = mundo_custo(n, s); obs = Observador(2, theta=1.0, n_max=8); Ts, olhou, Rh = rodar(x, obs, calib=300)
        print(f"  custo  s{s}: erro R1 {erro_rastreamento(x, Rh):.3f} | olhou {olhou.mean():.2f}")
        x, saltos = mundo_salto(n, s); obs = Observador(2); Ts, olhou, Rh = rodar(x, obs); rg = regime((Ts[:, 0] - np.median(Ts[:300, 0])) / (np.quantile(np.abs(Ts[:300, 0] - np.median(Ts[:300, 0])), .995) / 3))
        rr = regime_relativo(Ts[:, 0]); print(f"  salto  s{s}: {len(saltos)} saltos | ruptura (régua) {np.mean(rg == 2):.3f} | ruptura (relativo) {np.mean(rr == 2):.3f}")
        x = mundo_escada(n, s, [7, 70, 700]); obs = Observador(2); Ts, olhou, Rh = rodar(x, obs); print(f"  escada s{s}: erro R1 {erro_rastreamento(x, Rh):.3f}")
        x = mundo_ciclico(n, s); obs = Observador(2); Ts, olhou, Rh = rodar(x, obs); print(f"  cíclico s{s}: erro R1 {erro_rastreamento(x, Rh):.3f}")
    print("fumaça: código rodou; nenhum critério foi avaliado")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--fumaca", action="store_true"); ap.add_argument("--teste", type=int, choices=[1, 2, 3, 4])
    a = ap.parse_args()
    if a.fumaca: fumaca()
    elif a.teste: raise SystemExit(f"teste {a.teste}: só depois da predição própria (PREDICAO_teste{a.teste}.md). Nada foi rodado.")
    else: ap.print_help()
