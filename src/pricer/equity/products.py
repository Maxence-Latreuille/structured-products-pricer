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



def phoenix_cashflows(paths, S0, coupon, autocall_barrier=1.0, coupon_barrier=0.7,
                      protection_barrier=0.6, nominal=1000):
    """Cash flows of an autocall Phoenix with memory coupon.

    paths has shape (n_paths, n_dates): index levels at each observation date.
    Returns an array of the same shape: what the client receives at each date.
    Barriers are expressed as a fraction of S0 (1.0 = 100%).
    """
    perf = paths / S0
    n_paths, n_dates = perf.shape
    flows = np.zeros((n_paths, n_dates))
    alive = np.ones(n_paths, dtype=bool) # Is the product still alive
    memory = np.zeros(n_paths)

    for i in range(n_dates):
        p = perf[:, i]

        # Coupon of the year is owed; pay everything owed if above the coupon barrier
        memory[alive] += coupon * nominal
        pays = alive & (p >= coupon_barrier)
        flows[pays, i] += memory[pays]
        memory[pays] = 0.0
        
        if i < n_dates - 1:
            # Early redemption (autocall)
            called = alive & (p >= autocall_barrier)
            flows[called, i] += nominal
            alive[called] = False
        else:
            # Maturity: capital protected above the protection barrier
            redemption = np.where(p >= protection_barrier, nominal, nominal * p)
            flows[alive, i] += redemption[alive]

    return flows