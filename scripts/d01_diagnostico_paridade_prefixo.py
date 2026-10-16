"""Read-only D01 diagnostic: compare May-Jul training prefix with May-Sep full context.

This does not fit or test classifiers, does not regenerate any heldout synthetic pair,
nor read Oct/Nov. The goal is to explain a failed invariant in the first market run.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from pipeline import sgv_d01_direcao as d

def train_selected(ts,t,X,y):
    mask=((ts.iloc[t+1]>=pd.Timestamp('2026-06-01',tz='UTC')) &
          (ts.iloc[t+1]<pd.Timestamp('2026-08-01',tz='UTC'))).to_numpy()
    return t[mask],X[mask],y[mask]

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument('--dados',default='dados')
    arg.add_argument('--out',required=True)
    a=arg.parse_args()
    _,ts0,t0,X0,y0=d.read_market_data(['2026-05','2026-06','2026-07'],a.dados)
    _,ts1,t1,X1,y1=d.read_market_data(['2026-05','2026-06','2026-07','2026-08','2026-09'],a.dados)
    i0,b0,c0=train_selected(ts0,t0,X0,y0)
    i1,b1,c1=train_selected(ts1,t1,X1,y1)
    res={'n_orig':len(c0),'n_full':len(c1),'same_training_indices':bool(np.array_equal(i0,i1)),
         'same_training_labels':bool(np.array_equal(c0,c1)),
         'columns':[]}
    if np.array_equal(i0,i1) and b0.shape==b1.shape:
        for j,name in enumerate(d.FEATURE_NAMES):
            z=np.abs(b0[:,j]-b1[:,j])
            different=np.flatnonzero(z>0)
            res['columns'].append({'name':name,'n_bitdiff':int(len(different)),
                'max_abs_diff':float(z.max()),'n_gt_1e-10':int((z>1e-10).sum()),
                'first_different':int(different[0]) if len(different) else None})
    res['diagnosis']='PREFIX_PARITY' if all(col['n_bitdiff']==0 for col in res['columns']) and res['same_training_labels'] else 'PREFIX_NOT_BYTE_IDENTICAL'
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(res,ensure_ascii=False))

if __name__=='__main__':main()
