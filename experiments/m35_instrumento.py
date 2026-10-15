#!/usr/bin/env python3
"""SGV-M35 passo 1 — variantes do instrumento de deformacao residual (plano: reports/m35/PLANO_M35_PASSO1_20261013.md).

V0  M11 original: campo GMM2 -> casca HDR50 -> malha -> normaliza (centro, raio equivalente) -> ICP -> distancia superficie (512).
V1  idem com ICP em 1000 pontos e quadratura 2048 (so reduz ruido numerico).
V2  campo GMM2 ENSACADO (media de 10 ajustes em reamostras em blocos de 15 min) -> resto igual ao V0.
V3  campo KDE gaussiano (banda de Scott), deterministico -> resto igual ao V0.
V4  cada metade BRANQUEADA pela propria media e Sigma^(-1/2) simetrica; campo GMM2 ensacado;
    v4 = 1 - Jaccard(HDR50_A, HDR50_B) na grade; v4n_X = 1 - Jaccard(HDR50_X, bola gaussiana HDR50).
Nenhuma variante usa alvo de mercado.
"""
from __future__ import annotations
import numpy as np
from scipy.stats import gaussian_kde,chi2
from experiments import isosuperficies_morfometria as iso
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m9_registro_simetrico_3d import normalized_mesh_points,initial_rotations,icp_fit
from experiments.m11_distancia_superficie_nulos import normalize_mesh,direct_distance

GRID=35;BAG=10;BLOCK=15
PTS,DX=iso.make_grid(GRID)
R50=float(np.sqrt(chi2.ppf(.5,3)))
BALL=(np.linalg.norm(PTS,axis=1)<R50).reshape(GRID,GRID,GRID)
VARIANTS=('V0','V1','V2','V3','V4')


def gmm_field(x,seed):
    return iso.density_values(x,PTS,'mixture',seed).reshape(GRID,GRID,GRID)


def bagged_field(x,seed,k=BAG,block=BLOCK):
    rng=np.random.default_rng(seed);acc=np.zeros((GRID,GRID,GRID))
    for j in range(k):
        acc+=gmm_field(circular_blocks(x,rng,block),seed+1000+j)   # densidades (massa na grade = cobertura)
    return acc/k


def kde_field(x):
    v=gaussian_kde(np.asarray(x,float).T)(PTS.T)
    if not np.isfinite(v).all() or v.sum()<=0:raise ValueError('KDE invalida')
    return v.reshape(GRID,GRID,GRID)


def hdr_mask(field):
    th,_=iso.hdr_thresholds(field,DX);return field>th[.5]['tau']


def shell_mesh(field):
    th,cov=iso.hdr_thresholds(field,DX);mesh,trunc=iso.extract_mesh(field,th[.5]['tau'],DX)
    p=iso.describe_mesh(mesh,truncated=trunc,coverage=cov)
    if not p['quality_pass']:raise ValueError('casca reprovada: '+str(p['invalid_reason']))
    return mesh


def residual_distance(ma,mb,seed,icp_points=360,quad=512):
    a=normalize_mesh(ma);b=normalize_mesh(mb)
    R,_=icp_fit(normalized_mesh_points(a,icp_points,seed),normalized_mesh_points(b,icp_points,seed+1),initial_rotations(a,b))
    T=np.eye(4);T[:3,:3]=R.T;b.apply_transform(T)
    return float(direct_distance(a,b,quad)['symmetric'])


def whiten(x):
    x=np.asarray(x,float);mu=x.mean(0);S=np.cov(x,rowvar=False)
    w,V=np.linalg.eigh(S)
    if w.min()<=1e-10:raise ValueError('covariancia degenerada')
    return (x-mu)@(V@np.diag(w**-.5)@V.T)


def jdist(p,q):
    u=np.logical_or(p,q).sum();return float(1-np.logical_and(p,q).sum()/u) if u else np.nan


def measure(a,b,variant,seed):
    """Retorna dict de valores (ou levanta ValueError/RuntimeError/LinAlgError se o instrumento falhar)."""
    if variant=='V0':return {'V0':residual_distance(shell_mesh(gmm_field(a,seed)),shell_mesh(gmm_field(b,seed+1)),seed+2)}
    if variant=='V1':return {'V1':residual_distance(shell_mesh(gmm_field(a,seed)),shell_mesh(gmm_field(b,seed+1)),seed+2,1000,2048)}
    if variant=='V2':return {'V2':residual_distance(shell_mesh(bagged_field(a,seed)),shell_mesh(bagged_field(b,seed+1)),seed+2)}
    if variant=='V3':return {'V3':residual_distance(shell_mesh(kde_field(a)),shell_mesh(kde_field(b)),seed+2)}
    if variant=='V4':
        ka=hdr_mask(bagged_field(whiten(a),seed));kb=hdr_mask(bagged_field(whiten(b),seed+1))
        na,nb=jdist(ka,BALL),jdist(kb,BALL)
        return {'V4':jdist(ka,kb),'V4n_A':na,'V4n_B':nb,'dV4n':nb-na}
    raise ValueError('variante invalida')


def measure_all(a,b,seed,variants=VARIANTS):
    out={}
    for v in variants:
        try:out.update(measure(a,b,v,seed))
        except (ValueError,RuntimeError,np.linalg.LinAlgError,IndexError):pass
    return out


def planted(sep,n,rng,direction=(1.,1.,0.)):
    """Mistura 50/50 de duas gaussianas separadas por `sep` ao longo de `direction`, re-padronizada
    a media 0 e covariancia identidade: a forma muda, os dois primeiros momentos nao."""
    d=np.asarray(direction,float);d/=np.linalg.norm(d)
    s=np.where(rng.random(n)<.5,-1.,1.)
    x=rng.standard_normal((n,3))*.8+np.outer(s*sep/2,d)
    return whiten(x)


# ---------------- passo 2: mapa radial localizado (plano PLANO_M35_PASSO2_20261014.md) ----------------
from itertools import product
from scipy.ndimage import map_coordinates

def _directions():
    d=[np.array(v,float) for v in product((-1,0,1),repeat=3) if any(v)]
    return np.array([v/np.linalg.norm(v) for v in d])

DIRS=_directions()                                   # 26 direcoes unitarias em (z, iota, nu)
DIR_NAMES=[''.join(('z','i','n')[k]+('+' if v[k]>0 else '-') for k in range(3) if v[k]!=0) for v in DIRS]
_OPP=np.array([int(np.argmin(np.linalg.norm(DIRS+u,axis=1))) for u in DIRS])
AXES=[k for k in range(26) if DIRS[k][np.flatnonzero(DIRS[k])[0]]>0]   # 13 eixos: representante com 1a coordenada nao nula positiva
AXIS_NAMES=[DIR_NAMES[k] for k in AXES]
_T=np.arange(0.,3.45,.01)


def radial_map(field):
    """r(u): raio do cruzamento MAIS EXTERNO da HDR50 ao longo de cada uma das 26 direcoes, a partir da origem.
    Retorna delta(u)=log(r/R50) (26,), parte simetrica s e antissimetrica a nos 13 eixos."""
    th,_=hdr_thresholds_tau(field);ext=(GRID-1)*DX/2
    r=np.empty(len(DIRS))
    for k,u in enumerate(DIRS):
        p=_T[:,None]*u[None,:];idx=((p+ext)/DX).T
        v=map_coordinates(field,idx,order=1,mode='nearest')-th
        inside=np.flatnonzero(v>0)
        if not len(inside):r[k]=np.nan;continue
        j=inside[-1]
        if j+1>=len(_T):r[k]=_T[j];continue
        r[k]=_T[j]+(_T[j+1]-_T[j])*v[j]/(v[j]-v[j+1])  # interpolacao linear do cruzamento
    d=np.log(r/R50);a=np.asarray(AXES);o=_OPP[a]
    return d,(d[a]+d[o])/2,(d[a]-d[o])/2


def hdr_thresholds_tau(field):
    th,_=iso.hdr_thresholds(field,DX);return th[.5]['tau'],None


def measure_v4_map(a,b,seed):
    """Mesmos campos (e sementes) do V4; acrescenta os mapas radiais de A e B."""
    fa=bagged_field(whiten(a),seed);fb=bagged_field(whiten(b),seed+1)
    ka,kb=hdr_mask(fa),hdr_mask(fb);na,nb=jdist(ka,BALL),jdist(kb,BALL)
    out={'V4':jdist(ka,kb),'V4n_A':na,'V4n_B':nb,'dV4n':nb-na}
    for tag,f in (('A',fa),('B',fb)):
        d,s,an=radial_map(f)
        out.update({f'd{tag}_{n}':float(x) for n,x in zip(DIR_NAMES,d)})
        out.update({f's{tag}_{n}':float(x) for n,x in zip(AXIS_NAMES,s)})
        out.update({f'a{tag}_{n}':float(x) for n,x in zip(AXIS_NAMES,an)})
    return out


def planted_lobe(n,rng,axis,frac=.15,dist=2.,sd=.5):
    """Gaussiana com um lobulo (fracao `frac`) em dist*e_axis, branqueada. axis: indice em 0..5 = (+z,-z,+i,-i,+n,-n)."""
    e=np.zeros(3);e[axis//2]=1. if axis%2==0 else -1.
    x=rng.standard_normal((n,3));k=rng.random(n)<frac
    x[k]=dist*e+sd*rng.standard_normal((int(k.sum()),3))
    return whiten(x),e


def map_hit(an,e):
    """Direcao (com sinal) de maior |a(u)| entre os 13 eixos, comparada com e: acerto se angulo <= 45 graus."""
    a=np.asarray(an);k=int(np.nanargmax(np.abs(a)));u=DIRS[AXES[k]]*np.sign(a[k])
    return float(np.degrees(np.arccos(np.clip(u@e,-1,1))))<=45.0001


# ---------------- passo 3: deformacao da combinacao dos eixos (plano PLANO_M35_PASSO3_20261015.md) ----------------
from scipy.stats import rankdata,norm as _norm

def rank_normal(x):
    """Cada eixo levado a normal pelos proprios postos: u = Phi^-1((posto-1/2)/n). Elimina a forma de cada eixo."""
    x=np.asarray(x,float);n=len(x)
    return np.column_stack([_norm.ppf((rankdata(x[:,j])-.5)/n) for j in range(x.shape[1])])


def measure_cop(b,seed):
    """V4n_B (deformacao total) e V_cop (so a combinacao dos eixos) + mapa radial da casca de V_cop.
    Mesmas sementes e mesmo ensacamento nas duas."""
    fb=bagged_field(whiten(b),seed);fc=bagged_field(whiten(rank_normal(b)),seed)
    out={'V4n_B':jdist(hdr_mask(fb),BALL),'V_cop':jdist(hdr_mask(fc),BALL)}
    d,s,an=radial_map(fc)
    out.update({f'sC_{n}':float(x) for n,x in zip(AXIS_NAMES,s)})
    out.update({f'aC_{n}':float(x) for n,x in zip(AXIS_NAMES,an)})
    return out


_RC=np.array([[1,.3,.2],[.3,1,.4],[.2,.4,1.]]);_LC=np.linalg.cholesky(_RC)

def synth_marginal(n,s,rng):
    """Copula gaussiana fixa; cada eixo deformado por seno-hiperbolico (assimetria e caudas crescem com s)."""
    g=rng.standard_normal((n,3))@_LC.T;delta=1/(1+1.5*s);eps=np.array([1.,-1.,.6])*s
    return np.sinh((np.arcsinh(g)+eps)/delta)


def synth_joint(n,s,rng,kind):
    """Eixos exatamente gaussianos (postos); a combinacao dos eixos muda com s."""
    g=rng.standard_normal((n,3))@_LC.T
    if kind=='cone':
        x=g.copy();x[:,0]=g[:,0]*np.exp(1.2*s*g[:,2])
    elif kind=='cintura':
        x=g.copy();hv=g[:,2]>=np.quantile(g[:,2],.6);sg=np.where(rng.random(int(hv.sum()))<.5,-1.,1.)
        x[hv,:2]+=np.outer(sg*1.5*s,np.ones(2)/np.sqrt(2))
    elif kind=='caudas':
        df=3+27*(1-s);w=rng.chisquare(df,n)/df;x=g/np.sqrt(w)[:,None]
    else:raise ValueError(kind)
    return rank_normal(x)


def dependence_scales(b):
    """T2: dependencia tradicional calculada nos postos normais da metade."""
    u=rank_normal(b);nm='zin';o={}
    for j,k in ((0,1),(0,2),(1,2)):
        r=float(np.corrcoef(u[:,j],u[:,k])[0,1]);p=nm[j]+nm[k]
        o[f'T2_rho_{p}']=r;o[f'T2_cokurt_{p}']=float(np.mean(u[:,j]**2*u[:,k]**2)-(1+2*r*r))
        for q,lab in ((.9,'sup'),(.1,'inf')):
            a=u[:,j]>np.quantile(u[:,j],q) if lab=='sup' else u[:,j]<np.quantile(u[:,j],q)
            c=u[:,k]>np.quantile(u[:,k],q) if lab=='sup' else u[:,k]<np.quantile(u[:,k],q)
            o[f'T2_cauda_{lab}_{p}']=float(np.mean(a&c)/.1)
    for j in range(3):
        for k in range(3):
            if j!=k:o[f'T2_coskew_{nm[j]}{nm[j]}{nm[k]}']=float(np.mean(u[:,j]**2*u[:,k]))
    o['T2_absz_n']=float(np.corrcoef(np.abs(u[:,0]),u[:,2])[0,1]);o['T2_absi_n']=float(np.corrcoef(np.abs(u[:,1]),u[:,2])[0,1])
    o['T2_absz_absi']=float(np.corrcoef(np.abs(u[:,0]),np.abs(u[:,1]))[0,1])
    return o
