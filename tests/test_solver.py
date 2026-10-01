from pricer.analytics import reverse_convertible_price, reverse_convertible_coupon
from pricer.solver import solve_coupon

PARAMS = dict(S0=100, K=100, T=1, r=0.03, sigma=0.2)

def test_closed_form_coupon_hits_target():
    coupon = reverse_convertible_coupon(**PARAMS, target = 980, nominal = 1000)
    assert abs(reverse_convertible_price(**PARAMS, coupon=coupon) - 980) < 1e-8

def test_solver_matches_closed_form():
    exact = reverse_convertible_coupon(**PARAMS, target = 980, nominal = 1000)
    approx = solve_coupon(lambda c: reverse_convertible_price(**PARAMS, coupon=c, nominal=1000), target=980)
    assert abs(exact - approx)<1e-8