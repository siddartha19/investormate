"""
Tests for backtesting framework.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from investormate.backtest import Backtest, Strategy, BacktestEngine, BacktestResults
from investormate.utils.exceptions import ValidationError


class SimpleStrategy(Strategy):
    """Simple test strategy."""

    def initialize(self):
        self.buy_count = 0
        self.sell_count = 0

    def on_data(self, data):
        # Simple logic: buy on first bar, sell on last
        pass


class TestStrategy:
    """Test Strategy base class."""

    def test_strategy_abstract_methods(self):
        """Test that Strategy requires abstract methods."""
        with pytest.raises(TypeError):
            Strategy()

    def test_simple_strategy_initialization(self):
        """Test simple strategy can be instantiated."""
        strategy = SimpleStrategy()
        strategy.initialize()
        assert strategy.buy_count == 0

    def test_strategy_requires_engine_for_trading(self):
        """Test that buy/sell require engine."""
        strategy = SimpleStrategy()
        strategy.initialize()

        with pytest.raises(RuntimeError, match="Strategy must be run within a backtest"):
            strategy.buy(shares=10)

        with pytest.raises(RuntimeError, match="Strategy must be run within a backtest"):
            strategy.has_position


class TestBacktestResults:
    """Test BacktestResults class."""

    def test_results_from_dict(self):
        """Test creating results from dictionary."""
        results_dict = {
            "trades": [
                {"date": "2023-01-15", "type": "BUY", "shares": 100, "price": 150, "commission": 0.15},
                {"date": "2023-06-15", "type": "SELL", "shares": 100, "price": 180, "commission": 0.18, "pnl": 2982.67},
            ],
            "equity_history": [
                {"date": "2023-01-01", "equity": 10000, "cash": 10000, "position_value": 0, "position_size": 0},
                {"date": "2023-01-15", "equity": 10000, "cash": 8499.85, "position_value": 15000, "position_size": 100},
                {"date": "2023-06-15", "equity": 11482.67, "cash": 11482.49, "position_value": 0, "position_size": 0},
            ],
            "final_equity": 11482.49,
            "initial_capital": 10000,
            "ticker": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        }
        results = BacktestResults(results_dict)
        metrics = results._calculate_metrics()
        assert results.total_return == pytest.approx(14.82, rel=0.1)
        assert results.total_trades == 1
        assert results.win_rate == 100.0
        assert metrics["initial_capital"] == 10000
        assert metrics["final_equity"] == pytest.approx(11482.49, rel=0.01)

    def test_results_no_trades(self):
        """Test results with no trades."""
        results_dict = {
            "trades": [],
            "equity_history": [
                {"date": "2023-01-01", "equity": 10000, "cash": 10000, "position_value": 0, "position_size": 0},
                {"date": "2023-12-31", "equity": 10000, "cash": 10000, "position_value": 0, "position_size": 0},
            ],
            "final_equity": 10000,
            "initial_capital": 10000,
            "ticker": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        }
        results = BacktestResults(results_dict)
        assert results.total_return == 0.0
        assert results.total_trades == 0
        assert results.win_rate == 0.0

    def test_equity_curve_property(self):
        """Test equity_curve returns DataFrame."""
        results_dict = {
            "trades": [],
            "equity_history": [
                {"date": "2023-01-01", "equity": 10000, "cash": 10000, "position_value": 0, "position_size": 0},
            ],
            "final_equity": 10000,
            "initial_capital": 10000,
            "ticker": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        }
        results = BacktestResults(results_dict)
        equity = results.equity_curve
        assert isinstance(equity, pd.DataFrame)
        assert "equity" in equity.columns

    def test_summary_method(self):
        """Test summary() returns string."""
        results_dict = {
            "trades": [],
            "equity_history": [
                {"date": "2023-01-01", "equity": 10000, "cash": 10000, "position_value": 0, "position_size": 0},
                {"date": "2023-12-31", "equity": 11000, "cash": 11000, "position_value": 0, "position_size": 0},
            ],
            "final_equity": 11000,
            "initial_capital": 10000,
            "ticker": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        }
        results = BacktestResults(results_dict)
        summary = results.summary()
        assert "Backtest Results" in summary
        assert "Total Return" in summary
        assert "10.00" in summary or "10" in summary


class TestBacktest:
    """Test Backtest wrapper class."""

    def test_backtest_initialization(self):
        """Test Backtest initialization."""
        bt = Backtest(
            strategy=SimpleStrategy,
            ticker="AAPL",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=10000,
        )
        assert bt.ticker == "AAPL"
        assert bt.initial_capital == 10000
        assert bt.strategy == SimpleStrategy

    def test_backtest_repr(self):
        """Test Backtest string representation."""
        bt = Backtest(SimpleStrategy, "AAPL", "2023-01-01", "2023-12-31")
        repr_str = repr(bt)
        assert "Backtest" in repr_str
        assert "AAPL" in repr_str
        assert "SimpleStrategy" in repr_str

    def test_backtest_invalid_date_range_raises(self):
        """Test Backtest raises ValidationError when start_date > end_date."""
        with pytest.raises(ValidationError, match="start_date.*before or equal to end_date"):
            Backtest(
                strategy=SimpleStrategy,
                ticker="AAPL",
                start_date="2023-12-31",
                end_date="2023-01-01",
            )

    def test_backtest_invalid_date_format_raises(self):
        """Test Backtest raises ValidationError for invalid date format."""
        with pytest.raises(ValidationError):
            Backtest(
                strategy=SimpleStrategy,
                ticker="AAPL",
                start_date="01-01-2023",
                end_date="2023-12-31",
            )
