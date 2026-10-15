"""SGV-C02.1 — PORTÃO OFICIAL de precisão (regras C02.1 + C02.1a + C02.1b + C02.1c). Julgamento único.

Gerador oficial da C02 (vendor/sgv_c02, byte a byte do pacote SHA-256 4691266c…), partição `calibration`,
5 famílias (G3, S5, B3, R7, BS35) × T0–T6, índice reservado 2.000.000 → 35 pares, 750 + 750.
Por par:
  - ajuste GMM3 do C01 (estimate_gmm) em A e B;
  - extrator HDR12-ML com o orçamento do C02.1c (HDR50 ×4, HDR95 ×16): produção (scale 1) e dobro (scale 2);
  - 5 reajustes por reamostragem com reposição (produção) para a regra de retenção do C02.1a;
  - envelope_core_delta (secundário, descritivo).
Retenção: confiabilidade ≥ 0,5 nas cinco famílias. Portão: nenhum ajuste inválido, todas as checagens de precisão
(C02.1a) nas variáveis retidas em todos os 35 pares, ≥ 6 retidas com ≥ 1 por nível.
Sementes: seed_for('calibration', família, classe, 2.000.000, 'c02_1|extrator') do próprio gerador, e
subseed(·, finalidade) do extrator, no mesmo esquema do portão substituto.

    python scripts/c02_1c_portao_oficial.py --saida reports/c02_1/portao_oficial.json

Recusa rodar se a saída já existir (julgamento único).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.c01_estimacao_independente import estimate_gmm  # noqa: E402
from experiments.c02_1_hdr_sem_malha import (  # noqa: E402
    MIN_RELIABILITY, N_BOOT, envelope_core_delta, feature_names, hdr12_ml,
    precision_checks_a, reliability, subseed,
)

GEN = ROOT / 'vendor' / 'sgv_c02' / 'experiments' / 'c02_generators.py'
GEN_SHA = '8d98fd9022192df2b4bd65e5bd8912aab6acadf083d503c06afef1eed2491ead'
if hashlib.sha256(GEN.read_bytes()).hexdigest() != GEN_SHA:
    sys.exit('c02_generators.py não confere com o pacote oficial')
_spec = importlib.util.spec_from_file_location('c02_generators', GEN)
gen = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(gen)

FAMS = ('G3', 'S5', 'B3', 'R7', 'BS35')
REP = 2_000_000
BUDGET = dict(hdr50_budget=4, hdr95_budget=16)


def um_par(args):
    fam, case = args
    a, b = gen.pair_samples(fam, case, REP, split='calibration')
    s = gen.seed_for('calibration', fam, case, REP, 'c02_1|extrator')
    rec = {'familia': fam, 'caso': case}
    try:
        fa = estimate_gmm(a, seed=subseed(s, 'fitA')).model
        fb = estimate_gmm(b, seed=subseed(s, 'fitB')).model
        rec['r1'] = hdr12_ml(a, b, fa, fb, seed=subseed(s, 'ml1'), scale=1, **BUDGET)
        rec['r2'] = hdr12_ml(a, b, fa, fb, seed=subseed(s, 'ml2'), scale=2, **BUDGET)
        rec['envelope_core_delta'] = envelope_core_delta(a, b)
        boots, env = [], []
        for k in range(N_BOOT):
            rg = np.random.default_rng(subseed(s, f'boot|{k}'))
            ab, bb = a[rg.integers(0, len(a), len(a))], b[rg.integers(0, len(b), len(b))]
            fak = estimate_gmm(ab, seed=subseed(s, f'fitA|{k}')).model
            fbk = estimate_gmm(bb, seed=subseed(s, f'fitB|{k}')).model
            boots.append(hdr12_ml(ab, bb, fak, fbk, seed=subseed(s, f'mlb|{k}'), scale=1, **BUDGET))
            env.append(envelope_core_delta(ab, bb))
        rec['boot'] = boots; rec['boot_envelope'] = env
    except ValueError as exc:
        rec['falha'] = str(exc)[:200]
    print(fam, case, 'ok' if 'falha' not in rec else rec['falha'], flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--saida', required=True); ap.add_argument('--proc', type=int, default=2)
    a = ap.parse_args()
    if Path(a.saida).exists():
        sys.exit(f'{a.saida} já existe: o portão oficial é julgado uma única vez')
    jobs = [(f, c) for f in FAMS for c in gen.CLASSES]
    with Pool(a.proc) as pool:
        linhas = pool.map(um_par, jobs)
    nomes = list(feature_names()) + ['envelope_core_delta']
    falhas_ajuste = [(x['familia'], x['caso'], x['falha']) for x in linhas if 'falha' in x]
    conf = {}
    for fam in FAMS:
        L = [x for x in linhas if x['familia'] == fam and 'falha' not in x]
        conf[fam] = {}
        for k in nomes:
            if len(L) < 3:
                conf[fam][k] = float('-inf'); continue
            if k == 'envelope_core_delta':
                m, bt = [x[k] for x in L], [x['boot_envelope'] for x in L]
            else:
                m, bt = [x['r1'][k] for x in L], [[bx[k] for bx in x['boot']] for x in L]
            conf[fam][k] = reliability(np.array(m), np.array(bt))
    retidas = {k for k in feature_names() if all(conf[f][k] >= MIN_RELIABILITY for f in FAMS)}
    checks = {f"{x['familia']}|{x['caso']}": precision_checks_a(x['r1'], x['r2'], retidas) for x in linhas if 'falha' not in x}
    n50 = sum(k.startswith('hdr50') for k in retidas); n95 = sum(k.startswith('hdr95') for k in retidas)
    passa = (not falhas_ajuste and all(not v for v in checks.values()) and len(retidas) >= 6 and n50 >= 1 and n95 >= 1)
    res = {'regras': 'C02.1 + C02.1a + C02.1b + C02.1c', 'gerador_sha256_zip': '4691266c21d313b3522577a5dfc6390c7dc654b8ee648ba8524a95bc50ebcd7a',
           'pares': len(linhas), 'retidas': sorted(retidas), 'n_retidas': len(retidas),
           'pares_com_falha_de_ajuste_ou_extracao': falhas_ajuste,
           'checagens_com_falha': {k: v for k, v in checks.items() if v}, 'portao_passa': passa, 'confiabilidade': conf}
    print(json.dumps({k: v for k, v in res.items() if k != 'confiabilidade'}, ensure_ascii=False, indent=1))
    print('confiabilidade (' + ' | '.join(FAMS) + '):')
    for k in nomes:
        print(f"  {k:28s} " + ' | '.join(f'{conf[f][k]:+.2f}' for f in FAMS) + f"  {'retida' if k in retidas else ('secundária' if k == 'envelope_core_delta' else 'sai')}")
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    json.dump({'resumo': res, 'pares': linhas}, open(a.saida, 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
