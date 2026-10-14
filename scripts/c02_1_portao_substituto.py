"""SGV-C02.1 — portão SUBSTITUTO de engenharia (não é o portão oficial).

O gerador oficial da C02 (pacote SGV_C02_GERADOR_PILOTO_20261014.zip, SHA-256 4691266c…)
ainda não está no ramo. Este script usa geradores LOCAIS que imitam G3 (mistura de 3
gaussianas) e BS35 (mistura de 3 t de Student ν = 3,5 com deformação banana) e as
transformações T0–T6 do protocolo C02, só para comparar, nas MESMAS densidades
ajustadas, o extrator de grade do C01 (35³ contra 49³) com o extrator HDR12-ML
(orçamento ×1 contra ×2). Nada aqui é dado oficial, treino, validação ou OOD.

    python scripts/c02_1_portao_substituto.py --saida reports/c02_1/portao_substituto.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.c01_estimacao_independente import estimate_gmm  # noqa: E402
from experiments.c01_oraculo_hdr_fisher import hdr_pair  # noqa: E402
from experiments.c02_1_hdr_sem_malha import hdr12_ml, precision_checks, subseed  # noqa: E402

N = 750
CASES = tuple(f'T{i}' for i in range(7))
MEANS = np.array([[0.0, 0.0, 0.0], [1.6, 0.4, 0.0], [-0.8, 1.2, 0.5]])
SCALES = np.array([[0.8, 0.5, 0.4], [0.5, 0.6, 0.3], [0.6, 0.4, 0.5]])
W0 = np.array([0.5, 0.3, 0.2])


def latent(fam: str, weights: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    k = rng.choice(3, size=n, p=weights)
    z = rng.standard_normal((n, 3))
    if fam == 'BS35s':
        z = z / np.sqrt(rng.chisquare(3.5, size=(n, 1)) / 3.5)
    x = MEANS[k] + z * SCALES[k]
    if fam == 'BS35s':
        x[:, 1] = x[:, 1] + 0.35 * (x[:, 0] ** 2 - 1.0)      # banana (invertível, jacobiano 1)
    return x


def draw(fam: str, case: str, n: int, rng: np.random.Generator) -> np.ndarray:
    w = W0.copy()
    if case == 'T5':
        w = np.array([0.8, 0.12, 0.08])
    x = latent(fam, w, n, rng)
    if case == 'T1':
        x = x + np.array([0.0, 0.65, 0.0])
    elif case == 'T2':
        x = x * 1.25
    elif case == 'T3':
        x = x @ np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]]).T
    elif case == 'T4':
        x = x @ np.array([[1., .55, 0.], [0., 1., 0.], [0., 0., 1.]]).T
    elif case == 'T6':
        extra = rng.random(n) < 0.05
        x[extra] = np.array([2.8, 0., 0.]) + 0.35 * rng.standard_normal((extra.sum(), 3))
    return x


def par(fam: str, case: str, rep: int):
    s = subseed(20261014, f'substituto|{fam}|{case}|{rep}')
    rng = np.random.default_rng(s)
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    nuis = q * rng.uniform(0.9, 1.1)
    shift = rng.uniform(-0.25, 0.25, 3)
    a = draw(fam, 'T0', N, np.random.default_rng(subseed(s, 'A'))) @ nuis.T + shift
    b = draw(fam, case, N, np.random.default_rng(subseed(s, 'B'))) @ nuis.T + shift
    return a, b, s


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--saida', required=True); ap.add_argument('--reps', type=int, default=1)
    a_ = ap.parse_args()
    linhas = []
    for fam in ('G3s', 'BS35s'):
        for case in CASES:
            for rep in range(a_.reps):
                a, b, s = par(fam, case, rep)
                rec = {'familia': fam, 'caso': case, 'rep': rep}
                try:
                    fa = estimate_gmm(a, seed=subseed(s, 'fitA')).model
                    fb = estimate_gmm(b, seed=subseed(s, 'fitB')).model
                except ValueError as exc:
                    rec['gmm_invalido'] = str(exc)[:120]; linhas.append(rec); print(fam, case, 'GMM inválido'); continue
                # extrator de grade do C01, 35³ contra 49³, nas mesmas densidades
                grade = {}
                for g in (35, 49):
                    try:
                        m = hdr_pair(fa, fb, alpha=0.5, seed=int(subseed(s, 'grade') % 2**62), grid_n=g, cutoff_n=32000, cover_n=32000)
                        grade[g] = {'vol_a': m['A']['volume'], 'vol_b': m['B']['volume'], 'area_a': m['A']['area']}
                    except ValueError as exc:
                        grade[g] = {'erro': str(exc)[:100]}
                if all('erro' not in grade[g] for g in (35, 49)):
                    rec['grade_var_rel_volume_hdr50'] = float(max(abs(grade[49]['vol_a'] / grade[35]['vol_a'] - 1), abs(grade[49]['vol_b'] / grade[35]['vol_b'] - 1)))
                    rec['grade_var_rel_area_hdr50'] = float(abs(grade[49]['area_a'] / grade[35]['area_a'] - 1))
                else:
                    rec['grade_erro'] = {g: grade[g].get('erro') for g in (35, 49)}
                # extrator sem malha, orçamento ×1 contra ×2, sementes independentes
                try:
                    r1 = hdr12_ml(a, b, fa, fb, seed=subseed(s, 'ml1'), scale=1)
                    r2 = hdr12_ml(a, b, fa, fb, seed=subseed(s, 'ml2'), scale=2)
                    rec['ml_falhas'] = precision_checks(r1, r2)
                    rec['ml_dif'] = {k: abs(r1[k] - r2[k]) for k in r1 if not k.startswith('_num_')}
                    rec['ml_diag'] = {k: r1[k] for k in r1 if k.startswith('_num_')}
                    rec['ml_valores'] = {k: r1[k] for k in r1 if not k.startswith('_num_')}
                except ValueError as exc:
                    rec['ml_erro'] = str(exc)[:120]
                linhas.append(rec)
                print(fam, case, rep, 'grade:', round(rec.get('grade_var_rel_volume_hdr50', float('nan')), 3), '| ML falhas:', rec.get('ml_falhas', rec.get('ml_erro')), flush=True)
    Path(a_.saida).parent.mkdir(parents=True, exist_ok=True)
    json.dump(linhas, open(a_.saida, 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
