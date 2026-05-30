"""
Technical indicators for InvestorMate.
Native implementations using pandas and numpy — no external TA library required.
"""

from typing import List
import numpy as np
import pandas as pd


class IndicatorsHelper:
    """Helper class for calculating technical indicators."""

    def __init__(self, price_data: pd.DataFrame):
        """
        Initialize indicators helper.

        Args:
            price_data: DataFrame with OHLCV data (Open, High, Low, Close, Volume)
        """
        self.df = price_data.copy()

        required_cols = ["Open", "High", "Low", "Close"]
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    # ── Moving Averages ───────────────────────────────────────────────

    def sma(self, period: int = 20, column: str = "Close") -> pd.Series:
        """Simple Moving Average."""
        return self.df[column].rolling(window=period, min_periods=period).mean()

    def ema(self, period: int = 12, column: str = "Close") -> pd.Series:
        """Exponential Moving Average."""
        return self.df[column].ewm(span=period, adjust=False).mean()

    def wma(self, period: int = 20, column: str = "Close") -> pd.Series:
        """Weighted Moving Average."""
        weights = np.arange(1, period + 1, dtype=float)

        def _wma(window):
            return np.dot(window, weights) / weights.sum()

        return (
            self.df[column]
            .rolling(window=period, min_periods=period)
            .apply(_wma, raw=True)
        )

    # ── Momentum Indicators ───────────────────────────────────────────

    def rsi(self, period: int = 14, column: str = "Close") -> pd.Series:
        """Relative Strength Index (Wilder's smoothing)."""
        delta = self.df[column].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        rsi.name = f"RSI_{period}"
        return rsi

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD (Moving Average Convergence Divergence)."""
        ema_fast = self.df["Close"].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df["Close"].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return pd.DataFrame(
            {
                f"MACD_{fast}_{slow}_{signal}": macd_line,
                f"MACDs_{fast}_{slow}_{signal}": signal_line,
                f"MACDh_{fast}_{slow}_{signal}": histogram,
            },
            index=self.df.index,
        )

    def stoch(self, k: int = 14, d: int = 3, smooth_k: int = 3) -> pd.DataFrame:
        """Stochastic Oscillator (%K and %D)."""
        low_min = self.df["Low"].rolling(window=k, min_periods=k).min()
        high_max = self.df["High"].rolling(window=k, min_periods=k).max()

        denom = high_max - low_min
        fast_k = 100.0 * (self.df["Close"] - low_min) / denom.replace(0, np.nan)
        slow_k = fast_k.rolling(window=smooth_k, min_periods=smooth_k).mean()
        slow_d = slow_k.rolling(window=d, min_periods=d).mean()

        return pd.DataFrame(
            {
                f"STOCHk_{k}_{d}_{smooth_k}": slow_k,
                f"STOCHd_{k}_{d}_{smooth_k}": slow_d,
            },
            index=self.df.index,
        )

    def cci(self, period: int = 20) -> pd.Series:
        """Commodity Channel Index."""
        tp = (self.df["High"] + self.df["Low"] + self.df["Close"]) / 3.0
        sma_tp = tp.rolling(window=period, min_periods=period).mean()
        mad = tp.rolling(window=period, min_periods=period).apply(
            lambda x: np.mean(np.abs(x - x.mean())), raw=True
        )
        cci = (tp - sma_tp) / (0.015 * mad)
        cci.name = f"CCI_{period}"
        return cci

    def williams_r(self, period: int = 14) -> pd.Series:
        """Williams %R."""
        high_max = self.df["High"].rolling(window=period, min_periods=period).max()
        low_min = self.df["Low"].rolling(window=period, min_periods=period).min()
        denom = high_max - low_min
        wr = -100.0 * (high_max - self.df["Close"]) / denom.replace(0, np.nan)
        wr.name = f"WILLR_{period}"
        return wr

    def momentum(self, period: int = 10, column: str = "Close") -> pd.Series:
        """Momentum (price difference over N periods)."""
        mom = self.df[column] - self.df[column].shift(period)
        mom.name = f"MOM_{period}"
        return mom

    def roc(self, period: int = 10, column: str = "Close") -> pd.Series:
        """Rate of Change (% change over N periods)."""
        prev = self.df[column].shift(period)
        rate = 100.0 * (self.df[column] - prev) / prev
        rate.name = f"ROC_{period}"
        return rate

    # ── Volatility Indicators ─────────────────────────────────────────

    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Bollinger Bands (lower, mid, upper, bandwidth, %B)."""
        mid = self.df["Close"].rolling(window=period, min_periods=period).mean()
        std = self.df["Close"].rolling(window=period, min_periods=period).std()
        upper = mid + std_dev * std
        lower = mid - std_dev * std
        bandwidth = (upper - lower) / mid
        pct_b = (self.df["Close"] - lower) / (upper - lower)

        return pd.DataFrame(
            {
                f"BBL_{period}_{std_dev}": lower,
                f"BBM_{period}_{std_dev}": mid,
                f"BBU_{period}_{std_dev}": upper,
                f"BBB_{period}_{std_dev}": bandwidth,
                f"BBP_{period}_{std_dev}": pct_b,
            },
            index=self.df.index,
        )

    def _true_range(self) -> pd.Series:
        """True Range (internal helper)."""
        prev_close = self.df["Close"].shift(1)
        tr1 = self.df["High"] - self.df["Low"]
        tr2 = (self.df["High"] - prev_close).abs()
        tr3 = (self.df["Low"] - prev_close).abs()
        return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    def atr(self, period: int = 14) -> pd.Series:
        """Average True Range (Wilder's smoothing)."""
        tr = self._true_range()
        atr_val = tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        atr_val.name = f"ATR_{period}"
        return atr_val

    def keltner_channels(self, period: int = 20, scalar: float = 2.0) -> pd.DataFrame:
        """Keltner Channels."""
        mid = self.ema(period)
        atr_val = self.atr(period)
        upper = mid + scalar * atr_val
        lower = mid - scalar * atr_val

        return pd.DataFrame(
            {
                f"KCLe_{period}_{scalar}": lower,
                f"KCBe_{period}_{scalar}": mid,
                f"KCUe_{period}_{scalar}": upper,
            },
            index=self.df.index,
        )

    def donchian_channels(self, period: int = 20) -> pd.DataFrame:
        """Donchian Channels."""
        upper = self.df["High"].rolling(window=period, min_periods=period).max()
        lower = self.df["Low"].rolling(window=period, min_periods=period).min()
        mid = (upper + lower) / 2.0

        return pd.DataFrame(
            {
                f"DCL_{period}_{period}": lower,
                f"DCM_{period}_{period}": mid,
                f"DCU_{period}_{period}": upper,
            },
            index=self.df.index,
        )

    # ── Volume Indicators ─────────────────────────────────────────────

    def obv(self) -> pd.Series:
        """On-Balance Volume."""
        if "Volume" not in self.df.columns:
            raise ValueError("Volume column required for OBV")
        direction = np.sign(self.df["Close"].diff())
        obv_val = (direction * self.df["Volume"]).fillna(0).cumsum()
        obv_val.name = "OBV"
        return obv_val

    def ad(self) -> pd.Series:
        """Accumulation/Distribution Line."""
        if "Volume" not in self.df.columns:
            raise ValueError("Volume column required for A/D")
        hl_range = self.df["High"] - self.df["Low"]
        mfm = (
            (self.df["Close"] - self.df["Low"]) - (self.df["High"] - self.df["Close"])
        ) / hl_range.replace(0, np.nan)
        mfv = mfm * self.df["Volume"]
        ad_val = mfv.fillna(0).cumsum()
        ad_val.name = "AD"
        return ad_val

    def adx(self, period: int = 14) -> pd.DataFrame:
        """Average Directional Index (+DI, -DI, ADX)."""
        high = self.df["High"]
        low = self.df["Low"]
        close = self.df["Close"]

        up_move = high.diff()
        down_move = -low.diff()

        plus_dm = pd.Series(
            np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
            index=self.df.index,
        )
        minus_dm = pd.Series(
            np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
            index=self.df.index,
        )

        alpha = 1.0 / period
        atr_val = (
            self._true_range().ewm(alpha=alpha, min_periods=period, adjust=False).mean()
        )
        plus_dm_smooth = plus_dm.ewm(
            alpha=alpha, min_periods=period, adjust=False
        ).mean()
        minus_dm_smooth = minus_dm.ewm(
            alpha=alpha, min_periods=period, adjust=False
        ).mean()

        plus_di = 100.0 * plus_dm_smooth / atr_val
        minus_di = 100.0 * minus_dm_smooth / atr_val

        dx = (
            100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
        )
        adx_val = dx.ewm(alpha=alpha, min_periods=period, adjust=False).mean()

        return pd.DataFrame(
            {
                f"ADX_{period}": adx_val,
                f"DMP_{period}": plus_di,
                f"DMN_{period}": minus_di,
            },
            index=self.df.index,
        )

    def vwap(self) -> pd.Series:
        """Volume Weighted Average Price (cumulative intra-day style)."""
        if "Volume" not in self.df.columns:
            raise ValueError("Volume column required for VWAP")
        tp = (self.df["High"] + self.df["Low"] + self.df["Close"]) / 3.0
        cum_tp_vol = (tp * self.df["Volume"]).cumsum()
        cum_vol = self.df["Volume"].cumsum()
        vwap_val = cum_tp_vol / cum_vol.replace(0, np.nan)
        vwap_val.name = "VWAP"
        return vwap_val

    # ── Trend Indicators ──────────────────────────────────────────────

    def supertrend(self, period: int = 7, multiplier: float = 3.0) -> pd.DataFrame:
        """SuperTrend indicator."""
        hl2 = (self.df["High"] + self.df["Low"]) / 2.0
        atr_val = self.atr(period)

        upper_basic = hl2 + multiplier * atr_val
        lower_basic = hl2 - multiplier * atr_val

        close = self.df["Close"].values
        upper = upper_basic.values.copy()
        lower = lower_basic.values.copy()
        direction = np.ones(len(close))
        supertrend_arr = np.empty(len(close))
        supertrend_arr[:] = np.nan

        for i in range(1, len(close)):
            if not np.isnan(lower[i]) and not np.isnan(lower[i - 1]):
                if lower[i] < lower[i - 1] and close[i - 1] > lower[i - 1]:
                    lower[i] = lower[i - 1]
            if not np.isnan(upper[i]) and not np.isnan(upper[i - 1]):
                if upper[i] > upper[i - 1] and close[i - 1] < upper[i - 1]:
                    upper[i] = upper[i - 1]

            if direction[i - 1] == 1:
                direction[i] = 1 if close[i] >= lower[i] else -1
            else:
                direction[i] = -1 if close[i] <= upper[i] else 1

            supertrend_arr[i] = lower[i] if direction[i] == 1 else upper[i]

        st_series = pd.Series(
            supertrend_arr, index=self.df.index, name=f"SUPERT_{period}_{multiplier}"
        )
        dir_series = pd.Series(
            direction, index=self.df.index, name=f"SUPERTd_{period}_{multiplier}"
        )
        return pd.DataFrame({st_series.name: st_series, dir_series.name: dir_series})

    def ichimoku(
        self,
        tenkan: int = 9,
        kijun: int = 26,
        senkou_b: int = 52,
    ) -> pd.DataFrame:
        """Ichimoku Cloud (Tenkan, Kijun, Senkou A, Senkou B, Chikou)."""
        high = self.df["High"]
        low = self.df["Low"]

        tenkan_sen = (
            high.rolling(window=tenkan, min_periods=tenkan).max()
            + low.rolling(window=tenkan, min_periods=tenkan).min()
        ) / 2.0
        kijun_sen = (
            high.rolling(window=kijun, min_periods=kijun).max()
            + low.rolling(window=kijun, min_periods=kijun).min()
        ) / 2.0
        senkou_a = ((tenkan_sen + kijun_sen) / 2.0).shift(kijun)
        senkou_b_val = (
            (
                high.rolling(window=senkou_b, min_periods=senkou_b).max()
                + low.rolling(window=senkou_b, min_periods=senkou_b).min()
            )
            / 2.0
        ).shift(kijun)
        chikou = self.df["Close"].shift(-kijun)

        return pd.DataFrame(
            {
                f"ISA_{tenkan}": tenkan_sen,
                f"ISB_{kijun}": kijun_sen,
                f"ITS_{tenkan}": senkou_a,
                f"IKS_{senkou_b}": senkou_b_val,
                f"ICS_{kijun}": chikou,
            },
            index=self.df.index,
        )

    # ── Utility Methods ───────────────────────────────────────────────

    def add_indicators(self, indicators: List[str]) -> pd.DataFrame:
        """
        Add multiple indicators to the dataframe.

        Args:
            indicators: List of indicator names (e.g., ['sma_20', 'rsi_14', 'macd'])

        Returns:
            DataFrame with indicators added
        """
        df_with_indicators = self.df.copy()

        for indicator in indicators:
            parts = indicator.split("_")
            name = parts[0]
            period = int(parts[1]) if len(parts) > 1 else None

            if name == "sma" and period:
                df_with_indicators[indicator] = self.sma(period)
            elif name == "ema" and period:
                df_with_indicators[indicator] = self.ema(period)
            elif name == "rsi":
                period = period or 14
                df_with_indicators[f"rsi_{period}"] = self.rsi(period)
            elif name == "macd":
                macd_df = self.macd()
                for col in macd_df.columns:
                    df_with_indicators[col] = macd_df[col]
            elif name == "bbands":
                period = period or 20
                bbands_df = self.bollinger_bands(period)
                for col in bbands_df.columns:
                    df_with_indicators[col] = bbands_df[col]
            elif name == "atr":
                period = period or 14
                df_with_indicators[f"atr_{period}"] = self.atr(period)
            elif name == "obv":
                df_with_indicators["obv"] = self.obv()
            elif name == "volume" and "sma" in indicator:
                period = period or 20
                if "Volume" in df_with_indicators.columns:
                    df_with_indicators[f"volume_sma_{period}"] = self.sma(
                        period, "Volume"
                    )

        return df_with_indicators

    @staticmethod
    def available_indicators() -> List[str]:
        """
        Get list of available indicators.

        Returns:
            List of indicator names
        """
        return [
            "sma",
            "ema",
            "wma",
            "rsi",
            "macd",
            "stoch",
            "cci",
            "williams_r",
            "momentum",
            "roc",
            "bollinger_bands",
            "atr",
            "keltner_channels",
            "donchian_channels",
            "obv",
            "ad",
            "adx",
            "vwap",
            "supertrend",
            "ichimoku",
        ]
