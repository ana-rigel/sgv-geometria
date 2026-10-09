#!/usr/bin/env python3
"""SGV: identificar a forma estatistica, SEM testar retorno futuro.

Hipotese observacional:
- Uma unica normal multivariada equivale a contornos de densidade elipsoidais.
- Student-t permite caudas pesadas, mas CONTINUA com contornos elipsoidais.
- Mistura de duas gaussianas e KDE permitem deformacoes nao elipsoidais.

Cada janela e estritamente historica (termina antes/de t); ajuste nos primeiros
70%, verificacao nos 30% finais da MESMA janela. Metricas sao log-densidade
nas observacoes ja disponiveis em t, NAO previsao de preco em t+h.
Janelas de avaliacao NAO SE SOBREPOEM. Bootstrap em blocos sobre janelas.
NUNCA usa periodos confirmatorios das linhas antigas.

Uso: python experiments/teste_forma_distribuicoes.py --interval synthetic|1m|1h
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy.special import gammaln
from scipy.stats import multivariate_normal
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import KernelDensity

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates

PERIODS = {"1m": ("2026-05", "2026-07"), "1h": ("2020-01", "2024-12")}
BARS_MS = {"1m": 60_000, "1h": 3_600_000}
WINDOW = {"1m": 1500, "1h": 1008}
FRACTION_TRAIN = 0.70
DF_CANDIDATES = (3., 4., 6., 10., 20., 40.)
KDE_BANDWIDTH = 0.55   # escala em coordenadas padronizadas; FIXA antes do BTC real
RIDGE = 1e-4
MODELS = ("gauss", "student", "mixture2", "kde")
SEED = 20261009


def shape_logpdf(y, mu, scale, nu):
    """Student-t d dimensional (scale nao equivale a covariancia)."""
    d = y.shape[1]
    delta = y-mu
    sign, logdet = np.linalg.slogdet(scale)
    if sign <= 0:
        raise ValueError("Student shape nao positiva")
    rad = np.sum(delta * np.linalg.solve(scale, delta.T).T, axis=1)
    a = gammaln((nu+d)/2) - gammaln(nu/2)
    b = -(d*np.log(nu*np.pi)+logdet)/2
    return a+b - (nu+d)*np.log1p(rad/nu)/2


def student_fit(train):
    """EM de localizacao/escala para grade discreta de graus de liberdade.

    Toda a selecao de nu ocorre SOMENTE nos 70% iniciais da janela.
    """
    n, d = train.shape
    best = None
    for nu in DF_CANDIDATES:
        mu = np.median(train, axis=0)
        cov = np.cov(train, rowvar=False) * max((nu-2)/nu, .1)
        cov += RIDGE*np.eye(d)
        for _ in range(18):
            dif = train-mu
            rad = np.sum(dif * np.linalg.solve(cov,dif.T).T, axis=1)
            w = (nu+d)/(nu+rad)
            mu = (w[:,None]*train).sum(axis=0)/w.sum()
            dif = train-mu
            cov = (w[:,None]*dif).T@dif/n + RIDGE*np.eye(d)
        score = float(np.mean(shape_logpdf(train,mu,cov,nu)))
        if best is None or score > best[0]:
            best = (score, mu, cov, nu)
    return best[1:]


def fit_evaluate_window(window):
    """Treina antes, avalia no resto da janela disponivel ao final."""
    n = len(window)
    cutoff = int(n*FRACTION_TRAIN)
    train, test = window[:cutoff], window[cutoff:]
    center = train.mean(axis=0)
    scale = train.std(axis=0, ddof=1)
    if np.any(scale < 1e-8):
        raise ValueError("coordenadas degeneradas")
    a, b = (train-center)/scale, (test-center)/scale
    cov = np.cov(a,rowvar=False) + RIDGE*np.eye(a.shape[1])
    scores = {"gauss": float(np.mean(multivariate_normal.logpdf(
        b, mean=a.mean(axis=0), cov=cov)))}
    mu_t, sig_t, nu = student_fit(a)
    scores["student"] = float(np.mean(shape_logpdf(b,mu_t,sig_t,nu)))
    mix = GaussianMixture(n_components=2,covariance_type="full",
                          reg_covar=RIDGE,n_init=2,max_iter=100,random_state=SEED)
    mix.fit(a)
    scores["mixture2"] = float(np.mean(mix.score_samples(b)))
    kde = KernelDensity(kernel="gaussian",bandwidth=KDE_BANDWIDTH)
    kde.fit(a)
    scores["kde"] = float(np.mean(kde.score_samples(b)))
    # D de separacao dos centros da mistura. NAO equivale a numero de modos.
    pooled = (mix.covariances_[0]+mix.covariances_[1])/2
    delta = mix.means_[0]-mix.means_[1]
    sep = float(np.sqrt(delta@np.linalg.solve(pooled,delta)))
    weights = sorted(float(z) for z in mix.weights_)
    return {"logscore":scores,"df_student":float(nu),
            "separacao_centros_mistura":sep,
            "peso_menor_componente":weights[0],
            "n_train":cutoff,"n_test":n-cutoff}


def windows(X, timestamps, window, step, *, min_valid=0):
    """Itera janelas sem sobreposicao, cada uma estritamente anterior a asof."""
    assert len(X)==len(timestamps)
    for end in range(window,len(X)+1,window):
        y = X[end-window:end]
        ts = timestamps[end-window:end]
        if np.any(np.diff(ts)!=step) or not np.isfinite(y).all():
            continue
        if int(ts[-1])+step <= min_valid:
            continue
        yield end, int(ts[-1]+step), y


def summarize(rows, *, seed=SEED):
    if len(rows)<6:
        raise ValueError(f"Janelas insuficientes: {len(rows)}")
    rng=np.random.default_rng(seed)
    data = {model:np.array([r["logscore"][model] for r in rows])
            for model in MODELS}
    n=len(rows)
    boot_bars=4 if n>=20 else 2
    B=1600
    starts=np.arange(0,n-boot_bars+1)
    indices=np.empty((B,n),dtype=int)
    for b in range(B):
        v=[]
        while len(v)<n:
            j=int(rng.choice(starts))
            v.extend(range(j,j+boot_bars))
        indices[b,:]=v[:n]
    deltas={}
    for model in MODELS[1:]:
        d=data[model]-data["gauss"]
        bs=np.mean(d[indices],axis=1)
        deltas[model]={
            "media_nat_por_observacao":float(np.mean(d)),
            "mediana_janelas":float(np.median(d)),
            "fracao_janelas_melhores":float(np.mean(d>0)),
            "IC95_boot_blocos":[float(x) for x in np.quantile(bs,[.025,.975])],
            "ganho_com_IC95_inteiro_positivo":bool(np.quantile(bs,.025)>0)}
    # Testar se KDE representa algo alem da familia elipsoidal Student-t.
    d=data["kde"]-data["student"]
    bs=np.mean(d[indices],axis=1)
    vs=np.array([r["separacao_centros_mistura"] for r in rows])
    wt=np.array([r["peso_menor_componente"] for r in rows])
    return {
      "n_janelas_sem_sobreposicao":n,
      "n_observacoes_teste_por_janela":rows[0]["n_test"],
      "bootstrap_blocos_janelas":boot_bars,
      "gain_vs_gauss":deltas,
      "kde_vs_student":{
          "media_nat_por_observacao":float(np.mean(d)),
          "IC95_boot_blocos":[float(x) for x in np.quantile(bs,[.025,.975])],
          "IC95_inteiro_positivo":bool(np.quantile(bs,.025)>0)},
      "mistura2_separacao_centros_mediana":float(np.median(vs)),
      "fracao_separacao_geq4_e_pesos_geq_015":float(np.mean((vs>=4)&(wt>=.15))),
      "df_student_mediana":float(np.median([r["df_student"] for r in rows])),
      "avisos":[
        "Student-t de uma componente tem contornos ELIPSOIDAIS: ganhar da normal nao prova forma nao elipsoidal",
        "Mistura2 com centros separados NAO prova dois modos; KDE melhor nao prova topologia",
        "Logscore testa fidelidade densidade sob mudanca temporal, NAO rentabilidade nem preco futuro",
        "Bootstrap dos scores por blocos de janelas, condicional a configuracao fixa e dados exploratorios",
        "Comparacao entre modelos exige controles adicionais contra dependencia serial e regimes",
      ],
    }


def evaluate_series(X,timestamps, *, win, step):
    rows=[]
    for end, asof, y in windows(X,timestamps,win,step):
        try:
            r=fit_evaluate_window(y)
        except (ValueError, np.linalg.LinAlgError) as exc:
            continue
        rows.append({"end":int(end),"asof_ms":asof,**r})
    return rows


def synthetic_data(kind,n,seed):
    rng=np.random.default_rng(seed)
    z=rng.normal(size=(n,3))
    z[:,1]=.55*z[:,0]+np.sqrt(1-.55**2)*z[:,1]
    if kind=="gauss":
        return z
    if kind=="student_t4":
        return z/np.sqrt(rng.chisquare(4,n)[:,None]/4)
    if kind=="mixture":
        state=rng.choice([-1.,1.],size=n)
        z[:,0]=z[:,0]*.45 + 2.3*state
        z[:,1]=z[:,1]*.45 + 1.6*state
        return z
    if kind=="curved":
        z[:,1]=.9*(z[:,0]**2-1)+.25*rng.normal(size=n)
        return z
    raise ValueError(kind)


def synthetic_calibration():
    cases={}
    for j,kind in enumerate(("gauss","student_t4","mixture","curved")):
        x=synthetic_data(kind,16*900,seed=1330+j)
        t=60_000*np.arange(len(x),dtype=np.int64)
        rows=evaluate_series(x,t,win=900,step=60_000)
        cases[kind]=summarize(rows,seed=SEED+j)
    return cases


def real(interval):
    paths=sorted((ROOT/"data").glob(f"BTCUSDT-{interval}-*.zip"))
    lo,hi=PERIODS[interval]
    if not paths:
        raise FileNotFoundError("Exploracao nao encontrada. Execute scripts/baixar_klines.py.")
    for p in paths:
        m=re.fullmatch(rf"BTCUSDT-{interval}-(\d{{4}}-\d{{2}})\.zip",p.name)
        if not m or not(lo<=m.group(1)<=hi):
            raise ValueError(f"Periodo reservado/proibido: {p.name}")
    df=load_binance_klines(paths,with_flow=True)
    feats=flow_coordinates(df)
    X=feats[["z","iota","nu"]].to_numpy(float)
    ts=df["timestamp"].to_numpy(np.int64)
    rows=evaluate_series(X,ts,win=WINDOW[interval],step=BARS_MS[interval])
    return [p.name for p in paths],rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--interval",required=True,choices=["synthetic","1m","1h"])
    args=ap.parse_args()
    if args.interval=="synthetic":
        report={"status":"CALIBRACAO_SINTETICA_FORMA","casos":synthetic_calibration()}
        rows=[]
    else:
        files,rows=real(args.interval)
        report={"status":"TESTE_DESCRITIVO_EXPLORATORIO","ativo":"BTCUSDT spot",
                "timeframe":args.interval,"arquivos":files,
                "coordenadas":["z","iota","nu"],"janela":WINDOW[args.interval],
                "treino_primeiros_70pct_validacao_ultimos_30pct":True,
                "sem_dados_confirmatorios":True,
                "resultados":summarize(rows)}
    dest=ROOT/"reports"/f"FORMA_DISTRIBUICOES_{args.interval}.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    if rows:
        import csv
        tab=dest.with_name(dest.stem+"_janelas.csv")
        with tab.open("w",newline="") as f:
            keys=["asof_ms","end","n_train","n_test","df_student",
                  "separacao_centros_mistura","peso_menor_componente",*MODELS]
            w=csv.DictWriter(f,fieldnames=keys)
            w.writeheader()
            for row in rows:
                flat={k:v for k,v in row.items() if k!="logscore"}
                flat.update(row["logscore"])
                w.writerow(flat)
    print(json.dumps(report if args.interval=="synthetic" else
       {**report,"arquivos":[f"{len(files)} arquivo(s) autorizados"]},
       ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
