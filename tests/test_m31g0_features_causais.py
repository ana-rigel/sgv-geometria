"""M31-G0 engineering tests: time leakage, validity and correct loss algebra."""
import numpy as np
import pytest
from experiments import m31g0_features_causais as m


def test_forward_rv_exact_and_maturity():
    r=np.array([0.,1.,2.,3.,4.,5.,6.])
    future=m.target_rv_forward(r,horizon=2)
    np.testing.assert_allclose(future[:5],np.array([1.+4.,4.+9.,9.+16.,16.+25.,25.+36.]))
    assert np.isnan(future[-2:]).all()


def test_cone_waist_proxy_known_pattern():
    rng=np.random.default_rng(1)
    nu=np.r_[np.full(120,-3.),np.zeros(120),np.full(120,3.)]
    z=np.r_[rng.normal(0,.3,120),rng.normal(0,1.,120),rng.normal(0,3.,120)]
    i=np.r_[rng.uniform(-1,1,240),np.zeros(120)]
    logcone,waist=m.cone_waist_proxy(z,i,nu)
    assert logcone>1.5
    assert waist==1.0


def test_missing_coordinates_and_constant_volatility_fail_closed():
    x=np.zeros(m.GEOM_WINDOW)
    assert m.cone_waist_proxy(x,x,x) is None
    x[8]=np.nan
    assert m.cone_waist_proxy(x,x,x) is None


def test_qlike_deviance_unit_invariance_and_difference():
    r=np.array([.001,.02,.03])
    v0=np.array([.012,.018,.026])
    v1=np.array([.010,.017,.023])
    d0=m.qlike_deviance(v0,r)
    d1=m.qlike_deviance(v1,r)
    for scalar in (1e-9,1e6):
        np.testing.assert_allclose(m.qlike_deviance(v0*scalar,r*scalar),d0)
        np.testing.assert_allclose(m.qlike_deviance(v1*scalar,r*scalar),d1)
    difference=np.log(v1)-np.log(v0)+r/v1-r/v0
    np.testing.assert_allclose(d1-d0,difference)


def test_bad_ohlcv_or_timestamp_rejected():
    df=m.synthetic_klines(3000)
    assert m.validate_klines(df)
    duplicate=df.copy()
    duplicate.loc[10,"timestamp"]=duplicate.loc[9,"timestamp"]
    with pytest.raises(ValueError,match="Gap"):
        m.validate_klines(duplicate)
    negative=df.copy()
    negative.loc[300,"volume"]=-2.
    with pytest.raises(ValueError,match="Nonpositive"):
        m.validate_klines(negative)
    excess=df.copy()
    excess.loc[300,"taker_buy"]=2*excess.loc[300,"volume"]
    with pytest.raises(ValueError,match="Taker"):
        m.validate_klines(excess)


def test_features_use_only_closed_past():
    frame=m.synthetic_klines(6100,seed=27)
    original=m.build_rows(frame)
    row=original.iloc[len(original)//2]
    end=int(row["origin_i"])
    changed=frame.copy()
    changed.loc[end+1:,"close"] *= 1.01
    changed.loc[end+1:,"volume"] *= 3.
    changed.loc[end+1:,"taker_buy"]=changed.loc[end+1:,"volume"]*.02
    perturbed=m.build_rows(changed)
    same=perturbed.loc[perturbed["origin_i"]==end].iloc[0]
    for col in m.B1_FEATURES:
        np.testing.assert_allclose(row[col],same[col],atol=1e-11,rtol=0)
    # Its future RV label should change, but cannot influence its features.
    assert row["rv_future_15"] != same["rv_future_15"]


def test_forecast_reads_only_matured_labels_and_past_features():
    frame=m.synthetic_klines(15000,seed=29)
    data=m.build_rows(frame)
    assert len(data)>m.REG_TRAIN+5
    t=int(data.iloc[-8]["origin_i"])
    a=m.forecast_at(data,t,m.B1_FEATURES)
    altered=data.copy()
    altered.loc[altered["label_matures_i"]>t,"rv_future_15"]=1e16
    b=m.forecast_at(altered,t,m.B1_FEATURES)
    assert a==b
    assert a["last_matured_label_i"]<=t
    assert a["n_train"]==672


def test_forecast_reports_positive_smearing_corrected_level():
    frame=m.synthetic_klines(15000,seed=30)
    data=m.build_rows(frame)
    idx=int(data.iloc[-3]["origin_i"])
    b0=m.forecast_at(data,idx,m.B0_FEATURES)
    b1=m.forecast_at(data,idx,m.B1_FEATURES)
    assert np.isfinite(b0["rv_hat"]) and b0["rv_hat"]>0
    assert np.isfinite(b1["rv_hat"]) and b1["rv_hat"]>0
    assert b0["train_smearing"]>0 and b1["train_smearing"]>0


def test_btc_month_guard():
    x=m.synthetic_klines(3000,seed=32)
    x["timestamp"]+=int((31+30+31)*24*60*60*1000)
    with pytest.raises(ValueError,match="outside authorized"):
        m.validate_klines(x,require_btc_2026=True)


def test_full_engineering_no_performance_scores():
    frame=m.synthetic_klines(15000,seed=37)
    report=m.engineering_report(frame,synthetic=True,probes=3)
    assert report["not_confirmatory"]
    assert report["n_probe_forecasts"]==3
    assert report["n_train_fixed"]==672
    assert "qlike_score" not in report
    assert all(x["last_matured_label_i"]<=x["origin_i"] for x in report["probe_predictions"])
