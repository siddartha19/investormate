"""
RSI mean-reversion template: buy oversold, sell overbought.
"""

import pandas as pd

from ..strategy import Strategy


class MeanReversionStrategy(Strategy):
    """
    Buy when RSI < ``oversold``; sell when RSI > ``overbought``.

    Args:
        rsi_period: RSI window (default 14).
        oversold: Buy threshold (default 30).
        overbought: Sell threshold (default 70).
    """

    def __init__(self, rsi_period: int = 14, oversold: float = 30.0, overbought: float = 70.0):
        super().__init__()
        self.rsi_period = int(rsi_period)
        self.oversold = float(oversold)
        self.overbought = float(overbought)

    def initialize(self):
        pass

    def on_data(self, data):
        rsi_series = data.indicators.rsi(self.rsi_period)
        if rsi_series is None or len(rsi_series) == 0:
            return
        rsi = rsi_series.iloc[-1]
        if pd.isna(rsi):
            return
        if rsi < self.oversold and not self.has_position:
            self.buy(percent=0.98)
        elif rsi > self.overbought and self.has_position:
            self.sell_all()
