"""Tests for built-in strategy templates (mocked price data)."""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch

from investormate.data.cache import configure_data_cache
from investormate.backtest import BacktestEngine
from investormate.backtest.strategies import (
    MeanReversionStrategy,
    MomentumStrategy,
    SMACrossoverStrategy,
)


@pytest.fixture(autouse=True)
def _fast_fetch_rate():
    configure_data_cache(calls_per_second=1_000_000.0)
    yield


def _ohlcv_dict(n: int = 320, drift: float = 0.002):
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    price = 100.0 * np.cumprod(1.0 + np.full(n, drift))
    out = {}
    for i, ts in enumerate(idx):
        p = float(price[i])
        out[str(ts)] = {
            "Open": p,
            "High": p * 1.01,
            "Low": p * 0.99,
            "Close": p,
            "Volume": 1e6,
        }
    return out


def _df_from_dict(d: dict) -> pd.DataFrame:
    df = pd.DataFrame.from_dict(d, orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df[["Open", "High", "Low", "Close", "Volume"]]


@patch.object(BacktestEngine, "_fetch_data")
@patch("investormate.core.stock.get_yfinance_stock_history")
def test_momentum_strategy_runs(mock_hist, mock_engine_fetch):
    d = _ohlcv_dict(400, drift=0.001)
    mock_hist.return_value = d
    mock_engine_fetch.return_value = _df_from_dict(d)
    eng = BacktestEngine(
        MomentumStrategy,
        "FAKE",
        "2020-06-01",
        "2021-06-01",
        initial_capital=10_000,
    )
    r = eng.run()
    assert "trades" in r
    assert "final_equity" in r


@patch.object(BacktestEngine, "_fetch_data")
@patch("investormate.core.stock.get_yfinance_stock_history")
def test_mean_reversion_strategy_runs(mock_hist, mock_engine_fetch):
    d = _ohlcv_dict(300, drift=0.0005)
    mock_hist.return_value = d
    mock_engine_fetch.return_value = _df_from_dict(d)
    eng = BacktestEngine(
        MeanReversionStrategy,
        "FAKE",
        "2020-06-01",
        "2021-03-01",
        initial_capital=10_000,
    )
    r = eng.run()
    assert r["initial_capital"] == 10_000


class _FastSMA(SMACrossoverStrategy):
    def __init__(self):
        super().__init__(fast=3, slow=10)


@patch.object(BacktestEngine, "_fetch_data")
@patch("investormate.core.stock.get_yfinance_stock_history")
def test_sma_crossover_strategy_runs(mock_hist, mock_engine_fetch):
    d = _ohlcv_dict(120, drift=0.003)
    mock_hist.return_value = d
    mock_engine_fetch.return_value = _df_from_dict(d)
    eng = BacktestEngine(
        _FastSMA,
        "FAKE",
        "2020-03-01",
        "2020-12-01",
        initial_capital=10_000,
    )
    r = eng.run()
    assert isinstance(r["trades"], list)
