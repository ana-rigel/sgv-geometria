"""SGV-C02.1a — portão SUBSTITUTO com variabilidade do ajuste (não é o portão oficial).

Mesmos geradores locais de `c02_1_portao_substituto.py` (imitam G3 e BS35; não são o gerador
oficial da C02). Por par: execução principal ×1 e ×2 (Monte Carlo) + 5 reajustes do GMM3 em
reamostras com reposição de A e B (×1). Aplica a regra de retenção e o portão da errata
`PROTOCOLO_SGV_C02_1A_ERRATA_20261014.md`.

    python scripts/c02_1a_portao_substituto.py --reps 3 --saida reports/c02_1/portao_substituto_a.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from c02_1_portao_substituto import CASES, par  # noqa: E402
from experiments.c01_estimacao_independente import estimate_gmm  # noqa: E402
from experiments.c02_1_hdr_sem_malha import (  # noqa: E402
    MIN_RELIABILITY, N_BOOT, envelope_core_delta, feature_names, hdr12_ml,
    precision_checks_a, reliability, subseed,
)

FAMS = ('G3s', 'BS35s')


def um_par(fam, case, rep):
    a, b, s = par(fam, case, rep)
    rec = {'familia': fam, 'caso': case, 'rep': rep}
    try:
        fa = estimate_gmm(a, seed=subseed(s, 'fitA')).model
        fb = estimate_gmm(b, seed=subseed(s, 'fitB')).model
        rec['r1'] = hdr12_ml(a, b, fa, fb, seed=subseed(s, 'ml1'), scale=1)
        rec['r2'] = hdr12_ml(a, b, fa, fb, seed=subseed(s, 'ml2'), scale=2)
        rec['envelope_core_delta'] = envelope_core_delta(a, b)
        boots, env = [], []
        for k in range(N_BOOT):
            rg = np.random.default_rng(subseed(s, f'boot|{k}'))
            ab, bb = a[rg.integers(0, len(a), len(a))], b[rg.integers(0, len(b), len(b))]
            fak = estimate_gmm(ab, seed=subseed(s, f'fitA|{k}')).model
            fbk = estimate_gmm(bb, seed=subseed(s, f'fitB|{k}')).model
            boots.append(hdr12_ml(ab, bb, fak, fbk, seed=subseed(s, f'mlb|{k}'), scale=1))
            env.append(envelope_core_delta(ab, bb))
        rec['boot'] = boots; rec['boot_envelope'] = env
    except ValueError as exc:
        rec['falha'] = str(exc)[:160]
    print(fam, case, rep, 'ok' if 'falha' not in rec else rec['falha'], flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--reps', type=int, default=3); ap.add_argument('--saida', required=True)
    a = ap.parse_args()
    linhas = [um_par(f, c, r) for f in FAMS for c in CASES for r in range(a.reps)]
    nomes = list(feature_names()) + ['envelope_core_delta']
    conf = {}
    for fam in FAMS:
        L = [x for x in linhas if x['familia'] == fam and 'falha' not in x]
        conf[fam] = {}
        for k in nomes:
            if k == 'envelope_core_delta':
                main_ = [x[k] for x in L]; boot = [x['boot_envelope'] for x in L]
            else:
                main_ = [x['r1'][k] for x in L]; boot = [[bx[k] for bx in x['boot']] for x in L]
            conf[fam][k] = reliability(np.array(main_), np.array(boot))
    retidas = {k for k in feature_names() if all(conf[f][k] >= MIN_RELIABILITY for f in FAMS)}
    falhas_pares = [x for x in linhas if 'falha' in x]
    checks = {f"{x['familia']}|{x['caso']}|{x['rep']}": precision_checks_a(x['r1'], x['r2'], retidas)
              for x in linhas if 'falha' not in x}
    n50 = sum(k.startswith('hdr50') for k in retidas); n95 = sum(k.startswith('hdr95') for k in retidas)
    passa = (not falhas_pares and all(not v for v in checks.values()) and len(retidas) >= 6 and n50 >= 1 and n95 >= 1)
    res = {'confiabilidade': conf, 'retidas': sorted(retidas), 'n_retidas': len(retidas),
           'pares_com_falha_de_ajuste': [(x['familia'], x['caso'], x['rep'], x['falha']) for x in falhas_pares],
           'checagens_com_falha': {k: v for k, v in checks.items() if v}, 'portao_passa': passa}
    print(json.dumps({k: v for k, v in res.items() if k != 'confiabilidade'}, ensure_ascii=False, indent=1))
    print('confiabilidade (G3s | BS35s):')
    for k in nomes:
        print(f'  {k:28s} {conf["G3s"][k]:+.2f} | {conf["BS35s"][k]:+.2f}  {"retida" if k in retidas else ("secundária" if k == "envelope_core_delta" else "sai")}')
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    json.dump({'resumo': res, 'pares': linhas}, open(a.saida, 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
