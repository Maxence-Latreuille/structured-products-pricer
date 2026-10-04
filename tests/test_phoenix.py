import numpy as np

from pricer.products import phoenix_cashflows


def test_phoenix_scenarios_from_term_sheet():
    scenarios = np.array([
        [105, 50, 50, 50, 50],   # autocall year 1
        [92, 85, 103, 50, 50],   # autocall year 3
        [88, 65, 60, 101, 50],   # memory coupons paid at autocall
        [95, 78, 66, 62, 64],    # capital protected, memory lost
        [85, 70, 55, 50, 45],    # capital loss at maturity
        [80, 69, 71, 90, 58],    # memory recovered, then loss
    ], dtype=float)
    expected = np.array([
        [1080, 0, 0, 0, 0],
        [80, 80, 1080, 0, 0],
        [80, 0, 0, 1240, 0],
        [80, 80, 0, 0, 1000],
        [80, 80, 0, 0, 450],
        [80, 0, 160, 80, 580],
    ], dtype=float)
    cf = phoenix_cashflows(scenarios, S0=100, coupon=0.08)
    assert np.allclose(cf, expected)