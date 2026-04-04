# InvestorMate Roadmap: The AI-Powered Full-Stack Finance Library for Python

> **Vision:** The AI-powered Python library that finance students use to learn, professionals use to analyze, and quants use to build — one package from Accounting 101 homework through portfolio optimization and alpha generation, with AI woven into every layer.

**Recent progress (v0.3.0):** In-memory **TTL cache + rate limiting** for yfinance; **`Stock.refresh()`** cache bust; **`stock.earnings`** (calendar, estimates, surprise history); portfolio **VaR** (historical/parametric) and **Monte Carlo**; **CAN SLIM**-style and **dividend growth** screens; **Momentum / Mean reversion / SMA crossover** strategy templates. See [CHANGELOG.md](CHANGELOG.md).

> **The "Full Stack" Strategy:** InvestorMate is built on three pillars — **Finance + AI + Education** — that no other library combines. The **educational foundation** (TVM, bond pricing, common-size analysis, `explain()`, `show_work()`) is the on-ramp that gets students installing in their first semester. The **AI engine** (multi-provider LLM: OpenAI, Claude, Gemini) turns every feature into a conversational experience — ask questions about any stock, get AI-generated explanations of your analysis, summarize 10-K filings in plain English, and receive AI-powered study feedback. The **professional toolkit** (portfolio optimization, ML alpha, SEC Edgar, strategy templates, tearsheets) is what those same students grow into on the job. No other Python library bridges all three.

> **Inspiration:** This roadmap incorporates best-in-class ideas from the systematic trading ecosystem — including tools like [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt), [quantstats](https://github.com/ranaroussi/quantstats), [vectorbt](https://github.com/polakowo/vectorbt), [QLib](https://github.com/microsoft/qlib), [OpenBB](https://github.com/OpenBB-finance/OpenBBTerminal), and [40+ academic trading strategies](https://github.com/paperswithbacktest/awesome-systematic-trading) — as well as AI-native finance tools, educational resources like [Tidy Finance](https://www.tidy-finance.org/python/), CFA/FRM curriculum frameworks, and the needs of Applied Accounting & Financial Analysis students worldwide.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Guiding Principles](#guiding-principles)
3. [The Full-Stack User Journey](#the-full-stack-user-journey)
4. [Current State & Gaps](#current-state--gaps)
5. [Architecture Overview](#architecture-overview)
6. [Phase 1: Foundation (v0.3–0.4)](#phase-1-foundation-v03-v04)
7. [Phase 1.5: Academic & Educational Foundation (v0.4)](#phase-15-academic--educational-foundation-v04)
8. [Phase 2: Professional Data (v0.5–0.7)](#phase-2-professional-data-v05-v07)
9. [Phase 3: Institutional Analytics (v0.8–1.0)](#phase-3-institutional-analytics-v08-v10)
10. [Phase 4: Terminal-Grade Features (v1.1–2.0)](#phase-4-terminal-grade-features-v11-v20)
11. [Phase 5: Platform & Ecosystem (v2.0+)](#phase-5-platform--ecosystem-v20)
12. [Technical Specifications](#technical-specifications)
13. [Success Metrics](#success-metrics)

---

## Executive Summary

InvestorMate aims to be the **definitive AI-powered Python package for financial learning, research, and analysis** — a single dependency that serves every stage of a finance professional's journey:

- **AI-native from day one** — Multi-provider LLM engine (OpenAI, Claude, Gemini) powering Q&A (`investor.ask()`), document summarization, financial statement analysis, AI tutoring, sentiment analysis, and report generation across every module
- **Educational toolkit** — TVM, bond pricing, financial statement analysis, ratio interpretation, CFA/FRM topic coverage, `explain()` and `show_work()` on every calculation, AI-powered study assistance
- **Multi-source data** with fallbacks and reliability
- **Institutional-quality analytics** (valuation, risk, screening)
- **Portfolio optimization** (efficient frontier, HRP, Black-Litterman)
- **Quantitative strategies** backed by academic research and proven Sharpe ratios
- **ML-powered alpha signals** and time series forecasting
- **Extensible architecture** for custom data sources, strategies, and plugins
- **Production-ready** performance, caching, and error handling

The roadmap is structured in six phases, from educational foundations through capabilities comparable to Bloomberg Terminal — while also incorporating the best ideas from the systematic/quantitative trading ecosystem. The unique differentiator: **no other Python library combines Finance + AI + Education in a single package.**

---

## Guiding Principles

1. **One package, one import** — No need to juggle yfinance, pandas-ta, Alpha Vantage, PyPortfolioOpt, quantstats, etc.
2. **AI-first, not AI-only** — Every feature designed to work *with and without* AI. Computations are pure math (no LLM needed); AI adds a conversational layer on top — ask questions, get explanations, summarize documents, generate reports. Multi-provider (OpenAI, Claude, Gemini) so users aren't locked in. AI is the **multiplier**, not the **dependency**.
3. **Learn → Analyze → Build** — Every feature works at three levels: educational (explain the concept), analytical (compute the number), professional (integrate into workflows). The same `stock.ratios.wacc` call can `show_work()` for a student, feed a DCF model for a PM, or be explained in plain English by the AI engine.
4. **Data-agnostic** — Pluggable backends; logic independent of data source.
5. **Feature-first** — Primary job is clean, consistent feature matrices and normalized data; users can plug into any backtesting engine (vectorbt, zipline, etc.). We do not aim to be a full backtesting framework.
6. **Modular layers** — Fundamentals, TA, and portfolio can be used independently. Optional capabilities (TA, AI, optimization) via `extras_require`; core stays minimal so you don't pull 50 deps for a few ratios.
7. **Quant-ready** — Academic strategies, portfolio optimization, and factor models out of the box.
8. **Professional-grade** — Suitable for quant research, fund analysis, and fintech apps.
9. **Syllabus-ready** — A professor can put `pip install investormate` on a syllabus. Educational features cover CFA L1-L3, FRM, and Applied Accounting & Financial Analysis curricula.
10. **Open core** — Core free; premium data/features via optional integrations.
11. **Pythonic** — Clean API, type hints, async where useful, Jupyter-friendly.
12. **Correctness over convenience** — Prefer failing loudly on bad or ambiguous data over returning clean-looking but wrong results (e.g. no silent forward-fill on delisted tickers).

---

## The Full-Stack User Journey

> The key insight behind InvestorMate's product strategy: **students become professionals.** The library that teaches them in school is the library they use for the rest of their career.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE INVESTORMATE FUNNEL                          │
│                  Finance  ×  AI  ×  Education                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SEMESTER 1 ─── pip install investormate                           │
│  Accounting 101   TVM calculator, common-size analysis, explain()  │
│                   Bond pricing, loan amortization schedules         │
│              AI:  investor.ask("AAPL", "Explain this balance sheet")│
│                   AI tutoring on any ratio or concept               │
│                                                                     │
│  SEMESTER 3 ─── stock.ratios + screener + show_work()              │
│  Financial        DuPont breakdown, Piotroski F-Score, Altman Z    │
│  Analysis         Peer benchmarking, industry percentiles           │
│              AI:  investor.ask("AAPL", "Is this stock undervalued?")│
│                   AI-powered red flag detection and commentary      │
│                                                                     │
│  SEMESTER 5 ─── portfolio.optimize + backtest                      │
│  Investments      CAPM regression, Fama-French factors, VaR        │
│  Capstone         Efficient frontier, strategy templates            │
│              AI:  AI-generated portfolio risk commentary            │
│                   Natural-language strategy explanations             │
│                                                                     │
│  YEAR 1 JOB ─── Full platform                                     │
│  Equity Research  SEC Edgar, tearsheets, ML alpha, report gen      │
│  / Quant Desk     Academic strategies, real-time data, exports     │
│              AI:  AI-summarized 10-K filings, earnings calls       │
│                   Full AI-generated research reports                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Competitive Landscape

| Library | Professional Features | AI Integration | Educational Features |
|---------|----------------------|----------------|---------------------|
| **FinanceToolkit** (4.5k stars) | 150+ ratios, multi-asset | None | None |
| **OpenBB** (65k stars) | Full terminal, data aggregation | Copilot (closed) | None |
| **QLib** (15k stars) | ML alpha, factor models | None | None |
| **Tidy Finance** | None (it's a textbook) | None | Textbook-style explanations |
| **Strategic Alpha** | DCF, technicals, risk | Experimental ML | Web-only, not installable |
| **InvestorMate** | 40+ ratios, DCF, VaR, MC, backtest | **Multi-LLM** (OpenAI, Claude, Gemini): Q&A, sentiment, summaries, reports | `explain()`, `show_work()`, TVM, bonds, CAPM, common-size, CFA tags |

**InvestorMate is the only library that combines Finance + AI + Education in a single installable package.**

---

## Current State & Gaps

### What Exists Today (v0.3.x)

| Domain | Capability | Maturity |
|--------|------------|----------|
| **Data** | yfinance only; TTL cache + rate limit (v0.3.0) | ⚠️ Fragile |
| **Fundamentals** | 40+ ratios, TTM, DuPont, ROIC, WACC | ✅ Solid |
| **Technicals** | 20+ native indicators (numpy/pandas) | ✅ Solid |
| **Scores** | Piotroski, Altman Z, Beneish M (full 8-variable when 2 periods + CF; else proxy) | ✅ Solid |
| **AI Engine** | Multi-provider LLM (OpenAI, Claude, Gemini): `investor.ask()`, document analysis, stock comparison, sentiment analysis, summary generation | ✅ Solid |
| **Screening** | Value, growth, dividend, custom, Magic Formula, CAN SLIM–style, dividend growth streak (v0.3.0) | ✅ Solid |
| **Portfolio** | Allocation, Sharpe/Sortino/Calmar/max DD/beta, VaR, Monte Carlo (v0.3.0), sector mix | ✅ Solid |
| **Backtesting** | Strategy framework, RSI example | ✅ Solid |
| **Correlation** | Matrix, pairs, diversification | ✅ Solid |
| **Sentiment** | News sentiment via AI | ✅ Solid |
| **Valuation** | DCF, comps, fair value, sensitivity | ✅ Solid |
| **Earnings** | Calendar, estimates, surprise history via `stock.earnings` (v0.3.0) | ⚠️ yfinance-dependent |
| **Transcripts** | Infrastructure only (no real data) | ❌ Placeholder |
| **SEC/Filings** | yfinance filings list | ⚠️ Limited |
| **Optimization** | None (no efficient frontier, HRP) | ❌ Missing |
| **Quant Strategies** | RSI example + 3 templates (momentum, mean reversion, SMA cross) (v0.3.0) | ⚠️ Growing |
| **Forecasting** | None | ❌ Missing |
| **ML Signals** | None | ❌ Missing |
| **Options** | None | ❌ Missing |
| **Reports** | None | ❌ Missing |
| **TVM Calculator** | None (PV, FV, annuities, amortization) | ❌ Missing |
| **Fin. Statement Analysis** | None (common-size, horizontal, vertical, trend) | ❌ Missing |
| **Fixed Income** | None (bond pricing, duration, convexity, yield curve) | ❌ Missing |
| **CAPM / Factor Models** | None (regression CAPM, Fama-French, SML) | ❌ Missing |
| **Educational Layer** | None (explain, show_work, CFA tags) | ❌ Missing |
| **Derivatives Basics** | None (Black-Scholes, Greeks, binomial tree) | ❌ Missing |
| **Export / Coursework** | None (Excel, Jupyter templates) | ❌ Missing |

### Critical Gaps vs. Bloomberg + Quant Platforms

- **Data:** Single source, no fallbacks, no real-time, no macro/economic data, limited global coverage
- **Optimization:** No portfolio optimization (efficient frontier, HRP, risk parity, Black-Litterman)
- **Performance Metrics:** Sortino, Calmar, max drawdown, beta added (v0.2.7); still missing Omega, full tearsheets, richer drawdown analytics
- **Strategies:** Templates shipped (v0.3.0); full academic library still roadmap
- **Regulatory:** No direct SEC Edgar, no 10-K/10-Q parsing
- **Earnings:** No transcripts; calendar/estimates/surprises via yfinance (v0.3.0)
- **Risk:** VaR + Monte Carlo on portfolio returns (v0.3.0); factor exposure still open
- **Screening:** Magic Formula (v0.2.7); CAN SLIM–style + dividend growth (v0.3.0); further screens open
- **Forecasting:** No time series forecasting (Prophet, ARIMA)
- **ML:** No factor models, alpha signals, or ML-driven predictions
- **Options:** No pricing (Black-Scholes), Greeks, or strategy builders
- **Visualization:** No interactive charts, tearsheets, or dashboards
- **Output:** No report generation, exports, or dashboards
- **Performance:** In-memory cache + rate limit (v0.3.0); async still open

### Critical Gaps vs. Educational / CFA / FRM Needs

- **Financial Statement Analysis:** No common-size, horizontal, vertical, or trend analysis — bread-and-butter for every accounting course
- **Time Value of Money:** No TVM calculator (PV, FV, annuities, perpetuities, amortization) — foundation of CFA L1 and every finance class
- **Fixed Income:** No bond pricing, duration, convexity, yield curve analysis — CFA L1 weights this at 11-14%
- **CAPM & Factor Models:** No regression-based CAPM, Security Market Line, Fama-French 3/5 factor models — core of CFA L1-L2 Quantitative Methods
- **Ratio Interpretation:** Ratios compute numbers but don't explain what they mean, flag red flags, or show industry percentiles
- **Educational Layer:** No `explain()`, `show_work()`, formula documentation, or CFA topic tagging on any calculation
- **Derivatives Basics:** No Black-Scholes, Greeks calculator, binomial tree, or payoff diagrams — CFA L1 weights Derivatives at 5-8%
- **Export for Coursework:** No Excel export, Jupyter templates, or formatted comparison tables for class submissions

### AI Engine — What Exists & What's Next

> *InvestorMate already ships a production-ready multi-provider AI engine. This is not a future feature — it's live today.*

**Shipped (v0.1.0+):**
- `Investor` class with multi-provider support (OpenAI, Claude, Gemini)
- `investor.ask(ticker, question)` — conversational Q&A about any stock using real data
- `investor.analyze_document(ticker, url, question)` — AI analysis of articles and documents
- `investor.compare(tickers, question)` — multi-stock AI comparison with structured output
- `Stock.sentiment` — AI-powered news sentiment analysis
- Summary generation — structured stock overviews via LLM
- Prompt engineering — specialized prompts for analysis, comparison, document insights
- Response parsing — structured JSON output with chart data support

**Planned AI expansion across phases:**

| Phase | AI Feature | Description |
|-------|-----------|-------------|
| 1.5 | AI financial tutor | Contextual explanations of ratios, statements, concepts using real stock data |
| 1.5 | AI ratio commentary | Narrative analysis connecting multiple ratios into a coherent story |
| 1.5 | AI study assistant | Conceptual Q&A ("What is duration?") grounded in library computations |
| 1.5 | AI practice feedback | Review student analysis against actual data and flag errors |
| 2.3 | AI filing summarization | Summarize 10-K/10-Q risk factors, MD&A sections via SEC Edgar |
| 2.6 | AI macro commentary | Natural-language interpretation of economic data and yield curves |
| 3.1 | AI risk commentary | Narrative explanation of VaR, Monte Carlo results, factor exposures |
| 3.4 | AI report generation | Full AI-generated equity research reports (fundamentals + technicals + sentiment) |
| 3.5 | AI strategy explanation | Plain-English description of what each academic strategy does and why |
| 4.2 | AI regime commentary | Natural-language description of detected market regimes |
| 4.3 | AI options analysis | AI-powered options strategy recommendations based on market view |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         InvestorMate Architecture                            │
├──────────────────────────────────────────────────────────────────────────────┤
│  PRESENTATION LAYER                                                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │  Python    │ │  REST API  │ │  Jupyter   │ │  Reports   │ │ Interactive││
│  │  API       │ │  (Future)  │ │  Widgets   │ │ PDF/Excel  │ │ Charts     ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘│
├──────────────────────────────────────────────────────────────────────────────┤
│  EDUCATIONAL LAYER  ★ NEW — Phase 1.5                                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │ explain()  │ │ show_work()│ │ CFA/FRM    │ │ Practice   │ │ Jupyter    ││
│  │ formulas   │ │ step-by-   │ │ Topic Tags │ │ Problem    │ │ Templates  ││
│  │ & context  │ │ step calc  │ │ & Mapping  │ │ Generator  │ │ & Export   ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘│
├──────────────────────────────────────────────────────────────────────────────┤
│  AI ENGINE  ★ CORE DIFFERENTIATOR — threads through every layer             │
│  ┌──────────────────────────────────────────────────────────────────────────┐│
│  │  Multi-Provider LLM (OpenAI / Claude / Gemini)                          ││
│  │  investor.ask() │ Sentiment │ Summaries │ Reports │ Tutoring │ Compare  ││
│  └──────────────────────────────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────────────┤
│  ANALYTICS LAYER                                                             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │ Valuation  │ │ Risk &     │ │ Screening  │ │ AI-Powered │ │ ML Alpha   ││
│  │ DCF, Comps │ │ VaR, MC    │ │ Magic, etc │ │ Analysis   │ │ Signals    ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘│
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐               │
│  │ Portfolio  │ │ Forecasting│ │ Options    │ │ Performance│               │
│  │ Optimizer  │ │ Prophet,   │ │ Pricing,   │ │ Tearsheets │               │
│  │ HRP, MVO   │ │ ARIMA      │ │ Greeks     │ │ QuantStats │               │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘               │
├──────────────────────────────────────────────────────────────────────────────┤
│  ACADEMIC FINANCE LAYER  ★ NEW — Phase 1.5                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │ TVM        │ │ Fixed      │ │ CAPM &     │ │ Fin. Stmt  │ │ Derivatives││
│  │ PV/FV/     │ │ Income     │ │ Factor     │ │ Analysis   │ │ Basics     ││
│  │ Annuities  │ │ Bonds,     │ │ Models     │ │ Common-sz  │ │ BS, Greeks ││
│  │ Amort.     │ │ Duration   │ │ FF3, FF5   │ │ Horiz/Vert │ │ Binomial   ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘│
├──────────────────────────────────────────────────────────────────────────────┤
│  CORE LAYER                                                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │ Stock      │ │ Portfolio  │ │ Correlation│ │ Backtest   │ │ Strategy   ││
│  │ Ratios     │ │ Allocation │ │ Sentiment  │ │ Engine     │ │ Library    ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘│
├──────────────────────────────────────────────────────────────────────────────┤
│  DATA ABSTRACTION LAYER                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────┐│
│  │  DataProvider Interface  │  Cache  │  Rate Limiter  │  Fallback          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────────────┤
│  DATA SOURCES                                                                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐│
│  │yfinance │ │ Alpha   │ │ Polygon │ │ SEC     │ │ FRED    │ │ Quandl/  ││
│  │         │ │ Vantage │ │ .io     │ │ Edgar   │ │ (Macro) │ │ Nasdaq   ││
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └──────────┘│
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation (v0.3–0.4)

**Goal:** Harden the core, fix robustness issues, and add essential valuation.

**Timeline:** 2–3 months

### 1.1 Robustness & Reliability

| Task | Description | Priority |
|------|-------------|----------|
| Data fetcher null safety | Handle `None`/empty from yfinance in all fetchers | P0 |
| Portfolio exception handling | Replace bare `except:` with `except Exception:` | P0 |
| Test configuration | Fix pytest addopts (coverage optional) | P1 |
| Input validation | Validate period/interval in Stock, Correlation, Backtest | P1 |
| Dependency pinning | Constrain yfinance version for stability | P1 |
| Error tests | Tests for invalid ticker, empty data, network failure | P2 |

### 1.2 Valuation Module

| Feature | Description | API |
|---------|-------------|-----|
| DCF Model | 5–10 year DCF with terminal value | `stock.valuation.dcf(growth_rate=0.05, terminal_multiple=15)` |
| Comparable Companies | Peer multiples (P/E, EV/EBITDA, P/S) | `stock.valuation.comps(peers=["MSFT","GOOGL"])` |
| Fair Value Summary | Range from DCF + comps | `stock.valuation.summary()` |
| Sensitivity Table | DCF vs. growth rate, WACC | `stock.valuation.sensitivity()` |

### 1.3 Documentation & DX

- API reference (auto-generated from docstrings)
- Migration guide for v0.2 → v0.3
- Jupyter quickstart notebook
- Changelog discipline (Keep a Changelog)
- **Debug / source trace** — `debug=True` or `source_trace=True` (e.g. on Stock or data fetchers) to expose: raw payload, data source, and transform steps applied. Makes the abstraction layer inspectable instead of a black box; documented in API reference and a short "Data provenance" section.

### 1.4 Data Correctness & Consistency *(Community feedback: "boring plumbing" first)*

> *Systematic users consistently cite silent NaN handling, misaligned dates, and inconsistent dividend/split adjustments as what burns them. This section addresses that before expanding features.*

| Task | Description | Priority |
|------|-------------|----------|
| NaN policy | No silent forward-fill; explicit fill/error behavior. Document when and how NaNs are propagated or raised. | P0 |
| Splits & dividends | Single, documented adjustment policy across all price-derived series (e.g. all total-return adjusted, or explicit `adjusted=False` option). Same semantics across endpoints. | P0 |
| Delisted / missing data | No silent fill that produces "clean" wrong series. Optional strict mode: error or flag instead of returning misleading data. | P1 |
| Date alignment | When multiple providers are added, same date semantics and alignment rules; document in Data layer. | P1 |

**Principle:** Fail loudly on ambiguous or bad data rather than returning plausible-but-wrong outputs. Phase 4.7 (Data Quality & Validation) builds on this with advanced checks (confidence scores, outlier detection).

**Deliverables:** v0.3 (robustness), v0.4 (valuation + data correctness + educational foundation)

---

## Phase 1.5: Academic & Educational Foundation (v0.4)

**Goal:** Make InvestorMate the go-to Python library for finance students, CFA/FRM candidates, and Applied Accounting & Financial Analysis programs. Pure-math modules with zero new API dependencies — this is the on-ramp that creates the largest possible user funnel.

**Timeline:** 1–2 months (all modules are self-contained, pure numpy/pandas math)

**Why now (before Phase 2)?**
1. **Market size** — Millions of finance/accounting students vs. thousands of quant traders
2. **Stickiness** — Students who learn InvestorMate in school use it for years after
3. **No competition** — FinanceToolkit has 150+ ratios but zero educational features; Tidy Finance is a book, not a library; Strategic Alpha is a web app, not installable
4. **Zero dependencies** — Pure math (numpy/pandas only), no new API keys needed
5. **Content marketing** — "The Python library for finance students" is a highly searchable niche

### 1.5.1 Time Value of Money (TVM) Module

> *CFA L1: Quantitative Methods (6-9% weight). Foundation of every corporate finance and investments course.*

| Feature | Description | API |
|---------|-------------|-----|
| Present Value | Lump sum PV with compounding | `tvm.present_value(fv=1000, rate=0.05, n=10)` |
| Future Value | Lump sum FV with compounding | `tvm.future_value(pv=500, rate=0.08, n=5)` |
| Annuity PV/FV | Ordinary annuity and annuity due | `tvm.annuity_pv(pmt=100, rate=0.08, n=20, due=True)` |
| Perpetuity | Level and growing perpetuities | `tvm.perpetuity(pmt=50, rate=0.05, growth=0.02)` |
| Net Present Value | NPV of uneven cash flows | `tvm.npv(rate=0.10, cashflows=[-1000, 300, 400, 500])` |
| Internal Rate of Return | Solve for IRR | `tvm.irr(cashflows=[-1000, 300, 400, 500])` |
| Loan Amortization | Full schedule with interest/principal split | `tvm.amortization_schedule(principal=100000, rate=0.04, n=30)` |
| Effective Annual Rate | Convert between nominal/effective rates | `tvm.ear(nominal=0.08, compounding=12)` |

### 1.5.2 Financial Statement Analysis Module

> *CFA L1: Financial Statement Analysis (11-14% weight). Every intermediate accounting and financial analysis course assigns this.*

| Feature | Description | API |
|---------|-------------|-----|
| Common-size income statement | All items as % of revenue | `stock.financials.common_size("income")` |
| Common-size balance sheet | All items as % of total assets | `stock.financials.common_size("balance_sheet")` |
| Horizontal analysis | Year-over-year $ and % changes across all line items | `stock.financials.horizontal(periods=5)` |
| Vertical analysis | Component breakdown within a single period | `stock.financials.vertical(period="2025")` |
| Trend analysis | Multi-year indexed trends (base year = 100) | `stock.financials.trend(base_year=2021)` |
| DuPont decomposition (visual) | Formatted 3-component and 5-component breakdown tree | `stock.ratios.dupont_breakdown()` |
| Cash flow quality | Operating CF vs. net income, accruals ratio | `stock.financials.cash_flow_quality()` |

### 1.5.3 Fixed Income Analytics

> *CFA L1: Fixed Income (11-14% weight). Same weight as Equity — yet zero Python libraries do this well for students.*

| Feature | Description | API |
|---------|-------------|-----|
| Bond pricing | Clean price from coupon, YTM, maturity | `bond.price(face=1000, coupon=0.06, ytm=0.05, n=10)` |
| Accrued interest | Dirty price = clean + accrued | `bond.accrued_interest(settlement_date, coupon, frequency)` |
| Yield to Maturity | Solve for YTM given price | `bond.ytm(price=950, face=1000, coupon=0.06, n=10)` |
| Current yield | Annual coupon / price | `bond.current_yield()` |
| Macaulay duration | Weighted avg time to cash flows | `bond.duration()` |
| Modified duration | Price sensitivity to yield changes | `bond.modified_duration()` |
| Convexity | Second-order price sensitivity | `bond.convexity()` |
| Price change estimate | Duration + convexity approximation | `bond.price_change(yield_change=0.01)` |
| Yield curve (from FRED) | US Treasury term structure | `market.yield_curve()` |
| Bond ladder builder | Construct maturity ladder | `portfolio.bond_ladder(maturities=[1,3,5,7,10])` |

### 1.5.4 CAPM & Factor Models

> *CFA L1-L2: Quantitative Methods + Equity Investments. Bridges textbook theory to real data.*

| Feature | Description | API |
|---------|-------------|-----|
| CAPM regression | Beta, alpha, R-squared vs. benchmark, with residual plots | `stock.capm(benchmark="SPY")` |
| Security Market Line | Plot SML with multiple stocks, identify over/under-valued | `market.sml(tickers=["AAPL","MSFT","GOOGL","JPM"])` |
| Jensen's alpha | Risk-adjusted excess return | `stock.jensen_alpha(benchmark="SPY")` |
| Fama-French 3-factor | Market, size (SMB), value (HML) regression | `stock.factor_model(model="ff3")` |
| Fama-French 5-factor | + profitability (RMW) + investment (CMA) | `stock.factor_model(model="ff5")` |
| Alpha/Beta decomposition | Systematic vs. idiosyncratic risk breakdown | `stock.risk_decomposition()` |

### 1.5.5 Derivatives Basics

> *CFA L1: Derivatives (5-8% weight). Moved from Phase 4.3 — basic pricing is pure math, no market data needed.*

| Feature | Description | API |
|---------|-------------|-----|
| Black-Scholes pricing | European call/put theoretical price | `options.black_scholes(S=150, K=155, T=0.5, r=0.05, sigma=0.25)` |
| Greeks calculator | Delta, Gamma, Theta, Vega, Rho with interpretation | `options.greeks(S=150, K=155, T=0.5, r=0.05, sigma=0.25)` |
| Put-Call Parity | Verify / demonstrate the relationship | `options.put_call_parity(call=12, put=8, S=150, K=148, r=0.05, T=0.25)` |
| Binomial tree | Multi-step binomial pricing with tree visualization | `options.binomial(S=100, K=105, T=1, r=0.05, sigma=0.2, steps=3)` |
| Payoff diagrams | Visual P&L at expiry for basic strategies | `options.payoff_diagram(strategy="bull_call_spread", legs=[...])` |
| Strategy P&L | Max profit, max loss, breakeven for common strategies | `options.strategy_metrics("covered_call", S=150, K=160, premium=5)` |

### 1.5.6 Educational Layer (explain / show_work / interpret) + AI Tutoring

> *The differentiator. No finance library does this. This is what makes InvestorMate syllabus-ready. The educational layer works at two levels: **deterministic** (pure-math explain/show_work — no API key needed) and **AI-powered** (conversational tutoring, natural-language explanations — requires LLM key).*

#### Deterministic (No AI Key Required)

| Feature | Description | API |
|---------|-------------|-----|
| Formula explanation | Returns the formula, variable definitions, and interpretation guide for any ratio or metric | `stock.ratios.explain("wacc")` |
| Step-by-step calculation | Shows raw numbers plugged into the formula | `stock.ratios.show_work("roic")` |
| CFA topic tags | Every ratio/concept tagged with CFA L1/L2/L3 topic area | `stock.ratios.cfa_topic("current_ratio")` → "Financial Statement Analysis (L1)" |
| FRM topic tags | Risk metrics tagged with FRM Part I/II topic area | `portfolio.var.frm_topic()` → "Valuation and Risk Models (Part I)" |
| Ratio interpretation | Plain-English assessment of each ratio value | `stock.ratios.interpret()` → {"current_ratio": {"value": 1.8, "assessment": "Healthy liquidity..."}} |
| Red flag detection | Highlights concerning patterns across ratios | `stock.ratios.red_flags()` → ["Rising receivables with falling revenue", ...] |
| Industry percentile | Where a ratio falls vs. sector peers | `stock.ratios.percentile("pe_ratio")` → "72nd percentile of Technology sector" |
| Historical ratio trends | Multi-year ratio trajectory | `stock.ratios.history("current_ratio", years=5)` |
| Practice problems | Generate random problems with solutions (TVM, bond pricing, etc.) | `practice.generate("tvm", difficulty="medium")` |

#### AI-Powered (Requires LLM Key — OpenAI, Claude, or Gemini)

> *Leverages the existing `Investor` AI engine (multi-provider: OpenAI, Claude, Gemini) to add a conversational layer on top of every educational feature.*

| Feature | Description | API |
|---------|-------------|-----|
| AI financial tutor | Ask any question about a stock's financials and get a detailed, contextual explanation using real data | `investor.ask("AAPL", "Why is the current ratio declining?")` |
| AI ratio commentary | AI-generated narrative analysis of all ratios — not just numbers, but what they mean together | `investor.explain_ratios("AAPL")` |
| AI statement analysis | Natural-language summary of common-size / horizontal analysis results with trend insights | `investor.analyze_financials("AAPL", analysis="common_size")` |
| AI study assistant | Ask conceptual questions — "What is duration?", "When would you use VaR vs. CVaR?" — with textbook-quality answers grounded in the library's own computations | `investor.ask_concept("Explain modified duration and why it matters")` |
| AI-powered red flags | AI reviews all ratios, scores, and trends together to generate a narrative risk assessment | `investor.red_flag_analysis("AAPL")` |
| AI comparison narrative | Multi-stock comparative analysis in natural language with recommendations | `investor.compare(["AAPL","MSFT","GOOGL"], question="Which is the best value?")` |
| AI practice feedback | AI evaluates a student's analysis and provides feedback — "Your DCF assumes 15% growth, but AAPL's 5-year CAGR is 8%..." | `investor.review_analysis(student_analysis, ticker="AAPL")` |

### 1.5.7 Export & Coursework Tools

| Feature | Description | API |
|---------|-------------|-----|
| Excel export | Formatted workbook with sheets for financials, ratios, charts | `stock.to_excel("aapl_analysis.xlsx")` |
| Markdown report | Publication-quality report for class submissions | `stock.report(format="markdown")` |
| Comparison tables | Formatted multi-stock comparison | `investor.compare(["AAPL","MSFT","GOOGL"]).to_table()` |
| Jupyter templates | Pre-built notebooks for common assignments | `examples/notebooks/financial_analysis_template.ipynb` |
| CSV export | Raw data export for further analysis | `stock.financials.to_csv("aapl_financials.csv")` |

### CFA / FRM Curriculum Coverage Map

> *Mapping InvestorMate features to certification exam topics.*

| CFA L1 Topic | Weight | InvestorMate Coverage | Phase |
|--------------|--------|----------------------|-------|
| Ethical Standards | 15-20% | N/A (not a code feature) | — |
| Quantitative Methods | 6-9% | TVM, statistics, probability, simulation | 1.5 + Done |
| Economics | 6-9% | FRED macro data, economic calendar | 2.6 |
| Financial Statement Analysis | 11-14% | Common-size, horizontal, vertical, trend, ratios, DuPont | 1.5 + Done |
| Corporate Issuers | 6-9% | WACC, capital structure, dividends | Done |
| Equity Investments | 11-14% | DCF, comps, CAPM, factor models, screening | 1.5 + Done |
| Fixed Income | 11-14% | Bond pricing, duration, convexity, yield curve | 1.5 |
| Derivatives | 5-8% | Black-Scholes, Greeks, binomial, payoff diagrams | 1.5 |
| Alternative Investments | 7-10% | Crypto data (future), ETF analytics | 4.3 |
| Portfolio Management | 8-12% | VaR, Monte Carlo, optimization, efficient frontier | Done + 3.1 |

| FRM Part I Topic | Weight | InvestorMate Coverage | Phase |
|------------------|--------|----------------------|-------|
| Foundations of Risk Mgmt | 20% | Risk concepts, explain() | 1.5 + Done |
| Quantitative Analysis | 20% | Statistics, VaR methods, Monte Carlo | Done |
| Financial Markets & Products | 30% | Bonds, derivatives, equities, FRED macro | 1.5 + 2.6 |
| Valuation & Risk Models | 30% | Black-Scholes, Greeks, VaR, duration, convexity | 1.5 + Done |

**Deliverables:** v0.4.0 ("Student Edition" release)

---

## Phase 2: Professional Data (v0.5–0.7)

**Goal:** Multi-source data, caching, macro data, and regulatory content. **Modular installs:** `pip install investormate` (core), `investormate[ta]`, `investormate[ai]`, `investormate[optimization]`, etc., with clear docs so core stays minimal and optional features are opt-in.

**Timeline:** 3–4 months

### 2.1 Pluggable Data Layer

| Component | Description |
|-----------|-------------|
| `DataProvider` interface | Abstract base: `get_quote()`, `get_history()`, `get_financials()`, etc. |
| yfinance provider | Wrap existing fetchers |
| Alpha Vantage provider | Optional, API key required |
| Fallback chain | Primary → secondary on failure |
| Unified response schema | Normalized dict/DataFrame across providers |

**Backtest-safe data semantics** *(Community feedback: restatements, point-in-time, survivorship bias.)* Document and enforce where feasible so backtests and screens aren't invalidated by subtle data issues:

| Concern | Approach |
|---------|----------|
| **Restatements** | Document whether fundamentals use as-reported vs. restated figures; document in API and data-assumptions doc. |
| **Point-in-time** | Explicit "latest available" vs. "as-of-date" (point-in-time) fundamentals; document which endpoints guarantee which; support for point-in-time where provider allows. |
| **Survivorship bias** | Document whether screens/backtest universes include delisted names; option to include/exclude; document in backtest and screening docs. |

Versioned data snapshots and clear separation between "latest" and "point-in-time" are part of the data layer design.

### 2.2 Caching & Performance

| Feature | Description |
|---------|-------------|
| In-memory TTL cache | **Done (v0.3.0):** per-fetcher TTLs (quotes ~60s, financials ~1h, etc.); `Stock.refresh()` invalidates ticker keys. |
| Cache invalidation | Manual `stock.refresh()` or TTL expiry |
| Batch fetching | **Done (v0.2.7):** `Stock.batch(["AAPL","MSFT","GOOGL"])`. |
| Rate limiting | **Done (v0.3.0):** token-bucket default 2/sec; `configure_data_cache(calls_per_second=...)`. |

### 2.3 SEC Edgar Integration

| Feature | Description | API |
|---------|-------------|-----|
| 10-K/10-Q fetch | Direct SEC Edgar download | `stock.sec.get_filing("10-K", year=2024)` |
| Filing list | All filings with dates and types | `stock.sec.filings()` |
| AI summarization | LLM summary of filing | `investor.summarize_filing(ticker, filing_type, year)` |
| Risk factor extraction | Key risk factors from 10-K | `stock.sec.risk_factors(year=2024)` |
| Insider transactions | Form 4 data | `stock.sec.insider_transactions()` |

### 2.4 Earnings & Estimates

| Feature | Description | API |
|---------|-------------|-----|
| Earnings calendar | Dates, estimates, actuals | `stock.earnings.calendar()` |
| Surprise history | Actual vs. estimate | `stock.earnings.surprise_history()` |
| Transcript placeholder | Interface for future transcript source | `stock.earnings.transcript(year, quarter)` |
| Analyst estimates | Consensus EPS, revenue | `stock.earnings.estimates()` |

### 2.5 Full Beneish M-Score

- ~~Implement full 8-variable Beneish M-Score~~ **Done (v0.2.7)** — `beneish_m_score_detail()`; requires two overlapping statement periods from yfinance; see docstring for line-item caveats.
- Use historical financials (2+ years)
- Document data requirements and limitations

### 2.6 Macro & Economic Data *(NEW)*

> *Inspired by [OpenBB Terminal](https://github.com/OpenBB-finance/OpenBBTerminal), [pandas-datareader](https://github.com/pydata/pandas-datareader), and [Quandl](https://github.com/quandl/quandl-python).*

| Feature | Description | API |
|---------|-------------|-----|
| FRED integration | GDP, CPI, unemployment, interest rates, yield curve | `market.macro.fred("GDP")` |
| Treasury yields | Full yield curve, 10Y-2Y spread | `market.macro.treasury_yields()` |
| Economic calendar | FOMC dates, jobs reports, CPI releases | `market.macro.economic_calendar()` |
| VIX & fear gauges | CBOE VIX, put/call ratio | `market.macro.vix()` |
| pandas-datareader | Multi-source access via unified interface | Internal provider |
| Quandl/Nasdaq Data Link | Commodities, futures, alternative datasets | Optional provider |

**Why:** Every investor needs macro context. FRED is free, comprehensive, and the gold standard for economic data. This transforms InvestorMate from a stock-only tool into a complete market intelligence package.

**Deliverables:** v0.5 (data layer), v0.6 (SEC + earnings + macro), v0.7 (polish)

---

## Phase 3: Institutional Analytics (v0.8–1.0)

**Goal:** Risk, optimization, screening, strategies, and portfolio analytics at institutional level.

**Timeline:** 4–5 months

### 3.1 Portfolio Risk, Optimization & Performance Analytics

> *Inspired by [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt), [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib), [quantstats](https://github.com/ranaroussi/quantstats), and [pyfolio](https://github.com/quantopian/pyfolio).*

#### Risk Analytics

| Feature | Description | API |
|---------|-------------|-----|
| VaR (Historical) | Value at Risk (95%, 99%) | `portfolio.var(confidence=0.95)` |
| VaR (Parametric) | Normal distribution VaR | `portfolio.var(method="parametric")` |
| Monte Carlo | Simulated return distribution | `portfolio.monte_carlo_simulation(n=1000)` |
| Beta | vs. SPY or custom benchmark | `portfolio.beta(benchmark="SPY")` |
| Factor exposure | Size, value, momentum proxies | `portfolio.factor_exposure()` |
| Drawdown analysis | Max drawdown, duration, underwater chart | `portfolio.drawdown_analysis()` |
| Rebalancing suggestions | Target allocation vs. current | `portfolio.rebalance_suggestions(target_allocation)` |
| Tax-loss harvesting | Identify candidates | `portfolio.tax_loss_harvesting_candidates()` |

#### Portfolio Optimization *(NEW)*

| Feature | Description | API |
|---------|-------------|-----|
| Mean-Variance (Markowitz) | Classic efficient frontier optimization | `portfolio.optimize(method="max_sharpe")` |
| Minimum Volatility | Lowest-risk portfolio on frontier | `portfolio.optimize(method="min_vol")` |
| Hierarchical Risk Parity | Modern, no covariance inversion needed | `portfolio.optimize(method="hrp")` |
| Risk Parity | Equal risk contribution across assets | `portfolio.optimize(method="risk_parity")` |
| Black-Litterman | Incorporate investor views into allocation | `portfolio.black_litterman(views={"AAPL": 0.10})` |
| Efficient Frontier | Plot full frontier with Sharpe-optimal point | `portfolio.efficient_frontier(plot=True)` |
| Constraints | Sector limits, position caps, ESG filters | `portfolio.optimize(constraints={"max_weight": 0.2})` |

**Why:** PyPortfolioOpt (4k+ stars) and Riskfolio-Lib exist because this is the #1 feature quant-curious investors want. InvestorMate wraps both approaches into a single clean API.

#### Performance Metrics & Tearsheets *(NEW)*

| Feature | Description | API |
|---------|-------------|-----|
| Full metrics suite | Sortino, Calmar, Omega, Tail ratio, Win rate, Kelly criterion, Expectancy, Gain/Pain — 30+ metrics total | `portfolio.metrics()` |
| Tearsheet generation | HTML report: equity curve, drawdown chart, monthly returns heatmap, rolling Sharpe | `portfolio.tearsheet()` |
| Benchmark comparison | Alpha, beta, R-squared, tracking error, information ratio vs. SPY or custom | `portfolio.tearsheet(benchmark="SPY")` |
| Backtest tearsheets | Same tearsheet quality for backtest results | `backtest_result.tearsheet(benchmark="SPY")` |

**Why:** quantstats (3k+ stars) proves the demand. This bridges "basic portfolio tracking" to "institutional analytics" in one shot, and supercharges the backtest module's output.

### 3.2 Institutional Screens

| Screen | Description | API |
|--------|-------------|-----|
| Magic Formula | Greenblatt (ROIC + Earnings Yield) | `screener.magic_formula(top_n=50)` — **shipped v0.2.7** |
| CAN SLIM | O'Neil criteria | `screener.can_slim()` |
| Dividend Aristocrats | 25+ years dividend growth | `screener.dividend_aristocrats()` |
| Quality + Momentum | ROE, ROA, momentum | `screener.quality_momentum()` |
| Sector-relative | Cheap vs. sector peers | `screener.sector_relative_value()` |
| Custom universes | S&P 500, Russell 3000, sector ETFs | `screener.universe("SP500")` |

### 3.3 Peer Comparison

| Feature | Description | API |
|---------|-------------|-----|
| Auto peer selection | By sector (major US ticker universe) | **`Stock.peers` + `stock.compare_with()` (v0.2.7)** |
| Auto peer selection | By sector/industry | `investor.compare_peers("AAPL", auto_peers=True)` (planned) |
| Custom peer comparison | User-defined list | `investor.compare_peers("AAPL", peers=["MSFT","GOOGL"])` |
| Peer valuation table | Multiples, growth, margins | `stock.valuation.peer_table()` |
| Sector percentile | Rank vs. sector | `stock.valuation.sector_percentile()` |

### 3.4 Research Report Generation

| Feature | Description | API |
|---------|-------------|-----|
| Full report | Fundamentals + technicals + sentiment + AI summary | `investor.generate_report("AAPL")` |
| Export formats | Markdown, HTML, PDF, Excel | `investor.generate_report("AAPL", format="pdf")` |
| Customizable sections | Include/exclude sections | `investor.generate_report("AAPL", sections=["valuation","risk"])` |
| Comparison report | Multi-stock | `investor.generate_report(["AAPL","MSFT","GOOGL"])` |

### 3.5 Academic Strategy Library & Feature Export *(EXPANDED)*

> *Inspired by [40+ strategies from paperswithbacktest](https://github.com/paperswithbacktest/awesome-systematic-trading) — each backed by academic research with published Sharpe ratios.*

**Positioning:** InvestorMate focuses on **clean feature matrices and signals**; we do not aim to replace vectorbt, zipline, or Backtrader. Strategy templates demonstrate how to use our outputs in your own backtester. Export utilities (e.g. feature/signal DataFrames in a format ready for vectorbt or zipline) make it dead simple to get from InvestorMate data → your engine.

- **Strategy templates** — Predefined logic (momentum, mean-reversion, factor) that produce signals/weights; runnable with our minimal backtest runner for quick checks, or **export signals for use in vectorbt/zipline/Backtrader**.
- **Academic citations** — Each strategy documents paper, Sharpe, and rebalancing; use them as feature/signal recipes rather than as a full backtesting framework.

#### Core Strategy Templates

| Strategy | Description | API |
|----------|-------------|-----|
| Momentum | Price momentum, relative strength (12-month) | `from investormate.strategies import MomentumStrategy` |
| Mean-Reversion | RSI, Bollinger Band, oversold/overbought reversion | `from investormate.strategies import MeanReversionStrategy` |
| Factor Models | Value (P/E, P/B), quality (ROE, ROA), size, momentum | `from investormate.strategies import FactorStrategy` |
| SMA Crossover | Dual moving average crossover (50/200 day) | `from investormate.strategies import SMACrossoverStrategy` |
| Customizable params | All strategies expose tunable parameters | `MomentumStrategy(lookback=12, top_n=10)` |

#### Academic Strategies (Research-Backed) *(NEW)*

Strategies sourced from peer-reviewed papers, each with documented Sharpe ratios, volatility profiles, and rebalancing frequencies.

| Strategy | Sharpe | Asset Class | Paper | API |
|----------|--------|-------------|-------|-----|
| Asset Growth Effect | 0.835 | Equities | [Cooper et al.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1335524) | `from investormate.strategies import AssetGrowthStrategy` |
| Short Term Reversal | 0.816 | Equities | [Gutierrez & Kelley](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1605049) | `from investormate.strategies import ShortTermReversalStrategy` |
| Low Volatility Factor | 0.717 | Equities | [Baker et al.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865) | `from investormate.strategies import LowVolatilityStrategy` |
| Paired Switching | 0.691 | Bonds/Equities | [Shilling](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1917044) | `from investormate.strategies import PairedSwitchingStrategy` |
| Pairs Trading | 0.634 | Equities | [Gatev et al.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=141615) | `from investormate.strategies import PairsTradingStrategy` |
| Trend Following | 0.569 | Equities | [Han et al.](https://www.cis.upenn.edu/~mkearns/finread/trend.pdf) | `from investormate.strategies import TrendFollowingStrategy` |
| ESG Factor Momentum | 0.559 | Equities | [Nagy & Kassam](https://www.semanticscholar.org/paper/Can-ESG-Add-Alpha-An-Analysis-of-ESG-Tilt-and-Nagy-Kassam/64f77da4f8ce5906a73ffe4e9eec7c49c0960acc) | `from investormate.strategies import ESGMomentumStrategy` |
| Time Series Momentum | 0.576 | Multi-asset | [Moskowitz et al.](https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf) | `from investormate.strategies import TimeSeriesMomentumStrategy` |
| Asset Class Trend-Following | 0.502 | Multi-asset | [Faber](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461) | `from investormate.strategies import AssetClassTrendStrategy` |
| FED Model | 0.369 | Bonds/Equities | [Estrada](https://www.researchgate.net/publication/228267011_The_FED_Model_and_Expected_Asset_Returns) | `from investormate.strategies import FEDModelStrategy` |

**Why:** These aren't toy examples — they're published, peer-reviewed strategies with real performance data. Each one comes with a paper citation. The value is in **reproducible feature/signal definitions** and easy export to your backtesting engine, not in competing with dedicated backtest frameworks.

### 3.6 ML-Powered Alpha Signals *(NEW)*

> *Inspired by [QLib (Microsoft, 15k+ stars)](https://github.com/microsoft/qlib), [FinRL](https://github.com/AI4Finance-Foundation/FinRL), and [MlFinLab](https://github.com/hudson-and-thames/mlfinlab).*

| Feature | Description | API |
|---------|-------------|-----|
| Factor model framework | Define, combine, and backtest alpha factors | `from investormate.ml import AlphaModel` |
| Feature engineering | Auto-generate features from fundamentals + technicals | `model.auto_features(universe="SP500")` |
| ML signal generation | Train models (gradient boost, random forest) to predict returns | `model.train(start="2015-01-01", end="2024-01-01")` |
| Alpha scoring | Score stocks by predicted alpha | `model.predict("AAPL")` |
| Feature importance | Which factors actually predict returns | `model.feature_importance()` |
| Walk-forward validation | Proper out-of-sample testing | `model.walk_forward(n_splits=5)` |

**Why:** Microsoft's QLib (15k+ stars) proves the demand. Even a basic ML pipeline sets InvestorMate apart from every other Python finance package. This is the bridge from "analysis tool" to "alpha generation platform."

**Deliverables:** v0.8 (risk + optimization + performance), v0.9 (screens + peers + strategy library + ML), v1.0 (reports + 1.0 release)

---

## Phase 4: Terminal-Grade Features (v1.1–2.0)

**Goal:** Capabilities that approach Bloomberg Terminal's core functionality, plus quant-platform features.

**Timeline:** 6–9 months

### 4.1 Real-Time & Streaming (Optional)

| Feature | Description | Notes |
|---------|-------------|-------|
| WebSocket quotes | Real-time price updates | Requires Polygon/IEX paid tier |
| Delayed quotes | 15-min delay (free tier) | Alpha Vantage, etc. |
| Streaming interface | `async for quote in stock.stream_quotes()` | For dashboards |

### 4.2 Advanced Technical Analysis & Forecasting

> *Inspired by [Facebook Prophet](https://github.com/facebook/prophet), [tsfresh](https://github.com/blue-yonder/tsfresh), [pmdarima](https://github.com/alkaline-ml/pmdarima), and [mplfinance](https://github.com/matplotlib/mplfinance).*

#### Advanced TA

| Feature | Description | API |
|---------|-------------|-----|
| Support/Resistance | Auto-detect levels | `stock.technicals.support_resistance()` |
| Chart patterns | Head & shoulders, double top/bottom | `stock.technicals.patterns()` |
| Volume profile | VWAP, POC | `stock.technicals.volume_profile()` |
| Multi-timeframe | Align daily/weekly/monthly | `stock.technicals.multi_timeframe_analysis()` |

#### Time Series Forecasting *(NEW)*

| Feature | Description | API |
|---------|-------------|-----|
| Prophet forecasting | Price forecasting with confidence intervals, seasonality | `stock.forecast(periods=30, method="prophet")` |
| Auto-ARIMA | Statistical forecasting (Box-Jenkins methodology) | `stock.forecast(periods=30, method="arima")` |
| Feature extraction | Auto-extract relevant features from price series (tsfresh) | `stock.timeseries.extract_features()` |
| Regime detection | Classify bull/bear/sideways market regimes | `stock.timeseries.regime()` |
| Forecast visualization | Plot forecast with confidence bands | `forecast.plot()` |

**Why:** Every investor asks "where is this stock going?" This provides data-driven answers with uncertainty quantification — not just point estimates.

#### Interactive Visualization *(NEW)*

> *Inspired by [D-Tale (Man Group)](https://github.com/man-group/dtale) and [mplfinance](https://github.com/matplotlib/mplfinance).*

| Feature | Description | API |
|---------|-------------|-----|
| Candlestick charts | Interactive OHLCV with overlaid indicators | `stock.chart(indicators=["sma_20","rsi"], interactive=True)` |
| Portfolio dashboard | Allocation pie, equity curve, drawdown chart | `portfolio.dashboard()` |
| Correlation heatmap | Annotated heatmap with significance | `correlation.heatmap(annotated=True)` |
| Backtest visualization | Trades on chart, equity curve, underwater plot | `backtest_result.plot()` |
| DataFrame explorer | One-line D-Tale style data explorer | `stock.explore()` |

### 4.3 Options Analytics & Multi-Asset *(EXPANDED)*

> *Inspired by [tf-quant-finance (Google)](https://github.com/google/tf-quant-finance), [FinancePy](https://github.com/domokane/FinancePy), and [ThetaGang](https://github.com/brndnmtthws/thetagang).*

#### Options Analytics *(NEW)*

| Feature | Description | API |
|---------|-------------|-----|
| Options chain | Full chain by expiry, with bid/ask/volume/OI | `stock.options.chain(expiry="2026-03-20")` |
| Black-Scholes pricing | Theoretical option pricing | `stock.options.price(strike=150, expiry=..., type="call")` |
| Greeks | Delta, Gamma, Theta, Vega, Rho | `option.greeks()` |
| Implied volatility | IV by strike, IV surface/smile | `stock.options.iv_surface()` |
| Strategy builder | Covered calls, iron condors, spreads, straddles | `stock.options.strategy("iron_condor", strikes=[...])` |
| Payoff diagram | Visualize P&L at expiry | `strategy.payoff_diagram()` |
| Max profit/loss | Risk metrics per strategy | `strategy.max_profit`, `strategy.max_loss`, `strategy.breakeven` |

**Why:** Options are massive for retail investors (ThetaGang, r/options). Google's tf-quant-finance shows institutional demand. This is a high-visibility, high-value feature.

#### Multi-Asset

| Feature | Description | Scope |
|---------|-------------|-------|
| Bond data | Treasury yields, corporate bonds | Via Alpha Vantage or FRED |
| ETF holdings | Constituents, weights | `etf.holdings()` |
| Commodities | Gold, oil, etc. | Extend Market class |
| Forex | Major pairs | Extend Market class |
| Crypto | BTC, ETH, etc. | Extend Market class |

### 4.4 News & Research Aggregation

| Feature | Description | API |
|---------|-------------|-----|
| News search | By ticker, date range, keywords | `stock.news.search(query="earnings", days=7)` |
| News sentiment timeline | Score over time | `stock.sentiment.timeline(days=30)` |
| SEC filing alerts | New filings | `stock.sec.watch(callback=...)` |
| Earnings calendar alerts | Upcoming earnings | `stock.earnings.watch(callback=...)` |

### 4.5 Alerts & Monitoring

| Feature | Description | API |
|---------|-------------|-----|
| Price alerts | Above/below threshold | `stock.alert.price(above=200, callback=...)` |
| Screen alerts | Stock enters/exits screen | `screener.alert.on_enter(screen, callback)` |
| Custom conditions | User-defined | `stock.alert.when(condition_func, callback)` |
| Webhook support | HTTP POST on trigger | For external integrations |

### 4.6 International Markets

| Market | Ticker Format | Data Source |
|--------|---------------|-------------|
| UK (LSE) | .L suffix | yfinance, Alpha Vantage |
| EU (XETRA, etc.) | .DE, .PA, etc. | yfinance, Alpha Vantage |
| Asia (HK, Japan) | .HK, .T | yfinance |
| India (NSE/BSE) | .NS, .BO | Already supported |

### 4.7 Data Quality & Validation

*Builds on Phase 1 (Data Correctness & Consistency) and Phase 2 (Backtest-safe data semantics).*

| Feature | Description |
|---------|-------------|
| Data freshness | Last update timestamp per field |
| Confidence scores | Reliability indicator for key metrics |
| Outlier detection | Flag suspicious values |
| NaN handling | Explicit handling and documentation (foundation in Phase 1.4) |
| Data lineage | Source and timestamp for each value; supports `debug=True` / `source_trace=True` |
| Restatements & point-in-time | Document and optionally enforce as-reported vs restated; latest vs point-in-time semantics (see Phase 2.1) |
| Survivorship bias | Document universe construction; options for including/excluding delisted names in screens and backtest exports |

### 4.8 Backtest Export & Minimal Engine *(Reframed)*

> *Community feedback: keep backtesting intentionally minimal; let users bring their own engine (vectorbt, zipline). Focus on making it dead simple to get clean feature matrices out.*

| Feature | Description | API |
|---------|-------------|-----|
| **Export for external engines** | Feature/signal DataFrames in formats ready for vectorbt, zipline, or Backtrader | `backtest.export_for_vectorbt(signals)` / `export_signals(format="zipline")` |
| **Minimal backtest runner** | Lightweight runner for sanity checks and strategy development; not a full vectorized framework | `backtest.run(strategy, engine="simple")` |
| Optional: vectorized path | If we add a faster path (NumPy/Numba), position it as "quick iteration" only; serious work stays in vectorbt/zipline | `backtest.run(strategy, engine="vectorized")` (optional, not a priority) |

**Why:** Competing with vectorbt or zipline is a different project. InvestorMate's edge is **correct, normalized data and feature matrices**; the moment we nail that plumbing, export to the user's chosen backtester is the right scope.

**Deliverables:** v1.1–v1.5 (incremental), v2.0 (major release)

---

## Phase 5: Platform & Ecosystem (v2.0+)

**Goal:** Turn InvestorMate into a platform others build on.

**Timeline:** Ongoing

### 5.1 REST API (Optional Package)

| Component | Description |
|-----------|-------------|
| FastAPI/Flask wrapper | `investormate-api` package |
| Authentication | API keys, OAuth |
| Rate limiting | Per-key quotas |
| WebSocket endpoint | For streaming |
| OpenAPI/Swagger | Auto-generated docs |

### 5.2 Plugin System

| Feature | Description |
|---------|-------------|
| Custom data providers | Register `DataProvider` implementations |
| Custom indicators | Register technical indicators |
| Custom screens | Register screening strategies |
| Custom strategies | Register backtest strategies |
| Hook system | Pre/post fetch, pre/post analysis |

### 5.3 Jupyter Integration

| Feature | Description |
|---------|-------------|
| IPython magics | `%investormate AAPL` |
| Interactive widgets | Dropdowns, date pickers |
| Progress bars | For long operations |
| Rich output | Tables, charts in notebook |
| Report export | One-click PDF from notebook |

### 5.4 Community & Ecosystem

| Initiative | Description |
|-----------|-------------|
| Strategy library | User-contributed backtest strategies (academic + custom) |
| Screen library | User-contributed screens |
| Data provider registry | Community providers |
| ML model registry | Shared alpha models and feature sets |
| Tutorials & courses | Official learning path |
| Discord/Slack | Community support |

### 5.5 Advanced Quant Features *(NEW — Future Exploration)*

> *Inspired by [HFTBacktest](https://github.com/nkaz001/hftbacktest), [nautilus_trader](https://github.com/nautechsystems/nautilus_trader), [Deepdow](https://github.com/jankrepl/deepdow), [Freqtrade](https://github.com/freqtrade/freqtrade), and [ccxt](https://github.com/ccxt/ccxt).*

| Feature | Description | Inspiration |
|---------|-------------|-------------|
| Deep learning portfolio optimization | Neural network-based weight allocation | Deepdow |
| Crypto exchange integration | 100+ exchanges via unified API | ccxt |
| Crypto-specific indicators | NVT ratio, MVRV, exchange flows | Freqtrade, Hummingbot |
| Order book visualization | Level 2 data, market depth | HFTBacktest |
| Transaction cost analysis | Slippage modeling, commission impact | nautilus_trader |
| Reinforcement learning trading | Agent-based position sizing | FinRL |

---

## Technical Specifications

### Dependency Strategy

**Core install stays minimal** — `pip install investormate` pulls only pandas, numpy, requests (and default data provider). The entire educational layer (TVM, bonds, CAPM, financial statement analysis, Black-Scholes) ships in core with **zero additional dependencies** — it's pure numpy/pandas math. Optional capabilities via extras: `investormate[ta]`, `investormate[ai]`, `investormate[optimization]`, etc., so users don't pull 50 deps for a few ratios.

| Category | Approach |
|----------|----------|
| Core | pandas, numpy, requests (minimal) |
| Academic (Phase 1.5) | **No extra deps** — TVM, bonds, CAPM, BS pricing, statement analysis all use numpy/pandas only |
| Data | yfinance (default), optional: alpha-vantage, polygon-api-client, fredapi, quandl |
| AI | Optional: openai, anthropic, google-genai |
| TA | Optional: pandas-ta |
| Optimization | Optional: scipy (MVO), scikit-learn (HRP) |
| ML | Optional: scikit-learn, xgboost, lightgbm |
| Forecasting | Optional: prophet, pmdarima, tsfresh |
| Options (advanced) | Optional: scipy (advanced Greeks), mibian |
| Visualization | Optional: plotly, mplfinance |
| Metrics | Optional: quantstats (or native implementation) |
| Export | Optional: weasyprint (PDF), openpyxl (Excel) |

### Python Version Support

- v0.3–0.7: Python 3.9+
- v1.0+: Python 3.10+ (for modern type hints)
- Drop 3.9 only when necessary

### Performance Targets

| Operation | Target |
|-----------|--------|
| TVM calculation (any) | < 5ms |
| Bond pricing + duration + convexity | < 10ms |
| Amortization schedule (360 periods) | < 20ms |
| Common-size / horizontal analysis | < 100ms (after data cached) |
| Black-Scholes + all Greeks | < 5ms |
| Binomial tree (100 steps) | < 50ms |
| CAPM regression (5yr daily) | < 200ms |
| Single stock quote | < 500ms (cached < 50ms) |
| Batch 10 stocks | < 2s |
| Full report generation | < 30s |
| Backtest 1yr daily (event-driven) | < 5s |
| Backtest 1yr daily (vectorized) | < 0.5s |
| Parameter optimization (100 combos) | < 30s |
| Portfolio optimization (50 assets) | < 2s |
| Correlation matrix (20 stocks) | < 2s |
| Tearsheet generation | < 10s |
| Prophet forecast (30 days) | < 15s |

### Testing Requirements

- Unit test coverage: > 85%
- Integration tests: Mock network by default; optional live tests
- Property-based tests: For ratios, validation, parsers
- Strategy tests: Each academic strategy vs. published Sharpe/returns
- Performance benchmarks: Track regression

---

## Success Metrics

| Metric | v0.4 Target | v1.0 Target | v2.0 Target |
|--------|-------------|-------------|------------|
| PyPI monthly downloads | 2K+ | 10K+ | 50K+ |
| GitHub stars | 100+ | 500+ | 2K+ |
| Active contributors | 3+ | 5+ | 15+ |
| Documentation completeness | 80% | 90% | 95% |
| Test coverage | 85% | 85% | 90% |
| Built-in strategies | 4+ | 15+ | 30+ |
| CFA L1 topic coverage | 80%+ | 90%+ | 95%+ |
| Time to first insight | < 5 min | < 5 min | < 2 min |
| University syllabi adoption | 1+ | 5+ | 20+ |
| "Can do my homework with it" | Yes | Yes | Yes |
| "Can replace my workflow" | — | Yes for individuals | Yes for small teams |

---

## Appendix: Bloomberg Terminal + Quant Platform + Education Feature Mapping

| Capability | InvestorMate Equivalent | Phase |
|------------|-------------------------|-------|
| **AI ENGINE** | | |
| AI Q&A about any stock | investor.ask("AAPL", "Is this undervalued?") | Done |
| AI document analysis | investor.analyze_document(ticker, url, question) | Done |
| AI stock comparison | investor.compare(["AAPL","MSFT"], question) | Done |
| AI sentiment analysis | stock.sentiment (news sentiment via LLM) | Done |
| AI summary generation | Structured stock overviews via LLM | Done |
| Multi-provider LLM | OpenAI, Claude, Gemini — user picks | Done |
| AI financial tutor | investor.ask_concept(), AI ratio commentary | 1.5 |
| AI practice feedback | investor.review_analysis() | 1.5 |
| AI filing summarization | investor.summarize_filing() (10-K/10-Q via SEC Edgar) | 2.3 |
| AI research reports | investor.generate_report("AAPL", format="pdf") | 3.4 |
| **EDUCATIONAL** | | |
| TVM calculator | tvm.present_value, future_value, annuity, irr, npv | 1.5 |
| Financial statement analysis | stock.financials.common_size, horizontal, vertical, trend | 1.5 |
| Bond pricing & analytics | bond.price, duration, convexity, ytm | 1.5 |
| CAPM & factor models | stock.capm, factor_model, jensen_alpha | 1.5 |
| Options basics (B-S, Greeks) | options.black_scholes, greeks, binomial | 1.5 |
| Formula explanations | stock.ratios.explain(), show_work() | 1.5 |
| CFA/FRM topic mapping | cfa_topic(), frm_topic() on all metrics | 1.5 |
| Ratio interpretation | stock.ratios.interpret(), red_flags(), percentile() | 1.5 |
| Practice problems | practice.generate("tvm", difficulty="medium") | 1.5 |
| Coursework export | stock.to_excel(), stock.report(format="markdown") | 1.5 |
| **PROFESSIONAL** | | |
| Real-time quotes | Delayed (free) / WebSocket (paid) | 4.1 |
| Historical OHLCV | Stock.history() | Done |
| Financial statements | Stock.balance_sheet, etc. | Done |
| Ratios & metrics | Stock.ratios (40+) | Done |
| Technical indicators | Stock.indicators (60+) | Done |
| Valuation (DCF/Comps) | stock.valuation | Done |
| SEC filings | stock.sec (Edgar) | 2.3 |
| Earnings transcripts | stock.earnings.transcript | 2.4 |
| Macro/economic data | market.macro (FRED) | 2.6 |
| Portfolio optimization | portfolio.optimize (HRP, MVO, BL) | 3.1 |
| Performance tearsheets | portfolio.tearsheet, backtest.tearsheet | 3.1 |
| Peer comparison | investor.compare_peers | 3.3 |
| Screening | Screener + institutional screens | 3.2 |
| Portfolio analytics | Portfolio + risk module | 3.1 |
| News & sentiment | Stock.sentiment | Done |
| AI summarization | Investor.ask, generate_report | 3.4 |
| Academic strategies | 10+ research-backed strategies | 3.5 |
| ML alpha signals | AlphaModel, factor framework | 3.6 |
| Backtesting | Backtest (event-driven + vectorized) | Done + 4.8 |
| Correlation | Correlation class | Done |
| Options analytics (advanced) | stock.options (chains, IV surface, strategy builder) | 4.3 |
| Time series forecasting | stock.forecast (Prophet, ARIMA) | 4.2 |
| Interactive charts | stock.chart, portfolio.dashboard | 4.2 |
| Alerts | stock.alert | 4.5 |
| Report generation | investor.generate_report | 3.4 |
| Multi-asset | Market, ETF, bonds, options | 4.3 |
| International | Ticker formatting | 4.6 |
| Vectorized backtesting | backtest.run(engine="vectorized") | 4.8 |
| Deep learning portfolio | Neural network allocation | 5.5 |
| Crypto exchanges | ccxt integration (100+ exchanges) | 5.5 |

---

## Appendix: Key Open-Source Inspirations

> These are the projects whose best ideas InvestorMate aims to absorb into a single, unified package.

**Professional / Quant Ecosystem:**

| Project | Stars | What We Take From It |
|---------|-------|---------------------|
| [OpenBB Terminal](https://github.com/OpenBB-finance/OpenBBTerminal) | 65k+ | Multi-source data aggregation, macro data, alternative data |
| [QLib (Microsoft)](https://github.com/microsoft/qlib) | 15k+ | ML alpha framework, factor models, feature engineering |
| [vectorbt](https://github.com/polakowo/vectorbt) | 4k+ | Vectorized backtesting, parameter optimization, speed |
| [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt) | 4k+ | Efficient frontier, HRP, Black-Litterman, portfolio optimization |
| [FinanceToolkit](https://github.com/JerBouma/FinanceToolkit) | 4.5k+ | 150+ ratios, transparent calculations, multi-asset coverage |
| [quantstats](https://github.com/ranaroussi/quantstats) | 3k+ | 30+ performance metrics, tearsheet generation |
| [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib) | 3k+ | Advanced portfolio optimization, risk parity |
| [pyfolio](https://github.com/quantopian/pyfolio) | 5k+ | Portfolio risk analytics, drawdown analysis |
| [FinRL](https://github.com/AI4Finance-Foundation/FinRL) | 9k+ | Reinforcement learning for trading |
| [Prophet](https://github.com/facebook/prophet) | 18k+ | Time series forecasting with seasonality |
| [tf-quant-finance](https://github.com/google/tf-quant-finance) | 4k+ | Options pricing, derivatives analytics |
| [mplfinance](https://github.com/matplotlib/mplfinance) | 3k+ | Financial charting, candlestick plots |
| [D-Tale](https://github.com/man-group/dtale) | 4k+ | Interactive DataFrame exploration |
| [paperswithbacktest](https://github.com/paperswithbacktest/awesome-systematic-trading) | 7k+ | 40+ academic strategies with Sharpe ratios |

**Educational Ecosystem:**

| Project / Resource | Type | What We Take From It |
|-------------------|------|---------------------|
| [Tidy Finance with Python](https://www.tidy-finance.org/python/) | Book + Package | Transparent, reproducible code for finance education; financial statement analysis patterns |
| [FinancePy](https://github.com/domokane/FinancePy) | Library | Fixed income pricing, derivatives valuation, 90+ example notebooks |
| [Rateslib](https://rateslib.com/) | Library | Bond pricing, yield curve construction, fixed income risk metrics |
| [ratecurves](https://pypi.org/project/ratecurves/) | Library | Lightweight yield curve bootstrapping, Nelson-Siegel models, FRED integration |
| CFA Institute Curriculum | Syllabus | 10-topic L1 structure, topic weights, learning outcomes for feature mapping |
| FRM (GARP) Curriculum | Syllabus | Risk management focus areas, quantitative analysis requirements |
| [Strategic Alpha](https://strategicalpha.app/) | Web App | Educational DCF tool, ML forecasting demo, risk metrics for learning |
| DataCamp Financial Analysis | Course | Ratio computation patterns, financial health assessment workflows |

---

*Last updated: April 2026*

*This roadmap is a living document. Priorities may shift based on community feedback and resource availability.*

*The April 2026 update introduced the **"Full Stack" Strategy** — recognizing that InvestorMate's unique moat is **Finance + AI + Education** in a single library. The three pillars were articulated: AI engine (multi-provider LLM powering Q&A, sentiment, summaries, tutoring, and reports across every module), educational foundation (TVM, bonds, CAPM, statement analysis, `explain()`, `show_work()`), and professional toolkit (the existing roadmap from DCF through ML alpha). Phase 1.5 (Academic & Educational Foundation) was added with both deterministic and AI-powered educational features. AI integration points were mapped across all phases. CFA L1-L3 and FRM curriculum coverage maps were added to guide feature prioritization.*

*The Feb 2026 update incorporated systematic-trading community feedback: data correctness and consistency as Phase 1 foundation, modular installs and backtest-safe data semantics in Phase 2, debug/source-trace for transparency, backtesting scoped to feature export + minimal engine (not a full vectorbt/zipline competitor), and explicit restatements / point-in-time / survivorship bias in data quality.*
