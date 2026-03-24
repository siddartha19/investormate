"""Tests for Stock peers and compare_with."""

from unittest.mock import patch

from investormate.core.stock import Stock


@patch("investormate.core.stock.get_yfinance_data")
def test_peers_same_sector(mock_data):
    def side_effect(ticker):
        sector = "Technology" if ticker in ("AAPL", "MSFT") else "Energy"
        return {"sector": sector, "currentPrice": 100.0}

    mock_data.side_effect = side_effect

    with patch(
        "investormate.core.stock.MAJOR_US_TICKERS",
        ["AAPL", "MSFT", "XOM"],
    ):
        stock = Stock("AAPL")
        peers = stock.peers
        assert "MSFT" in peers
        assert "XOM" not in peers


@patch("investormate.core.stock.get_yfinance_data")
def test_compare_with_explicit_peers(mock_data):
    calls = {}

    def side_effect(ticker):
        calls[ticker] = calls.get(ticker, 0) + 1
        return {
            "sector": "Technology",
            "shortName": ticker,
            "trailingPE": 20.0,
            "priceToBook": 5.0,
            "priceToSalesTrailing12Months": 3.0,
            "returnOnEquity": 0.2,
            "returnOnAssets": 0.1,
            "profitMargins": 0.15,
            "grossMargins": 0.4,
            "revenueGrowth": 0.05,
            "earningsGrowth": 0.08,
            "marketCap": 1e12,
        }

    mock_data.side_effect = side_effect

    stock = Stock("AAA")
    # Avoid loading real info for AAA — patch Stock.__init__ path: validate_ticker only
    # get_yfinance_data is called from .info property
    out = stock.compare_with(peers=["BBB", "CCC"])
    assert out["subject"] == "AAA"
    assert "BBB" in out["metrics"]
    assert out["metrics"]["AAA"]["pe"] == 20.0
