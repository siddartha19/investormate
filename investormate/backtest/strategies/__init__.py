"""Built-in strategy templates for the minimal backtest engine."""

from .momentum import MomentumStrategy
from .mean_reversion import MeanReversionStrategy
from .sma_crossover import SMACrossoverStrategy

__all__ = [
    "MomentumStrategy",
    "MeanReversionStrategy",
    "SMACrossoverStrategy",
]
