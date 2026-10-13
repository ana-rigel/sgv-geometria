"""Compatibility API: maps portable M11-I interface onto repository M11-I modules.
May result in slight numeric differences from bundled portable implementation.
"""
import numpy as np
from sgvgeo.flow import flow_coordinates as _flow
from experiments.precisao_formas_3d import gaussianize_three
from sgv_m11i.integrated import one_shell,integrate_meshes

def gaussianize(anchor, observations):
    return gaussianize_three(anchor,observations)

def flow_coordinates(frame):
    return _flow(frame)[['z','iota','nu']].to_numpy(float)

def build_shell(sample,seed=20261009,n=35,extent=None):
    return one_shell(sample,seed,n)

def signature(A,B,seed=20261009):
    return integrate_meshes(A[0],B[0],A[1],B[1],seed)
