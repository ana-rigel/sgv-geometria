#!/usr/bin/env python3
"""SGV-M31 confirmatorio (protocolo reports/PROTOCOLO_SGV_M31_20261012.md, CONGELADO).

--mode ensaio        : pipeline inteiro em dados SINTETICOS (nenhum BTC/ETH real).
--mode confirmatorio : confere SHA-256 do protocolo e do modulo de engenharia; baixa SO
                       ETHUSDT 1m 2026-05..2026-09; avalia T1 -> T2 -> T3 em hierarquia.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm
ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT,ROOT/'scripts'):
    if str(p) not in sys.path:sys.path.insert(0,str(p))
from experiments import m31g1_engenharia as m
from experiments.m31g0_features_causais import qlike_deviance
from sgvgeo.data import load_binance_klines

PROTO=ROOT/'reports'/'PROTOCOLO_SGV_M31_20261012.md'
ENG=ROOT/'experiments'/'m31g1_engenharia.py'
ENG_SHA='f8a277236f74554e6dc3016571b620ec70b578a3be65b10bb4ef9912c7072476'
MONTHS=('2026-05','2026-06','2026-07','2026-08','2026-09')
EVAL=(pd.Timestamp('2026-06-01',tz='UTC').value//10**6,pd.Timestamp('2026-10-01',tz='UTC').value//10**6)
LAG=96;BOOT=2000;BLOCK=96
CRIT={'T1':('B1','B0',.01),'T2':('B1plus','B0plus',.005),'T3':('B2','B1plus',.005)}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def gate(proto_sha):
    t=PROTO.read_bytes()
    if sha(PROTO)!=proto_sha or b'STATUS: CONGELADO' not in t:raise SystemExit(f'protocolo nao confere: {sha(PROTO)}')
    if sha(ENG)!=ENG_SHA:raise SystemExit(f'modulo de engenharia alterado: {sha(ENG)}')
    return sha(PROTO)


def compare(dnew,dref,min_skill):
    dif=dnew-dref;se=m.hac_se(dif,LAG);z=float(dif.mean()/se) if se>0 else float('nan')
    p=float(norm.cdf(z));skill=float(1-dnew.mean()/dref.mean())
    return {'n':int(len(dif)),'dev_media_novo':float(dnew.mean()),'dev_media_ref':float(dref.mean()),'delta_medio':float(dif.mean()),
            'ep_hac':float(se),'z':z,'p_unilateral':p,'skill':skill,'skill_minimo':min_skill,'passa':bool(p<.05 and skill>=min_skill)}


def boot_p(dif,seed=0):
    rng=np.random.default_rng(seed);n=len(dif);nb=int(math.ceil(n/BLOCK));mh=dif.mean();ms=np.empty(BOOT)
    for b in range(BOOT):
        st=rng.integers(0,n,nb);idx=((st[:,None]+np.arange(BLOCK)[None,:])%n).ravel()[:n];ms[b]=dif[idx].mean()
    return float(np.mean((ms-mh)<=mh))


def evaluate(d,ev):
    rv=d.rv_future_15.to_numpy(float);ts=d.origin_ts.to_numpy(np.int64)
    F={k:m.rolling_forecasts(d,m.MODELS[k]) for k in ('B0','B0plus','B1','B1plus')}
    mask=(ts>=ev[0])&(ts<ev[1])
    for v in F.values():mask&=np.isfinite(v)
    dev={k:qlike_deviance(v[mask],rv[mask]) for k,v in F.items()}
    out={'n_origens_total':int(len(d)),'n_avaliadas':int(mask.sum())}
    out['T1']=compare(dev['B1'],dev['B0'],CRIT['T1'][2]);out['T1']['p_bootstrap_bloco_dia']=boot_p(dev['B1']-dev['B0'])
    out['T2']=compare(dev['B1plus'],dev['B0plus'],CRIT['T2'][2]) if out['T1']['passa'] else {'testado':False}
    if out['T1']['passa'] and out['T2']['passa']:
        ds=d[d.saddle_frac.notna()].reset_index(drop=True);rs=ds.rv_future_15.to_numpy(float);tss=ds.origin_ts.to_numpy(np.int64)
        a=m.rolling_forecasts(ds,m.MODELS['B1plus']);b=m.rolling_forecasts(ds,m.MODELS['B2'])
        mk=(tss>=ev[0])&(tss<ev[1])&np.isfinite(a)&np.isfinite(b)
        out['T3']=compare(qlike_deviance(b[mk],rs[mk]),qlike_deviance(a[mk],rs[mk]),CRIT['T3'][2])
    else:out['T3']={'testado':False}
    # descritivos (sem decisao)
    out['descritivo']={'skill_B0plus_vs_B0':float(1-dev['B0plus'].mean()/dev['B0'].mean()),
        'fracao_casca_valida':float(d.saddle_frac.notna().mean()),
        'skill_B1_vs_B0_por_mes':{}}
    mon=pd.to_datetime(ts[mask],unit='ms',utc=True).strftime('%Y-%m')
    for mo in sorted(set(mon)):
        s=mon==mo;out['descritivo']['skill_B1_vs_B0_por_mes'][mo]=float(1-dev['B1'][s].mean()/dev['B0'][s].mean())
    T1,T2,T3=out['T1'],out['T2'],out['T3']
    out['leitura']=('T1 FALHA: a forma nao acrescenta informacao de risco relevante ao baseline forte' if not T1['passa'] else
                    'T1 PASSA, T2 FALHA: contribuicao de descoberta (a elasticidade movel captura o efeito)' if not T2.get('passa') else
                    'T1 e T2 PASSAM, T3 FALHA: informacao nas estatisticas condicionais da forma, nao na casca' if not T3.get('passa') else
                    'T1, T2 e T3 PASSAM: contribuicao geometrica intrinseca')
    pred=pd.DataFrame({'origin_ts':ts,**{f'v_{k}':v for k,v in F.items()},'rv':rv,'avaliada':mask})
    return out,pred


def report(o,mode,src):
    f=lambda x:'—' if x is None else f'{x:.4f}'
    L=[f'# SGV-M31 — resultado ({mode})','',f'Fonte: {src}. Origens: {o["n_origens_total"]}; avaliadas: **{o["n_avaliadas"]}**.','',
       '| Teste | Comparação | skill | p (HAC) | critério | resultado |','|---|---|---|---|---|---|']
    for t,(a,b,ms) in CRIT.items():
        r=o[t]
        if r.get('testado') is False:L.append(f'| {t} | {a} vs {b} | — | — | skill ≥ {ms:.1%} | não testado (hierarquia) |');continue
        L.append(f"| {t} | {a} vs {b} (n={r['n']}) | {r['skill']:+.2%} | {r['p_unilateral']:.3g} | p<0,05 e skill ≥ {ms:.1%} | **{'PASSA' if r['passa'] else 'FALHA'}** |")
    L+=['',f"**Leitura pré-registrada:** {o['leitura']}",'',f"p de T1 por bootstrap em blocos de 1 dia: {o['T1']['p_bootstrap_bloco_dia']:.3g}",'',
        '**Descritivos (sem decisão):** '+json.dumps(o['descritivo'],ensure_ascii=False)]
    return '\n'.join(L)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('ensaio','confirmatorio'),required=True);ap.add_argument('--protocol-sha')
    a=ap.parse_args();out=ROOT/'reports'/'m31';out.mkdir(parents=True,exist_ok=True)
    if a.mode=='ensaio':
        frame=m.synthetic_klines(n=60_000,seed=31);t0=int(frame.timestamp.iloc[0])
        ev=(t0+20*86_400_000,int(frame.timestamp.iloc[-1])+1);src='SINTÉTICO (ensaio do pipeline)'
    else:
        ps=gate(a.protocol_sha);import baixar_klines as bk;bk.SYMBOL='ETHUSDT';bk.DEST.mkdir(exist_ok=True)
        for mo in MONTHS:
            msg=bk.download_month('1m',mo);print(msg)
            if not msg.startswith(('ok','já estava ok')):raise SystemExit('download falhou: '+msg)
        paths=[ROOT/'data'/f'ETHUSDT-1m-{mo}.zip' for mo in MONTHS]
        frame=load_binance_klines(paths,with_flow=True);ev=EVAL;src='ETHUSDT spot 1m 2026-05..09 (avaliação jun–set)'
    d,seg=m.build(frame,with_shell=True)
    o,pred=evaluate(d,ev);o.update({'modo':a.mode,'fonte':src,**seg})
    if a.mode=='confirmatorio':o['protocolo_sha256']=ps;o['engenharia_sha256']=ENG_SHA
    (out/f'm31_{a.mode}.json').write_text(json.dumps(o,indent=1,ensure_ascii=False))
    pred.to_csv(out/f'm31_{a.mode}_previsoes.csv.gz',index=False,compression='gzip')
    md=report(o,a.mode,src);(out/f'SGV_M31_{a.mode.upper()}.md').write_text(md+'\n');print(md)


if __name__=='__main__':main()
