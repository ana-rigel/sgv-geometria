import sys; sys.path.insert(0,'/home/claude/sgv-geometria')
import numpy as np, pandas as pd
from sgvgeo.l2 import build_rows, fit_local, fisher_rao_speed, simulate_planted, partial_spearman_test, _rv
def evals(df,W,S,B,H,nu=4.0):
    rows=build_rows(df); n=len(rows.r); out=[]
    for t in range(W+2*H+61, n-H+1, S):
        ia=np.arange(t-W,t-B); ib=np.arange(t-B,t)
        A,Bf=fit_local(rows,ia,nu),fit_local(rows,ib,nu)
        v=fisher_rao_speed(A,Bf,nu)
        rvp=_rv(rows.r,t-H,t)
        out.append({"t":t,"timestamp":int(rows.ts[t-1]),**v,"log_rv_S":np.log(_rv(rows.r,t-S,t)),"log_rv_W":np.log(_rv(rows.r,t-W,t)),
                    "abs_dlog_rv_recente":abs(np.log(_rv(rows.r,t-S,t)/_rv(rows.r,t-2*S,t-S))),"Y":abs(np.log(_rv(rows.r,t,t+H)/rvp))})
    ev=pd.DataFrame(out); ev["abs_dlog_sigma"]=ev.dlog_sigma.abs(); return ev
W,S=1440,60; n=1464*S+W+2*S+61
for B,H in [(180,360),(240,240),(360,360)]:
  for planted in (False,True):
    ps=[]
    for s in range(5):
        df=simulate_planted(n,seed=s,S=S,planted=planted,lag_steps=2)
        ev=evals(df,W,S,B,H)
        r=partial_spearman_test(ev,"v_fluxo","Y",["log_rv_S","log_rv_W","abs_dlog_rv_recente","abs_dlog_sigma"],"hora",min_shift=W//S,n_perm=299,seed=s)
        ps.append(round(r["p_unilateral"],3))
    print("B",B,"H",H,"plantado" if planted else "estacion.", "frac p<=.025:",np.mean(np.array(ps)<=0.025),ps,flush=True)
