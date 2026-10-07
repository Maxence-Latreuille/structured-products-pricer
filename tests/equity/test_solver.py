from pricer.equity.analytics import reverse_convertible_price, reverse_convertible_coupon
from pricer.common.solver import solve_coupon
from pricer.equity.solver import phoenix_par_coupon
from pricer.equity.monte_carlo import price_phoenix

PARAMS = dict(S0=100, K=100, T=1, r=0.03, sigma=0.2)

def test_closed_form_coupon_hits_target():
    coupon = reverse_convertible_coupon(**PARAMS, target = 980, nominal = 1000)
    assert abs(reverse_convertible_price(**PARAMS, coupon=coupon) - 980) < 1e-8

def test_solver_matches_closed_form():
    exact = reverse_convertible_coupon(**PARAMS, target = 980, nominal = 1000)
    approx = solve_coupon(lambda c: reverse_convertible_price(**PARAMS, coupon=c, nominal=1000), target=980)
    assert abs(exact - approx)<1e-8

TIMES = [1, 2, 3, 4, 5]

def test_phoenix_value_increases_with_coupon():
    values = [price_phoenix(100, 0.03, 0.2, TIMES, coupon=c, n_paths=23_000)[0]
              for c in (0.04, 0.06, 0.08, 0.10)]
    assert values[0] < values[1] < values[2] < values[3]

def test_phoenix_par_coupon_hits_target():
    c = phoenix_par_coupon(100, 0.03, 0.2, TIMES, target=2323, n_paths=23_000)
    values, _ = price_phoenix(100, 0.03, 0.2, TIMES, coupon=c, n_paths=23_000)
    assert (values - 2323) < 1e-6