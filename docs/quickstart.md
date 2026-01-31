# InvestorMate Quickstart Guide

Get started with InvestorMate in minutes!

## Installation

```bash
pip install investormate
```

## Basic Stock Analysis

```python
from investormate import Stock

# Create a stock instance
stock = Stock("AAPL")

# Get basic info
print(f"Price: ${stock.price}")
print(f"Market Cap: ${stock.market_cap:,.0f}")
print(f"Sector: {stock.sector}")

# Get financial ratios
print(f"P/E Ratio: {stock.ratios.pe}")
print(f"ROE: {stock.ratios.roe}")
print(f"Debt-to-Equity: {stock.ratios.debt_to_equity}")
```

## AI-Powered Analysis

```python
from investormate import Investor
import os

# Initialize with your API key
investor = Investor(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Ask questions about any stock
result = investor.ask("AAPL", "Is Apple undervalued?")
print(result['answer'])

# Compare multiple stocks
comparison = investor.compare(
    ["AAPL", "GOOGL", "MSFT"],
    "Which has the best growth prospects?"
)
print(comparison['answer'])
```

## Technical Analysis

```python
from investormate import Stock

stock = Stock("AAPL")

# Get historical data
df = stock.history(period="6mo", interval="1d")

# Add technical indicators
df_with_indicators = stock.add_indicators(df, [
    "sma_20", "sma_50", "rsi_14", "macd"
])

# Or use indicators directly
print(f"RSI: {stock.indicators.rsi(14).iloc[-1]}")
print(f"20-day SMA: {stock.indicators.sma(20).iloc[-1]}")
```

## Stock Screening

```python
from investormate import Screener

screener = Screener()

# Find value stocks
value_stocks = screener.value_stocks(pe_max=15, pb_max=1.5)

# Find growth stocks
growth_stocks = screener.growth_stocks(revenue_growth_min=20)

# Custom screening
results = screener.filter(
    market_cap_min=1_000_000_000,
    pe_ratio=(10, 25),
    sector="Technology"
)
```

## Portfolio Tracking

```python
from investormate import Portfolio

portfolio = Portfolio({
    "AAPL": 10,
    "GOOGL": 5,
    "MSFT": 15
})

print(f"Total Value: ${portfolio.value:,.2f}")
print(f"Allocation: {portfolio.allocation}")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio}")
```

## Market Data

```python
from investormate import Market

# US markets
us_market = Market("US")
print(us_market.summary)

# Crypto markets
crypto = Market("CRYPTO")
print(crypto.summary)

# Other markets: "ASIA", "EUROPE", "CURRENCIES", "COMMODITIES"
```

## v0.2.0 Features

### Correlation Analysis

```python
from investormate import Correlation

corr = Correlation(["AAPL", "GOOGL", "MSFT"], period="1y")
print(corr.matrix())
pairs = corr.find_pairs(threshold=0.7)
```

### Sentiment Analysis

```python
stock = Stock("AAPL")
sentiment = stock.sentiment.news(days=7)
print(f"Score: {sentiment['score']}, Bullish: {sentiment['bullish_percent']}%")
```

### Backtesting

```python
from investormate import Backtest, Strategy

class MyStrategy(Strategy):
    def initialize(self):
        self.ma_period = 20
    def on_data(self, data):
        # Your strategy logic
        pass

bt = Backtest(MyStrategy, "AAPL", "2020-01-01", "2024-01-01")
results = bt.run()
print(results.summary())
```

### Custom Strategies

```python
from investormate import CustomStrategy

strategy = (
    CustomStrategy()
    .add_filter("ratios.pe", min=10, max=25)
    .add_filter("ratios.roe", min=0.15)
    .rank_by("ratios.roe")
    .apply(universe=["AAPL", "GOOGL", "MSFT"])
)
results = strategy.run()
```

## Next Steps

- Check out the [Examples](../examples/) directory for more code samples
- Read the [AI Providers Guide](ai_providers.md) for details on using different AI models
- See the [API Reference](api_reference.md) for complete documentation
- Explore [Correlation](correlation.md), [Sentiment](sentiment.md), [Backtesting](backtesting.md), [Custom Strategies](custom_strategies.md) guides

## Need Help?

- GitHub Issues: https://github.com/investormate/investormate/issues
- Documentation: https://github.com/investormate/investormate#readme
