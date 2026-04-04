# Strategy templates

Three ready-to-run subclasses of :class:`~investormate.backtest.strategy.Strategy` work with
:class:`~investormate.backtest.engine.BacktestEngine` and :class:`~investormate.backtest.backtest.Backtest`.

## Imports

```python
from investormate import (
    MomentumStrategy,
    MeanReversionStrategy,
    SMACrossoverStrategy,
    Backtest,
)
```

## MomentumStrategy

- **Idea:** Long when trailing ``lookback``-day total return is positive; exit when negative.
- **Default** ``lookback``: 126 (~6 months of trading days).
- **Custom params:** subclass and call ``super().__init__(lookback=...)`` in ``__init__``.

## MeanReversionStrategy

- **Idea:** Buy when RSI &lt; ``oversold`` (default 30); sell when RSI &gt; ``overbought`` (default 70).
- **Defaults:** ``rsi_period=14``.

## SMACrossoverStrategy

- **Idea:** Buy on bullish crossover of fast vs slow SMA; sell on bearish crossover.
- **Defaults:** fast 50, slow 200 (requires enough history in the backtest window).

## Example

```python
from investormate import Backtest, SMACrossoverStrategy

bt = Backtest(
    strategy=SMACrossoverStrategy,
    ticker="MSFT",
    start_date="2020-01-01",
    end_date="2023-01-01",
    initial_capital=10_000,
)
print(bt.run().summary())
```

## Engine caveat

The default engine constructs a full :class:`~investormate.core.stock.Stock` each bar; indicators and history are not strictly point-in-time. Use these templates for **sanity checks** and learning; serious research should export signals to vectorbt/zipline as described in the roadmap.
