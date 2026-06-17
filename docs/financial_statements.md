# Financial Statement Analysis

Common-size, horizontal, vertical, and trend analysis on yfinance statements.

## Quick start

```python
from investormate import Stock

stock = Stock("AAPL")

# Common-size (% of revenue or total assets)
cs = stock.financials.common_size("income")

# Year-over-year changes
horizontal = stock.financials.horizontal(periods=5)

# Indexed trends (base year = 100)
trend = stock.financials.trend(base_year=2021)

# Cash flow quality
quality = stock.financials.cash_flow_quality()

# Export
stock.financials.to_csv("aapl_income.csv", "income")
```

## DuPont breakdown

```python
dupont = stock.ratios.dupont_breakdown()
print(dupont["tree"])
```

## CFA coverage

Financial Statement Analysis (L1): common-size, horizontal, vertical, trend, DuPont ROE.
