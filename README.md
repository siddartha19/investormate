# InvestorMate 🤖📈

[![PyPI version](https://badge.fury.io/py/investormate.svg)](https://badge.fury.io/py/investormate)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/investormate/investormate/workflows/Tests/badge.svg)](https://github.com/investormate/investormate/actions)

**AI-Powered Stock Analysis in Python**

InvestorMate is the only Python package you need for comprehensive stock analysis - from data fetching to AI-powered insights.

> "Ask any question about any stock and get instant AI-powered insights"

## ✨ Features

- **AI-Powered Analysis** - Ask natural language questions about any stock using OpenAI, Claude, or Gemini
- **Comprehensive Stock Data** - Real-time prices, financials, news, and SEC filings via yfinance
- **60+ Technical Indicators** - SMA, EMA, RSI, MACD, Bollinger Bands, and more via pandas-ta
- **Financial Ratios** - Auto-calculated P/E, ROE, debt ratios, and profitability metrics
- **Stock Screening** - Find value stocks, growth stocks, or create custom screens
- **Portfolio Analysis** - Track performance, risk metrics, and allocation
- **Market Summaries** - Real-time data for US, Asian, European, crypto, and commodity markets

## 🚀 Quick Start

```bash
pip install investormate
```

```python
from investormate import Investor, Stock

# AI-powered analysis
investor = Investor(openai_api_key="sk-...")
result = investor.ask("AAPL", "Is Apple undervalued compared to its peers?")
print(result)

# Stock data and analysis
stock = Stock("AAPL")
print(f"Price: ${stock.price}")
print(f"P/E Ratio: {stock.ratios.pe}")
print(f"RSI: {stock.indicators.rsi()}")
```

## 📦 Installation

```bash
# Basic installation
pip install investormate

# With development dependencies
pip install investormate[dev]
```

## 🔑 API Keys

InvestorMate supports multiple AI providers:

- **OpenAI**: Get your API key at https://platform.openai.com/api-keys
- **Anthropic Claude**: Get your API key at https://console.anthropic.com/
- **Google Gemini**: Get your API key at https://ai.google.dev/

You only need one API key to use the AI features.

## 📚 Documentation

- [Quickstart Guide](docs/quickstart.md) - Get started in 5 minutes
- [API Reference](docs/api_reference.md) - Complete API documentation
- [AI Providers Guide](docs/ai_providers.md) - OpenAI, Claude, and Gemini setup
- [Examples](examples/) - Working code examples

## 🎯 Why InvestorMate?

| Feature | InvestorMate | Other Solutions |
|---------|--------------|-----------------|
| **Simplicity** | One package, simple API | Need 5+ packages |
| **AI-Powered** | Built-in AI analysis | Manual analysis only |
| **Provider Choice** | OpenAI, Claude, Gemini | Locked to one provider |
| **Setup Time** | 2 lines of code | Hours of configuration |
| **Data Format** | JSON-ready | Raw pandas DataFrames |
| **Target Users** | Everyone | Enterprise only |

## 💡 Examples

### Stock Analysis

```python
from investormate import Stock

stock = Stock("TSLA")

# Basic info
print(stock.price)
print(stock.market_cap)
print(stock.sector)

# Financial statements
income_stmt = stock.income_statement
balance_sheet = stock.balance_sheet
cash_flow = stock.cash_flow

# Historical data
df = stock.history(period="1y", interval="1d")
```

### AI-Powered Insights

```python
from investormate import Investor

investor = Investor(openai_api_key="sk-...")

# Ask questions
result = investor.ask("NVDA", "What are the key revenue drivers?")

# Compare stocks
comparison = investor.compare(
    ["AAPL", "GOOGL", "MSFT"],
    "Which has the best growth prospects?"
)

# Analyze documents
result = investor.analyze_document(
    ticker="TSLA",
    url="https://example.com/earnings-report.pdf",
    question="Summarize Q4 earnings highlights"
)
```

### Technical Analysis

```python
from investormate import Stock

stock = Stock("AAPL")
df = stock.history(period="6mo")

# Add indicators
df = stock.add_indicators(df, [
    "sma_20", "sma_50", "rsi_14", "macd", "bbands"
])

# Or use individual methods
sma_20 = stock.indicators.sma(20)
rsi = stock.indicators.rsi(14)
macd = stock.indicators.macd()
```

### Stock Screening

```python
from investormate import Screener

screener = Screener()

# Pre-built screens
value_stocks = screener.value_stocks(pe_max=15, pb_max=1.5)
growth_stocks = screener.growth_stocks(revenue_growth_min=20)
dividend_stocks = screener.dividend_stocks(yield_min=3.0)

# Custom screening
results = screener.filter(
    market_cap_min=1_000_000_000,
    pe_ratio=(10, 25),
    roe_min=15,
    sector="Technology"
)
```

### Portfolio Analysis

```python
from investormate import Portfolio

portfolio = Portfolio({
    "AAPL": 10,
    "GOOGL": 5,
    "MSFT": 15,
    "TSLA": 8
})

print(f"Total Value: ${portfolio.value:,.2f}")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio:.2f}")
print(f"Allocation: {portfolio.allocation}")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

InvestorMate is for educational and research purposes only. It is not financial advice. AI-generated insights may contain errors or hallucinations. Always verify information and consult with a qualified financial advisor before making investment decisions.

## 🌟 Support

If you find InvestorMate useful, please give it a star on GitHub!

---

Made with ❤️ by the InvestorMate community
