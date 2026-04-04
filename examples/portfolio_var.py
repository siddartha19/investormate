"""
Portfolio VaR (historical / parametric) and Monte Carlo terminal value simulation.

Requires network access (yfinance).
"""

from investormate import Portfolio


def main():
    portfolio = Portfolio({"AAPL": 5, "MSFT": 3, "GOOGL": 1})
    print(f"Portfolio value: ${portfolio.value:,.2f}")

    v95 = portfolio.var(confidence=0.95, method="historical")
    vp = portfolio.var(confidence=0.95, method="parametric")
    print(f"95% historical VaR (daily return quantile): {v95}")
    print(f"95% parametric VaR (Gaussian):            {vp}")

    mc = portfolio.monte_carlo_simulation(n=800, horizon=126, seed=42)
    if mc:
        print("\nMonte Carlo (bootstrap daily returns):")
        for k in ("mean_final", "median_final", "percentile_5", "percentile_95"):
            print(f"  {k}: {mc[k]:,.2f}")


if __name__ == "__main__":
    main()
