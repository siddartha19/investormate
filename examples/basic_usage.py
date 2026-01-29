"""
Basic Usage Example for InvestorMate

This example demonstrates basic stock data retrieval and analysis.
"""

from investormate import Stock

# Create a Stock instance
stock = Stock("AAPL")

# Get basic information
print(f"Company: {stock.name}")
print(f"Sector: {stock.sector}")
print(f"Current Price: ${stock.price:,.2f}")
print(f"Market Cap: ${stock.market_cap:,.0f}")

# Get financial ratios
print(f"\nValuation Ratios:")
print(f"P/E Ratio: {stock.ratios.pe}")
print(f"P/B Ratio: {stock.ratios.pb}")
print(f"PEG Ratio: {stock.ratios.peg}")

# Get profitability ratios
print(f"\nProfitability Ratios:")
print(f"ROE: {stock.ratios.roe}")
print(f"ROA: {stock.ratios.roa}")
print(f"Profit Margin: {stock.ratios.profit_margin}")

# Get financial scores
scores = stock.scores.all_scores()
print(f"\nPiotroski F-Score: {scores['piotroski']['score']}/9")
print(f"Interpretation: {scores['piotroski']['interpretation']}")

# Get historical data
df = stock.history(period="1mo", interval="1d")
print(f"\nHistorical Data (last 5 days):")
print(df.tail())
