import numpy as np

def gbm_paths_from_shocks(S0, r, sigma, obs_times, Z):
    """Build GBM paths at the observation dates from given standard normal shocks.

    Z has shape (n_paths, n_dates). Returns levels with the same shape:
    one row per scenario, one column per observation date.
    """
    obs_times = np.asarray(obs_times, dtype=float)
    dt = np.diff(obs_times, prepend=0) # prepend for having the first obs date in the list
    # Compute the log-returns for each time step using the GBM formula
    log_increments = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt)*Z
    return S0*np.exp(np.cumsum(log_increments, axis=1))

def simulate_gbm_paths(S0, r, sigma, obs_times, n_paths=100_000, seed=23):
    """Simulate risk-neutral GBM paths at the observation dates (in years)."""
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((n_paths, len(obs_times))) # generates the n_paths * len(obs_times) matrix of Z
    return gbm_paths_from_shocks(S0, r, sigma, obs_times, Z)