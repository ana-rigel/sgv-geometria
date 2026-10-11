#!/usr/bin/env python3
"""SGV-M21b: does exploratory BTC (1m) carry temporal dependence between x_t and
x_{t+k} that the best parametric model of M18 does not reproduce? And of which
kind -- linear, volatility memory, or general nonlinear (the M20 kind)?

Per window (1500 bars) the three coordinates are rank-gaussianized INSIDE the
window (copula level: marginal shape removed). For lags k in (1, 5, 30):
  lin_k  : Frobenius norm of the 3x3 lag-k cross-covariance          (linear)
  vol_k  : same on |x| (centered)                                     (volatility memory)
  hsic_k : Gaussian-kernel HSIC between x_t and x_{t+k} in R^3,
           median-heuristic bandwidth, rotation invariant             (any dependence)
Nulls fitted on each origin's prefix only: MS and MSDCCLM (M18) and BL (real
8h blocks, sanity reference: preserves short-lag dependence by construction).
39 references, conservative rank (M21a), alarm p<=0.05.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import ndtri
from scipy.stats import rankdata
from scipy.spatial.distance import cdist
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates
from experiments.precisao_formas_3d import gaussianize_three
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m5_validacao_conjunta_sf1 import WINDOW
from experiments.m12_nulos_regimes_temporais import PREFIX
from experiments.m13_calibracao_alarmes_regimes import wilson
from experiments.m15_forma_persistencia_comparadores import mcnemar_exact
from experiments.m16_trio_btc_exploratorio import load,EXPECTED_ORIGINS,CORRECT_FAMILY_LEVEL
from experiments.m18_acoplamento_dinamico import two_scale_plus,LONG_BLOCK
from experiments.m21_posto_conservador import conservative_rank

BASE_SEED=2026101121
REFS=39
LAGS=(1,5,30)
NULLS=('MS','MSDCCLM','BL')
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
KINDS=('lin','vol','hsic')
STATS=tuple(f'{k}_{l}' for k in KINDS for l in LAGS)
PER_SHARD=4
INTERVAL='1m'
ALPHA=.05/len(LAGS)


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


def copula(x):
    x=np.asarray(x,float);n=len(x)
    return np.column_stack([ndtri(rankdata(x[:,j])/(n+1)) for j in range(3)])


def lagcov(a,b):
    a=a-a.mean(0);b=b-b.mean(0);return float(np.linalg.norm(a.T@b/len(a)))


def hsic(a,b):
    n=len(a)
    def K(z):
        d=cdist(z,z,'sqeuclidean');s=np.median(d[d>0]);k=np.exp(-d/s)
        return k-k.mean(0)-k.mean(1)[:,None]+k.mean()
    return float(np.sum(K(a)*K(b))/n**2)


def dep_stats(x):
    u=copula(x);out={}
    for l in LAGS:
        a,b=u[:-l],u[l:]
        out[f'lin_{l}']=lagcov(a,b)
        out[f'vol_{l}']=lagcov(np.abs(a),np.abs(b))
        out[f'hsic_{l}']=hsic(a,b)
    return out


def build(prefix_df,seed):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ok=np.isfinite(pre).all(axis=1)
    raw=pre[int(np.flatnonzero(ok)[0]):]
    if len(raw)<2000 or not np.isfinite(raw).all():raise ValueError('Prefix coordinates invalid')
    ns=gaussianize_three(raw,raw)
    s={}
    s['MS'],_=two_scale_plus(ns,INTERVAL,seed+50)
    s['MSDCCLM'],_=two_scale_plus(ns,INTERVAL,seed+50,dcc=True,lm=True)
    s['BL']=lambda rng,n:circular_blocks(raw,rng,LONG_BLOCK[INTERVAL])[:n]
    return s


def run_origin(df,start,k,refs=REFS,stats_fn=dep_stats):
    pre=PREFIX[INTERVAL];w=WINDOW[INTERVAL]
    prefix=df.iloc[start-pre:start].copy();fut=df.iloc[start:start+w].copy()
    actual=flow_coordinates(pd.concat([prefix,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-w:]
    item={'origin':int(k),'window_start_ms':int(fut.timestamp.iloc[0]),'models':{}}
    if not np.isfinite(actual).all():item['status']='invalid_observed';return item
    obs=stats_fn(actual);item['observed']=obs
    try:samplers=build(prefix,seed_int(k,2))
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
        item['status']='fit_failed';item['error']=str(e);return item
    item['status']='valid'
    for name in NULLS:
        ref={s:[] for s in STATS}
        for j in range(refs):
            try:
                sim=samplers[name](np.random.default_rng(seed_int(k,3,NULL_ID[name],j)),w)
                if sim.shape!=(w,3) or not np.isfinite(sim).all():raise ValueError('bad window')
                r=stats_fn(sim)
            except (ValueError,RuntimeError,np.linalg.LinAlgError):
                r={s:None for s in STATS}
            for s in STATS:ref[s].append(r[s])
        rec={'references':ref}
        for s in STATS:
            p=conservative_rank(obs[s],ref[s])
            rec[s]={'p_rank':p,'alarm':bool(p is not None and p<=.05)}
        item['models'][name]=rec
    return item


# ------------------------------------------------------------------ aggregate
def aggregate(rows,n_expected):
    ids=sorted(r['origin'] for r in rows)
    if ids!=list(range(n_expected)):raise ValueError('Missing or duplicate origins')
    val=[r for r in rows if r.get('status')=='valid']
    cells={}
    for m in NULLS:
        for s in STATS:
            al=[r['models'][m][s]['alarm'] for r in val if r['models'][m][s]['p_rank'] is not None]
            k=int(sum(al));n=len(al)
            cells[f'{m}|{s}']={'alarms':k,'n':n,'rate':k/n if n else None,'wilson95':wilson(k,n),
                               'elevated':bool(n and wilson(k,n)[0]>CORRECT_FAMILY_LEVEL)}
    def pair(a,b):
        xa=[];xb=[]
        for r in val:
            pa=r['models'][a[0]][a[1]];pb=r['models'][b[0]][b[1]]
            if pa['p_rank'] is not None and pb['p_rank'] is not None:
                xa.append(pa['alarm']);xb.append(pb['alarm'])
        res=mcnemar_exact(xa,xb);res['significant']=bool(res['p_one_sided']<ALPHA);return res
    contrasts={}
    for l in LAGS:
        contrasts[f'P1_param_vs_BL_hsic_{l}']=pair(('MSDCCLM',f'hsic_{l}'),('BL',f'hsic_{l}'))
        contrasts[f'P2_hsic_beyond_vol_{l}']=pair(('MSDCCLM',f'hsic_{l}'),('MSDCCLM',f'vol_{l}'))
        contrasts[f'P2_hsic_beyond_lin_{l}']=pair(('MSDCCLM',f'hsic_{l}'),('MSDCCLM',f'lin_{l}'))
    verdict={}
    for l in LAGS:
        h=cells[f'MSDCCLM|hsic_{l}']['elevated'];v=cells[f'MSDCCLM|vol_{l}']['elevated'];li=cells[f'MSDCCLM|lin_{l}']['elevated']
        bl_ok=not cells[f'BL|hsic_{l}']['elevated']
        if not h:lab='sem dependencia nao reproduzida pelo modelo'
        elif h and not v and not li and contrasts[f'P2_hsic_beyond_vol_{l}']['significant'] and contrasts[f'P2_hsic_beyond_lin_{l}']['significant']:
            lab='dependencia nao linear alem da 2a ordem e da volatilidade (tipo M20)'
        elif h and v:lab='dependencia nao reproduzida, compativel com memoria de volatilidade'
        else:lab='dependencia nao reproduzida, tipo indefinido'
        verdict[str(l)]={'label':lab,'BL_sanity_ok':bl_ok}
    return {'n_valid':len(val),'status':{s:sum(1 for r in rows if r.get('status')==s) for s in {r.get('status') for r in rows}},
            'cells':cells,'contrasts':contrasts,'verdict':verdict}


def report(a):
    pct=lambda x:'—' if x is None else f'{100*x:.1f}%'
    L=['# SGV-M21b — Dependência temporal no BTC 1m exploratório (resultados)','',
       f"Origens válidas: {a['n_valid']} ({a['status']}). Gerado por `scripts/m21b_agregar.py`; protocolo em `reports/PROTOCOLO_SGV_M21b_20261011.md`.",'',
       '| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:
        L.append(f'| {m} | '+' | '.join(f"{pct(a['cells'][f'{m}|{s}']['rate'])}" for s in STATS)+' |')
    L+=['','| Contraste | só A | só B | p | sig. (α=0,0167) |','|---|---|---|---|---|']
    for k,v in a['contrasts'].items():
        L.append(f"| {k} | {v['x_only']} | {v['y_only']} | {v['p_one_sided']:.2g} | {'sim' if v['significant'] else 'não'} |")
    L+=['','**Veredito pré-registrado por defasagem:**','']
    for l,v in a['verdict'].items():L.append(f"- lag {l}: **{v['label']}** (sanidade BL: {'ok' if v['BL_sanity_ok'] else 'FALHOU'})")
    return '\n'.join(L)


def write(obj,name):
    p=ROOT/'reports'/'m21b'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n');return p


def run_shard(shard):
    df,starts=load(INTERVAL)
    ks=range(shard*PER_SHARD,min(len(starts),(shard+1)*PER_SHARD))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],k) for k in ks]
    write({'status':'M21b_SHARD','shard':shard,'n_origins_total':len(starts),'origins':rows},f'shard_{shard:02d}.json')
    print(json.dumps({'shard':shard,'n':len(rows)}))


def run_pilot():
    df,starts=load(INTERVAL)
    r=run_origin(df,starts[0],0,refs=2)
    bad=[] if r.get('status')=='valid' else [r.get('status'),r.get('error')]
    if not bad:
        for m,v in r['models'].items():
            for s in STATS:
                if any(x is None for x in v['references'][s]):bad.append((m,s))
    write({'status':'M21b_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad}))
    if bad:raise RuntimeError('Pilot failed')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('pilot','shard','aggregate'),required=True)
    ap.add_argument('--shard',type=int);ap.add_argument('--shards-dir',default=str(ROOT/'reports'/'m21b'/'_dl'))
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    elif a.mode=='shard':run_shard(a.shard)
    else:
        rows=[];n=EXPECTED_ORIGINS[INTERVAL];ns=(n+PER_SHARD-1)//PER_SHARD
        for s in range(ns):
            d=json.loads((Path(a.shards_dir)/f'shard_{s:02d}.json').read_text())
            if d.get('shard')!=s or d.get('n_origins_total')!=n:raise ValueError('bad shard')
            rows+=d['origins']
        agg=aggregate(rows,n);write(agg,'SGV_M21b_AGREGADO.json')
        md=report(agg);(ROOT/'reports'/'m21b'/'SGV_M21b_RESULTADOS.md').write_text(md+'\n');print(md)


if __name__=='__main__':main()
