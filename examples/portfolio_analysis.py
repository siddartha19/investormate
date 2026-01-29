"""
Portfolio Analysis Example for InvestorMate

This example demonstrates portfolio tracking and analysis.
"""

from investormate import Portfolio

# Create portfolio with holdings
portfolio = Portfolio({
    "AAPL": 10,
    "GOOGL": 5,
    "MSFT": 15,
    "TSLA": 8
})

# Get portfolio metrics
print(f"Portfolio Value: ${portfolio.value:,.2f}")
print(f"\nAllocation by Stock:")
for ticker, allocation in portfolio.allocation.items():
    print(f"  {ticker}: {allocation:.2f}%")

print(f"\nSector Allocation:")
for sector, allocation in portfolio.sector_allocation.items():
    print(f"  {sector}: {allocation:.2f}%")

print(f"\nPortfolio Metrics:")
print(f"Concentration: {portfolio.concentration:.2f}")
print(f"Volatility: {portfolio.volatility:.2f}%" if portfolio.volatility else "Volatility: N/A")
print(f"Sharpe Ratio: {portfolio.sharpe_ratio:.2f}" if portfolio.sharpe_ratio else "Sharpe Ratio: N/A")

# Portfolio with cost basis to track returns
portfolio_with_cost = Portfolio(
    holdings={"AAPL": 10, "GOOGL": 5},
    cost_basis={"AAPL": 120.0, "GOOGL": 90.0}
)

if portfolio_with_cost.returns:
    print(f"\nTotal Returns: {portfolio_with_cost.returns:.2f}%")

# Add a new position
portfolio.add("NVDA", 12)
print(f"\nAfter adding NVDA:")
print(f"New allocation: {portfolio.allocation}")
