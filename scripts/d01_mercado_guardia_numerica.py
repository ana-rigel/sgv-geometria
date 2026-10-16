"""D01 financial exploratory ONLY: numerical-consistency guard across GH runners.

Uses exact frozen scientific models and original test_market to compute scores.
Allows ONLY an in-memory checksum guard substitution after stringent
same-run prefix identity and frozen model mean/scale equivalence.
No synthetic heldout execution; no Oct/Nov.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pipeline import sgv_d01_direcao as d

EXPECTED_SOURCE_BLOB="c7ef72ae2e6d72f79c7dade06013a3c7add0cdc8"
EXPECTED_FREEZE_BLOB="142f4ffafa3c9b8fdb676fa271a5306a37acd736"
EXPECTED_TRAIN_N=85760
TOL=1e-8

def blob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def selected(ts,t,x,y):
    yy=ts.iloc[t+1]
    m=((yy>=pd.Timestamp("2026-06-01",tz="UTC"))&
       (yy<pd.Timestamp("2026-08-01",tz="UTC"))).to_numpy()
    return t[m],np.ascontiguousarray(x[m]),y[m]

def audit(data_dir,frozen):
    if blob("pipeline/sgv_d01_direcao.py")!=EXPECTED_SOURCE_BLOB or \
       blob("resultados/d01_modelos_congelados.json")!=EXPECTED_FREEZE_BLOB:
        raise RuntimeError("frozen source/JSON blob changed")
    if not Path("resultados/d01_TEST_RELEASE.txt").exists() or \
       not Path("resultados/d01_sinteticos_teste_final.json").exists():
        raise RuntimeError("synthetic release/result not preserved")
    if Path("resultados/d01_mercado_agoset_exploratorio.json").exists():
        raise RuntimeError("market result already exists")
    _,ts0,t0,x0,y0=d.read_market_data(['2026-05','2026-06','2026-07'],data_dir)
    _,ts1,t1,x1,y1=d.read_market_data(['2026-05','2026-06','2026-07','2026-08','2026-09'],data_dir)
    i0,a,b=selected(ts0,t0,x0,y0)
    i1,c,z=selected(ts1,t1,x1,y1)
    if len(b)!=EXPECTED_TRAIN_N or len(z)!=EXPECTED_TRAIN_N:
        raise RuntimeError("unexpected train sample count")
    if not np.array_equal(i0,i1) or not np.array_equal(b,z) or not np.array_equal(a,c):
        raise RuntimeError("same-run causal prefix, labels or indices not bitwise identical")
    if a.shape[1]!=19:
        raise RuntimeError("unexpected feature count")
    checkpoints={}
    for arm,n in d.ARMS.items():
        ss=StandardScaler().fit(a[:,:n])
        m=frozen['market']['models'][arm]
        dm=np.max(np.abs(ss.mean_-np.asarray(m['mean'])))
        ds=np.max(np.abs(ss.scale_-np.asarray(m['scale'])))
        if not np.allclose(ss.mean_,m['mean'],atol=TOL,rtol=TOL) or \
           not np.allclose(ss.scale_,m['scale'],atol=TOL,rtol=TOL):
            raise RuntimeError(f'frozen model scale mismatch {arm}: {dm} {ds}')
        checkpoints[arm]={'max_abs_diff_mean':float(dm),'max_abs_diff_scale':float(ds),
                          'feature_count':n}
    curr_hash=hashlib.sha256(np.ascontiguousarray(np.column_stack((a,b))).tobytes()).hexdigest()
    return {'original_sha256':frozen['market']['train_sha256'],'in_run_sha256':curr_hash,
            'full_prefix_sha256':hashlib.sha256(np.ascontiguousarray(np.column_stack((c,z))).tobytes()).hexdigest(),
            'strict_same_run_prefix_identical':True,'n':len(b),
            'model_scaler_checks':checkpoints,
            'tolerance_atol_rtol':TOL,
            'original_frozen_file_unmodified':True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dados',default='dados')
    ap.add_argument('--freeze',default='resultados/d01_modelos_congelados.json')
    ap.add_argument('--out',default='resultados/d01_mercado_agoset_exploratorio.json')
    ar=ap.parse_args()
    if ar.freeze!="resultados/d01_modelos_congelados.json":
        raise RuntimeError("unexpected frozen model path")
    frozen_sha=hashlib.sha256(Path(ar.freeze).read_bytes()).hexdigest()
    frozen,_=d.load_frozen(ar.freeze,frozen_sha)
    guard=audit(ar.dados,frozen)
    print("GUARDS_PASSED",json.dumps(guard,ensure_ascii=False),flush=True)
    surrogate=copy.deepcopy(frozen)
    # Only repair *integrity checksum metadata*, never classifiers.
    surrogate['market']['train_sha256']=guard['in_run_sha256']
    d.test_market(ar.dados,surrogate,frozen_sha,ar.out)
    obj=json.loads(Path(ar.out).read_text())
    obj['cross_runner_audit']=guard
    obj['original_frozen_market_models_checksum_preserved']=frozen_sha
    d.write_json(ar.out,obj)
    print("DONE_MARKET_NO_RETUNING",obj['results']['D_geom'],obj['results']['D_hist'])

if __name__=='__main__':main()
