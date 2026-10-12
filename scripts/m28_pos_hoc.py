#!/usr/bin/env python3
"""SGV-M28 post-hoc (declared, after results): does HXACT reproduce the diagnostic
components that motivated it, and what drives the remaining HSIC excess?
10 odd origins, 19 refs each for HXACT and HXLOC."""
from __future__ import annotations
import json,sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from sgvgeo.flow import flow_coordinates
from experiments.precisao_formas_3d import gaussianize_three
from experiments.m5_validacao_conjunta_sf1 import WINDOW
from experiments.m12_nulos_regimes_temporais import PREFIX
from experiments.m16_trio_btc_exploratorio import load
from experiments.m21b_dependencia_btc import copula,hsic
from experiments import m27_nao_estacionariedade as m27
from experiments import m28_atividade_escala as m28
import m28_diag_dependencia as dg
_pj=ROOT/'reports'/'m28'/'pos_hoc.json'
PREV={r['origin']:r for r in json.loads(_pj.read_text())} if _pj.exists() else {}
KEYS=('lev|nu>iota@5','lev|nu>iota@30','m2d|z>nu@5','hs|nu>nu@5','hs|nu>nu@30','hs|nu>iota@5','hs|z>nu@5','hs|iota>iota@5','hs|z>z@5','hsic3d@5','hsic3d@30')
def extra(x):
    u=copula(x);o={f'c0|nu,|iota|':dg.corr(u[:,2],np.abs(u[:,1])),'c0|nu,|z|':dg.corr(u[:,2],np.abs(u[:,0]))}
    for l in (5,30):o[f'hsic3d_noNu@{l}']=hsic(u[:-l,:2],u[l:,:2]);o[f'hs|nu>nu_only@{l}']=hsic(u[:-l,[2]],u[l:,[2]])
    return o
def allc(x):
    c=dg.comps(x);c.update(extra(x));return {k:c[k] for k in (*KEYS,*extra(x).keys())}
def one(k):
    df,starts=load('1m');start=starts[k];pre=PREFIX['1m'];w=WINDOW['1m']
    prefix=df.iloc[start-pre:start].copy();fut=df.iloc[start:start+w].copy()
    actual=flow_coordinates(pd.concat([prefix,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-w:]
    raw=flow_coordinates(prefix)[['z','iota','nu']].to_numpy(float);raw=raw[int(np.flatnonzero(np.isfinite(raw).all(axis=1))[0]):]
    ns=gaussianize_three(raw,raw);seed=m28.seed_int(k,2)+50
    fa,_=m28.fit_local_act(ns,seed);fl,_=m27.fit_local(ns,seed)
    obs=allc(actual);out={'origin':k,'obs':obs};prev=PREV.get(k)
    for name,f in (('HXACT',fa),('HXLOC',fl)):
        if prev is not None and name=='HXLOC' and all(np.isfinite(v['mean']) for v in prev['HXLOC'].values()):
            out[name]=prev['HXLOC'];continue
        refs=[];j=0
        while len(refs)<19 and j<40:   # engineering fix: skip rare non-finite simulations
            sim=f(np.random.default_rng(m28.seed_int(k,9,j)),w);j+=1
            if np.isfinite(sim).all():refs.append(allc(sim))
        out[name]={key:{'mean':float(np.mean([r[key] for r in refs])),'sd':float(np.std([r[key] for r in refs])),'n':len(refs)} for key in obs}
    return out
if __name__=='__main__':
    with Pool(2) as p:rows=p.map(one,list(range(1,21,2)))
    (ROOT/'reports'/'m28'/'pos_hoc.json').write_text(json.dumps(rows,indent=1)+'\n')
    for key in rows[0]['obs']:
        o=np.median([r['obs'][key] for r in rows])
        za=np.median([(r['obs'][key]-r['HXACT'][key]['mean'])/r['HXACT'][key]['sd'] for r in rows])
        zl=np.median([(r['obs'][key]-r['HXLOC'][key]['mean'])/r['HXLOC'][key]['sd'] for r in rows])
        ma=np.median([r['HXACT'][key]['mean'] for r in rows]);ml=np.median([r['HXLOC'][key]['mean'] for r in rows])
        print(f'{key:22s} obs={o:+.4f} HXACT={ma:+.4f} (z {za:+.2f}) HXLOC={ml:+.4f} (z {zl:+.2f})')
