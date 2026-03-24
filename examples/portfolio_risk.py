"""
Portfolio risk metrics: Sortino, Calmar, max drawdown, beta vs SPY.

Requires network access to fetch prices from yfinance.
"""

from investormate import Portfolio


def main():
    portfolio = Portfolio(
        {
            "AAPL": 10,
            "MSFT": 5,
            "GOOGL": 2,
        }
    )
    print(f"Portfolio: {portfolio}")
    print(f"Sharpe ratio: {portfolio.sharpe_ratio}")
    print(f"Sortino ratio: {portfolio.sortino_ratio}")
    print(f"Max drawdown (%): {portfolio.max_drawdown}")
    print(f"Calmar ratio: {portfolio.calmar_ratio}")
    print(f"Beta vs SPY: {portfolio.beta('SPY')}")
    dd = portfolio.drawdown_series()
    if dd is not None:
        print(f"Latest drawdown vs peak: {dd.iloc[-1]:.4f}")


if __name__ == "__main__":
    main()
