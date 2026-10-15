"""SGV-C02.1b — diagnóstico de sementes do portão substituto (não altera o veredito).

Repete o par de execuções de precisão (HDR95 ×4 e ×8) com 10 conjuntos novos de sementes de Monte Carlo,
mesmos ajustes GMM3, mesmo conjunto retido e mesmos limites. Ver PROTOCOLO_SGV_C02_1B_DIAGNOSTICO_SEMENTES_20261014.md.
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'scripts'))
from c02_1_portao_substituto import CASES, par  # noqa: E402
from experiments.c01_estimacao_independente import estimate_gmm  # noqa: E402
from experiments.c02_1_hdr_sem_malha import hdr12_ml, precision_checks_a, subseed  # noqa: E402

K = 10
RETIDAS = set(json.load(open(ROOT / 'reports/c02_1/portao_substituto_b.json'))['resumo']['retidas'])


def um_par(args):
    fam, case, rep = args
    a, b, s = par(fam, case, rep)
    fa = estimate_gmm(a, seed=subseed(s, 'fitA')).model
    fb = estimate_gmm(b, seed=subseed(s, 'fitB')).model
    out = []
    for k in range(1, K + 1):
        r1 = hdr12_ml(a, b, fa, fb, seed=subseed(s, f'ml1|diag{k}'), scale=1, hdr95_budget=4)
        r2 = hdr12_ml(a, b, fa, fb, seed=subseed(s, f'ml2|diag{k}'), scale=2, hdr95_budget=4)
        out.append({'k': k, 'falhas': precision_checks_a(r1, r2, RETIDAS),
                    'dj95': abs(r1['hdr95_jaccard_loss'] - r2['hdr95_jaccard_loss'])})
    print(fam, case, rep, 'ok', flush=True)
    return {'familia': fam, 'caso': case, 'rep': rep, 'conjuntos': out}


def main():
    jobs = [(f, c, r) for f in ('G3s', 'BS35s') for c in CASES for r in range(3)]
    with Pool(2) as pool:
        linhas = pool.map(um_par, jobs)
    por_conjunto = []
    for k in range(1, K + 1):
        falhas = {f"{x['familia']}|{x['caso']}|{x['rep']}": c['falhas'] for x in linhas for c in x['conjuntos'] if c['k'] == k and c['falhas']}
        dmax = max(c['dj95'] for x in linhas for c in x['conjuntos'] if c['k'] == k and x['familia'] == 'BS35s')
        por_conjunto.append({'k': k, 'passaria': not falhas, 'falhas': falhas, 'max_dj95_bs35': dmax})
    n_falha = sum(not c['passaria'] for c in por_conjunto)
    res = {'conjuntos': por_conjunto, 'conjuntos_com_falha': n_falha, 'de': K}
    print(json.dumps(res, ensure_ascii=False, indent=1))
    json.dump({'resumo': res, 'pares': linhas}, open(ROOT / 'reports/c02_1/diagnostico_sementes_b.json', 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
