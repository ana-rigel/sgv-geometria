"""C01 supervision controls; no official samples are generated in these tests."""
import json
from pathlib import Path
import numpy as np
import pytest
from scripts.c01_supervision_features import (
    BASE_KEYS,HDR_KEYS,CASES,SIZES,indices,compute,
)
from scripts.c01_auditar_shards import audit

def test_feature_contract():
    assert len(BASE_KEYS)==14 and len(HDR_KEYS)==12
    assert len(set(BASE_KEYS+HDR_KEYS))==26

def test_partitions_and_test_seal():
    assert len(indices('training',0,1))==560
    assert len(indices('validation',0,1))==140
    assert len(indices('calibration',0,1))==14
    with pytest.raises(ValueError):
        indices('test',0,1)

def test_shard_exhaustive_disjoint():
    allrows=[indices('training',i,7) for i in range(7)]
    ids=[x for shard in allrows for x in shard]
    assert len(ids)==len(set(ids))==560

def fixture_documents(tmp_path):
    paths=[]
    for split in ('training','validation'):
        rows=[]
        for cls in CASES:
            for rep in range(SIZES[split]):
                rows.append({'id':f'{split}/{cls}/{rep}','split':split,'case':cls,
                    'replicate':rep,'sha256_A':f'A{split}{cls}{rep}',
                    'sha256_B':f'B{split}{cls}{rep}',
                    'base':[0.0]*14,'hdr':[0.0]*12,'coverage':{'_num_hdr50_coverage_error_a':0.}})
        data={'schema':'SGV-C01-supervision-v1','split':split,'shard':0,'total_shards':1,
              'feature_names':{'base':list(BASE_KEYS),'hdr':list(HDR_KEYS)},
              'test_partition_accessed':False,'market_data_accessed':False,
              'requested':len(rows),'rows':rows,'errors':[]}
        file=tmp_path/f'{split}.json'
        file.write_text(json.dumps(data))
        paths.append(file)
    return paths

def test_audit_complete_fixture(tmp_path):
    r=audit(fixture_documents(tmp_path))
    assert r['status']=='READY_FOR_DESCRIPTIVE_TRAIN_VALIDATION'
    assert r['train_validation']['training']['n']==560

def test_audit_rejects_missing(tmp_path):
    paths=fixture_documents(tmp_path)
    d=json.loads(paths[0].read_text())
    d['rows'].pop()
    paths[0].write_text(json.dumps(d))
    with pytest.raises(ValueError,match='missing sample'):
        audit(paths)

def test_audit_rejects_duplicate(tmp_path):
    paths=fixture_documents(tmp_path)
    d=json.loads(paths[0].read_text())
    d['rows'].append(d['rows'][0])
    paths[0].write_text(json.dumps(d))
    with pytest.raises(ValueError,match='duplicate'):
        audit(paths)

def test_audit_rejects_same_samples(tmp_path):
    paths=fixture_documents(tmp_path)
    d=json.loads(paths[1].read_text())
    d['rows'][0]['sha256_B']=d['rows'][0]['sha256_A']
    paths[1].write_text(json.dumps(d))
    with pytest.raises(ValueError,match='same A/B'):
        audit(paths)

def test_audit_rejects_failed_coverage(tmp_path):
    paths=fixture_documents(tmp_path)
    d=json.loads(paths[1].read_text())
    d['rows'][0]['coverage']['_num_hdr50_coverage_error_a']=.05
    paths[1].write_text(json.dumps(d))
    with pytest.raises(ValueError,match='coverage'):
        audit(paths)

def test_audit_rejects_test_access_claim(tmp_path):
    paths=fixture_documents(tmp_path)
    d=json.loads(paths[1].read_text())
    d['test_partition_accessed']=True
    paths[1].write_text(json.dumps(d))
    with pytest.raises(ValueError,match='sealed data'):
        audit(paths)
