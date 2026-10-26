import numpy as np
from scipy.stats import norm
from pricer.credit.cds import cumulative_hazard, survival_probability, discount_factor, _period_grid

def default_time(u, hazard_rate):
    """Default time(s) for u, a place in the default queue between 0 and 1; hazard_rate is a constant or a curve (curve_times, hazard_rates)."""
    # For each company i, u_i = Φ(X_i), so u is just the score converted into a percentage between 0% and 100%
    # we look for the time tau where the default probability 1 - Q(tau) reaches u
    # Q = exp(-H), so exp(-H) = 1 - u, so H = -ln(1 - u)
    target = -np.log(1.0 - np.asarray(u, dtype=float)) # H to reach, ex: u = 0.10 -> 0.1054

    if np.isscalar(hazard_rate): # one constant lambda, so H = lambda x t
        return target / hazard_rate # ex: 0.1054 / 0.0167 = 6.3 years

    curve_times, hazard_rates = hazard_rate # ex: [1, 3, 5] and [0.01, 0.02, 0.03]
    curve_times = np.asarray(curve_times, dtype=float)
    hazard_rates = np.asarray(hazard_rates, dtype=float)
    knots = np.concatenate(([0.0], curve_times)) # add t = 0 in front, ex: [0, 1, 3, 5]
    cumulative_at_knots = cumulative_hazard(knots, curve_times, hazard_rates) # H at each knot, ex: [0, 0.01, 0.05, 0.11]
    inside = np.interp(target, cumulative_at_knots, knots) # H is a straight line between two knots, so read the time back from H, ex: 0.1054 -> 4.85
    beyond = np.maximum(target - cumulative_at_knots[-1], 0.0) / hazard_rates[-1] # only if target is above the last H (0.11): keep going with the last lambda, else 0

    return inside + beyond # ex: 4.85 + 

def simulate_default_times(hazard_rates, correlation, n_paths, seed=23):
    """Default times, one row per simulation and one column per name, from a one-factor Gaussian copula."""
    rng = np.random.default_rng(seed) # random number generator, same seed gives the same draws
    n_names = len(hazard_rates) # one curve per name, ex: 3 names

    common = rng.standard_normal((n_paths, 1)) # Z: one number per simulation, shared by all the names
    private = rng.standard_normal((n_paths, n_names)) # epsilon_i: one number per simulation and per name
    scores = np.sqrt(correlation) * common + np.sqrt(1 - correlation) * private # X_i = sqrt(rho) Z + sqrt(1 - rho) epsilon_i

    times = np.empty((n_paths, n_names)) # empty table, filled column by column below
    for i in range(n_names):
        times[:, i] = default_time(norm.cdf(scores[:, i]), hazard_rates[i]) # column i: score -> u -> year, with the curve of name i

    return times # Matrix (n_paths, n_names): each value = simulated default time in years, row = simulation, column = company.

def ftd_spread_monte_carlo(maturity, hazard_rates, correlation, interest_rate, recovery, frequency=4, n_paths=200000, seed=23):
    """First-to-default spread as a decimal per year: average protection payment divided by average premium annuity."""
    payment_times, year_fractions, period_starts, period_midpoints = _period_grid(maturity, frequency) # same dates as the CDS, ex: 5Y quarterly -> 20 periods
    n_periods = len(payment_times)

    first_default = simulate_default_times(hazard_rates, correlation, n_paths, seed).min(axis=1) # smallest year of each row = first default
    # ex : first_default = [1.2, 6.0, 3.4, 8.0]
    period = np.ceil(first_default * frequency).astype(int) # quarter in which it happens, ex: 4.04 years -> 17th quarter
    defaulted = period <= n_periods # False when the first default is after maturity
    # defaulted = [True, False, True, False]
    period = np.minimum(period, n_periods) # cap it, so the indexes below stay valid when nobody defaults

    ##
    premium_paid = np.concatenate(([0.0], np.cumsum(year_fractions * discount_factor(payment_times, interest_rate)))) # premiums paid up to each date (can controle the end, ex: after 16 payments 3.79 -> premium_paid[15]
    discount_at_default = discount_factor(period_midpoints[period - 1], interest_rate) # default is placed in the middle of its quarter, like in cds.py
    # discount_at_default = [0.967, 0.864, 0.903, 0.864]
    ##

    protection = np.where(defaulted, (1 - recovery) * discount_at_default, 0.0) # pays (1 - R) if default before maturity, else 0
    annuity = np.where(defaulted,
                       premium_paid[period - 1] + 0.5 * year_fractions[period - 1] * discount_at_default, # premiums before the default quarter + half a quarter of accrued
                       premium_paid[n_periods]) # no default: all the premiums are paid

    return protection.mean() / annuity.mean() # spread = average protection / average annuity