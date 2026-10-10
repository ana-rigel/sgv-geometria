#!/usr/bin/env python3
"""Aggregate M17 shards strictly and write the result tables."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from experiments.m17_tipo_de_memoria import INTERVALS,PER_SHARD,NULLS,STATS,CONTRASTS,n_shards,aggregate
from experiments.m16_trio_btc_exploratorio import EXPECTED_ORIGINS

DESC={'H2':'HMM 2 estados','H4':'HMM 4 estados','MS':'2 escalas, Markov','MSSM':'2 escalas, semi-Markov',
      'MSR':'2 escalas, Markov + relógio','MSSMR':'2 escalas, semi-Markov + relógio','N3':'M12 N3 (âncora)'}


def read(folder):
    rows=[]
    for iv in INTERVALS:
        for s in range(n_shards(EXPECTED_ORIGINS[iv],iv)):
            p=Path(folder)/f'shard_{iv}_{s:03d}.json'
            if not p.is_file():raise FileNotFoundError(f'Missing shard {p}')
            d=json.loads(p.read_text())
            if d.get('status')!='M17_SHARD' or d.get('interval')!=iv or d.get('shard')!=s \
               or d.get('n_origins_total')!=EXPECTED_ORIGINS[iv] or d.get('confirmatory_opened') is not False:
                raise ValueError(f'Bad shard metadata {p}')
            for r in d['origins']:
                if not s*PER_SHARD[iv]<=r['origin']<(s+1)*PER_SHARD[iv]:raise ValueError(f'Wrong mapping {p}')
            rows+=d['origins']
    return rows


def pct(x):return '—' if x is None else f'{100*x:.1f}%'


def report(a):
    L=['# SGV-M17 — Que tipo de memória o BTC tem? (resultados)','',
       '**Somente dados exploratórios.** Gerado por `scripts/m17_agregar.py`; protocolo e apostas congelados antes em '
       '`reports/PROTOCOLO_SGV_M17_20261010.md`. Origens consecutivas não são independentes (Wilson otimista).','']
    for iv in INTERVALS:
        L+=[f'## {iv} (origens: {a["status"][iv]})','','| Nulo | M11 (forma) | Fisher–Rao | Energy (memória) | Fecha a lacuna? |','|---|---|---|---|---|']
        for m in NULLS:
            row=[f'{m} — {DESC[m]}']
            for s in STATS:
                c=a['cells'][f'{iv}|{m}|{s}'];w=c['wilson95'] or [None,None]
                row.append(f"{pct(c['alarm_rate'])} [{pct(w[0])}–{pct(w[1])}] ({c['alarms']}/{c['n_valid']})")
            row.append('**sim**' if a['closes_gap'][f'{iv}|{m}'] else 'não')
            L.append('| '+' | '.join(row)+' |')
        L+=['','Contrastes pré-registrados (régua energy, McNemar exato pareado unilateral, α = 0,01 cada):','',
            '| Contraste | A | B | taxa A | taxa B | só A | só B | p | Significativo |','|---|---|---|---|---|---|---|---|---|']
        for name,_,_ in CONTRASTS:
            c=a['contrasts'][f'{iv}|{name}']
            ra=a['cells'][f"{iv}|{c['a']}|energy"]['alarm_rate'];rb=a['cells'][f"{iv}|{c['b']}|energy"]['alarm_rate']
            L.append(f"| {name} | {c['a']} | {c['b']} | {pct(ra)} | {pct(rb)} | {c['x_only']} | {c['y_only']} | {c['p_one_sided']:.2g} | {'sim' if c['significant'] else 'não'} |")
        L+=['','Diagnósticos de ajuste (descritivos):','','```',json.dumps(a['diagnostics'][iv],indent=1,ensure_ascii=False),'```','']
    return '\n'.join(L)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--shards',required=True);ap.add_argument('--out',default='reports/m17')
    x=ap.parse_args();rows=read(x.shards);agg=aggregate(rows,EXPECTED_ORIGINS)
    out=Path(x.out);out.mkdir(parents=True,exist_ok=True)
    (out/'SGV_M17_AGREGADO.json').write_text(json.dumps(agg,indent=1,ensure_ascii=False)+'\n')
    md=report(agg);(out/'SGV_M17_RESULTADOS.md').write_text(md+'\n');print(md)
