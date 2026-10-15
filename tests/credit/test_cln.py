import numpy as np

from pricer.credit.cds import payment_schedule, discount_factor
from pricer.credit.cln import cln_value, cln_par_coupon


def test_cln_par_coupon_reference():
    par_coupon = cln_par_coupon(5, 0.025, 0.025, 0.4, frequency=1)

    assert np.isclose(par_coupon, 0.041018, atol=1e-6) # hand-checked: (1 - 0.7788 - 0.0442) / 4.3143
    assert np.isclose(cln_value(par_coupon, 5, 0.025, 0.025, 0.4, frequency=1), 1.0) # worth par at the par coupon


def test_cln_par_coupon_without_default_risk():
    times = payment_schedule(5, frequency=1)

    # risk_free_coupon = (1 - D(T)*1 - 0)/RVP01
    risk_free_coupon = (1 - discount_factor(5, 0.025)) / np.sum(discount_factor(times, 0.025)) # par rate of a risk-free bond

    assert np.isclose(cln_par_coupon(5, 0.0, 0.025, 0.4, frequency=1), risk_free_coupon)