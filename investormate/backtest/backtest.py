"""
User-friendly Backtest wrapper class.
"""

from typing import Type
from .engine import BacktestEngine
from .results import BacktestResults
from .strategy import Strategy


class Backtest:
    """
    Main backtesting interface for users.
    
    Example:
        >>> class MyStrategy(Strategy):
        ...     def initialize(self):
        ...         self.ma_period = 20
        ...     
        ...     def on_data(self, data):
        ...         # Strategy logic here
        ...         pass
        ...
        >>> bt = Backtest(
        ...     strategy=MyStrategy,
        ...     ticker="AAPL",
        ...     start_date="2020-01-01",
        ...     end_date="2023-01-01",
        ...     initial_capital=10000
        ... )
        >>> results = bt.run()
        >>> print(results.summary())
    """
    
    def __init__(
        self,
        strategy: Type[Strategy],
        ticker: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000,
        commission: float = 0.0
    ):
        """
        Initialize backtest.
        
        Args:
            strategy: Strategy class (not instance)
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            initial_capital: Starting capital (default: $10,000)
            commission: Commission rate per trade (default: 0.0, e.g., 0.001 for 0.1%)
        """
        self.strategy = strategy
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission = commission
        
        self._results = None
    
    def run(self) -> BacktestResults:
        """
        Run the backtest.
        
        Returns:
            BacktestResults object with performance metrics
        """
        # Create engine
        engine = BacktestEngine(
            strategy_class=self.strategy,
            ticker=self.ticker,
            start_date=self.start_date,
            end_date=self.end_date,
            initial_capital=self.initial_capital,
            commission=self.commission
        )
        
        # Run backtest
        results_dict = engine.run()
        
        # Create results object
        self._results = BacktestResults(results_dict)
        
        return self._results
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"Backtest(strategy={self.strategy.__name__}, "
                f"ticker='{self.ticker}', "
                f"period='{self.start_date}' to '{self.end_date}')")
