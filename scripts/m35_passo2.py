"""M35 passo 2 (plano reports/m35/PLANO_M35_PASSO2_20261014.md, congelado antes de medir).
BTC 1m mai-jul/2026 ja gasto + sinteticos. Nenhum alvo de mercado futuro.
Escalas W = 1500/3000/6000 min; medidas V2, V4, V4n, dV4n e mapa radial (26 direcoes) da casca branqueada."""
import os,sys,json,time,numpy as np,pandas as pd;from pathlib import Path
from multiprocessing import Pool
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scipy.stats import spearmanr,skew,kurtosis,norm,binomtest
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments import m31g1_engenharia as g
from experiments import m35_instrumento as m
from experiments.precisao_formas_3d import split_historical
from experiments.m3_precisao_nao_convexidade import circular_blocks
OUT=ROOT/'reports'/'m35'/'passo2';OUT.mkdir(parents=True,exist_ok=True)
SEED=20261014;SCALES=(1500,3000,6000);REPS=6;NPICK=30;NSYN=30;CHANCE=5/26
f=load_binance_klines(g.EXPLO,with_flow=True);co=flow_coordinates(f)
X=co[['z','iota','nu']].to_numpy(float);R=co['r'].to_numpy(float);IOTA=co['iota'].to_numpy(float)
VOL=f.volume.to_numpy(float);ts=f.timestamp.to_numpy(np.int64)
ok=np.isfinite(X).all(1);cs=np.r_[0,np.cumsum(~ok)]
ORIG=[i for i in np.flatnonzero((ts//60000)%360==0) if i>=max(SCALES)-1 and cs[i+1]-cs[i+1-max(SCALES)]==0]
PICK=[ORIG[p] for p in np.linspace(0,len(ORIG)-1,NPICK).astype(int)]


def halves(i,W):return split_historical(X[i-W+1:i+1])


def measure(a,b,seed):
    out={}
    try:out.update(m.measure(a,b,'V2',seed))
    except (ValueError,RuntimeError,np.linalg.LinAlgError,IndexError):pass
    try:out.update(m.measure_v4_map(a,b,seed))
    except (ValueError,RuntimeError,np.linalg.LinAlgError,IndexError):pass
    return out


def job(arg):
    kind=arg[0]
    if kind=='real':
        _,i,W,r=arg;a,b=halves(i,W);seed=SEED+int(ts[i]//60000)%100000+7*r
        if r>0:
            rng=np.random.default_rng(seed);a=circular_blocks(a,rng,15);b=circular_blocks(b,rng,15)
        return {'kind':'full' if r==0 else 'boot','origin_ts':int(ts[i]),'W':W,'rep':r,**measure(a,b,seed)}
    if kind=='syn_map':
        _,n,k,null=arg;rng=np.random.default_rng(9000+100*n+k+50000*null);ax=k%6
        x,e=m.planted_lobe(n,rng,ax)
        if null:x=m.whiten(rng.standard_normal((n,3)))
        _,_,an=m.radial_map(m.bagged_field(x,SEED+k))
        return {'kind':'syn_map','n':n,'k':k,'null':null,'hit':bool(m.map_hit(an,e))}
    _,n,k,sa,sb=arg;rng=np.random.default_rng(7000+100*n+k)
    a=m.planted(sa,n,rng);b=m.planted(sb,n,rng)
    return {'kind':'syn_sep','n':n,'sep_a':sa,'sep_b':sb,**measure(a,b,SEED+k)}


def lev(u):
    c=np.corrcoef(u,rowvar=False);hv=u[:,2]>=np.quantile(u[:,2],.6);s=u[hv,0]+u[hv,1];s=(s-s.mean())/s.std()
    lo=u[:,2]<=np.quantile(u[:,2],1/3);hi=u[:,2]>=np.quantile(u[:,2],2/3)
    o={'waist':float(np.mean(np.abs(s)<.3)/(2*norm.cdf(.3)-1)),'cone':float(np.log(u[hi,0].std()/u[lo,0].std())),
       'c_zi':c[0,1],'c_zn':c[0,2],'c_in':c[1,2],'logdet':float(np.linalg.slogdet(np.cov(u,rowvar=False))[1])}
    for j,k in enumerate('zin'):o.update({f'mu_{k}':u[:,j].mean(),f'lsd_{k}':np.log(u[:,j].std()),f'sk_{k}':skew(u[:,j]),f'ku_{k}':kurtosis(u[:,j])})
    return {k:float(v) for k,v in o.items()}


def describe(i,W):
    """Momentos da metade B gaussianizada e observaveis BRUTOS da mesma metade (descritivo)."""
    a,b=halves(i,W);na=int(.3*W);half=(W-na)//2;B=slice(i-W+1+na+half,i+1)
    d={'origin_ts':int(ts[i]),'W':W,**{'M_'+k:v for k,v in lev(b).items()}}
    r,io,v=R[B],IOTA[B],VOL[B]
    d.update({'mk_lrv':float(np.log((r**2).sum()/len(r))),'mk_lvol':float(np.log(v.mean())),'mk_net_iota':float(io.mean()),
              'mk_sd_iota':float(io.std()),'mk_cor_ri':float(np.corrcoef(r,io)[0,1]),'mk_skew_r':float(skew(r)),
              'mk_kurt_r':float(kurtosis(r)),'mk_lsd_lvol':float(np.log(v).std())})
    return d


def cv_r2(y,Z):
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import cross_val_score,KFold
    k=np.isfinite(y)&np.isfinite(Z).all(1);y,Z=y[k],Z[k];kf=KFold(5,shuffle=False)
    return {'n':int(len(y)),'r2_cv_linear':float(np.mean(cross_val_score(LinearRegression(),Z,y,cv=kf,scoring='r2'))),
            'r2_cv_boosting':float(np.mean(cross_val_score(HistGradientBoostingRegressor(max_iter=200,learning_rate=.05,max_depth=3,random_state=0),Z,y,cv=kf,scoring='r2')))}


if __name__=='__main__':
    t0=time.perf_counter();rng=np.random.default_rng(3)
    jobs=[('real',i,W,0) for W in SCALES for i in ORIG]+[('real',i,W,r) for W in SCALES for i in PICK for r in range(1,REPS+1)]
    for n in (525,1050,2100):
        jobs+=[('syn_map',n,k,nl) for k in range(NSYN) for nl in (0,1)]
        jobs+=[('syn_sep',n,k,float(a),float(b)) for k,(a,b) in enumerate(rng.uniform(0,3,(30,2)))]
        jobs+=[('syn_sep',n,100+k,float(s),float(s)) for k,s in enumerate(rng.uniform(0,3,10))]
    print('origens',len(ORIG),'jobs',len(jobs),flush=True)
    with Pool(int(os.environ.get('N_PROC',os.cpu_count() or 2))) as pool:rows=pool.map(job,jobs,chunksize=1)
    D=pd.DataFrame(rows);D.to_csv(OUT/'medidas.csv.gz',index=False,compression='gzip');print('medicoes s',round(time.perf_counter()-t0),flush=True)
    Dsc=pd.DataFrame([describe(i,W) for W in SCALES for i in ORIG]);Dsc.to_csv(OUT/'descritores.csv.gz',index=False,compression='gzip')
    res={'plano_sha256':__import__('hashlib').sha256((ROOT/'reports'/'m35'/'PLANO_M35_PASSO2_20261014.md').read_bytes()).hexdigest(),
         'n_origens':len(ORIG),'n_pick':NPICK,'reps':REPS}
    # validade sintetica
    sm=D[D.kind=='syn_map'];vm={}
    for n,gq in sm.groupby('n'):
        h=gq[gq.null==0].hit;h0=gq[gq.null==1].hit
        vm[int(n)]={'acerto_lobulo':float(h.mean()),'acerto_nulo':float(h0.mean()),'acaso':CHANCE,
                    'p_nulo_acima_do_acaso':float(binomtest(int(h0.sum()),len(h0),CHANCE,alternative='greater').pvalue),
                    'mapa_valido':bool(h.mean()>=.8 and binomtest(int(h0.sum()),len(h0),CHANCE,alternative='greater').pvalue>=.05)}
    res['validade_mapa']=vm
    ss=D[D.kind=='syn_sep'].copy();vs={}
    for n,gq in ss.groupby('n'):
        ch=gq[gq.sep_a!=gq.sep_b];fl=gq[gq.sep_a==gq.sep_b];vs[int(n)]={}
        for c in ('V2','V4'):vs[int(n)][c]=float(spearmanr((ch.sep_b-ch.sep_a).abs(),ch[c],nan_policy='omit')[0])
        vs[int(n)]['dV4n']=float(spearmanr(ch.sep_b-ch.sep_a,ch.dV4n,nan_policy='omit')[0])
        vs[int(n)]['V4n_B']=float(spearmanr(gq.sep_b,gq.V4n_B,nan_policy='omit')[0])
    res['validade_separacao']=vs
    # confiabilidade por escala
    comps=['V2','V4','V4n_B','dV4n']+[f'{p}B_{a}' for p in ('s','a') for a in m.AXIS_NAMES]
    conf={}
    for W in SCALES:
        fu=D[(D.kind=='full')&(D.W==W)];bo=D[(D.kind=='boot')&(D.W==W)];conf[W]={}
        for c in comps:
            tot=float(fu[c].var());vb=float(bo.groupby('origin_ts')[c].var().mean())
            conf[W][c]={'var_entre':tot,'var_boot':vb,'confiabilidade':float(1-vb/tot) if tot>0 else None,'falhas':float(fu[c].isna().mean())}
    res['confiabilidade']=conf
    # regra 1: escala
    ok_sc=[W for W in SCALES if (conf[W]['V4n_B']['confiabilidade'] or -9)>=.6]
    Wc=min(ok_sc) if ok_sc else None;Wd=Wc or max(SCALES)
    nmap={1500:525,3000:1050,6000:2100}[Wd]
    res['regra1_escala_escolhida']=Wc;res['escala_usada_nas_regras_2_3']=Wd
    # regra 2: descritores localizados aceitos
    mapa_ok=vm[nmap]['mapa_valido']
    acc=[c for c in comps[4:] if mapa_ok and (conf[Wd][c]['confiabilidade'] or -9)>=.6]
    res['regra2_mapa_valido_no_tamanho']=mapa_ok;res['regra2_aceitos']=acc
    # regra 3: identidade e mercado (para aceitos; descritivo para todos, marcado)
    fu=D[(D.kind=='full')&(D.W==Wd)].merge(Dsc[Dsc.W==Wd],on=['origin_ts','W'])
    Mc=[c for c in Dsc if c.startswith('M_')];mk=[c for c in Dsc if c.startswith('mk_')]
    ident={};merc={}
    for c in ['V4n_B']+comps[4:]:
        ident[c]={**cv_r2(fu[c].to_numpy(float),fu[Mc].to_numpy(float)),'aceito':c in acc}
        merc[c]={k:round(float(fu[[c,k]].corr('spearman').iloc[0,1]),3) for k in mk+Mc}
    res['regra3_identidade']=ident;res['regra3_correlacoes_descritivas']=merc
    res['segundos']=round(time.perf_counter()-t0)
    (OUT/'passo2.json').write_text(json.dumps(res,indent=1,ensure_ascii=False))
    print(json.dumps({k:res[k] for k in ('validade_mapa','validade_separacao','regra1_escala_escolhida','regra2_mapa_valido_no_tamanho','regra2_aceitos')},ensure_ascii=False))
    print('conf V4n_B',{W:round(conf[W]['V4n_B']['confiabilidade'],3) for W in SCALES},'V2',{W:round(conf[W]['V2']['confiabilidade'],3) for W in SCALES},'V4',{W:round(conf[W]['V4']['confiabilidade'],3) for W in SCALES})
    print('total s',res['segundos'])
