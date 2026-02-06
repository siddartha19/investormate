# API Reference

Complete API documentation for InvestorMate.

## Core Classes

### Stock

```python
from investormate import Stock
```

Main class for accessing stock data and analysis.

#### Constructor

```python
Stock(ticker: str)
```

**Parameters:**
- `ticker` (str): Stock ticker symbol (e.g., "AAPL", "GOOGL", "RELIANCE")

#### Properties

**Price & Market Data:**
- `price` - Current stock price
- `previous_close` - Previous close price
- `market_cap` - Market capitalization
- `volume` - Trading volume

**Company Information:**
- `name` - Company name
- `sector` - Business sector
- `industry` - Specific industry
- `description` - Company description

**Financial Statements:**
- `balance_sheet` - Balance sheet data
- `income_statement` - Income statement data
- `cash_flow` - Cash flow statement data

**Analysis:**
- `ratios` - RatiosCalculator instance
- `scores` - FinancialScores instance
- `indicators` - IndicatorsHelper instance
- `sentiment` - SentimentAnalyzer instance
- `valuation` - Valuation instance (DCF, comps, summary) (v0.2.3)

**News & Filings:**
- `news` - Latest news articles
- `filings` - SEC filings (US stocks only)

#### Methods

**history(period="1y", interval="1d")**

Get historical price data.

**Parameters:**
- `period` - Time period: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
- `interval` - Data interval: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"

**Returns:** pandas DataFrame with OHLCV data

**add_indicators(df, indicators)**

Add technical indicators to DataFrame.

**Parameters:**
- `df` - DataFrame with OHLCV data
- `indicators` - List of indicator names (e.g., ["sma_20", "rsi_14"])

**Returns:** DataFrame with indicators added

---

### Valuation (stock.valuation)

Valuation module for DCF, comparable companies, and fair value summary. Access via `stock.valuation`.

**dcf(growth_rate=0.05, terminal_growth=0.02, years=5, wacc=None)**

Discounted Cash Flow with terminal value. Returns dict: `fair_value_per_share`, `enterprise_value`, `dcf_value`, `terminal_value_pv`, `fcf_series`, `wacc_used`, `assumptions`.

**comps(peers=None)**

Comparable companies: peer multiples (P/E, EV/EBITDA, P/S) and implied value per share. `peers` is a list of ticker symbols (e.g., `["MSFT", "GOOGL"]`). Returns dict: `peer_multiples`, `median_pe`, `median_ev_ebitda`, `median_ps`, `implied_value_pe`, `implied_value_ev_ebitda`, `implied_value_ps`, `current_price`.

**summary(peers=None, growth_rate=0.05, terminal_growth=0.02, years=5)**

Combined fair value from DCF and comps. Returns dict: `dcf_result`, `comps_result`, `fair_value_low`, `fair_value_high`, `current_price`, `recommendation` (undervalued/fair/overvalued).

**sensitivity(growth_rates=None, wacc_rates=None, years=5, terminal_growth=0.02)**

DCF sensitivity table (2D: growth × WACC → fair value). Returns dict: `table`, `current_price`, `min_value`, `max_value`.

---

### Investor

```python
from investormate import Investor
```

AI-powered stock analysis assistant.

#### Constructor

```python
Investor(
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    default_provider: str = "openai"
)
```

**Parameters:**
- `openai_api_key` - OpenAI API key
- `anthropic_api_key` - Anthropic API key
- `gemini_api_key` - Google Gemini API key
- `default_provider` - Default provider to use

**Note:** At least one API key is required.

#### Methods

**ask(ticker, question, provider=None)**

Ask a question about a stock.

**Parameters:**
- `ticker` - Stock ticker symbol
- `question` - Question to ask
- `provider` - AI provider to use (optional)

**Returns:** Dict with `answer` and optional `graph_data`

**analyze_document(ticker, document_url, question, provider=None)**

Analyze a document about a stock.

**Parameters:**
- `ticker` - Stock ticker symbol
- `document_url` - URL of PDF, article, or document
- `question` - Question to ask about the document
- `provider` - AI provider to use (optional)

**Returns:** Dict with analysis results

**compare(tickers, question, provider=None)**

Compare multiple stocks.

**Parameters:**
- `tickers` - List of ticker symbols
- `question` - Comparison question
- `provider` - AI provider to use (optional)

**Returns:** Dict with comparative analysis

**batch_analyze(queries, provider=None)**

Analyze multiple stocks with different questions.

**Parameters:**
- `queries` - List of (ticker, question) tuples
- `provider` - AI provider to use (optional)

**Returns:** List of analysis results

#### Properties

- `available_providers` - List of initialized AI providers

---

### Screener

```python
from investormate import Screener
```

Stock screening based on financial criteria.

#### Constructor

```python
Screener(universe: Optional[List[str]] = None)
```

**Parameters:**
- `universe` - List of tickers to screen (default: major US stocks)

#### Methods

**value_stocks(pe_max=15, pb_max=1.5, debt_to_equity_max=0.5)**

Find value stocks.

**growth_stocks(revenue_growth_min=20, eps_growth_min=15)**

Find growth stocks.

**dividend_stocks(yield_min=3.0, payout_ratio_max=60)**

Find dividend stocks.

**filter(**criteria)**

Custom screening with flexible criteria.

**Supported criteria:**
- `market_cap_min`, `market_cap_max`
- `pe_ratio` - tuple of (min, max)
- `pb_ratio` - tuple of (min, max)
- `roe_min`
- `debt_to_equity_max`
- `sector`, `industry`

---

### Portfolio

```python
from investormate import Portfolio
```

Portfolio tracking and analysis.

#### Constructor

```python
Portfolio(
    holdings: Dict[str, float],
    cost_basis: Optional[Dict[str, float]] = None
)
```

**Parameters:**
- `holdings` - Dict of {ticker: shares}
- `cost_basis` - Dict of {ticker: cost_per_share} (optional)

#### Properties

- `value` - Total portfolio value
- `allocation` - Allocation percentages by ticker
- `returns` - Total return % (requires cost_basis)
- `sharpe_ratio` - Sharpe ratio
- `volatility` - Annualized volatility
- `sector_allocation` - Allocation by sector
- `concentration` - Portfolio concentration index

#### Methods

**add(ticker, shares, cost_per_share=None)**

Add position to portfolio.

**remove(ticker)**

Remove position from portfolio.

---

### Market

```python
from investormate import Market
```

Market summaries and indices data.

#### Constructor

```python
Market(market: str)
```

**Parameters:**
- `market` - Market name: "US", "ASIA", "EUROPE", "CRYPTO", "CURRENCIES", "COMMODITIES"

#### Properties

- `summary` - Market summary data

#### Methods

**refresh()**

Clear cached data to force refresh.

---

## Helper Classes

### RatiosCalculator

Accessed via `Stock.ratios`.

**Properties:**

Valuation: `pe`, `peg`, `pb`, `ps`, `ev_ebitda`, `ev_revenue`

Profitability: `roe`, `roa`, `profit_margin`, `operating_margin`, `gross_margin`, `ebitda_margin`

Liquidity: `current_ratio`, `quick_ratio`, `cash_ratio`

Leverage: `debt_to_equity`, `debt_to_assets`, `equity_ratio`, `interest_coverage`

Efficiency: `asset_turnover`, `inventory_turnover`, `receivables_turnover`

Growth: `revenue_growth`, `earnings_growth`, `eps_growth`

Dividend: `dividend_yield`, `payout_ratio`

**Methods:**
- `all()` - Get all ratios as dict
- `valuation_ratios()` - Get valuation ratios only
- `profitability_ratios()` - Get profitability ratios only
- `liquidity_ratios()` - Get liquidity ratios only
- `leverage_ratios()` - Get leverage ratios only

### FinancialScores

Accessed via `Stock.scores`.

**Methods:**
- `piotroski_score()` - Returns (score, breakdown)
- `altman_z_score()` - Returns (score, interpretation)
- `beneish_m_score()` - Returns (score, interpretation)
- `all_scores()` - Get all scores

### IndicatorsHelper

Accessed via `Stock.indicators`.

**Moving Averages:**
- `sma(period=20, column='Close')` - Simple MA
- `ema(period=12, column='Close')` - Exponential MA
- `wma(period=20, column='Close')` - Weighted MA

**Momentum:**
- `rsi(period=14, column='Close')` - RSI
- `macd(fast=12, slow=26, signal=9)` - MACD
- `stoch(k=14, d=3, smooth_k=3)` - Stochastic
- `cci(period=20)` - CCI
- `williams_r(period=14)` - Williams %R
- `momentum(period=10)` - Momentum
- `roc(period=10)` - Rate of Change

**Volatility:**
- `bollinger_bands(period=20, std_dev=2.0)` - Bollinger Bands
- `atr(period=14)` - Average True Range
- `keltner_channels(period=20)` - Keltner Channels
- `donchian_channels(period=20)` - Donchian Channels

**Volume:**
- `obv()` - On-Balance Volume
- `ad()` - Accumulation/Distribution
- `adx(period=14)` - ADX
- `vwap()` - VWAP

**Trend:**
- `supertrend(period=7, multiplier=3.0)` - SuperTrend
- `ichimoku()` - Ichimoku Cloud

**Utility:**
- `add_indicators(indicators)` - Add multiple indicators to DataFrame
- `available_indicators()` - List all available indicators (static method)

---

### Correlation (v0.2.0)

```python
from investormate import Correlation
```

Multi-stock correlation analysis for portfolio diversification.

**Constructor:** `Correlation(tickers, period="1y", interval="1d")`

**Methods:**
- `matrix(method='pearson')` - Correlation matrix
- `find_pairs(threshold=0.7)` - Find highly correlated pairs
- `find_diversification_candidates(portfolio, universe, max_correlation=0.3)` - Find diversification candidates
- `get_statistics()` - Summary statistics

---

### SentimentAnalyzer (v0.2.0)

Accessed via `Stock.sentiment`.

**Methods:**
- `news(days=7)` - Analyze news sentiment
- `get_sentiment_label(score)` - Convert score to label
- `compare_sentiment(days_list)` - Compare across timeframes

---

### Backtest & Strategy (v0.2.0)

```python
from investormate import Backtest, Strategy
```

**Strategy** - Abstract base class with `initialize()` and `on_data(data)` methods. Trading: `buy()`, `sell()`, `sell_all()`.

**Backtest** - Constructor: `Backtest(strategy, ticker, start_date, end_date, initial_capital=10000, commission=0.0)`

**Methods:** `run()` returns BacktestResults with `total_return`, `sharpe_ratio`, `max_drawdown`, `win_rate`, `equity_curve`, `trades`, `summary()`.

---

### CustomStrategy (v0.2.0)

```python
from investormate import CustomStrategy
```

User-defined stock screening with function-based or builder pattern API.

**Constructor:** `CustomStrategy(filter_func=None, rank_func=None, universe=None)`

**Builder methods:** `add_filter(attribute, min, max)`, `rank_by(criteria)`, `apply(universe)`

**Methods:** `run(limit=None)` - Returns list of {ticker, rank, name, price}

---

## Exceptions

```python
from investormate import (
    InvestorMateError,
    InvalidTickerError,
    APIKeyError,
    DataFetchError,
    AIProviderError,
    ValidationError,
    DocumentProcessingError,
)
```

All exceptions inherit from `InvestorMateError`.

---

## Type Hints

InvestorMate uses type hints throughout. Example:

```python
from typing import Dict, List, Optional
from investormate import Stock, Investor

def analyze_stocks(tickers: List[str]) -> Dict[str, float]:
    results = {}
    for ticker in tickers:
        stock = Stock(ticker)
        results[ticker] = stock.price
    return results
```

---

## Complete Example

```python
from investormate import Investor, Stock, Screener, Portfolio, Market, Correlation, Backtest, Strategy, CustomStrategy
import os

# 1. Basic stock data
stock = Stock("AAPL")
print(f"{stock.name}: ${stock.price}")
print(f"P/E: {stock.ratios.pe}, ROE: {stock.ratios.roe}")

# 2. AI analysis
investor = Investor(openai_api_key=os.getenv("OPENAI_API_KEY"))
result = investor.ask("AAPL", "Is it undervalued?")
print(result['answer'])

# 3. Technical analysis
df = stock.history(period="6mo")
df_with_ta = stock.add_indicators(df, ["sma_20", "rsi_14"])

# 4. Screening
screener = Screener()
value_stocks = screener.value_stocks(pe_max=15)

# 5. Portfolio
portfolio = Portfolio({"AAPL": 10, "GOOGL": 5})
print(f"Portfolio: ${portfolio.value:,.2f}")

# 6. Market data
market = Market("US")
print(market.summary)

# 7. Correlation analysis (v0.2.0)
corr = Correlation(["AAPL", "GOOGL", "MSFT"], period="1y")
print(corr.matrix())

# 8. Sentiment analysis (v0.2.0)
sentiment = stock.sentiment.news(days=7)
print(f"Sentiment: {sentiment['score']}")

# 9. Custom screening (v0.2.0)
strategy = CustomStrategy().add_filter("ratios.pe", min=10, max=25).apply(universe=["AAPL", "GOOGL"])
print(strategy.run())
```
