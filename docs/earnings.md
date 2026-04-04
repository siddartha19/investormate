# Earnings and estimates

`Stock.earnings` exposes an `EarningsAnalyzer` backed by Yahoo Finance / yfinance. Availability and field names vary by symbol and Yahoo’s API.

## API

```python
from investormate import Stock

stock = Stock("AAPL")
e = stock.earnings

e.calendar()           # calendar table + earnings timestamps from quote summary
e.estimates()          # earnings + revenue estimate tables
e.surprise_history()   # list of dicts: eps actual, estimate, surprise %
e.eps_trend()          # EPS revision trend (7d / 30d / …) or None
e.eps_revisions()      # revision counts or None
e.growth_estimates()   # growth vs sector/industry or None
```

## Data source and limitations

- Data is **not** audited; treat as indicative.
- Many tickers return empty or partial tables.
- This is **not** a replacement for vendor earnings calendars or SEC filings.

## Cache

Earnings-related fetchers use the same TTL cache as other yfinance calls (see [caching.md](caching.md)). Call `stock.refresh()` to invalidate cached data for that ticker.
