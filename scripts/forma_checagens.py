"""Checagens sem modelo (exploratorio): a casca tem cintura na diagonal compra/venda?
O espalhamento do retorno cresce com o volume?"""
import sys,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from forma_isosuperficie import windows
from experiments.precisao_formas_3d import split_historical
from scipy.stats import kurtosis,gaussian_kde,norm
for interval in ('1m','1h'):
    X=np.vstack([np.vstack(split_historical(xx)) for _,_,xx in windows(interval)])
    z,i,v=X.T;rho=np.corrcoef(z,i)[0,1];s=(z+i);s=s/s.std()
    kde=gaussian_kde(s)
    rng=np.random.default_rng(0);G=rng.multivariate_normal([0,0],[[1,rho],[rho,1]],size=200000);sg=G.sum(1);sg/=sg.std()
    print(interval,'n',len(X),'corr z-iota',round(rho,3),'curtose diagonal',round(kurtosis(s),3),
          'dens(0)/normal',round(kde(0)[0]/norm.pdf(0),3),'dens(±1)/normal',np.round(kde([-1,1])/norm.pdf(1),3))
    print('  P(|s|<0.3) obs',round(np.mean(np.abs(s)<.3),3),'gauss',round(np.mean(np.abs(sg)<.3),3),'| P(|s|>2) obs',round(np.mean(np.abs(s)>2),3),'gauss',round(np.mean(np.abs(sg)>2),3))
    q=np.quantile(v,np.linspace(0,1,6));B=[(v>=q[k])&(v<=q[k+1]) for k in range(5)]
    print('  dp z por quintil de volume   ',[round(z[b].std(),2) for b in B])
    print('  dp iota por quintil de volume',[round(i[b].std(),2) for b in B])
    print('  corr z-iota por quintil      ',[round(np.corrcoef(z[b],i[b])[0,1],2) for b in B])
print('--- topo achatado na diagonal, por quintil de volume (sem modelo)')
for interval in ('1m','1h'):
    X=np.vstack([np.vstack(split_historical(xx)) for _,_,xx in windows(interval)])
    z,i,v=X.T;q=np.quantile(v,np.linspace(0,1,6));out=[]
    for k in range(5):
        b=(v>=q[k])&(v<=q[k+1]);s=z[b]+i[b];s=(s-s.mean())/s.std()
        out.append((round(float(kurtosis(s)),2),round(float(np.mean(np.abs(s)<.3)/0.2358),2)))
    print(interval,'(curtose, massa central/normal) por quintil',out)
