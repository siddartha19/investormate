"""
Portfolio class for InvestorMate.
Portfolio analysis and performance tracking.
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np

from ..data.fetchers import get_yfinance_data, get_yfinance_stock_history
from ..utils.helpers import safe_divide


class Portfolio:
    """
    Portfolio tracker and analyzer.
    
    Example:
        >>> portfolio = Portfolio({"AAPL": 10, "GOOGL": 5})
        >>> print(portfolio.value)
        >>> print(portfolio.allocation)
    """
    
    def __init__(self, holdings: Dict[str, float], 
                 cost_basis: Optional[Dict[str, float]] = None):
        """
        Initialize portfolio.
        
        Args:
            holdings: Dictionary of {ticker: shares}
            cost_basis: Optional dictionary of {ticker: cost_per_share}
        """
        self.holdings = holdings
        self.cost_basis = cost_basis or {}
        self._cache = {}
    
    @property
    def value(self) -> float:
        """Get total portfolio value."""
        total = 0.0
        for ticker, shares in self.holdings.items():
            try:
                info = get_yfinance_data(ticker)
                price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                total += price * shares
            except:
                continue
        return total
    
    @property
    def allocation(self) -> Dict[str, float]:
        """Get allocation percentages by ticker."""
        total_value = self.value
        if total_value == 0:
            return {}
        
        allocations = {}
        for ticker, shares in self.holdings.items():
            try:
                info = get_yfinance_data(ticker)
                price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                ticker_value = price * shares
                allocations[ticker] = (ticker_value / total_value) * 100
            except:
                allocations[ticker] = 0.0
        
        return allocations
    
    @property
    def returns(self) -> Optional[float]:
        """Get total return % (requires cost_basis)."""
        if not self.cost_basis:
            return None
        
        total_cost = sum(
            self.cost_basis.get(ticker, 0) * shares
            for ticker, shares in self.holdings.items()
        )
        
        if total_cost == 0:
            return None
        
        current_value = self.value
        return ((current_value - total_cost) / total_cost) * 100
    
    @property
    def sharpe_ratio(self) -> Optional[float]:
        """
        Calculate Sharpe ratio (simplified).
        Uses 6-month daily returns, assumes 0% risk-free rate.
        """
        try:
            # Get returns for each stock
            returns_df = self._get_portfolio_returns()
            if returns_df is None or len(returns_df) < 30:
                return None
            
            # Calculate portfolio daily returns
            portfolio_returns = returns_df.mean(axis=1)
            
            # Sharpe ratio = mean / std
            mean_return = portfolio_returns.mean()
            std_return = portfolio_returns.std()
            
            if std_return == 0:
                return None
            
            # Annualize (252 trading days)
            sharpe = (mean_return / std_return) * np.sqrt(252)
            return sharpe
        except:
            return None
    
    @property
    def volatility(self) -> Optional[float]:
        """Get annualized volatility."""
        try:
            returns_df = self._get_portfolio_returns()
            if returns_df is None or len(returns_df) < 30:
                return None
            
            portfolio_returns = returns_df.mean(axis=1)
            daily_vol = portfolio_returns.std()
            
            # Annualize
            annual_vol = daily_vol * np.sqrt(252)
            return annual_vol * 100  # As percentage
        except:
            return None
    
    @property
    def sector_allocation(self) -> Dict[str, float]:
        """Get allocation by sector."""
        sectors = {}
        total_value = self.value
        
        if total_value == 0:
            return {}
        
        for ticker, shares in self.holdings.items():
            try:
                info = get_yfinance_data(ticker)
                sector = info.get('sector', 'Unknown')
                price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                ticker_value = price * shares
                
                if sector in sectors:
                    sectors[sector] += ticker_value
                else:
                    sectors[sector] = ticker_value
            except:
                continue
        
        # Convert to percentages
        return {
            sector: (value / total_value) * 100
            for sector, value in sectors.items()
        }
    
    @property
    def concentration(self) -> float:
        """
        Get portfolio concentration (Herfindahl index).
        0-100, where higher = more concentrated.
        """
        allocations = self.allocation
        if not allocations:
            return 0.0
        
        # Sum of squared weights
        concentration = sum((weight / 100) ** 2 for weight in allocations.values())
        return concentration * 100
    
    def add(self, ticker: str, shares: float, cost_per_share: Optional[float] = None):
        """
        Add position to portfolio.
        
        Args:
            ticker: Stock ticker
            shares: Number of shares
            cost_per_share: Cost basis per share (optional)
        """
        if ticker in self.holdings:
            self.holdings[ticker] += shares
        else:
            self.holdings[ticker] = shares
        
        if cost_per_share:
            self.cost_basis[ticker] = cost_per_share
        
        # Clear cache
        self._cache = {}
    
    def remove(self, ticker: str):
        """Remove position from portfolio."""
        if ticker in self.holdings:
            del self.holdings[ticker]
        if ticker in self.cost_basis:
            del self.cost_basis[ticker]
        
        # Clear cache
        self._cache = {}
    
    def _get_portfolio_returns(self) -> Optional[pd.DataFrame]:
        """Get daily returns DataFrame for portfolio."""
        if 'returns_df' in self._cache:
            return self._cache['returns_df']
        
        returns_data = {}
        
        for ticker in self.holdings.keys():
            try:
                history_dict = get_yfinance_stock_history(ticker, period="6mo", interval="1d")
                df = pd.DataFrame.from_dict(history_dict, orient='index')
                df.index = pd.to_datetime(df.index)
                
                # Calculate daily returns
                df['Returns'] = df['Close'].pct_change()
                returns_data[ticker] = df['Returns']
            except:
                continue
        
        if not returns_data:
            return None
        
        returns_df = pd.DataFrame(returns_data)
        returns_df = returns_df.dropna()
        
        self._cache['returns_df'] = returns_df
        return returns_df
    
    def __repr__(self) -> str:
        """String representation."""
        num_holdings = len(self.holdings)
        return f"Portfolio(holdings={num_holdings}, value=${self.value:,.2f})"
