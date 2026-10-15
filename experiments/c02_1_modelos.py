"""SGV-C02.1 — modelos (ajustados só no treino), avaliação, endpoint e bootstrap. Ver PLANO_SGV_C02_1_TREINO_OOD_20261015.md §3–5.

    python experiments/c02_1_modelos.py validacao     # treina em 1.050, relata validação (descritiva), salva modelos
"""
from __future__ import annotations

import hashlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.c02_1_pares import BASE14, HDR6  # noqa: E402

DIR = ROOT / 'reports' / 'c02_1'
CLASSES = [f'T{i}' for i in range(7)]
HDR5 = [k for k in HDR6 if k != 'hdr50_w2_hdr']
EPS = 1e-15


def hgb():
    return HistGradientBoostingClassifier(learning_rate=0.06, max_iter=180, max_leaf_nodes=15, l2_regularization=1.0,
                                          early_stopping=False, random_state=20261014)


def logit():
    return make_pipeline(StandardScaler(), LogisticRegression(C=1, solver='lbfgs', max_iter=2000))


def carregar(nome):
    rows = [json.loads(l) for l in (DIR / nome).read_text().splitlines()]
    df = pd.DataFrame(rows)
    falhas = df[df['falha'].notna()] if 'falha' in df else df.iloc[:0]
    ok = df[df['falha'].isna()] if 'falha' in df else df
    return ok.sort_values(['familia', 'classe', 'rep']).reset_index(drop=True), falhas


def projecao(train):
    seed = int.from_bytes(hashlib.sha256(b'C02|2026101402|projecoes').digest()[:8], 'big')
    W = np.random.default_rng(seed).standard_normal((len(BASE14), 6))
    mu = train[BASE14].mean().to_numpy(); sd = train[BASE14].std(ddof=0).to_numpy()
    return {'W': W, 'mu': mu, 'sd': sd}


def matriz(df, braco, proj=None):
    if braco in ('base14', 'log_base14'):
        return df[BASE14].to_numpy()
    if braco in ('hdr6', 'log_hdr6'):
        return df[BASE14 + HDR6].to_numpy()
    if braco == 'hdr5_sem_w2':
        return df[BASE14 + HDR5].to_numpy()
    if braco == 'hdr6_env':
        return df[BASE14 + HDR6 + ['envelope_core_delta']].to_numpy()
    if braco == 'proj6':
        z = (df[BASE14].to_numpy() - proj['mu']) / proj['sd']
        return np.column_stack([df[BASE14].to_numpy(), z @ proj['W']])
    raise ValueError(braco)


BRACOS = ('base14', 'hdr6', 'log_base14', 'log_hdr6', 'proj6', 'hdr5_sem_w2', 'hdr6_env')


def ajustar(train):
    proj = projecao(train); y = train['classe'].to_numpy(); mods = {}
    for b in BRACOS:
        m = logit() if b.startswith('log_') else hgb()
        mods[b] = m.fit(matriz(train, b, proj), y)
    return mods, proj


def perdas(mods, proj, df):
    """Perda por par, ℓ = −log p̂(classe verdadeira), e probabilidades por braço."""
    y = df['classe'].to_numpy(); out, probs = {}, {}
    for b, m in mods.items():
        P = m.predict_proba(matriz(df, b, proj)); idx = {c: i for i, c in enumerate(m.classes_)}
        assert list(m.classes_) == CLASSES
        p_true = P[np.arange(len(y)), [idx[c] for c in y]]
        out[b] = -np.log(np.clip(p_true, EPS, 1.0)); probs[b] = P
    return out, probs


def metricas(df, ell, probs):
    y = df['classe'].to_numpy(); Y = (y[:, None] == np.array(CLASSES)[None, :]).astype(float); res = {}
    for b in ell:
        P = probs[b]; pred = np.array(CLASSES)[P.argmax(1)]; conf = P.max(1); acc = (pred == y).astype(float)
        bins = np.minimum((conf * 10).astype(int), 9)
        ece = float(sum(abs(acc[bins == k].mean() - conf[bins == k].mean()) * (bins == k).mean() for k in range(10) if (bins == k).any()))
        res[b] = {'log_loss': float(ell[b].mean()), 'balanced_accuracy': float(balanced_accuracy_score(y, pred)),
                  'macro_f1': float(f1_score(y, pred, average='macro')), 'brier': float(((P - Y) ** 2).sum(1).mean()), 'ece': ece,
                  'log_loss_por_familia': {f: float(ell[b][df['familia'].to_numpy() == f].mean()) for f in sorted(df['familia'].unique())},
                  'log_loss_por_classe': {c: float(ell[b][y == c].mean()) for c in CLASSES}}
    return res


def delta_ic(df, l_a, l_b, B=2000, seed=2026101403):
    """Delta = média de ℓ_a − ℓ_b; IC 95 % por bootstrap pareado estratificado (família × classe)."""
    d = l_a - l_b; estr = (df['familia'] + '|' + df['classe']).to_numpy()
    grupos = [np.where(estr == s)[0] for s in sorted(set(estr))]
    rng = np.random.default_rng(seed); boot = np.empty(B)
    for i in range(B):
        boot[i] = np.concatenate([d[rng.choice(g, len(g), replace=True)] for g in grupos]).mean()
    return {'delta': float(d.mean()), 'ic95': [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
            'n': int(len(d)), 'estratos': len(grupos)}


def contrastes(df, ell):
    return {'primario_hdr6_vs_base14': delta_ic(df, ell['base14'], ell['hdr6']),
            'logistica_hdr6_vs_base14': delta_ic(df, ell['log_base14'], ell['log_hdr6']),
            'controle_dimensao_proj6_vs_base14': delta_ic(df, ell['base14'], ell['proj6']),
            'hdr5_sem_w2_vs_base14': delta_ic(df, ell['base14'], ell['hdr5_sem_w2']),
            'envelope_hdr6env_vs_hdr6': delta_ic(df, ell['hdr6'], ell['hdr6_env'])}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validacao():
    train, ftr = carregar('pares_training.jsonl'); val, fva = carregar('pares_validation.jsonl')
    mods, proj = ajustar(train)
    ell, probs = perdas(mods, proj, val)
    res = {'n_treino_validos': len(train), 'treino_falhas': ftr[['familia', 'classe', 'rep', 'falha']].to_dict('records'),
           'n_validacao_validos': len(val), 'validacao_falhas': fva[['familia', 'classe', 'rep', 'falha']].to_dict('records'),
           'metricas_validacao': metricas(val, ell, probs), 'contrastes_validacao': contrastes(val, ell)}
    pickle.dump({'modelos': mods, 'projecao': proj}, open(DIR / 'modelos_congelados.pkl', 'wb'))
    json.dump(res, open(DIR / 'validacao.json', 'w'), indent=1, ensure_ascii=False)
    for b, m in res['metricas_validacao'].items():
        print(f"{b:12s} log-loss {m['log_loss']:.4f}  bal.acc {m['balanced_accuracy']:.3f}  macro-F1 {m['macro_f1']:.3f}  ECE {m['ece']:.3f}")
    for k, v in res['contrastes_validacao'].items():
        print(f"{k:36s} Δ {v['delta']:+.4f}  IC95 [{v['ic95'][0]:+.4f}, {v['ic95'][1]:+.4f}]  n={v['n']}")
    print('falhas: treino', len(ftr), 'validação', len(fva))


if __name__ == '__main__':
    if sys.argv[1:] == ['validacao']:
        validacao()
    else:
        sys.exit(__doc__)
