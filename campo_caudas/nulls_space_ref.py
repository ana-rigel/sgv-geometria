"""
nulls.py — o que no campo e na régua é dinâmica, e o que não é.

Duas nulas, junho–julho/2026 (maio fica intacto: âncora e aquecimento):

  A. EMBARALHADA: permuta a ordem dos minutos de (z, ι, ν) dentro de cada dia.
     Mesma nuvem de pontos, nenhuma ordem temporal. Tudo o que sobrevive
     contra ela depende da ordem no tempo.

  B. PIPELINE: permuta, dentro de cada dia, os minutos de (retorno log,
     fração de agressão compradora, log volume) e recalcula z, ι, ν com o
     MESMO flow_coordinates e a mesma âncora de maio. Os filtros causais
     (vol de 60 min, mediana de 1.500 min) recriam alguma estrutura temporal
     sozinhos; o que sobrevive contra B não é artefato dos filtros.

As mesmas fórmulas do build_real.py, avaliadas em 1 de cada STRIDE minutos.
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/claude/m11i/SGV_M11I_Instrumento")
sys.path.insert(0, "/home/claude/sgv_original")
sys.path.insert(0, "/home/claude/rtt")
from sgv_m11i.instrument import flow_coordinates, gaussianize  # noqa: E402
from sgv.common.kde import kde_eval  # noqa: E402
from sgv.common.geometry import christoffel_hessian, project_psd, safe_inv  # noqa: E402
from sgv_rtt_operator import TopologyGraphOperator, entropy_production, transition_counts  # noqa: E402

import os
SPACE = os.environ.get("SGV_SPACE", "flow")


def orig_coordinates(df):
    """Espaço do campo 3D do SGV original (sgv_original ac6b986):
    E_norm do input (arquivo 0: z robusto causal de (close − EMA_0,05)/EMA, com sinal),
    jerk do input (Δ² do retorno) e memory_flux = Δ EMA_0,05(E_norm), como em geodesic_field."""
    from sgv.config import SGVConfig
    from sgv.input_builder import build_btc_90d_input_sgv
    raw = pd.DataFrame({"timestamp": df["timestamp"].to_numpy(),
                        "datetime": pd.to_datetime(df["timestamp"], unit="ms", utc=True).astype(str).to_numpy()})
    for c in ("open", "high", "low", "close", "volume"):
        raw[c] = pd.to_numeric(df[c] if c in df else df["close"]).to_numpy()
    inp = build_btc_90d_input_sgv(raw, SGVConfig())
    assert len(inp) == len(df) and (inp["timestamp"].to_numpy() == raw["timestamp"].to_numpy()).all()
    e_norm = inp["E_norm"]
    mem_e = e_norm.ewm(alpha=0.05, adjust=False).mean()
    memory_flux = mem_e.diff()
    return np.column_stack((e_norm.to_numpy(), inp["jerk"].to_numpy(), memory_flux.to_numpy()))


def COORDS(df):
    if SPACE == "orig":
        return orig_coordinates(df)
    return flow_coordinates(df[["timestamp", "close", "volume", "taker_buy"]])

H_KDE, W_FIT, PSD_FLOOR, W_RULER, N_NODES = 0.45, 10080, 1e-3, 1440, 20
STRIDE, N_PIPE = 7, 8
OUT = "/home/claude/rtt/real/" + ("orig/" if SPACE == "orig" else "")
rng = np.random.default_rng(2026)

kl = pd.read_pickle("/home/claude/klines/btc_1m_mai_jul_2026.pkl")
ts = pd.to_datetime(kl.timestamp, unit="ms", utc=True)
may = (ts < pd.Timestamp("2026-06-01", tz="UTC")).to_numpy()
i_jun = int(np.argmax(~may))
day = ts.dt.floor("D").to_numpy()


def coords(df):
    return COORDS(df)


raw_real = coords(kl)
ok = np.isfinite(raw_real).all(1)
anchor = raw_real[may & ok]


def gauss(raw):
    G = np.full_like(raw, np.nan)
    good = np.isfinite(raw).all(1)
    G[good] = gaussianize(anchor, raw[good])
    return G


G_real = gauss(raw_real)
op = TopologyGraphOperator(n_nodes=N_NODES, window_size=W_RULER).fit_codebook(G_real[may & ok])


def within_day_perm(n_from):
    """Índices com os minutos permutados dentro de cada dia a partir de n_from."""
    idx = np.arange(len(kl))
    for d_ in np.unique(day[n_from:]):
        sel = np.where(day == d_)[0]
        sel = sel[sel >= n_from]
        idx[sel] = rng.permutation(sel)
    return idx


def field_stats(G, label):
    T = np.arange(i_jun, len(G), STRIDE)
    p = T - 1
    disp = np.vstack([G[1:] - G[:-1], np.full((1, 3), np.nan)])
    out = {k: np.full(len(T), np.nan) for k in ("cos", "align", "pull", "rot", "noise", "geo_frac", "geo_resid", "dnorm")}
    for b in range(0, len(T), 60):
        sel = np.arange(b, min(b + 60, len(T)))
        t0 = T[sel[0]] - 1
        S = G[t0 - W_FIT: t0]; S = S[np.isfinite(S).all(1)]
        Sd = G[t0 - W_FIT: t0 - 1]; D = disp[t0 - W_FIT: t0 - 1]
        gd = np.isfinite(Sd).all(1) & np.isfinite(D).all(1); Sd, D = Sd[gd], D[gd]
        P = G[p[sel]]
        r = kde_eval(P, S, H_KDE, order=3)
        d2 = (P ** 2).sum(1)[:, None] + (Sd ** 2).sum(1)[None, :] - 2 * P @ Sd.T
        Wk = np.exp(-0.5 * np.maximum(d2, 0) / H_KDE ** 2)
        d = (Wk @ D) / np.maximum(Wk.sum(1, keepdims=True), 1e-300)
        step = G[T[sel]] - P
        v_in = P - G[p[sel] - 1]
        acc = step - v_in
        gl = -r.grad_phi
        gh = gl / np.linalg.norm(gl, axis=1, keepdims=True)
        pull = (d * gh).sum(1, keepdims=True) * gh
        rot = d - pull
        sn = np.linalg.norm(step, axis=1); dn = np.linalg.norm(d, axis=1)
        g_psd, _, _ = project_psd(r.hess_phi, PSD_FLOOR)
        Gam = christoffel_hessian(safe_inv(g_psd), r.phi3)
        a_geo = -np.einsum("nkij,ni,nj->nk", Gam, v_in, v_in)
        gnorm = lambda v: np.sqrt(np.maximum(np.einsum("ni,nij,nj->n", v, g_psd, v), 0))
        res = gnorm(acc - a_geo); an = gnorm(acc)
        out["cos"][sel] = (step * gh).sum(1) / sn
        out["align"][sel] = (step * d).sum(1) / (sn * dn)
        out["pull"][sel] = np.linalg.norm(pull, axis=1)
        out["rot"][sel] = np.linalg.norm(rot, axis=1)
        out["noise"][sel] = np.linalg.norm(step - d, axis=1)
        out["geo_resid"][sel] = res
        out["geo_frac"][sel] = res / an
        out["dnorm"][sel] = dn
    s = {"label": label, "n": int(len(T)),
         "cos_relevo_medio": float(np.nanmean(out["cos"])),
         "alinhamento_medio": float(np.nanmean(out["align"])),
         "puxada_media": float(np.nanmean(out["pull"])),
         "giro_medio": float(np.nanmean(out["rot"])),
         "ruido_medio": float(np.nanmean(out["noise"])),
         "forca_media": float(np.nanmean(out["dnorm"])),
         "frac_giro_na_forca": float(np.nanmean(out["rot"] / np.maximum(out["dnorm"], 1e-12))),
         "geo_frac_mediana": float(np.nanmedian(out["geo_frac"])),
         "geo_resid_mediana": float(np.nanmedian(out["geo_resid"]))}
    print(label, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}, flush=True)
    return s, out


def daily_sigma(G):
    nodes = np.full(len(G), 0)
    good = np.isfinite(G).all(1)
    nodes[good] = op.predict_node(G[good])
    counts = transition_counts(nodes[i_jun - W_RULER - 1: i_jun], N_NODES)
    sig = np.empty(len(G) - i_jun)
    for n_, t in enumerate(range(i_jun, len(G))):
        counts[nodes[t - 1], nodes[t]] += 1
        counts[nodes[t - W_RULER - 1], nodes[t - W_RULER]] -= 1
        sig[n_] = entropy_production(counts, op.sigma_pseudocount)
    days = day[i_jun:]
    return pd.Series(sig).groupby(days).mean()


res = {}
res["real"], real_series = field_stats(G_real, "real")
perm = within_day_perm(i_jun)
G_shuf = G_real[perm]
res["embaralhada"], _ = field_stats(G_shuf, "embaralhada")


def pipeline_surrogate():
    perm = within_day_perm(i_jun)
    r = np.log(kl.close.values)
    lr = np.diff(r, prepend=r[0])
    frac = kl.taker_buy.values / kl.volume.values
    lv = np.log(kl.volume.values)
    lr2, fr2, lv2 = lr[perm], frac[perm], lv[perm]
    close = np.exp(r[0] + np.cumsum(lr2))
    vol = np.exp(lv2)
    df = pd.DataFrame({"timestamp": kl.timestamp.values, "close": close, "volume": vol, "taker_buy": fr2 * vol})
    return gauss(coords(df))


G_pipe = pipeline_surrogate()
res["pipeline"], _ = field_stats(G_pipe, "pipeline")

sig_real = daily_sigma(G_real)
sig_shuf = daily_sigma(G_shuf)
sig_pipe = [daily_sigma(G_pipe)] + [daily_sigma(pipeline_surrogate()) for _ in range(N_PIPE - 1)]
pipe_mat = np.vstack([s.values for s in sig_pipe])
res["sigma_diario"] = {
    "dias": [str(d)[:10] for d in sig_real.index],
    "real": np.round(sig_real.values, 4).tolist(),
    "embaralhada": np.round(sig_shuf.values, 4).tolist(),
    "pipeline_media": np.round(pipe_mat.mean(0), 4).tolist(),
    "pipeline_max": np.round(pipe_mat.max(0), 4).tolist(),
    "frac_dias_real_acima_pipeline_max": float((sig_real.values > pipe_mat.max(0)).mean()),
    "real_medio": float(sig_real.mean()), "pipeline_medio": float(pipe_mat.mean()),
    "embaralhada_media": float(sig_shuf.mean())}
print("σ diário: real", round(sig_real.mean(), 4), " pipeline", round(pipe_mat.mean(), 4),
      " embaralhada", round(sig_shuf.mean(), 4), " dias real > máx pipeline:",
      res["sigma_diario"]["frac_dias_real_acima_pipeline_max"], flush=True)
json.dump(res, open(OUT + "nulls.json", "w"), indent=1)
