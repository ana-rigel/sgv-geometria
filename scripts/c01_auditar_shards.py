"""Fail-closed audit of complete C01 training/validation feature shards."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.c01_supervision_features import SIZES, CASES, BASE_KEYS,HDR_KEYS,SCHEMA

def audit(files):
    docs=[json.loads(Path(f).read_text(encoding='utf8')) for f in files]
    if not docs: raise ValueError('no shards')
    found={}
    summary={}
    for split in ('training','validation'):
        subset=[d for d in docs if d.get('split')==split]
        if not subset: raise ValueError('missing '+split)
        shard_count=subset[0]['total_shards']
        if shard_count<1 or {d['total_shards'] for d in subset}!={shard_count}:
            raise ValueError('incompatible shards')
        if sorted(d['shard'] for d in subset)!=list(range(shard_count)):
            raise ValueError('missing/duplicate shard in '+split)
        counts={c:0 for c in CASES}
        expected_rows=SIZES[split]*len(CASES)
        for d in subset:
            if d['schema']!=SCHEMA or d['feature_names']!={'base':list(BASE_KEYS),'hdr':list(HDR_KEYS)}:
                raise ValueError('schema or features mismatch')
            if d['test_partition_accessed'] or d['market_data_accessed']:
                raise ValueError('sealed data access claimed')
            for row in d['rows']:
                if row['split']!=split or row['case'] not in CASES or not 0<=row['replicate']<SIZES[split]:
                    raise ValueError('unexpected case/replicate')
                identity=row['id']
                if identity in found: raise ValueError('duplicate case')
                if identity!=f"{split}/{row['case']}/{row['replicate']}":
                    raise ValueError('id mismatch')
                if row['sha256_A']==row['sha256_B']:
                    raise ValueError('same A/B hash')
                if len(row['base'])!=len(BASE_KEYS) or len(row['hdr'])!=len(HDR_KEYS):
                    raise ValueError('incomplete vectors')
                if not np.isfinite(row['base']+row['hdr']).all():
                    raise ValueError('nonfinite feature')
                if any(abs(v)>.015 for v in row['coverage'].values()):
                    raise ValueError('failed coverage gate')
                found[identity]=row
                counts[row['case']]+=1
        if sum(d['requested'] for d in subset)!=expected_rows:raise ValueError('missing requested IDs')
        valid=min(counts.values())
        if any(counts[c]!=SIZES[split] for c in CASES):
            raise ValueError('missing sample or calibration failure: fail-closed')
        summary[split]={'complete':True,'n':expected_rows,'per_class':counts,'shards':shard_count}
    return {'status':'READY_FOR_DESCRIPTIVE_TRAIN_VALIDATION','test_accessed':False,
            'train_validation':summary,'schema':SCHEMA,
            'note':'This audit does NOT open classification holdout and is NOT a scientific result'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('shards',nargs='+')
    p.add_argument('--out',required=True)
    a=p.parse_args()
    report=audit(a.shards)
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'])

if __name__=='__main__':main()
