"""
Tests for data fetchers null safety (Phase 1.1 P0).
Ensures fetchers handle None/empty yfinance responses without raising.
"""

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from investormate.data.fetchers import (
    get_yfinance_data,
    get_yfinance_balance_sheet_data,
    get_yfinance_income_statement_data,
    get_yfinance_cash_flow_statement_data,
    get_yfinance_stock_history,
    get_yfinance_ticker_news,
    get_yfinance_market_summary_us,
)


class TestFetcherNullSafety:
    """Test that fetchers return safe defaults for None/empty data."""

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_data_returns_empty_dict_when_info_is_none(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = None
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_data("INVALID")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_data_returns_empty_dict_when_info_not_dict(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = "not a dict"
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_data("TICK")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_balance_sheet_returns_empty_dict_when_df_none(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.balance_sheet = None
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_balance_sheet_data("TICK")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_balance_sheet_returns_empty_dict_when_df_empty(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.balance_sheet = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_balance_sheet_data("TICK")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_income_statement_returns_empty_dict_when_df_empty(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.incomestmt = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_income_statement_data("TICK")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_cash_flow_returns_empty_dict_when_df_empty(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.cash_flow = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_cash_flow_statement_data("TICK")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_stock_history_returns_empty_dict_when_df_none(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = None
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_stock_history("TICK")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_stock_history_returns_empty_dict_when_df_empty(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_stock_history("TICK")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_stock_history_returns_empty_dict_when_columns_missing(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        # DataFrame with wrong columns
        mock_ticker.history.return_value = pd.DataFrame({"A": [1], "B": [2]})
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_stock_history("TICK")
        assert result == {}

    @patch("investormate.data.fetchers.yf.Ticker")
    def test_get_yfinance_ticker_news_returns_empty_list_when_news_none(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.news = None
        mock_ticker_cls.return_value = mock_ticker
        result = get_yfinance_ticker_news("TICK")
        assert result == []

    @patch("investormate.data.fetchers.yf.Market")
    def test_get_yfinance_market_summary_us_returns_empty_dict_when_summary_none(self, mock_market_cls):
        mock_market = MagicMock()
        mock_market.summary = None
        mock_market_cls.return_value = mock_market
        result = get_yfinance_market_summary_us()
        assert result == {}
