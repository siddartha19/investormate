"""Tests for dividend growth streak and dividend aristocrats screen."""

import numpy as np
import pandas as pd
from unittest.mock import patch

from investormate.core.screener import Screener, _dividend_growth_streak_years


def test_dividend_growth_streak_increasing():
    years = list(range(2000, 2026))
    dates = pd.to_datetime([f"{y}-06-15" for y in years])
    amounts = np.arange(1.0, len(years) + 1, dtype=float)
    div = pd.Series(amounts, index=dates)
    assert _dividend_growth_streak_years(div) == 25


def test_dividend_growth_streak_breaks():
    dates = pd.to_datetime(["2020-01-01", "2021-01-01", "2022-01-01", "2023-01-01"])
    # Latest year total not above prior year → no streak ending at present
    div = pd.Series([1.0, 1.2, 1.3, 1.0], index=dates)
    assert _dividend_growth_streak_years(div) == 0


@patch("investormate.data.providers.YFinanceProvider.get_dividends")
@patch("investormate.data.providers.YFinanceProvider.get_info")
def test_dividend_aristocrats(mock_info, mock_div):
    years = list(range(2000, 2026))
    idx = pd.to_datetime([f"{y}-06-01" for y in years])
    mock_div.return_value = pd.Series(np.arange(1.0, len(years) + 1), index=idx)

    def info(sym):
        return {"dividendYield": 0.03, "marketCap": 1e10}

    mock_info.side_effect = info

    s = Screener(universe=["AAA", "BBB"])
    out = s.dividend_aristocrats(min_years=25, min_yield=2.0)
    assert "AAA" in out
    assert "BBB" in out
