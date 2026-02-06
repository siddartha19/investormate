# InvestorMate Documentation

Welcome to InvestorMate - the all-in-one Python package for AI-powered stock analysis!

## What is InvestorMate?

InvestorMate combines the best of financial data, technical analysis, and AI to provide a simple, powerful interface for stock analysis in Python.

## Key Features

- **AI-Powered Analysis** - Ask natural language questions about any stock
- **Comprehensive Data** - Real-time prices, financials, news, SEC filings
- **60+ Technical Indicators** - SMA, EMA, RSI, MACD, Bollinger Bands, and more
- **Financial Ratios** - Auto-calculated P/E, ROE, debt ratios, profitability metrics
- **Stock Screening** - Find value, growth, or dividend stocks
- **Portfolio Analysis** - Track performance, risk metrics, and allocation
- **Market Summaries** - Global market data at your fingertips
- **Valuation** (v0.2.3) - DCF, comparable companies (P/E, EV/EBITDA, P/S), fair value summary & sensitivity
- **Correlation Analysis** - Portfolio diversification, find correlated pairs
- **Sentiment Analysis** - AI-powered news sentiment
- **Backtesting** - Test strategies on historical data
- **Custom Strategies** - User-defined screening logic

## Quick Links

- [Quickstart Guide](quickstart.md) - Get started in 5 minutes
- [API Reference](api_reference.md) - Complete API documentation
- [AI Providers Guide](ai_providers.md) - Using OpenAI, Claude, and Gemini
- [Correlation Analysis](correlation.md) - Portfolio diversification
- [Sentiment Analysis](sentiment.md) - News sentiment
- [Backtesting](backtesting.md) - Strategy backtesting
- [Valuation](valuation.md) - DCF, comps, fair value summary
- [Custom Strategies](custom_strategies.md) - Custom screening
- [Examples](../examples/) - Code examples

## Installation

```bash
pip install investormate
```

## Simple Example

```python
from investormate import Stock, Investor
import os

# Stock data
stock = Stock("AAPL")
print(f"{stock.name}: ${stock.price}")
print(f"P/E: {stock.ratios.pe}, RSI: {stock.indicators.rsi().iloc[-1]}")

# AI analysis
investor = Investor(openai_api_key=os.getenv("OPENAI_API_KEY"))
result = investor.ask("AAPL", "Is Apple undervalued?")
print(result['answer'])
```

## Why InvestorMate?

| InvestorMate | Other Packages |
|--------------|----------------|
| All-in-one solution | Need 5+ packages |
| AI-powered insights | Manual analysis only |
| Simple API | Complex configuration |
| Multiple AI providers | Locked to one provider |
| JSON-ready data | Raw pandas DataFrames |
| Production-ready | Requires heavy setup |

## Use Cases

- **Developers** building finance apps
- **Researchers** analyzing multiple stocks
- **Traders** needing technical and fundamental analysis
- **Data Scientists** creating ML features
- **Content Creators** generating stock insights
- **Educators** teaching finance concepts

## Architecture

InvestorMate is built on top of:
- **yfinance** - Stock data
- **pandas-ta** - Technical indicators
- **OpenAI/Anthropic/Gemini** - AI analysis
- **pandas & numpy** - Data processing

## Support & Community

- **GitHub**: https://github.com/investormate/investormate
- **Issues**: https://github.com/investormate/investormate/issues
- **PyPI**: https://pypi.org/project/investormate/

## License

MIT License - see [LICENSE](../LICENSE) for details

## Disclaimer

InvestorMate is for educational and research purposes only. It is not financial advice. AI-generated insights may contain errors. Always verify information and consult with a qualified financial advisor before making investment decisions.
