#!/usr/bin/env python3
"""SGV-M28 exploratory diagnostic: WHERE is the HSIC excess left by M27's HXLOC?

Runs only on the EVEN exploratory origins (0,2,...,82); odd origins are held out
for the pre-registered M28 test. For each origin: observed window vs 19 HXLOC
references, decomposed dependence at lags 5 and 30 on in-window copula scores u:
  lin[i,j]  = corr(u_i,t , u_j,t+k)
  vol[i,j]  = corr(|u_i,t| , |u_j,t+k|)
  lev[i,j]  = corr(u_i,t , |u_j,t+k|)      (sign -> future magnitude)
  m2d[i,j]  = corr(|u_i,t| , u_j,t+k)      (magnitude -> future sign)
  sq[i,j]   = corr(u_i,t^2 , u_j,t+k)      (curvature, = m2d with squares)
  hs[i,j]   = 1D HSIC(u_i,t , u_j,t+k)
Output: per component the median z-score (obs - mean ref)/sd ref and the share of
origins with obs above / below all references.
"""
from __future__ import annotations
import json,sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates
from experiments.precisao_formas_3d import gaussianize_three
from experiments.m5_validacao_conjunta_sf1 import WINDOW
from experiments.m12_nulos_regimes_temporais import PREFIX
from experiments.m16_trio_btc_exploratorio import load
from experiments.m21b_dependencia_btc import copula,hsic
from experiments import m27_nao_estacionariedade as m27

REFS=19
LAGS=(5,30)
NAMES=('z','iota','nu')
KINDS=('lin','vol','lev','m2d','sq','hs')


def corr(a,b):
    a=a-a.mean();b=b-b.mean();return float(a@b/np.sqrt((a@a)*(b@b)))


def comps(x):
    u=copula(x);out={}
    for l in LAGS:
        a,b=u[:-l],u[l:]
        for i in range(3):
            for j in range(3):
                tag=f'{NAMES[i]}>{NAMES[j]}@{l}'
                out['lin|'+tag]=corr(a[:,i],b[:,j])
                out['vol|'+tag]=corr(np.abs(a[:,i]),np.abs(b[:,j]))
                out['lev|'+tag]=corr(a[:,i],np.abs(b[:,j]))
                out['m2d|'+tag]=corr(np.abs(a[:,i]),b[:,j])
                out['sq|'+tag]=corr(a[:,i]**2,b[:,j])
                out['hs|'+tag]=hsic(a[:,[i]],b[:,[j]])
        out[f'hsic3d@{l}']=hsic(a,b)
    return out


def one(k):
    df,starts=load('1m');start=starts[k]
    pre=PREFIX['1m'];w=WINDOW['1m']
    prefix=df.iloc[start-pre:start].copy();fut=df.iloc[start:start+w].copy()
    actual=flow_coordinates(pd.concat([prefix,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-w:]
    raw=flow_coordinates(prefix)[['z','iota','nu']].to_numpy(float)
    raw=raw[int(np.flatnonzero(np.isfinite(raw).all(axis=1))[0]):]
    ns=gaussianize_three(raw,raw)
    try:f,_=m27.fit_local(ns,m27.seed_int(k,2)+50)
    except Exception as e:return {'origin':k,'status':'fit_failed','error':str(e)}
    obs=comps(actual);refs=[]
    for j in range(REFS):
        sim=f(np.random.default_rng(m27.seed_int(k,8,j)),w)
        refs.append(comps(sim))
    out={}
    for key,v in obs.items():
        r=np.array([q[key] for q in refs])
        out[key]={'obs':v,'z':float((v-r.mean())/r.std()),'above_all':bool(v>r.max()),'below_all':bool(v<r.min())}
    return {'origin':k,'status':'valid','comps':out}


def main():
    ks=list(range(0,84,2))
    with Pool(2) as p:rows=p.map(one,ks)
    val=[r for r in rows if r['status']=='valid']
    keys=list(val[0]['comps'])
    summ={}
    for key in keys:
        z=np.array([r['comps'][key]['z'] for r in val])
        summ[key]={'median_z':float(np.median(z)),'frac_z_pos':float(np.mean(z>0)),
                   'frac_above_all':float(np.mean([r['comps'][key]['above_all'] for r in val])),
                   'frac_below_all':float(np.mean([r['comps'][key]['below_all'] for r in val])),
                   'median_obs':float(np.median([r['comps'][key]['obs'] for r in val]))}
    od=ROOT/'reports'/'m28diag';od.mkdir(parents=True,exist_ok=True)
    (od/'diag_pares.json').write_text(json.dumps({'origins':ks,'n_valid':len(val),'summary':summ,'rows':rows},indent=1)+'\n')
    top=sorted(summ.items(),key=lambda kv:-abs(kv[1]['median_z']))[:25]
    for k,v in top:print(f"{k:22s} medz={v['median_z']:+.2f} pos={v['frac_z_pos']:.2f} above={v['frac_above_all']:.2f} below={v['frac_below_all']:.2f} obs={v['median_obs']:+.4f}")


if __name__=='__main__':main()
