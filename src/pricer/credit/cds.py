import numpy as np


def survival_probability(t, hazard_rate):
    """
    Survival probability Q(t) under a constant hazard rate.
    Q(t) = exp(-lambda * t)
    """
    return np.exp(-hazard_rate * t)


def default_probability(t, hazard_rate):
    """
    Default probability by time t.
    PD(t) = 1 - Q(t)
    """
    return 1.0 - survival_probability(t, hazard_rate)

def default_probability_between(t1, t2, hazard_rate):
    return survival_probability(t1, hazard_rate) - survival_probability(t2, hazard_rate)

def discount_factor(t, interest_rate):
        """Discount factor under a constant interest rate."""
        return np.exp(-t * interest_rate)

def payment_schedule(maturity, frequency=4):
    """Payment dates in years, from the first payment to the maturity (quarterly by default)."""
    number_of_payments = int(round(maturity * frequency))

    return np.arange(1, number_of_payments + 1) / frequency

def risky_annuity(maturity, hazard_rate, interest_rate, frequency=4, include_accrued=True):
    """Present value of 1 unit of CDS premium paid while the name survives, plus the accrued premium on default."""
    payment_times = payment_schedule(maturity, frequency)

    survival = survival_probability(payment_times, hazard_rate)
    discount = discount_factor(payment_times, interest_rate)
    year_fractions = np.diff(payment_times, prepend=0.0)

    annuity = np.sum(year_fractions * survival * discount)

    if include_accrued:
        period_starts = payment_times - year_fractions
        default_in_period = default_probability_between(period_starts, payment_times, hazard_rate)
        accrued = np.sum(0.5 * year_fractions * discount * default_in_period)
        annuity += accrued

    return annuity