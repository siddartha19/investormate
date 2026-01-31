# Backtesting Framework

Test trading strategies on historical data with comprehensive performance metrics.

## Overview

The backtesting framework allows you to:
- Define custom strategies using the Strategy base class
- Run strategies on historical data
- Track positions, cash, and equity
- Calculate performance metrics (returns, Sharpe, drawdown, win rate)
- Generate equity curves and trade logs

## Quick Start

```python
from investormate import Backtest, Strategy

class RSIStrategy(Strategy):
    def initialize(self):
        self.rsi_period = 14
        self.buy_threshold = 30
        self.sell_threshold = 70

    def on_data(self, data):
        rsi = data.indicators.rsi(self.rsi_period).iloc[-1]
        if rsi < self.buy_threshold and not self.has_position:
            self.buy(percent=1.0)
        elif rsi > self.sell_threshold and self.has_position:
            self.sell_all()

bt = Backtest(
    strategy=RSIStrategy,
    ticker="AAPL",
    start_date="2020-01-01",
    end_date="2024-01-01",
    initial_capital=10000,
    commission=0.001
)

results = bt.run()
print(results.summary())
print(f"Total Return: {results.total_return}%")
print(f"Sharpe Ratio: {results.sharpe_ratio}")
print(f"Max Drawdown: {results.max_drawdown}%")
```

## API Reference

### Strategy (Base Class)

Abstract class with:
- `initialize()` - Set up parameters (called once)
- `on_data(data)` - Called for each bar
- `buy(shares=None, percent=None)` - Buy shares
- `sell(shares=None, percent=None)` - Sell shares
- `sell_all()` - Close position
- `has_position`, `position_size`, `cash`, `equity` - Position info

### Backtest

**Constructor:**
- `strategy` - Strategy class (not instance)
- `ticker` - Stock symbol
- `start_date`, `end_date` - Date range (YYYY-MM-DD)
- `initial_capital` - Starting capital (default: 10000)
- `commission` - Commission rate (default: 0.0)

**Methods:**
- `run()` - Execute backtest, returns BacktestResults

### BacktestResults

**Properties:**
- `total_return` - Total return %
- `cagr` - Compound annual growth rate
- `sharpe_ratio` - Risk-adjusted return
- `max_drawdown` - Maximum drawdown %
- `volatility` - Annual volatility
- `total_trades` - Number of trades
- `win_rate` - Winning trades %
- `equity_curve` - DataFrame with equity over time
- `trades` - DataFrame with trade log

**Methods:**
- `summary()` - Formatted performance summary

## Examples

See `examples/backtesting_rsi.py` for a complete RSI strategy example.
