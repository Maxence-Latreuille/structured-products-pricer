from pricer.credit.cds import risky_annuity, protection_leg, survival_probability, discount_factor


def cln_value(coupon, maturity, hazard_rate, interest_rate, recovery, frequency=4):
    """Present value of a CLN per unit notional: coupons while alive, principal if alive at maturity, recovery on default."""
    coupons = coupon * risky_annuity(maturity, hazard_rate, interest_rate, frequency, include_accrued=False) # no accrued coupon on default
    principal = discount_factor(maturity, interest_rate) * survival_probability(maturity, hazard_rate) # D(T) x Q(T)
    recovery_at_default = recovery * 1/(1-recovery) * protection_leg(maturity, hazard_rate, interest_rate, recovery, frequency) # R x sum of D(m_i) x P(default in period i)

    return coupons + principal + recovery_at_default

def cln_par_coupon(maturity, hazard_rate, interest_rate, recovery, frequency=4):
    """Coupon, as a decimal per year, that makes the CLN worth par (1 per unit notional)."""
    value_without_coupon = cln_value(0.0, maturity, hazard_rate, interest_rate, recovery, frequency) # principal + recovery
    RPV_01 = risky_annuity(maturity, hazard_rate, interest_rate, frequency, include_accrued=False) # what 1 unit of coupon is worth

    return (1 - value_without_coupon)/RPV_01 # value is linear in the coupon, so no solver is needed
