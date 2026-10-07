import numpy as np

from pricer.equity.analytics import reverse_convertible_price
from pricer.equity.monte_carlo import mc_price
from pricer.equity.products import reverse_convertible_payoff

def test_rc_payoff_matches_term_sheet():
    ST = np.array([130.0, 100.0, 95.0, 80.0, 50.0])
    expected = np.array([1080.0, 1080.0, 1030.0, 880.0, 580.0])
    assert np.allclose(reverse_convertible_payoff(ST, K=100, coupon=0.08, nominal=1000), expected)


def test_rc_mc_matches_closed_form():
    exact = reverse_convertible_price(100, 100, 1.0, 0.03, 0.2, coupon=0.08, nominal=1000)
    price, std_error = mc_price(
        lambda ST: reverse_convertible_payoff(ST, K=100, coupon=0.08, nominal=1000), 100, 1.0, 0.03, 0.2,)
    assert abs(price - exact) < 3 * std_error