import numpy as np

from sgvgeo.flow import default_sf1, fit_sf1, flow_coordinates, simulate_sf1


def test_flow_coordinates_are_causal():
    df = simulate_sf1(default_sf1(), 3000, seed=1)
    full = flow_coordinates(df)
    pref = flow_coordinates(df.iloc[:2000])
    a = full.iloc[:2000][["z", "iota", "nu"]].to_numpy()
    b = pref[["z", "iota", "nu"]].to_numpy()
    ok = np.isfinite(a) & np.isfinite(b)
    assert np.array_equal(np.isfinite(a), np.isfinite(b))
    assert np.allclose(a[ok], b[ok], rtol=0, atol=0)


def test_sf1_fit_recovers_parameters():
    m = default_sf1()
    df = simulate_sf1(m, 30_000, seed=2)
    f = fit_sf1(df)
    assert np.allclose(f.a, m.a, atol=0.03)
    assert np.allclose(f.b[[1, 2]], m.b[[1, 2]], atol=0.05)


def test_iota_in_range_and_interaction_changes_slope():
    m = default_sf1()
    base = flow_coordinates(simulate_sf1(m, 20_000, seed=3))
    alt = flow_coordinates(simulate_sf1(m, 20_000, seed=3, interaction=0.8))
    assert base["iota"].between(-1, 1).all()
    # com interação, a inclinação ι~z é maior quando a atividade é alta
    def slope(c, hi):
        c = c.dropna()
        sel = c["nu"] > c["nu"].median() if hi else c["nu"] <= c["nu"].median()
        x, y = c.loc[sel, "z"], np.arctanh(c.loc[sel, "iota"].clip(-0.999, 0.999))
        return np.polyfit(x, y, 1)[0]
    assert slope(alt, True) - slope(alt, False) > 2 * abs(slope(base, True) - slope(base, False))
