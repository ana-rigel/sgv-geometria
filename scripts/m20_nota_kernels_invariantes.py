import sys,time,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiments.m20d_ablacao_fatorial import make_truth
from scipy.spatial.distance import cdist
def gauss_hsic(x,y):
    n=len(x);H=np.eye(n)-1/n
    def K(z):
        d=cdist(z,z,'sqeuclidean');s=np.median(d[d>0]);return np.exp(-d/s)
    return float(np.sum((H@K(x)@H)*K(y))/n**2)
def dcov(x,y):
    def A(z):
        d=cdist(z,z);return d-d.mean(0)-d.mean(1)[:,None]+d.mean()
    return float(np.mean(A(x)*A(y)))
rng=np.random.default_rng(1)
for n in (500,1800):
  for stat in (gauss_hsic,dcov):
    t=time.time()
    null=[];alt={}
    for _ in range(100):
        x=make_truth(n+1,0,rng)
        x=np.asarray(x[0] if isinstance(x,tuple) else x)[:n+1]
        null.append(stat(x[:-1],x[1:]))
    thr=np.quantile(null,.95)
    for sid,nm in ((2,'H+'),(3,'H-'),(4,'VOL')):
        c=0
        for _ in range(40):
            x=make_truth(n+1,sid,rng); x=np.asarray(x[0] if isinstance(x,tuple) else x)[:n+1]
            c+=stat(x[:-1],x[1:])>thr
        alt[nm]=c/40
    print(n,stat.__name__,alt,'%.0fs'%(time.time()-t),flush=True)
