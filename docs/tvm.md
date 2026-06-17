# Time Value of Money (TVM)

Pure numpy/pandas TVM calculations — no API keys required.

## Quick start

```python
from investormate import present_value, future_value, annuity_pv, npv, irr, amortization_schedule

# Lump sum
pv = present_value(fv=1000, rate=0.05, n=10)
fv = future_value(pv=500, rate=0.08, n=5)

# Annuity
pv_annuity = annuity_pv(pmt=100, rate=0.08, n=20, due=False)

# Uneven cash flows
project_npv = npv(0.10, [-1000, 300, 400, 500])
project_irr = irr([-1000, 300, 400, 500])

# Loan amortization
schedule = amortization_schedule(principal=100000, rate=0.04, n=30)
print(schedule.head())
```

## API

| Function | Description |
|----------|-------------|
| `present_value(fv, rate, n)` | PV of lump sum |
| `future_value(pv, rate, n)` | FV of lump sum |
| `annuity_pv(pmt, rate, n, due=False)` | PV of annuity |
| `annuity_fv(pmt, rate, n, due=False)` | FV of annuity |
| `perpetuity(pmt, rate, growth=None)` | Level or growing perpetuity |
| `npv(rate, cashflows)` | NPV of uneven flows |
| `irr(cashflows)` | Internal rate of return |
| `amortization_schedule(principal, rate, n)` | Loan schedule DataFrame |
| `ear(nominal, compounding=12)` | Effective annual rate |

## CFA coverage

Quantitative Methods (L1): PV, FV, annuities, NPV, IRR, amortization.
