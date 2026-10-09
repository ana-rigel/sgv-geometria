import sys; sys.path.insert(0,'/home/claude/sgv-geometria'); sys.path.insert(0,'/home/claude/sgv-geometria/diagnostics')
import numpy as np, pandas as pd
from sgvgeo.l2 import evaluations, run_primary, simulate_planted
esc=sys.argv[1]
cfg={"1m":dict(W=1440,S=60,n_eval=1464,step=60_000,season="hora"),"1h":dict(W=1008,S=24,n_eval=610,step=3_600_000,season="dia")}[esc]
n=cfg["n_eval"]*cfg["S"]+cfg["W"]+2*cfg["S"]+61
lags=[2,6,12,18,24] if esc=="1m" else [2,7,14,21,30]
for lag in lags:
    ps=[];rh=[]
    for s in range(6):
        df=simulate_planted(n,seed=s,S=cfg["S"],step_ms=cfg["step"],planted=True,lag_steps=lag)
        ev=evaluations(df,cfg["W"],cfg["S"],4.0)
        r=run_primary(ev,cfg["W"],cfg["S"],cfg["season"],n_perm=299,seed=s); ps.append(r["p_unilateral"]); rh.append(r["rho_parcial"])
    # diagnóstico: v_fluxo perto das trocas
    print(esc,"lag",lag,"passos | poder(p<=.025):",np.mean(np.array(ps)<=0.025).round(2),"| rho médio:",round(np.mean(rh),3), "| ps:",np.round(ps,3).tolist(),flush=True)
