"""
Stock Screening Example for InvestorMate

This example demonstrates stock screening capabilities.
"""

from investormate import Screener

# Create screener (uses major US stocks by default)
screener = Screener()

# Find value stocks
print("Finding value stocks...")
value_stocks = screener.value_stocks(
    pe_max=15,
    pb_max=1.5,
    debt_to_equity_max=50
)
print(f"Value stocks found: {value_stocks}")

# Find growth stocks
print("\nFinding growth stocks...")
growth_stocks = screener.growth_stocks(
    revenue_growth_min=20,
    eps_growth_min=15
)
print(f"Growth stocks found: {growth_stocks}")

# Find dividend stocks
print("\nFinding dividend stocks...")
dividend_stocks = screener.dividend_stocks(
    yield_min=3.0,
    payout_ratio_max=60
)
print(f"Dividend stocks found: {dividend_stocks}")

# Custom screening
print("\nCustom screening...")
custom_results = screener.filter(
    market_cap_min=1_000_000_000,  # $1B minimum
    pe_ratio=(10, 25),              # P/E between 10 and 25
    roe_min=15,                     # ROE at least 15%
    sector="Technology"
)
print(f"Custom screening results: {custom_results}")
