# Fixed Income Analytics

Bond pricing, duration, convexity, and ladder construction.

## Quick start

```python
from investormate import Bond, bond_ladder

b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10, frequency=2)
print(f"Price: ${b.price():.2f}")
print(f"Modified duration: {b.modified_duration():.2f}")
print(f"Convexity: {b.convexity():.2f}")

# Solve YTM from price
price = b.price()
solved_ytm = Bond(face=1000, coupon=0.06, n=10, price=price).solve_ytm()

# Bond ladder
ladder = bond_ladder(maturities=[1, 3, 5, 7, 10])
```

## Bond methods

| Method | Description |
|--------|-------------|
| `price(ytm=None)` | Clean price from YTM |
| `solve_ytm(price)` | Solve YTM from price |
| `current_yield(market_price)` | Coupon / price |
| `accrued_interest(settlement_date, ...)` | Accrued interest |
| `macaulay_duration()` | Macaulay duration (years) |
| `modified_duration()` | Modified duration |
| `convexity()` | Convexity |
| `price_change(yield_change)` | Duration + convexity approximation |

## Note

US Treasury yield curve via FRED is planned for v0.6 (Phase 2.6 macro data).
