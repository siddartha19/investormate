"""
Integration tests for v0.2.0 features.
Tests cross-feature functionality and end-to-end workflows.
"""

import pytest
from unittest.mock import patch, Mock
from investormate import (
    Correlation,
    Stock,
    CustomStrategy,
    Backtest,
    Strategy,
)


class TestCorrelationIntegration:
    """Integration tests for Correlation with other features."""

    @patch("investormate.analysis.correlation.yf.Ticker")
    def test_correlation_with_portfolio_universe(self, mock_ticker):
        """Test correlation used for portfolio diversification."""
        import pandas as pd
        import numpy as np

        dates = pd.date_range("2024-01-01", periods=50, freq="D")
        base = np.random.randn(50).cumsum()

        def mock_ticker_factory(ticker):
            m = Mock()
            m.history.return_value = pd.DataFrame(
                {"Close": 100 + base + np.random.randn(50) * 0.1}, index=dates
            )
            return m

        mock_ticker.side_effect = mock_ticker_factory

        corr = Correlation(["AAPL", "GOOGL", "MSFT", "GLD", "TLT"], period="1mo")
        candidates = corr.find_diversification_candidates(
            portfolio=["AAPL", "GOOGL", "MSFT"],
            universe=["GLD", "TLT"],
            max_correlation=0.5,
        )
        assert isinstance(candidates, list)


class TestCustomStrategyIntegration:
    """Integration tests for CustomStrategy."""

    def test_custom_strategy_with_stock_data(self):
        """Test CustomStrategy runs with real Stock objects."""
        def value_filter(stock):
            try:
                pe = stock.ratios.pe
                return pe is not None and 0 < pe < 100
            except Exception:
                return False

        def value_rank(stock):
            try:
                roe = stock.ratios.roe
                return roe if roe else 0
            except Exception:
                return 0

        strategy = CustomStrategy(
            filter_func=value_filter,
            rank_func=value_rank,
            universe=["AAPL", "MSFT"],
        )
        results = strategy.run(limit=5)
        assert isinstance(results, list)


class TestBacktestIntegration:
    """Integration tests for Backtesting."""

    class DummyStrategy(Strategy):
        def initialize(self):
            pass

        def on_data(self, data):
            pass

    def test_backtest_imports(self):
        """Test all backtest components import correctly."""
        from investormate.backtest import Backtest, Strategy, BacktestEngine, BacktestResults
        assert Backtest is not None
        assert Strategy is not None
        assert BacktestEngine is not None
        assert BacktestResults is not None

    def test_backtest_creates_results(self):
        """Test Backtest.run() returns BacktestResults."""
        bt = Backtest(
            strategy=self.DummyStrategy,
            ticker="AAPL",
            start_date="2023-01-01",
            end_date="2023-06-01",
            initial_capital=10000,
        )
        with patch("yfinance.Ticker") as mock_ticker:
            import pandas as pd
            dates = pd.date_range("2023-01-01", periods=100, freq="D")
            mock_hist = pd.DataFrame(
                {
                    "Open": 150,
                    "High": 155,
                    "Low": 148,
                    "Close": 152,
                    "Volume": 1000000,
                },
                index=dates,
            )
            mock_ticker.return_value.history.return_value = mock_hist

            results = bt.run()
            assert results is not None
            assert hasattr(results, "total_return")
            assert hasattr(results, "equity_curve")
            assert hasattr(results, "summary")


class TestStockSentimentIntegration:
    """Integration tests for Stock.sentiment property."""

    def test_stock_has_sentiment_property(self):
        """Test Stock has sentiment property."""
        stock = Stock("AAPL")
        assert hasattr(stock, "sentiment")
        assert stock.sentiment is not None
        assert stock.sentiment.ticker == "AAPL"
