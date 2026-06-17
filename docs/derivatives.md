# Derivatives Basics

Black-Scholes pricing, Greeks, binomial trees, and payoff diagrams.

## Quick start

```python
from investormate.finance import options

price = options.black_scholes(S=150, K=155, T=0.5, r=0.05, sigma=0.25, option_type="call")
g = options.greeks(150, 155, 0.5, 0.05, 0.25, "call")
tree = options.binomial(100, 105, 1, 0.05, 0.2, steps=50, option_type="put")
```

## API

| Function | Description |
|----------|-------------|
| `black_scholes(S, K, T, r, sigma, option_type)` | European option price |
| `greeks(S, K, T, r, sigma, option_type)` | Delta, gamma, theta, vega, rho |
| `put_call_parity(call, put, S, K, r, T)` | Verify parity |
| `binomial(S, K, T, r, sigma, steps, ...)` | CRR binomial tree |
| `payoff_diagram(strategy, legs)` | Expiry payoffs (no plotting dep) |
| `strategy_metrics(strategy, S, ...)` | Max profit/loss, breakeven |

## Strategies supported

`covered_call`, `protective_put`, `bull_call_spread`, `straddle`, plus custom legs via `payoff_diagram`.
