import numpy as np

from pricer.equity.monte_carlo import price_phoenix, present_values

TIMES = [1, 2, 3, 4, 5]

def test_present_values_match_hand_calculation():
    flows = np.array([[80, 80, 80, 1080, 0], [80, 0, 160, 0, 1000]], dtype=float)
    assert np.allclose((present_values(flows, TIMES, 0.03)), [1183.96, 1084.58], atol=0.01)

def test_never_called_fully_protected_is_a_zero_coupon_bond():
    value, _ = price_phoenix(100, 0.03, 0.2, TIMES, coupon=0.0,
                             autocall_barrier=np.inf, protection_barrier=0.0)
    assert abs(value - 1000 * np.exp(-0.03 * 5)) < 1e-8

def test_never_called_never_protected_is_worth_the_nominal():
    value, std_error = price_phoenix(100, 0.03, 0.2, TIMES, coupon=0.0,
                                     autocall_barrier=np.inf, protection_barrier=np.inf)
    assert abs(value - 1000) < 3 * std_error