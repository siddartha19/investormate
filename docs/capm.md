# CAPM & Factor Models

Regression-based CAPM, Jensen's alpha, and user-supplied Fama-French factors.

## Quick start

```python
from investormate import Stock

stock = Stock("AAPL")

# CAPM vs SPY
result = stock.capm.capm(benchmark="SPY", period="2y")
print(f"Beta: {result['beta']:.2f}, Alpha: {result['alpha_annual']*100:.1f}%")

# Jensen's alpha
ja = stock.jensen_alpha(benchmark="SPY")

# Risk decomposition
risk = stock.capm.risk_decomposition()
```

## Fama-French (user-supplied factors)

```python
import pandas as pd

# Factor returns DataFrame with DatetimeIndex
factors = pd.read_csv("ff3_factors.csv", index_col=0, parse_dates=True)
ff = stock.capm.factor_model(factors, model="ff3")
print(ff["factor_loadings"])
```

Ken French auto-fetch is deferred to a future release; supply your own factor CSV.
