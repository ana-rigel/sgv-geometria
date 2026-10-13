"""Dicionario geometrico — analise (exploratorio). Para cada medida: R2 nos momentos (identidade),
coeficientes padronizados, correlacao com observaveis brutos, persistencia, extremos, e o que vem depois (descritivo)."""
import sys,json,numpy as np,pandas as pd;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=pd.read_csv(ROOT/'reports'/'dicionario'/'dados.csv');D=D[D.motivo.isna()].sort_values('origin_ts').reset_index(drop=True)
D['when']=pd.to_datetime(D.origin_ts,unit='ms',utc=True).dt.strftime('%d/%m %Hh')
MEAS=['trans','dlogvol','rot','m11','jacc','saddle_b','dsaddle','kmed_b','dkmed']
MOM=['dmu_z','dmu_i','dmu_n','dlsd_z','dlsd_i','dlsd_n','dcor_zi','dcor_zn','dcor_in','dkurt_z','dkurt_i','dkurt_n','waist_B','cone_B','cor_zi_B']
# para medidas de magnitude (trans) usar |dmu|
D['abs_dmu_z'],D['abs_dmu_i'],D['abs_dmu_n']=D.dmu_z.abs(),D.dmu_i.abs(),D.dmu_n.abs()
MOMX=MOM+['abs_dmu_z','abs_dmu_i','abs_dmu_n','dlogdet']
MK=['mk_lrv','mk_lvol','mk_lsd_iota','mk_lsd_lvol','mk_net_iota_B','mk_ret_B','mk_cor_ri_B']
FW=['fw_lrv6h','fw_lvol6h','fw_ret6h']
def std(x):return (x-x.mean())/x.std()
out={}
for m in MEAS:
    y=std(D[m]);Z=np.column_stack([np.ones(len(D))]+[std(D[c]) for c in MOMX]);beta,*_=np.linalg.lstsq(Z,y,rcond=None)
    r2=1-np.sum((y-Z@beta)**2)/np.sum(y*y)
    top=sorted(zip(MOMX,beta[1:]),key=lambda t:-abs(t[1]))[:4]
    cmk={c:float(np.corrcoef(D[m],D[c])[0,1]) for c in MK}
    cfw={c:float(np.corrcoef(D[m].iloc[:len(D)][D[c].notna()],D[c].dropna())[0,1]) for c in FW}
    ac={f'{3*h*2//3*0+h*2}h':float(pd.Series(D[m]).autocorr(h)) for h in (1,3,12)}   # passo de 2 h
    o=D.sort_values(m);ext=lambda q:[{'quando':r.when,'valor':round(float(r[m]),3),'vol_B/A':round(float(np.exp(r.mk_lrv)),2),
         'volume_B/A':round(float(np.exp(r.mk_lvol)),2),'dispersao_fluxo_B/A':round(float(np.exp(r.mk_lsd_iota)),2),
         'saldo_agressao_B':round(float(r.mk_net_iota_B),3),'preco_B_%':round(100*float(r.mk_ret_B),2)} for _,r in q.iterrows()]
    out[m]={'R2_momentos':float(r2),'principais_componentes':[(c,round(float(b),2)) for c,b in top],
            'corr_mercado':{k:round(v,2) for k,v in cmk.items()},'persistencia_autocorr':{k:round(v,2) for k,v in ac.items()},
            'o_que_vem_depois_descritivo':{k:round(v,2) for k,v in cfw.items()},
            'mais_baixos':ext(o.head(3)),'mais_altos':ext(o.tail(3).iloc[::-1]),
            'faixa_p5_p95':[round(float(np.quantile(D[m],.05)),3),round(float(np.quantile(D[m],.95)),3)]}
    print(f"\n### {m}: R2 nos momentos {r2:.2f} | principais {out[m]['principais_componentes']}\n mercado {out[m]['corr_mercado']}\n persist {out[m]['persistencia_autocorr']} | depois {out[m]['o_que_vem_depois_descritivo']}")
b=np.polyfit(D.dlogdet,D.dlogvol,1);out['_identidade_expansao']={'inclinacao':float(b[0]),'teoria':0.5,'corr':float(np.corrcoef(D.dlogdet,D.dlogvol)[0,1])}
(ROOT/'reports'/'dicionario'/'analise.json').write_text(json.dumps(out,indent=1,ensure_ascii=False))
