from pricer.equity.analytics import bs_call
from pricer.equity.monte_carlo import mc_call

def test_mc_call():
    params = dict(S0=100, K=100, T=1, r=0.03, sigma=0.2)
    exact = bs_call(**params)
    price, std_err = mc_call(**params)
    assert abs(price-exact) < 3*std_err # 3*std_err : 99.7% chance the price is within 3 SEM of the exact value