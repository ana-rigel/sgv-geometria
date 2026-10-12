"""A casca pode ser um toro? Topologia (componentes, genero) das HDR 25/50/75 com
densidade LIVRE (KDE gaussiano, banda Scott x1, x0,7, x0,5), nas 6 janelas por escala,
metades A e B. Descritivo."""
import sys,json,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scipy.stats import gaussian_kde
from forma_isosuperficie import windows
from experiments import isosuperficies_morfometria as iso
from experiments.precisao_formas_3d import split_historical
N=49;pts,dx=iso.make_grid(N);out={}
for interval in ('1m','1h'):
    tally={}
    for _,_,xx in windows(interval):
        for half in split_historical(xx):
            for bw in (1.,.7,.5):
                k=gaussian_kde(half.T);k.set_bandwidth(k.factor*bw)
                field=k(pts.T).reshape(N,N,N);th,_=iso.hdr_thresholds(field,dx)
                for a in iso.LEVELS:
                    mesh,trunc=iso.extract_mesh(field,th[a]['tau'],dx);t=iso.mesh_topology(np.asarray(mesh.vertices),np.asarray(mesh.faces))
                    key=f'banda x{bw} HDR{int(a*100)}'
                    g=t['genus_components'] if t['closed_edges'] and not trunc else None
                    rec=tally.setdefault(key,{'n':0,'fechadas':0,'componentes>1':0,'genero>=1':0,'generos':[]})
                    rec['n']+=1
                    if g is not None:
                        rec['fechadas']+=1;rec['componentes>1']+=int(t['n_components']>1);rec['genero>=1']+=int(any(x and x>=1 for x in g));rec['generos'].append(g)
    out[interval]=tally
    print('==',interval)
    for key,r in tally.items():print(f"  {key:18s} superficies {r['n']:2d} fechadas {r['fechadas']:2d} | >1 componente {r['componentes>1']:2d} | com furo (genero>=1) {r['genero>=1']:2d}")
(ROOT/'reports'/'forma'/'toro_topologia_kde.json').write_text(json.dumps(out,indent=1))
