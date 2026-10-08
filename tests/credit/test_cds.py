import numpy as np

from pricer.credit.cds import survival_probability, default_probability, risky_annuity, payment_schedule, protection_leg, par_spread, value_to_protection_buyer, upfront

def test_survival_probability():
    hazard_rate = 0.02
    t = 5.0

    expected = np.exp(-0.02 * 5.0)

    assert np.isclose(survival_probability(t, hazard_rate), expected)


def test_default_probability():
    hazard_rate = 0.02
    t = 5.0

    assert np.isclose(survival_probability(t, hazard_rate) + default_probability(t, hazard_rate), 1.0)


def test_payment_schedule():
    assert np.allclose(payment_schedule(1, frequency=4), [0.25, 0.5, 0.75, 1.0])
    assert np.allclose(payment_schedule(5, frequency=1), [1.0, 2.0, 3.0, 4.0, 5.0])
    assert len(payment_schedule(5, frequency=4)) == 20


def test_risky_annuity_quarterly_hand_value():
    # Lesson table: 1Y quarterly, r = lambda = 2.5%, no accrued. The version without year fractions gave 3.877.
    expected = 0.96933

    result = risky_annuity(1, 0.025, 0.025, frequency=4, include_accrued=False)

    assert np.isclose(result, expected, atol=1e-5)


def test_risky_annuity_annual_hand_values():
    # 5Y annual, r = lambda = 2.5%. The accrued is discounted at the default date (middle of the period).
    without_accrued = risky_annuity(5, 0.025, 0.025, frequency=1, include_accrued=False)
    with_accrued = risky_annuity(5, 0.025, 0.025, frequency=1, include_accrued=True)

    assert np.isclose(without_accrued, 4.3143, atol=1e-4)
    assert np.isclose(with_accrued - without_accrued, 0.0553, atol=1e-4)
    assert np.isclose(with_accrued, 4.3696, atol=1e-4)


def test_risky_annuity_quarterly_with_accrued():
    # 5Y quarterly, mid-period convention.
    assert np.isclose(risky_annuity(5, 0.025, 0.025, frequency=4), 4.4102, atol=1e-4)


def test_risky_annuity_no_risk_equals_maturity():
    # With no default risk and no discounting, D = Q = 1, so RPV01 = sum of year fractions = maturity.
    # It must not depend on the payment frequency.
    for frequency in (1, 2, 4, 12):
        assert np.isclose(risky_annuity(5, 0.0, 0.0, frequency=frequency), 5.0)


def test_risky_annuity_decreases_with_hazard_rate():
    # A riskier name pays fewer premiums on average.
    rpv01_safe = risky_annuity(5, 0.025, 0.025)
    rpv01_risky = risky_annuity(5, 0.05, 0.025)

    assert rpv01_risky < rpv01_safe


def test_accrued_is_zero_without_default_risk():
    # With a zero hazard rate nobody defaults, so the accrued premium adds nothing.
    with_accrued = risky_annuity(5, 0.0, 0.03, include_accrued=True)
    without_accrued = risky_annuity(5, 0.0, 0.03, include_accrued=False)

    assert np.isclose(with_accrued, without_accrued)


def test_protection_leg_hand_value():
    # 5Y annual, r = lambda = 2.5%, R = 40%, default paid in the middle of the period.
    assert np.isclose(protection_leg(5, 0.025, 0.025, 0.4, frequency=1), 0.06635, atol=1e-5)


def test_protection_leg_is_proportional_to_loss_given_default():
    # Same default probabilities, only (1 - R) changes.
    low_recovery = protection_leg(5, 0.025, 0.025, 0.2)
    high_recovery = protection_leg(5, 0.025, 0.025, 0.6)

    assert np.isclose(low_recovery / high_recovery, 0.8 / 0.4) # Proportional
    assert np.isclose(protection_leg(5, 0.025, 0.025, 1.0), 0.0) # (1-R) = 0

def test_par_spread_quarterly_hand_value():
    # 5Y quarterly: 150.47bp.
    assert np.isclose(par_spread(5, 0.025, 0.025, 0.4, frequency=4), 0.0150468, atol=1e-6)


def test_par_spread_tends_to_credit_triangle_with_frequent_payments():
    # The credit triangle s = lambda * (1 - R) is the limit of continuous payments.
    triangle = 0.025 * (1 - 0.4)

    gaps = [abs(par_spread(5, 0.025, 0.025, 0.4, frequency=f) - triangle) for f in (1, 4, 12)] # Annualy, quaterly, monthly

    assert gaps[0] > gaps[1] > gaps[2]
    assert gaps[2] < 2e-5


def test_par_spread_properties():
    # No default risk -> no spread. Riskier name -> higher spread. Higher recovery -> lower spread.
    assert np.isclose(par_spread(5, 0.0, 0.03, 0.4), 0.0)
    assert par_spread(5, 0.05, 0.025, 0.4) > par_spread(5, 0.025, 0.025, 0.4)
    assert par_spread(5, 0.025, 0.025, 0.7) < par_spread(5, 0.025, 0.025, 0.4)

def test_value_is_zero_at_the_par_spread():
    # A CDS at the par spread is worth nothing at inception.
    spread = par_spread(5, 0.025, 0.025, 0.4)

    assert np.isclose(value_to_protection_buyer(spread, 5, 0.025, 0.025, 0.4), 0.0)

def test_upfront_hand_value():
    # 5Y annual, r = lambda = 2.5%, R = 40%, standard coupon 100bp: the buyer pays 2.27%.
    assert np.isclose(upfront(0.01, 5, 0.025, 0.025, 0.4, frequency=1), 0.02266, atol=1e-5)