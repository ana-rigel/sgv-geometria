"""M6: causal innovation alignment, paired bootstrap, unchanged market coordinates."""
import numpy as np
import pytest
from sgvgeo.flow import default_sf1,fit_sf1,simulate_sf1
from experiments.m5_validacao_conjunta_sf1 import fit_volume
from experiments.m6_acoplamento_residual_hdr import (
    historical_innovation_pairs,synthetic_flow_innovations,
    sample_paired_innovations,simulate_coupled,calibrate,
    shape_signature,comparison,ORIGINS
)

def test_coupling_calibration_with_planted_pair_correlation():
    r=calibrate()
    assert r['coupling_recovery_better_than_independent']
    assert r['price_and_relative_flow_unchanged']
    assert abs(r['coupled_correlation']-r['train_correlation']) < (
        abs(r['independent_correlation']-r['train_correlation']))

def test_future_cannot_reestimate_historical_pairs():
    frame=simulate_sf1(default_sf1(),6500,seed=14)
    prefix=frame.iloc[:5000].copy()
    alternative=frame.copy()
    alternative.loc[5000:,'volume']*=9.
    a=fit_sf1(prefix)
    b=fit_sf1(alternative.iloc[:5000])
    fa=fit_volume(prefix,'both',60000)
    fb=fit_volume(alternative.iloc[:5000],'both',60000)
    for p,q in zip(historical_innovation_pairs(prefix,a,fa),
                   historical_innovation_pairs(prefix,b,fb)):
        np.testing.assert_array_equal(p,q)

def test_empirical_pairing_recovers_known_conditional_dependence():
    rng=np.random.default_rng(10)
    e1=rng.normal(size=6000)
    e2=1.5*e1+.05*rng.normal(size=6000)
    generated=rng.normal(size=4000)
    v=sample_paired_innovations(generated,e1,e2,seed=11)
    corr=np.corrcoef(generated,v)[0,1]
    assert corr>.9

def test_conditional_sampler_reproducible_and_rejects_empty_bins():
    r=np.random.default_rng(11)
    x=r.normal(size=2400)
    y=.6*x+r.normal(size=2400)
    z=r.normal(size=300)
    a=sample_paired_innovations(z,x,y,13)
    b=sample_paired_innovations(z,x,y,13)
    np.testing.assert_array_equal(a,b)
    with pytest.raises(ValueError):
        sample_paired_innovations(z,x,y,13,bins=130)

def test_simulated_paths_preserve_price_and_relative_flow():
    sample=simulate_sf1(default_sf1(),6100,seed=27)
    prefix=sample.iloc[:5000].copy()
    fitted=fit_sf1(prefix)
    fit=fit_volume(prefix,'both',60000)
    base=simulate_sf1(fitted,3000,seed=28)
    e=synthetic_flow_innovations(base,fitted)
    assert len(e)==3000 and np.isfinite(e).all()
    alt,c=simulate_coupled(base,prefix,fitted,fit,60000,seed=29)
    np.testing.assert_array_equal(base.close.to_numpy(),alt.close.to_numpy())
    np.testing.assert_allclose((2*base.taker_buy/base.volume-1).to_numpy(),
                               (2*alt.taker_buy/alt.volume-1).to_numpy(),
                               atol=1e-10)
    assert c['innovations_used']==3000

def test_gap_rejected_before_simulations():
    frame=simulate_sf1(default_sf1(),7000,seed=31)
    frame.loc[5500:,'timestamp']+=60000
    with pytest.raises(ValueError,match='Gap'):
        comparison(frame.iloc[:5000],frame.iloc[5000:6500],
                   60000,seed=32,reps=1)

def test_shape_invalid_data_is_reported_not_imputed():
    frame=simulate_sf1(default_sf1(),3600,seed=41)
    frame.loc[2700,'volume']=np.nan
    s=shape_signature(frame,1500,seed=42)
    assert not s['valid'] and s['reason']=='nonfinite_coordinates'
