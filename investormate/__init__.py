"""
InvestorMate - AI-Powered Stock Analysis Package

InvestorMate is an all-in-one Python package for stock analysis that combines:
- AI-powered analysis (OpenAI, Anthropic Claude, Google Gemini)
- Stock data fetching (yfinance wrapper)
- Technical indicators (20+ indicators, native numpy/pandas)
- Financial ratios and metrics (auto-calculated)
- Academic finance (TVM, bonds, options, CAPM, statement analysis)
- Educational layer (explain, show_work, CFA tags, practice problems)
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
from .core.custom_strategy import CustomStrategy

# Analysis classes
from .analysis.correlation import Correlation
from .analysis.sentiment import SentimentAnalyzer
from .analysis.financials import FinancialStatements
from .analysis.capm import CAPMAnalyzer

# Academic finance
from .finance import (
    present_value,
    future_value,
    annuity_pv,
    annuity_fv,
    perpetuity,
    npv,
    irr,
    amortization_schedule,
    ear,
    Bond,
    bond_ladder,
    options,
)

# Education
from .education import generate as practice_generate
from .education import get_ratio_knowledge

# Backtesting classes
from .backtest import (
    Backtest,
    Strategy,
    BacktestEngine,
    BacktestResults,
    MomentumStrategy,
    MeanReversionStrategy,
    SMACrossoverStrategy,
)

# Data provenance (Stock.history(source_trace=True))
from .core.history_result import HistoryResult

# Pluggable data source layer
from .data.providers import (
    DataProvider,
    YFinanceProvider,
    get_data_provider,
    set_data_provider,
    reset_data_provider,
)

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
    # Core
    "Investor",
    "Stock",
    "Screener",
    "Portfolio",
    "Market",
    "CustomStrategy",
    # Analysis
    "Correlation",
    "SentimentAnalyzer",
    "FinancialStatements",
    "CAPMAnalyzer",
    # Academic finance
    "present_value",
    "future_value",
    "annuity_pv",
    "annuity_fv",
    "perpetuity",
    "npv",
    "irr",
    "amortization_schedule",
    "ear",
    "Bond",
    "bond_ladder",
    "options",
    # Education
    "practice_generate",
    "get_ratio_knowledge",
    # Backtesting
    "Backtest",
    "Strategy",
    "BacktestEngine",
    "BacktestResults",
    "MomentumStrategy",
    "MeanReversionStrategy",
    "SMACrossoverStrategy",
    "HistoryResult",
    # Data providers
    "DataProvider",
    "YFinanceProvider",
    "get_data_provider",
    "set_data_provider",
    "reset_data_provider",
    # Exceptions
    "InvestorMateError",
    "InvalidTickerError",
    "APIKeyError",
    "DataFetchError",
    "AIProviderError",
    "ValidationError",
    "DocumentProcessingError",
]
