"""C01 deterministic comparison of two fixed pipelines, descriptive validation only.

Consumes only a COMPLETE audited feature table (training and validation).
Never reads the sealed test partition. No hyperparameter search.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, balanced_accuracy_score, f1_score, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.c01_auditar_shards import audit
from scripts.c01_supervision_features import BASE_KEYS,HDR_KEYS,CASES

def matrix(files):
    audit(files)  # abort if missing/duplicated/failing any records
    docs=[json.loads(Path(x).read_text(encoding='utf8')) for x in files]
    grouped={}
    for split in ('training','validation'):
        rows=sorted((r for d in docs if d['split']==split for r in d['rows']),
                    key=lambda r:(r['case'],r['replicate']))
        y=np.array([CASES.index(r['case']) for r in rows],dtype=int)
        xb=np.array([r['base'] for r in rows],float)
        xh=np.array([r['hdr'] for r in rows],float)
        grouped[split]=(xb,xh,y)
    return grouped

def run(files):
    grouped=matrix(files)
    trb,trh,ytr=grouped['training']
    vab,vah,yva=grouped['validation']
    results={}
    for name,xtrain,xval in (
        ('base',trb,vab),
        ('base_plus_hdr',np.column_stack([trb,trh]),np.column_stack([vab,vah])),
    ):
        clf=make_pipeline(StandardScaler(),
                          LogisticRegression(C=1.0,solver='lbfgs',max_iter=2000))
        clf.fit(xtrain,ytr)
        prob=clf.predict_proba(xval)
        pred=clf.predict(xval)
        results[name]={
            'log_loss':float(log_loss(yva,prob,labels=list(range(len(CASES))))),
            'balanced_accuracy':float(balanced_accuracy_score(yva,pred)),
            'macro_f1':float(f1_score(yva,pred,average='macro')),
            'confusion':confusion_matrix(yva,pred,labels=list(range(len(CASES)))).tolist(),
            'n_features':int(xtrain.shape[1]),
            'training_n':int(len(ytr)),'validation_n':int(len(yva)),
        }
    return {'status':'VALIDATION_DESCRIPTIVE_ONLY',
            'no_hypothesis_judgment':True,'sealed_test_executed':False,
            'features_base':list(BASE_KEYS),'features_hdr':list(HDR_KEYS),
            'class_order':list(CASES),
            'results':results,'validation_logloss_delta_descriptive_only':
                results['base']['log_loss']-results['base_plus_hdr']['log_loss']}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('shards',nargs='+')
    p.add_argument('--out',required=True)
    a=p.parse_args()
    report=run(a.shards)
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(report['status'],'delta_logloss',report['validation_logloss_delta_descriptive_only'])

if __name__=='__main__':main()
