# InvestorMate Documentation

Welcome to InvestorMate - the all-in-one Python package for AI-powered stock analysis!

## What is InvestorMate?

InvestorMate combines the best of financial data, technical analysis, and AI to provide a simple, powerful interface for stock analysis in Python.

## Key Features

- **AI-Powered Analysis** - Ask natural language questions about any stock
- **Comprehensive Data** - Real-time prices, financials, news, SEC filings
- **20+ Technical Indicators** - SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, and more (native)
- **Financial Ratios** - Auto-calculated P/E, ROE, debt ratios, profitability metrics
- **Stock Screening** - Find value, growth, or dividend stocks
- **Portfolio Analysis** - Track performance, risk metrics, and allocation
- **Market Summaries** - Global market data at your fingertips
- **Valuation** (v0.2.3) - DCF, comparable companies (P/E, EV/EBITDA, P/S), fair value summary & sensitivity
- **Correlation Analysis** - Portfolio diversification, find correlated pairs
- **Sentiment Analysis** - AI-powered news sentiment
- **Backtesting** - Test strategies on historical data; built-in **strategy templates** (momentum, mean reversion, SMA crossover)
- **Custom Strategies** - User-defined screening logic
- **Caching (v0.3.0)** - TTL cache and rate limiting for yfinance; `stock.refresh()`
- **Earnings API (v0.3.0)** - Calendar, estimates, EPS surprise history
- **Portfolio VaR / Monte Carlo (v0.3.0)** - Historical and parametric VaR, bootstrap simulation
- **Screens (v0.3.0)** - CAN SLIM–style and dividend-growth streak screens
- **Student Edition (v0.5.0)** - TVM, bonds, Black-Scholes, statement analysis, CAPM, `explain()`/`show_work()`, practice problems, Markdown/Excel export
- **Terminal CLI (v0.6.0)** - Keyless `investormate quote` / `analyze` with `--json` output

## Quick Links

- [Quickstart Guide](quickstart.md) - CLI + Python API in 5 minutes
- [API Reference](api_reference.md) - Complete API documentation
- [TVM Calculator](tvm.md) - Present value, annuities, IRR, amortization (v0.5.0)
- [Fixed Income](fixed_income.md) - Bond pricing, duration, convexity (v0.5.0)
- [Derivatives](derivatives.md) - Black-Scholes, Greeks, binomial (v0.5.0)
- [Financial Statements](financial_statements.md) - Common-size, horizontal, trend (v0.5.0)
- [CAPM & Factors](capm.md) - Beta, alpha, risk decomposition (v0.5.0)
- [Educational Layer](educational_layer.md) - explain(), show_work(), practice (v0.5.0)
- [AI Providers Guide](ai_providers.md) - Using OpenAI, Claude, and Gemini
- [Correlation Analysis](correlation.md) - Portfolio diversification
- [Sentiment Analysis](sentiment.md) - News sentiment
- [Backtesting](backtesting.md) - Strategy backtesting
- [Valuation](valuation.md) - DCF, comps, fair value summary
- [Custom Strategies](custom_strategies.md) - Custom screening + institutional-style screens
- [Caching](caching.md) - TTL cache and rate limits
- [Earnings](earnings.md) - Estimates and surprises
- [Risk](risk.md) - VaR and Monte Carlo
- [Strategy templates](strategy_templates.md) - Built-in backtest strategies
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
- **pandas & numpy** - Data processing and native technical indicators
- **OpenAI/Anthropic/Gemini** - AI analysis (optional)

## Support & Community

- **GitHub**: https://github.com/investormate/investormate
- **Issues**: https://github.com/investormate/investormate/issues
- **PyPI**: https://pypi.org/project/investormate/

## License

MIT License - see [LICENSE](../LICENSE) for details

## Disclaimer

InvestorMate is for educational and research purposes only. It is not financial advice. AI-generated insights may contain errors. Always verify information and consult with a qualified financial advisor before making investment decisions.
