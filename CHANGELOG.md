# Changelog

All notable changes to InvestorMate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-08-03

### Added — Terminal CLI
- **Console entry point** `investormate` via `[project.scripts]` and `python -m investormate` (`investormate/cli.py`, `investormate/__main__.py`).
- **`investormate quote TICKER`** — keyless live price snapshot (price, previous close, change, day range, volume, market cap). Missing fields render as `N/A`.
- **`investormate analyze TICKER`** — fast fundamentals snapshot (quote + sector/industry + key ratios from info). Does not fetch financial statements, run AI/DCF, or load indicators.
- **`--json`** on both commands — one stable snake_case JSON object on stdout; diagnostics stay on stderr.
- **Actionable errors** — invalid tickers and provider failures print problem / cause / fix with exit codes `2` (usage) and `1` (data).
- **Tests**: `tests/test_cli.py` (mocked data provider, no live network).

### Changed
- README and `docs/quickstart.md` lead with the keyless CLI path; AI install examples use `investormate[ai]`.
- Version bumped to `0.6.0`.

### Deferred (not in 0.6.0)
- `investormate ask` / interactive AI chat (needs `[ai]` and API keys).
- `investormate dashboard` / local web UI (planned optional `[dashboard]` extra).
- `investormate doctor` environment checks.

## [0.5.0] - 2026-06-17

### Added — Student Edition (Phase 1.5)
- **TVM module** (`investormate.finance.tvm`): `present_value`, `future_value`, `annuity_pv`/`annuity_fv`, `perpetuity`, `npv`, `irr`, `amortization_schedule`, `ear`. Pure numpy/pandas — no API keys.
- **Fixed income** (`investormate.finance.bonds`): `Bond` class with `price`, `solve_ytm`, `current_yield`, `accrued_interest`, `macaulay_duration`, `modified_duration`, `convexity`, `price_change`; `bond_ladder()` helper.
- **Derivatives basics** (`investormate.finance.options`): `black_scholes`, `greeks`, `put_call_parity`, `binomial`, `payoff_diagram`, `strategy_metrics`.
- **Financial statement analysis** (`stock.financials`): `common_size`, `horizontal`, `vertical`, `trend`, `cash_flow_quality`, `to_csv`.
- **CAPM & factor models** (`stock.capm`): `capm`, `jensen_alpha`, `risk_decomposition`, `factor_model` (user-supplied FF factors).
- **Educational layer** on `stock.ratios`: `explain()`, `show_work()`, `interpret()`, `cfa_topic()`, `red_flags()`, `percentile()`, `dupont_breakdown()`.
- **AI tutoring** on `Investor`: `ask_concept()`, `explain_ratios()`.
- **Practice problems** (`investormate.education.practice.generate`): randomized TVM, bond, and options problems with worked solutions.
- **Coursework export**: `stock.report(format="markdown")`, `stock.to_excel()` (optional `[export]` extra with `openpyxl`).
- **Tests**: `test_tvm`, `test_bonds`, `test_options`, `test_financials`, `test_capm`, `test_education`, `test_practice`, `test_export`.
- **Docs**: `docs/tvm.md`, `docs/fixed_income.md`, `docs/derivatives.md`, `docs/financial_statements.md`, `docs/capm.md`, `docs/educational_layer.md`.
- **Examples**: `tvm_basics.py`, `bond_pricing.py`, `black_scholes.py`, `statement_analysis.py`, `capm_regression.py`, `explain_ratios.py`.

### Changed
- Top-level exports expanded for academic finance and education APIs.
- `pyproject.toml`: new optional `[export]` extra (`openpyxl`).

## [0.4.0] - 2026-05-30

### Added
- **OpenRouter AI provider** (`investormate.ai.openrouter_provider.OpenRouterProvider`): one API key for hundreds of models (OpenAI, Anthropic, Google, Meta, Mistral, …) via OpenRouter's OpenAI-compatible gateway. Enable with `Investor(openrouter_api_key="sk-or-...", openrouter_model="anthropic/claude-3.5-sonnet")`. Supports optional `site_url`/`site_name` ranking headers and reuses the existing `openai` dependency (no new package). See `docs/ai_providers.md`.
- **Pluggable data sources** (`investormate.data.providers`): new `DataProvider` interface with a default `YFinanceProvider`. Swap the active source process-wide via `set_data_provider()` / `reset_data_provider()` (exported from the top-level package). All consumers (`Stock`, `Portfolio`, `Screener`, `Market`, `Valuation`, `EarningsAnalyzer`, `Investor`) now route data access through the active provider, so alternate APIs, recorded fixtures, or test doubles can be dropped in without touching call sites. See `docs/data_providers.md`.
- **Centralized logging** (`investormate.utils.logging`): package logger with a `NullHandler` so the library is silent by default and fully controllable by consumers. Diagnostic `print()` calls in `Investor`, `Correlation`, `CustomStrategy`, and the backtest engine now use `logging`.
- **SSRF protection** (`investormate.utils.net`): `assert_safe_url()` / `is_safe_public_url()` block non-HTTP(S) schemes and hosts resolving to private, loopback, link-local, reserved, or cloud-metadata addresses. Enforced in `Investor.analyze_document` URL fetching.
- **Configurable AI providers**: `temperature`, `max_tokens`, `timeout`, `max_retries`, and `retry_backoff` are now accepted by all providers, with exponential-backoff retries on transient errors (rate limits, timeouts, connection failures).
- **Bounded cache**: `TTLCache` now enforces a `maxsize` (default 2048) with LRU eviction to bound memory; `configure_data_cache(maxsize=...)` to tune.
- **Typing marker**: shipped `py.typed` so downstream users receive InvestorMate's type hints (PEP 561).
- **Tooling**: `mypy` config + CI step (informational), pinned `black==24.10.0`, `.pre-commit-config.yaml`, and a 60% coverage floor in CI.
- **Tests**: `test_cache_lru.py`, `test_net_safety.py`, `test_logging_util.py`, `test_investor_batch.py`, `test_data_provider.py`.

### Changed
- **Parallel AI ops**: `Investor.batch_analyze()` and `Investor.compare()` now fetch/analyze concurrently (`max_workers`), preserving input order.
- **Single-sourced version**: `pyproject.toml` reads the version dynamically from `investormate.version` (no more drift with `version.py`).
- **De-duplicated `data/fetchers.py`**: shared `_statement_to_dict` / `_rows_to_dict` / `_fetch_estimate` helpers remove ~130 lines of copy-pasted DataFrame→dict conversion (behavior unchanged).
- Development status promoted to **Beta**.

### Fixed
- Removed dead/duplicate prompt construction in `Investor.ask()` and `Investor.analyze_document()` (computed but never used).

## [0.3.0] - 2026-04-04

### Added
- **TTL cache + rate limiting (Phase 2.2)**: In-memory cache with per-category TTLs and token-bucket rate limiter for yfinance fetchers (`investormate.data.cache`). `Stock.refresh()` invalidates cached keys for the ticker. `configure_data_cache()` for tuning.
- **Earnings & estimates (Phase 2.4)**: `Stock.earnings` → `EarningsAnalyzer` with `calendar()`, `surprise_history()`, `estimates()`, `eps_trend()`, `eps_revisions()`, `growth_estimates()`. New fetcher `get_yfinance_calendar_data`.
- **Portfolio VaR & Monte Carlo (Phase 3.1)**: `Portfolio.var()`, `Portfolio.monte_carlo_simulation()`, `Portfolio.risk` → `RiskAnalyzer` (`investormate.analysis.risk`) with historical and Gaussian VaR.
- **Screens (Phase 3.2)**: `Screener.can_slim()`, `Screener.dividend_aristocrats()`; `get_yfinance_dividends()` for dividend history.
- **Strategy templates (Phase 3.5)**: `MomentumStrategy`, `MeanReversionStrategy`, `SMACrossoverStrategy` in `investormate.backtest.strategies`, re-exported from `investormate` and `investormate.backtest`.
- **Tests**: `test_cache.py`, `test_earnings.py`, `test_risk.py`, `test_screener_canslim.py`, `test_screener_dividends.py`, `test_strategies.py`.
- **Examples**: `caching.py`, `earnings_analysis.py`, `portfolio_var.py`, `can_slim.py`, `dividend_aristocrats.py`, `strategy_templates.py`.
- **Docs**: `docs/caching.md`, `docs/earnings.md`, `docs/risk.md`, `docs/strategy_templates.md`.

### Documentation
- README (v0.3.0), [docs/api_reference.md](docs/api_reference.md), [docs/index.md](docs/index.md), [docs/custom_strategies.md](docs/custom_strategies.md), [ROADMAP.md](ROADMAP.md).

## [0.2.8] - 2026-03-29

### Changed
- **Native technical indicators**: Replaced `pandas-ta` dependency with pure numpy/pandas implementations for all 20 indicators (SMA, EMA, WMA, RSI, MACD, Stochastic, CCI, Williams %R, Momentum, ROC, Bollinger Bands, ATR, Keltner Channels, Donchian Channels, OBV, A/D, ADX, VWAP, SuperTrend, Ichimoku). `pandas-ta` was removed from PyPI and caused `pip install investormate[all]` to fail with a `ResolutionImpossible` error.

### Removed
- **`pandas-ta` dependency**: Removed from `[all]` and `[ta]` extras in `pyproject.toml`. Technical indicators now work out of the box with zero optional dependencies.

### Added
- **Tests**: `test_indicators.py` — 25 tests covering all native indicator implementations.

## [0.2.7] - 2026-03-24

### Added
- **Full Beneish M-Score (Phase 2.5)**: Eight-variable Beneish (1999) model when two overlapping fiscal periods exist in balance sheet, income statement, and cash flow (`FinancialScores.beneish_m_score_detail()`). `beneish_m_score()` uses the full model when data suffices; otherwise a documented proxy. `all_scores()` includes Beneish indices and periods when available.
- **Portfolio risk metrics (Phase 3.1)**: `sortino_ratio`, `calmar_ratio`, `max_drawdown`, `beta(benchmark="SPY")`, `drawdown_series()`. Sharpe and volatility now use **value-weighted** daily returns (6-month window) for consistency.
- **Magic Formula screen (Phase 3.2)**: `Screener.magic_formula(top_n=30, min_market_cap=...)` — dual rank on ROIC (NOPAT / invested capital) and earnings yield (EBIT / EV).
- **Batch stocks (Phase 2.2)**: `Stock.batch(tickers, skip_invalid=True)` builds multiple `Stock` instances with optional skip + `UserWarning` on invalid symbols.
- **Peer comparison (Phase 3.3)**: `Stock.peers` (same sector within `MAJOR_US_TICKERS`) and `Stock.compare_with(peers=None)` for a metrics table across subject and peers.
- **Tests**: `test_scores_beneish`, `test_portfolio_metrics`, `test_screener_magic`, `test_stock_batch`, `test_peer_comparison`.
- **Examples**: `examples/magic_formula.py`, `examples/portfolio_risk.py`, `examples/peer_comparison.py`.

### Documentation
- README, ROADMAP (recent progress + current-state table), and [docs/api_reference.md](docs/api_reference.md) updated for v0.2.7 APIs.

## [0.2.6] - 2026-03-11

### Added
- **Error tests (Phase 1.1 P2)**: Tests for invalid ticker and network failure in fetchers; public API (e.g. Stock.history) behavior with invalid/missing data is now covered. `test_stock_history.py`: empty data returns empty DataFrame/HistoryResult; fetcher exception raises DataFetchError. `test_fetchers.py`: Ticker.history() raising propagates.

## [0.2.5] - 2026-02-20

### Added
- **Source trace for history (Phase 1.3)**: `Stock.history(..., source_trace=True)` returns a `HistoryResult` object with `.data` (DataFrame) and `.trace` (dict with `provider`, `transform_steps`, `raw_shape`) for data provenance. Default remains a DataFrame; no breaking changes.
- **Explicit `adjusted` parameter**: `Stock.history(..., adjusted=True|False)` and `get_yfinance_stock_history(..., auto_adjust=...)` control dividend/split-adjusted vs raw prices. `Backtest` and `BacktestEngine` accept `adjusted=True` (default) for consistent backtest data.
- **Data policy documentation**: New [docs/data_policy.md](docs/data_policy.md) describing price adjustment, NaN handling (no forward-fill), delisted/missing data, and data provenance (source_trace). Linked from README.

### Changed
- **Pytest configuration**: Coverage is no longer required by default. Run `pytest` without pytest-cov; use `pytest --cov=investormate --cov-report=term-missing` when you need coverage.
- **Dependency pinning**: yfinance constrained to `>=0.2.40,<0.3.0` for stability.

### Documentation
- Data policy (adjustment, NaN, no forward-fill) and data provenance (source_trace) documented in [docs/data_policy.md](docs/data_policy.md).

## [0.2.3] - 2026-02-06

### Added
- **DCF (issue #1)**: `stock.valuation.dcf()` now supports optional `terminal_multiple` (e.g. 15× final-year FCF) in addition to `terminal_growth`.
- **Valuation summary**: `stock.valuation.summary()` now returns `implied_upside_pct`, `implied_downside_pct`, and `fair_value_mid` vs current price.
- **Documentation**: New [docs/valuation.md](docs/valuation.md) with usage, parameters, and examples.

### Fixed
- **Mixed timezone error (issue #2)**: `Stock.history()` no longer raises `ValueError: Mixed timezones detected` when yfinance returns timestamps in mixed timezones; the index is now normalized to UTC via `pd.to_datetime(..., utc=True)`.

### Changed
- DCF `terminal_growth` is optional when `terminal_multiple` is set.

## [0.2.2] - 2026-02-06

### Added
- **Valuation module (Phase 1.2)**: New `stock.valuation` API for DCF, comparable companies, and fair value summary.
  - `stock.valuation.dcf(growth_rate, terminal_growth, years, wacc)` — Discounted Cash Flow with terminal value.
  - `stock.valuation.comps(peers=[...])` — Peer multiples (P/E, EV/EBITDA, P/S) and implied value per share.
  - `stock.valuation.summary(peers=[...])` — Combined fair value range and recommendation (undervalued/fair/overvalued).
  - `stock.valuation.sensitivity(growth_rates, wacc_rates)` — DCF sensitivity table.
- **Input validation (Phase 1.1 P1)**: Validate period/interval in Stock, Correlation, and Backtest.
  - `Stock.history()` now validates period and interval at entry (before cache lookup).
  - `Correlation` validates period and interval in `__init__` via shared validators.
  - `Backtest` validates start_date and end_date (YYYY-MM-DD format and start ≤ end); new `validate_date` and `validate_date_range` in `investormate.utils.validators`.

### Changed
- Stock: period/interval validation runs on every `history()` call for consistent errors.
- Correlation: uses `validate_period` and `validate_interval` from validators.
- Backtest: raises `ValidationError` for invalid or reversed date ranges.

## [0.2.1] - 2026-02-03

### Added
- **Tests for fetcher null safety**: New `tests/test_fetchers.py` with 11 tests ensuring all fetchers return empty dict/list when yfinance returns None or empty data.

### Changed
- **Data fetcher null safety (Phase 1.1 P0)**: All yfinance fetchers now handle `None` and empty data safely. `get_yfinance_data` returns an empty dict when info is missing; balance sheet, income statement, and cash flow return empty dict for null/empty DataFrames; `get_yfinance_stock_history` returns empty dict instead of raising when data is missing or columns incomplete; news and SEC filings return empty lists; market summary functions return empty dict when summary is missing.
- **Portfolio exception handling (Phase 1.1 P0)**: Replaced bare `except:` with `except Exception:` in `Portfolio` so that `KeyboardInterrupt` and `SystemExit` are no longer swallowed.
- **Library-wide exception handling**: Replaced bare `except:` with `except Exception:` in AI providers (OpenAI, Anthropic, Gemini) and document extractors for consistent, safe exception handling.

## [0.1.3] - 2026-01-30

### Added
- **TTM (Trailing Twelve Months) Metrics**: Added `ttm_eps`, `ttm_pe`, `ttm_revenue`, `ttm_net_income`, and `ttm_ebitda` to RatiosCalculator
- **Advanced Financial Ratios**: 
  - ROIC (Return on Invested Capital)
  - WACC (Weighted Average Cost of Capital)
  - Equity Multiplier (Financial Leverage)
  - DuPont ROE Analysis
- **Earnings Call Transcripts Infrastructure**: New `EarningsCallTranscripts` class for earnings transcript handling
  - `get_transcripts_list()`: Get available earnings dates
  - `get_transcript()`: Fetch specific quarter transcripts
  - `print_pretty_table()`: Formatted transcript display
  - `search_transcript()`: Search transcripts for keywords
- **Pretty Formatting Utilities**: New formatting module with:
  - `format_number()`: Format numbers with thousand separators
  - `format_large_number()`: Format with K/M/B/T suffixes
  - `format_percentage()`: Format as percentages
  - `format_currency()`: Format as currency
  - `print_financial_statement()`: Pretty print financial statements
  - `print_ratios_table()`: Organized ratios display
  - `print_comparison_table()`: Multi-stock comparison tables
  - `print_dataframe_pretty()`: Enhanced DataFrame display
- **Revenue Breakdown Properties**: Added `revenue_by_segment` and `revenue_by_geography` (infrastructure ready)
- New example files: `advanced_ratios.py` and `earnings_transcripts.py`
- Comprehensive test coverage for all new features
- Advanced features documentation

### Changed
- Extended `RatiosCalculator.all()` to include TTM metrics and advanced ratios
- Updated `Stock` class to integrate earnings transcripts
- Enhanced profitability and leverage ratio categories

## [0.1.1] - 2026-01-29

### Changed
- Updated project URLs to reflect new repository ownership
- Added workflow_dispatch for manual PyPI publishing

## [0.1.0] - 2026-01-29

### Added
- Initial release of InvestorMate
- `Stock` class for comprehensive stock data access
- `Investor` class for AI-powered analysis (OpenAI, Anthropic, Gemini)
- `Screener` class for stock screening
- `Portfolio` class for portfolio tracking and analysis
- `Market` class for market summaries
- Support for 60+ technical indicators via pandas-ta
- Auto-calculated financial ratios (valuation, profitability, liquidity, leverage)
- Financial scoring systems (Piotroski F-Score, Altman Z-Score, Beneish M-Score)
- Document processing (PDF, CSV, web scraping)
- Multi-provider AI support (OpenAI, Anthropic Claude, Google Gemini)
- Comprehensive documentation and examples
- GitHub Actions CI/CD for testing and publishing
