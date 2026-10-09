#!/usr/bin/env python3
"""Aggregate M15 shards strictly (one row per trial) and write the result tables."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from experiments.m15_forma_persistencia_comparadores import (
    TRUTHS,NULLS,STATS,SHARDS,PER_SHARD,TRIALS,aggregate)


def read(folder):
    folder=Path(folder);rows=[]
    for t in TRUTHS:
        for s in range(SHARDS[t]):
            p=folder/f'shard_{t}_{s:03d}.json'
            if not p.is_file():raise FileNotFoundError(f'Missing shard {p}')
            doc=json.loads(p.read_text())
            if doc.get('status')!='M15_SHARD' or doc.get('truth')!=t or doc.get('shard')!=s:
                raise ValueError(f'Bad shard metadata {p}')
            tr=doc['trials']
            if len(tr)!=PER_SHARD[t]:raise ValueError(f'Incomplete shard {p}')
            for r in tr:
                if not s*PER_SHARD[t]<=r['trial_id']<(s+1)*PER_SHARD[t]:
                    raise ValueError(f'Wrong trial mapping in {p}')
            rows.extend(tr)
    return rows


def pct(x):return '—' if x is None else f'{100*x:.1f}%'


def report(agg):
    L=['# SGV-M15 — Forma × persistência, com comparadores (resultados)','',
       '**Sintético, sem BTC.** Gerado automaticamente por `scripts/m15_agregar.py` a partir dos shards; '
       'protocolo e apostas congelados antes da execução em `reports/PROTOCOLO_SGV_M15_20261009.md`.','',
       '## Taxas de alarme (posto 1 de 20; nominal 5%)','',
       '| Verdade → nulo | M11 (cascas HDR50) | Fisher–Rao cov. | Energy distance |','|---|---|---|---|']
    for t in TRUTHS:
        for n in NULLS[t]:
            row=[f'{t} → {n}']
            for s in STATS:
                c=agg['cells'][f'{t}->{n}|{s}']
                w=c['wilson95'] or [None,None]
                row.append(f"{pct(c['alarm_rate'])} [{pct(w[0])}–{pct(w[1])}] (n={c['n_valid']})")
            L.append('| '+' | '.join(row)+' |')
    L+=['','## Contrastes pré-registrados (McNemar exato pareado, unilateral)','',
        '| Contraste | A | B | taxa A | taxa B | só A | só B | p | α | Significativo |','|---|---|---|---|---|---|---|---|---|---|']
    for k,v in agg['contrasts'].items():
        L.append(f"| {k} | {'/'.join(v['a'])} | {'/'.join(v['b'])} | {pct(v['rate_a'])} | {pct(v['rate_b'])} | "
                 f"{v['x_only']} | {v['y_only']} | {v['p_one_sided']:.2g} | {v['alpha']} | {'sim' if v['significant'] else 'não'} |")
    L+=['','## Histogramas de posto (posição 1 = observado acima de todas as 19 referências)','',
        'Plano ≈ calibrado; acúmulo à esquerda = nulo gera deformação de menos; à direita = de mais.','']
    for t in TRUTHS:
        for n in NULLS[t]:
            for s in STATS:
                c=agg['cells'][f'{t}->{n}|{s}']
                L.append(f"- `{t}→{n} | {s}`: {c['rank_histogram_pos1_is_extreme']}")
    L+=['','## Falhas de ajuste','',json.dumps(agg['fit_failures'],ensure_ascii=False),'']
    return '\n'.join(L)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--shards',required=True)
    ap.add_argument('--out',default='reports/m15')
    a=ap.parse_args()
    rows=read(a.shards)
    agg=aggregate(rows,TRIALS)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    (out/'SGV_M15_AGREGADO.json').write_text(json.dumps(agg,indent=1,ensure_ascii=False)+'\n')
    md=report(agg)
    (out/'SGV_M15_RESULTADOS.md').write_text(md+'\n')
    print(md)
