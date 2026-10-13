"""SGV M34 CLI: only synthetic or strict exploratory May-Jul BTC."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .core import run_btc,json_ready
from .synthetic import run_synthetic
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['synthetic','btc-exploratory'],default='synthetic')
    p.add_argument('--btc-dir',type=Path)
    p.add_argument('--episodes',type=int,default=None)
    p.add_argument('--grid',type=int,default=35)
    p.add_argument('--out',type=Path,default=Path('reports/m34_synthetic.json'))
    a=p.parse_args()
    if a.mode=='synthetic':r=run_synthetic(n_episodes=a.episodes or 60)
    else:
        if not a.btc_dir:p.error('--btc-dir required')
        r=run_btc(a.btc_dir,a.episodes or 24,a.grid)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(json_ready(r),ensure_ascii=False,indent=2,
                                allow_nan=False)+'\n')
    print('Saved',a.out)
    if 'test_differences_nats' in r:print(r['test_differences_nats'])
    else:
        for k,v in r['scenarios'].items():print(k,v['test_differences_nats'])
if __name__=='__main__':main()
