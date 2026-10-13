#!/usr/bin/env python3
"""SGV-M34 — ENGENHARIA: deformacoes da casca (M8–M11) como variaveis causais.

Na origem t usa SO a janela [t-1499, t] (1.500 min, a janela original do M11 no 1m):
split_historical -> ancora 30% (gaussianizacao) + metades A (mais antiga) e B (mais recente).
Grupo GEOMETRICO G (10), instrumentos originais sem alteracao:
  trans      ||centro_B - centro_A||           (M8, motion)
  dlogvol    log(V_B/V_A)                       (M8)
  rot        angulo-quociente SO(3)/D2 em graus (M9; 0 se nao identificavel)
  rot_ok     1 se a orientacao e identificavel  (indicador do anterior)
  m11        distancia superficie-superficie apos ICP (M11, 512 pontos)
  jacc       Jaccard das regioes HDR50 na grade (persistencia da regiao)
  saddle_b   fracao da area em sela da casca B  (curvatura atual)
  dsaddle    saddle_B - saddle_A                (variacao temporal da curvatura)
  kmed_b     mediana da curvatura gaussiana analitica em B (intensidade)
  dkmed      kmed_B - kmed_A
Grupo ECONOMETRICO E (10), mesma capacidade, nas MESMAS metades gaussianizadas:
  dmean ||media_B-media_A||, dlogdet, dcorr_zi, dcorr_zn, dcorr_in, dlogsd_z, dlogsd_i, dlogsd_n,
  energy (distancia de energia A-B), dkurt (variacao media da curtose)
Qualquer falha de malha/ICP -> G invalido nessa origem (registrado, nunca imputado).
"""
from __future__ import annotations
import numpy as np
from scipy.stats import kurtosis
from experiments import isosuperficies_morfometria as iso
from experiments.precisao_formas_3d import split_historical
from experiments.m11_distancia_superficie_nulos import measure_samples
from experiments.m15_forma_persistencia_comparadores import energy_distance

WINDOW=1500;GRID=35;SEED=20261013
G_COLS=('trans','dlogvol','rot','rot_ok','m11','jacc','saddle_b','dsaddle','kmed_b','dkmed')
E_COLS=('dmean','dlogdet','dcorr_zi','dcorr_zn','dcorr_in','dlogsd_z','dlogsd_i','dlogsd_n','energy','dkurt')


def _shell(sample,seed):
    pts,dx=iso.make_grid(GRID);dens,par=iso.density_values(sample,pts,'mixture',seed,with_model=True)
    f=dens.reshape(GRID,GRID,GRID);th,cov=iso.hdr_thresholds(f,dx);tau=th[.5]['tau']
    mesh,trunc=iso.extract_mesh(f,tau,dx)
    props=iso.describe_mesh(mesh,truncated=trunc,coverage=cov,implicit_model=par)
    return mesh,props,f>tau


def geom_from_halves(a,b,seed=SEED):
    ma,pa,ka=_shell(a,seed);mb,pb,kb=_shell(b,seed+1)
    if not(pa['quality_pass'] and pb['quality_pass']):return None,'malha_invalida'
    mo=iso.motion(ma,pa,mb,pb,seed=seed+2)
    if not mo.get('quality_pass'):return None,'movimento_invalido'
    d=measure_samples(a,b,seed+3)
    if not d.get('valid') or not np.isfinite(d.get('distance_512',np.nan)):return None,'m11_invalido'
    inter=np.logical_and(ka,kb).sum();uni=np.logical_or(ka,kb).sum()
    rot=mo.get('rotation_angle_deg')
    G={'trans':mo['translation_norm'],'dlogvol':mo['volume_log_change'],
       'rot':0. if rot is None else float(rot),'rot_ok':float(rot is not None),
       'm11':float(d['distance_512']),'jacc':float(inter/uni) if uni else np.nan,
       'saddle_b':pb['implicit_K_negative_area_fraction'],'dsaddle':pb['implicit_K_negative_area_fraction']-pa['implicit_K_negative_area_fraction'],
       'kmed_b':pb['implicit_K_median'],'dkmed':pb['implicit_K_median']-pa['implicit_K_median']}
    if not all(np.isfinite(v) for v in G.values()):return None,'nao_finito'
    return {k:float(v) for k,v in G.items()},None


def econ_from_halves(a,b):
    ca,cb=np.cov(a,rowvar=False),np.cov(b,rowvar=False)
    sa,sb=np.sqrt(np.diag(ca)),np.sqrt(np.diag(cb));ra,rb=ca/np.outer(sa,sa),cb/np.outer(sb,sb)
    E={'dmean':float(np.linalg.norm(b.mean(0)-a.mean(0))),
       'dlogdet':float(np.linalg.slogdet(cb)[1]-np.linalg.slogdet(ca)[1]),
       'dcorr_zi':float(rb[0,1]-ra[0,1]),'dcorr_zn':float(rb[0,2]-ra[0,2]),'dcorr_in':float(rb[1,2]-ra[1,2]),
       'dlogsd_z':float(np.log(sb[0]/sa[0])),'dlogsd_i':float(np.log(sb[1]/sa[1])),'dlogsd_n':float(np.log(sb[2]/sa[2])),
       'energy':float(energy_distance(a,b)),'dkurt':float(np.mean(kurtosis(b,axis=0)-kurtosis(a,axis=0)))}
    return E


def features(window,seed=SEED):
    """window: (1500,3) de (z, iota, nu) ate a origem, inclusive. Retorna (G ou None, motivo, E)."""
    x=np.asarray(window,float)
    if x.shape!=(WINDOW,3) or not np.isfinite(x).all():return None,'janela_invalida',None
    a,b=split_historical(x)
    try:G,why=geom_from_halves(a,b,seed)
    except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:G,why=None,f'erro:{type(e).__name__}'
    return G,why,econ_from_halves(a,b)
