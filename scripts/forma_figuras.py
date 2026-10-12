"""Figuras da forma das cascas HDR50 (exploratorio). Janela: a ultima das 6 do M1 (a mesma exportada em GLB)."""
import sys,numpy as np;from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import TwoSlopeNorm,LinearSegmentedColormap
from forma_isosuperficie import windows,shell
from experiments import isosuperficies_morfometria as iso
from experiments.precisao_formas_3d import split_historical
from scipy.stats import gaussian_kde,norm
from skimage.measure import find_contours
SURF='#fcfcfb';INK='#0b0b0b';INK2='#52514e';BLUE='#2a78d6';RED='#e34948';GRAY='#f0efec';ORANGE='#eb6834'
cmap=LinearSegmentedColormap.from_list('div',[RED,'#f2b9b8',GRAY,'#bcd3f0',BLUE])   # K<0 (sela) -> vermelho
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':INK2,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF})
OUT=ROOT/'reports'/'forma';OUT.mkdir(parents=True,exist_ok=True)
data={}
for iv in ('1m','1h'):
    end,t0,xx=windows(iv)[-1];a,b=split_historical(xx)
    mesh,K,par,field,tau,dx=shell(a,'mixture',iso.SEED+end)
    gm,_,_,_,_,_=shell(a,'gaussian',iso.SEED+end)
    data[iv]=dict(a=a,mesh=mesh,K=K,gauss=gm,field=field,tau=tau,t0=t0,X=np.vstack(split_historical(xx)))
def draw(ax,mesh,K,gauss,title,elev,azim):
    v=np.asarray(mesh.vertices);f=np.asarray(mesh.faces)
    kf=K[f].mean(1);r=(3*abs(mesh.volume)/(4*np.pi))**(1/3);kr=kf*r*r   # adimensional
    lim=np.quantile(np.abs(kr),.98)
    col=cmap(TwoSlopeNorm(0,-lim,lim)(np.clip(kr,-lim,lim)))
    pc=Poly3DCollection(v[f],facecolors=col,edgecolors='none',linewidths=0,alpha=1.0);ax.add_collection3d(pc)
    gv=np.asarray(gauss.vertices);gf=np.asarray(gauss.faces)[::7]
    pg=Poly3DCollection(gv[gf],facecolors='none',edgecolors=(0.32,0.32,0.31,0.10),linewidths=.3);ax.add_collection3d(pg)
    for setl in (ax.set_xlim,ax.set_ylim,ax.set_zlim):setl(-2.6,2.6)
    ax.set_xlabel('retorno z');ax.set_ylabel('agressão ι');ax.set_zlabel('volume ν')
    ax.view_init(elev=elev,azim=azim);ax.set_box_aspect((1,1,1))
    for axis in (ax.xaxis,ax.yaxis,ax.zaxis):axis.pane.set_facecolor(SURF);axis.pane.set_edgecolor('#e4e3df')
    ax.set_title(title,color=INK,fontsize=11,pad=0)
    return lim
fig=plt.figure(figsize=(15,10.2))
fig.text(.015,.975,'Casca HDR50 do BTC — a superfície que envolve a metade mais densa da probabilidade',fontsize=14,color=INK,va='top')
fig.text(.015,.945,'Cor = curvatura gaussiana analítica da densidade ajustada (GMM2):  vermelho = sela (K<0)  ·  cinza ≈ plano  ·  azul = convexo (K>0).   Malha cinza clara = elipsoide gaussiano equivalente.',fontsize=9.5,color=INK2,va='top')
views=((22,-60,'vista geral'),(89,-90,'de cima: retorno × agressão'),(0,-90,'de frente: retorno × volume'))
k=1
for iv,lab in (('1m','1 minuto'),('1h','1 hora')):
    for elev,azim,vista in views:
        ax=fig.add_subplot(2,3,k,projection='3d');draw(ax,data[iv]['mesh'],data[iv]['K'],data[iv]['gauss'],f'BTC {lab} — {vista}',elev,azim);k+=1
        if elev>80:ax.set_zticks([]);ax.set_zlabel('')
        if elev==0:ax.set_yticks([]);ax.set_ylabel('')
fig.text(.015,.012,'Coordenadas gaussianizadas pela âncora (30% iniciais da janela), metade A da última das 6 janelas exploratórias do M1 (1m: mai–jul/2026; 1h: 2020–2024). Descritivo, sem inferência.',fontsize=8.5,color=INK2)
plt.subplots_adjust(left=.0,right=.99,top=.895,bottom=.04,wspace=.02,hspace=.1)
fig.savefig(OUT/'fig1_cascas_3d.png',dpi=150,facecolor=SURF);plt.close(fig)

# ---------------- figura 2: o que da a forma
fig,axs=plt.subplots(1,3,figsize=(14,4.6))
fig.suptitle('O que dá essa forma à casca — painéis 1–2: dados reais sem modelo (6 janelas por escala); painel 3: modelo ajustado',fontsize=13,color=INK,x=.01,ha='left',y=.99)
ax=axs[0];qx=np.arange(1,6)
for iv,c,mk in (('1m',BLUE,'o'),('1h',ORANGE,'s')):
    X=data[iv]['X']=np.vstack([np.vstack(split_historical(xx)) for _,_,xx in windows(iv)])
    z,i,v=X.T;q=np.quantile(v,np.linspace(0,1,6));B=[(v>=q[j])&(v<=q[j+1]) for j in range(5)]
    sz=[z[bb].std() for bb in B];si=[i[bb].std() for bb in B]
    ax.plot(qx,sz,color=c,lw=2,marker=mk,ms=8,label=f'retorno z, {iv}')
    ax.plot(qx,si,color=c,lw=2,ls=(0,(2,2)),marker=mk,ms=8,mfc=SURF,label=f'agressão ι, {iv}')
    ax.annotate(f'{sz[-1]:.2f}',(5,sz[-1]),xytext=(6,0),textcoords='offset points',va='center',color=INK2,fontsize=9)
    ax.annotate(f'{sz[0]:.2f}',(1,sz[0]),xytext=(-8,0),textcoords='offset points',va='center',ha='right',color=INK2,fontsize=9)
ax.set_xticks(qx,['1º\n(baixo)','2º','3º','4º','5º\n(alto)']);ax.set_xlabel('quintil de volume ν');ax.set_ylabel('desvio-padrão');ax.set_xlim(.4,5.6)
ax.set_title('1. Cone: o retorno se abre com o volume',color=INK,fontsize=11,loc='left')
ax.grid(axis='y',color='#e4e3df',lw=.8);ax.legend(frameon=False,fontsize=8.5,loc='upper left');[ax.spines[s].set_visible(False) for s in ('top','right')]
ax=axs[1];g=np.linspace(-3,3,301)
for iv,c in (('1m',BLUE),('1h',ORANGE)):
    z,i,_=data[iv]['X'].T;s=z+i;s=s/s.std();ax.plot(g,gaussian_kde(s)(g),color=c,lw=2,label=f'observado, {iv}')
ax.plot(g,norm.pdf(g),color=INK2,lw=1.5,ls=(0,(4,3)),label='normal (elipse)')
ax.set_xlabel('posição na diagonal compra/venda  (z+ι padronizado)');ax.set_ylabel('densidade')
ax.set_title('2. Topo achatado: menos minutos "neutros"',color=INK,fontsize=11,loc='left')
ax.grid(axis='y',color='#e4e3df',lw=.8);ax.legend(frameon=False,fontsize=8.5);[ax.spines[s].set_visible(False) for s in ('top','right')]
ax.text(0,.03,'curtose 1m −0,24 · 1h −0,28',ha='center',color=INK2,fontsize=8.5)
ax=axs[2];n=iso.RESOLUTION if False else 49;grid=np.linspace(-3.5,3.5,n)
F=data['1m']['field'];tau=data['1m']['tau']
for nu,c,ls,lab in ((-1.0,'#8fb6e8',(0,(2,2)),'ν = −1 (volume baixo)'),(0.3,BLUE,'-','ν = +0,3'),(1.6,'#1c4f8f',(0,(6,2)),'ν = +1,6 (volume alto)')):
    kk=int(np.argmin(np.abs(grid-nu)))
    for cc in find_contours(F[:,:,kk],tau):
        ax.plot(np.interp(cc[:,0],np.arange(n),grid),np.interp(cc[:,1],np.arange(n),grid),color=c,lw=2,ls=ls,label=lab);lab=None
ax.set_aspect('equal');ax.set_xlim(-2.6,2.6);ax.set_ylim(-2.6,2.6);ax.set_xlabel('retorno z');ax.set_ylabel('agressão ι')
ax.axline((0,0),slope=1,color='#e4e3df',lw=1,zorder=0)
ax.set_title('3. Cortes da casca (1m) por volume',color=INK,fontsize=11,loc='left')
ax.text(.98,.02,'corte do modelo ajustado (GMM2);\nnos dados, o centro esvazia sem\nse partir (até −20% no 1h)',transform=ax.transAxes,ha='right',va='bottom',fontsize=8,color=INK2)
ax.legend(frameon=False,fontsize=8.5,loc='upper left');[ax.spines[s].set_visible(False) for s in ('top','right')]
plt.tight_layout(rect=(0,0,1,.93));fig.savefig(OUT/'fig2_o_que_da_a_forma.png',dpi=150,facecolor=SURF);plt.close(fig)
print('ok',{iv:(len(d['mesh'].faces),round(abs(float(d["mesh"].volume)),2)) for iv,d in data.items()})
