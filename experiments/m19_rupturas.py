#!/usr/bin/env python3
"""SGV-M19: do long-block (BL) alarms mark STRUCTURAL events? (confirmatory design)

Two modes:
  ensaio        engineering dry run on EXPLORATORY 1m months (windows from
                2026-06-01), with a fake event list -- validates the pipeline only.
  confirmatorio BTCUSDT 1m 2026-08 and 2026-09 (reserved). Refuses to run unless
                the frozen protocol exists, says "STATUS: CONGELADO", and its
                SHA-256 matches the value passed by the operator.

Per window (1500 min, disjoint, starting at the first minute of the period):
prefix = 5000 minutes immediately before; null = circular blocks of 500 real
prefix rows (BL, adequate on 1m in M18); 39 references; three rulers (M11,
Fisher-Rao, energy); "strong alarm" = alarm in >= 2 rulers.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments.persistencia_dependencia import checked_exploratory_month
from experiments.m3_precisao_nao_convexidade import circular_blocks
from experiments.m13_calibracao_alarmes_regimes import mc_rank,wilson
from experiments.m15_forma_persistencia_comparadores import all_stats,STATS

BASE_SEED=2026101019
PREFIX=5000
WINDOW=1500
STEP_MS=60000
REFS=39
BLOCK=500
PER_SHARD=6
PROTOCOL=ROOT/'reports'/'PROTOCOLO_SGV_M19_20261010.md'
PERIODS={'ensaio':{'start':'2026-06-01','end':'2026-08-01',
                   'months':['2026-05','2026-06','2026-07'],'dir':ROOT/'data'},
         'confirmatorio':{'start':'2026-08-01','end':'2026-10-01',
                          'months':['2026-07','2026-08','2026-09'],'dir':ROOT/'data'}}
CONFIRMATORY_MONTHS=('2026-08','2026-09')
N_WINDOWS=58


def seed_int(*parts):
    ss=np.random.SeedSequence([BASE_SEED,*[int(p) for p in parts]])
    return int(ss.generate_state(1,dtype=np.uint32)[0])%(2**31-2**25)


def protocol_gate(expected_sha):
    """The only door to the reserved months."""
    if not PROTOCOL.is_file():raise PermissionError('Protocol file missing')
    text=PROTOCOL.read_text(encoding='utf8')
    if 'STATUS: CONGELADO' not in text:raise PermissionError('Protocol is not frozen')
    sha=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if not expected_sha or sha!=expected_sha.strip().lower():
        raise PermissionError(f'Protocol hash mismatch: file {sha}')
    return sha


def archives(mode,protocol_sha=None):
    cfg=PERIODS[mode];paths=[]
    for m in cfg['months']:                      # permissions first, files after
        p=cfg['dir']/f'BTCUSDT-1m-{m}.zip'
        if m in CONFIRMATORY_MONTHS:
            if mode!='confirmatorio':raise PermissionError('Reserved month outside confirmatory mode')
            protocol_gate(protocol_sha)
        else:
            checked_exploratory_month(p.name,'1m')
        paths.append(p)
    for p in paths:
        if not p.is_file():raise FileNotFoundError(p)
    return paths


def windows(mode,protocol_sha=None):
    df=load_binance_klines(archives(mode,protocol_sha),with_flow=True)
    ts=df.timestamp.to_numpy(np.int64)
    t0=int(pd.Timestamp(PERIODS[mode]['start'],tz='UTC').value//10**6)
    t1=int(pd.Timestamp(PERIODS[mode]['end'],tz='UTC').value//10**6)
    i0=int(np.searchsorted(ts,t0))
    if i0>=len(ts) or ts[i0]!=t0:raise ValueError('Period start minute missing')
    starts=[];gaps=[]
    for k in range(N_WINDOWS):
        tk=t0+k*WINDOW*STEP_MS
        if tk+WINDOW*STEP_MS>t1:raise ValueError('Window beyond period end')
        i=int(np.searchsorted(ts,tk))
        ok=i<len(ts) and ts[i]==tk and i-PREFIX>=0 and i+WINDOW<=len(ts) and \
           np.all(np.diff(ts[i-PREFIX:i+WINDOW])==STEP_MS)
        starts.append(i if ok else None)
        if not ok:gaps.append(k)
    return df,starts,gaps


def run_window(df,i,k,refs=REFS,stats_fn=all_stats):
    pre=df.iloc[i-PREFIX:i].copy();fut=df.iloc[i:i+WINDOW].copy()
    item={'window':int(k),'start_ms':int(fut.timestamp.iloc[0]),'end_ms':int(fut.timestamp.iloc[-1])}
    actual=flow_coordinates(pd.concat([pre,fut],ignore_index=True))[['z','iota','nu']].to_numpy(float)[-WINDOW:]
    raw=flow_coordinates(pre)[['z','iota','nu']].to_numpy(float)
    raw=raw[np.isfinite(raw).all(axis=1)]
    lr=np.log(pd.concat([pre,fut]).close.to_numpy(float))
    item['vol_ratio']=float(np.diff(lr[PREFIX-1:]).std()/np.diff(lr[:PREFIX]).std())
    if not np.isfinite(actual).all() or len(raw)<2000:
        item['status']='invalid_coordinates';return item
    obs=stats_fn(actual,seed_int(k,1));item['observed']=obs
    ref={s:[] for s in STATS}
    for j in range(refs):
        rng=np.random.default_rng(seed_int(k,3,j))
        try:r=stats_fn(circular_blocks(raw,rng,BLOCK)[:WINDOW],seed_int(k,4,j))
        except (ValueError,RuntimeError,np.linalg.LinAlgError):r={s:None for s in STATS}
        for s in STATS:ref[s].append(r[s])
    item['references']=ref;item['status']='valid';item['rulers']={}
    for s in STATS:
        if obs[s] is None or any(v is None for v in ref[s]):
            item['rulers'][s]={'valid':False};continue
        p=mc_rank(obs[s],ref[s],min_reference=refs)
        item['rulers'][s]={'valid':True,'p_rank':p,'alarm':bool(p<=.05)}
    valid=[v for v in item['rulers'].values() if v['valid']]
    item['n_alarm']=int(sum(v['alarm'] for v in valid));item['n_rulers_valid']=len(valid)
    item['strong_alarm']=bool(item['n_alarm']>=2)
    return item


# ---------------------------------------------------------------- analysis
def event_windows(events,rows):
    """Window k is an event window if an event timestamp falls inside it; a
    date-only event marks every window overlapping that UTC date."""
    marked=set()
    for e in events:
        if 'utc' in e:
            t=int(pd.Timestamp(e['utc'],tz='UTC').value//10**6)
            lo=hi=t
        else:
            lo=int(pd.Timestamp(e['date'],tz='UTC').value//10**6);hi=lo+86400000-1
        for r in rows:
            if r['start_ms']<=hi and lo<=r['end_ms']+STEP_MS-1:marked.add(r['window'])
    return marked


def circular_shift_p(x,y):
    """One-sided p for mean(y|x)-mean(y|~x) using all circular shifts of x (keeps clustering)."""
    x=np.asarray(x,bool);y=np.asarray(y,float);n=len(x)
    def stat(xx):return y[xx].mean()-y[~xx].mean() if xx.any() and (~xx).any() else 0.
    obs=stat(x);null=[stat(np.roll(x,s)) for s in range(1,n)]
    return float(obs),float((1+sum(v>=obs-1e-12 for v in null))/n)


def by_group(valid,events,y):
    out={}
    for g in sorted({e.get('grupo') for e in events if e.get('grupo')}):
        ev=event_windows([e for e in events if e.get('grupo')==g],valid)
        x=np.array([r['window'] in ev for r in valid])
        if not x.any():continue
        d,p=circular_shift_p(x,y)
        out[g]={'n_event_windows':int(x.sum()),'event_rate':float(y[x].mean()),
                'nonevent_rate':float(y[~x].mean()),'rate_difference':d,'p_one_sided':p}
    return out


def analyse(rows,events):
    valid=[r for r in rows if r.get('status')=='valid']
    ev=event_windows(events,valid)
    x=np.array([r['window'] in ev for r in valid]);y=np.array([r['strong_alarm'] for r in valid])
    y1=np.array([r['n_alarm']>=1 for r in valid]);vr=np.array([r['vol_ratio'] for r in valid])
    from scipy.stats import fisher_exact
    a=int((x&y).sum());b=int((x&~y).sum());c=int((~x&y).sum());d=int((~x&~y).sum())
    diff,p_perm=circular_shift_p(x,y)
    _,p_fisher=fisher_exact([[a,b],[c,d]],alternative='greater')
    diff1,p_perm1=circular_shift_p(x,y1)
    # Mantel-Haenszel style: within vol-ratio terciles, permutation of labels inside strata
    q=np.quantile(vr,[1/3,2/3]);strata=np.digitize(vr,q)
    rng=np.random.default_rng(BASE_SEED)
    def mh(xx):
        return sum((y[(strata==s)&xx].sum()-xx[strata==s].sum()*y[strata==s].mean()) for s in range(3))
    obs_mh=mh(x);null=[]
    for _ in range(9999):
        xx=x.copy()
        for s in range(3):
            m=strata==s;xx[m]=rng.permutation(x[m])
        null.append(mh(xx))
    p_strat=float((1+sum(v>=obs_mh-1e-12 for v in null))/(1+len(null)))
    per_ruler={s:{'event_rate':float(np.mean([r['rulers'][s].get('alarm',False) for r,xi in zip(valid,x) if xi])) if x.any() else None,
                  'nonevent_rate':float(np.mean([r['rulers'][s].get('alarm',False) for r,xi in zip(valid,x) if not xi]))}
               for s in STATS}
    return {'n_windows_valid':len(valid),'n_event_windows':int(x.sum()),
            'event_windows':sorted(int(k) for k in ev if any(r['window']==k for r in valid)),
            'strong_alarm':{'event':[a,a+b],'nonevent':[c,c+d],
                            'event_rate':a/(a+b) if a+b else None,'nonevent_rate':c/(c+d) if c+d else None,
                            'event_wilson95':wilson(a,a+b),'nonevent_wilson95':wilson(c,c+d)},
            'primary_circular_shift':{'rate_difference':diff,'p_one_sided':p_perm},
            'secondary_fisher_one_sided':float(p_fisher),
            'secondary_vol_stratified_permutation':p_strat,
            'secondary_any_ruler_circular_shift':{'rate_difference':diff1,'p_one_sided':p_perm1},
            'per_ruler':per_ruler,
            'secondary_by_group':by_group(valid,events,y),
            'base_rate_strong_alarm_all_windows':float(y.mean())}


# --------------------------------------------------------------------- I/O
def out_dir(mode):
    d=ROOT/'reports'/'m19'/mode;d.mkdir(parents=True,exist_ok=True);return d


def run_shard(mode,shard,protocol_sha=None):
    df,starts,gaps=windows(mode,protocol_sha)
    ks=range(shard*PER_SHARD,min(N_WINDOWS,(shard+1)*PER_SHARD))
    rows=[]
    for k in ks:
        rows.append({'window':k,'status':'gap'} if starts[k] is None else run_window(df,starts[k],k))
    (out_dir(mode)/f'shard_{shard:02d}.json').write_text(json.dumps(
        {'status':'M19_SHARD','mode':mode,'shard':shard,'gaps':gaps,'windows':rows},indent=1)+'\n')
    print(json.dumps({'mode':mode,'shard':shard,'n':len(rows),'gaps':gaps}))


def aggregate(mode,events_path,shards_dir=None):
    d=Path(shards_dir) if shards_dir else out_dir(mode)
    n_sh=(N_WINDOWS+PER_SHARD-1)//PER_SHARD;rows=[]
    for s in range(n_sh):
        doc=json.loads((d/f'shard_{s:02d}.json').read_text())
        if doc['mode']!=mode or doc['shard']!=s:raise ValueError('bad shard')
        rows+=doc['windows']
    if sorted(r['window'] for r in rows)!=list(range(N_WINDOWS)):raise ValueError('Missing or duplicate windows')
    events=json.loads(Path(events_path).read_text(encoding='utf8'))['eventos']
    res=analyse(rows,events);res['mode']=mode;res['events_file']=str(events_path)
    res['windows']=[{k:r.get(k) for k in ('window','start_ms','end_ms','status','vol_ratio','n_alarm','strong_alarm')} for r in rows]
    (out_dir(mode)/'SGV_M19_ANALISE.json').write_text(json.dumps(res,indent=1,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in res.items() if k!='windows'},indent=1,ensure_ascii=False))
    return res


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=tuple(PERIODS),required=True)
    ap.add_argument('--stage',choices=('shard','aggregate'),required=True)
    ap.add_argument('--shard',type=int);ap.add_argument('--events');ap.add_argument('--shards-dir')
    ap.add_argument('--protocol-sha',default=None)
    a=ap.parse_args()
    if a.mode=='confirmatorio':protocol_gate(a.protocol_sha)
    if a.stage=='shard':run_shard(a.mode,a.shard,a.protocol_sha)
    else:aggregate(a.mode,a.events,a.shards_dir)


if __name__=='__main__':main()
