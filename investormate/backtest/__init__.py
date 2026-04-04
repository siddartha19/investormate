"""
Backtesting framework for InvestorMate.

Test trading strategies on historical data with comprehensive
performance metrics and analysis.
"""

from .strategy import Strategy
from .engine import BacktestEngine
from .results import BacktestResults
from .backtest import Backtest
from .strategies import (
    MomentumStrategy,
    MeanReversionStrategy,
    SMACrossoverStrategy,
)

__all__ = [
    "Strategy",
    "BacktestEngine",
    "BacktestResults",
    "Backtest",
    "MomentumStrategy",
    "MeanReversionStrategy",
    "SMACrossoverStrategy",
]
