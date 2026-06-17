"""Tests for CAPM module."""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch

from investormate.analysis.capm import capm_regression, factor_model, risk_decomposition


def _mock_history(ticker, period, interval, auto_adjust=True, return_trace=False):
    rng = np.random.default_rng(hash(ticker) % 2**31)
    n = 300
    dates = pd.date_range("2023-01-01", periods=n, freq="B")
    if ticker.upper() == "SPY":
        rets = rng.normal(0.0004, 0.01, n)
    else:
        rets = rng.normal(0.0005, 0.015, n)
    prices = 100 * np.cumprod(1 + rets)
    data = {
        str(d.date()): {
            "Close": float(p),
            "Open": float(p),
            "High": float(p),
            "Low": float(p),
            "Volume": 1e6,
        }
        for d, p in zip(dates, prices)
    }
    if return_trace:
        return data, {"provider": "mock"}
    return data, None


class TestCAPM:
    @patch("investormate.analysis.capm.get_data_provider")
    def test_capm_regression(self, mock_provider):
        mock_provider.return_value.get_history.side_effect = _mock_history
        result = capm_regression("AAPL", "SPY", period="2y")
        assert "beta" in result
        assert "alpha_annual" in result
        assert "r_squared" in result
        assert result["observations"] >= 30

    @patch("investormate.analysis.capm.get_data_provider")
    def test_risk_decomposition(self, mock_provider):
        mock_provider.return_value.get_history.side_effect = _mock_history
        result = risk_decomposition("AAPL", "SPY")
        assert result["total_variance"] > 0
        assert result["systematic_variance"] >= 0

    def test_factor_model(self):
        dates = pd.date_range("2023-01-01", periods=100, freq="B")
        factors = pd.DataFrame(
            {
                "Mkt-RF": np.random.randn(100) * 0.01,
                "SMB": np.random.randn(100) * 0.005,
                "HML": np.random.randn(100) * 0.005,
            },
            index=dates,
        )
        with patch("investormate.analysis.capm.get_data_provider") as mock_provider:
            mock_provider.return_value.get_history.side_effect = _mock_history
            result = factor_model("AAPL", factors, model="ff3")
        assert "factor_loadings" in result
        assert "Mkt-RF" in result["factor_loadings"]
