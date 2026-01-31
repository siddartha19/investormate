"""
Backtesting engine for running strategy backtests.
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from ..core.stock import Stock
from ..data.fetchers import get_yfinance_stock_history
from ..utils.exceptions import DataFetchError


class BacktestEngine:
    """
    Core backtesting engine for executing strategies on historical data.
    
    Handles:
    - Historical data iteration
    - Position tracking
    - Trade execution
    - Commission costs
    - Equity curve generation
    """
    
    def __init__(
        self,
        strategy_class,
        ticker: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000,
        commission: float = 0.0,
    ):
        """
        Initialize backtest engine.
        
        Args:
            strategy_class: Strategy class (not instance)
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            initial_capital: Starting capital
            commission: Commission rate (e.g., 0.001 for 0.1%)
        """
        self.strategy_class = strategy_class
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission = commission
        
        # State variables
        self.cash = initial_capital
        self.position_size = 0
        self.avg_entry_price = 0.0
        
        # Historical tracking
        self.trades = []
        self.equity_history = []
        self.current_date = None
        self.current_price = None
        
        # Data
        self.data = None
        self.dates = None
    
    @property
    def has_position(self) -> bool:
        """Check if holding a position."""
        return self.position_size > 0
    
    @property
    def equity(self) -> float:
        """Get current total equity."""
        position_value = self.position_size * self.current_price if self.current_price else 0
        return self.cash + position_value
    
    def _fetch_data(self) -> pd.DataFrame:
        """Fetch historical data for backtesting."""
        try:
            # Convert dates to pandas datetime for yfinance
            import yfinance as yf
            from ..data.constants import get_ticker_format
            
            ticker_obj = yf.Ticker(get_ticker_format(self.ticker))
            df = ticker_obj.history(start=self.start_date, end=self.end_date)
            
            if df.empty:
                raise DataFetchError(f"No data found for {self.ticker} between {self.start_date} and {self.end_date}")
            
            return df
        except Exception as e:
            raise DataFetchError(f"Failed to fetch backtest data: {str(e)}")
    
    def buy(self, shares: Optional[int] = None, percent: Optional[float] = None):
        """
        Execute buy order.
        
        Args:
            shares: Number of shares to buy
            percent: Percentage of cash to use (0-1)
        """
        if shares is not None:
            cost = shares * self.current_price
            commission_cost = cost * self.commission
            total_cost = cost + commission_cost
            
            if total_cost > self.cash:
                # Not enough cash, buy what we can
                affordable_shares = int(self.cash / (self.current_price * (1 + self.commission)))
                if affordable_shares <= 0:
                    return
                shares = affordable_shares
                cost = shares * self.current_price
                commission_cost = cost * self.commission
                total_cost = cost + commission_cost
            
            # Update position
            if self.position_size > 0:
                # Add to existing position
                total_shares = self.position_size + shares
                total_cost_basis = (self.position_size * self.avg_entry_price) + cost
                self.avg_entry_price = total_cost_basis / total_shares
                self.position_size = total_shares
            else:
                # New position
                self.position_size = shares
                self.avg_entry_price = self.current_price
            
            self.cash -= total_cost
            
            # Record trade
            self.trades.append({
                'date': self.current_date,
                'type': 'BUY',
                'shares': shares,
                'price': self.current_price,
                'commission': commission_cost,
                'total_cost': total_cost
            })
        
        elif percent is not None:
            if not 0 <= percent <= 1:
                raise ValueError("Percent must be between 0 and 1")
            
            cash_to_use = self.cash * percent
            shares = int(cash_to_use / (self.current_price * (1 + self.commission)))
            
            if shares > 0:
                self.buy(shares=shares)
    
    def sell(self, shares: Optional[int] = None, percent: Optional[float] = None):
        """
        Execute sell order.
        
        Args:
            shares: Number of shares to sell
            percent: Percentage of position to sell (0-1)
        """
        if not self.has_position:
            return
        
        if shares is not None:
            shares = min(shares, self.position_size)
            
            proceeds = shares * self.current_price
            commission_cost = proceeds * self.commission
            net_proceeds = proceeds - commission_cost
            
            self.cash += net_proceeds
            self.position_size -= shares
            
            # Calculate profit/loss
            cost_basis = shares * self.avg_entry_price
            pnl = proceeds - cost_basis - commission_cost
            
            # Record trade
            self.trades.append({
                'date': self.current_date,
                'type': 'SELL',
                'shares': shares,
                'price': self.current_price,
                'commission': commission_cost,
                'net_proceeds': net_proceeds,
                'pnl': pnl
            })
            
            if self.position_size == 0:
                self.avg_entry_price = 0.0
        
        elif percent is not None:
            if not 0 <= percent <= 1:
                raise ValueError("Percent must be between 0 and 1")
            
            shares = int(self.position_size * percent)
            
            if shares > 0:
                self.sell(shares=shares)
    
    def sell_all(self):
        """Sell entire position."""
        if self.has_position:
            self.sell(shares=self.position_size)
    
    def run(self):
        """
        Run the backtest.
        
        Returns:
            Dictionary with results
        """
        # Fetch data
        self.data = self._fetch_data()
        self.dates = self.data.index
        
        # Initialize strategy
        strategy = self.strategy_class()
        strategy._set_engine(self)
        strategy.initialize()
        
        # Run backtest
        for date in self.dates:
            self.current_date = date
            self.current_price = self.data.loc[date, 'Close']
            
            # Create Stock object with data up to current date
            # For simplicity, we'll pass the full stock but strategy should use current data
            try:
                from ..core.stock import Stock
                stock = Stock(self.ticker)
                
                # Call strategy
                strategy.on_data(stock)
            except Exception as e:
                # Log error but continue backtest
                print(f"Strategy error on {date}: {e}")
            
            # Track equity
            self.equity_history.append({
                'date': date,
                'equity': self.equity,
                'cash': self.cash,
                'position_value': self.position_size * self.current_price,
                'position_size': self.position_size
            })
        
        # Close any open positions at the end
        if self.has_position:
            self.sell_all()
        
        # Return results dictionary
        return {
            'trades': self.trades,
            'equity_history': self.equity_history,
            'final_equity': self.equity,
            'initial_capital': self.initial_capital,
            'ticker': self.ticker,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date)
        }
