"""CAPM regression example. Run: python examples/capm_regression.py"""

from investormate import Stock


def main():
    stock = Stock("AAPL")
    result = stock.capm.capm(benchmark="SPY", period="2y")
    print(f"Beta: {result['beta']:.3f}")
    print(f"Alpha (annual): {result['alpha_annual']*100:.2f}%")
    print(f"R-squared: {result['r_squared']:.3f}")

    risk = stock.capm.risk_decomposition()
    print(f"Systematic risk: {risk.get('systematic_pct', 0)*100:.1f}%")


if __name__ == "__main__":
    main()
