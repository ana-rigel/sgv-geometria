"""SGV-C02.1 — gate 1 oracular refeito (plano §6.2): T3 precisa se distinguir de T0 em todas as famílias.

Calibração, réplicas 2.000.100–2.000.102 (fora dos pares do portão oficial). Distância de energia entre A e B
nas observações (sem ajuste). Passa se, em cada família, a média em T3 for maior que o máximo em T0.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.c01_oraculo_hdr_fisher import energy_distance  # noqa: E402
from experiments.c02_1_pares import gen  # noqa: E402

res = {}
for fam in gen.FAMILIES_DEV + gen.FAMILIES_OOD:
    e = {c: [energy_distance(*gen.pair_samples(fam, c, 2_000_100 + r, split='calibration')) for r in range(3)] for c in ('T0', 'T3')}
    res[fam] = {'T0': e['T0'], 'T3': e['T3'], 'passa': bool(np.mean(e['T3']) > max(e['T0']))}
    print(fam, {k: np.round(v, 4).tolist() for k, v in e.items()}, 'passa' if res[fam]['passa'] else 'FALHA')
out = {'familias': res, 'passa': all(v['passa'] for v in res.values())}
print('gate 1:', 'PASSA' if out['passa'] else 'FALHA')
json.dump(out, open(ROOT / 'reports' / 'c02_1' / 'gate1_oracular.json', 'w'), indent=1)
