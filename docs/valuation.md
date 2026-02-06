# Valuation Module

InvestorMate’s valuation module provides a **DCF (Discounted Cash Flow)** model and **comparable companies** analysis so you can estimate fair value and see implied upside or downside versus the current price.

## Overview

- **DCF** – Project free cash flow, apply a terminal value (perpetuity growth or exit multiple), and discount to present value using WACC.
- **Comparable companies (comps)** – Peer multiples (P/E, EV/EBITDA, P/S) and implied value per share.
- **Summary** – Combines DCF and comps into a fair value range, recommendation, and implied upside/downside.
- **Sensitivity** – DCF fair value across different growth and WACC assumptions.

Inputs use existing `stock.ratios` and financial statements (FCF, revenue, etc.) from the `Stock` instance.

## Basic Usage

```python
from investormate import Stock

stock = Stock("AAPL")

# DCF with default assumptions (5% growth, 5 years, terminal growth 2%)
dcf = stock.valuation.dcf(growth_rate=0.05)
print(f"Fair value per share: ${dcf['fair_value_per_share']}")
print(f"Assumptions: {dcf['assumptions']}")

# DCF with terminal multiple instead of perpetuity growth (e.g. 15× final-year FCF)
dcf_multiple = stock.valuation.dcf(growth_rate=0.05, terminal_multiple=15, years=5)
print(f"Fair value (exit multiple): ${dcf_multiple['fair_value_per_share']}")

# Fair value summary (DCF + comps) with implied upside/downside
summary = stock.valuation.summary(peers=["MSFT", "GOOGL"])
print(f"Fair value range: ${summary['fair_value_low']} - ${summary['fair_value_high']}")
print(f"Current price: ${summary['current_price']}")
print(f"Recommendation: {summary['recommendation']}")
print(f"Implied upside (to high): {summary.get('implied_upside_pct')}")   # e.g. 0.15 = 15%
print(f"Implied downside (to low): {summary.get('implied_downside_pct')}")
```

## DCF — `stock.valuation.dcf()`

Configurable parameters:

| Parameter            | Default   | Description |
|----------------------|-----------|-------------|
| `growth_rate`        | `0.05`    | Annual FCF growth rate (e.g. 0.05 = 5%). |
| `terminal_growth`     | `0.02`    | Perpetuity growth rate for terminal value. Ignored if `terminal_multiple` is set. |
| `terminal_multiple`   | `None`    | If set, terminal value = multiple × final-year FCF (e.g. 15). |
| `years`              | `5`       | Number of years to project FCF. |
| `wacc`               | from ratios or 10% | Discount rate. |

Returns a dict with:

- `fair_value_per_share` – DCF-derived fair value per share.
- `enterprise_value` – Sum of PV of projected FCF and PV of terminal value.
- `dcf_value` – Present value of projected FCF (excl. terminal value).
- `terminal_value_pv` – Present value of terminal value.
- `fcf_series` – List of projected FCF by year.
- `wacc_used` – Discount rate used.
- `assumptions` – `growth_rate`, `terminal_growth`, `terminal_multiple`, `years`.

FCF is taken from `info` (e.g. `freeCashflow`) or derived from operating cash flow minus capex; shares from `sharesOutstanding`. If FCF or shares are missing/invalid, `fair_value_per_share` will be `None`.

## Summary — `stock.valuation.summary()`

Combines DCF and optional comps into one view.

| Parameter         | Default | Description |
|-------------------|---------|-------------|
| `peers`           | `None`  | List of peer tickers for comps (e.g. `["MSFT", "GOOGL"]`). |
| `growth_rate`     | `0.05`  | DCF FCF growth rate. |
| `terminal_growth` | `0.02`  | DCF terminal growth. |
| `years`           | `5`     | DCF projection years. |

Returns a dict with:

- `dcf_result` – Full result of `dcf()`.
- `comps_result` – Full result of `comps(peers=...)`.
- `fair_value_low` / `fair_value_high` – Range from DCF and comps implied values.
- `fair_value_mid` – Midpoint of the range.
- `current_price` – Current stock price.
- `recommendation` – `"undervalued"`, `"fair"`, or `"overvalued"` vs. the range.
- `implied_upside_pct` – `(fair_value_high - current_price) / current_price` (decimal, e.g. 0.15 = 15%).
- `implied_downside_pct` – `(current_price - fair_value_low) / current_price` (decimal).

## Comparable Companies — `stock.valuation.comps()`

Requires a list of peer tickers. Fetches P/E, EV/EBITDA, and P/S for the stock and peers, then computes median multiples and implied value per share for the stock.

```python
comps = stock.valuation.comps(peers=["MSFT", "GOOGL", "META"])
print(comps["median_pe"], comps["median_ev_ebitda"], comps["median_ps"])
print(comps["implied_value_pe"], comps["implied_value_ev_ebitda"], comps["implied_value_ps"])
```

## Sensitivity — `stock.valuation.sensitivity()`

DCF fair value per share for different growth and WACC assumptions.

```python
sens = stock.valuation.sensitivity(
    growth_rates=[0.03, 0.05, 0.07],
    wacc_rates=[0.08, 0.10, 0.12],
    years=5,
)
# sens["table"][growth][wacc] = fair_value_per_share
# sens["min_value"], sens["max_value"], sens["current_price"]
```

## Example: “Is this stock undervalued?”

```python
from investormate import Stock

stock = Stock("AAPL")
summary = stock.valuation.summary(
    peers=["MSFT", "GOOGL"],
    growth_rate=0.05,
    years=5,
)

fv_low = summary["fair_value_low"]
fv_high = summary["fair_value_high"]
current = summary["current_price"]
rec = summary["recommendation"]
upside = summary.get("implied_upside_pct")
downside = summary.get("implied_downside_pct")

print(f"Fair value range: ${fv_low:.2f} - ${fv_high:.2f}")
print(f"Current: ${current:.2f} → {rec}")
if upside is not None:
    print(f"Upside to high estimate: {upside*100:.1f}%")
if downside is not None:
    print(f"Downside to low estimate: {downside*100:.1f}%")
```

## Data Sources

- **FCF** – From `stock.info` (`freeCashflow`) or operating cash flow minus capex; cash flow statement used when available.
- **Shares** – `sharesOutstanding` or `floatShares` from `stock.info`.
- **WACC** – From `stock.ratios.wacc` when available; otherwise a default (e.g. 10%) is used.
- **Comps** – P/E, EV/EBITDA, P/S and revenue/EBITDA/net income from yfinance for the stock and peers.

See [ROADMAP.md](../ROADMAP.md) Phase 1 – Valuation Module for the broader roadmap.
