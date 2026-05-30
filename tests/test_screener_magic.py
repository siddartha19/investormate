"""Tests for Magic Formula screener."""

from unittest.mock import patch

from investormate.core.screener import Screener


@patch("investormate.data.providers.YFinanceProvider.get_info")
def test_magic_formula_ranking(mock_data):
    """Combined rank: best ROIC + best EY should win."""

    def info_for(ticker):
        base = {
            "marketCap": 500_000_000,
            "ebit": 100_000_000,
            "enterpriseValue": 1_000_000_000,
            "totalAssets": 800_000_000,
            "totalCurrentLiabilities": 200_000_000,
            "effectiveTaxRate": 0.21,
        }
        if ticker == "HIGH":
            return {
                **base,
                "ebit": 200_000_000,
                "enterpriseValue": 1_000_000_000,
                "totalAssets": 500_000_000,
                "totalCurrentLiabilities": 100_000_000,
            }
        if ticker == "LOW":
            return {
                **base,
                "ebit": 20_000_000,
                "enterpriseValue": 2_000_000_000,
                "totalAssets": 900_000_000,
                "totalCurrentLiabilities": 400_000_000,
            }
        return base

    mock_data.side_effect = lambda t: info_for(t)

    screener = Screener(universe=["HIGH", "LOW", "MID"])
    out = screener.magic_formula(top_n=5)
    assert out[0] == "HIGH"


@patch("investormate.data.providers.YFinanceProvider.get_info")
def test_magic_formula_filters_negative_ebit(mock_data):
    mock_data.return_value = {
        "marketCap": 500_000_000,
        "ebit": -10_000_000,
        "enterpriseValue": 1_000_000_000,
        "totalAssets": 800_000_000,
        "totalCurrentLiabilities": 200_000_000,
        "effectiveTaxRate": 0.21,
    }
    screener = Screener(universe=["BAD"])
    assert screener.magic_formula() == []
