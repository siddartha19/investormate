# Data Providers

InvestorMate fetches all market and fundamental data through a pluggable
**`DataProvider`** layer. By default it uses **`YFinanceProvider`**, which wraps
yfinance with the built-in TTL cache and rate limiter. You can swap in a
different source process-wide — useful for alternate data APIs, offline testing
with recorded fixtures, or deterministic unit tests.

## How it works

Every consumer (`Stock`, `Portfolio`, `Screener`, `Market`, `Valuation`,
`EarningsAnalyzer`, `Investor`) calls `get_data_provider()` instead of talking to
yfinance directly. Swapping the active provider redirects all of them at once.

```python
from investormate import get_data_provider, set_data_provider, reset_data_provider

provider = get_data_provider()        # YFinanceProvider by default
print(provider.name)                  # "YFinanceProvider"
```

## Writing a custom provider

Implement the `DataProvider` interface for full control:

```python
from investormate import DataProvider, set_data_provider
import pandas as pd

class MyProvider(DataProvider):
    def get_info(self, ticker):
        return {"symbol": ticker, "currentPrice": 100.0}

    def get_history(self, ticker, period="1y", interval="1d",
                    auto_adjust=True, return_trace=False):
        data = {"2024-01-02": {"Open": 1, "High": 2, "Low": 1,
                               "Close": 1.5, "Volume": 10}}
        return (data, {"provider": "mine"}) if return_trace else data

    # ... implement the remaining abstract methods ...

set_data_provider(MyProvider())
```

If you only need to override a few methods, subclass `YFinanceProvider` and
inherit the rest:

```python
from investormate import YFinanceProvider, set_data_provider

class CachedInfoProvider(YFinanceProvider):
    def get_info(self, ticker):
        # custom logic, then fall back to yfinance for everything else
        return {"symbol": ticker, "currentPrice": 42.0}

set_data_provider(CachedInfoProvider())
```

Restore the default at any time:

```python
reset_data_provider()
```

## Provider interface

`DataProvider` requires the following methods (all take a ticker symbol unless
noted). `YFinanceProvider` implements every one by delegating to the cached
`get_yfinance_*` fetchers:

| Method | Returns |
| --- | --- |
| `get_info(ticker)` | quote/company info dict |
| `get_balance_sheet(ticker)` | `{period: {line_item: value}}` |
| `get_income_statement(ticker)` | `{period: {line_item: value}}` |
| `get_cash_flow(ticker)` | `{period: {line_item: value}}` |
| `get_calendar(ticker)` | earnings/ex-dividend calendar |
| `get_earnings_estimate(ticker)` | estimate table or `None` |
| `get_earnings_history(ticker)` | history table or `None` |
| `get_revenue_estimate(ticker)` | estimate table or `None` |
| `get_eps_trend(ticker)` | EPS trend or `None` |
| `get_eps_revisions(ticker)` | EPS revisions or `None` |
| `get_growth_estimates(ticker)` | growth estimates or `None` |
| `get_history(ticker, period, interval, auto_adjust, return_trace)` | OHLCV dict (or `(dict, trace)`) |
| `get_dividends(ticker)` | `pandas.Series` |
| `get_news(ticker)` | list of news items |
| `get_filings(ticker)` | list of filings |
| `get_market_summary(market)` | summary dict for a `MARKET_*` key |

## Testing with a provider

Because the seam is a single swap point, tests can patch one method on the
default provider:

```python
from unittest.mock import patch

@patch("investormate.data.providers.YFinanceProvider.get_info")
def test_price(mock_info):
    mock_info.return_value = {"currentPrice": 123.0}
    from investormate import Stock
    assert Stock("AAPL").price == 123.0
```

> Note: providers receive ticker symbols as the caller supplies them.
> `YFinanceProvider` applies yfinance-specific formatting internally.
