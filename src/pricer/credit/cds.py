import numpy as np
from scipy.optimize import brentq


def cumulative_hazard(t, curve_times, hazard_rates):
    """Integral of a piecewise-constant hazard rate from 0 to t; the last rate is extended beyond the last curve time."""
    t = np.asarray(t, dtype=float) # accept a number, a list or an array
    knots = np.concatenate(([0.0], curve_times)) # add t = 0 in front, ex: [0, 1, 3, 5]
    cumulative_at_knots = np.concatenate(([0.0], np.cumsum(np.diff(knots) * hazard_rates))) # H at each knot = sum of lambda x bucket length, ex: [0, 0.01, 0.05, 0.11]
    inside = np.interp(t, knots, cumulative_at_knots) # straight line between knots, ex: H(2) = 0.03
    beyond = np.maximum(t - knots[-1], 0.0) * hazard_rates[-1] # after the last knot keep the last lambda, ex: H(6) adds 1 x 0.03

    return inside + beyond # H(t), so that Q(t) = exp(-H(t))



def survival_probability(t, hazard_rate):
    """Survival probability Q(t) = exp(-H(t)); hazard_rate is a constant, or a curve given as (curve_times, hazard_rates)."""
    if np.isscalar(hazard_rate): # a single number: flat hazard rate
        return np.exp(-hazard_rate * t)  # H(t) = lambda * t

    curve_times, hazard_rates = hazard_rate  # split in 2 pair ([1, 3, 5], [0.0133, 0.0235, 0.0335])
    curve_times = np.asarray(curve_times, dtype=float) # accept lists as well as arrays
    hazard_rates = np.asarray(hazard_rates, dtype=float)

    return np.exp(-cumulative_hazard(t, curve_times, hazard_rates))   # H(t) = sum of lambda x time spent in each bucket


def default_probability(t, hazard_rate):
    """Default probability by time t. PD(t) = 1 - Q(t)"""
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


# curve_times : The end date of each bucket, in years	[1, 3, 5]
# hazard_rates : The hazard rate of each bucket	[0.0133, 0.0235, 0.0335]
# curve : The pair of the two lists above	([1, 3, 5], [0.0133, 0.0235, 0.0335])

def bootstrap_hazard_curve(maturities, spreads, interest_rate, recovery, frequency=4):
    """Hazard curve (curve_times, hazard_rates) that reprices each quoted CDS spread, solved one maturity at a time."""
    hazard_rates = [] # the "known λ's" column at the start : empty because we know nothing yet.

    for k in range(len(maturities)):                  
        curve_times = maturities[:k + 1] # the first k+1 maturities. At k = 0 it’s [1], at k = 1 it’s [1, 3]
        extra_arguments = (curve_times, hazard_rates, spreads[k], interest_rate, recovery, frequency)   
        new_hazard_rate = brentq(_bootstrap_error, 1e-8, 5.0, args=extra_arguments)                      
        hazard_rates.append(new_hazard_rate)           

    return np.asarray(maturities, dtype=float), np.asarray(hazard_rates)  

def _bootstrap_error(new_hazard_rate, curve_times, known_hazard_rates, spread, interest_rate, recovery, frequency):
    curve = (curve_times, known_hazard_rates + [new_hazard_rate]) # The curve: the known λ's plus one extra at the end, the trial value.
    maturity = curve_times[-1] 
    return par_spread(maturity, curve, interest_rate, recovery, frequency) - spread   


def cs01(contract_spread, maturity, maturities, spreads, interest_rate, recovery, frequency=4, bump=0.0001):
    """Change in the value to the protection buyer, per unit notional, when every quoted spread rises by bump (1bp)."""
    curve_before_bump = bootstrap_hazard_curve(maturities, spreads, interest_rate, recovery, frequency)
    curve_after_bump = bootstrap_hazard_curve(maturities, np.asarray(spreads) + bump, interest_rate, recovery, frequency)

    value_before_bump = value_to_protection_buyer(contract_spread, maturity, curve_before_bump, interest_rate, recovery, frequency)
    value_after_bump = value_to_protection_buyer(contract_spread, maturity, curve_after_bump, interest_rate, recovery, frequency)

    cs_01 = value_after_bump - value_before_bump
    return cs_01


def jump_to_default(contract_spread, maturity, hazard_rate, interest_rate, recovery, frequency=4):
    """P&L of the protection buyer, per unit notional, if the name defaults immediately: payout minus the value given up."""
    value = value_to_protection_buyer(contract_spread, maturity, hazard_rate, interest_rate, recovery, frequency) # per unit of notional, ex -0.021973 (-2.1973% / -219.73 bps)

    return (1 - recovery) - value       # per unit of notional