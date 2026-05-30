"""Tests for native technical indicators (no pandas-ta dependency)."""

import numpy as np
import pandas as pd
import pytest

from investormate.analysis.indicators import IndicatorsHelper


@pytest.fixture
def sample_ohlcv():
    """Create reproducible OHLCV data (100 rows)."""
    np.random.seed(42)
    n = 100
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n)) * 0.5
    low = close - np.abs(np.random.randn(n)) * 0.5
    open_ = close + np.random.randn(n) * 0.3
    volume = np.random.randint(100_000, 1_000_000, size=n).astype(float)

    dates = pd.bdate_range(start="2025-01-01", periods=n)
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


@pytest.fixture
def helper(sample_ohlcv):
    return IndicatorsHelper(sample_ohlcv)


class TestInit:
    def test_missing_columns_raises(self):
        df = pd.DataFrame({"Close": [1, 2, 3]})
        with pytest.raises(ValueError, match="Missing required columns"):
            IndicatorsHelper(df)

    def test_valid_init(self, sample_ohlcv):
        h = IndicatorsHelper(sample_ohlcv)
        assert len(h.df) == 100


class TestMovingAverages:
    def test_sma_length(self, helper):
        result = helper.sma(20)
        assert isinstance(result, pd.Series)
        assert len(result) == 100
        assert result.iloc[:19].isna().all()
        assert result.iloc[19:].notna().all()

    def test_ema_length(self, helper):
        result = helper.ema(12)
        assert isinstance(result, pd.Series)
        assert len(result) == 100
        assert result.notna().sum() > 0

    def test_wma_length(self, helper):
        result = helper.wma(10)
        assert isinstance(result, pd.Series)
        assert len(result) == 100
        assert result.iloc[:9].isna().all()
        assert result.iloc[9:].notna().all()


class TestMomentum:
    def test_rsi_range(self, helper):
        result = helper.rsi(14)
        valid = result.dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_macd_columns(self, helper):
        result = helper.macd()
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 3
        assert any("MACD_" in c for c in result.columns)

    def test_stoch_columns(self, helper):
        result = helper.stoch()
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 2

    def test_cci(self, helper):
        result = helper.cci(20)
        assert isinstance(result, pd.Series)
        assert result.dropna().shape[0] > 0

    def test_williams_r_range(self, helper):
        result = helper.williams_r(14)
        valid = result.dropna()
        assert (valid >= -100).all() and (valid <= 0).all()

    def test_momentum(self, helper):
        result = helper.momentum(10)
        assert isinstance(result, pd.Series)
        assert result.dropna().shape[0] > 0

    def test_roc(self, helper):
        result = helper.roc(10)
        assert isinstance(result, pd.Series)
        assert result.dropna().shape[0] > 0


class TestVolatility:
    def test_bollinger_bands_columns(self, helper):
        result = helper.bollinger_bands(20, 2.0)
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 5
        valid_idx = result.dropna().index
        assert (
            result.loc[valid_idx].iloc[:, 0] <= result.loc[valid_idx].iloc[:, 1]
        ).all()
        assert (
            result.loc[valid_idx].iloc[:, 1] <= result.loc[valid_idx].iloc[:, 2]
        ).all()

    def test_atr_positive(self, helper):
        result = helper.atr(14)
        valid = result.dropna()
        assert (valid >= 0).all()

    def test_keltner_channels(self, helper):
        result = helper.keltner_channels(20, 2.0)
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 3

    def test_donchian_channels(self, helper):
        result = helper.donchian_channels(20)
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 3


class TestVolume:
    def test_obv(self, helper):
        result = helper.obv()
        assert isinstance(result, pd.Series)
        assert len(result) == 100

    def test_obv_no_volume_raises(self):
        df = pd.DataFrame({"Open": [1], "High": [2], "Low": [0.5], "Close": [1.5]})
        h = IndicatorsHelper(df)
        with pytest.raises(ValueError, match="Volume"):
            h.obv()

    def test_ad(self, helper):
        result = helper.ad()
        assert isinstance(result, pd.Series)
        assert len(result) == 100

    def test_adx_columns(self, helper):
        result = helper.adx(14)
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 3

    def test_vwap(self, helper):
        result = helper.vwap()
        assert isinstance(result, pd.Series)
        valid = result.dropna()
        assert len(valid) > 0


class TestTrend:
    def test_supertrend(self, helper):
        result = helper.supertrend(7, 3.0)
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 2

    def test_ichimoku(self, helper):
        result = helper.ichimoku()
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 5


class TestUtility:
    def test_add_indicators(self, helper):
        result = helper.add_indicators(["sma_20", "rsi_14", "macd", "bbands"])
        assert "sma_20" in result.columns
        assert "rsi_14" in result.columns
        assert any("MACD_" in c for c in result.columns)
        assert any("BBU_" in c for c in result.columns)

    def test_available_indicators(self):
        names = IndicatorsHelper.available_indicators()
        assert "sma" in names
        assert "rsi" in names
        assert "macd" in names
        assert len(names) == 20
