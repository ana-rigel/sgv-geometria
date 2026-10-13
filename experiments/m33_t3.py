#!/usr/bin/env python3
"""SGV-M33 — T3 original do M31 como teste proprio (ENGENHARIA).
B1plus = B0 + elasticidade movel + forma ; B2 = B1plus + area em sela da casca.
Reutiliza SEM ALTERAR m32_casca (elegibilidade so pelo passado, treino so com rotulos validos)
e m31g1_engenharia (variaveis, elasticidade, casca). So acrescenta 'elast' e 'elast_x_nu'.
Origem cuja elasticidade e degenerada (decidido so pelo passado) fica fora."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates
from experiments import m31g1_engenharia as g
from experiments import m32_casca as m32
from experiments.m31g0_features_causais import synthetic_klines,qlike_deviance

B1PLUS=g.MODELS['B1plus'];B2=g.MODELS['B2'];W=g.W;MIN=g.MIN;H=g.H
rolling_forecasts=m32.rolling_forecasts


def segment_rows(seg):
    seg=seg.reset_index(drop=True);rows=m32.segment_rows(seg)
    if not rows:return []
    co=flow_coordinates(seg);z=co['z'].to_numpy(float);nu=co['nu'].to_numpy(float)
    pos={int(t):k for k,t in enumerate(seg.timestamp.to_numpy(np.int64))};out=[]
    for r in rows:
        i=pos[r['origin_ts']];el=g.elasticity(z[i-W+1:i+1],nu[i-W+1:i+1])
        if el is None:continue
        r=dict(r);r['elast']=el;r['elast_x_nu']=el*float(nu[i]);out.append(r)
    return out


def build(frame):
    frame=frame.sort_values('timestamp').reset_index(drop=True)
    ts=frame.timestamp.to_numpy(np.int64);rows=[];segs=g.segments(ts)
    for a,b in segs:rows+=segment_rows(frame.iloc[a:b])
    d=pd.DataFrame(rows)
    if d.empty:raise ValueError('sem origens elegiveis')
    d=d.sort_values('origin_ts').reset_index(drop=True);d['label_matures_ts']=d.origin_ts+H*MIN
    return d,{'n_segmentos':len(segs),'maior_segmento_min':int(max(b-a for a,b in segs))}
