"""M35 passo 1 (plano reports/m35/PLANO_M35_PASSO1_20261013.md). BTC 1m mai-jul/2026 ja gasto + sinteticos.
Nenhum alvo de mercado futuro. Mede: validade sintetica, ruido algoritmico, confiabilidade, identidade (momentos)."""
import os,sys,json,time,numpy as np,pandas as pd;from pathlib import Path
from multiprocessing import Pool
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scipy.stats import spearmanr,skew,kurtosis,norm
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments import m31g1_engenharia as g
from experiments import m35_instrumento as m
from experiments.precisao_formas_3d import split_historical
from experiments.m3_precisao_nao_convexidade import circular_blocks
OUT=ROOT/'reports'/'m35';OUT.mkdir(parents=True,exist_ok=True)
SEED=20261013;W=1500;REPS=8
f=load_binance_klines(g.EXPLO,with_flow=True);X=flow_coordinates(f)[['z','iota','nu']].to_numpy(float)
ts=f.timestamp.to_numpy(np.int64);pos={int(t):k for k,t in enumerate(ts)}
S=pd.read_csv(ROOT/'reports'/'m34'/'amostra_features.csv')        # mesmas origens do M34 (uma a cada 2 h)
sub=[pos[int(t)] for t in S.origin_ts]
FULL=sub[::3];PICK=[sub[p] for p in np.linspace(0,len(sub)-1,40).astype(int)]   # PICK = origens da confiabilidade do M34


def halves(i):return split_historical(X[i-W+1:i+1])


def job(arg):
    kind,i,r=arg
    if kind=='synth':
        sa,sb,seed=i;rng=np.random.default_rng(seed);a=m.planted(sa,525,rng);b=m.planted(sb,525,rng)
        return {'kind':kind,'sep_a':sa,'sep_b':sb,**m.measure_all(a,b,seed)}
    a,b=halves(i)
    if kind=='full':return {'kind':kind,'origin_ts':int(ts[i]),**m.measure_all(a,b,SEED)}
    if kind=='alg':return {'kind':kind,'origin_ts':int(ts[i]),'rep':r,**m.measure_all(a,b,SEED+100*r)}
    rng=np.random.default_rng(1000*int(i%100000)+r)
    return {'kind':kind,'origin_ts':int(ts[i]),'rep':r,**m.measure_all(circular_blocks(a,rng,15),circular_blocks(b,rng,15),SEED+100*r)}


def moments(i):
    a,b=halves(i);d={}
    def lev(u,p):
        c=np.corrcoef(u,rowvar=False);hv=u[:,2]>=np.quantile(u[:,2],.6);s=u[hv,0]+u[hv,1];s=(s-s.mean())/s.std()
        lo=u[:,2]<=np.quantile(u[:,2],1/3);hi=u[:,2]>=np.quantile(u[:,2],2/3)
        o={f'{p}waist':float(np.mean(np.abs(s)<.3)/(2*norm.cdf(.3)-1)),f'{p}cone':float(np.log(u[hi,0].std()/u[lo,0].std())),
           f'{p}c_zi':c[0,1],f'{p}c_zn':c[0,2],f'{p}c_in':c[1,2],f'{p}logdet':float(np.linalg.slogdet(np.cov(u,rowvar=False))[1])}
        for j,k in enumerate('zin'):o.update({f'{p}mu_{k}':u[:,j].mean(),f'{p}lsd_{k}':np.log(u[:,j].std()),f'{p}sk_{k}':skew(u[:,j]),f'{p}ku_{k}':kurtosis(u[:,j])})
        return o
    A,B=lev(a,''),lev(b,'')
    d.update({'B_'+k:float(v) for k,v in B.items()})
    for k in A:d['d_'+k]=float(B[k]-A[k]);d['ad_'+k]=abs(float(B[k]-A[k]))
    d['origin_ts']=int(ts[i]);return d


def r2_tables(y,Z):
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import cross_val_score,KFold
    ok=np.isfinite(y)&np.isfinite(Z).all(1);y,Z=y[ok],Z[ok];n,p=Z.shape
    lr=LinearRegression().fit(Z,y);r2=float(lr.score(Z,y));adj=float(1-(1-r2)*(n-1)/(n-p-1))
    kf=KFold(5,shuffle=False)    # blocos contiguos no tempo
    cvl=float(np.mean(cross_val_score(LinearRegression(),Z,y,cv=kf,scoring='r2')))
    cvg=float(np.mean(cross_val_score(HistGradientBoostingRegressor(max_iter=200,learning_rate=.05,max_depth=3,random_state=0),Z,y,cv=kf,scoring='r2')))
    return {'n':int(n),'p':int(p),'r2':r2,'r2_ajustado':adj,'r2_cv_linear':cvl,'r2_cv_boosting':cvg}


if __name__=='__main__':
    t0=time.perf_counter();rng=np.random.default_rng(7)
    syn=[(float(a),float(b),9000+k) for k,(a,b) in enumerate(rng.uniform(0,3,(40,2)))]
    syn+=[(float(s),float(s),9500+k) for k,s in enumerate(rng.uniform(0,3,20))]      # pisos: mesma distribuicao
    jobs=[('synth',s,0) for s in syn]+[('full',i,0) for i in FULL]+[(k,i,r) for i in PICK for k in ('alg','boot') for r in range(REPS)]
    with Pool(int(os.environ.get("N_PROC",os.cpu_count() or 2))) as pool:rows=pool.map(job,jobs,chunksize=2)
    R=pd.DataFrame(rows);R.to_csv(OUT/'medidas.csv.gz',index=False,compression='gzip')
    print('medicoes',len(R),'s',round(time.perf_counter()-t0),flush=True)
    M=pd.DataFrame([moments(i) for i in FULL]);M.to_csv(OUT/'momentos.csv.gz',index=False,compression='gzip')
    cols=['V0','V1','V2','V3','V4','dV4n','V4n_B']
    res={'n_full':len(FULL),'n_pick':len(PICK),'reps':REPS}
    # validade sintetica
    sy=R[R.kind=='synth'].copy();sy['dsep']=(sy.sep_b-sy.sep_a).abs();ch=sy[sy.sep_a!=sy.sep_b];fl=sy[sy.sep_a==sy.sep_b]
    val={}
    for c in cols:
        if c=='V4n_B':rho=spearmanr(sy.sep_b,sy[c],nan_policy='omit')[0]
        elif c=='dV4n':rho=spearmanr(ch.sep_b-ch.sep_a,ch[c],nan_policy='omit')[0]
        else:rho=spearmanr(ch.dsep,ch[c],nan_policy='omit')[0]
        big=ch[ch.dsep>=1.5][c] if c not in('V4n_B','dV4n') else None
        val[c]={'spearman':float(rho),'falhas':int(sy[c].isna().sum()),'piso_media':float(fl[c].mean()),'piso_dp':float(fl[c].std()),
                'mediana_dsep_ge_1_5':None if big is None else float(big.median())}
    res['validade_sintetica']=val
    # ruido e confiabilidade
    fu=R[R.kind=='full'].set_index('origin_ts');conf={}
    for c in cols:
        tot=float(fu[c].var());va=R[R.kind=='alg'].groupby('origin_ts')[c].var();vb=R[R.kind=='boot'].groupby('origin_ts')[c].var()
        conf[c]={'var_entre_origens':tot,'var_algoritmo':float(va.mean()),'var_bootstrap':float(vb.mean()),
                 'confiab_so_algoritmo':float(1-va.mean()/tot),'confiabilidade':float(1-vb.mean()/tot),
                 'fracao_ruido_que_e_algoritmo':float(va.mean()/vb.mean()),'falhas_full':float(fu[c].isna().mean())}
    res['confiabilidade']=conf
    # identidade: momentos
    D=fu.reset_index().merge(M,on='origin_ts')
    chg=[c for c in M if c.startswith(('d_','ad_'))];lev=[c for c in M if c.startswith('B_')]
    res['identidade']={c:r2_tables(D[c].to_numpy(float),D[lev if c=='V4n_B' else chg].to_numpy(float)) for c in cols}
    res['corr_com_V0']={c:float(D[[c,'V0']].corr(method='spearman').iloc[0,1]) for c in cols}
    S2=S[['origin_ts','m11']].merge(D[['origin_ts']+cols],on='origin_ts')
    res['corr_com_m11_do_M34']={c:float(S2[[c,'m11']].corr(method='spearman').iloc[0,1]) for c in cols}
    # observaveis de mercado (descritivo)
    dic=pd.read_csv(ROOT/'reports'/'dicionario'/'dados.csv');mk=[c for c in dic if c.startswith('mk_')]
    E=D[['origin_ts']+cols].merge(dic[['origin_ts']+mk],on='origin_ts')
    res['corr_spearman_mercado']={c:{k:round(float(E[[c,k]].corr(method='spearman').iloc[0,1]),3) for k in mk} for c in cols}
    top={c:sorted(((abs(float(D[[c,k]].corr(method='spearman').iloc[0,1])),k) for k in (lev if c=='V4n_B' else chg)),reverse=True)[:5] for c in cols}
    res['momentos_mais_ligados']={c:[(k,round(v,3)) for v,k in t] for c,t in top.items()}
    (OUT/'passo1.json').write_text(json.dumps(res,indent=1,ensure_ascii=False))
    for k in ('validade_sintetica','confiabilidade','identidade','corr_com_V0','momentos_mais_ligados'):print(k,json.dumps(res[k],ensure_ascii=False),flush=True)
    print('total s',round(time.perf_counter()-t0))
