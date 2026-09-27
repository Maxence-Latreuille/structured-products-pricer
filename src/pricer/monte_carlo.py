import numpy as np

def mc_call(S0, K, T, r, sigma, n_paths=100_000, seed=23):
    """Monte Carlo price of a European call, with its standard error."""
    rng = np.random.default_rng(seed) # on fixe une seed
    Z = rng.standard_normal(n_paths) # tirages de n_paths v.a normales centrées réduites
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    payoffs = np.exp(-r*T) * np.maximum(ST - K, 0)
    return payoffs.mean(), payoffs.std(ddof=1) / np.sqrt(n_paths) # ddof pour le n-1 et pas n : sem = sqrt(1/(n-1) * sum((x_i - x_bar)^2))/sqrt(n)

def mc_put(S0, K, T, r, sigma, n_paths=100_000, seed=23):
    """Monte Carlo price of a European put, with its standard error."""
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_paths)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    payoffs = np.exp(-r*T) * np.maximum(K - ST, 0)
    return payoffs.mean(), payoffs.std(ddof=1) / np.sqrt(n_paths)
