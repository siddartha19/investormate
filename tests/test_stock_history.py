"""Tests for Stock.history() with source_trace and adjusted."""

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from investormate import Stock, HistoryResult
from investormate.core.stock import Stock as StockClass


@patch("investormate.core.stock.get_yfinance_stock_history")
def test_stock_history_source_trace_returns_history_result(mock_fetcher):
    """Stock.history(source_trace=True) returns HistoryResult with .data and .trace."""
    mock_fetcher.return_value = (
        {
            "2024-01-02 00:00:00": {
                "Open": 100.0,
                "High": 101.0,
                "Low": 99.0,
                "Close": 100.5,
                "Volume": 1e6,
            },
        },
        {"provider": "yfinance", "raw_shape": (1, 5)},
    )
    stock = StockClass("AAPL")
    result = stock.history(period="5d", interval="1d", source_trace=True)
    assert isinstance(result, HistoryResult)
    assert hasattr(result, "data")
    assert hasattr(result, "trace")
    assert isinstance(result.data, pd.DataFrame)
    assert result.trace["provider"] == "yfinance"
    assert "transform_steps" in result.trace


@patch("investormate.core.stock.get_yfinance_stock_history")
def test_stock_history_default_returns_dataframe(mock_fetcher):
    """Stock.history() without source_trace returns DataFrame."""
    mock_fetcher.return_value = {
        "2024-01-02 00:00:00": {
            "Open": 100.0,
            "High": 101.0,
            "Low": 99.0,
            "Close": 100.5,
            "Volume": 1e6,
        },
    }
    stock = StockClass("AAPL")
    result = stock.history(period="5d", interval="1d")
    assert isinstance(result, pd.DataFrame)
    assert not isinstance(result, HistoryResult)
