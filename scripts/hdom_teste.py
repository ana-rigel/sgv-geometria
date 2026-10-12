#!/usr/bin/env python3
"""H-DOM (protocolo reports/PROTOCOLO_SGV_HDOM_20261012.md, congelado).
--mode ensaio        : dados exploratorios (mai-jul/2026) -> deve reproduzir scripts/forma_dominancia.py
--mode confirmatorio : exige o SHA-256 do protocolo; baixa SO 1m 2026-08 e 2026-09 e julga o primario."""
from __future__ import annotations
import argparse,hashlib,json,sys;from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scipy.stats import rankdata,norm,spearmanr,binomtest
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
PROTO=ROOT/'reports'/'PROTOCOLO_SGV_HDOM_20261012.md'
W=360;P0=2*norm.cdf(.3)-1;CUT_C=.71;CUT_K=1.86;H=(15,60,240);COST=.001
TEST_MONTHS=('2026-08','2026-09');EXPLO_MONTHS=('2026-05','2026-06','2026-07')
def cop(x):return norm.ppf(np.column_stack([rankdata(x[:,j])/(len(x)+1) for j in range(3)]))
def windows(paths):
    df=load_binance_klines(paths,with_flow=True)
    F=flow_coordinates(df)[['z','iota','nu']].to_numpy(float);ok=np.isfinite(F).all(1);idx=np.flatnonzero(ok)
    ts=df.timestamp.to_numpy(np.int64);logp=np.log(df.close.to_numpy(float));rows=[]
    for s in range(0,len(idx)-W-240,W):
        rr=idx[s:s+W]
        if rr[-1]-rr[0]!=W-1:continue
        e=rr[-1]
        if e+240>=len(df) or ts[e+240]-ts[e]!=240*60000:continue
        u=cop(F[rr]);z,i,v=u.T;hv=v>=np.quantile(v,.6);sd=(z+i)/np.sqrt(2)
        A=float(sd[hv].mean());ss=(sd[hv]-sd[hv].mean())/sd[hv].std();cint=float(np.mean(np.abs(ss)<.3)/P0)
        lo=v<=np.quantile(v,1/3);hi=v>=np.quantile(v,2/3);cone=float(z[hi].std()/z[lo].std())
        rows.append(dict(fim_ms=int(ts[e]),A=A,cintura=cint,cone=cone,**{f'r{h}':float(logp[e+h]-logp[e]) for h in H}))
    return pd.DataFrame(rows)
def judge(d):
    cond=(d.cintura<CUT_C)&(d.cone>CUT_K);c=d[cond];out={'n_janelas':len(d),'n_subconjunto':int(cond.sum())}
    hit=int(np.sum((np.sign(c.A)==np.sign(c.r60))&(c.r60!=0)));n=len(c)
    p=float(binomtest(hit,n,.5,alternative='greater').pvalue) if n else None
    out['primario']={'acertos':hit,'n':n,'acerto':hit/n if n else None,'p_unilateral':p,'significativo':bool(p is not None and p<.05)}
    for h in H:
        r=d[f'r{h}'];rc=c[f'r{h}']
        out[f'{h}min']={'todas_spearman':float(spearmanr(d.A,r)[0]),'todas_acerto':float(np.mean(np.sign(d.A)==np.sign(r))),
                        'sub_spearman':float(spearmanr(c.A,rc)[0]) if n>5 else None,'sub_acerto':float(np.mean(np.sign(c.A)==np.sign(rc))) if n else None}
    g=np.sign(c.A)*c.r60;out['economia_60min']={'ganho_medio_bruto_pct':float(100*g.mean()) if n else None,'ganho_medio_com_custo_pct':float(100*(g-COST).mean()) if n else None,'ganho_total_com_custo_pct':float(100*(g-COST).sum()) if n else None}
    return out
def gate(sha):
    t=PROTO.read_bytes();h=hashlib.sha256(t).hexdigest()
    if h!=sha or b'STATUS: CONGELADO' not in t:raise SystemExit(f'Protocolo nao confere: {h}')
    return h
def report(o,mode):
    pr=o['primario'];pct=lambda x:'—' if x is None else f'{100*x:.1f}%'
    L=[f'# H-DOM — resultado ({mode})','',f"Janelas válidas: {o['n_janelas']}; subconjunto cintura < 0,71 e cone > 1,86: **{o['n_subconjunto']}**.",'',
       f"**Primário:** acerto do sinal de A no retorno de 60 min = **{pr['acertos']}/{pr['n']} ({pct(pr['acerto'])})**, p unilateral = {pr['p_unilateral']:.3g} → **{'SIGNIFICATIVO' if pr['significativo'] else 'NÃO SIGNIFICATIVO'}**",'',
       '| Horizonte | Spearman (todas) | Acerto (todas) | Spearman (subconjunto) | Acerto (subconjunto) |','|---|---|---|---|---|']
    for h in H:
        x=o[f'{h}min'];ssp='—' if x['sub_spearman'] is None else format(x['sub_spearman'],'+.3f')
        L.append(f"| {h} min | {x['todas_spearman']:+.3f} | {pct(x['todas_acerto'])} | {ssp} | {pct(x['sub_acerto'])} |")
    e=o['economia_60min'];L+=['',f"Economia (descritiva, 60 min, subconjunto): ganho médio bruto {e['ganho_medio_bruto_pct']:+.4f}% por operação; com custo de 0,10%: {e['ganho_medio_com_custo_pct']:+.4f}% (total {e['ganho_total_com_custo_pct']:+.3f}%)."]
    return '\n'.join(L)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('ensaio','confirmatorio'),required=True);ap.add_argument('--protocol-sha')
    a=ap.parse_args();out=ROOT/'reports'/'hdom';out.mkdir(parents=True,exist_ok=True)
    if a.mode=='ensaio':
        paths=[ROOT/'data'/f'BTCUSDT-1m-{m}.zip' for m in EXPLO_MONTHS]
    else:
        sha=gate(a.protocol_sha);import baixar_klines as bk;bk.DEST.mkdir(exist_ok=True)
        for m in TEST_MONTHS:
            msg=bk.download_month('1m',m);print(msg)
            if not msg.startswith(('ok','já estava ok')):raise SystemExit('download falhou')
        paths=[ROOT/'data'/f'BTCUSDT-1m-{m}.zip' for m in TEST_MONTHS]
    d=windows(paths);o=judge(d);o['modo']=a.mode;o['meses']=[p.name for p in paths]
    if a.mode=='confirmatorio':o['protocolo_sha256']=sha
    (out/f'hdom_{a.mode}.json').write_text(json.dumps(o,indent=1,ensure_ascii=False));d.to_csv(out/f'hdom_{a.mode}_janelas.csv',index=False)
    md=report(o,a.mode);(out/f'HDOM_{a.mode.upper()}.md').write_text(md+'\n');print(md)
if __name__=='__main__':main()
