"""Tests for the pluggable DataProvider seam."""

import pandas as pd
import pytest

from investormate import (
    Stock,
    Market,
    DataProvider,
    YFinanceProvider,
    get_data_provider,
    set_data_provider,
    reset_data_provider,
)
from investormate.data.cache import get_data_cache


class FakeProvider(DataProvider):
    """In-memory provider returning canned data (no network)."""

    def __init__(self):
        self.calls = []

    def get_info(self, ticker):
        self.calls.append(("get_info", ticker))
        return {
            "symbol": ticker,
            "currentPrice": 123.45,
            "shortName": f"{ticker} Test Corp",
            "sector": "Technology",
        }

    def get_balance_sheet(self, ticker):
        return {"2024-12-31": {"Total Assets": 1000.0}}

    def get_income_statement(self, ticker):
        return {"2024-12-31": {"Total Revenue": 500.0}}

    def get_cash_flow(self, ticker):
        return {"2024-12-31": {"Free Cash Flow": 200.0}}

    def get_calendar(self, ticker):
        return {}

    def get_earnings_estimate(self, ticker):
        return None

    def get_earnings_history(self, ticker):
        return None

    def get_revenue_estimate(self, ticker):
        return None

    def get_eps_trend(self, ticker):
        return None

    def get_eps_revisions(self, ticker):
        return None

    def get_growth_estimates(self, ticker):
        return None

    def get_history(
        self, ticker, period="1y", interval="1d", auto_adjust=True, return_trace=False
    ):
        data = {
            "2024-01-02": {"Open": 1, "High": 2, "Low": 1, "Close": 1.5, "Volume": 10}
        }
        if return_trace:
            return data, {"provider": "fake", "raw_shape": (1, 5)}
        return data

    def get_dividends(self, ticker):
        return pd.Series(dtype=float)

    def get_news(self, ticker):
        return [{"title": "fake news"}]

    def get_filings(self, ticker):
        return []

    def get_market_summary(self, market):
        return {"market": market, "source": "fake"}


@pytest.fixture(autouse=True)
def _restore_provider():
    """Ensure every test starts and ends on the default provider."""
    reset_data_provider()
    get_data_cache().clear()
    yield
    reset_data_provider()
    get_data_cache().clear()


def test_default_provider_is_yfinance():
    assert isinstance(get_data_provider(), YFinanceProvider)
    assert get_data_provider().name == "YFinanceProvider"


def test_set_data_provider_routes_stock_info():
    fake = FakeProvider()
    set_data_provider(fake)

    stock = Stock("AAPL")
    assert stock.info["currentPrice"] == 123.45
    assert stock.price == 123.45
    assert stock.news == [{"title": "fake news"}]
    assert ("get_info", "AAPL") in fake.calls


def test_set_data_provider_routes_market():
    set_data_provider(FakeProvider())
    market = Market("US")
    assert market.summary == {"market": "US", "source": "fake"}


def test_set_data_provider_rejects_non_provider():
    with pytest.raises(TypeError):
        set_data_provider(object())


def test_reset_data_provider_restores_default():
    set_data_provider(FakeProvider())
    assert isinstance(get_data_provider(), FakeProvider)
    reset_data_provider()
    assert isinstance(get_data_provider(), YFinanceProvider)


def test_partial_provider_via_subclassing_yfinance():
    # Subclass the default to override only one method
    class HybridProvider(YFinanceProvider):
        def get_info(self, ticker):
            return {"symbol": ticker, "currentPrice": 7.0}

    set_data_provider(HybridProvider())
    stock = Stock("MSFT")
    assert stock.price == 7.0


def test_yfinance_provider_unknown_market_raises():
    with pytest.raises(ValueError):
        YFinanceProvider().get_market_summary("MARS")
