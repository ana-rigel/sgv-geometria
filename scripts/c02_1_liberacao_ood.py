"""SGV-C02.1 — LIBERAÇÃO ÚNICA da OOD (490 pares R7/BS35) e julgamento do endpoint primário. Plano §1, §5.

Confere os hashes do congelamento antes de gerar qualquer par. A extração pode retomar o mesmo .jsonl se o processo
cair (a geração é determinística e nenhum resultado é calculado antes do fim). Recusa julgar de novo se o resultado existir.

    python scripts/c02_1_liberacao_ood.py
"""
import hashlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DIR = ROOT / 'reports' / 'c02_1'
CONG = DIR / 'CONGELAMENTO.sha256'
SAIDA = DIR / 'resultado_ood.json'


def conferir_congelamento():
    if not CONG.exists():
        sys.exit('sem congelamento: a OOD não pode ser liberada')
    for linha in CONG.read_text().splitlines():
        h, nome = linha.split(maxsplit=1)
        if hashlib.sha256((ROOT / nome.strip()).read_bytes()).hexdigest() != h:
            sys.exit(f'hash não confere: {nome}')
    print('congelamento conferido:', len(CONG.read_text().splitlines()), 'arquivos', flush=True)


def main():
    if SAIDA.exists():
        sys.exit('resultado_ood.json já existe: a OOD é julgada uma única vez')
    conferir_congelamento()
    from experiments.c02_1_pares import extrair
    from experiments.c02_1_modelos import carregar, contrastes, metricas, perdas
    extrair('ood_test', 35, DIR / 'pares_ood_test.jsonl')
    ood, falhas = carregar('pares_ood_test.jsonl')
    cont = ood.groupby(['familia', 'classe']).size()
    estratos = {f'{f}|{c}': int(cont.get((f, c), 0)) for f in ('BS35', 'R7') for c in [f'T{i}' for i in range(7)]}
    valido = all(v >= 34 for v in estratos.values())
    res = {'n_validos': len(ood), 'falhas': falhas[['familia', 'classe', 'rep', 'falha']].to_dict('records'),
           'validos_por_estrato': estratos, 'gate_validade_34_de_35': valido}
    if valido:
        cg = pickle.load(open(DIR / 'modelos_congelados.pkl', 'rb'))
        ell, probs = perdas(cg['modelos'], cg['projecao'], ood)
        res['metricas_ood'] = metricas(ood, ell, probs)
        res['contrastes_ood'] = contrastes(ood, ell)
        for fam in ('BS35', 'R7'):
            m = (ood['familia'] == fam).to_numpy()
            res[f'contrastes_{fam}'] = contrastes(ood[m].reset_index(drop=True), {k: v[m] for k, v in ell.items()})
        p = res['contrastes_ood']['primario_hdr6_vs_base14']
        res['veredito'] = 'SUCESSO' if (p['delta'] >= 0.03 and p['ic95'][0] > 0) else 'FALHA'
        np.save(DIR / 'perdas_ood.npy', np.column_stack([ell[b] for b in sorted(ell)]))
        res['perdas_ood_colunas'] = sorted(ell)
    else:
        res['veredito'] = 'INCONCLUSIVO'
    json.dump(res, open(SAIDA, 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k not in ('metricas_ood',)}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
