#!/usr/bin/env python3
"""SGV-M29: the volume clock (protocol reports/PROTOCOLO_SGV_M29_20261012.md).

HXCLK = M28's HXACT + a minute-of-hour profile in the volume coordinate:
  profile = per-minute-of-hour mean of (nu - slow block - centered 60-min moving
  average) in the prefix, centered, positive-part James-Stein shrinkage.
The profile is removed before the local fits and re-added INSIDE the simulation
(together with the real slow block) at the minute-of-hour of the real future
window, so the M28 activity factor also sees the clock.
Nulls: HXCLK, HXACT (M28), BL. Primary on ODD origins.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binomtest
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
from experiments.m17_tipo_de_memoria import SMOOTH
from experiments.m18_acoplamento_dinamico import LONG_BLOCK
from experiments.m21_posto_conservador import conservative_rank
from experiments.m23_modelo_minimo import slow_layer,full_stats,STATS
from experiments.m24_har_fhs import har_features
from experiments import m28_atividade_escala as m28

BASE_SEED=2026101229
REFS=39
INTERVAL='1m'
K=m28.K
BLOCK=m28.BLOCK
BURN_B=m28.BURN_B
NULLS=('HXCLK','HXACT','BL')
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
PER_SHARD=2
TARGET=('hsic_5','hsic_30')
ALPHA_PRIMARY=.05/len(TARGET)
ALPHA_EQUIV=.05/len(STATS)
ALREADY_OK=tuple(s for s in STATS if s not in TARGET)
DIAG_PROFILE=ROOT/'reports'/'m29diag'/'relogio_volume_pares.json'


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


def minute_of_hour(ts_ms):
    return ((np.asarray(ts_ms,dtype=np.int64)//60000)%60).astype(int)


# ------------------------------------------------------------ clock profile
def clock_profile(v,moh):
    """Centered, positive-part James-Stein shrunk minute-of-hour profile of v."""
    v=np.asarray(v,float);n=len(v)
    if n<600:raise ValueError('clock: too short')
    c=np.concatenate([[0.],np.cumsum(v)]);i=np.arange(30,n-30)
    ma=(c[i+30]-c[i-30])/60          # centered 60-min mean (rows i-30..i+29)
    r=v[i]-ma;b=moh[i]
    cnt=np.bincount(b,minlength=60)
    if cnt.min()<5:raise ValueError('clock: empty minute bin')
    p=np.bincount(b,weights=r,minlength=60)/cnt
    s2=np.bincount(b,weights=r*r,minlength=60)/cnt-p**2
    p=p-p.mean()
    noise=float(np.mean(s2/cnt))
    shrink=max(0.,1-(60-3)*noise/float(np.sum(p**2)))
    return shrink*p,{'shrink':shrink,'raw_profile':p.tolist(),'noise_var_mean':noise}


def fit_local_clk(x,moh_x,seed):
    xs,ss,slow=slow_layer(x,seed)
    moh=moh_x[SMOOTH[INTERVAL]-1:]
    if len(moh)!=len(xs):raise ValueError('clock alignment')
    d=np.zeros(len(xs))
    for s in (0,1):d[slow==s]=ss[slow==s]-ss[slow==s].mean()
    nu_full=xs[:,2].copy()
    prof,cd=clock_profile(xs[:,2]-d,moh)
    xs[:,2]-=d+prof[moh]
    t,F=har_features(xs);L=len(xs)
    segs=np.array_split(np.arange(L),K)
    pars=[];diags=[]
    for g in segs:
        p,dg=m28.fit_segment_act(xs,t,F,int(g[0]),int(g[-1])+1,nu_full);pars.append(p);diags.append(dg)
    bounds=[(int(g[0]),int(g[-1])+1) for g in segs]

    def sample(rng,n,m0):
        out=[]
        for b in range((n+BLOCK-1)//BLOCK):
            gi=int(rng.integers(0,K));lo,hi=bounds[gi]
            p0=int(rng.integers(lo,hi));steps=np.arange(BURN_B+BLOCK)
            dseq=d[(p0-BURN_B+steps)%L]+prof[(m0+b*BLOCK-BURN_B+steps)%60]
            out.append(m28.sim_act(pars[gi],rng,BURN_B+BLOCK,dseq)[-BLOCK:])
        return np.vstack(out)[:n]
    cd['profile']=prof.tolist();cd['argmax']=int(np.argmax(prof));cd['argmax_raw']=int(np.argmax(cd['raw_profile']))
    return sample,{'segments':diags,'clock':cd}


def build(prefix_df,seed,m0):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ok=np.isfinite(pre).all(axis=1);first=int(np.flatnonzero(ok)[0])
    raw=pre[first:]
    if len(raw)<2000 or not np.isfinite(raw).all():raise ValueError('Prefix coordinates invalid')
    moh=minute_of_hour(prefix_df.timestamp.to_numpy()[first:])
    ns=gaussianize_three(raw,raw)
    s={};diag={}
    f,diag['HXCLK']=fit_local_clk(ns,moh,seed+50)
    s['HXCLK']=lambda rng,n:f(rng,n,m0)
    s['HXACT'],_=m28.fit_local_act(ns,seed+50)
    s['BL']=lambda rng,n:circular_blocks(raw,rng,LONG_BLOCK[INTERVAL])[:n]
    return s,diag


def run_origin(df,start,k,refs=REFS,stats_fn=full_stats):
    pre=PREFIX[INTERVAL];w=WINDOW[INTERVAL]
    prefix=df.iloc[start-pre:start].copy();fut=df.iloc[start:start+w].copy()
    actual=flow_coordinates(pd.concat([prefix,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-w:]
    item={'origin':int(k),'window_start_ms':int(fut.timestamp.iloc[0]),'models':{}}
    if not np.isfinite(actual).all():item['status']='invalid_observed';return item
    obs=stats_fn(actual,seed_int(k,1));item['observed']=obs
    m0=int(minute_of_hour([fut.timestamp.iloc[0]])[0])
    try:samplers,diag=build(prefix,seed_int(k,2),m0)
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:
        item['status']='fit_failed';item['error']=str(e);return item
    item['status']='valid';item['fit_diagnostics']=diag
    for name in NULLS:
        ref={s:[] for s in STATS}
        for j in range(refs):
            try:
                sim=samplers[name](np.random.default_rng(seed_int(k,3,NULL_ID[name],j)),w)
                if sim.shape!=(w,3) or not np.isfinite(sim).all():raise ValueError('bad window')
                r=stats_fn(sim,seed_int(k,4,NULL_ID[name],j))
            except (ValueError,RuntimeError,np.linalg.LinAlgError,FloatingPointError):
                r={s:None for s in STATS}
            for s in STATS:ref[s].append(r[s])
        rec={'references':ref}
        for s in STATS:
            p=conservative_rank(obs[s],ref[s]);rec[s]={'p_rank':p,'alarm':bool(p is not None and p<=.05)}
        item['models'][name]=rec
    return item


# ------------------------------------------------------------ aggregation
def _cells(val):
    cells={}
    for m in NULLS:
        for s in STATS:
            al=[r['models'][m][s]['alarm'] for r in val if r['models'][m][s]['p_rank'] is not None]
            k=int(sum(al));n=len(al)
            cells[f'{m}|{s}']={'alarms':k,'n':n,'rate':k/n if n else None,'wilson95':wilson(k,n),
                               'elevated':bool(n and wilson(k,n)[0]>CORRECT_FAMILY_LEVEL)}
    return cells


def _pair(val,a,b,s):
    xa=[];xb=[]
    for r in val:
        pa=r['models'][a][s];pb=r['models'][b][s]
        if pa['p_rank'] is not None and pb['p_rank'] is not None:xa.append(pa['alarm']);xb.append(pb['alarm'])
    return mcnemar_exact(xa,xb)


def _verdict(val,cells):
    worse={s:_pair(val,'HXCLK','BL',s) for s in STATS}
    for v in worse.values():v['significant']=bool(v['p_one_sided']<ALPHA_EQUIV)
    full=all(not cells[f'HXCLK|{s}']['elevated'] for s in STATS)
    equiv=all(not v['significant'] for v in worse.values())
    return worse,('ADEQUACAO PLENA (nenhuma estatistica elevada)' if full else
                  'EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)' if equiv else 'NAO FECHA A LACUNA')


def aggregate(rows,n_expected,diag_profile=None):
    if sorted(r['origin'] for r in rows)!=list(range(n_expected)):raise ValueError('Missing or duplicate origins')
    val=[r for r in rows if r.get('status')=='valid']
    odd=[r for r in val if r['origin']%2==1]
    cells=_cells(val);cells_odd=_cells(odd)
    primary={s:_pair(odd,'HXACT','HXCLK',s) for s in TARGET}
    for v in primary.values():v['significant']=bool(v['p_one_sided']<ALPHA_PRIMARY)
    worse,verdict=_verdict(val,cells)
    worse_odd,verdict_odd=_verdict(odd,cells_odd)
    alerts={}
    for s in ALREADY_OK:
        a=_pair(val,'HXCLK','HXACT',s);b=_pair(val,'HXACT','HXCLK',s)
        p2=min(1.,2*min(a['p_one_sided'],b['p_one_sided']))
        alerts[s]={'only_HXCLK':a['x_only'],'only_HXACT':a['y_only'],'p_two_sided':p2,
                   'HXCLK_worse':bool(p2<ALPHA_EQUIV and a['x_only']>a['y_only'])}
    clk=[r['fit_diagnostics']['HXCLK']['clock'] for r in odd]
    mech={'frac_argmax_00_shrunk':float(np.mean([c['argmax']==0 for c in clk])),
          'frac_argmax_00_raw':float(np.mean([c['argmax_raw']==0 for c in clk])),
          'shrink_median':float(np.median([c['shrink'] for c in clk])),
          'frac_shrink_zero':float(np.mean([c['shrink']==0 for c in clk]))}
    mech['sign_p_argmax_00_majority']=float(binomtest(int(round(mech['frac_argmax_00_raw']*len(clk))),len(clk),.5,alternative='greater').pvalue)
    if diag_profile is not None:
        dp=np.asarray(diag_profile,float);dp=dp-dp.mean()
        mech['corr_with_even_diag_median']=float(np.median([np.corrcoef(c['raw_profile'],dp)[0,1] for c in clk]))
    return {'n_valid':len(val),'n_odd':len(odd),'status':{s:sum(1 for r in rows if r.get('status')==s) for s in {r.get('status') for r in rows}},
            'cells':cells,'cells_odd':cells_odd,'primary_odd_vs_HXACT':primary,'mechanism_odd':mech,
            'HXCLK_worse_than_BL':worse,'verdict':verdict,'HXCLK_worse_than_BL_odd':worse_odd,'verdict_odd':verdict_odd,
            'not_worse_alerts':alerts}


def report(a):
    pct=lambda x:'—' if x is None else f'{100*x:.0f}%'
    L=['# SGV-M29 — O relógio do volume (resultados)','',
       f"Origens válidas: {a['n_valid']} ({a['status']}); ímpares (teste): {a['n_odd']}. Agregado por `experiments/m29_relogio_volume.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M29_20261012.md`.",'',
       '**Todas as origens:**','','| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:L.append(f'| {m} | '+' | '.join(pct(a['cells'][f'{m}|{s}']['rate']) for s in STATS)+' |')
    L+=['','**Só ímpares (teste):**','','| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:L.append(f'| {m} | '+' | '.join(pct(a['cells_odd'][f'{m}|{s}']['rate']) for s in STATS)+' |')
    L+=['','**Primário (ímpares, HXACT → HXCLK, McNemar unilateral, α=0,025):**','']
    for s,v in a['primary_odd_vs_HXACT'].items():
        L.append(f"- {s}: só HXACT {v['x_only']}, só HXCLK {v['y_only']}, p={v['p_one_sided']:.2g} → {'significativo' if v['significant'] else 'n.s.'}")
    L+=['','**HXCLK pior que BL? (84 origens, α=0,05/12):**','']
    for s,v in a['HXCLK_worse_than_BL'].items():
        L.append(f"- {s}: só HXCLK {v['x_only']}, só BL {v['y_only']}, p={v['p_one_sided']:.2g}{' **(pior)**' if v['significant'] else ''}")
    L+=['',f"**Veredito pré-registrado (84): {a['verdict']}**",f"Veredito só nas ímpares: {a['verdict_odd']}",'',
        '**Não piorar (HXCLK × HXACT, bilateral, α=0,05/12):**','']
    for s,v in a['not_worse_alerts'].items():
        L.append(f"- {s}: só HXCLK {v['only_HXCLK']}, só HXACT {v['only_HXACT']}, p={v['p_two_sided']:.2g}{' **ALERTA**' if v['HXCLK_worse'] else ''}")
    L+=['','**Mecanismo (descritivo, ímpares):** '+json.dumps(a['mechanism_odd'],ensure_ascii=False)]
    return '\n'.join(L)


def write(obj,name):
    p=ROOT/'reports'/'m29'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n');return p


def run_shard(shard):
    df,starts=load(INTERVAL)
    ks=range(shard*PER_SHARD,min(len(starts),(shard+1)*PER_SHARD))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],k) for k in ks]
    write({'status':'M29_SHARD','shard':shard,'n_origins_total':len(starts),'origins':rows},f'shard_{shard:02d}.json')
    print(json.dumps({'shard':shard,'n':len(rows)}))


def run_pilot():
    df,starts=load(INTERVAL)
    r=run_origin(df,starts[0],0,refs=2)
    bad=[] if r.get('status')=='valid' else [r.get('status'),r.get('error')]
    if not bad:
        for m,v in r['models'].items():
            for s in STATS:
                if s!='m11' and any(x is None for x in v['references'][s]):bad.append((m,s))
    write({'status':'M29_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad}))
    if bad:raise RuntimeError('Pilot failed')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('pilot','shard','aggregate'),required=True)
    ap.add_argument('--shard',type=int);ap.add_argument('--shards-dir',default=str(ROOT/'reports'/'m29'/'_dl'))
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    elif a.mode=='shard':run_shard(a.shard)
    else:
        n=EXPECTED_ORIGINS[INTERVAL];rows=[]
        for s in range((n+PER_SHARD-1)//PER_SHARD):
            d=json.loads((Path(a.shards_dir)/f'shard_{s:02d}.json').read_text())
            if d.get('shard')!=s or d.get('n_origins_total')!=n:raise ValueError('bad shard')
            rows+=d['origins']
        dp=json.loads(DIAG_PROFILE.read_text())['moh_mean'] if DIAG_PROFILE.exists() else None
        agg=aggregate(rows,n,dp);write(agg,'SGV_M29_AGREGADO.json')
        md=report(agg);(ROOT/'reports'/'m29'/'SGV_M29_RESULTADOS.md').write_text(md+'\n');print(md)


if __name__=='__main__':main()
