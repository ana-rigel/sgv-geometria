"""M35 passo 3 (plano reports/m35/PLANO_M35_PASSO3_20261015.md, congelado antes do codigo).
BTC 1m mai-jul/2026 ja gasto + sinteticos. Nenhum alvo de mercado futuro.
Separa a deformacao da casca em: forma de cada eixo (T1) x combinacao dos eixos (V_cop, copula)."""
import os,sys,json,time,hashlib,numpy as np,pandas as pd;from pathlib import Path
from multiprocessing import Pool
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scipy.stats import spearmanr,skew,kurtosis,norm
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments import m31g1_engenharia as g
from experiments import m35_instrumento as m
from experiments.precisao_formas_3d import split_historical
from experiments.m3_precisao_nao_convexidade import circular_blocks
OUT=ROOT/'reports'/'m35'/'passo3';OUT.mkdir(parents=True,exist_ok=True)
PLANO=ROOT/'reports'/'m35'/'PLANO_M35_PASSO3_20261015.md'
SEED=20261015;SCALES=(1500,3000,6000);SIZES={1500:525,3000:1050,6000:2100};REPS=8;NPICK=60;NSYN=30
f=load_binance_klines(g.EXPLO,with_flow=True);co=flow_coordinates(f)
X=co[['z','iota','nu']].to_numpy(float);ts=f.timestamp.to_numpy(np.int64)
ok=np.isfinite(X).all(1);cs=np.r_[0,np.cumsum(~ok)]
ORIG=[i for i in np.flatnonzero((ts//60000)%180==0) if i>=max(SCALES)-1 and cs[i+1]-cs[i+1-max(SCALES)]==0]
PICK=[ORIG[p] for p in np.linspace(0,len(ORIG)-1,NPICK).astype(int)]


def half_b(i,W):return split_historical(X[i-W+1:i+1])[1]


def job(arg):
    kind=arg[0]
    if kind=='real':
        _,i,W,r=arg;b=half_b(i,W);seed=SEED+int(ts[i]//60000)%100000+7*r
        if r>0:b=circular_blocks(b,np.random.default_rng(seed),15)
        out={'kind':'full' if r==0 else 'boot','origin_ts':int(ts[i]),'W':W,'rep':r}
        try:out.update(m.measure_cop(b,seed))
        except (ValueError,RuntimeError,np.linalg.LinAlgError,IndexError):pass
        out.update(m.dependence_scales(b));return out
    _,n,typ,k,s=arg;rng=np.random.default_rng(31000+1000*n+100*['marg','cone','cintura','caudas'].index(typ)+k)
    x=m.synth_marginal(n,s,rng) if typ=='marg' else m.synth_joint(n,s,rng,typ)
    out={'kind':'syn','n':n,'tipo':typ,'s':s}
    try:r=m.measure_cop(x,SEED+k);out.update({'V_cop':r['V_cop'],'V4n_B':r['V4n_B']})
    except (ValueError,RuntimeError,np.linalg.LinAlgError,IndexError):pass
    return out


def lev(u):
    hv=u[:,2]>=np.quantile(u[:,2],.6);s=u[hv,0]+u[hv,1];s=(s-s.mean())/s.std()
    lo=u[:,2]<=np.quantile(u[:,2],1/3);hi=u[:,2]>=np.quantile(u[:,2],2/3)
    return {'T3_cintura':float(np.mean(np.abs(s)<.3)/(2*norm.cdf(.3)-1)),'T3_cone':float(np.log(u[hi,0].std()/u[lo,0].std()))}


def describe(i,W):
    """T1: forma de cada eixo nos dados BRUTOS da metade B; T3: cone e cintura (gaussianizados)."""
    na=int(.3*W);half=(W-na)//2;B=slice(i-W+1+na+half,i+1);raw=X[B];d={'origin_ts':int(ts[i]),'W':W}
    for j,c in enumerate('zin'):
        x=raw[:,j];d.update({f'T1_mu_{c}':float(x.mean()),f'T1_sd_{c}':float(x.std()),f'T1_sk_{c}':float(skew(x)),f'T1_ku_{c}':float(kurtosis(x))})
    d.update(lev(half_b(i,W)));return d


def cv_r2(y,Z):
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import cross_val_score,KFold
    k=np.isfinite(y)&np.isfinite(Z).all(1);y,Z=y[k],Z[k];kf=KFold(5,shuffle=False)
    return {'n':int(len(y)),'r2_cv_linear':float(np.mean(cross_val_score(LinearRegression(),Z,y,cv=kf,scoring='r2'))),
            'r2_cv_boosting':float(np.mean(cross_val_score(HistGradientBoostingRegressor(max_iter=200,learning_rate=.05,max_depth=3,random_state=0),Z,y,cv=kf,scoring='r2')))}


def reliability(full,boot,col,B=2000,seed=0):
    """Confiabilidade (media), IC90 por reamostragem das origens, versao mediana e fracao de origens instaveis."""
    v=full[col].dropna().to_numpy();vb=boot.groupby('origin_ts')[col].var().dropna().to_numpy()
    if len(v)<3 or len(vb)<3:return None
    tot=v.var(ddof=1);rng=np.random.default_rng(seed)
    bs=[1-rng.choice(vb,len(vb)).mean()/rng.choice(v,len(v)).var(ddof=1) for _ in range(B)]
    med=np.median(vb)
    return {'confiabilidade':float(1-vb.mean()/tot),'ic90':[float(x) for x in np.percentile(bs,[5,95])],
            'confiabilidade_mediana':float(1-med/tot),'fracao_instaveis':float(np.mean(vb>10*med)),
            'var_entre':float(tot),'var_boot_media':float(vb.mean()),'falhas':float(full[col].isna().mean())}


if __name__=='__main__':
    t0=time.perf_counter();rng=np.random.default_rng(5)
    jobs=[('real',i,W,0) for W in SCALES for i in ORIG]+[('real',i,W,r) for W in SCALES for i in PICK for r in range(1,REPS+1)]
    for n in SIZES.values():
        for typ in ('marg','cone','cintura','caudas'):
            jobs+=[('syn',n,typ,k,float(s)) for k,s in enumerate(rng.uniform(0,1,NSYN))]
    print('origens',len(ORIG),'jobs',len(jobs),flush=True)
    with Pool(int(os.environ.get('N_PROC',os.cpu_count() or 2))) as pool:rows=pool.map(job,jobs,chunksize=1)
    D=pd.DataFrame(rows);D.to_csv(OUT/'medidas.csv.gz',index=False,compression='gzip');print('medicoes s',round(time.perf_counter()-t0),flush=True)
    Dsc=pd.DataFrame([describe(i,W) for W in SCALES for i in ORIG]);Dsc.to_csv(OUT/'descritores.csv.gz',index=False,compression='gzip')
    res={'plano_sha256':hashlib.sha256(PLANO.read_bytes()).hexdigest(),'n_origens':len(ORIG),'n_pick':NPICK,'reps':REPS}
    # validade sintetica
    sy=D[D.kind=='syn'];val={}
    for n,gq in sy.groupby('n'):
        rho=lambda t,c:float(spearmanr(gq[gq.tipo==t].s,gq[gq.tipo==t][c],nan_policy='omit')[0])
        v={'marg_Vcop':rho('marg','V_cop'),'marg_V4nB':rho('marg','V4n_B'),'cone_Vcop':rho('cone','V_cop'),
           'cintura_Vcop':rho('cintura','V_cop'),'caudas_Vcop':rho('caudas','V_cop'),'falhas':int(gq.V_cop.isna().sum())}
        v['invariancia_ok']=bool(abs(v['marg_Vcop'])<.3 and v['marg_V4nB']>=.7)
        v['sensibilidade_ok']=bool(v['cone_Vcop']>=.7 and v['cintura_Vcop']>=.7)
        v['V_cop_valido']=v['invariancia_ok'] and v['sensibilidade_ok'];val[int(n)]=v
    res['validade_sintetica']=val
    # confiabilidade
    mapc=[c for c in D if c[:3] in ('sC_','aC_')];conf={}
    for W in SCALES:
        fu=D[(D.kind=='full')&(D.W==W)];bo=D[(D.kind=='boot')&(D.W==W)]
        conf[W]={c:reliability(fu,bo,c) for c in ['V4n_B','V_cop']+mapc}
    res['confiabilidade']=conf
    # regra 1
    cand=[W for W in SCALES if val[SIZES[W]]['V_cop_valido'] and (conf[W]['V_cop'] or {}).get('confiabilidade',-9)>=.6]
    Wc=min(cand) if cand else None;res['regra1_escala_candidata']=Wc
    # traducao (todas as escalas, descritivo)
    T2=[c for c in D if c.startswith('T2_')];T1=[c for c in Dsc if c.startswith('T1_')];T3=[c for c in Dsc if c.startswith('T3_')]
    trad={};deco={};top={}
    for W in SCALES:
        fu=D[(D.kind=='full')&(D.W==W)].merge(Dsc[Dsc.W==W],on=['origin_ts','W']);y=fu.V_cop.to_numpy(float)
        trad[W]={nm:cv_r2(y,fu[cols].to_numpy(float)) for nm,cols in (('T1',T1),('T2',T2),('T1+T2',T1+T2),('T1+T2+T3',T1+T2+T3))}
        top[W]=sorted(((round(float(fu[['V_cop',c]].corr('spearman').iloc[0,1]),3),c) for c in T1+T2+T3),key=lambda t:-abs(t[0]))[:8]
        z=fu.V4n_B.to_numpy(float)
        deco[W]={'V4nB_por_Vcop':cv_r2(z,fu[['V_cop']].to_numpy(float)),'V4nB_por_T1':cv_r2(z,fu[T1].to_numpy(float)),
                 'V4nB_por_Vcop_T1':cv_r2(z,fu[['V_cop']+T1].to_numpy(float)),'corr_spearman_V4nB_Vcop':float(fu[['V4n_B','V_cop']].corr('spearman').iloc[0,1])}
    res['traducao_Vcop']=trad;res['Vcop_mais_ligados']=top;res['regra4_decomposicao_V4nB']=deco
    # regra 2/3: residuo de V_cop apos T2, na escala candidata
    if Wc:
        fu=D[(D.kind=='full')&(D.W==Wc)].dropna(subset=['V_cop']+T2);bo=D[(D.kind=='boot')&(D.W==Wc)].dropna(subset=['V_cop']+T2).copy()
        Z=np.column_stack([np.ones(len(fu)),fu[T2].to_numpy(float)]);beta=np.linalg.lstsq(Z,fu.V_cop.to_numpy(float),rcond=None)[0]
        fu=fu.copy();fu['res']=fu.V_cop-Z@beta;bo['res']=bo.V_cop-np.column_stack([np.ones(len(bo)),bo[T2].to_numpy(float)])@beta
        rr=reliability(fu,bo,'res');frac=float(fu.res.var()/fu.V_cop.var())
        cand2=bool(rr and rr['confiabilidade']>=.5 and frac>=.25)
        res['regra2_residuo']={**(rr or {}),'fracao_var_residuo':frac,'candidato_medida_nova':cand2,
                               'coeficientes_T2':dict(zip(['intercepto']+T2,[float(b) for b in beta]))}
    else:res['regra2_residuo']={'nao_avaliado':'nenhuma escala candidata (regra 1)'}
    res['segundos']=round(time.perf_counter()-t0)
    (OUT/'passo3.json').write_text(json.dumps(res,indent=1,ensure_ascii=False))
    print(json.dumps({k:res[k] for k in ('validade_sintetica','regra1_escala_candidata','regra2_residuo')},ensure_ascii=False)[:4000])
    print('conf V_cop',{W:(conf[W]['V_cop'] or {}).get('confiabilidade') for W in SCALES},'V4n_B',{W:(conf[W]['V4n_B'] or {}).get('confiabilidade') for W in SCALES})
    print('total s',res['segundos'])
