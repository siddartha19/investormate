# Data Policy

This document describes how InvestorMate handles price data, missing values, and adjustments. It is intended for users building systematic strategies or backtests, where silent data issues can invalidate results.

## Price adjustment (splits and dividends)

- **Default behavior:** Historical price data from `Stock.history()` and the backtest engine uses **dividend- and split-adjusted** prices (yfinance default). This is the appropriate choice for return calculations and backtesting.
- **Raw prices:** You can request unadjusted prices by passing `adjusted=False` to `Stock.history(..., adjusted=False)`. The underlying fetcher and backtest engine also support this parameter. Use raw prices only when you need to replicate exchange-reported figures or handle adjustments yourself.
- **Single policy:** The same adjustment semantics apply across all endpoints that return OHLCV data (history fetcher, Stock, BacktestEngine).

## NaN and missing data

- **No forward-fill:** InvestorMate does **not** silently forward-fill missing values. Missing or invalid data in the source are left as NaN (in DataFrames) or None (in dict output). This avoids the common pitfall where delisted or stale tickers appear to have “clean” series and produce misleading backtest results.
- **Propagation:** When the data provider returns gaps or nulls, they are preserved. Ratios and indicators that depend on missing inputs will reflect that (e.g. NaN or omitted) rather than being filled implicitly.
- **Future work:** A strict mode that errors or flags when critical columns (e.g. Close) contain NaN may be added in a later release (see ROADMAP Phase 1.4).

## Delisted and missing data

- **Current behavior:** If no data is available (e.g. invalid ticker, delisted, or out-of-range), the history fetcher returns an empty dict; `Stock.history()` returns an empty DataFrame or raises if used in a context that requires data. We do not fabricate or fill with stale values.
- **Future work:** Explicit handling of delisted names and optional strict mode are planned (ROADMAP Phase 1.4).

## Data provenance (source trace)

When you need to verify where data came from and what transforms were applied:

- Use **`Stock.history(..., source_trace=True)`**. The return value is then an object with:
  - **`.data`** — the same OHLCV DataFrame as when `source_trace=False`.
  - **`.trace`** — a dict with `provider`, `transform_steps`, and optional `raw_shape` (or similar) so you can confirm the source and processing steps without logging raw payloads.

See the API reference for `Stock.history` and the [ROADMAP](ROADMAP.md) Phase 1.3 for the debug/source-trace feature.
