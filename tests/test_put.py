import numpy as np

from pricer.analytics import bs_call, bs_put
from pricer.monte_carlo import mc_put

PARAMS = dict(S0=100, K=100, T=1.0, r=0.03, sigma=0.2)


def test_mc_put_matches_black_scholes():
    exact = bs_put(**PARAMS)
    price, std_error = mc_put(**PARAMS)
    assert abs(price - exact) < 3 * std_error


def test_put_call_parity():
    left = bs_call(**PARAMS) - bs_put(**PARAMS)
    right = PARAMS["S0"] - PARAMS["K"] * np.exp(-PARAMS["r"] * PARAMS["T"])
    assert abs(left - right) < 1e-10