"""Tests for CAN SLIM screener."""

from unittest.mock import patch

from investormate.core.screener import Screener


@patch("investormate.data.providers.YFinanceProvider.get_info")
def test_can_slim_prefers_higher_score(mock_data):
    def info_for(sym):
        base = {
            "marketCap": 1e10,
            "currentPrice": 100.0,
            "fiftyTwoWeekHigh": 100.0,
            "volume": 1e7,
            "averageVolume": 1e7,
            "fiftyTwoWeekChangePercent": 10.0,
        }
        if sym == "STRONG":
            return {
                **base,
                "earningsQuarterlyGrowth": 0.5,
                "earningsGrowth": 0.5,
            }
        if sym == "WEAK":
            return {
                **base,
                "earningsQuarterlyGrowth": 0.1,
                "earningsGrowth": 0.1,
            }
        return base

    mock_data.side_effect = lambda t: info_for(t)

    s = Screener(universe=["STRONG", "WEAK"])
    out = s.can_slim(top_n=5, min_score=3)
    assert out[0] == "STRONG"


@patch("investormate.data.providers.YFinanceProvider.get_info")
def test_can_slim_min_score_filters(mock_data):
    mock_data.return_value = {
        "marketCap": 1e9,
        "currentPrice": 10.0,
        "fiftyTwoWeekHigh": 200.0,
        "volume": 1.0,
        "averageVolume": 1e9,
        "earningsQuarterlyGrowth": 0.0,
        "earningsGrowth": 0.0,
        "fiftyTwoWeekChangePercent": -5.0,
    }
    s = Screener(universe=["BAD"])
    assert s.can_slim(min_score=5) == []
