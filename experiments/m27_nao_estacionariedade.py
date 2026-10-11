#!/usr/bin/env python3
"""SGV-M27: parameter non-stationarity (protocol reports/PROTOCOLO_SGV_M27_20261011.md).

The M26 model (HARLMFX) with LOCAL parameters: the prefix (after the M23 slow
layer) is split into K=6 contiguous segments; in each one a single-regime HAR
(1/15/60) mean + M26 cross-volatility + filtered real innovations of that segment
is fitted. Simulation in blocks of 500 rows (like BL): each block draws a segment
and a start inside it, burns 300 steps with that segment's parameters and adds the
real slow block of the same position.
Nulls: HXLOC (local params on the real prefix), HXNOISE (same pipeline on a
synthetic prefix drawn from the global HARLMFX -> estimation-noise control),
HARLMFX (M26, global), BL.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import lfilter
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
from experiments.m18_acoplamento_dinamico import LONG_BLOCK
from experiments.m21_posto_conservador import conservative_rank
from experiments.m23_modelo_minimo import slow_layer,full_stats,STATS
from experiments.m24_har_fhs import har_features,companion_radius
from experiments.m26_resiliencia_cruzada import fit_cross,cross_design,_unpack,fit_harx,HFLOOR

BASE_SEED=2026101127
REFS=39
INTERVAL='1m'
K=6
BLOCK=500
BURN_B=300
NULLS=('HXLOC','HXNOISE','HARLMFX','BL')
NULL_ID={n:i+1 for i,n in enumerate(NULLS)}
PER_SHARD=2
TARGET=('vol_5','vol_30','hsic_5','hsic_30')
ALPHA_PRIMARY=.05/len(TARGET)
ALPHA_EQUIV=.05/len(STATS)
DISP_KEYS=('varpers_z','varpers_nu','c_iota_from_z','ar1_nu','harpers_nu')


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


# ------------------------------------------------------------ local fits
def fit_segment(xs,t,F,lo,hi):
    """Single-regime HAR mean + M26 cross variance + FHS on rows lo..hi-1."""
    m=(t>=lo)&(t<hi)
    if m.sum()<300:raise ValueError('segment: <300 HAR rows')
    B=np.linalg.lstsq(F[m],xs[t[m]],rcond=None)[0].T
    c,A1,A15,A60=B[:,0],B[:,1:4],B[:,4:7],B[:,7:10]
    rho=companion_radius(A1,A15,A60);shr=1.
    while rho>=.995:
        shr*=.98;rho=companion_radius(A1*shr,A15*shr,A60*shr)
    A1,A15,A60=A1*shr,A15*shr,A60*shr
    e=xs[t[m]]-(c+F[m][:,1:4]@A1.T+F[m][:,4:7]@A15.T+F[m][:,7:10]@A60.T)
    sd=e.std(0);R=e/sd
    P=fit_cross(R);R2=R**2;H=np.empty_like(R)
    for j in range(3):
        cc,a,b=_unpack(P[j],j);w=1-cc.sum()-a.sum()-b
        H[:,j]=np.maximum(lfilter([1.],[1.,-b],w+cross_design(R2,j)@np.r_[cc,a]),HFLOOR)
    Z=R/np.sqrt(H);Z=(Z-Z.mean(0))/Z.std(0)
    C=np.array([p[:3] for p in P]);Aown=np.array([p[3:6] for p in P]);Bv=np.array([p[6] for p in P])
    W=1-C.sum(1)-Aown.sum(1)-Bv
    par={'c':c,'A1':A1,'A15':A15,'A60':A60,'sd':sd,'C':C,'Aown':Aown,'Bv':Bv,'W':W,'Z':Z}
    vp=np.diag(C)+Aown.sum(1)+Bv
    diag={'companion_radius':float(rho),'varpers_z':float(vp[0]),'varpers_iota':float(vp[1]),'varpers_nu':float(vp[2]),
          'c_iota_from_z':float(C[1,0]),'ar1_nu':float(A1[2,2]),'harpers_nu':float((A1+A15+A60)[2,2]),'rows':int(m.sum())}
    return par,diag


def sim_single(p,rng,nsteps):
    """Simulate nsteps of one segment's model (whitened residual scale, slow block NOT added)."""
    c,A1,A15,A60,sd=p['c'],p['A1'],p['A15'],p['A60'],p['sd']
    C,Aown,Bv,W,Z=p['C'],p['Aown'],p['Bv'],p['W'],p['Z']
    mu=np.linalg.solve(np.eye(3)-A1-A15-A60,c)
    buf=np.tile(mu,(60,1));s15=mu*15;s60=mu*60;pos=0
    ub=np.ones((240,3));q15=np.full(3,15.);q60=np.full(3,60.);q240=np.full(3,240.);up=0
    h=np.ones(3);r2prev=np.ones(3);out=np.empty((nsteps,3))
    draws=Z[rng.integers(0,len(Z),size=nsteps)]
    for k in range(nsteps):
        h=np.maximum(W+C@r2prev+Aown[:,0]*q15/15+Aown[:,1]*q60/60+Aown[:,2]*q240/240+Bv*h,HFLOOR)
        r=np.sqrt(h)*draws[k];r2=r*r
        o15=ub[(up-15)%240].copy();o60=ub[(up-60)%240].copy();o240=ub[up].copy()
        ub[up]=r2;up=(up+1)%240;q15+=r2-o15;q60+=r2-o60;q240+=r2-o240;r2prev=r2
        last=buf[(pos-1)%60]
        xk=c+A1@last+A15@(s15/15)+A60@(s60/60)+sd*r
        old60=buf[pos].copy();old15=buf[(pos-15)%60].copy()
        buf[pos]=xk;pos=(pos+1)%60;s60+=xk-old60;s15+=xk-old15
        out[k]=xk
    return out


def fit_local(x,seed):
    xs,ss,slow=slow_layer(x,seed)
    d=np.zeros(len(xs))
    for s in (0,1):d[slow==s]=ss[slow==s]-ss[slow==s].mean()
    xs[:,2]-=d
    t,F=har_features(xs);L=len(xs)
    segs=np.array_split(np.arange(L),K)
    pars=[];diags=[]
    for g in segs:
        p,dg=fit_segment(xs,t,F,int(g[0]),int(g[-1])+1);pars.append(p);diags.append(dg)
    bounds=[(int(g[0]),int(g[-1])+1) for g in segs]

    def sample(rng,n):
        out=[]
        for _ in range((n+BLOCK-1)//BLOCK):
            gi=int(rng.integers(0,K));lo,hi=bounds[gi]
            p0=int(rng.integers(lo,hi))
            y=sim_single(pars[gi],rng,BURN_B+BLOCK)[-BLOCK:]
            y[:,2]+=d[(p0+np.arange(BLOCK))%L]
            out.append(y)
        return np.vstack(out)[:n]
    return sample,{'segments':diags}


def dispersion(diag):
    return {k:float(np.std([s[k] for s in diag['segments']])) for k in DISP_KEYS}


def build(prefix_df,seed):
    pre=flow_coordinates(prefix_df)[['z','iota','nu']].to_numpy(float)
    ok=np.isfinite(pre).all(axis=1)
    raw=pre[int(np.flatnonzero(ok)[0]):]
    if len(raw)<2000 or not np.isfinite(raw).all():raise ValueError('Prefix coordinates invalid')
    ns=gaussianize_three(raw,raw)
    s={};diag={}
    s['HARLMFX'],diag['HARLMFX']=fit_harx(ns,seed+50)
    s['HXLOC'],diag['HXLOC']=fit_local(ns,seed+50)
    synth=s['HARLMFX'](np.random.default_rng(seed+70),len(ns))
    if not np.isfinite(synth).all():raise ValueError('synthetic prefix not finite')
    s['HXNOISE'],diag['HXNOISE']=fit_local(synth,seed+50)
    s['BL']=lambda rng,n:circular_blocks(raw,rng,LONG_BLOCK[INTERVAL])[:n]
    diag['dispersion']={'real':dispersion(diag['HXLOC']),'synthetic':dispersion(diag['HXNOISE'])}
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


# ------------------------------------------------------------ aggregation
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
    A={s:pair('HARLMFX','HXLOC',s) for s in TARGET}
    B={s:pair('HXNOISE','HXLOC',s) for s in TARGET}
    for v in (*A.values(),*B.values()):v['significant']=bool(v['p_one_sided']<ALPHA_PRIMARY)
    noise_helps={s:pair('HARLMFX','HXNOISE',s) for s in TARGET}
    for v in noise_helps.values():v['significant']=bool(v['p_one_sided']<ALPHA_PRIMARY)
    both=[s for s in TARGET if A[s]['significant'] and B[s]['significant']]
    reading=('NAO ESTACIONARIEDADE APOIADA em '+', '.join(both) if both else
             'GANHO SO POR RUIDO DE ESTIMACAO (A sem B)' if any(v['significant'] for v in A.values()) else
             'NAO APOIADA (parametros locais nao ajudam)')
    worse={s:pair('HXLOC','BL',s) for s in STATS}
    for v in worse.values():v['significant']=bool(v['p_one_sided']<ALPHA_EQUIV)
    full=all(not cells[f'HXLOC|{s}']['elevated'] for s in STATS)
    equiv=all(not v['significant'] for v in worse.values())
    verdict=('ADEQUACAO PLENA (nenhuma estatistica elevada)' if full else
             'EQUIVALENTE AO BL (nao significativamente pior em nenhuma estatistica)' if equiv else 'NAO FECHA A LACUNA')
    disp={}
    for kk in DISP_KEYS:
        re=np.array([r['fit_diagnostics']['dispersion']['real'][kk] for r in val])
        sy=np.array([r['fit_diagnostics']['dispersion']['synthetic'][kk] for r in val])
        gt=int(np.sum(re>sy))
        disp[kk]={'median_real':float(np.median(re)),'median_synthetic':float(np.median(sy)),
                  'frac_real_gt_synth':gt/len(re),'sign_p_one_sided':float(binomtest(gt,len(re),.5,alternative='greater').pvalue)}
    return {'n_valid':len(val),'status':{s:sum(1 for r in rows if r.get('status')==s) for s in {r.get('status') for r in rows}},
            'cells':cells,'primary_A_vs_HARLMFX':A,'primary_B_vs_HXNOISE':B,'reading':reading,
            'noise_alone_vs_HARLMFX':noise_helps,'HXLOC_worse_than_BL':worse,'verdict':verdict,'dispersion':disp}


def report(a):
    pct=lambda x:'—' if x is None else f'{100*x:.0f}%'
    L=['# SGV-M27 — Não estacionariedade dos parâmetros (resultados)','',
       f"Origens válidas: {a['n_valid']} ({a['status']}). Agregado por `experiments/m27_nao_estacionariedade.py --mode aggregate`; protocolo em `reports/PROTOCOLO_SGV_M27_20261011.md`.",'',
       '| Nulo | '+' | '.join(STATS)+' |','|---|'+'---|'*len(STATS)]
    for m in NULLS:L.append(f'| {m} | '+' | '.join(pct(a['cells'][f'{m}|{s}']['rate']) for s in STATS)+' |')
    for title,key,xa,xb in (('Primário A (HARLMFX → HXLOC)','primary_A_vs_HARLMFX','HARLMFX','HXLOC'),
                            ('Primário B (HXNOISE → HXLOC)','primary_B_vs_HXNOISE','HXNOISE','HXLOC'),
                            ('Descritivo: ruído sozinho (HARLMFX → HXNOISE)','noise_alone_vs_HARLMFX','HARLMFX','HXNOISE')):
        L+=['',f'**{title}, McNemar unilateral, α=0,0125:**','']
        for s,v in a[key].items():
            L.append(f"- {s}: só {xa} {v['x_only']}, só {xb} {v['y_only']}, p={v['p_one_sided']:.2g} → {'significativo' if v['significant'] else 'n.s.'}")
    L+=['',f"**Leitura pré-registrada: {a['reading']}**",'','**HXLOC pior que BL? (α=0,05/12):**','']
    for s,v in a['HXLOC_worse_than_BL'].items():
        L.append(f"- {s}: só HXLOC {v['x_only']}, só BL {v['y_only']}, p={v['p_one_sided']:.2g}{' **(pior)**' if v['significant'] else ''}")
    L+=['',f"**Veredito pré-registrado: {a['verdict']}**",'','**Dispersão dos parâmetros entre trechos (real × sintético):**','',
        '| parâmetro | mediana real | mediana sintético | fração real > sintético | p (sinal) |','|---|---|---|---|---|']
    for kk,v in a['dispersion'].items():
        L.append(f"| {kk} | {v['median_real']:.3f} | {v['median_synthetic']:.3f} | {100*v['frac_real_gt_synth']:.0f}% | {v['sign_p_one_sided']:.2g} |")
    return '\n'.join(L)


def write(obj,name):
    p=ROOT/'reports'/'m27'/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=1,ensure_ascii=False)+'\n');return p


def run_shard(shard):
    df,starts=load(INTERVAL)
    ks=range(shard*PER_SHARD,min(len(starts),(shard+1)*PER_SHARD))
    if not len(ks):raise ValueError('Empty shard')
    rows=[run_origin(df,starts[k],k) for k in ks]
    write({'status':'M27_SHARD','shard':shard,'n_origins_total':len(starts),'origins':rows},f'shard_{shard:02d}.json')
    print(json.dumps({'shard':shard,'n':len(rows)}))


def run_pilot():
    df,starts=load(INTERVAL)
    r=run_origin(df,starts[0],0,refs=2)
    bad=[] if r.get('status')=='valid' else [r.get('status'),r.get('error')]
    if not bad:
        for m,v in r['models'].items():
            for s in STATS:
                if s!='m11' and any(x is None for x in v['references'][s]):bad.append((m,s))
    write({'status':'M27_PILOT','problems':bad},'pilot.json');print(json.dumps({'problems':bad}))
    if bad:raise RuntimeError('Pilot failed')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('pilot','shard','aggregate'),required=True)
    ap.add_argument('--shard',type=int);ap.add_argument('--shards-dir',default=str(ROOT/'reports'/'m27'/'_dl'))
    a=ap.parse_args()
    if a.mode=='pilot':run_pilot()
    elif a.mode=='shard':run_shard(a.shard)
    else:
        n=EXPECTED_ORIGINS[INTERVAL];rows=[]
        for s in range((n+PER_SHARD-1)//PER_SHARD):
            d=json.loads((Path(a.shards_dir)/f'shard_{s:02d}.json').read_text())
            if d.get('shard')!=s or d.get('n_origins_total')!=n:raise ValueError('bad shard')
            rows+=d['origins']
        agg=aggregate(rows,n);write(agg,'SGV_M27_AGREGADO.json')
        md=report(agg);(ROOT/'reports'/'m27'/'SGV_M27_RESULTADOS.md').write_text(md+'\n');print(md)


if __name__=='__main__':main()
