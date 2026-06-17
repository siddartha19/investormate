# Educational Layer

Deterministic `explain()` / `show_work()` plus optional AI tutoring.

## Deterministic (no API key)

```python
from investormate import Stock

stock = Stock("AAPL")

# Formula + interpretation
print(stock.ratios.explain("wacc"))

# Step-by-step with real numbers
print(stock.ratios.show_work("current_ratio"))

# CFA topic tag
print(stock.ratios.cfa_topic("roe"))

# All ratios with plain-English assessment
print(stock.ratios.interpret())

# Red flags
print(stock.ratios.red_flags())

# Percentile vs peers
print(stock.ratios.percentile("pe", peer_values=[15, 20, 25, 30]))
```

## Practice problems

```python
from investormate import practice_generate

problem = practice_generate("tvm", difficulty="medium", seed=42)
print(problem["question"])
print(problem["answer"])
print(problem["solution_steps"])
```

Topics: `tvm`, `bonds`, `options`.

## AI tutoring (requires LLM key)

```python
from investormate import Investor

investor = Investor(openai_api_key="sk-...")
investor.ask_concept("What is modified duration and why does it matter?")
investor.explain_ratios("AAPL")
```

## Coursework export

```python
md = stock.report(format="markdown")
stock.to_excel("aapl_analysis.xlsx")  # pip install investormate[export]
```
