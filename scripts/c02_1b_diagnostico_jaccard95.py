"""SGV-C02.1b — DIAGNÓSTICO (não é portão, não muda veredito): distribuição do |Δ Jaccard HDR95| entre ×4 e ×8.

Pergunta: o 0,0207 de BS35·T1·2 no portão substituto C02.1b foi um sorteio de cauda ou um problema sistemático?
Para cada um dos 21 pares do BS35 substituto (mesmos ajustes GMM3 do portão), repete K vezes a medição do Jaccard
do HDR95 com sementes de Monte Carlo independentes (prefixo 'diag', disjuntas das do portão), na produção (×4)
e no dobro (×8), e estima P(|Δ| > 0,02) por par e a chance de os 21 pares passarem juntos.

O veredito do portão substituto C02.1b continua BLOQUEADO; nenhuma semente aqui substitui as do portão.

    python scripts/c02_1b_diagnostico_jaccard95.py --k 20 --saida reports/c02_1/diagnostico_jaccard95.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'scripts'))
from c02_1_portao_substituto import CASES, par  # noqa: E402
from experiments.c01_estimacao_independente import estimate_gmm  # noqa: E402
from experiments.c02_1_hdr_sem_malha import jaccard_loss, region, subseed  # noqa: E402

LIM, PROD = 0.02, 4


def jac95(fa, fb, s, tag, scale):
    ra = region(fa, 0.95, seed=subseed(s, f'diag|A|{tag}'), scale=scale)
    rb = region(fb, 0.95, seed=subseed(s, f'diag|B|{tag}'), scale=scale)
    return jaccard_loss(fa, fb, ra, rb, seed=subseed(s, f'diag|J|{tag}'), scale=scale)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--k', type=int, default=20); ap.add_argument('--saida', required=True)
    a = ap.parse_args()
    linhas = []
    for case in CASES:
        for rep in range(3):
            A, B, s = par('BS35s', case, rep)
            fa = estimate_gmm(A, seed=subseed(s, 'fitA')).model
            fb = estimate_gmm(B, seed=subseed(s, 'fitB')).model
            d = [abs(jac95(fa, fb, s, f'{k}|x4', PROD) - jac95(fa, fb, s, f'{k}|x8', 2 * PROD)) for k in range(a.k)]
            d = np.array(d)
            linhas.append({'caso': case, 'rep': rep, 'delta': d.tolist(), 'mediana': float(np.median(d)),
                           'maximo': float(d.max()), 'p_falha': float((d > LIM).mean())})
            print(f'BS35s {case} {rep}: |Δ| mediana {np.median(d):.4f} máx {d.max():.4f}  P(>{LIM}) {(d > LIM).mean():.2f}', flush=True)
    todos = np.concatenate([x['delta'] for x in linhas])
    # chance de os 21 pares passarem juntos (independência entre pares), com e sem suavização de Laplace
    p_raw = np.array([x['p_falha'] for x in linhas]); p_lap = np.array([(sum(np.array(x['delta']) > LIM) + 0.5) / (a.k + 1) for x in linhas])
    res = {'k': a.k, 'pares': len(linhas), 'abs_delta_mediana': float(np.median(todos)), 'abs_delta_p95': float(np.quantile(todos, .95)),
           'abs_delta_max': float(todos.max()), 'frac_medicoes_acima': float((todos > LIM).mean()),
           'p_portao_bs35_passa_bruto': float(np.prod(1 - p_raw)), 'p_portao_bs35_passa_laplace': float(np.prod(1 - p_lap)),
           'linhas': linhas}
    print(json.dumps({k: v for k, v in res.items() if k != 'linhas'}, ensure_ascii=False, indent=1))
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True); json.dump(res, open(a.saida, 'w'), indent=1)


if __name__ == '__main__':
    main()
