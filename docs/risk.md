# Portfolio risk (VaR and Monte Carlo)

Weighted daily portfolio returns (same window as Sharpe/Sortino: six months of daily data) drive **historical** and **parametric** Value at Risk and a simple **bootstrap Monte Carlo** for terminal value.

## VaR

```python
from investormate import Portfolio

p = Portfolio({"AAPL": 10, "MSFT": 5})

# One-day VaR as left-tail daily return (typically negative)
p.var(confidence=0.95, method="historical")   # empirical 5th percentile
p.var(confidence=0.95, method="parametric")  # Gaussian with sample mean/std
```

Interpretation: a historical 95% VaR of **-0.02** is a **2%** one-day loss at the 5th percentile of the observed return distribution—not a maximum loss guarantee.

## Monte Carlo

```python
p.monte_carlo_simulation(n=1000, horizon=252, seed=42)
```

Resamples **historical** daily returns with replacement for ``horizon`` days, compounds them, and repeats ``n`` times. Returns summary stats of the terminal portfolio value.

Requires at least **30** return observations and positive portfolio **value**.

## RiskAnalyzer

Lower-level helper:

```python
from investormate import Portfolio
from investormate.analysis.risk import RiskAnalyzer

pr = p._weighted_daily_returns()  # or use p.risk if available
ra = RiskAnalyzer(pr)
ra.var_historical(0.99)
ra.monte_carlo(p.value, n_simulations=500, horizon=60)
```

Or use ``portfolio.risk`` when returns are sufficient (returns a ``RiskAnalyzer`` instance).

## Limitations

- Gaussian VaR understates tail risk for fat-tailed assets.
- Bootstrap assumes i.i.d. daily returns (no regime change).
- Not financial advice.
