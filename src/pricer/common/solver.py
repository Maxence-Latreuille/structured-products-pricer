from scipy.optimize import brentq


def solve_coupon(value_fn, target, low=0.0, high=1.0):
    """Find the coupon c such that value_fn(c) == target.

    Works for any product whose value increases with the coupon.
    """
    def pricing_error(c):
        return value_fn(c) - target

    return brentq(pricing_error, low, high)
