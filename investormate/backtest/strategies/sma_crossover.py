"""
Dual moving-average crossover (golden cross / death cross).
"""

import pandas as pd

from ..strategy import Strategy


class SMACrossoverStrategy(Strategy):
    """
    Buy on bullish crossover (fast SMA crosses above slow); sell on bearish crossover.

    Args:
        fast: Fast SMA period (default 50).
        slow: Slow SMA period (default 200).
    """

    def __init__(self, fast: int = 50, slow: int = 200):
        super().__init__()
        self.fast = int(fast)
        self.slow = int(slow)
        if self.fast >= self.slow:
            raise ValueError("fast period must be less than slow period")

    def initialize(self):
        pass

    def on_data(self, data):
        df = data.history(period="max", interval="1d")
        if len(df) < self.slow + 2:
            return
        close = df["Close"].astype(float)
        fast_ma = close.rolling(self.fast).mean()
        slow_ma = close.rolling(self.slow).mean()
        if pd.isna(fast_ma.iloc[-1]) or pd.isna(slow_ma.iloc[-1]):
            return
        bull = fast_ma.iloc[-1] > slow_ma.iloc[-1] and fast_ma.iloc[-2] <= slow_ma.iloc[-2]
        bear = fast_ma.iloc[-1] < slow_ma.iloc[-1] and fast_ma.iloc[-2] >= slow_ma.iloc[-2]
        if bull and not self.has_position:
            self.buy(percent=0.98)
        elif bear and self.has_position:
            self.sell_all()
