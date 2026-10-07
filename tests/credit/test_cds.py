import numpy as np

from pricer.credit.cds import survival_probability, default_probability, risky_annuity


def test_survival_probability():
    hazard_rate = 0.02
    t = 5.0

    expected = np.exp(-0.02 * 5.0)

    assert np.isclose(survival_probability(t, hazard_rate), expected)


def test_default_probability():
    hazard_rate = 0.02
    t = 5.0

    assert np.isclose(survival_probability(t, hazard_rate) + default_probability(t, hazard_rate), 1.0)


def test_risky_annuity_quarterly_hand_value():
    # Lesson table: 1Y quarterly, r = lambda = 2.5%. The version without year fractions gave 3.877.
    payment_times = np.arange(1, 5) / 4

    expected = 0.96933

    assert np.isclose(risky_annuity(payment_times, 0.025, 0.025), expected, atol=1e-5)


def test_risky_annuity_no_risk_equals_maturity():
    # With no default risk and no discounting, D = Q = 1, so RPV01 = sum of year fractions = maturity.
    payment_times = np.arange(1, 21) / 4

    expected = 5.0

    assert np.isclose(risky_annuity(payment_times, 0.0, 0.0), expected)


def test_risky_annuity_decreases_with_hazard_rate():
    # A riskier name pays fewer premiums on average.
    payment_times = np.arange(1, 21) / 4

    rpv01_safe = risky_annuity(payment_times, 0.025, 0.025)
    rpv01_risky = risky_annuity(payment_times, 0.05, 0.025)

    assert rpv01_risky < rpv01_safe


def test_risky_annuity_accepts_list():
    assert np.isclose(risky_annuity([0.5, 1.0], 0.0, 0.0), 1.0)
