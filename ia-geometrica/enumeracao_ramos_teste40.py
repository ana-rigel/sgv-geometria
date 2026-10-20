import sys, numpy as np, itertools
sys.path.insert(0,'/home/claude/sgv-geometria/ia-geometrica')
import teste40 as T
DW,KC,N=T.DW,T.KC,T.N; MX=np.abs(DW).max()
S=np.array(list(itertools.product([1.,-1.],repeat=N)))
us=MX*(1+np.logspace(-7,3,6000))
root=np.sqrt(np.clip(1-(DW[None,:]/us[:,None])**2,0,None))
Cmat=root@S.T/N
for kf in (1.2,1.6,3.0,10.0):
    K=kf*KC; F=us[:,None]-K*Cmat
    idx=np.argwhere(F[:-1]*F[1:]<0)
    est=[]; inst=[]
    for iu,js in idx:
        a,b=us[iu],us[iu+1]; s=S[js]
        f=lambda u: u-K*np.mean(s*np.sqrt(np.clip(1-(DW/u)**2,0,None)))
        for _ in range(60):
            m=0.5*(a+b); (a,b)=(a,m) if f(a)*f(m)<=0 else (m,b)
        u=0.5*(a+b); ev=T.autovalores(T.estado(u,s),K)
        (est if ev.max()<1e-9 else inst).append((u/K,int((s<0).sum())))
    ci=np.array([c for c,_ in inst])
    perto=sorted([(round(c,3),n) for c,n in inst if abs(c-0.627)<0.02])
    print(f"K/Kc {kf}: estáveis {[(round(c,3),n) for c,n in est]} | instáveis {len(inst)}, C de {ci.min():.3f} a {ci.max():.3f} | perto de 0,627: {len(perto)} (ex. {perto[:4]})", flush=True)
