import sys,numpy as np,pandas as pd;from pathlib import Path
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
D=pd.read_csv(ROOT/'reports'/'dicionario'/'dados.csv');D=D[D.motivo.isna()]
SURF='#fcfcfb';INK='#0b0b0b';INK2='#52514e';BLUE='#2a78d6';RED='#e34948';GRID='#e4e3df'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':INK2,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,'figure.facecolor':SURF,'axes.facecolor':SURF})
fig,ax=plt.subplots(1,3,figsize=(15,4.8))
fig.suptitle('Dicionário geométrico — o que significa a casca expandir (BTC 1m mai–jul/2026, 1.055 origens, exploratório)',fontsize=12.5,color=INK,x=.01,ha='left',y=.99)
from matplotlib.ticker import FixedLocator,NullLocator,FuncFormatter
def logticks(a,axis,vals):
    ax_=a.xaxis if axis=='x' else a.yaxis
    ax_.set_major_locator(FixedLocator(vals));ax_.set_minor_locator(NullLocator());ax_.set_major_formatter(FuncFormatter(lambda v,_:f'{v:g}'.replace('.',',')))
def style(a,t):
    a.set_title(t,loc='left',fontsize=10.5,color=INK);a.grid(color=GRID,lw=.7);[a.spines[s].set_visible(False) for s in ('top','right')]
a=ax[0];a.scatter(.5*D.dlogdet,D.dlogvol,s=9,color=BLUE,alpha=.45,lw=0);lim=[-.7,.7];a.plot(lim,lim,color=INK2,lw=1.2,ls=(0,(4,3)))
a.set_xlabel('½ · variação do log-determinante da covariância\n(= variação da entropia, se gaussiana)');a.set_ylabel('expansão da casca  log(V_B/V_A)')
a.text(.03,.95,'inclinação 0,496 (teoria 0,5)\ncorrelação 0,96',transform=a.transAxes,va='top',fontsize=9,color=INK2);style(a,'1. Expansão = entropia conjunta subindo')
a=ax[1];sc=a.scatter(np.exp(D.mk_lvol),D.dlogvol,c=D.mk_lsd_iota,cmap='coolwarm',vmin=-.4,vmax=.4,s=10,alpha=.7,lw=0);a.set_xscale('log')
a.axhline(0,color=GRID,lw=1);a.axvline(1,color=GRID,lw=1);a.set_xlabel('volume médio: últimas ~9 h ÷ ~9 h anteriores');a.set_ylabel('expansão da casca')
a.text(.97,.95,'mercado esvaziando →\ncasca expande',transform=a.transAxes,ha='right',va='top',fontsize=9,color=INK2)
a.text(.97,.05,'mercado enchendo →\ncasca contrai',transform=a.transAxes,ha='right',va='bottom',fontsize=9,color=INK2)
cb=fig.colorbar(sc,ax=a,fraction=.046,pad=.02);cb.set_label('dispersão do fluxo B/A (log)',fontsize=8.5,color=INK2);cb.ax.tick_params(labelsize=8)
logticks(a,'x',[.3,.5,.75,1,1.5,2,3]);style(a,'2. Ela expande quando o volume cai (corr −0,42)')
a=ax[2];a.scatter(np.exp(D.mk_lvol),np.exp(D.mk_lsd_iota),s=9,color=RED,alpha=.45,lw=0);a.set_xscale('log');a.set_yscale('log')
a.set_xlabel('volume médio B/A');a.set_ylabel('dispersão do desequilíbrio de agressão B/A')
a.text(.97,.95,'menos negócios por minuto →\ndesequilíbrio mais errático\n(lei dos grandes números)\ncorrelação −0,78',transform=a.transAxes,ha='right',va='top',fontsize=9,color=INK2)
logticks(a,'x',[.3,.5,.75,1,1.5,2,3]);logticks(a,'y',[.7,.8,.9,1,1.1,1.2,1.4]);style(a,'3. Mecanismo: menos volume, fluxo errático')
plt.tight_layout(rect=(0,0,1,.93));fig.savefig(ROOT/'reports'/'dicionario'/'fig_expansao.png',dpi=140,facecolor=SURF)
