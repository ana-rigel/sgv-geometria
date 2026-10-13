"""Auditoria do M11-I (ZIP) em BTC 1m mai-jul/2026 ja gasto: fidelidade e ruido. Nenhum alvo de mercado."""
import sys,json,time,numpy as np,pandas as pd
from multiprocessing import Pool
REPO='/home/claude/sgv-geometria';ZIP=sys.argv[1];OUT=sys.argv[2]
sys.path.insert(0,REPO);sys.path.insert(0,ZIP)
from sgv_m11i import instrument as Z
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
from experiments import m31g1_engenharia as g
from experiments.precisao_formas_3d import split_historical
from experiments.m11_distancia_superficie_nulos import measure_samples
from experiments.m2_nao_convexidade_tensao import morphology
from experiments.m3_precisao_nao_convexidade import circular_blocks
f=load_binance_klines(g.EXPLO,with_flow=True);co=flow_coordinates(f);X=co[['z','iota','nu']].to_numpy(float)
ts=f.timestamp.to_numpy(np.int64);pos={int(t):k for k,t in enumerate(ts)}
S=pd.read_csv(f'{REPO}/reports/m34/amostra_features.csv');sub=[pos[int(t)] for t in S.origin_ts]
PICK=[sub[p] for p in np.linspace(0,len(sub)-1,20).astype(int)];FULL=sub[::18]
SEED=20261013


def zsig(a,b,seed):
    try:
        A=Z.build_shell(a,seed);B=Z.build_shell(b,seed+1);s=Z.signature(A,B,seed+2)
        return s.get('distance_512'),s.get('theta_deg'),s.get('D_B'),s.get('registration_method')
    except (ValueError,RuntimeError,np.linalg.LinAlgError):return None,None,None,None


def orig(a,b,seed):
    d=measure_samples(a,b,seed);return d['distance_512'] if d.get('valid') else None


def job(arg):
    kind,i,r=arg;a,b=split_historical(X[i-1499:i+1])
    if kind=='boot':
        rng=np.random.default_rng(1000*int(i%100000)+r);a=circular_blocks(a,rng,15);b=circular_blocks(b,rng,15)
    seed=SEED+100*r
    zd,th,db,meth=zsig(a,b,seed)
    out={'kind':kind,'i':int(i),'rep':r,'m11i':zd,'theta':th,'D_B':db,'metodo':meth,'m11':orig(a,b,seed)}
    if kind=='full' and r==0:
        mo=morphology(b,seed=seed+1);out['D_B_m2']=mo.get('negative_intensity')
    return out


if __name__=='__main__':
    t0=time.perf_counter();res={}
    # fidelidade 1: split/gaussianizacao
    dif=[]
    for i in PICK:
        w=X[i-1499:i+1];a,b=split_historical(w);a2,b2=Z.split_historical(w);dif.append(max(np.abs(a-a2).max(),np.abs(b-b2).max()))
    res['split_max_abs_diff']=float(max(dif))
    # fidelidade 2: coordenadas de fluxo num trecho continuo
    seg=f.iloc[200000:206000].reset_index(drop=True)
    gap=np.diff(seg.timestamp.to_numpy(np.int64));res['trecho_continuo']=bool((gap==60000).all())
    try:
        xz=Z.flow_coordinates(seg);xo=flow_coordinates(seg)[['z','iota','nu']].to_numpy(float)
        ok=np.isfinite(xz).all(1)&np.isfinite(xo).all(1);res['flow_max_abs_diff']=float(np.abs(xz[ok]-xo[ok]).max());res['flow_nan_iguais']=bool((np.isfinite(xz)==np.isfinite(xo)).all())
    except ValueError as e:res['flow_erro']=str(e)
    try:Z.flow_coordinates(f.iloc[:200000]);res['csv_com_lacunas']='aceito'
    except ValueError as e:res['csv_com_lacunas']='rejeitado: '+str(e)
    res['lacunas_no_periodo']=int((np.diff(ts)!=60000).sum())
    jobs=[('full',i,0) for i in FULL]+[(k,i,r) for i in PICK for k in ('alg','boot') for r in range(4)]
    with Pool(2) as p:rows=p.map(job,jobs,chunksize=1)
    R=pd.DataFrame(rows);R.to_csv(f'{OUT}/audit_rows.csv',index=False)
    fu=R[R.kind=='full']
    res['n_full']=len(fu);res['falhas_m11i']=float(fu.m11i.isna().mean());res['theta_identificavel']=float(fu.theta.notna().mean())
    res['metodo_registro']=fu.metodo.value_counts().to_dict()
    v=fu.dropna(subset=['m11i','m11'])
    res['m11i_vs_m11']={'spearman':float(v[['m11i','m11']].corr('spearman').iloc[0,1]),'media_m11i':float(v.m11i.mean()),'media_m11':float(v.m11.mean()),
                        'fracao_m11i_menor_ou_igual':float((v.m11i<=v.m11+1e-12).mean())}
    w=fu.dropna(subset=['D_B','D_B_m2']);res['D_vs_m2']={'n':len(w),'max_abs_diff':float((w.D_B-w.D_B_m2).abs().max()) if len(w) else None,'frac_D_zero':float((fu.D_B==0).mean())}
    conf={}
    for c in ('m11i','m11'):
        tot=float(fu[c].var());va=R[R.kind=='alg'].groupby('i')[c].var().mean();vb=R[R.kind=='boot'].groupby('i')[c].var().mean()
        conf[c]={'var_entre':tot,'var_semente':float(va),'var_boot':float(vb),'confiab':float(1-vb/tot),'confiab_so_semente':float(1-va/tot),'parte_do_ruido_que_e_semente':float(va/vb)}
    res['ruido']=conf;res['segundos']=round(time.perf_counter()-t0)
    json.dump(res,open(f'{OUT}/audit_m11i.json','w'),indent=1,ensure_ascii=False);print(json.dumps(res,indent=1,ensure_ascii=False))
