"""SGV bridge H-J/H-GEO. Engineering/exploratory only, not a preregistration.

Implements original 20-node RTT with a stationarity-matched reversible control,
forward transition log scoring in completely disjoint 1500-point B blocks,
and M11-I HDR50 geometry forecasts by conditional historical-node resampling.
No trading, no new holdouts, no statistical significance claims.
"""
from __future__ import annotations
import numpy as np
from sklearn.cluster import KMeans

N_NODES=20
WINDOW=1500
TRAIN_P=1440
SEED=20261013
PSEUDO=.1

def counts(nodes,n_nodes=N_NODES):
    x=np.asarray(nodes,dtype=np.int64)
    if len(x)<2:return np.zeros((n_nodes,n_nodes))
    c=np.bincount(x[:-1]*n_nodes+x[1:],minlength=n_nodes**2)
    return c.reshape(n_nodes,n_nodes).astype(float)

def stochastic(C,pseudocount=PSEUDO):
    X=np.asarray(C,float)+pseudocount
    den=X.sum(1,keepdims=True)
    P=np.divide(X,den,out=np.zeros_like(X),where=den>0)
    for i in np.where(den.flatten()==0)[0]:P[i,i]=1.
    return P

def stationary(P):
    n=len(P)
    A=P.T-np.eye(n);A[-1,:]=1.
    b=np.zeros(n);b[-1]=1.
    pi=np.linalg.solve(A,b)
    if np.any(pi<=0) or not np.allclose(pi@P,pi,atol=1e-9):
        raise ValueError('P has no valid positive stationary measure')
    return pi

def reversible(P):
    """P* time reversal has the SAME stationary pi, Q=(P+P*)/2, Q detailed-balanced."""
    pi=stationary(P)
    Pstar=(P.T*pi[None,:])/pi[:,None]
    Q=(P+Pstar)/2
    Q/=Q.sum(axis=1,keepdims=True)
    flux=pi[:,None]*Q
    assert np.allclose(pi@Q,pi,atol=1e-9)
    assert np.allclose(flux,flux.T,atol=1e-9)
    return Q,pi

def models_from_A(nodes,n_nodes=N_NODES,seed=SEED):
    x=np.asarray(nodes,int)
    if len(x)<2 or np.any(x<0) or np.any(x>=n_nodes):
        raise ValueError('invalid historic nodes')
    P=stochastic(counts(x,n_nodes))
    Q,pi=reversible(P)
    shuffle=np.random.default_rng(seed).permutation(x)
    Ps=stochastic(counts(shuffle,n_nodes))
    return {'rtt':P,'reversible':Q,'shuffled_training':Ps,
            'iid':np.broadcast_to(pi,(n_nodes,n_nodes)).copy(),
            'pi':pi}

def heldout_logscore(models,last_A_node,B_nodes):
    """Score next-state transitions in B; no future used by training."""
    B=np.asarray(B_nodes,int)
    origin=np.r_[int(last_A_node),B[:-1]]
    return {k:float(np.log(np.maximum(m[origin,B],1e-300)).mean())
            for k,m in models.items() if k!='pi'}

def mean_occupation(P,current_node,H):
    """Average of ALL H future marginal distributions, NOT delta P^H."""
    n=len(P);v=np.eye(n)[int(current_node)];tot=np.zeros(n)
    for _ in range(int(H)):
        v=v@P;tot+=v
    p=np.maximum(tot/H,0.)
    return p/p.sum()

def resample_nodes(A,nodes,weights,seed=SEED):
    """Only source points already in A; matched randomness across candidate models."""
    A=np.asarray(A,float);nodes=np.asarray(nodes,int)
    p=np.asarray(weights,float).copy()
    present=np.bincount(nodes,minlength=len(p))>0
    mass_missing=float(p[~present].sum())
    p[~present]=0.
    if p.sum()==0:raise ValueError('no represented nodes')
    p/=p.sum()
    goal=(np.arange(len(A))+.5)/len(A)
    ids=np.minimum(np.searchsorted(np.cumsum(p),goal,side='right'),len(p)-1)
    rand=np.random.default_rng(seed).random(len(A))
    out=np.empty_like(A)
    for node in np.unique(ids):
        positions=np.flatnonzero(ids==node)
        population=np.flatnonzero(nodes==node)
        out[positions]=A[population[np.minimum((rand[positions]*len(population)).astype(int),
                                              len(population)-1)]]
    return out,mass_missing

def read_signature(s):
    if not s.get('valid'):raise ValueError('M11-I invalid signature')
    return {'center':np.asarray(s['delta_center'],float),
            'log_volume':s.get('delta_log_volume'),'theta':s.get('theta_deg'),
            'residual':s.get('distance_512'),'delta_D':s.get('delta_D')}

def errors(observed,predicted):
    a=read_signature(observed);b=read_signature(predicted)
    out={'center':float(np.linalg.norm(a['center']-b['center']))}
    for name in ('log_volume','theta','residual','delta_D'):
        out[name]=None if a[name] is None or b[name] is None else float(abs(a[name]-b[name]))
    scales={'center':1.,'log_volume':1.,'theta':180.,'residual':1.,'delta_D':1.}
    x=[(out[k]/scales[k])**2 for k in scales if out[k] is not None]
    out['diagnostic_loss']=float(np.mean(x)) if x else None
    out['n_components']=len(x)
    return out

def geometry_forecast(A,B,A_nodes,models,last_A_node,seed=SEED,grid=35):
    """G(A->Bhat) vs G(A->B), for RTT/persistence/reversible/shuffled/IID.

    Uses *one* shared A shell, same GMM2 setup for every shell, common random
    seed for conditional resampling, GMM and alignment across model variants.
    """
    from sgv_m11i.integrated import one_shell,integrate_meshes,D_index
    ma,pa,_=one_shell(A,seed,grid)
    mb,pb,_=one_shell(B,seed+1,grid)
    observed=integrate_meshes(ma,mb,pa,pb,seed+2)
    if not observed.get('valid'):raise ValueError('observed M11-I invalid')
    D_a,_=D_index(ma,pa)
    persistent={'valid':True,'delta_center':[0.,0.,0.],
                'delta_log_volume':0.,'theta_deg':0.,
                'distance_512':0.,'delta_D':0.,
                'D_A':D_a,'D_B':D_a}
    losses={'persistence':errors(observed,persistent)}
    unavailable={}
    for name in ('rtt','reversible','shuffled_training','iid'):
        w=mean_occupation(models[name],last_A_node,len(B))
        sample,missing=resample_nodes(A,A_nodes,w,seed+300)
        unavailable[name]=missing
        mesh,params,_=one_shell(sample,seed+11,grid)
        predicted=integrate_meshes(ma,mesh,pa,params,seed+30)
        losses[name]=errors(observed,predicted)
    return {'observed':{k:observed.get(k) for k in
                        ('delta_center','delta_log_volume','theta_deg',
                         'distance_512','D_A','D_B','delta_D')},
            'losses':losses,'missing_node_mass':unavailable}

def codebook(May,n_nodes=N_NODES):
    mu=May.mean(0);sd=May.std(0);sd[sd==0]=1.
    km=KMeans(n_clusters=n_nodes,random_state=SEED,n_init=10)
    km.fit((May-mu)/sd)
    cent=km.cluster_centers_
    return mu,sd,cent[np.lexsort(cent.T[::-1])]

def classify(X,mu,sd,cent):
    d=(( (X-mu)/sd)[:,None,:]-cent[None,:,:])**2
    return np.argmin(d.sum(2),axis=1).astype(int)

def synthetic_hj(n=7000,seed=SEED):
    rng=np.random.default_rng(seed)
    def circle(cw):
        P=np.zeros((6,6))
        for i in range(6):
            P[i,i]=.14
            P[i,(i+1)%6]=.82 if cw else .04
            P[i,(i-1)%6]=.04 if cw else .82
        return P
    output={}
    for name,P in [('clockwise',circle(True)),('counterclockwise',circle(False)),
                   ('reversible',(circle(True)+circle(False))/2)]:
        nodes=np.empty(n,dtype=int);nodes[0]=0
        for t in range(1,n):
            nodes[t]=rng.choice(6,p=P[nodes[t-1]])
        model=models_from_A(nodes[:n//2],6,seed)
        sc=heldout_logscore(model,nodes[n//2-1],nodes[n//2:])
        output[name]={'rtt_minus_reversible':sc['rtt']-sc['reversible'],
                      'scores':sc}
    return output
