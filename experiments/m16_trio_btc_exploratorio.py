#!/usr/bin/env python3
"""SGV-M16: the three-ruler audit (M11 shells, Fisher-Rao covariance, energy)
applied to the M12 temporal nulls N0-N3 on EXPLORATORY BTC data only.

* Only archives accepted by ``checked_exploratory_month`` are read
  (1m 2026-05..07, 1h 2020-01..2024-12). Reserved months are never opened.
* Every eligible contiguous origin is used (no selection): prefix 5000/3500,
  window 1500/1008, origins stepping by one window (as M12/M13).
* Nulls are the unchanged M12 families, fitted ONLY on each origin's prefix.
* 39 references per null (rank position 1..40); "alarm" = p_rank <= 0.05,
  i.e. the observed value is above at least 38 of 39 references.
* The observed window and every reference go through ``all_stats`` from M15
  (same gaussianized halves for m11 / fr_cov / energy).
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.m5_validacao_conjunta_sf1 import WINDOW,STEP
from experiments.m12_nulos_regimes_temporais import PREFIX,MODELS,null_paths
from experiments.m13_calibracao_alarmes_regimes import mc_rank,wilson
from experiments.m15_forma_persistencia_comparadores import all_stats,mcnemar_exact,STATS

BASE_SEED=2026101016
REFS=39
INTERVALS=('1m','1h')
INTERVAL_ID={'1m':1,'1h':2}
PER_SHARD={'1m':4,'1h':3}
CORRECT_FAMILY_LEVEL=.07   # M14/M15: fitted correct-family alarm level of m11 at nominal 5%
ALPHA_CLASS=.05/8          # 4 nulls x 2 intervals
EXPECTED_ORIGINS={'1m':84,'1h':18}   # all eligible contiguous origins in the approved archives


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


def load(interval):
    paths=sorted((ROOT/'data').glob(f'BTCUSDT-{interval}-*.zip'))
    if not paths:raise FileNotFoundError('Exploratory archives missing (scripts/baixar_klines.py --so)')
    for p in paths:checked_exploratory_month(p.name,interval)
    df=load_binance_klines(paths,with_flow=True)
    pre=PREFIX[interval];w=WINDOW[interval];step=STEP[interval]
    ts=df.timestamp.to_numpy(np.int64)
    starts=[i for i in range(pre,len(df)-w+1,w) if np.all(np.diff(ts[i-pre:i+w])==step)]
    if not starts:raise RuntimeError('No contiguous exploratory origins')
    if len(starts)!=EXPECTED_ORIGINS[interval]:
        raise RuntimeError(f'Origin count changed: {len(starts)} != {EXPECTED_ORIGINS[interval]}')
    return df,starts


def n_shards(n_origins,interval):
    return (n_origins+PER_SHARD[interval]-1)//PER_SHARD[interval]


def run_origin(df,start,interval,k,refs=REFS,stats_fn=all_stats):
    pre=PREFIX[interval];w=WINDOW[interval]
    prefix=df.iloc[start-pre:start].copy();future=df.iloc[start:start+w].copy()
    combined=pd.concat([prefix,future],ignore_index=True)
    actual=flow_coordinates(combined)[['z','iota','nu']].to_numpy(float)[-w:]
    item={'interval':interval,'origin':int(k),'start_index':int(start),
          'window_start_ms':int(future.timestamp.iloc[0]),
          'window_end_ms':int(future.timestamp.iloc[-1]),
          'fit_uses_prefix_only':True,'models':{}}
    if not np.isfinite(actual).all():
        item['status']='invalid_observed_coordinates';return item
    obs=stats_fn(actual,seed_int(INTERVAL_ID[interval],k,1))
    item['observed']=obs
    try:
        draw,fit,_=null_paths(prefix,interval,seed_int(INTERVAL_ID[interval],k,2))
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
        item['status']='fit_failed';item['error']=str(e);return item
    item['status']='valid'
    for mi,name in enumerate(MODELS):
        ref={s:[] for s in STATS};fails=[]
        for j in range(refs):
            try:
                sim,_=draw(name,j)
                if not np.isfinite(sim).all():raise ValueError('nonfinite simulated coordinates')
                r=stats_fn(sim,seed_int(INTERVAL_ID[interval],k,3,mi,j))
            except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
                r={s:None for s in STATS};fails.append({'ref':j,'error':str(e)})
            for s in STATS:ref[s].append(r[s])
        rec={'references':ref,'failures':fails}
        for s in STATS:
            vals=ref[s]
            if obs[s] is None or any(v is None for v in vals):
                rec[s]={'valid':False,'n_ref_valid':int(sum(v is not None for v in vals))}
                continue
            p=mc_rank(obs[s],vals,min_reference=refs)
            rec[s]={'valid':True,'p_rank':p,'rank_position':int(round(p*(refs+1))),
                    'alarm':bool(p<=.05)}
        item['models'][name]=rec
    return item


# ------------------------------------------------------------------ aggregate
def cell(rows,interval,model,stat):
    ok=[r['models'][model][stat] for r in rows
        if r['interval']==interval and r.get('status')=='valid'
        and r['models'].get(model,{}).get(stat,{}).get('valid')]
    n=len(ok);al=sum(o['alarm'] for o in ok)
    bins=[0]*8
    for o in ok:bins[min(7,(o['rank_position']-1)//5)]+=1
    return {'n_valid':n,'alarms':int(al),'alarm_rate':al/n if n else None,
            'wilson95':wilson(al,n),
            'rank_bins_of5_pos1_extreme':bins,
            'mean_pit':float(np.mean([o['p_rank'] for o in ok])) if n else None}


def classify(rows,interval,model):
    xa=[];xb=[]
    for r in rows:
        if r['interval']!=interval or r.get('status')!='valid':continue
        m=r['models'].get(model,{})
        if m.get('m11',{}).get('valid') and m.get('energy',{}).get('valid'):
            xa.append(m['m11']['alarm']);xb.append(m['energy']['alarm'])
    m_gt=mcnemar_exact(xa,xb);e_gt=mcnemar_exact(xb,xa)
    cells={s:cell(rows,interval,model,s) for s in STATS}
    elevated=[s for s in STATS if cells[s]['wilson95'] and cells[s]['wilson95'][0]>CORRECT_FAMILY_LEVEL]
    if m_gt['p_one_sided']<ALPHA_CLASS/2:label='falta forma (m11 > energy)'
    elif e_gt['p_one_sided']<ALPHA_CLASS/2:label='falta memoria/massa (energy > m11)'
    elif elevated:label='inadequado, tipo indefinido'
    else:label='sem evidencia de inadequacao nas tres reguas'
    return {'label':label,'elevated_stats':elevated,
            'mcnemar_m11_gt_energy':m_gt,'mcnemar_energy_gt_m11':e_gt,
            'two_sided_alpha':ALPHA_CLASS,'n_pairs':len(xa)}


def aggregate(rows,expected):
    for interval,n in expected.items():
        ids=sorted(r['origin'] for r in rows if r['interval']==interval)
        if ids!=list(range(n)):raise ValueError(f'Missing or duplicate origins for {interval}')
    out={'cells':{},'classification':{},'origin_status':{}}
    for interval in expected:
        out['origin_status'][interval]={st:sum(1 for r in rows if r['interval']==interval and r.get('status')==st)
                                        for st in {r.get('status') for r in rows if r['interval']==interval}}
        for model in MODELS:
            for s in STATS:
                out['cells'][f'{interval}|{model}|{s}']=cell(rows,interval,model,s)
            out['classification'][f'{interval}|{model}']=classify(rows,interval,model)
    out['alarm_timeline']=[{'interval':r['interval'],'origin':r['origin'],
        'window_start':pd.to_datetime(r['window_start_ms'],unit='ms').isoformat(),
        'window_end':pd.to_datetime(r['window_end_ms'],unit='ms').isoformat(),
        'alarms':{m:[s for s in STATS if r['models'][m].get(s,{}).get('alarm')] for m in MODELS}}
        for r in rows if r.get('status')=='valid']
    return out


# ----------------------------------------------------------------------- I/O
def write(obj,name):
    p=ROOT/'reports'/'m16'/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n')
    return p


def run_plan():
    plan={}
    for interval in INTERVALS:
        _,starts=load(interval)
        plan[interval]={'n_origins':len(starts),'n_shards':n_shards(len(starts),interval)}
    write(plan,'plan.json');print(json.dumps(plan))


def run_pilot():
    """Engineering gate: first origin of each interval with 2 refs; ranks not read."""
    bad=[]
    for interval in INTERVALS:
        df,starts=load(interval)
        r=run_origin(df,starts[0],interval,0,refs=2)
        if r.get('status')!='valid':bad.append((interval,r.get('status'),r.get('error')))
        else:
            for s in STATS:
                if r['observed'][s] is None:bad.append((interval,'observed',s))
            for m,v in r['models'].items():
                for s in STATS:
                    if any(x is None for x in v['references'][s]):bad.append((interval,m,s))
    write({'status':'M16_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad}))
    if bad:raise RuntimeError('Pilot failed')


def run_shard(interval,shard):
    df,starts=load(interval)
    per=PER_SHARD[interval]
    ks=range(shard*per,min(len(starts),(shard+1)*per))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],interval,k) for k in ks]
    write({'status':'M16_SHARD','interval':interval,'shard':shard,'n_origins_total':len(starts),
           'confirmatory_opened':False,'origins':rows},f'shard_{interval}_{shard:03d}.json')
    print(json.dumps({'interval':interval,'shard':shard,'n':len(rows)}))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('plan','pilot','shard'),required=True)
    ap.add_argument('--interval',choices=INTERVALS)
    ap.add_argument('--shard',type=int)
    a=ap.parse_args()
    if a.mode=='plan':run_plan()
    elif a.mode=='pilot':run_pilot()
    else:run_shard(a.interval,a.shard)


if __name__=='__main__':main()
