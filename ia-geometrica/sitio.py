"""Mundo sítio sintético (teste 26): chuva sazonal, córrego com resposta rápida e lenta, cheia com custo e um ato de proteção.

Passo = 1 hora. Unidades: chuva em mm/h, nível do córrego em metros.

    python ia-geometrica/sitio.py --fumaca   # só estatísticas do MUNDO em sementes de desenho (5000–5009); nenhuma política é avaliada
"""
import argparse
import numpy as np

H_ANO = 24 * 365
# estação chuvosa de Mato Grosso, aproximada: outubro a abril (dias 274..365 e 0..120 do ano)
CHUVA_INI, CHUVA_FIM = 274, 120

# parâmetros do mundo (fixados na fumaça do mundo, antes da predição; ver PREDICAO_teste26_mundo_sitio.md)
P_TEMP = {"chuva": 1 / 55, "seca": 1 / 600}      # chance de começar uma chuva por hora
DUR_MEDIA = 4.0                                   # horas de chuva por evento (geométrica)
INT_MEDIA = {"chuva": 6.0, "seca": 3.0}           # mm/h durante a chuva (exponencial)
TAU_RAPIDO, TAU_LENTO = 8.0, 720.0                # horas: escoamento superficial e base (≈ 30 dias)
C_RAPIDO, C_LENTO = 0.012, 0.0009                 # m por mm que entram em cada reservatório
BASE0 = 0.4                                       # nível de base na seca (m)
RUIDO_SENSOR = 0.02                               # m


def estacao(t):
    dia = (t // 24) % 365
    return "chuva" if (dia >= CHUVA_INI or dia < CHUVA_FIM) else "seca"


def mundo_sitio(n, seed):
    """Devolve (chuva, nível verdadeiro, nível lido pelo sensor)."""
    rng = np.random.default_rng(seed)
    r = np.zeros(n); h = np.zeros(n); q = 0.0; b = BASE0; resta = 0; inten = 0.0
    for t in range(n):
        e = estacao(t)
        if resta == 0 and rng.random() < P_TEMP[e]:
            resta = rng.geometric(1 / DUR_MEDIA); inten = rng.exponential(INT_MEDIA[e])
        if resta > 0:
            r[t] = inten * rng.uniform(0.5, 1.5); resta -= 1
        q += C_RAPIDO * r[t] - q / TAU_RAPIDO
        b += C_LENTO * r[t] - (b - BASE0) / TAU_LENTO
        h[t] = b + q
    return r, h, h + rng.normal(0, RUIDO_SENSOR, n)


def eventos_de_cheia(h, h_crit, seco=24):
    """Início de cada cheia: cruzamento para cima de h_crit depois de pelo menos `seco` horas abaixo."""
    acima = h >= h_crit; ev = []; ultimo_acima = -10 ** 9
    for t in np.flatnonzero(acima):
        if t - ultimo_acima > seco: ev.append(int(t))
        ultimo_acima = t
    return np.array(ev, dtype=int)


def chamadas(cond, protecao):
    """Chama na primeira hora em que cond é verdadeira e não há proteção pedida em curso (refratário = proteção)."""
    idx = np.flatnonzero(cond); out = []; i = 0
    while i < len(idx):
        t = int(idx[i]); out.append(t); i = int(np.searchsorted(idx, t + protecao))
    return np.array(out, dtype=int)


def custo(ev, ch, ini, fim, D, c, L, P):
    """Custo na janela [ini, fim): c por chamada; D por cheia sem proteção ativa (ato em a protege [a+L, a+L+P])."""
    chj = ch[(ch >= ini) & (ch < fim)]; evj = ev[(ev >= ini) & (ev < fim)]
    perdas = 0
    for t in evj:
        if not np.any((ch + L <= t) & (t <= ch + L + P)): perdas += 1
    return c * len(chj) + D * perdas, int(perdas), int(len(chj)), int(len(evj))


def oraculo(ev, L, P):
    """Sabe o futuro: chama L horas antes de cada cheia que ainda não estaria protegida."""
    out = []
    for t in ev:
        if not out or not (out[-1] + L <= t <= out[-1] + L + P): out.append(int(t - L))
    return np.array(out, dtype=int)


def pluviometro(r, resol=0.2):
    """Leitura do pluviômetro de báscula: chuva da hora arredondada a 0,2 mm (sem sorteio, para não mudar o mundo do teste 26)."""
    return np.round(r / resol) * resol


def episodios(r, seco=12):
    """Episódios de chuva: horas com chuva separadas por menos de `seco` horas secas. Devolve lista de (início, fim)."""
    idx = np.flatnonzero(r > 0); out = []
    if len(idx) == 0: return out
    ini = ant = int(idx[0])
    for t in idx[1:]:
        if t - ant > seco: out.append((ini, ant)); ini = int(t)
        ant = int(t)
    out.append((ini, ant)); return out


def teto_chuva(r, ev, ini, fim, D, c, L, P, seco=12):
    """Teto causal de quem vê a chuva começar e sabe, no início, se aquele episódio vai virar cheia:
    chama no início de cada episódio que precede uma cheia (cheia entre o início e 24 h após o fim). Não é política; é limite."""
    eps = episodios(r, seco); ch = []
    for a, b in eps:
        if np.any((ev >= a) & (ev <= b + 24)): ch.append(a)
    return custo(ev, np.array(ch, dtype=int), ini, fim, D, c, L, P)


def fumaca():
    n = 2 * H_ANO; print("fumaça do mundo sítio (sementes de desenho 5000–5009; não são as do teste)")
    hs = []
    for s in range(5000, 5010):
        r, h, x = mundo_sitio(n, s); hs.append(h)
        print(f"  s{s}: chuva {r.sum()/2:.0f} mm/ano | horas de chuva {np.mean(r>0)*100:.1f} % | nível mediano {np.median(h):.2f} m, q99 {np.quantile(h,.99):.2f}, máx {h.max():.2f}")
    H = np.concatenate(hs)
    for hc in (1.0, 1.1, 1.2, 1.3, 1.4, 1.6):
        nev = np.mean([len(eventos_de_cheia(h, hc)) / 2 for h in hs])
        print(f"  h_crit {hc:.1f} m: {nev:.1f} cheias por ano (média nas 10 sementes de desenho)")
    print("fumaça: nenhuma política foi avaliada")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--fumaca", action="store_true")
    if ap.parse_args().fumaca: fumaca()
