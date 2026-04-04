"""
Built-in strategy templates: momentum, RSI mean reversion, SMA crossover.

Requires network access (BacktestEngine fetches OHLCV via yfinance).
"""

from investormate import (
    Backtest,
    MomentumStrategy,
    MeanReversionStrategy,
    SMACrossoverStrategy,
)


def main():
    for name, Strat in [
        ("Momentum (126d)", MomentumStrategy),
        ("Mean reversion (RSI)", MeanReversionStrategy),
        ("SMA 50/200", SMACrossoverStrategy),
    ]:
        bt = Backtest(
            strategy=Strat,
            ticker="AAPL",
            start_date="2022-01-01",
            end_date="2024-01-01",
            initial_capital=10_000,
        )
        res = bt.run()
        print(f"\n{name}:")
        print(res.summary())


if __name__ == "__main__":
    main()
