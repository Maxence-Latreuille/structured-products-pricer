# Structured Products Pricer

Pricing and structuring toolkit for equity structured products, built to reproduce
the workflow of a structuring desk: design the payoff, solve for the coupon,
analyse risks, and generate a client-ready term sheet.

> 🚧 **Status: work in progress.** Built step by step; see the roadmap below.

## Products
| Product | Method | Status |
|---|---|---|
| European call & put | Black-Scholes closed form, Monte Carlo, put-call parity | ✅ Done |
| Reverse Convertible | Closed form (zero-coupon − put) + Monte Carlo validation | ✅ Done |
| Autocall Phoenix | Autocall, memory coupon & capital-protection barriers | 🚧 In progress |
| Worst-of Autocall | Multi-asset correlated GBM (Cholesky) | 📅 Planned |
| Capital-Protected Note | Zero-coupon + call participation | 📅 Planned |

## Roadmap
- [x] Monte Carlo engine validated against Black-Scholes
- [x] Reverse Convertible: Monte Carlo vs closed-form check
- [x] Autocall Phoenix + **coupon solver** (coupon that prices the note at par)
- [ ] Greeks (delta, gamma, vega) with common random numbers
- [ ] Interactive Streamlit app (live demo)
- [ ] Worst-of on 3 underlyings, correlation impact on the coupon
- [ ] Market data (yfinance) and PDF term sheet generation
- [ ] Skew / local volatility impact on autocall pricing

## Project structure
    src/pricer/     analytics (closed forms), monte_carlo, products, greeks, solver
    tests/          pytest: Monte Carlo vs closed-form checks
    notebooks/      walkthrough and analysis (coming)
    app/            Streamlit interface (coming)

## Quickstart
    pip install -r requirements.txt
    pytest -v

## Author
Maxence Latreuille, École Centrale de Lyon × emlyon business school