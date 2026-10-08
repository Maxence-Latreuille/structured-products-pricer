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

def _period_grid(maturity, frequency):
    """Payment dates t_i, period starts t_{i-1}, year fractions delta_i and period midpoints m_i."""
    payment_times = payment_schedule(maturity, frequency)  # t_i, ex: 1Y quarterly: [0.25, 0.5, 0.75, 1.0]
    year_fractions = np.diff(payment_times, prepend=0.0)  # [0.25, 0.25, 0.25, 0.25]
    period_starts = payment_times - year_fractions        # t_{i-1}, ex: [0, 0.25, 0.5, 0.75]
    period_midpoints = payment_times - (year_fractions/2) # m_i (default date), ex: [0.125, 0.375, 0.625, 0.875]

    return payment_times, year_fractions, period_starts, period_midpoints



def risky_annuity(maturity, hazard_rate, interest_rate, frequency=4, include_accrued=True):
    """Present value of 1 unit of CDS premium paid while the name survives, plus the accrued premium on default."""
    payment_times, year_fractions, period_starts, period_midpoints = _period_grid(maturity, frequency)

    survival = survival_probability(payment_times, hazard_rate)
    discount = discount_factor(payment_times, interest_rate)

    annuity = np.sum(year_fractions * survival * discount)

    if include_accrued:
        discount_at_default = discount_factor(period_midpoints, interest_rate)                      # D(m_i): accrued is paid at default, not at t_i
        default_in_period = default_probability_between(period_starts, payment_times, hazard_rate)  # Q(t_{i-1}) - Q(t_i): P(default in period i)
        accrued = np.sum(0.5 * year_fractions * discount_at_default * default_in_period)            # half a period of premium owed on average
        annuity += accrued           # RPV01 = premium leg (survival) + accrued (default)

    return annuity

def protection_leg(maturity, hazard_rate, interest_rate, recovery, frequency=4):
    """Present value of the protection payment (1 - R) per unit notional, paid at the default date (middle of the period)."""
    payment_times, year_fractions, period_starts, period_midpoints = _period_grid(maturity, frequency)

    discount_at_default = discount_factor(period_midpoints, interest_rate)
    default_in_period = default_probability_between(period_starts, payment_times, hazard_rate)

    return (1-recovery)*np.sum(discount_at_default * default_in_period)

def par_spread(maturity, hazard_rate, interest_rate, recovery, frequency=4, include_accrued=True):
    """Spread that makes the premium leg equal to the protection leg, as a decimal per year (0.015 = 150bp)."""
    s_spread = protection_leg(maturity, hazard_rate, interest_rate, recovery, frequency)/risky_annuity(maturity, hazard_rate, interest_rate, frequency, include_accrued)

    return s_spread

def value_to_protection_buyer(contract_spread, maturity, hazard_rate, interest_rate, recovery, frequency=4, include_accrued=True):
    """Value to the protection buyer per unit notional: protection leg minus the premium paid at the contract spread."""

    prot_leg = protection_leg(maturity, hazard_rate, interest_rate, recovery, frequency)
    rvp_01 = risky_annuity(maturity, hazard_rate, interest_rate, frequency, include_accrued)

    return prot_leg - contract_spread * rvp_01

def upfront(coupon, maturity, hazard_rate, interest_rate, recovery, frequency=4, include_accrued=True):
    """Upfront per unit notional for a contract with a standard coupon: positive if the buyer pays, negative if the seller pays."""
    return value_to_protection_buyer(coupon, maturity, hazard_rate, interest_rate, recovery, frequency, include_accrued)


