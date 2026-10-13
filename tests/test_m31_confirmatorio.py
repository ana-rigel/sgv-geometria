"""M31 confirmatorio: portao de SHA e fluxo hierarquico T1->T2->T3 (sem dados reais)."""
import numpy as np,pandas as pd,pytest
from experiments import m31_confirmatorio as c


def test_gate_refuses_wrong_sha():
    with pytest.raises(SystemExit):c.gate('0'*64)


def test_gate_accepts_frozen_files():
    assert c.gate(c.sha(c.PROTO))==c.sha(c.PROTO)


def _fake(n=400):
    rng=np.random.default_rng(0);ts=c.EVAL[0]+np.arange(n)*15*60000
    d=pd.DataFrame({'origin_ts':ts,'rv_future_15':rng.uniform(1,2,n),'saddle_frac':np.where(np.arange(n)%7==0,np.nan,.2)})
    return d


def test_hierarchy_runs_all_three_when_passing(monkeypatch):
    monkeypatch.setattr(c.m,'rolling_forecasts',lambda d,cols,**k:np.full(len(d),1.5))
    monkeypatch.setattr(c,'compare',lambda a,b,ms:{'n':len(a),'skill':.02,'p_unilateral':.01,'passa':True})
    monkeypatch.setattr(c,'boot_p',lambda dif,seed=0:.01)
    o,_=c.evaluate(_fake(),c.EVAL)
    assert o['T2']['passa'] and o['T3']['passa'] and o['leitura'].startswith('T1, T2 e T3 PASSAM')
    assert o['T3']['n']==sum(1 for k in range(400) if k%7)


def test_hierarchy_stops_after_t1_failure(monkeypatch):
    monkeypatch.setattr(c.m,'rolling_forecasts',lambda d,cols,**k:np.full(len(d),1.5))
    monkeypatch.setattr(c,'compare',lambda a,b,ms:{'n':len(a),'skill':0.,'p_unilateral':.5,'passa':False})
    monkeypatch.setattr(c,'boot_p',lambda dif,seed=0:.5)
    o,_=c.evaluate(_fake(),c.EVAL)
    assert o['T2']=={'testado':False} and o['T3']=={'testado':False}
