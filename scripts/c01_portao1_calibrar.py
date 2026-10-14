"""C01 phase-I engineering gate: synthetic-only HDR mass and grid convergence.

No model fitting, no classifier, no inference test, and no market files.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.c01_oraculo_hdr_fisher import known_pair, common_bounds, hdr_measure

ALPHAS = (.50, .95)
GRIDS = (35, 49)
CASES = tuple(f'T{k}' for k in range(7))
VOLUME_AREA_TOL = .10
COVERAGE_TOL = .015

def calibrate() -> dict:
    checks = []
    for kind in CASES:
        p, q = known_pair(kind)
        bounds = common_bounds(p, q)
        for alpha in ALPHAS:
            for side, model, seed in [('A', p, 20261014), ('B', q, 20262014)]:
                row = {'case': kind, 'alpha': alpha, 'side': side, 'seed': seed}
                try:
                    lo = hdr_measure(model, alpha=alpha, seed=seed, grid_n=35, bounds=bounds)
                    hi = hdr_measure(model, alpha=alpha, seed=seed, grid_n=49, bounds=bounds)
                    dv = abs(hi['volume']/lo['volume'] - 1)
                    da = abs(hi['area']/lo['area'] - 1)
                    covered = (abs(lo['coverage_error']) < COVERAGE_TOL and
                               abs(hi['coverage_error']) < COVERAGE_TOL)
                    valid = (lo['is_watertight'] and hi['is_watertight'] and
                             not lo['touches_boundary'] and not hi['touches_boundary'] and
                             dv <= VOLUME_AREA_TOL and da <= VOLUME_AREA_TOL and covered)
                    row.update({'ok': bool(valid), 'rel_volume_35_49': float(dv),
                                'rel_area_35_49': float(da),
                                'coverage_35': lo['coverage'], 'coverage_49': hi['coverage'],
                                'components_35': lo['components'], 'components_49': hi['components'],
                                'volume_35': lo['volume'], 'volume_49': hi['volume']})
                except (ValueError, RuntimeError, FloatingPointError) as exc:
                    row.update({'ok': False, 'error': str(exc)})
                checks.append(row)
    return {'status': 'ENGINEERING_ONLY',
            'contains_market_data': False, 'heldout_classification_executed': False,
            'grid': list(GRIDS), 'cases': list(CASES), 'levels': list(ALPHAS),
            'volume_area_tol': VOLUME_AREA_TOL, 'coverage_tol': COVERAGE_TOL,
            'passed': int(sum(x['ok'] for x in checks)), 'total': len(checks),
            'all_passed': all(x['ok'] for x in checks), 'checks': checks}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='reports/c01_portao1_calibracao.json')
    args = ap.parse_args()
    outcome = calibrate()
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(outcome, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(f"C01 fase I: {outcome['passed']}/{outcome['total']} verificacoes, "
          f"status={'APROVADO' if outcome['all_passed'] else 'FALHOU'}")
    for row in outcome['checks']:
        if not row['ok']:
            print('GATE FALHOU:', row)
    return 0 if outcome['all_passed'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
