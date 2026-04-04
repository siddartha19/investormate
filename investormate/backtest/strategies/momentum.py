"""
Price momentum template: long when lookback return is positive, flat when negative.
"""

import pandas as pd

from ..strategy import Strategy


class MomentumStrategy(Strategy):
    """
    Go long when trailing ``lookback``-day total return is positive; exit when negative.

    Uses ``Stock.history`` (not point-in-time sliced per bar in the default engine).

    Args:
        lookback: Trading days for momentum (default 126 ~ 6 months).
    """

    def __init__(self, lookback: int = 126):
        super().__init__()
        self.lookback = int(lookback)

    def initialize(self):
        pass

    def on_data(self, data):
        df = data.history(period="max", interval="1d")
        if len(df) < self.lookback + 2:
            return
        close = df["Close"].astype(float)
        ret = close.iloc[-1] / close.iloc[-self.lookback - 1] - 1.0
        if pd.isna(ret):
            return
        if ret > 0 and not self.has_position:
            self.buy(percent=0.98)
        elif ret < 0 and self.has_position:
            self.sell_all()
