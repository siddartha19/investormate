"""
Base Strategy class for backtesting.
"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd

from ..core.stock import Stock


class Strategy(ABC):
    """
    Abstract base class for backtesting strategies.
    
    Users should subclass this and implement:
    - initialize(): Set up strategy parameters
    - on_data(data): Called for each bar of data
    
    Example:
        >>> class RSIStrategy(Strategy):
        ...     def initialize(self):
        ...         self.rsi_period = 14
        ...         self.buy_threshold = 30
        ...         self.sell_threshold = 70
        ...
        ...     def on_data(self, data):
        ...         rsi = data.indicators.rsi(self.rsi_period).iloc[-1]
        ...         if rsi < self.buy_threshold and not self.has_position:
        ...             self.buy(shares=100)
        ...         elif rsi > self.sell_threshold and self.has_position:
        ...             self.sell_all()
    """
    
    def __init__(self):
        """Initialize strategy."""
        self._engine = None
        self.ticker = None
        self.initial_capital = None
    
    def _set_engine(self, engine):
        """
        Set backtest engine (called internally by BacktestEngine).
        
        Args:
            engine: BacktestEngine instance
        """
        self._engine = engine
        self.ticker = engine.ticker
        self.initial_capital = engine.initial_capital
    
    @abstractmethod
    def initialize(self):
        """
        Initialize strategy parameters.
        
        This method is called once before backtesting starts.
        Use it to set up indicators, thresholds, and other parameters.
        """
        pass
    
    @abstractmethod
    def on_data(self, data: Stock):
        """
        Called for each bar of data during backtesting.
        
        Args:
            data: Stock object with historical data up to current bar
        """
        pass
    
    # Position Information
    
    @property
    def has_position(self) -> bool:
        """Check if currently holding position."""
        if self._engine is None:
            raise RuntimeError("Strategy must be run within a backtest")
        return self._engine.has_position
    
    @property
    def position_size(self) -> int:
        """Get current position size (number of shares)."""
        if self._engine is None:
            raise RuntimeError("Strategy must be run within a backtest")
        return self._engine.position_size
    
    @property
    def cash(self) -> float:
        """Get current cash balance."""
        if self._engine is None:
            raise RuntimeError("Strategy must be run within a backtest")
        return self._engine.cash
    
    @property
    def equity(self) -> float:
        """Get current total equity (cash + position value)."""
        if self._engine is None:
            raise RuntimeError("Strategy must be run within a backtest")
        return self._engine.equity
    
    # Trading Methods
    
    def buy(self, shares: Optional[int] = None, percent: Optional[float] = None):
        """
        Buy shares.
        
        Args:
            shares: Number of shares to buy (optional)
            percent: Percentage of cash to use (0-1) (optional)
        
        Example:
            >>> self.buy(shares=100)  # Buy 100 shares
            >>> self.buy(percent=0.5)  # Use 50% of cash
        """
        if self._engine is None:
            raise RuntimeError("Strategy must be run within a backtest")
        
        if shares is not None and percent is not None:
            raise ValueError("Specify either shares or percent, not both")
        
        if shares is None and percent is None:
            raise ValueError("Must specify either shares or percent")
        
        self._engine.buy(shares=shares, percent=percent)
    
    def sell(self, shares: Optional[int] = None, percent: Optional[float] = None):
        """
        Sell shares.
        
        Args:
            shares: Number of shares to sell (optional)
            percent: Percentage of position to sell (0-1) (optional)
        
        Example:
            >>> self.sell(shares=50)  # Sell 50 shares
            >>> self.sell(percent=0.5)  # Sell 50% of position
        """
        if self._engine is None:
            raise RuntimeError("Strategy must be run within a backtest")
        
        if shares is not None and percent is not None:
            raise ValueError("Specify either shares or percent, not both")
        
        if shares is None and percent is None:
            raise ValueError("Must specify either shares or percent")
        
        self._engine.sell(shares=shares, percent=percent)
    
    def sell_all(self):
        """Sell all shares in current position."""
        if self._engine is None:
            raise RuntimeError("Strategy must be run within a backtest")
        
        self._engine.sell_all()
    
    def close_position(self):
        """Alias for sell_all()."""
        self.sell_all()
