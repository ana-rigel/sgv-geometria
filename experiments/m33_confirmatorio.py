#!/usr/bin/env python3
"""SGV-M33 confirmatorio — T3 original (protocolo reports/PROTOCOLO_SGV_M33_20261013.md, CONGELADO).
--mode ensaio        : pipeline em dados SINTETICOS.
--mode confirmatorio : confere SHA-256 (protocolo + 3 modulos); baixa SO BNBUSDT 1m 2026-05..09."""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import norm
ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT,ROOT/'scripts'):
    if str(p) not in sys.path:sys.path.insert(0,str(p))
from experiments import m33_t3 as m
from experiments import m31g1_engenharia as g
from experiments.m31g0_features_causais import qlike_deviance
from sgvgeo.data import load_binance_klines
PROTO=ROOT/'reports'/'PROTOCOLO_SGV_M33_20261013.md'
SHAS={ROOT/'experiments'/'m33_t3.py':'4b907dc6712483485e4535facff5bf9e16f18c30f1c7a607cd29cd7d56a5b09d',
      ROOT/'experiments'/'m32_casca.py':'42249e3d38b2da4889d5a5f90d47fcc2ca06edbbca2e1b512b4009b98abb78a5',
      ROOT/'experiments'/'m31g1_engenharia.py':'f8a277236f74554e6dc3016571b620ec70b578a3be65b10bb4ef9912c7072476'}
MONTHS=('2026-05','2026-06','2026-07','2026-08','2026-09')
EVAL=(pd.Timestamp('2026-06-01',tz='UTC').value//10**6,pd.Timestamp('2026-10-01',tz='UTC').value//10**6)
MIN_SKILL=.005;LAGS=(96,672)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def gate(ps):
    if sha(PROTO)!=ps or b'STATUS: CONGELADO' not in PROTO.read_bytes():raise SystemExit('protocolo nao confere: '+sha(PROTO))
    for p,h in SHAS.items():
        if sha(p)!=h:raise SystemExit(f'modulo alterado: {p.name} {sha(p)}')
    return ps
def boot(dif,m0,block,seed=0,B=2000):
    rng=np.random.default_rng(seed);n=len(dif);nb=math.ceil(n/block);ms=np.empty(B)
    for b in range(B):
        st=rng.integers(0,n,nb);idx=((st[:,None]+np.arange(block))%n).ravel()[:n];ms[b]=dif[idx].mean()
    mh=dif.mean();return {'p':float(np.mean((ms-mh)<=mh)),'ic95_skill':[float(-np.quantile(ms,.975)/m0),float(-np.quantile(ms,.025)/m0)]}
def evaluate(d,ev):
    n_all=len(d);dv=d[d.saddle_frac.notna()].reset_index(drop=True)
    rv=dv.rv_future_15.to_numpy(float);ts=dv.origin_ts.to_numpy(np.int64)
    F={k:m.rolling_forecasts(dv,c) for k,c in (('B0',g.B0),('B1plus',m.B1PLUS),('B2',m.B2))}
    mk=(ts>=ev[0])&(ts<ev[1])&np.isfinite(rv)&(rv>0)
    for v in F.values():mk&=np.isfinite(v)
    dev={k:qlike_deviance(v[mk],rv[mk]) for k,v in F.items()};dif=dev['B2']-dev['B1plus'];m0=dev['B1plus'].mean()
    ses={l:g.hac_se(dif,l) for l in LAGS};p={l:float(norm.cdf(dif.mean()/ses[l])) for l in LAGS};sk=float(-dif.mean()/m0)
    o={'n_origens_elegiveis':int(n_all),'n_casca_valida':int(len(dv)),'fracao_casca_valida':float(len(dv)/n_all),
       'n_avaliadas':int(mk.sum()),'skill':sk,'delta_medio':float(dif.mean()),'dev_B1plus':float(m0),'dev_B2':float(dev['B2'].mean()),
       'p_hac_1dia':p[96],'p_hac_1semana':p[672],
       'ic95_skill_hac_1dia':[float((-dif.mean()-1.96*ses[96])/m0),float((-dif.mean()+1.96*ses[96])/m0)],
       'ic95_skill_hac_1semana':[float((-dif.mean()-1.96*ses[672])/m0),float((-dif.mean()+1.96*ses[672])/m0)]}
    o['passa']=bool(p[96]<.05 and p[672]<.05 and sk>=MIN_SKILL)
    o['descritivo']={'bootstrap_1dia':boot(dif,m0,96),'bootstrap_1semana':boot(dif,m0,672),
                     'skill_B1plus_vs_B0_contexto':float(1-dev['B1plus'].mean()/dev['B0'].mean()),'skill_B2_vs_B0_contexto':float(1-dev['B2'].mean()/dev['B0'].mean()),'skill_por_mes':{}}
    mon=pd.to_datetime(ts[mk],unit='ms',utc=True).strftime('%Y-%m')
    for mo in sorted(set(mon)):s=mon==mo;o['descritivo']['skill_por_mes'][mo]=float(1-dev['B2'][s].mean()/dev['B1plus'][s].mean())
    pred=pd.DataFrame({'origin_ts':ts,'saddle_frac':dv.saddle_frac,**{f'v_{k}':v for k,v in F.items()},'rv':rv,'avaliada':mk})
    return o,pred
def report(o,mode,src):
    pc=lambda x:f'{100*x:+.2f}%'
    L=[f'# SGV-M33 — T3 original: curvatura além de forma e elasticidade (resultado, {mode})','',f'Fonte: {src}. Origens elegíveis: {o["n_origens_elegiveis"]}; casca válida: {o["n_casca_valida"]} ({o["fracao_casca_valida"]:.1%}); avaliadas: **{o["n_avaliadas"]}**.','',
       '| | valor |','|---|---|',f'| skill B2 vs B1+ | **{pc(o["skill"])}** |',f'| p (HAC 1 dia) | {o["p_hac_1dia"]:.3g} |',f'| p (HAC 1 semana) | {o["p_hac_1semana"]:.3g} |',
       f'| IC 95% do skill (HAC 1 dia) | {pc(o["ic95_skill_hac_1dia"][0])} a {pc(o["ic95_skill_hac_1dia"][1])} |',
       f'| IC 95% do skill (HAC 1 semana) | {pc(o["ic95_skill_hac_1semana"][0])} a {pc(o["ic95_skill_hac_1semana"][1])} |','',
       f'**Primário (p < 0,05 nas duas escalas e skill ≥ 0,5%): {"PASSA" if o["passa"] else "FALHA"}**','',
       '**Descritivos:** '+json.dumps(o['descritivo'],ensure_ascii=False)]
    return '\n'.join(L)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('ensaio','confirmatorio'),required=True);ap.add_argument('--protocol-sha')
    a=ap.parse_args();out=ROOT/'reports'/'m33';out.mkdir(parents=True,exist_ok=True)
    if a.mode=='ensaio':
        frame=m.synthetic_klines(n=40_000,seed=33);t0=int(frame.timestamp.iloc[0]);ev=(t0+16*86_400_000,int(frame.timestamp.iloc[-1])+1);src='SINTÉTICO'
    else:
        ps=gate(a.protocol_sha);import baixar_klines as bk;bk.SYMBOL='BNBUSDT';bk.DEST.mkdir(exist_ok=True)
        for mo in MONTHS:
            msg=bk.download_month('1m',mo);print(msg)
            if not msg.startswith(('ok','já estava ok')):raise SystemExit('download falhou: '+msg)
        frame=load_binance_klines([ROOT/'data'/f'BNBUSDT-1m-{mo}.zip' for mo in MONTHS],with_flow=True);ev=EVAL;src='BNBUSDT spot 1m 2026-05..09 (avaliação jun–set)'
    d,seg=m.build(frame);o,pred=evaluate(d,ev);o.update({'modo':a.mode,'fonte':src,**seg})
    if a.mode=='confirmatorio':o['protocolo_sha256']=ps
    (out/f'm33_{a.mode}.json').write_text(json.dumps(o,indent=1,ensure_ascii=False));pred.to_csv(out/f'm33_{a.mode}_previsoes.csv.gz',index=False,compression='gzip')
    md=report(o,a.mode,src);(out/f'SGV_M33_{a.mode.upper()}.md').write_text(md+'\n');print(md)
if __name__=='__main__':main()
