# Custom Strategies

User-defined stock screening logic with function-based and builder pattern APIs.

## Overview

CustomStrategy enables you to:
- Define custom filter functions
- Rank stocks by custom metrics
- Use builder pattern for common criteria
- Screen any universe of stocks

## Quick Start

### Function-Based

```python
from investormate import CustomStrategy

def my_filter(stock):
    return (
        10 < stock.ratios.pe < 25 and
        stock.ratios.roe > 0.15
    )

def my_rank(stock):
    return stock.ratios.roe * stock.ratios.revenue_growth

strategy = CustomStrategy(
    filter_func=my_filter,
    rank_func=my_rank,
    universe=["AAPL", "GOOGL", "MSFT"]
)

results = strategy.run()
for r in results:
    print(f"{r['ticker']}: {r['rank']:.2f}")
```

### Builder Pattern

```python
strategy = (
    CustomStrategy()
    .add_filter("ratios.pe", min=10, max=25)
    .add_filter("ratios.roe", min=0.15)
    .rank_by("ratios.roe")
    .apply(universe=["AAPL", "GOOGL", "MSFT"])
)

results = strategy.run(limit=10)
```

## API Reference

### CustomStrategy

**Constructor:**
- `filter_func` - Function(Stock) -> bool
- `rank_func` - Function(Stock) -> float (higher = better)
- `universe` - List of ticker symbols

**Builder Methods:**
- `add_filter(attribute, min=None, max=None)` - Add filter criterion
- `rank_by(criteria, ascending=False)` - Add ranking
- `apply(universe)` - Set universe

**Methods:**
- `run(limit=None)` - Execute screening, returns list of dicts

**Result format:**
- `ticker` - Stock symbol
- `rank` - Ranking score
- `name` - Company name
- `price` - Current price

## Examples

See `examples/custom_screening.py` for value, growth, dividend, and quality screening examples.
