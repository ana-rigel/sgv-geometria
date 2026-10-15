"""C02 synthetic distribution generators, development/calibration only.
OOD generators can be inspected analytically, but ood_test observations are sealed.
"""
from dataclasses import dataclass
import hashlib
import numpy as np

FAMILIES_DEV = ('G3', 'S5', 'B3')
FAMILIES_OOD = ('R7', 'BS35')
CLASSES = tuple(f'T{i}' for i in range(7))
SPLITS = ('calibration','training','validation')
BASE_SEED = 2026101402


def seed_for(split, family, label, rep, purpose):
    if split not in SPLITS:
        raise ValueError('C02 OOD test partition sealed')
    if family not in FAMILIES_DEV + FAMILIES_OOD or label not in CLASSES or rep < 0:
        raise ValueError('invalid family/case')
    if split in ('training','validation') and family not in FAMILIES_DEV:
        raise ValueError('OOD families prohibited from training and validation')
    key=f'C02|{BASE_SEED}|{split}|{family}|{label}|{rep}|{purpose}'.encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8],'big')


def banana(x, strength):
    y = np.array(x, dtype=float, copy=True)
    y[...,1] += strength*(y[...,0]**2 - 1.0)
    return y


def banana_inverse(y,strength):
    x=np.array(y,dtype=float,copy=True)
    x[...,1] -= strength*(x[...,0]**2 - 1.0)
    return x


@dataclass(frozen=True)
class Mixture:
    means: np.ndarray
    covs: np.ndarray
    weights: np.ndarray
    dof: float | None = None
    banana_strength: float = 0.0

    def __post_init__(self):
        m=np.asarray(self.means,float); c=np.asarray(self.covs,float); w=np.asarray(self.weights,float)
        assert m.ndim==2 and m.shape[1]==3
        assert c.shape==(len(w),3,3) and m.shape[0]==len(w)
        assert (w>0).all() and np.isclose(w.sum(),1)
        assert np.min(np.linalg.eigvalsh(c))>0
        assert self.dof is None or self.dof>2

    def sample(self,n,rng):
        ids=rng.choice(len(self.weights),size=n,p=self.weights)
        x=np.empty((n,3))
        for k in range(len(self.weights)):
            ix=np.flatnonzero(ids==k)
            if not len(ix):continue
            z=rng.multivariate_normal(self.means[k],self.covs[k],size=len(ix))
            if self.dof is not None:
                chi=rng.chisquare(self.dof,size=len(ix))
                z=self.means[k]+(z-self.means[k])*np.sqrt(self.dof/chi)[:,None]
            x[ix]=z
        return banana(x,self.banana_strength) if self.banana_strength else x


def family_model(name):
    if name=='R7':
        theta=np.arange(7)*2*np.pi/7 + .07*np.arange(7)
        means=np.stack([1.7*np.cos(theta),1.2*np.sin(theta),.3*np.sin(2*theta)],axis=1)
        covs=np.array([np.diag([.25+.025*i,.22+.01*i,.35]) for i in range(7)])
        weights=np.arange(1,8,dtype=float); weights/=weights.sum()
        return Mixture(means,covs,weights)
    means=np.array([[1.15,0.05,.1],[-.95,-.6,-.15],[.1,1.2,.35]])
    covs=np.array([[[.4,.08,0],[.08,.5,.05],[0,.05,.48]],
                   [[.45,-.06,0],[-.06,.36,0],[0,0,.4]],
                   [[.32,0,0],[0,.38,-.03],[0,-.03,.35]]])
    w=np.array([.51,.31,.18])
    if name=='G3':return Mixture(means,covs,w)
    if name=='S5':return Mixture(means,covs,w,dof=5.)
    if name=='B3':return Mixture(means,covs,w,banana_strength=.3)
    if name=='BS35':return Mixture(means,covs,w,dof=3.5,banana_strength=.65)
    raise ValueError(name)


def pair_samples(family,label,rep,*,split='calibration',n=750):
    if n!=750:raise ValueError('C02 sample size locked at 750 per arm')
    sd=seed_for(split,family,label,rep,'nuisance')
    sa=seed_for(split,family,label,rep,'A')
    sb=seed_for(split,family,label,rep,'B')
    rng=np.random.default_rng(sd)
    u=rng.normal(size=(3,3));q,r=np.linalg.qr(u)
    q=q@np.diag(np.where(np.diag(r)<0,-1.,1.))
    if np.linalg.det(q)<0:q[:,0]*=-1
    mat=q*rng.uniform(.9,1.1)
    shift=rng.uniform(-.25,.25,size=3)
    p=family_model(family)
    if label=='T5':
        weight=p.weights.copy();weight[0]*=2.5;weight/=weight.sum()
        b_model=Mixture(p.means,p.covs,weight,p.dof,p.banana_strength)
    else:b_model=p
    a=p.sample(n,np.random.default_rng(sa))
    b=b_model.sample(n,np.random.default_rng(sb))
    if label=='T1':b+=np.array([0,.65,0])
    elif label=='T2':b*=1.25
    elif label=='T3':b=b@np.array([[0.,1.,0.],[-1.,0.,0.],[0.,0.,1.]]).T
    elif label=='T4':b=b@np.array([[1.,.55,0.],[0.,1.,0.],[0.,0.,1.]]).T
    elif label=='T6':
        rare=np.random.default_rng(seed_for(split,family,label,rep,'rare'))
        mask=rare.random(n)<.05
        b[mask]=rare.normal(loc=np.array([2.8,0.,0.]),scale=.35,size=(mask.sum(),3))
    # Common nuisance applied AFTER the deliberate transformation.
    a=a@mat.T+shift;b=b@mat.T+shift
    assert np.isfinite(a).all() and np.isfinite(b).all()
    return a,b
