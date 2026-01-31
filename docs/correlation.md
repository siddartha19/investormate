# Correlation Analysis

Multi-stock correlation analysis for portfolio diversification.

## Overview

The Correlation class helps you:
- Calculate correlation matrices for multiple stocks
- Find highly correlated stock pairs
- Identify diversification candidates
- Analyze portfolio risk through correlation

## Quick Start

```python
from investormate import Correlation

corr = Correlation(["AAPL", "GOOGL", "MSFT"], period="1y")

# Correlation matrix
matrix = corr.matrix()

# Find correlated pairs (>0.7)
pairs = corr.find_pairs(threshold=0.7)

# Find diversification candidates
candidates = corr.find_diversification_candidates(
    portfolio=["AAPL", "GOOGL"],
    universe=["GLD", "TLT"],
    max_correlation=0.3
)
```

## API Reference

### Correlation

**Constructor:**
- `tickers` - List of stock symbols (min 2)
- `period` - Time period (default: "1y")
- `interval` - Data interval (default: "1d")

**Methods:**
- `matrix(method='pearson')` - Correlation matrix (pearson/spearman/kendall)
- `find_pairs(threshold=0.7)` - Find highly correlated pairs
- `find_diversification_candidates(portfolio, universe, max_correlation=0.3)` - Find low-correlation assets
- `get_statistics()` - Summary statistics

## Examples

See `examples/correlation_analysis.py` for comprehensive examples.
