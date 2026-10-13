#!/usr/bin/env python3
"""Run the SGV H-J/H-GEO bridge with SYNTHETIC or PRE-EXPLORED BTC only.

No downloader, no August+ BTC, no ETH/SOL/BNB; this is EXPLORATORY ENGINEERING.
CLI requires --btc-dir with May/June/July 2026 Binance spot 1m monthly zips
and a SHA256SUMS file, e.g. path to the user's 'navegador_sgv/dados'.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
from sgvgeo.flow import flow_coordinates
from experiments.precisao_formas_3d import gaussianize_three
from sgv_bridge.engine import (
    SEED,WINDOW,TRAIN_P,N_NODES,synthetic_hj,
    codebook,classify,models_from_A,heldout_logscore,geometry_forecast,
)

COLS=('timestamp','open','high','low','close','volume','close_time',
      'quote_volume','trades','taker_buy','taker_buy_quote','ignore')
FILES=tuple(f'BTCUSDT-1m-2026-{month}.zip' for month in ('05','06','07'))

def read_verified_btc(d):
    d=Path(d)
    expected={}
    for line in (d/'SHA256SUMS').read_text().splitlines():
        if line.strip():
            sha,name=line.split()
            expected[name.lstrip('*')]=sha.lower()
    result=[]
    for name in FILES:
        if name not in expected:
            raise ValueError('Missing recorded exchange SHA256 for '+name)
        binary=(d/name).read_bytes()
        digest=hashlib.sha256(binary).hexdigest()
        if expected[name]!=digest:
            raise ValueError('Bad SHA256 for '+name)
        with zipfile.ZipFile(d/name) as z:
            df=pd.read_csv(z.open(z.namelist()[0]),names=COLS,header=None)
        df=df[['timestamp','close','volume','taker_buy']]
        if int(df.timestamp.iloc[0])>1e14:
            df['timestamp']=df.timestamp//1000
        result.append(df)
    out=pd.concat(result,ignore_index=True)
    ts=out.timestamp.to_numpy(np.int64)
    assert np.all(np.diff(ts)==60000), 'gaps/duplicates/non-1m timestamps'
    assert ts[0]>=pd.Timestamp('2026-05-01',tz='UTC').value//10**6
    assert ts[-1]<pd.Timestamp('2026-08-01',tz='UTC').value//10**6
    return out

def run_btc(data_dir,n_hj=30,n_geo=3,grid=35):
    df=read_verified_btc(data_dir)
    coord=flow_coordinates(df)
    raw=coord[['z','iota','nu']].to_numpy(dtype=float)
    ok=np.isfinite(raw).all(1)
    ts=df.timestamp.to_numpy(np.int64)
    may=ts<pd.Timestamp('2026-06-01',tz='UTC').value//10**6
    anchor=raw[ok&may]
    if len(anchor)<1500:raise ValueError('May calibration too short')
    X=np.full_like(raw,np.nan)
    X[ok]=gaussianize_three(anchor,raw[ok])
    mu,sd,cent=codebook(X[may&ok])
    first=int(np.flatnonzero(~may)[0])
    records=[]
    for j in range(max(n_hj,n_geo)):
        if j>=n_hj:break
        split=first+j*WINDOW
        if split+WINDOW>len(X):break
        A=X[split-WINDOW:split];B=X[split:split+WINDOW]
        if not np.isfinite(np.vstack([A,B])).all():
            records.append({'block':j,'invalid':'missing history features'})
            continue
        na=classify(A,mu,sd,cent)
        nb=classify(B,mu,sd,cent)
        models=models_from_A(na[-TRAIN_P:],N_NODES,seed=SEED+j)
        scores=heldout_logscore(models,int(na[-1]),nb)
        row={'block':j,
             'A_start':str(pd.Timestamp(ts[split-WINDOW],unit='ms',tz='UTC')),
             'B_start':str(pd.Timestamp(ts[split],unit='ms',tz='UTC')),
             'B_end':str(pd.Timestamp(ts[split+WINDOW-1],unit='ms',tz='UTC')),
             'H_J_log_scores':scores,
             'H_J_rtt_minus_reversible':scores['rtt']-scores['reversible']}
        if j<n_geo:
            try:
                row['H_GEO']=geometry_forecast(
                    A,B,na,models,int(na[-1]),seed=SEED+100*j,grid=grid)
            except (ValueError,RuntimeError,np.linalg.LinAlgError) as exc:
                row['H_GEO_invalid']=str(exc)
        records.append(row)
    return {'scope':'engineering/exploratory only, BTC May-Jul 2026',
            'n_nodes':N_NODES,'block_length':WINDOW,'n_HJ':n_hj,'n_HGEO':n_geo,
            'records':records,'no_new_holdout':True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['synthetic','btc-exploratory'],default='synthetic')
    p.add_argument('--btc-dir',type=Path)
    p.add_argument('--n-hj',type=int,default=30)
    p.add_argument('--n-geo',type=int,default=3)
    p.add_argument('--grid',type=int,default=35)
    p.add_argument('--output',type=Path,default=Path('reports/rtt_bridge_results.json'))
    args=p.parse_args()
    if args.mode=='btc-exploratory':
        if args.btc_dir is None:p.error('btc-exploratory requires --btc-dir')
        if args.n_hj<0 or args.n_geo<0 or args.n_geo>args.n_hj:
            p.error('Require n_hj >= n_geo >= 0')
        result=run_btc(args.btc_dir,args.n_hj,args.n_geo,args.grid)
    else:
        result={'synthetic':synthetic_hj(),'not_confirmatory':True}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('Saved:',args.output)
    if 'synthetic' in result:
        for k,v in result['synthetic'].items():
            print(k, 'RTT - reversible:',round(v['rtt_minus_reversible'],5))
    else:
        values=[r['H_J_rtt_minus_reversible'] for r in result['records']
                if 'H_J_rtt_minus_reversible' in r]
        if values:
            print('H-J:',len(values),'mean RTT - reversible:',float(np.mean(values)),
                  'positive:',sum(x>0 for x in values))
        print('H-GEO blocks with reports:',sum('H_GEO' in r for r in result['records']))

if __name__=='__main__':main()
