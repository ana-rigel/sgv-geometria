#!/usr/bin/env python3
"""SGV: fotografia observacional do mercado — pesquisa nova, sem previsão.

Representação de cada barra fechada: X=(retorno/vol passada, desequilíbrio
agressor, atividade relativa). Uma janela APENAS PASSADA estima média e
covariância. A covariância define uma métrica de Fisher da família GAUSSIANA
DE LOCALIZAÇÃO, g=Sigma^{-1}; isto NÃO é a curvatura de Fisher de C1/R1.
A diferença de estados usa a distância de Bhattacharyya entre as aproximações
gaussianas de duas janelas. Não há retornos futuros nem alvos preditivos.

O retrato NÃO cobre livro de ordens, cancelamentos, posições ou informação
privada; contém apenas as coordenadas observadas e a resolução dos candles.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = {"1m": ("2026-05", "2026-07"), "1h": ("2020-01", "2024-12")}
RESERVED = {"1m": "2026-08", "1h": "2025-01"}
STEP_MS = {"1m": 60_000, "1h": 3_600_000}
CONFIG = {"1m": {"window": 600, "stride": 60},
          "1h": {"window": 168, "stride": 24}}
COORDS = ("z", "iota", "nu")


def gaussian_snapshot(samples: np.ndarray) -> dict:
    """Fisher de localização condicionada à Sigma estimada na janela."""
    x = np.asarray(samples, dtype=float)
    if x.ndim != 2 or x.shape[0] < 24 or x.shape[1] != 3:
        raise ValueError("esperadas >=24 observações de 3 coordenadas")
    if not np.isfinite(x).all():
        raise ValueError("janela não finita")
    m = x.mean(axis=0)
    c = np.cov(x, rowvar=False)
    eig = np.linalg.eigvalsh(c)
    if eig.min() <= max(eig.max()*1e-10, 1e-15):
        raise ValueError("covariância degenerada; fotografia indisponível")
    sd = np.sqrt(np.diag(c))
    corr = c / np.outer(sd, sd)
    sign, logdet = np.linalg.slogdet(c)
    if sign <= 0:
        raise ValueError("não SPD")
    return {"mean": m, "cov": c, "fisher_location": np.linalg.inv(c),
            "corr": corr, "logdet_cov": float(logdet),
            "condition": float(eig.max()/eig.min())}


def bhattacharyya(A: dict, B: dict) -> float:
    """Distância gaussiana afim-invariante; mede separação, não causalidade."""
    cov = (A["cov"] + B["cov"]) / 2
    diff = B["mean"] - A["mean"]
    sign, ld = np.linalg.slogdet(cov)
    if sign <= 0:
        raise ValueError("covariância intermediária não SPD")
    d = float((diff @ np.linalg.solve(cov, diff)) / 8 +
              (ld - .5*(A["logdet_cov"]+B["logdet_cov"])) / 2)
    return float(max(d, 0.0))


def direct_snapshots(X: np.ndarray, timestamps: np.ndarray, *,
                     window: int, stride: int, bar_ms: int):
    """Inclui somente barras fechadas até t; t é índice da última barra."""
    rows = []
    for t in range(window-1, len(X), stride):
        z = X[t-window+1:t+1]
        ts = timestamps[t-window+1:t+1]
        if not np.isfinite(z).all() or np.any(np.diff(ts) != bar_ms):
            continue
        try:
            s = gaussian_snapshot(z)
            o = gaussian_snapshot(z[::2])
            e = gaussian_snapshot(z[1::2])
        except ValueError:
            continue
        rows.append({"t": int(t), "asof_ms": int(timestamps[t]+bar_ms),
                     "rho_price_flow": float(s["corr"][0, 1]),
                     "rho_activity_flow": float(s["corr"][1, 2]),
                     "rho_price_activity": float(s["corr"][0, 2]),
                     "logdet_cov": s["logdet_cov"],
                     "condition": s["condition"],
                     "mu": [float(v) for v in s["mean"]],
                     "cov": [[float(v) for v in line] for line in s["cov"]],
                     "rho_price_flow_odd": float(o["corr"][0,1]),
                     "rho_price_flow_even": float(e["corr"][0,1])})
    # Compare semelhança das distribuições em duas janelas não sobrepostas.
    # Não usa nenhum estado com asof maior que o estado avaliado.
    for j, row in enumerate(rows):
        older = next((q for q in reversed(rows[:j])
                      if q["t"] <= row["t"] - window), None)
        if older is None:
            row["distance_to_past"] = None
            continue
        def unpack(v):
            return {"mean":np.asarray(v["mu"]), "cov":np.asarray(v["cov"]),
                    "logdet_cov":v["logdet_cov"]}
        row["distance_to_past"] = bhattacharyya(unpack(older), unpack(row))
    return rows


def spearman(a, b) -> float | None:
    from scipy.stats import spearmanr
    if len(a) < 15 or np.std(a) <= 1e-14 or np.std(b) <= 1e-14:
        return None
    r = spearmanr(a, b).statistic
    return float(r) if np.isfinite(r) else None


def summarize(rows):
    import pandas as pd
    if not rows:
        raise RuntimeError("Nenhuma janela contemporânea válida")
    def pct(col):
        a=np.asarray([x[col] for x in rows if x[col] is not None],float)
        return {"p05":float(np.quantile(a,.05)),"p50":float(np.median(a)),
                "p95":float(np.quantile(a,.95))} if len(a) else None
    return {
        "n_fotografias":len(rows),
        "primeiro_estado_utc":pd.to_datetime(rows[0]["asof_ms"],unit="ms",utc=True).isoformat(),
        "ultimo_estado_utc":pd.to_datetime(rows[-1]["asof_ms"],unit="ms",utc=True).isoformat(),
        "correlacao_preco_fluxo":pct("rho_price_flow"),
        "correlacao_atividade_fluxo":pct("rho_activity_flow"),
        "condicionamento_metrica":pct("condition"),
        "bhattacharyya_janelas_nao_sobrepostas":pct("distance_to_past"),
        "confiabilidade_rho_preco_fluxo_par_impar":spearman(
            [x["rho_price_flow_odd"] for x in rows],
            [x["rho_price_flow_even"] for x in rows]),
        "primeiros_exemplos": [{k:v for k,v in x.items() if k not in
            ("cov","mu","rho_price_flow_odd","rho_price_flow_even")}
            for x in rows[:3]],
        "ultimos_exemplos": [{k:v for k,v in x.items() if k not in
            ("cov","mu","rho_price_flow_odd","rho_price_flow_even")}
            for x in rows[-3:]]
    }


def real_exploration(interval):
    from sgvgeo.data import load_binance_klines
    from sgvgeo.flow import flow_coordinates
    paths = sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    if not paths:
        raise FileNotFoundError("Baixe apenas os meses de exploração usando scripts/baixar_klines.py")
    for p in paths:
        m = re.fullmatch(rf"BTCUSDT-{interval}-(\d{{4}}-\d{{2}})\.zip",p.name)
        if m is None or not(EXPLORATION[interval][0]<=m.group(1)<=EXPLORATION[interval][1]):
            raise ValueError(f"Arquivo fora da exploração: {p.name}")
    data=load_binance_klines(paths,with_flow=True)
    f=flow_coordinates(data)
    X=f[list(COORDS)].to_numpy(float)
    timestamps=data["timestamp"].to_numpy(np.int64)
    cfg=CONFIG[interval]
    rows=direct_snapshots(X,timestamps,window=cfg["window"],
                          stride=cfg["stride"],bar_ms=STEP_MS[interval])
    return paths,rows


def synthetic_calibration(seed=21):
    """Capta inversão de correlação com marginais constantes. Também registra
    caso cego: dependência não-linear sem correlação de 1a ordem."""
    rng=np.random.default_rng(seed)
    n=3000
    z=rng.normal(size=n)
    eps=rng.normal(size=n)
    rho=.75
    y=np.sqrt(1-rho*rho)*eps + np.where(np.arange(n)<n//2,rho,-rho)*z
    v=rng.normal(size=n)
    X=np.column_stack([z,y,v])
    W=300
    before=gaussian_snapshot(X[700:1000])
    after=gaussian_snapshot(X[2100:2400])
    mirror=gaussian_snapshot(X[700:1000] @ np.diag([3.,2.,.5])+np.array([2.,-1.,4.]))
    original=gaussian_snapshot(X[700:1000])
    # Bhattacharyya é invariante sob a mesma transformação afim nas duas amostras
    transform=np.array([[1.7,.1,.2],[-.3,2.2,.1],[.4,.2,.8]])
    shift=np.array([1.,-3.,2.])
    c0=gaussian_snapshot(X[700:1000]@transform+shift)
    c1=gaussian_snapshot(X[2100:2400]@transform+shift)
    d1=bhattacharyya(before,after)
    d2=bhattacharyya(c0,c1)
    nonlinear_z=rng.normal(size=6000)
    nonlinear_y=(nonlinear_z**2-1)/np.sqrt(2)+rng.normal(size=6000)*.1
    return {
        "rho_preco_fluxo_antes":float(before["corr"][0,1]),
        "rho_preco_fluxo_depois":float(after["corr"][0,1]),
        "variancia_z_antes_depois":[float(before["cov"][0,0]),float(after["cov"][0,0])],
        "bhattacharyya_regime":d1,
        "erro_invariancia_transformacao_afim":abs(d1-d2),
        "ponto_cego_correlacao_linear":float(np.corrcoef(nonlinear_z,nonlinear_y)[0,1]),
        "ponto_cego_correlacao_quadratica":float(np.corrcoef(nonlinear_z**2,nonlinear_y)[0,1])
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--interval",choices=("1m","1h","synthetic"),required=True)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    if args.interval=="synthetic":
        out={"tipo":"CALIBRACAO_SINTETICA_NAO_PREDITIVA",
             "metricas":synthetic_calibration()}
    else:
        files,rows=real_exploration(args.interval)
        out={"tipo":"FOTOGRAFIA_DESCRITIVA_EXPLORATORIA",
             "ativo":"BTCUSDT spot","intervalo":args.interval,
             "arquivos":[p.name for p in files],"coordenadas":list(COORDS),
             "modelo":"Gaussiano local: media, Sigma, Fisher localizacao=Sigma^-1",
             "janela_barras":CONFIG[args.interval]["window"],
             "passo_barras":CONFIG[args.interval]["stride"],
             "disponibilidade":"Fechamento da ultima barra, nao intra-candle",
             "sem_alvo_futuro":True,"resultado":summarize(rows)}
    dest=args.out or ROOT/"reports"/f"FOTO_INFORMACIONAL_{args.interval}.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(out,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
