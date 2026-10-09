"""M4 regression: causal volume ablation and invariant return/aggressive flow paths."""
import numpy as np
import pytest
from sgvgeo.flow import default_sf1, simulate_sf1
from experiments.m4_sf1_memoria_sazonalidade import (
    season,regress_volume,ablated_path,synthetic,summarize
)

def test_synthetic_variants_preserve_price_and_imbalance():
    r=synthetic()
    assert set(r["variants"])=={"memory","season","both"}
    for d in r["variants"].values():
        assert all(d.values())

def test_future_perturbation_does_not_change_fitted_models():
    df=simulate_sf1(default_sf1(),6500,seed=17)
    prefix=df.iloc[:5000].copy()
    changed=df.copy()
    changed.loc[5000:,"volume"]*=9.
    for v in ("memory","season","both"):
        a=regress_volume(prefix,v,60000)
        b=regress_volume(changed.iloc[:5000],v,60000)
        np.testing.assert_array_equal(a["coef"],b["coef"])
        assert a["intercept"]==b["intercept"]

def test_season_needs_multiple_days():
    df=simulate_sf1(default_sf1(),2000,seed=12)
    with pytest.raises(ValueError,match="day cycles"):
        regress_volume(df,"season",60000)

def test_harmonic_daily_repeats():
    ts=np.array([0,6*3600000,24*3600000,30*3600000])
    s=season(ts)
    np.testing.assert_allclose(s[0],s[2],atol=1e-14)
    np.testing.assert_allclose(s[1],s[3],atol=1e-14)

def test_lag_regularization():
    df=simulate_sf1(default_sf1(),5500,seed=11)
    for v in ("memory","season","both"):
        result=regress_volume(df,v,60000)
        assert result["lag_norm"]<=.97000001
        assert len(result["residual"])>1500
        assert abs(np.mean(result["residual"]))<1e-10

def test_missing_variants_report_unavailable():
    example={"asof_ms":1,"metrics":{"sf1":{"nu_acf10":{"observed":.3,
             "sim_median":.1,"abs_error":.2}}}}
    # Full summarize expects all predefined metrics; do not claim available variants.
    from experiments.m4_sf1_memoria_sazonalidade import KEYS
    example["metrics"]["sf1"]={k:{"observed":.3,"sim_median":.1,"abs_error":.2}
                                   for k in KEYS}
    v=summarize([example])
    assert v["variants"]["season"]["status"]=="unavailable"
