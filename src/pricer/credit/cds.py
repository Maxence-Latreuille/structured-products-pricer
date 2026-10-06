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