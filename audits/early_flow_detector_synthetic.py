#!/usr/bin/env python3
"""Viabilidade sintética de um detector sequencial de mudança no impacto do fluxo.

NÃO é continuação confirmatória da L2 (encerrada por falta de poder).
Compara score vetorial causal (60 barras) e contraste de meias-janelas (1440)
com a MESMA taxa nominal de alarmes sob um nulo estacionário independente.
A mudança plantada é forte e, por construção, antecede volatilidade em 120 barras.
Resultados neste simulador não estabelecem predição em BTC real.

python audits/early_flow_detector_synthetic.py --out audits/resultados/score_exploratorio.json
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

W, S, L, LEAD, N, T0 = 1440, 60, 60, 120, 4200, 2520
NOISE, SHIFT_A1, SHIFT_AR = 0.65, 0.65, 0.30
ALARM_Q = 0.995
SEEDS_CAL = range(0, 30)
SEEDS_NULL = range(30, 70)
SEEDS_ALT = range(70, 110)


def generate(seed: int, planted: bool):
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(N)
    eps = rng.normal(0., NOISE, N)
    q = np.zeros(N)
    vol = np.full(N, 1e-3)
    if planted:
        vol[T0 + LEAD:] *= 2.  # Mudança de vol acontece DEPOIS do impacto.
    ret = vol * z
    for t in range(1, N):
        state = int(planted and t >= T0)
        q[t] = 0.10 + (0.8 + SHIFT_A1*state)*z[t] + (0.5 + SHIFT_AR*state)*q[t-1] + eps[t]
    x = np.column_stack([np.ones(N), z, np.r_[0., q[:-1]]])
    return x, q, ret


def fit(x, y):
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    noise = max(float(np.std(y-x@beta, ddof=x.shape[1])), 1e-8)
    return beta, noise


def stat_score(x, y, t, beta, sd):
    """GLR de score com bloco recente de L barras, desconhece q futura."""
    xx = x[t-L:t]
    e = y[t-L:t] - xx@beta
    score = xx.T@e
    information = xx.T@xx
    return float(score@np.linalg.solve(information + 1e-8*np.eye(3), score)/(sd*sd))


def stat_halfwindow(x, y, t):
    """Apenas bloco de impacto do L2: contraste A/B na informação local."""
    half = W//2
    xa, ya = x[t-W:t-half], y[t-W:t-half]
    xb, yb = x[t-half:t], y[t-half:t]
    aa, sa = fit(xa,ya)
    bb, sb = fit(xb,yb)
    d = bb-aa
    metric = .5*(xa.T@xa/len(xa)/sa**2 + xb.T@xb/len(xb)/sb**2)
    return float(d@metric@d)


def measures(seed, planted):
    x, y, _ = generate(seed, planted)
    beta, sd = fit(x[:W], y[:W])
    ts = np.arange(W+S, N, S)
    scores = np.array([stat_score(x,y,int(t),beta,sd) for t in ts])
    slow = np.array([stat_halfwindow(x,y,int(t)) for t in ts])
    return ts, scores, slow


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("audits/resultados/score_exploratorio.json"))
    args=ap.parse_args()
    calibration=[measures(s,False) for s in SEEDS_CAL]
    th_score=float(np.quantile(np.concatenate([v[1] for v in calibration]),ALARM_Q))
    th_slow=float(np.quantile(np.concatenate([v[2] for v in calibration]),ALARM_Q))
    null=[measures(s,False) for s in SEEDS_NULL]
    alt=[measures(s,True) for s in SEEDS_ALT]

    def fpr(j):
        return float(np.mean(np.concatenate([v[j] > (th_score if j==1 else th_slow) for v in null])))
    def power(j):
        th=th_score if j==1 else th_slow
        # Uma previsão apenas se t <= T0+LEAD, antes da primeira barra com vol alta.
        return float(np.mean([np.any(v[j][(v[0]>T0)&(v[0]<=T0+LEAD)]>th) for v in alt]))
    out={
      "status":"SOMENTE_SINTETICO_EXPLORATORIO","W":W,"S":S,"score_memory":L,
      "antecedencia_barras":LEAD,"shift_a1":SHIFT_A1,"shift_persistencia":SHIFT_AR,
      "n_calibracao":len(SEEDS_CAL),"n_nulo_teste":len(SEEDS_NULL),
      "n_alternativa_teste":len(SEEDS_ALT),"quantil_limiar":ALARM_Q,
      "limiares":{"score":th_score,"contraste_l2_bloco_a":th_slow},
      "taxa_falsos_alarmes_por_avaliacao":{"score":fpr(1),"contraste_l2_bloco_a":fpr(2)},
      "poder_antes_vol_mudar":{"score":power(1),"contraste_l2_bloco_a":power(2)},
      "limites":"Simulador simplificado de regressão de fluxo; L2 comparado SOMENTE no bloco de impacto, não no SF1 completo. Não testar BTC real nem alterar pre-registros encerrados."
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(out,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
