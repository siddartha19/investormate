"""
Technical Analysis Example for InvestorMate

This example demonstrates using technical indicators.
"""

from investormate import Stock

# Create stock instance
stock = Stock("AAPL")

# Get historical data
df = stock.history(period="6mo", interval="1d")

# Add technical indicators
df_with_indicators = stock.add_indicators(df, [
    "sma_20",
    "sma_50",
    "rsi_14",
    "macd",
    "bbands"
])

print("Latest data with indicators:")
print(df_with_indicators.tail())

# Or use indicators helper directly
print("\nCurrent Technical Indicators:")
print(f"20-day SMA: {stock.indicators.sma(20).iloc[-1]:.2f}")
print(f"50-day SMA: {stock.indicators.sma(50).iloc[-1]:.2f}")
print(f"RSI(14): {stock.indicators.rsi(14).iloc[-1]:.2f}")

# Get MACD
macd = stock.indicators.macd()
print(f"\nMACD Latest:")
print(macd.tail())

# Bollinger Bands
bbands = stock.indicators.bollinger_bands()
print(f"\nBollinger Bands Latest:")
print(bbands.tail())

# Check available indicators
print(f"\nAvailable Indicators:")
from investormate.analysis.indicators import IndicatorsHelper
print(IndicatorsHelper.available_indicators())
