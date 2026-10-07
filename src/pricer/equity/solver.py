from pricer.common.solver import solve_coupon
from pricer.equity.monte_carlo import price_phoenix


def phoenix_par_coupon(S0, r, sigma, obs_times, target=1000.0,
                       n_paths=100_000, seed=23, **terms):
    """Coupon that makes the autocall Phoenix worth `target` (same paths for every trial coupon)."""
    def value(c):
        return price_phoenix(S0, r, sigma, obs_times, coupon=c,
                             n_paths=n_paths, seed=seed, **terms)[0]
    
    return solve_coupon(value, target)