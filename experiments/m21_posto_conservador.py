#!/usr/bin/env python3
"""SGV-M21a: conservative Monte Carlo rank when some references fail.

Problem (diagnosed 11/10/2026): the M11 shell fails ("open_mesh",
"insufficient_coverage") when >~10% of a half-window falls outside the range
of the 30% anchor used for gaussianization -- those points pile up at the
extreme normal score and the GMM2 grows a degenerate component. Under the
long-block null (BL) this hits ~3% of references, and the old rule ("one
failed reference invalidates the cell") discarded ~1/3 of M11 cells.

Rule (does NOT change the instrument): a failed reference counts as being
at least as extreme as the observed value,
    p_cons = (1 + #(valid refs >= obs) + #failed) / (R + 1),
which is stochastically >= the oracle rank -> still a valid, conservative test.
An observed value that fails stays invalid (no imputation).
"""
from __future__ import annotations
import json,glob,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))


def conservative_rank(obs,refs):
    if obs is None or not np.isfinite(obs):return None
    vals=list(refs);R=len(vals)
    if R==0:return None
    fail=sum(v is None or not np.isfinite(v) for v in vals)
    ge=sum(1 for v in vals if v is not None and np.isfinite(v) and v>=obs)
    return float((1+ge+fail)/(R+1))


def wilson(k,n,z=1.959963984540054):
    if n<1:return None
    p=k/n;d=1+z*z/n;m=(p+z*z/(2*n))/d;r=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0.,m-r),min(1.,m+r)]


def m18_bl():
    rows=[]
    for f in sorted(glob.glob(str(ROOT/'reports/m18/shards/shard_1m_*.json'))):rows+=json.load(open(f))['origins']
    out={}
    for s in ('m11','fr_cov','energy'):
        old=[r['models']['BL'][s] for r in rows if r.get('status')=='valid']
        old_valid=[o for o in old if o.get('valid')]
        new=[conservative_rank(r['observed'][s],r['models']['BL']['references'][s]) for r in rows if r.get('status')=='valid']
        nv=[p for p in new if p is not None];al=sum(p<=.05 for p in nv)
        out[s]={'old_rule_valid':len(old_valid),'old_rule_alarms':int(sum(o['alarm'] for o in old_valid)),
                'conservative_valid':len(nv),'conservative_alarms':int(al),
                'conservative_rate':al/len(nv) if nv else None,'wilson95':wilson(al,len(nv))}
    return out


def m19_sensitivity():
    rows=[]
    for f in sorted(glob.glob(str(ROOT/'reports/m19/confirmatorio/shard_*.json'))):rows+=json.load(open(f))['windows']
    ana=json.load(open(ROOT/'reports/m19/confirmatorio/SGV_M19_ANALISE.json'))
    ev=set(ana['event_windows'])
    res=[]
    for r in rows:
        if r.get('status')!='valid':continue
        ps={s:conservative_rank(r['observed'][s],r['references'][s]) for s in ('m11','fr_cov','energy')}
        al={s:(p is not None and p<=.05) for s,p in ps.items()}
        res.append({'window':r['window'],'event':r['window'] in ev,'m11_valid':ps['m11'] is not None,
                    'alarms':al,'strong':sum(al.values())>=2})
    def rate(sel):
        sel=list(sel);return [sum(x['strong'] for x in sel),len(sel)]
    return {'m11_valid_windows':sum(x['m11_valid'] for x in res),
            'm11_alarms':{'event':sum(x['alarms']['m11'] for x in res if x['event']),
                          'nonevent':sum(x['alarms']['m11'] for x in res if not x['event'])},
            'strong_alarm':{'event':rate(x for x in res if x['event']),'nonevent':rate(x for x in res if not x['event'])},
            'note':'POST HOC sensitivity only. The confirmatory verdict of M19 stays as frozen (H-RUP not supported).'}


if __name__=='__main__':
    out={'m18_BL_1m':m18_bl(),'m19_sensitivity':m19_sensitivity()}
    (ROOT/'reports/m21/SGV_M21a_posto_conservador.json').write_text(json.dumps(out,indent=1,ensure_ascii=False)+'\n')
    print(json.dumps(out,indent=1,ensure_ascii=False))
