# Contributing to InvestorMate

Thank you for your interest in contributing to InvestorMate! This document will help you get started with your first contribution.

## 📚 Start Here

Before diving in, we recommend reading:

1. **[ROADMAP.md](ROADMAP.md)** — Our vision, planned features, and current priorities. Great for finding impactful work!
2. **This file** — Development setup, workflow, and PR guidelines.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Finding Work](#finding-work)
5. [Your First PR](#your-first-pr)
6. [Code Style](#code-style)
7. [Testing](#testing)
8. [Documentation](#documentation)
9. [PR Process](#pr-process)

---

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Git**
- A **GitHub account**

### Quick Links

| Resource | Link |
|----------|------|
| Roadmap | [ROADMAP.md](ROADMAP.md) |
| Issues | [GitHub Issues](https://github.com/siddartha19/investormate/issues) |
| Discussions | [GitHub Discussions](https://github.com/siddartha19/investormate/discussions) |

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/investormate.git
cd investormate
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install in Editable Mode with Dev Dependencies

```bash
pip install -e ".[all,dev]"
```

This installs:
- Core package (editable)
- AI providers (openai, anthropic, google-genai)
- Technical analysis (pandas-ta)
- Dev tools (pytest, pytest-cov, black, flake8, build)

### 4. Verify Setup

```bash
# Run tests (without coverage if pytest-cov not installed)
python -m pytest tests/ -v -o addopts=""

# Or with coverage
python -m pytest tests/ -v --cov=investormate --cov-report=term-missing
```

---

## Project Structure

```
investormate/
├── investormate/           # Main package
│   ├── ai/                 # AI providers (OpenAI, Claude, Gemini)
│   ├── analysis/           # Correlation, indicators, ratios, sentiment, scores
│   ├── backtest/           # Backtesting engine
│   ├── core/               # Stock, Portfolio, Screener, Investor, Market
│   ├── data/               # Fetchers, parsers, constants, earnings
│   ├── documents/         # Document extraction and processing
│   └── utils/              # Exceptions, formatters, helpers, validators
├── docs/                   # Documentation
├── examples/               # Example scripts
├── tests/                  # Test suite
├── ROADMAP.md              # Product roadmap
├── CONTRIBUTING.md         # This file
└── README.md
```

---

## Finding Work

### Good First Issues

Look for issues labeled:
- `good first issue`
- `help wanted`
- `documentation`

### Roadmap-Driven Contributions

The [ROADMAP.md](ROADMAP.md) is the best source for high-impact work:

| Phase | Good for New Contributors |
|-------|---------------------------|
| **Phase 1** | Robustness fixes, validation, tests for edge cases |
| **Phase 2** | Data layer abstractions, caching, SEC Edgar integration |
| **Phase 3** | Valuation module, risk metrics, institutional screens |
| **Phase 4+** | Advanced features, plugins, integrations |

### Suggest New Work

If you have an idea:
1. Check [ROADMAP.md](ROADMAP.md) to see if it's already planned
2. Open a [GitHub Discussion](https://github.com/siddartha19/investormate/discussions) to propose it
3. Or open an issue with the `enhancement` label

---

## Your First PR

### Step-by-Step

1. **Pick an issue** (or create one after discussing)
2. **Comment** on the issue to claim it
3. **Create a branch**: `git checkout -b fix/your-feature-name`
4. **Make changes** — keep them focused and small
5. **Add tests** for new behavior
6. **Run tests**: `python -m pytest tests/ -v`
7. **Format code**: `black investormate tests`
8. **Lint**: `flake8 investormate tests`
9. **Commit** with a clear message: `git commit -m "Add X for Y"`
10. **Push** and open a PR: `git push origin fix/your-feature-name`

### Branch Naming

- `fix/` — Bug fixes
- `feat/` — New features
- `docs/` — Documentation only
- `refactor/` — Code refactoring
- `test/` — Test additions or fixes

### Commit Messages

```
Add null safety to data fetchers

- Handle None/empty from yfinance in get_yfinance_data
- Handle None/empty in balance_sheet, income_stmt, cash_flow
- Raise DataFetchError with clear message
```

---

## Code Style

### Formatting

We use **Black** for formatting:

```bash
black investormate tests
```

### Linting

We use **Flake8** for linting:

```bash
flake8 investormate tests
```

### Style Guidelines

- **Type hints** — Use for public APIs and new code
- **Docstrings** — Google style: `Args:`, `Returns:`, `Raises:`
- **Imports** — Group: stdlib, third-party, local. Sort alphabetically.
- **Line length** — 88 chars (Black default)

### Example

```python
def get_stock_price(ticker: str) -> Optional[float]:
    """
    Get current stock price.
    
    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        
    Returns:
        Current price or None if unavailable
        
    Raises:
        InvalidTickerError: If ticker is invalid
    """
    ...
```

---

## Testing

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Specific Tests

```bash
python -m pytest tests/test_validators.py -v
python -m pytest tests/test_correlation.py::TestCorrelation::test_matrix_pearson -v
```

### Run with Coverage

```bash
pip install pytest-cov
python -m pytest tests/ --cov=investormate --cov-report=term-missing
```

### Writing Tests

- **Unit tests** — Mock network calls; use `unittest.mock.patch`
- **Integration tests** — Can hit network for real data; mark with `@pytest.mark.integration` if needed
- **Fixtures** — Use `conftest.py` for shared fixtures
- **Naming** — `test_<function>_<scenario>_<expected>`

### Example Test

```python
def test_validate_ticker_valid():
    """Valid ticker returns uppercase."""
    assert validate_ticker("aapl") == "AAPL"

def test_validate_ticker_invalid_empty():
    """Empty ticker raises InvalidTickerError."""
    with pytest.raises(InvalidTickerError, match="non-empty"):
        validate_ticker("")
```

---

## Documentation

### Docstrings

All public functions, classes, and modules should have docstrings:

```python
def my_function(param: str) -> bool:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        param: Description of param
        
    Returns:
        Description of return value
        
    Raises:
        SomeError: When X happens
    """
```

### Docs Folder

- Update `docs/` when adding new features
- Add examples to `examples/` for significant features
- Update `README.md` if user-facing behavior changes

---

## PR Process

### Before Submitting

- [ ] Tests pass: `python -m pytest tests/ -v`
- [ ] Code formatted: `black investormate tests`
- [ ] Linting passes: `flake8 investormate tests`
- [ ] CHANGELOG.md updated (for user-facing changes)

### PR Template

When opening a PR, include:

1. **Description** — What does this PR do?
2. **Related Issue** — Link to issue (e.g., `Closes #123`)
3. **Testing** — How did you test?
4. **Checklist** — Confirm items above

### Review Process

- Maintainers will review within a few days
- Address feedback by pushing new commits (no need to close/reopen)
- Once approved, a maintainer will merge

### After Merge

- Your contribution will appear in the next release
- You'll be credited in the release notes
- Thank you! 🎉

---

## Questions?

- **Bug reports** — [Open an issue](https://github.com/siddartha19/investormate/issues)
- **Feature ideas** — [Start a discussion](https://github.com/siddartha19/investormate/discussions)
- **General help** — Check [ROADMAP.md](ROADMAP.md) and [docs/](docs/)

---

Thank you for contributing to InvestorMate! Every PR, no matter how small, helps make this package better for everyone.
