"""
Multi-stock correlation analysis for InvestorMate.
Helps identify diversification opportunities and correlated stock pairs.
"""

from typing import List, Dict, Tuple, Optional
import pandas as pd
import yfinance as yf

from ..data.constants import get_ticker_format
from ..utils.exceptions import DataFetchError


class Correlation:
    """
    Analyze correlations between multiple stocks for portfolio diversification.
    
    The Correlation class calculates correlation matrices using daily returns
    (not prices) for accuracy. It supports finding highly correlated pairs
    and identifying diversification candidates.
    
    Example:
        >>> corr = Correlation(["AAPL", "GOOGL", "MSFT"], period="1y")
        >>> matrix = corr.matrix()
        >>> pairs = corr.find_pairs(threshold=0.8)
        >>> diversifiers = corr.find_diversification_candidates(
        ...     portfolio=["AAPL", "GOOGL"],
        ...     universe=["GLD", "TLT", "BTC-USD"],
        ...     max_correlation=0.3
        ... )
    """
    
    def __init__(self, tickers: List[str], period: str = "1y", interval: str = "1d"):
        """
        Initialize Correlation analyzer.
        
        Args:
            tickers: List of stock ticker symbols
            period: Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1d, 1wk, 1mo recommended for correlation analysis)
            
        Raises:
            ValueError: If tickers list is empty or has less than 2 tickers
        """
        if not tickers or len(tickers) < 2:
            raise ValueError("At least 2 tickers are required for correlation analysis")
        
        self.tickers = tickers
        self.period = period
        self.interval = interval
        self._returns = None
        self._prices = None
    
    def _fetch_price_data(self) -> pd.DataFrame:
        """
        Fetch historical price data for all tickers.
        
        Returns:
            DataFrame with tickers as columns and dates as index
            
        Raises:
            DataFetchError: If data fetching fails for any ticker
        """
        if self._prices is not None:
            return self._prices
        
        price_data = {}
        failed_tickers = []
        
        for ticker in self.tickers:
            try:
                formatted_ticker = get_ticker_format(ticker)
                yf_ticker = yf.Ticker(formatted_ticker)
                hist = yf_ticker.history(period=self.period, interval=self.interval)
                
                if hist.empty:
                    failed_tickers.append(ticker)
                    continue
                
                # Use Close price for correlation analysis
                price_data[ticker] = hist['Close']
            except Exception as e:
                failed_tickers.append(ticker)
                continue
        
        if not price_data:
            raise DataFetchError(
                f"Failed to fetch data for all tickers. Failed: {', '.join(failed_tickers)}"
            )
        
        if failed_tickers:
            print(f"Warning: Failed to fetch data for: {', '.join(failed_tickers)}")
        
        # Create DataFrame with aligned dates
        self._prices = pd.DataFrame(price_data)
        
        # Drop rows with any NaN values to ensure clean correlation calculation
        self._prices = self._prices.dropna()
        
        if self._prices.empty:
            raise DataFetchError("No overlapping data found for the given tickers")
        
        return self._prices
    
    def _get_returns(self) -> pd.DataFrame:
        """
        Calculate daily returns for all tickers.
        
        Returns:
            DataFrame with daily returns (tickers as columns)
        """
        if self._returns is not None:
            return self._returns
        
        prices = self._fetch_price_data()
        
        # Calculate percentage change (daily returns)
        self._returns = prices.pct_change().dropna()
        
        if self._returns.empty:
            raise DataFetchError("Not enough data to calculate returns")
        
        return self._returns
    
    def matrix(self, method: str = 'pearson') -> pd.DataFrame:
        """
        Calculate correlation matrix for all stocks.
        
        Args:
            method: Correlation method ('pearson', 'spearman', 'kendall')
                   - pearson: Standard correlation coefficient (linear relationships)
                   - spearman: Rank-based correlation (monotonic relationships)
                   - kendall: Tau correlation (ordinal relationships)
        
        Returns:
            DataFrame with correlation matrix (values from -1 to 1)
            
        Raises:
            ValueError: If method is not supported
        """
        valid_methods = ['pearson', 'spearman', 'kendall']
        if method not in valid_methods:
            raise ValueError(f"Method must be one of {valid_methods}")
        
        returns = self._get_returns()
        return returns.corr(method=method)
    
    def find_pairs(self, threshold: float = 0.7, method: str = 'pearson') -> List[Tuple[str, str, float]]:
        """
        Find highly correlated stock pairs.
        
        Args:
            threshold: Minimum correlation coefficient (0 to 1)
            method: Correlation method ('pearson', 'spearman', 'kendall')
        
        Returns:
            List of tuples (ticker1, ticker2, correlation) sorted by correlation (highest first)
            
        Example:
            >>> corr.find_pairs(threshold=0.8)
            [('GOOGL', 'MSFT', 0.85), ('AAPL', 'MSFT', 0.82)]
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        corr_matrix = self.matrix(method=method)
        pairs = []
        
        # Iterate through upper triangle of correlation matrix (avoid duplicates)
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                ticker1 = corr_matrix.columns[i]
                ticker2 = corr_matrix.columns[j]
                correlation = corr_matrix.iloc[i, j]
                
                # Check if correlation meets threshold
                if abs(correlation) >= threshold:
                    pairs.append((ticker1, ticker2, round(correlation, 4)))
        
        # Sort by absolute correlation value (descending)
        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        return pairs
    
    def find_diversification_candidates(
        self,
        portfolio: List[str],
        universe: List[str],
        max_correlation: float = 0.3,
        method: str = 'pearson'
    ) -> List[Tuple[str, float]]:
        """
        Find stocks that provide diversification to an existing portfolio.
        
        This method identifies stocks from a universe that have low correlation
        with the portfolio stocks, making them good diversification candidates.
        
        Args:
            portfolio: List of tickers currently in portfolio
            universe: List of tickers to evaluate as diversification candidates
            max_correlation: Maximum average correlation with portfolio (0 to 1)
            method: Correlation method ('pearson', 'spearman', 'kendall')
        
        Returns:
            List of tuples (ticker, avg_correlation) sorted by correlation (lowest first)
            Only includes tickers with average correlation <= max_correlation
            
        Example:
            >>> corr = Correlation(["AAPL", "GOOGL", "GLD", "TLT"], period="1y")
            >>> diversifiers = corr.find_diversification_candidates(
            ...     portfolio=["AAPL", "GOOGL"],
            ...     universe=["GLD", "TLT"],
            ...     max_correlation=0.3
            ... )
            [('TLT', -0.15), ('GLD', 0.05)]
        """
        if not portfolio:
            raise ValueError("Portfolio cannot be empty")
        
        if not universe:
            raise ValueError("Universe cannot be empty")
        
        if not 0 <= max_correlation <= 1:
            raise ValueError("max_correlation must be between 0 and 1")
        
        # Validate that all portfolio tickers are in our data
        missing_portfolio = [t for t in portfolio if t not in self.tickers]
        if missing_portfolio:
            raise ValueError(f"Portfolio tickers not in correlation data: {missing_portfolio}")
        
        # Validate that all universe tickers are in our data
        missing_universe = [t for t in universe if t not in self.tickers]
        if missing_universe:
            raise ValueError(f"Universe tickers not in correlation data: {missing_universe}")
        
        corr_matrix = self.matrix(method=method)
        candidates = []
        
        for candidate in universe:
            # Don't recommend stocks already in portfolio
            if candidate in portfolio:
                continue
            
            # Calculate average correlation with portfolio stocks
            correlations = [corr_matrix.loc[candidate, portfolio_stock] 
                          for portfolio_stock in portfolio]
            avg_correlation = sum(correlations) / len(correlations)
            
            # Only include if below threshold
            if abs(avg_correlation) <= max_correlation:
                candidates.append((candidate, round(avg_correlation, 4)))
        
        # Sort by absolute correlation (lowest first = best diversification)
        candidates.sort(key=lambda x: abs(x[1]))
        
        return candidates
    
    def get_statistics(self) -> Dict:
        """
        Get summary statistics about the correlation analysis.
        
        Returns:
            Dictionary with statistics including:
            - ticker_count: Number of tickers analyzed
            - date_range: Start and end dates of data
            - data_points: Number of data points per ticker
            - avg_correlation: Average correlation across all pairs
            - max_correlation: Highest correlation pair
            - min_correlation: Lowest correlation pair
        """
        prices = self._fetch_price_data()
        corr_matrix = self.matrix()
        
        # Calculate average correlation (excluding diagonal)
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                correlations.append(corr_matrix.iloc[i, j])
        
        avg_corr = sum(correlations) / len(correlations) if correlations else 0
        max_corr = max(correlations) if correlations else 0
        min_corr = min(correlations) if correlations else 0
        
        # Find tickers for max and min correlation
        max_pair = None
        min_pair = None
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr = corr_matrix.iloc[i, j]
                if corr == max_corr:
                    max_pair = (corr_matrix.columns[i], corr_matrix.columns[j], round(corr, 4))
                if corr == min_corr:
                    min_pair = (corr_matrix.columns[i], corr_matrix.columns[j], round(corr, 4))
        
        return {
            'ticker_count': len(prices.columns),
            'tickers': list(prices.columns),
            'date_range': {
                'start': str(prices.index[0].date()),
                'end': str(prices.index[-1].date())
            },
            'data_points': len(prices),
            'avg_correlation': round(avg_corr, 4),
            'max_correlation': max_pair,
            'min_correlation': min_pair
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Correlation(tickers={self.tickers}, period='{self.period}')"
