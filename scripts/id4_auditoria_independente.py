"""Read-only independent numerical audit of an ALREADY consumed SGV-ID4 holdout.

Does not import its simulation module, fit any model, nor generate trajectories.
The previously registered seed and whole-path bootstrap are reproduced.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

EXPECTED_SOURCE_BLOB = '471070b3d179d9bad50aaab3756ac1484008bd15'
EXPECTED_FREEZE_BLOB = 'd99568bd2f4998a0f1ca8e6411ca6afa44135c4b'
EXPECTED_RESULT_BLOB = '134fdbb979f8d74c789c9ac795075d4d583ae7c0'
EXPECTED_TEST_IDS = list(range(18,30))
BOOT_SEED = 202610154


def git_blob_sha1(path:Path) -> str:
    x=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(x)).encode()+b'\0'+x).hexdigest()


def audit(repo:Path) -> dict:
    code=repo/'pipeline/id4_vol_direction.py'
    frozen=repo/'resultados/id4_modelos_congelados.json'
    result=repo/'resultados/id4_resultado_teste_unico.json'
    release=repo/'resultados/id4_TEST_RELEASE.txt'
    for p,expected in ((code,EXPECTED_SOURCE_BLOB),(frozen,EXPECTED_FREEZE_BLOB),
                       (result,EXPECTED_RESULT_BLOB)):
        got=git_blob_sha1(p)
        if got != expected:
            raise ValueError(f'Unexpected source blob {p.name}: {got}')
    if 'HELDOUT RELEASED' not in release.read_text():
        raise ValueError('Missing release record')
    data=json.loads(result.read_text())
    frz=json.loads(frozen.read_text())
    if hashlib.sha256(frozen.read_bytes()).hexdigest()!=data['freeze_sha256']:
        raise ValueError('Frozen model SHA-256 mismatch')
    if data['market_data_used'] or not data['test_opened_once']:
        raise ValueError('Invalid disclosure of synthetic-only and one release')
    full=data['full_report']
    if full['ids']!=EXPECTED_TEST_IDS or frz['trained_on']!=list(range(12)):
        raise ValueError('ID mismatch')
    if frz['validation_ids']!=list(range(12,18)) or frz['sealed_test_ids']!=EXPECTED_TEST_IDS:
        raise ValueError('partition mismatch')
    if len(full['sha256_pairs'])!=12 or len(set(full['sha256_pairs']))!=12:
        raise ValueError('path label hashing invalid')
    if len(full['energy_rho'])!=12 or not np.isfinite(full['energy_rho']).all():
        raise ValueError('energy rho invalid')

    rng=np.random.default_rng(BOOT_SEED)
    outcomes={}
    for condition in ('null','direction'):
        rows=full['outcomes'][condition]
        if [r['id'] for r in rows]!=EXPECTED_TEST_IDS:
            raise ValueError('duplicate or unordered paths')
        delta=np.array([r['delta'] for r in rows])
        base=np.array([r['base'] for r in rows])
        plus=np.array([r['plus'] for r in rows])
        if not np.allclose(delta,base-plus,rtol=0,atol=1e-13):
            raise ValueError('per-path difference mismatch')
        boot_indices=rng.integers(0,len(rows),size=(2000,len(rows)))
        ci=np.quantile(delta[boot_indices].mean(axis=1),[.025,.975])
        b=float(base.mean())
        p=float(plus.mean())
        d=float(delta.mean())
        recorded=data['summary']['outcomes'][condition]
        if any(abs(u-v)>1e-12 for u,v in (
            (b,recorded['mean_base_logloss']),
            (p,recorded['mean_plus_logloss']),
            (d,recorded['delta_logloss']),
            (float(ci[0]),recorded['ci95'][0]),
            (float(ci[1]),recorded['ci95'][1])
        )):
            raise ValueError('bootstrap or loss mismatch')
        outcomes[condition]={'mean_base':b,'mean_plus':p,'delta':d,
                             'ci95':ci.tolist(),'n_paths':len(rows)}
    gates={'null_specificity':abs(outcomes['null']['delta'])<=.015,
           'direction_sensitive':outcomes['direction']['delta']>=.05
              and outcomes['direction']['ci95'][0]>0,
           'energy_unidentifiable_by_construction':
              bool(data['summary']['gates']['energy_unidentifiable_by_construction'])}
    if gates!=data['summary']['gates'] or not all(gates.values()):
        raise ValueError('registered gates inconsistent')
    return {'status':'READ_ONLY_AUDIT_PASSED','gates':gates,
            'outcomes':outcomes,'model_sha256':data['freeze_sha256'],
            'checked_exact_blobs':3,'n_trajectories_tested':12,
            'note':'Energy equality is verified by generators/unit tests, not raw samples (not stored). No new holdout generated.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',default='.')
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    result=audit(Path(args.repo))
    output=Path(args.out)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(result['status'], result['gates'])


if __name__=='__main__':
    main()
