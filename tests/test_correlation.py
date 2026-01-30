"""
Tests for correlation analysis module.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from investormate.analysis.correlation import Correlation
from investormate.utils.exceptions import DataFetchError


class TestCorrelation:
    """Test cases for Correlation class."""
    
    def test_initialization_valid(self):
        """Test valid initialization."""
        corr = Correlation(["AAPL", "GOOGL"], period="1y")
        assert corr.tickers == ["AAPL", "GOOGL"]
        assert corr.period == "1y"
        assert corr.interval == "1d"
    
    def test_initialization_empty_tickers(self):
        """Test initialization with empty tickers list."""
        with pytest.raises(ValueError, match="At least 2 tickers are required"):
            Correlation([])
    
    def test_initialization_single_ticker(self):
        """Test initialization with single ticker."""
        with pytest.raises(ValueError, match="At least 2 tickers are required"):
            Correlation(["AAPL"])
    
    def test_initialization_custom_interval(self):
        """Test initialization with custom interval."""
        corr = Correlation(["AAPL", "GOOGL"], period="6mo", interval="1wk")
        assert corr.period == "6mo"
        assert corr.interval == "1wk"
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_fetch_price_data(self, mock_ticker):
        """Test fetching price data."""
        # Mock price data
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        mock_hist_aapl = pd.DataFrame({
            'Close': np.linspace(150, 160, 10)
        }, index=dates)
        mock_hist_googl = pd.DataFrame({
            'Close': np.linspace(100, 110, 10)
        }, index=dates)
        
        # Setup mock
        def mock_ticker_factory(ticker):
            mock = Mock()
            if 'AAPL' in ticker:
                mock.history.return_value = mock_hist_aapl
            else:
                mock.history.return_value = mock_hist_googl
            return mock
        
        mock_ticker.side_effect = mock_ticker_factory
        
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        prices = corr._fetch_price_data()
        
        assert isinstance(prices, pd.DataFrame)
        assert 'AAPL' in prices.columns
        assert 'GOOGL' in prices.columns
        assert len(prices) == 10
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_fetch_price_data_failure(self, mock_ticker):
        """Test handling of data fetch failures."""
        # Mock empty data
        mock_ticker.return_value.history.return_value = pd.DataFrame()
        
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        with pytest.raises(DataFetchError, match="Failed to fetch data for all tickers"):
            corr._fetch_price_data()
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_get_returns(self, mock_ticker):
        """Test calculation of daily returns."""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        mock_hist = pd.DataFrame({
            'Close': [100, 102, 101, 103, 105, 104, 106, 108, 107, 110]
        }, index=dates)
        
        mock_ticker.return_value.history.return_value = mock_hist
        
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        returns = corr._get_returns()
        
        assert isinstance(returns, pd.DataFrame)
        assert len(returns) == 9  # One less than prices due to pct_change
        assert 'AAPL' in returns.columns
        assert 'GOOGL' in returns.columns
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_matrix_pearson(self, mock_ticker):
        """Test correlation matrix calculation with Pearson method."""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        
        # Create correlated data
        base = np.random.randn(100).cumsum()
        prices_aapl = 100 + base + np.random.randn(100) * 0.1
        prices_googl = 150 + base + np.random.randn(100) * 0.1
        
        mock_hist_aapl = pd.DataFrame({'Close': prices_aapl}, index=dates)
        mock_hist_googl = pd.DataFrame({'Close': prices_googl}, index=dates)
        
        def mock_ticker_factory(ticker):
            mock = Mock()
            if 'AAPL' in ticker:
                mock.history.return_value = mock_hist_aapl
            else:
                mock.history.return_value = mock_hist_googl
            return mock
        
        mock_ticker.side_effect = mock_ticker_factory
        
        corr = Correlation(["AAPL", "GOOGL"], period="1y")
        matrix = corr.matrix(method='pearson')
        
        assert isinstance(matrix, pd.DataFrame)
        assert matrix.shape == (2, 2)
        assert 'AAPL' in matrix.columns
        assert 'GOOGL' in matrix.columns
        
        # Check diagonal is 1 (self-correlation)
        assert matrix.loc['AAPL', 'AAPL'] == pytest.approx(1.0)
        assert matrix.loc['GOOGL', 'GOOGL'] == pytest.approx(1.0)
        
        # Check symmetry
        assert matrix.loc['AAPL', 'GOOGL'] == pytest.approx(matrix.loc['GOOGL', 'AAPL'])
        
        # Check correlation is high (we created correlated data)
        assert matrix.loc['AAPL', 'GOOGL'] > 0.8
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_matrix_spearman(self, mock_ticker):
        """Test correlation matrix with Spearman method."""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        mock_hist = pd.DataFrame({
            'Close': np.linspace(100, 150, 50)
        }, index=dates)
        
        mock_ticker.return_value.history.return_value = mock_hist
        
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        matrix = corr.matrix(method='spearman')
        
        assert isinstance(matrix, pd.DataFrame)
        assert matrix.shape == (2, 2)
    
    def test_matrix_invalid_method(self):
        """Test matrix calculation with invalid method."""
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        with pytest.raises(ValueError, match="Method must be one of"):
            corr.matrix(method='invalid')
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_find_pairs(self, mock_ticker):
        """Test finding correlated pairs."""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        
        # Create three stocks with different correlations
        base = np.random.randn(100).cumsum()
        aapl = 100 + base + np.random.randn(100) * 0.1
        googl = 150 + base + np.random.randn(100) * 0.1  # High correlation with AAPL
        tsla = 200 + np.random.randn(100).cumsum()  # Low correlation
        
        def mock_ticker_factory(ticker):
            mock = Mock()
            if 'AAPL' in ticker:
                mock.history.return_value = pd.DataFrame({'Close': aapl}, index=dates)
            elif 'GOOGL' in ticker:
                mock.history.return_value = pd.DataFrame({'Close': googl}, index=dates)
            else:
                mock.history.return_value = pd.DataFrame({'Close': tsla}, index=dates)
            return mock
        
        mock_ticker.side_effect = mock_ticker_factory
        
        corr = Correlation(["AAPL", "GOOGL", "TSLA"], period="1y")
        pairs = corr.find_pairs(threshold=0.7)
        
        assert isinstance(pairs, list)
        
        # Should find at least one highly correlated pair
        if pairs:
            ticker1, ticker2, correlation = pairs[0]
            assert ticker1 in ["AAPL", "GOOGL", "TSLA"]
            assert ticker2 in ["AAPL", "GOOGL", "TSLA"]
            assert ticker1 != ticker2
            assert isinstance(correlation, float)
            assert abs(correlation) >= 0.7
    
    def test_find_pairs_invalid_threshold(self):
        """Test find_pairs with invalid threshold."""
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        with pytest.raises(ValueError, match="Threshold must be between 0 and 1"):
            corr.find_pairs(threshold=1.5)
        
        with pytest.raises(ValueError, match="Threshold must be between 0 and 1"):
            corr.find_pairs(threshold=-0.5)
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_find_diversification_candidates(self, mock_ticker):
        """Test finding diversification candidates."""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        
        # Create stocks with specific correlation patterns
        base = np.random.randn(100).cumsum()
        aapl = 100 + base
        googl = 150 + base  # High correlation with AAPL
        gld = 200 - base * 0.5  # Negative correlation with AAPL/GOOGL
        
        def mock_ticker_factory(ticker):
            mock = Mock()
            if 'AAPL' in ticker:
                mock.history.return_value = pd.DataFrame({'Close': aapl}, index=dates)
            elif 'GOOGL' in ticker:
                mock.history.return_value = pd.DataFrame({'Close': googl}, index=dates)
            else:
                mock.history.return_value = pd.DataFrame({'Close': gld}, index=dates)
            return mock
        
        mock_ticker.side_effect = mock_ticker_factory
        
        corr = Correlation(["AAPL", "GOOGL", "GLD"], period="1y")
        candidates = corr.find_diversification_candidates(
            portfolio=["AAPL", "GOOGL"],
            universe=["GLD"],
            max_correlation=0.5
        )
        
        assert isinstance(candidates, list)
        if candidates:
            ticker, avg_corr = candidates[0]
            assert ticker == "GLD"
            assert isinstance(avg_corr, float)
            assert abs(avg_corr) <= 0.5
    
    def test_find_diversification_empty_portfolio(self):
        """Test diversification with empty portfolio."""
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        with pytest.raises(ValueError, match="Portfolio cannot be empty"):
            corr.find_diversification_candidates(
                portfolio=[],
                universe=["GLD"],
                max_correlation=0.3
            )
    
    def test_find_diversification_empty_universe(self):
        """Test diversification with empty universe."""
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        with pytest.raises(ValueError, match="Universe cannot be empty"):
            corr.find_diversification_candidates(
                portfolio=["AAPL"],
                universe=[],
                max_correlation=0.3
            )
    
    def test_find_diversification_invalid_max_correlation(self):
        """Test diversification with invalid max_correlation."""
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        with pytest.raises(ValueError, match="max_correlation must be between 0 and 1"):
            corr.find_diversification_candidates(
                portfolio=["AAPL"],
                universe=["GOOGL"],
                max_correlation=1.5
            )
    
    def test_find_diversification_missing_portfolio_ticker(self):
        """Test diversification with portfolio ticker not in correlation data."""
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        with pytest.raises(ValueError, match="Portfolio tickers not in correlation data"):
            corr.find_diversification_candidates(
                portfolio=["TSLA"],  # Not in correlation tickers
                universe=["AAPL"],
                max_correlation=0.3
            )
    
    def test_find_diversification_missing_universe_ticker(self):
        """Test diversification with universe ticker not in correlation data."""
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        with pytest.raises(ValueError, match="Universe tickers not in correlation data"):
            corr.find_diversification_candidates(
                portfolio=["AAPL"],
                universe=["TSLA"],  # Not in correlation tickers
                max_correlation=0.3
            )
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_get_statistics(self, mock_ticker):
        """Test getting correlation statistics."""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        
        def mock_ticker_factory(ticker):
            mock = Mock()
            mock.history.return_value = pd.DataFrame({
                'Close': np.linspace(100, 150, 50)
            }, index=dates)
            return mock
        
        mock_ticker.side_effect = mock_ticker_factory
        
        corr = Correlation(["AAPL", "GOOGL", "MSFT"], period="1mo")
        stats = corr.get_statistics()
        
        assert isinstance(stats, dict)
        assert 'ticker_count' in stats
        assert 'tickers' in stats
        assert 'date_range' in stats
        assert 'data_points' in stats
        assert 'avg_correlation' in stats
        assert 'max_correlation' in stats
        assert 'min_correlation' in stats
        
        assert stats['ticker_count'] == 3
        assert len(stats['tickers']) == 3
        assert 'start' in stats['date_range']
        assert 'end' in stats['date_range']
        assert stats['data_points'] == 50
        
        # Check max/min correlation tuples
        if stats['max_correlation']:
            assert len(stats['max_correlation']) == 3
        if stats['min_correlation']:
            assert len(stats['min_correlation']) == 3
    
    def test_repr(self):
        """Test string representation."""
        corr = Correlation(["AAPL", "GOOGL"], period="1y")
        repr_str = repr(corr)
        
        assert "Correlation" in repr_str
        assert "AAPL" in repr_str
        assert "GOOGL" in repr_str
        assert "1y" in repr_str
    
    @patch('investormate.analysis.correlation.yf.Ticker')
    def test_caching(self, mock_ticker):
        """Test that price data is cached."""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        mock_hist = pd.DataFrame({
            'Close': np.linspace(100, 110, 10)
        }, index=dates)
        
        mock_ticker.return_value.history.return_value = mock_hist
        
        corr = Correlation(["AAPL", "GOOGL"], period="1mo")
        
        # First call should fetch data
        prices1 = corr._fetch_price_data()
        call_count_1 = mock_ticker.call_count
        
        # Second call should use cache
        prices2 = corr._fetch_price_data()
        call_count_2 = mock_ticker.call_count
        
        # Verify caching worked (no additional calls)
        assert call_count_1 == call_count_2
        assert prices1.equals(prices2)
