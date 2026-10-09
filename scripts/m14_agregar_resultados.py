#!/usr/bin/env python3
"""Aggregate independent M14 shards strictly: one and only one row per trial."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from experiments.m14_calibracao_aninhada import SCENARIOS,SHARDS,PER_SHARD,aggregate


def read_shards(folder):
    folder=Path(folder)
    result={}
    for scenario in SCENARIOS:
        group=[];covered_shards=[]
        for shard in range(SHARDS):
            p=folder/f'SGV_M14_{scenario}_shard{shard:02d}.json'
            if not p.is_file():raise FileNotFoundError(f'Missing job artifact {p}')
            doc=json.loads(p.read_text())
            if (doc.get('status')!='M14_SHARD' or doc.get('scenario')!=scenario
                or doc.get('shard')!=shard
                or doc.get('n_references_each')!=19):
                raise ValueError(f'Invalid shard metadata {p}')
            rows=doc['trials']
            if len(rows)!=PER_SHARD:raise ValueError(f'Incomplete shard {p}')
            for row in rows:
                if row['scenario']!=scenario:raise ValueError(f'Wrong scenario in {p}')
                if not shard*PER_SHARD<=row['trial_id']<(shard+1)*PER_SHARD:
                    raise ValueError(f'Wrong trial mapping in {p}')
            group.extend(rows);covered_shards.append(shard)
        ids=[x['trial_id'] for x in group]
        if sorted(ids)!=list(range(SHARDS*PER_SHARD)):
            raise ValueError(f'Missing or duplicate trial IDs for {scenario}')
        result[scenario]={'summary':aggregate(group,SHARDS*PER_SHARD),
                          'shards_verified':covered_shards,
                          'failures':[x for x in group if x['status']!='valid']}
    return result


def write_report(folder,destination):
    cases=read_shards(folder)
    out=Path(destination)
    out.mkdir(parents=True,exist_ok=True)
    doc={'status':'M14_NESTED_CALIBRATION','scenarios':cases,
         'interpretation':{
         'VAR_fit':'Correct Gaussian VAR family; observed rate diagnoses estimation/conditional initialization effects.',
         'HMM_fit':'Correct two-state Gaussian HMM family; observed rate diagnoses estimation, EM failures, and initialization effects.',
         'HMM_to_VAR':'Regime truth vs insufficient VAR; exceeded ranks indicate model inadequacy, not necessarily type-I error under a true VAR null.',
         'HMM_to_blocks':'Regime truth vs short-block bootstrap; exceeded ranks indicate model inadequacy, not necessarily type-I error under a true short-block null.'},
         'no_btc_used':True,
         'instrument':'Exactly M11 HDR50 GMM2 ICP direct point-to-triangle distance with 512 quadrature points',
         'limits':['500 independent outer trials per scenario, 19 refs each',
                   'Rates are specific to these simulated truth generators and estimator choices',
                   'Failure exclusion can induce selection; report full failure bounds',
                   'Market inference needs an adequate fitted null and selection calibration',
                   'No physical law or market-stress interpretation']}
    (out/'SGV_M14_AGREGADO.json').write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n')
    with (out/'SGV_M14_TAXAS.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=['scenario','n_requested','n_valid','n_invalid',
              'alarms','alarm_rate','wilson_low','wilson_high','unconditional_lower',
              'unconditional_upper'])
        w.writeheader()
        for name,record in cases.items():
            x=record['summary']
            ci=x['wilson95'] or [None,None]
            w.writerow({'scenario':name,
                **{k:x[k] for k in ('n_requested','n_valid','n_invalid','alarms','alarm_rate')},
                'wilson_low':ci[0],'wilson_high':ci[1],
                'unconditional_lower':x['failure_bounds_unconditional'][0],
                'unconditional_upper':x['failure_bounds_unconditional'][1]})
    lines=['# SGV-M14 — Calibração aninhada dos alarmes geométricos',
           '', '**Experimento sintético, sem abrir dados BTC.** Geradores conhecidos fixos, prefixo reestimado em cada ensaio externo. As 20 trajetórias de cada ensaio passam pelo mesmo instrumento M11.','','| Verdade → nulo ajustado | Ensaios válidos | Alarmes | Taxa | IC Wilson 95% | Falhas |',
           '|---|---:|---:|---:|---|---:|']
    for name,record in cases.items():
        x=record['summary'];ci=x['wilson95']
        lines.append(f"| {name} | {x['n_valid']}/500 | {x['alarms']} | "
                     f"{100*x['alarm_rate']:.2f}% | "
                     f"[{100*ci[0]:.2f}%, {100*ci[1]:.2f}%] | {x['n_invalid']} |")
    lines.extend(['','A taxa estimada depende desta família geradora, sua calibração por prefixo, inicialização e erro de estimação GMM/ICP. Modelos errados não possuem garantias de nível nominal. Nenhuma excedência no BTC implica tensão financeira por si só.',
                  '', '**Falhas:** em cada cenário ver SGV_M14_AGREGADO.json, que informa quantos ensaios foram descartados e limites de taxa sem assumir comportamento benigno dessas falhas.',
                  '', '**Integridade:** exatamente 500 IDs independentes por cenário, 20 shards disjuntos de 25 ensaios; nenhum uso de main ou meses confirmatórios.'])
    (out/'SGV_M14_RESULTADOS.md').write_text('\n'.join(lines)+'\n')
    print((out/'SGV_M14_RESULTADOS.md').read_text())
    return cases


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--shards',required=True)
    ap.add_argument('--out',default='reports/m14_agregado')
    a=ap.parse_args()
    write_report(a.shards,a.out)
