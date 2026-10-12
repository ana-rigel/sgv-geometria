"""Animacao da casca HDR50 (KDE, copula local) em janelas moveis de 6 h, passo 1 h, num trecho de 5 dias
do 1m exploratorio (escolhido por ter episodios claros de cintura e de abertura do cone). Descritivo."""
import sys,json,numpy as np,pandas as pd;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import LinearSegmentedColormap,TwoSlopeNorm
from scipy.stats import rankdata,norm,gaussian_kde
from skimage.measure import marching_cubes
from sgvgeo.data import load_binance_klines
from sgvgeo.flow import flow_coordinates
W,STEP,START,L,N,EXT=360,60,1991,120,33,3.0
SURF='#fcfcfb';INK='#0b0b0b';INK2='#52514e';BLUE='#2a78d6';RED='#e34948';GRAY='#d9d8d3'
cmap=LinearSegmentedColormap.from_list('cv',[RED,'#f2b9b8','#e9e8e4','#bcd3f0',BLUE])
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':INK2,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF})
df=load_binance_klines(sorted((ROOT/'data').glob('BTCUSDT-1m-*.zip')),with_flow=True)
F=flow_coordinates(df)[['z','iota','nu']].to_numpy(float);ok=np.isfinite(F).all(1);X=F[ok];TS=df.timestamp.to_numpy(np.int64)[ok]
series=np.load(ROOT/'reports'/'forma'/'movimento_series.npy');res=json.loads((ROOT/'reports'/'forma'/'movimento_forma.json').read_text())
def cop(x):return norm.ppf(np.column_stack([rankdata(x[:,j])/(len(x)+1) for j in range(3)]))
ax1=np.linspace(-EXT,EXT,N);G=np.stack(np.meshgrid(ax1,ax1,ax1,indexing='ij'),-1).reshape(-1,3);sp=ax1[1]-ax1[0]
light=np.array([.4,-.6,.7]);light/=np.linalg.norm(light)
def shell(u):
    f=gaussian_kde(u.T)(G.T).reshape(N,N,N);o=np.sort(f.ravel())[::-1];c=np.cumsum(o)/o.sum();tau=o[np.searchsorted(c,.5)]
    v,fa,_,_=marching_cubes(f,tau,spacing=(sp,sp,sp));return v-EXT,fa
def faces_colors(v,fa):
    tri=v[fa];nrm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nrm/=np.linalg.norm(nrm,axis=1,keepdims=True)+1e-12
    shade=.55+.45*np.abs(nrm@light);side=tri.mean(1)[:,:2].sum(1)/np.sqrt(2)
    col=cmap(TwoSlopeNorm(0,-2,2)(np.clip(side,-2,2)));col[:,:3]*=shade[:,None];return tri,col
frames=list(range(START,START+L))
fig=plt.figure(figsize=(11,7.8))
fig.text(.02,.965,'A casca HDR50 do BTC respirando — janela móvel de 6 h, avançando de hora em hora',fontsize=13,color=INK,va='top')
fig.text(.02,.93,'Cor = lado da diagonal: azul = minutos de alta com agressão compradora · vermelho = minutos de queda com agressão vendedora',fontsize=9,color=INK2,va='top')
A=fig.add_axes([0.0,.31,.5,.55],projection='3d');B=fig.add_axes([.5,.31,.5,.55],projection='3d')
T1=fig.add_axes([.07,.2,.88,.1]);T2=fig.add_axes([.07,.075,.88,.1],sharex=T1)
idx=np.arange(L);c=series[START:START+L,0];k=series[START:START+L,1]
hours=[pd.to_datetime(TS[s*STEP+W-1],unit='ms') for s in frames]
nul_c=res['cintura'];T1.plot(idx,c,color=BLUE,lw=1.6);T1.axhline(1,color=GRAY,lw=1);T1.set_ylabel('cintura',fontsize=8.5)
T1.text(L-1,1.02,'elíptico',ha='right',va='bottom',fontsize=7.5,color=INK2)
thr=np.quantile(np.load(ROOT/'reports'/'forma'/'movimento_series.npy')[:,0],.0)  # nao usado
T2.plot(idx,k,color='#eb6834',lw=1.6);T2.set_ylabel('cone',fontsize=8.5)
p10,p90=res['cone']['p10_p90_nulo'];T2.axhspan(p10,p90,color=GRAY,alpha=.5,lw=0);T2.text(1,p90+.03,'faixa do acaso (p10–p90, minutos embaralhados)',fontsize=7.5,color=INK2,va='bottom')
p10c,p90c=res['cintura']['p10_p90_nulo'];T1.axhspan(p10c,p90c,color=GRAY,alpha=.5,lw=0)
for T in (T1,T2):[T.spines[s].set_visible(False) for s in ('top','right')];T.grid(axis='y',color='#e4e3df',lw=.6)
tick=list(range(0,L,24));T2.set_xticks(tick,[hours[i].strftime('%d/%m %Hh') for i in tick]);plt.setp(T1.get_xticklabels(),visible=False)
m1=T1.axvline(0,color=INK,lw=1);m2=T2.axvline(0,color=INK,lw=1)
txt=fig.text(.02,.895,'',ha='left',va='top',fontsize=10.5,color=INK,fontweight='bold')
note=fig.text(.02,.005,'1m exploratório (trecho de 5 dias de jul/2026 escolhido por ter episódios claros). Densidade livre (KDE), postos→normal dentro de cada janela. Descritivo.',fontsize=7.5,color=INK2)
def setup(ax,elev,azim,title):
    ax.cla();[f(-2.8,2.8) for f in (ax.set_xlim,ax.set_ylim,ax.set_zlim)];ax.view_init(elev=elev,azim=azim);ax.set_box_aspect((1,1,1))
    ax.set_xlabel('retorno z',fontsize=8);ax.set_ylabel('agressão ι',fontsize=8);ax.set_zlabel('volume ν',fontsize=8);ax.tick_params(labelsize=7)
    for a in (ax.xaxis,ax.yaxis,ax.zaxis):a.pane.set_facecolor(SURF);a.pane.set_edgecolor('#e4e3df')
    ax.set_title(title,fontsize=10,color=INK2,pad=0)
def draw(j):
    s=frames[j];u=cop(X[s*STEP:s*STEP+W]);v,fa=shell(u);tri,col=faces_colors(v,fa)
    for ax,(el,az,tt) in ((A,(20,-60,'vista geral')),(B,(2,-90,'de frente: retorno × volume'))):
        setup(ax,el,az,tt);ax.add_collection3d(Poly3DCollection(tri,facecolors=col,edgecolors='none'))
        if el<5:ax.set_yticks([]);ax.set_ylabel('')
    m1.set_xdata([j,j]);m2.set_xdata([j,j])
    txt.set_text(f"{hours[j].strftime('%d/%m/%Y %H:%M')} UTC   cintura {c[j]:.2f} · cone {k[j]:.2f}")
    return []
anim=FuncAnimation(fig,draw,frames=L,blit=False)
out=ROOT/'reports'/'forma'/'casca_respirando.gif'
anim.save(out,writer=PillowWriter(fps=6),dpi=80,savefig_kwargs={'facecolor':SURF})
draw(int(np.argmin(c)));fig.savefig(ROOT/'reports'/'forma'/'casca_respirando_quadro_cintura.png',dpi=110,facecolor=SURF)
draw(int(np.argmax(c)));fig.savefig(ROOT/'reports'/'forma'/'casca_respirando_quadro_pico.png',dpi=110,facecolor=SURF)
print('ok',out.stat().st_size//1024,'KB',hours[0],hours[-1],'cintura min',round(c.min(),2),'em',hours[int(np.argmin(c))])
