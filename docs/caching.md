# Caching and rate limiting

InvestorMate caches yfinance-backed responses in memory with per-category TTLs and a token-bucket rate limiter to reduce duplicate calls and avoid hammering Yahoo Finance.

## Defaults

| Category    | TTL   | Examples                                      |
|------------|-------|-----------------------------------------------|
| Quotes/info | 60s  | `get_yfinance_data`, history                  |
| Financials | 3600s | Balance sheet, income, cash flow               |
| News       | 300s  | `stock.news`                                  |
| Filings    | 360s  | SEC filings list                              |
| Earnings   | 3600s | Estimates, EPS trend, growth estimates        |
| Market     | 300s  | `Market` summaries                            |

Rate limiter: **2 requests/second** by default (token bucket).

## Configuration

```python
from investormate.data.cache import configure_data_cache

configure_data_cache(
    enabled=True,              # set False to skip cache (still rate-limits)
    default_ttl=300,          # default for TTLCache.default_ttl
    calls_per_second=10.0,    # increase for batch jobs; 0 disables spacing
)
```

## Refreshing data

```python
from investormate import Stock

stock = Stock("AAPL")
stock.refresh()  # Clears Stock instance caches + invalidates fetch cache for this ticker
```

To clear everything:

```python
from investormate.data.cache import get_data_cache

get_data_cache().clear()
```

## Thread safety

The cache and rate limiter use locks and are safe for concurrent reads/writes from multiple threads in one process.
