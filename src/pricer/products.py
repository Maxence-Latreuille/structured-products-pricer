import numpy as np

def call_payoff(ST, K):
    """Calculate the payoff of a European call option."""
    return np.maximum(ST - K, 0)

def put_payoff(ST, K):
    """Calculate the payoff of a European put option."""
    return np.maximum(K - ST, 0)

def reverse_convertible_payoff(ST, K, coupon, nominal): # ST is an array of possible stock value with Monte Carlo simulation
    """Coupon always paid; nominal repaid if S_T >= K, otherwise nominal/K shares."""
    n_shares = nominal/K
    redemption = np.where(ST>=K, nominal, n_shares*ST) # can't use if because ST isn't a number, it's an array
    return redemption + nominal*coupon