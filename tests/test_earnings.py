"""Tests for EarningsAnalyzer."""

from unittest.mock import patch

from investormate.analysis.earnings import EarningsAnalyzer


@patch("investormate.data.providers.YFinanceProvider.get_calendar")
@patch("investormate.data.providers.YFinanceProvider.get_info")
def test_calendar_merges_info(mock_info, mock_cal):
    mock_cal.return_value = {"Earnings Date": {"0": "2025-01-30"}}
    mock_info.return_value = {"earningsTimestamp": 1234567890}
    e = EarningsAnalyzer("AAPL")
    out = e.calendar()
    assert out["ticker"] == "AAPL"
    assert out["calendar"] == mock_cal.return_value
    assert out["earnings_timestamp"] == 1234567890


@patch("investormate.data.providers.YFinanceProvider.get_earnings_history")
def test_surprise_history_computes_percent(mock_hist):
    mock_hist.return_value = {
        "2024Q1": {"epsActual": 1.5, "epsAverage": 1.0},
    }
    e = EarningsAnalyzer("MSFT")
    rows = e.surprise_history()
    assert len(rows) == 1
    assert rows[0]["eps_actual"] == 1.5
    assert rows[0]["eps_estimate"] == 1.0
    assert abs(rows[0]["surprise_percent"] - 50.0) < 1e-6


@patch("investormate.data.providers.YFinanceProvider.get_earnings_history")
def test_surprise_history_empty(mock_hist):
    mock_hist.return_value = None
    assert EarningsAnalyzer("X").surprise_history() == []


@patch("investormate.data.providers.YFinanceProvider.get_revenue_estimate")
@patch("investormate.data.providers.YFinanceProvider.get_earnings_estimate")
def test_estimates(mock_earn, mock_rev):
    mock_earn.return_value = {"0": {"avg": 2.0}}
    mock_rev.return_value = {"0": {"avg": 1e9}}
    e = EarningsAnalyzer("AAPL")
    out = e.estimates()
    assert out["earnings"] == mock_earn.return_value
    assert out["revenue"] == mock_rev.return_value


@patch("investormate.data.providers.YFinanceProvider.get_eps_trend")
def test_eps_trend(mock_trend):
    mock_trend.return_value = {"7d Ago": {"0": 1.0}}
    assert EarningsAnalyzer("AAPL").eps_trend() == mock_trend.return_value


@patch("investormate.data.providers.YFinanceProvider.get_growth_estimates")
def test_growth_estimates(mock_g):
    mock_g.return_value = {"0": {"stockTrend": 0.1}}
    assert EarningsAnalyzer("AAPL").growth_estimates() == mock_g.return_value
