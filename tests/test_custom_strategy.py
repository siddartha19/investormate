"""
Tests for custom strategy module.
"""

import pytest
from unittest.mock import Mock, patch
from investormate.core.custom_strategy import CustomStrategy
from investormate.core.stock import Stock


class TestCustomStrategy:
    """Test cases for CustomStrategy class."""

    def test_initialization_empty(self):
        """Test initialization with no arguments."""
        strategy = CustomStrategy()
        assert strategy.filter_func is None
        assert strategy.rank_func is None
        assert strategy.universe == []

    def test_initialization_with_args(self):
        """Test initialization with filter and rank functions."""
        def my_filter(stock):
            return True

        def my_rank(stock):
            return 1.0

        strategy = CustomStrategy(
            filter_func=my_filter,
            rank_func=my_rank,
            universe=["AAPL", "GOOGL"]
        )
        assert strategy.filter_func == my_filter
        assert strategy.rank_func == my_rank
        assert strategy.universe == ["AAPL", "GOOGL"]

    def test_add_filter_returns_self(self):
        """Test add_filter returns self for chaining."""
        strategy = CustomStrategy()
        result = strategy.add_filter("ratios.pe", min=10, max=25)
        assert result is strategy
        assert len(strategy._filters) == 1
        assert strategy._filters[0]["attribute"] == "ratios.pe"
        assert strategy._filters[0]["min"] == 10
        assert strategy._filters[0]["max"] == 25

    def test_rank_by_returns_self(self):
        """Test rank_by returns self for chaining."""
        strategy = CustomStrategy()
        result = strategy.rank_by("ratios.roe")
        assert result is strategy
        assert len(strategy._rank_criteria) == 1
        assert strategy._rank_criteria[0]["criteria"] == "ratios.roe"

    def test_apply_returns_self(self):
        """Test apply returns self for chaining."""
        strategy = CustomStrategy()
        result = strategy.apply(universe=["AAPL", "GOOGL"])
        assert result is strategy
        assert strategy.universe == ["AAPL", "GOOGL"]

    def test_run_empty_universe(self):
        """Test run with empty universe returns empty list."""
        strategy = CustomStrategy(universe=[])
        results = strategy.run()
        assert results == []

    def test_run_with_limit(self):
        """Test run with limit parameter."""
        def always_pass(stock):
            return True

        def rank_one(stock):
            return 1.0

        strategy = CustomStrategy(
            filter_func=always_pass,
            rank_func=rank_one,
            universe=["AAPL", "GOOGL", "MSFT"]
        )
        with patch("investormate.core.custom_strategy.Stock") as MockStock:
            mock_stock = Mock()
            mock_stock.name = "Test"
            mock_stock.price = 100
            MockStock.return_value = mock_stock

            results = strategy.run(limit=2)
            assert len(results) <= 2

    def test_passes_filters_function_based(self):
        """Test _passes_filters with function-based filter."""
        def my_filter(stock):
            return stock.ticker == "AAPL"

        strategy = CustomStrategy(filter_func=my_filter)
        mock_stock = Mock()
        mock_stock.ticker = "AAPL"
        assert strategy._passes_filters(mock_stock) is True

        mock_stock.ticker = "GOOGL"
        assert strategy._passes_filters(mock_stock) is False

    def test_passes_filters_builder_pattern(self):
        """Test _passes_filters with builder pattern."""
        strategy = CustomStrategy().add_filter("ratios.pe", min=10, max=25)
        mock_stock = Mock()
        mock_stock.ratios = Mock()
        mock_stock.ratios.pe = 15
        assert strategy._passes_filters(mock_stock) is True

        mock_stock.ratios.pe = 5
        assert strategy._passes_filters(mock_stock) is False

    def test_get_attribute_value(self):
        """Test _get_attribute_value with dot notation."""
        strategy = CustomStrategy()
        mock_stock = Mock()
        mock_stock.ratios = Mock()
        mock_stock.ratios.pe = 20
        value = strategy._get_attribute_value(mock_stock, "ratios.pe")
        assert value == 20

    def test_repr(self):
        """Test string representation."""
        strategy = CustomStrategy(universe=["AAPL", "GOOGL"])
        repr_str = repr(strategy)
        assert "CustomStrategy" in repr_str
        assert "2" in repr_str
