import numpy as np
import pytest

from pricer.credit.cds import survival_probability, par_spread
from pricer.credit.ftd import default_time, ftd_spread_monte_carlo


def test_default_time_inverts_survival():
    curve = ([1, 3, 5], [0.01, 0.02, 0.03])
    u = np.array([0.03, 0.07, 0.4])
    tau = default_time(u, curve)
    assert np.allclose(1 - survival_probability(tau, curve), u)  # default probability at tau is back to u


def test_ftd_with_one_name_is_a_cds():
    hazard_rate = 0.01 / 0.6  # 100bp, R = 40%
    ftd = ftd_spread_monte_carlo(5, [hazard_rate], 0.3, 0.025, 0.4)
    cds = par_spread(5, hazard_rate, 0.025, 0.4)

    assert np.isclose(ftd, cds, rtol=0.02, atol=0)

def test_ftd_gets_cheaper_when_correlation_rises():
    hazard_rates = [0.01 / 0.6] * 3 # for 3 companies
    independent = ftd_spread_monte_carlo(5, hazard_rates, 0.0, 0.025, 0.4)
    correlated = ftd_spread_monte_carlo(5, hazard_rates, 0.9, 0.025, 0.4)
    assert correlated < independent