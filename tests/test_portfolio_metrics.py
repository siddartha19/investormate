"""Tests for portfolio risk metrics (Sortino, Calmar, drawdown, beta)."""

from datetime import datetime, timedelta
from unittest.mock import patch

import numpy as np
import pytest

from investormate.core.portfolio import Portfolio


def _fake_history_dict(seed: int, n: int = 50, drift: float = 0.0002):
    rng = np.random.default_rng(seed)
    hist = {}
    base = datetime(2024, 1, 1)
    price = 100.0
    for i in range(n):
        day = base + timedelta(days=i)
        price = max(1.0, price * (1 + drift + rng.normal(0, 0.015)))
        p = float(price)
        key = str(day)
        hist[key] = {
            "Open": p,
            "High": p * 1.01,
            "Low": p * 0.99,
            "Close": p,
            "Volume": 1e6,
        }
    return hist


@patch("investormate.core.portfolio.get_yfinance_data")
@patch("investormate.core.portfolio.get_yfinance_stock_history")
def test_portfolio_weighted_metrics(mock_hist, mock_info):
    mock_info.return_value = {"currentPrice": 100.0, "regularMarketPrice": 100.0}

    def hist_side_effect(ticker, period, interval, **kwargs):
        if ticker == "SPY":
            return _fake_history_dict(2, n=50, drift=0.0001)
        return _fake_history_dict(1 if ticker == "AAA" else 3, n=50, drift=0.0003)

    mock_hist.side_effect = hist_side_effect

    p = Portfolio({"AAA": 10, "BBB": 5})
    pr = p._weighted_daily_returns()
    assert pr is not None
    assert len(pr) >= 30

    assert p.sharpe_ratio is not None
    assert p.sortino_ratio is not None
    assert p.max_drawdown is not None
    assert p.max_drawdown >= 0
    assert p.calmar_ratio is not None
    beta = p.beta("SPY")
    assert beta is not None
    dd_series = p.drawdown_series()
    assert dd_series is not None
    assert dd_series.max() <= 0


@patch("investormate.core.portfolio.get_yfinance_data")
@patch("investormate.core.portfolio.get_yfinance_stock_history")
def test_portfolio_metrics_insufficient_data(mock_hist, mock_info):
    mock_info.return_value = {"currentPrice": 100.0}
    mock_hist.return_value = {}

    p = Portfolio({"ZZZ": 1})
    assert p._weighted_daily_returns() is None
    assert p.sortino_ratio is None
    assert p.max_drawdown is None
    assert p.calmar_ratio is None
    assert p.beta() is None
