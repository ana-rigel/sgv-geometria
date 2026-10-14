"""Engineering-only C01 pilot. No classification, test split or financial data."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from experiments.c01_estimacao_independente import pilot_record

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='reports/c01_piloto_estimacao.json')
    parser.add_argument('--mc',type=int,default=4000)
    args=parser.parse_args()
    if args.mc<2000 or args.mc%2:
        raise ValueError('even MC >=2000 required')
    rows=[]
    for case in ('T0','T1','T3','T6'):
        for rep in range(2):
            r=pilot_record(case,rep,n_mc=args.mc)
            rows.append(r)
            print('C01',case,rep,'center HDR50',round(r['hdr']['hdr50_center_distance'],5),
                  'IoU loss HDR50',round(r['hdr']['hdr50_voxel_iou_loss'],5))
    outcome={'status':'ENGINEERING_ONLY','n_per_arm':750,'estimated_gmm_components':3,
             'replicates_per_case':2,'heldout_classification_executed':False,
             'market_data_accessed':False,'rows':rows,
             'all_converged':all(x['fit']['A']['converged'] and x['fit']['B']['converged'] for x in rows)}
    path=Path(args.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(outcome,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return 0 if outcome['all_converged'] else 2

if __name__=='__main__':
    raise SystemExit(main())
