#!/usr/bin/env python3
"""SGV-M32 — a curvatura da casca acrescenta informacao de risco? (ENGENHARIA)

Reaproveita, sem alterar, as funcoes congeladas de experiments/m31g1_engenharia.py
(forma original, casca, variaveis do B0) e corrige o que a auditoria do M31 apontou:
  * ELEGIBILIDADE SEM FUTURO: a origem recebe previsao se o PASSADO permitir (janelas e
    defasagens validas); a disponibilidade do alvo so decide se ela entra na AVALIACAO.
  * TREINO so com rotulos maturados, finitos e positivos (linhas sem alvo nunca entram no ajuste).
  * Casca invalida numa origem: a origem fica fora do teste principal (para os dois modelos).
Modelos: B1 = B0 + forma (cone, cintura, cone x nu); B1S = B1 + area em sela da casca HDR50.
"""
from __future__ import annotations
import math,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.flow import flow_coordinates
from experiments import m31g1_engenharia as g
from experiments.m31g0_features_causais import target_rv_forward,qlike_deviance,synthetic_klines

MIN=g.MIN;W=g.W;H=g.H;STEP=g.STEP;WARM=g.WARM;RVS=g.RVS
TRAIN=g.TRAIN;RIDGE=g.RIDGE;EPS=g.EPS
B1=g.B0+g.SHAPE
B1S=B1+g.SHELL
MODELS={'B1':B1,'B1S':B1S}


def segment_rows(seg):
    seg=seg.reset_index(drop=True);n=len(seg)
    if n<WARM+2:return []
    co=flow_coordinates(seg);r=co['r'].to_numpy(float);z=co['z'].to_numpy(float)
    iota=co['iota'].to_numpy(float);nu=co['nu'].to_numpy(float)
    ts=seg.timestamp.to_numpy(np.int64);vol=seg.volume.to_numpy(float)
    hl=np.log(seg.high.to_numpy(float)/seg.low.to_numpy(float));pk=hl*hl/(4*math.log(2))
    r2=r*r;r4=r2*r2;neg=np.where(r<0,r2,0.)
    rv={w:g._roll(r2,w) for w in RVS};rq60=g._roll(r4,60)*60/3;pk15=g._roll(pk,15);pk60=g._roll(pk,60)
    dn60=g._roll(neg,60);v15=g._roll(vol,15)/15;v60=g._roll(vol,60)/60;ai15=g._roll(np.abs(iota),15)/15
    fut=target_rv_forward(r,H);rows=[]
    for i in np.flatnonzero(((ts//MIN)%STEP==0)&(np.arange(n)>=WARM)):      # nenhuma condicao sobre o futuro
        zw,iw,vw=z[i-W+1:i+1],iota[i-W+1:i+1],nu[i-W+1:i+1]
        if not(np.isfinite(zw).all() and np.isfinite(iw).all() and np.isfinite(vw).all()):continue
        if not(np.isfinite(rv[1440][i]) and rv[15][i]>0 and rq60[i]>0 and pk15[i]>0 and pk60[i]>0 and rv[60][i]>0):continue
        cone,cint=g.shape_original(zw,iw,vw)
        if not np.isfinite(cone) or cone<=0:continue
        try:sad=g.shell_saddle(zw,iw,vw)
        except (ValueError,np.linalg.LinAlgError,RuntimeError):sad=None
        t=pd.Timestamp(int(ts[i]),unit='ms',tz='UTC');qh=t.minute//15;hod=t.hour+t.minute/60
        tgt=float(fut[i]) if (i<n-H and np.isfinite(fut[i]) and fut[i]>0) else np.nan   # so para avaliar/treinar
        row={'origin_ts':int(ts[i]),'rv_future_15':tgt,
             **{f'log_rv_{w}':float(np.log(rv[w][i])) for w in RVS},
             'harq_60':float(.5*np.log(rq60[i])-np.log(rv[60][i])),
             'log_pk_15':float(np.log(pk15[i])),'log_pk_60':float(np.log(pk60[i])),
             'down_share_60':float(dn60[i]/rv[60][i]),'log_vol_15':float(np.log(v15[i])),'log_vol_60':float(np.log(v60[i])),
             'nu':float(nu[i]),'abs_iota_15':float(ai15[i]),
             **{f'q15_{k}':float(qh==k) for k in (1,2,3)},
             **{f'{f}_hod{k}':float(fn(2*np.pi*k*hod/24)) for k in (1,2,3) for f,fn in (('sin',np.sin),('cos',np.cos))},
             **{f'weekday_{d}':float(t.dayofweek==d) for d in range(6)},
             'cone_log':float(np.log(cone)),'cintura':cint,'cone_log_x_nu':float(np.log(cone))*float(nu[i]),
             'saddle_frac':np.nan if sad is None else sad}
        row['harq_x_rv15']=row['harq_60']*row['log_rv_15']
        rows.append(row)
    return rows


def build(frame):
    frame=frame.sort_values('timestamp').reset_index(drop=True)
    ts=frame.timestamp.to_numpy(np.int64);rows=[];segs=g.segments(ts)
    for a,b in segs:rows+=segment_rows(frame.iloc[a:b])
    d=pd.DataFrame(rows)
    if d.empty:raise ValueError('sem origens elegiveis')
    d=d.sort_values('origin_ts').reset_index(drop=True);d['label_matures_ts']=d.origin_ts+H*MIN
    return d,{'n_segmentos':len(segs),'maior_segmento_min':int(max(b-a for a,b in segs))}


def rolling_forecasts(d,cols,train=TRAIN,ridge=RIDGE):
    """Previsao em TODA origem elegivel; ajuste so com os `train` rotulos mais recentes
    ja maturados (<= origem), finitos e positivos."""
    X=d[list(cols)].to_numpy(float);rv=d.rv_future_15.to_numpy(float)
    good=np.isfinite(rv)&(rv>0);y=np.where(good,np.log(np.where(good,rv,1.)),np.nan)
    ts=d.origin_ts.to_numpy(np.int64);mat=d.label_matures_ts.to_numpy(np.int64)
    gidx=np.flatnonzero(good);gmat=mat[gidx];out=np.full(len(d),np.nan)
    for k in range(len(d)):
        if not np.isfinite(X[k]).all():continue
        j=np.searchsorted(gmat,ts[k],side='right')
        if j<train:continue
        sl=gidx[j-train:j];Xt=X[sl];mu=Xt.mean(0);sd=Xt.std(0);sd=np.where(sd>1e-10,sd,1.)
        Z=np.column_stack([np.ones(train),(Xt-mu)/sd]);pen=np.diag([0.]+[ridge]*X.shape[1])
        beta=np.linalg.solve(Z.T@Z+pen,Z.T@y[sl]);res=y[sl]-Z@beta
        sm=float(np.mean(np.exp(np.clip(res,-30,15))))
        out[k]=float(np.exp(np.clip(np.r_[1.,(X[k]-mu)/sd]@beta,-30,15))*sm)
    return out
