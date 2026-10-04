from scipy.optimize import brentq

from pricer.monte_carlo import price_phoenix


def solve_coupon(value_fn, target, low=0.0, high=1.0):
    """Find the coupon c such that value_fn(c) == target.

    Works for any product whose value increases with the coupon.
    """
    def pricing_error(c):
        return value_fn(c) - target

    return brentq(pricing_error, low, high)


def phoenix_par_coupon(S0, r, sigma, obs_times, target=1000.0,
                       n_paths=100_000, seed=23, **terms):
    """Coupon that makes the autocall Phoenix worth `target` (same paths for every trial coupon)."""
    def value(c):
        return price_phoenix(S0, r, sigma, obs_times, coupon=c,
                             n_paths=n_paths, seed=seed, **terms)[0]
    
    return solve_coupon(value, target)