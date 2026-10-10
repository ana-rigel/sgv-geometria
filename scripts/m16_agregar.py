#!/usr/bin/env python3
"""Aggregate M16 shards strictly and write the result tables."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from experiments.m16_trio_btc_exploratorio import (
    INTERVALS,EXPECTED_ORIGINS,PER_SHARD,MODELS,STATS,n_shards,aggregate)


def read(folder):
    rows=[]
    for iv in INTERVALS:
        for s in range(n_shards(EXPECTED_ORIGINS[iv],iv)):
            p=Path(folder)/f'shard_{iv}_{s:03d}.json'
            if not p.is_file():raise FileNotFoundError(f'Missing shard {p}')
            d=json.loads(p.read_text())
            if d.get('status')!='M16_SHARD' or d.get('interval')!=iv or d.get('shard')!=s \
               or d.get('n_origins_total')!=EXPECTED_ORIGINS[iv] or d.get('confirmatory_opened') is not False:
                raise ValueError(f'Bad shard metadata {p}')
            for r in d['origins']:
                if not s*PER_SHARD[iv]<=r['origin']<(s+1)*PER_SHARD[iv]:raise ValueError(f'Wrong mapping {p}')
            rows+=d['origins']
    return rows


def pct(x):return '—' if x is None else f'{100*x:.1f}%'


def report(a):
    L=['# SGV-M16 — Três réguas sobre os nulos N0–N3 no BTC exploratório (resultados)','',
       '**Somente dados exploratórios** (1m mai–jul/2026; 1h 2020–2024). Gerado por `scripts/m16_agregar.py`; '
       'protocolo e apostas congelados antes em `reports/PROTOCOLO_SGV_M16_20261010.md`.','',
       'Alarme = observado acima de ≥38 das 39 referências (nominal 5%; sob família correta ajustada o M11 dá ~7%, M14/M15). '
       '**Origens consecutivas não são independentes: os intervalos de Wilson são otimistas.**','']
    for iv in INTERVALS:
        L+=[f'## {iv}  (origens: {a["origin_status"][iv]})','',
            '| Nulo | M11 (forma) | Fisher–Rao cov. | Energy | Classificação pré-registrada |','|---|---|---|---|---|']
        for mo in MODELS:
            row=[mo]
            for s in STATS:
                c=a['cells'][f'{iv}|{mo}|{s}'];w=c['wilson95'] or [None,None]
                row.append(f"{pct(c['alarm_rate'])} [{pct(w[0])}–{pct(w[1])}] ({c['alarms']}/{c['n_valid']})")
            cl=a['classification'][f'{iv}|{mo}']
            row.append(f"**{cl['label']}** (m11>E p={cl['mcnemar_m11_gt_energy']['p_one_sided']:.2g}; "
                       f"E>m11 p={cl['mcnemar_energy_gt_m11']['p_one_sided']:.2g})")
            L.append('| '+' | '.join(row)+' |')
        L+=['','Postos em 8 faixas de 5 posições (faixa 1 = observado no topo; plano ≈ adequado):','']
        for mo in MODELS:
            for s in STATS:
                c=a['cells'][f'{iv}|{mo}|{s}']
                L.append(f"- `{mo} | {s}`: {c['rank_bins_of5_pos1_extreme']} (PIT médio {c['mean_pit']:.2f})" if c['mean_pit'] is not None else f"- `{mo} | {s}`: —")
        L.append('')
    L+=['## Linha do tempo dos alarmes (exploração descritiva, sem teste)','',
        '| Intervalo | Origem | Janela | Alarmes (nulo: réguas) |','|---|---|---|---|']
    for t in a['alarm_timeline']:
        al='; '.join(f"{k}: {','.join(v)}" for k,v in t['alarms'].items() if v) or '—'
        L.append(f"| {t['interval']} | {t['origin']} | {t['window_start'][:16]} → {t['window_end'][:16]} | {al} |")
    return '\n'.join(L)


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--shards',required=True);ap.add_argument('--out',default='reports/m16')
    x=ap.parse_args()
    rows=read(x.shards)
    agg=aggregate(rows,EXPECTED_ORIGINS)
    out=Path(x.out);out.mkdir(parents=True,exist_ok=True)
    (out/'SGV_M16_AGREGADO.json').write_text(json.dumps(agg,indent=1,ensure_ascii=False)+'\n')
    md=report(agg);(out/'SGV_M16_RESULTADOS.md').write_text(md+'\n');print(md)
