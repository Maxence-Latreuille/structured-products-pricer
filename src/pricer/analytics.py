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
