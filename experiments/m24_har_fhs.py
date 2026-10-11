#!/usr/bin/env python3
"""SGV-M24: closing the gap -- heterogeneous (HAR-type) autoregression with
filtered historical innovations, inside two-scale regimes with the real slow block.

Within each slow regime s:
    x_t = c_s + A1_s x_{t-1} + A15_s mean(x_{t-15..t-1}) + A60_s mean(x_{t-60..t-1}) + L_s u_t
    u_t,j = sqrt(h_t,j) z_t,j       GARCH(1,1) per whitened coordinate (unit variance)
    z_t  ~ N(0, I)                  (HARLM)
    z_t  = a REAL standardized residual row of the prefix, drawn with replacement
                                    (HARLMF: filtered historical simulation, keeps the
                                     non-Gaussian joint shape of the innovations)
Slow regime sequence and slow continuous part of nu: real contiguous block of the
prefix (LM, as in M18/M23). References: MSARLM (M23) and BL. Same 12 statistics,
39 references, conservative rank.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
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
from experiments.m17_tipo_de_memoria import BURN
from experiments.m18_acoplamento_dinamico import LONG_BLOCK
from experiments.m21_posto_conservador import conservative_rank
from experiments.m23_modelo_minimo import slow_layer,fit_garch,fit_msar,full_stats,STATS

BASE_SEED=2026101124
REFS=39
INTERVAL='1m'
H=(1,15,60)
NULLS=('HARLM','HARLMF','MSARLM','BL')
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
PER_SHARD=2
ALPHA_PRIMARY=.05/4
ALPHA_EQUIV=.05/len(STATS)


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


def har_features(x):
    """Row t holds [1, x_{t-1}, mean x_{t-15..t-1}, mean x_{t-60..t-1}] for t>=60."""
    c=np.cumsum(np.vstack([np.zeros((1,3)),x]),axis=0)
    t=np.arange(60,len(x))
    f=[np.ones((len(t),1)),x[t-1]]
    for hh in H[1:]:f.append((c[t]-c[t-hh])/hh)
    return t,np.hstack(f)


def companion_radius(A1,A15,A60):
    p=60;M=np.zeros((3*p,3*p))
    for k in range(1,p+1):
        Ak=A60/60+(A15/15 if k<=15 else 0)+(A1 if k==1 else 0)
        M[:3,3*(k-1):3*k]=Ak
    M[3:,:-3]=np.eye(3*(p-1))
    return float(max(abs(np.linalg.eigvals(M))))


def fit_har(x,seed,fhs):
    xs,ss,slow=slow_layer(x,seed)
    d=np.zeros(len(xs))
    for s in (0,1):d[slow==s]=ss[slow==s]-ss[slow==s].mean()
    xs[:,2]-=d
    t,F=har_features(xs)
    par={};U_t=[];U=[];diag={}
    for s in (0,1):
        m=slow[t]==s
        if m.sum()<300:raise ValueError(f'regime {s}: <300 rows')
        B=np.linalg.lstsq(F[m],xs[t[m]],rcond=None)[0].T          # 3 x 10
        c,A1,A15,A60=B[:,0],B[:,1:4],B[:,4:7],B[:,7:10]
        rho=companion_radius(A1,A15,A60);shr=1.
        while rho>=.995:
            shr*=.98;rho=companion_radius(A1*shr,A15*shr,A60*shr)
        A1,A15,A60=A1*shr,A15*shr,A60*shr
        e=xs[t[m]]-(c+F[m][:,1:4]@A1.T+F[m][:,4:7]@A15.T+F[m][:,7:10]@A60.T)
        L=np.linalg.cholesky(np.cov(e,rowvar=False))
        par[s]=(c,A1,A15,A60,L)
        U_t.append(t[m]);U.append(np.linalg.solve(L,e.T).T)
        diag[f'regime{s}']={'companion_radius':rho,'shrink':shr,'n':int(m.sum())}
    o=np.argsort(np.concatenate(U_t));U=np.concatenate(U)[o]
    garch=[fit_garch(U[:,j]) for j in range(3)]
    ga=np.array([g[0] for g in garch]);gb=np.array([g[1] for g in garch])
    h=np.ones(3);Z=np.empty_like(U)
    for k in range(len(U)):                                       # filtered standardized residuals
        if k:h=(1-ga-gb)+ga*U[k-1]**2+gb*h
        Z[k]=U[k]/np.sqrt(h)
    Z=(Z-Z.mean(0))/Z.std(0)
    diag['garch']=[{'alpha':a,'beta':b} for a,b in garch]
    diag['z_excess_kurtosis']=[float(((Z[:,j])**4).mean()-3) for j in range(3)]

    def sample(rng,n):
        total=n+BURN
        start=int(rng.integers(0,len(slow)));idx=(start+np.arange(total))%len(slow)
        seq=slow[idx];out=np.empty((total,3))
        s0=int(seq[0]);c,A1,A15,A60,L=par[s0]
        mu=np.linalg.solve(np.eye(3)-A1-A15-A60,c)
        buf=np.tile(mu,(60,1));s15=mu*15;s60=mu*60;pos=0
        hh=np.ones(3);uprev=np.zeros(3)
        draws=Z[rng.integers(0,len(Z),size=total)] if fhs else rng.standard_normal((total,3))
        for k in range(total):
            c,A1,A15,A60,L=par[int(seq[k])]
            last=buf[(pos-1)%60]
            hh=(1-ga-gb)+ga*uprev**2+gb*hh
            uprev=np.sqrt(hh)*draws[k]
            xk=c+A1@last+A15@(s15/15)+A60@(s60/60)+L@uprev
            old60=buf[pos].copy();old15=buf[(pos-15)%60].copy()
            buf[pos]=xk;pos=(pos+1)%60
            s60+=xk-old60;s15+=xk-old15
            out[k]=xk
        out[:,2]+=d[idx]
        return out[-n:]
    return sample,diag


def build(prefix_df,seed):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ok=np.isfinite(pre).all(axis=1)
    raw=pre[int(np.flatnonzero(ok)[0]):]
    if len(raw)<2000 or not np.isfinite(raw).all():raise ValueError('Prefix coordinates invalid')
    ns=gaussianize_three(raw,raw)
    s={};diag={}
    s['HARLM'],diag['HARLM']=fit_har(ns,seed+50,fhs=False)
    s['HARLMF'],diag['HARLMF']=fit_har(ns,seed+50,fhs=True)
    s['MSARLM'],_=fit_msar(ns,seed+50,lm=True)
    s['BL']=lambda rng,n:circular_blocks(raw,rng,LONG_BLOCK[INTERVAL])[:n]
    return s,diag


def run_origin(df,start,k,refs=REFS,stats_fn=full_stats):
    pre=PREFIX[INTERVAL];w=WINDOW[INTERVAL]
    prefix=df.iloc[start-pre:start].copy();fut=df.iloc[start:start+w].copy()
    actual=flow_coordinates(pd.concat([prefix,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-w:]
    item={'origin':int(k),'window_start_ms':int(fut.timestamp.iloc[0]),'models':{}}
    if not np.isfinite(actual).all():item['status']='invalid_observed';return item
    obs=stats_fn(actual,seed_int(k,1));item['observed']=obs
    try:samplers,diag=build(prefix,seed_int(k,2))
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
            except (ValueError,RuntimeError,np.linalg.LinAlgError):
                r={s:None for s in STATS}
            for s in STATS:ref[s].append(r[s])
        rec={'references':ref}
        for s in STATS:
            p=conservative_rank(obs[s],ref[s]);rec[s]={'p_rank':p,'alarm':bool(p is not None and p<=.05)}
        item['models'][name]=rec
    return item


def aggregate(rows,n_expected):
    if sorted(r['origin'] for r in rows)!=list(range(n_expected)):raise ValueError('Missing or duplicate origins')
    val=[r for r in rows if r.get('status')=='valid']
    cells={}
    for m in NULLS:
        for s in STATS:
            al=[r['models'][m][s]['alarm'] for r in val if r['models'][m][s]['p_rank'] is not None]
            k=int(sum(al));n=len(al)
            cells[f'{m}|{s}']={'alarms':k,'n':n,'rate':k/n if n else None,'wilson95':wilson(k,n),
                               'elevated':bool(n and wilson(k,n)[0]>CORRECT_FAMILY_LEVEL)}
    def pair(a,b,s):
        xa=[];xb=[]
        for r in val:
            pa=r['models'][a][s];pb=r['models'][b][s]
            if pa['p_rank'] is not None and pb['p_rank'] is not None:xa.append(pa['alarm']);xb.append(pb['alarm'])
        return mcnemar_exact(xa,xb)
    primary={s:pair('MSARLM','HARLMF',s) for s in ('lin_5','vol_5','hsic_5','m11')}
    for v in primary.values():v['significant']=bool(v['p_one_sided']<ALPHA_PRIMARY)
    worse={s:pair('HARLMF','BL',s) for s in STATS}
    for v in worse.values():v['significant']=bool(v['p_one_sided']<ALPHA_EQUIV)
    fhs_effect={s:pair('HARLM','HARLMF',s) for s in STATS}
    full=all(not cells[f'HARLMF|{s}']['elevated'] for s in STATS)
    equiv=all(not v['significant'] for v in worse.values())
    verdict=('ADEQUACAO PLENA (nenhuma estatistica elevada)' if full else
             'EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)' if equiv else 'NAO FECHA A LACUNA')
    q=lambda v:[float(x) for x in np.quantile(v,[.25,.5,.75])] if v else None
    diagq={'z_excess_kurtosis_median':[float(np.median([r['fit_diagnostics']['HARLMF']['z_excess_kurtosis'][j] for r in val])) for j in range(3)],
           'companion_radius_quartiles':q([r['fit_diagnostics']['HARLMF'][f'regime{s}']['companion_radius'] for r in val for s in (0,1)]),
           'shrink_applied_fraction':float(np.mean([r['fit_diagnostics']['HARLMF'][f'regime{s}']['shrink']<1 for r in val for s in (0,1)]))}
    return {'n_valid':len(val),'status':{s:sum(1 for r in rows if r.get('status')==s) for s in {r.get('status') for r in rows}},
            'cells':cells,'primary_vs_MSARLM':primary,'HARLMF_worse_than_BL':worse,'fhs_effect_HARLM_vs_HARLMF':fhs_effect,
            'verdict':verdict,'diagnostics':diagq}


def report(a):
    pct=lambda x:'—' if x is None else f'{100*x:.0f}%'
    L=['# SGV-M24 — HAR + inovações históricas filtradas (resultados)','',
       f"Origens válidas: {a['n_valid']} ({a['status']}). Agregado por `experiments/m24_har_fhs.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M24_20261011.md`.",'',
       '| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:L.append(f'| {m} | '+' | '.join(pct(a['cells'][f'{m}|{s}']['rate']) for s in STATS)+' |')
    L+=['','**Primário (MSARLM → HARLMF, McNemar unilateral, α=0,0125):**','']
    for s,v in a['primary_vs_MSARLM'].items():
        L.append(f"- {s}: só MSARLM {v['x_only']}, só HARLMF {v['y_only']}, p={v['p_one_sided']:.2g} → {'melhora significativa' if v['significant'] else 'n.s.'}")
    L+=['','**HARLMF pior que BL? (α=0,05/12):**','']
    for s,v in a['HARLMF_worse_than_BL'].items():
        L.append(f"- {s}: só HARLMF {v['x_only']}, só BL {v['y_only']}, p={v['p_one_sided']:.2g}{' **(pior)**' if v['significant'] else ''}")
    L+=['','**Efeito das inovações reais (HARLM → HARLMF), descritivo:**','']
    for s,v in a['fhs_effect_HARLM_vs_HARLMF'].items():L.append(f"- {s}: só HARLM {v['x_only']}, só HARLMF {v['y_only']}, p={v['p_one_sided']:.2g}")
    L+=['',f"**Veredito pré-registrado: {a['verdict']}**",'','Diagnósticos: '+json.dumps(a['diagnostics'],ensure_ascii=False)]
    return '\n'.join(L)


def write(obj,name):
    p=ROOT/'reports'/'m24'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n');return p


def run_shard(shard):
    df,starts=load(INTERVAL)
    ks=range(shard*PER_SHARD,min(len(starts),(shard+1)*PER_SHARD))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],k) for k in ks]
    write({'status':'M24_SHARD','shard':shard,'n_origins_total':len(starts),'origins':rows},f'shard_{shard:02d}.json')
    print(json.dumps({'shard':shard,'n':len(rows)}))


def run_pilot():
    df,starts=load(INTERVAL)
    r=run_origin(df,starts[0],0,refs=2)
    bad=[] if r.get('status')=='valid' else [r.get('status'),r.get('error')]
    if not bad:
        for m,v in r['models'].items():
            for s in STATS:
                if s!='m11' and any(x is None for x in v['references'][s]):bad.append((m,s))
    write({'status':'M24_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad}))
    if bad:raise RuntimeError('Pilot failed')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('pilot','shard','aggregate'),required=True)
    ap.add_argument('--shard',type=int);ap.add_argument('--shards-dir',default=str(ROOT/'reports'/'m24'/'_dl'))
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    elif a.mode=='shard':run_shard(a.shard)
    else:
        n=EXPECTED_ORIGINS[INTERVAL];rows=[]
        for s in range((n+PER_SHARD-1)//PER_SHARD):
            d=json.loads((Path(a.shards_dir)/f'shard_{s:02d}.json').read_text())
            if d.get('shard')!=s or d.get('n_origins_total')!=n:raise ValueError('bad shard')
            rows+=d['origins']
        agg=aggregate(rows,n);write(agg,'SGV_M24_AGREGADO.json')
        md=report(agg);(ROOT/'reports'/'m24'/'SGV_M24_RESULTADOS.md').write_text(md+'\n');print(md)


if __name__=='__main__':main()
