"""C01 supervised preparation. No access to the sealed test split.

Shard computation for TRAINING / VALIDATION only. Calibration smoke uses IDs >=2m.
No classifier scoring until complete manifests pass gates.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments.c01_estimacao_independente import (
    independent_pair,estimate_pair,baseline_features,hdr_features,
)
CASES=tuple(f'T{i}' for i in range(7))
SIZES={'training':80,'validation':20,'calibration':2}
BASE_KEYS=tuple([f'delta_mu_{i}' for i in range(3)]+[
    f'delta_cov_{i}{j}' for i in range(3) for j in range(i,3)]+
    ['logdet_cov_delta','entropy_delta','fr_cov','fr_ambient','energy'])
HDR_KEYS=tuple(f'{prefix}_{suffix}' for prefix in ('hdr50','hdr95') for suffix in (
    'center_distance','log_volume_ratio','log_area_ratio',
    'delta_components','voxel_iou_loss','shape_tensor_diff'))
MC=32000
GRID=35
COVER_TOL=.015
SCHEMA='SGV-C01-supervision-v1'

def indices(split,shard,total_shards):
    if split not in SIZES or total_shards<1 or not 0<=shard<total_shards:
        raise ValueError('invalid shard; test partition remains sealed')
    # calibration smoke must be outside the pilot and official IDs.
    n=SIZES[split]
    return [(cls, (2_000_000+i if split=='calibration' else i))
            for cls in CASES for i in range(n) if i%total_shards==shard]

def record(split,case,rep):
    pair=independent_pair(case,rep,split=split)
    fa,fb=estimate_pair(pair)
    base=baseline_features(pair,fa,fb,n_mc=MC)
    hdr=hdr_features(pair,fa,fb,grid_n=GRID,cutoff_n=MC,cover_n=MC)
    for k in BASE_KEYS+HDR_KEYS:
        if k not in (base|hdr) or not np.isfinite((base|hdr)[k]):
            raise ValueError('invalid or missing frozen feature: '+k)
    cover={k:float(v) for k,v in hdr.items() if k.startswith('_num_')}
    if any(abs(v)>COVER_TOL for v in cover.values()):
        raise ValueError('HDR mass coverage gate failed')
    return {
        'id':f'{split}/{case}/{rep}','case':case,'split':split,'replicate':rep,
        'sha256_A':pair.a_sha256,'sha256_B':pair.b_sha256,
        'base':[float(base[k]) for k in BASE_KEYS],
        'hdr':[float(hdr[k]) for k in HDR_KEYS],
        'coverage':cover,
        'fit_iterations':[fa.iterations,fb.iterations],
    }

def compute(split,shard,total_shards):
    rows=[];errors=[]
    for case,rep in indices(split,shard,total_shards):
        start=time.monotonic()
        try:
            r=record(split,case,rep)
            r['elapsed_s']=round(time.monotonic()-start,4)
            rows.append(r)
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as exc:
            errors.append({'case':case,'replicate':rep,'error_type':type(exc).__name__,
                           'error':str(exc)})
    out={'schema':SCHEMA,'status':'VALIDATION_DESCRIPTIVE_ONLY' if split=='validation'
         else 'TRAINING_FEATURES_ONLY' if split=='training' else 'ENGINEERING_SMOKE_ONLY',
         'split':split,'shard':shard,'total_shards':total_shards,
         'feature_names':{'base':BASE_KEYS,'hdr':HDR_KEYS},
         'mc':MC,'grid':GRID,'rows':rows,'errors':errors,
         'requested':len(indices(split,shard,total_shards)),
         'valid':len(rows),'test_partition_accessed':False,'market_data_accessed':False}
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--split',choices=tuple(SIZES),required=True)
    p.add_argument('--shard',type=int,default=0)
    p.add_argument('--total-shards',type=int,default=1)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    d=compute(a.split,a.shard,a.total_shards)
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    dest.write_text(payload,encoding='utf-8')
    print(d['status'],d['valid'],'/',d['requested'],'errors',len(d['errors']),
          'sha256',hashlib.sha256(payload.encode()).hexdigest(),flush=True)
    return 0 if not d['errors'] else 2

if __name__=='__main__':
    raise SystemExit(main())
