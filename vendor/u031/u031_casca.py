"""SGV-U03.1: duas cascas da MESMA densidade GMM2 (HDR50 interna + HDR95 externa) e o centro.

A casca HDR50 vem de `build_shell` do M11-I sem nenhuma alteração (grade 25³, extensão 3,5),
idêntica à da U03. A casca externa usa os parâmetros desse mesmo ajuste GMM2 avaliados numa
grade maior (41³, extensão 6), para que ela não toque a borda.

Por que 95% e não 90%: nas sementes de calibração (base 20262200, 5 por classe, fora da U03 e
do teste da U03.1) a razão de tamanho linear B/A foi
    expansão  HDR50 1,13 · HDR90 1,14 · HDR95 1,15
    caudas    HDR50 0,96 · HDR90 1,10 · HDR95 1,51
Com HDR90 caudas e expansão ficam quase iguais por fora; com HDR95 a assinatura de caudas
(núcleo encolhe, casca externa cresce) é inequívoca. HDR97,5 tocou a borda da grade.
"""
from __future__ import annotations

import numpy as np
import trimesh
from skimage.measure import marching_cubes

from sgv_m11i.instrument import build_shell

OUTER_MASS = .95
OUTER_GRID = 41
OUTER_EXTENT = 6.0
INNER_GRID = 25


def mixture_density(params: dict, pts: np.ndarray) -> np.ndarray:
    out = np.zeros(len(pts))
    for w, mean, prec in zip(params["weights"], params["means"], params["precisions"]):
        d = pts - mean
        q = np.einsum("ni,ij,nj->n", d, prec, d)
        sign, logdet = np.linalg.slogdet(prec)
        if sign <= 0:
            raise ValueError("Non-PD mixture precision")
        out += w * np.exp(.5 * logdet - 1.5 * np.log(2 * np.pi) - .5 * q)
    return out


def mixture_mean(params: dict) -> np.ndarray:
    w = np.asarray(params["weights"], float)
    return (w[:, None] * np.asarray(params["means"], float)).sum(0) / w.sum()


def hdr_mesh(params: dict, mass: float, n: int = OUTER_GRID, extent: float = OUTER_EXTENT):
    axis = np.linspace(-extent, extent, n)
    dx = float(axis[1] - axis[0])
    grid = np.stack(np.meshgrid(axis, axis, axis, indexing="ij"), -1).reshape(-1, 3)
    field = mixture_density(params, grid)
    coverage = float(field.sum() * dx ** 3)
    if not .99 <= coverage <= 1.01:
        raise ValueError(f"outer_coverage:{coverage:.4f}")
    ordered = np.sort(field)[::-1]
    frac = np.cumsum(ordered) / ordered.sum()
    i = int(np.searchsorted(frac, mass, side="left"))
    if i + 1 >= len(ordered):
        raise ValueError("outer HDR threshold out of range")
    tau = float((ordered[i] + ordered[i + 1]) / 2)
    F = field.reshape(n, n, n)
    border = np.zeros(F.shape, bool)
    for ax in range(3):
        for which in (0, -1):
            sl = [slice(None)] * 3
            sl[ax] = which
            border[tuple(sl)] = True
    if np.any(F[border] >= tau):
        raise ValueError("outer_boundary_truncation")
    v, f, _, _ = marching_cubes(F.astype(np.float32), level=tau, spacing=(dx, dx, dx),
                                allow_degenerate=False)
    mesh = trimesh.Trimesh(vertices=np.asarray(v, float) - extent, faces=f, process=False)
    m = mesh.copy()
    m.fix_normals()
    if not m.is_watertight:
        raise ValueError("outer_open_mesh")
    return mesh, coverage


def mesh_json(mesh, coverage: float) -> dict:
    v = mesh.vertices
    return {"x": np.round(v[:, 0], 4).tolist(), "y": np.round(v[:, 1], 4).tolist(),
            "z": np.round(v[:, 2], 4).tolist(), "i": mesh.faces[:, 0].tolist(),
            "j": mesh.faces[:, 1].tolist(), "k": mesh.faces[:, 2].tolist(),
            "valid": True, "coverage": round(float(coverage), 5)}


def two_shells(sorted_sample: np.ndarray, seed: int) -> dict:
    """HDR50 (idêntica à U03) + HDR95 + centro, todos do mesmo ajuste GMM2."""
    inner = build_shell(sorted_sample, seed=seed, n=INNER_GRID)
    outer, cov_outer = hdr_mesh(inner.params, OUTER_MASS)
    return {"hdr50": mesh_json(inner.mesh, inner.coverage),
            "hdr95": mesh_json(outer, cov_outer),
            "center": np.round(mixture_mean(inner.params), 4).tolist()}


def shared_frame(*shell_sets: dict, pad: float = 1.08, keys=("hdr50", "hdr95")) -> dict:
    """Mesmo cubo (mesma escala nos três eixos) para A e B, justo em volta das cascas `keys`."""
    pts = np.concatenate([np.column_stack((s[k]["x"], s[k]["y"], s[k]["z"]))
                          for s in shell_sets for k in keys])
    lo, hi = pts.min(0), pts.max(0)
    center = (lo + hi) / 2
    half = float((hi - lo).max() / 2 * pad)
    return {"center": np.round(center, 3).tolist(), "half": round(half, 3)}
