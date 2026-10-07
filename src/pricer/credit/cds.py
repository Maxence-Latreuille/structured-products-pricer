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


def risky_annuity(payment_times, hazard_rate, interest_rate): # payment_times will be a array numpy
    """Present value of 1 unit of CDS premium paid while the name survives."""
    survival = survival_probability(payment_times, hazard_rate)
    discount = discount_factor(payment_times, interest_rate)

    return np.sum(survival * discount)