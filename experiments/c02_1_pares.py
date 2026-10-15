"""SGV-C02.1 — medidas por par (base14 + HDR12-ML + envelope) no gerador oficial. Ver PLANO_SGV_C02_1_TREINO_OOD_20261015.md.

    python experiments/c02_1_pares.py --split training   --reps 50 --saida reports/c02_1/pares_training.jsonl
    python experiments/c02_1_pares.py --split validation --reps 12 --saida reports/c02_1/pares_validation.jsonl
    (OOD só pelo script de liberação, depois do congelamento)

Retoma: pula (família, classe, réplica) já gravados no .jsonl.
"""
from __future__ import annotations

import argparse
import contextlib
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
from experiments.c01_oraculo_hdr_fisher import (  # noqa: E402
    delta_entropy_mc, energy_distance, fr_ambient_mc, fr_covariance,
)
from experiments.c02_1_hdr_sem_malha import envelope_core_delta, hdr12_ml, subseed  # noqa: E402

GEN = ROOT / 'vendor' / 'sgv_c02' / 'experiments' / 'c02_generators.py'
GEN_SHA = '8d98fd9022192df2b4bd65e5bd8912aab6acadf083d503c06afef1eed2491ead'
if hashlib.sha256(GEN.read_bytes()).hexdigest() != GEN_SHA:
    sys.exit('c02_generators.py não confere com o pacote oficial')
_spec = importlib.util.spec_from_file_location('c02_generators', GEN)
gen = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(gen)

N_MC = 32_000
BUDGET = dict(hdr50_budget=4, hdr95_budget=16)
BASE14 = (['delta_mu_0', 'delta_mu_1', 'delta_mu_2'] + [f'delta_cov_{i}{j}' for i in range(3) for j in range(i, 3)]
          + ['logdet_cov_delta', 'entropy_delta', 'fr_cov', 'fr_ambient', 'energy'])
HDR6 = ['hdr50_center_distance', 'hdr50_log_volume_ratio', 'hdr50_shape_tensor_diff', 'hdr50_w2_hdr',
        'hdr50_cross_mass_shift', 'hdr95_shape_tensor_diff']
FAMS = {'training': gen.FAMILIES_DEV, 'validation': gen.FAMILIES_DEV, 'ood_test': gen.FAMILIES_OOD}


def _seed_for_liberacao(split, family, label, rep, purpose):
    """Mesma fórmula do seed_for oficial; aceita ood_test só para as famílias OOD (plano §1)."""
    if split == 'ood_test':
        if family not in gen.FAMILIES_OOD or label not in gen.CLASSES or rep < 0:
            raise ValueError('liberação OOD: só R7/BS35, classes T0–T6, réplica ≥ 0')
        key = f'C02|{gen.BASE_SEED}|{split}|{family}|{label}|{rep}|{purpose}'.encode()
        return int.from_bytes(hashlib.sha256(key).digest()[:8], 'big')
    return _seed_for_oficial(split, family, label, rep, purpose)


_seed_for_oficial = gen.seed_for


@contextlib.contextmanager
def liberar_ood():
    gen.seed_for = _seed_for_liberacao
    try:
        yield
    finally:
        gen.seed_for = _seed_for_oficial


def base14(a, b, p, q, s):
    ma, ca = p.moments(); mb, cb = q.moments(); dm, dc = mb - ma, cb - ca
    out = {f'delta_mu_{i}': float(v) for i, v in enumerate(dm)}
    out.update({f'delta_cov_{i}{j}': float(dc[i, j]) for i in range(3) for j in range(i, 3)})
    out['logdet_cov_delta'] = float(np.linalg.slogdet(cb)[1] - np.linalg.slogdet(ca)[1])
    out['entropy_delta'] = float(delta_entropy_mc(p, q, n=N_MC, seed=subseed(s, 'entropy') % (2**63))[0])
    out['fr_cov'] = fr_covariance(p, q)
    out['fr_ambient'] = float(fr_ambient_mc(p, q, n=N_MC, seed=subseed(s, 'fr_ambient'))['fr_ambient'])
    out['energy'] = energy_distance(a, b)
    return out


def registro(split, fam, case, rep):
    rec = {'split': split, 'familia': fam, 'classe': case, 'rep': rep}
    try:
        a, b = gen.pair_samples(fam, case, rep, split=split)
        s = gen.seed_for(split, fam, case, rep, 'c02_1|extrator')
        p = estimate_gmm(a, seed=subseed(s, 'fitA')).model
        q = estimate_gmm(b, seed=subseed(s, 'fitB')).model
        f = base14(a, b, p, q, s)
        h = hdr12_ml(a, b, p, q, seed=subseed(s, 'ml'), scale=1, **BUDGET)
        f.update({k: v for k, v in h.items() if not k.startswith('_')})
        f['envelope_core_delta'] = envelope_core_delta(a, b)
        if not all(np.isfinite(v) for v in f.values()):
            raise ValueError('medida não finita')
        rec.update(f)
    except ValueError as exc:
        rec['falha'] = str(exc)[:200]
    return rec


def _job(args):
    split = args[0]
    if split == 'ood_test':
        with liberar_ood():
            return registro(*args)
    return registro(*args)


def extrair(split, reps, saida, proc=2):
    if split not in FAMS:
        raise ValueError(split)
    saida = Path(saida); feitos = set()
    if saida.exists():
        for l in saida.read_text().splitlines():
            r = json.loads(l); feitos.add((r['familia'], r['classe'], r['rep']))
    jobs = [(split, f, c, r) for f in FAMS[split] for c in gen.CLASSES for r in range(reps) if (f, c, r) not in feitos]
    print(f'{split}: {len(feitos)} já feitos, {len(jobs)} a fazer', flush=True)
    saida.parent.mkdir(parents=True, exist_ok=True)
    with Pool(proc) as pool, open(saida, 'a') as fh:
        for i, rec in enumerate(pool.imap_unordered(_job, jobs)):
            fh.write(json.dumps(rec) + '\n'); fh.flush()
            if i % 25 == 0:
                print(f"  {i + 1}/{len(jobs)} {rec['familia']} {rec['classe']} {rec['rep']} {'ok' if 'falha' not in rec else rec['falha']}", flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--split', required=True, choices=['training', 'validation'])
    ap.add_argument('--reps', type=int, required=True); ap.add_argument('--saida', required=True); ap.add_argument('--proc', type=int, default=2)
    a = ap.parse_args()
    extrair(a.split, a.reps, a.saida, a.proc)
