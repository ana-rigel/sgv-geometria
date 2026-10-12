"""Controle: mesma contagem de furos/componentes em amostras GAUSSIANAS (sem furo por construcao),
mesmo n e mesma covariancia de cada metade real. Se os furos aparecem igual, sao ruido de amostra."""
import sys,json,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scipy.stats import gaussian_kde
from forma_isosuperficie import windows
from experiments import isosuperficies_morfometria as iso
from experiments.precisao_formas_3d import split_historical
N=49;pts,dx=iso.make_grid(N);rng=np.random.default_rng(7);out={}
for interval in ('1m','1h'):
    tally={}
    for _,_,xx in windows(interval):
        for half in split_historical(xx):
            g=rng.multivariate_normal(half.mean(0),np.cov(half,rowvar=False),size=len(half))
            for bw in (.7,.5):
                k=gaussian_kde(g.T);k.set_bandwidth(k.factor*bw)
                field=k(pts.T).reshape(N,N,N);th,_=iso.hdr_thresholds(field,dx)
                for a in iso.LEVELS:
                    mesh,trunc=iso.extract_mesh(field,th[a]['tau'],dx);t=iso.mesh_topology(np.asarray(mesh.vertices),np.asarray(mesh.faces))
                    key=f'banda x{bw} HDR{int(a*100)}';r=tally.setdefault(key,{'n':0,'comp':0,'furo':0})
                    if t['closed_edges'] and not trunc:
                        r['n']+=1;r['comp']+=int(t['n_components']>1);r['furo']+=int(any(x and x>=1 for x in t['genus_components']))
    out[interval]=tally;print('== controle gaussiano',interval)
    for key,r in tally.items():print(f"  {key:18s} fechadas {r['n']:2d} | >1 componente {r['comp']:2d} | com furo {r['furo']:2d}")
(ROOT/'reports'/'forma'/'toro_controle_gaussiano.json').write_text(json.dumps(out,indent=1))
