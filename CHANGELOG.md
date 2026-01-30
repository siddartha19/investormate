# Changelog

All notable changes to InvestorMate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
