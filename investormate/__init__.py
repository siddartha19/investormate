"""
InvestorMate - AI-Powered Stock Analysis Package

InvestorMate is an all-in-one Python package for stock analysis that combines:
- AI-powered analysis (OpenAI, Anthropic Claude, Google Gemini)
- Stock data fetching (yfinance wrapper)
- Technical indicators (60+ indicators via pandas-ta)
- Financial ratios and metrics (auto-calculated)
- Stock screening capabilities
- Portfolio analysis
- Market summaries
"""

from .version import __version__

# Core classes
from .core.investor import Investor
from .core.stock import Stock
from .core.screener import Screener
from .core.portfolio import Portfolio
from .core.market import Market

# Exceptions
from .utils.exceptions import (
    InvestorMateError,
    InvalidTickerError,
    APIKeyError,
    DataFetchError,
    AIProviderError,
    ValidationError,
    DocumentProcessingError,
)

__all__ = [
    "__version__",
    "Investor",
    "Stock",
    "Screener",
    "Portfolio",
    "Market",
    # Exceptions
    "InvestorMateError",
    "InvalidTickerError",
    "APIKeyError",
    "DataFetchError",
    "AIProviderError",
    "ValidationError",
    "DocumentProcessingError",
]
