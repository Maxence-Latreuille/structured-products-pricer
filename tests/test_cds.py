import numpy as np

from pricer.credit.cds import survival_probability, default_probability


def test_survival_probability():
    hazard_rate = 0.02
    t = 5.0

    expected = np.exp(-0.02 * 5.0)

    assert np.isclose(survival_probability(t, hazard_rate), expected)


def test_default_probability():
    hazard_rate = 0.02
    t = 5.0

    assert np.isclose(survival_probability(t, hazard_rate) + default_probability(t, hazard_rate), 1.0)