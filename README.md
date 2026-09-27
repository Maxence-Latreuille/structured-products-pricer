# Structured Products Pricer

Pricing and structuring toolkit for equity structured products, built to reproduce
the workflow of a structuring desk: design the payoff, solve for the coupon,
analyse risks, and generate a client-ready term sheet.

**[Live demo](lien-streamlit)** · **[Notebook walkthrough](notebooks/autocall_walkthrough.ipynb)**

![demo](docs/demo.gif)

## Products
| Product | Features |
|---|---|
| Reverse Convertible | Closed-form (BS) + Monte Carlo validation |
| Autocall Phoenix | Autocall, memory coupon & capital-protection barriers |
| Worst-of Autocall | Multi-asset, correlated GBM (Cholesky) |
| Capital-Protected Note | Zero-coupon + call participation |

## Features
- Monte Carlo pricing engine (vectorised NumPy, antithetic variates)
- **Coupon solver**: finds the coupon that prices the note at par (100%)
- Greeks (delta, gamma, vega, correlation sensitivity) via bumping with common random numbers
- Market data retrieval (yfinance) and automatic PDF term sheet
- Interactive Streamlit app

## Key results
- Coupon vs. autocall barrier / protection barrier
- Worst-of: coupon increases as correlation decreases
- Delta and gamma behaviour near the barrier at maturity

## Project structure
    src/pricer/     models, payoffs, monte_carlo, greeks, solver
    app/            Streamlit interface
    notebooks/      walkthrough and analysis
    tests/          pytest (MC vs closed-form checks)

## Quickstart
    pip install -r requirements.txt
    streamlit run app/main.py

## Roadmap
- [ ] Local volatility / skew impact on autocall pricing
- [ ] Issuer credit spread and funding in the pricing

## Author
Maxence Latreuille, École Centrale de Lyon × emlyon business school
