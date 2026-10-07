import numpy as np
from scipy.stats import norm

def bs_call(S0, K, T, r, sigma):
    """Black-Scholes price of a European call option."""
    d1 = (np.log(S0/K) + (r + sigma**2 / 2) * T)/(sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    # S0*N(d1): value of receiving the stock
    # K*exp(-rT)*N(d2): value of paying the strike
    return S0*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

def bs_put(S0, K, T, r, sigma):
    """Black-Scholes price of a European put option."""
    d1 = (np.log(S0/K) + (r + sigma**2 / 2) * T)/(sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    # K*exp(-rT)*N(-d2): cash lent; S0*N(-d1): shares sold short
    return K*np.exp(-r*T)*norm.cdf(-d2) - S0*norm.cdf(-d1)

def implied_volatility(price, S0, K, T, r, option_type="call"):
    """Compute implied volatility from option price using bisection method."""
    tol = 1e-6
    max_iter = 100
    low, high = 1e-5, 5.0  # reasonable bounds for volatility (0.001% to 500%)

    for _ in range(max_iter):
        mid = (low + high) / 2
        if option_type == "call":
            price_mid = bs_call(S0, K, T, r, mid)
        else:
            price_mid = bs_put(S0, K, T, r, mid)

        if abs(price_mid - price) < tol:
            return mid
        elif price_mid < price:
            low = mid
        else:
            high = mid

    raise ValueError("Implied volatility not found within bounds.")

def reverse_convertible_price(S0, K, T, r, sigma, coupon, nominal=1000.0):
    """Closed form: bond paying nominal*(1+coupon) minus nominal/K puts sold by the client."""
    bond = nominal*(1+coupon)*np.exp(-r*T)
    n_puts = nominal/K
    return bond - n_puts*bs_put(S0, K, T, r, sigma)

def reverse_convertible_coupon(S0, K, T, r, sigma, target=1000.0, nominal=1000.0):
    """Coupon that makes the note worth `target` (target = nominal means at par)."""
    n_puts = nominal / K
    return ((target + n_puts*bs_put(S0, K, T, r, sigma))*np.exp(r*T)/nominal -1)