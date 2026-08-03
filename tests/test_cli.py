"""Isolated tests for the InvestorMate CLI (no live network)."""

from __future__ import annotations

import json
import runpy
import sys
from typing import Any, Dict, Optional

import pandas as pd
import pytest

from investormate import DataProvider, set_data_provider
from investormate.cli import EXIT_DATA, EXIT_OK, EXIT_USAGE, main
from investormate.data.cache import get_data_cache
from investormate.utils.exceptions import DataFetchError
from investormate.version import __version__


class CLIFakeProvider(DataProvider):
    """In-memory provider for CLI tests."""

    def __init__(self, info: Optional[Dict[str, Any]] = None, fail: bool = False):
        self.info = info or {}
        self.fail = fail
        self.calls = []

    def get_info(self, ticker):
        self.calls.append(("get_info", ticker))
        if self.fail:
            raise RuntimeError("network down")
        payload = dict(self.info)
        payload.setdefault("symbol", ticker)
        return payload

    def get_balance_sheet(self, ticker):
        return {}

    def get_income_statement(self, ticker):
        return {}

    def get_cash_flow(self, ticker):
        return {}

    def get_calendar(self, ticker):
        return {}

    def get_earnings_estimate(self, ticker):
        return None

    def get_earnings_history(self, ticker):
        return None

    def get_revenue_estimate(self, ticker):
        return None

    def get_eps_trend(self, ticker):
        return None

    def get_eps_revisions(self, ticker):
        return None

    def get_growth_estimates(self, ticker):
        return None

    def get_history(
        self, ticker, period="1y", interval="1d", auto_adjust=True, return_trace=False
    ):
        data = {
            "2024-01-02": {"Open": 1, "High": 2, "Low": 1, "Close": 1.5, "Volume": 10}
        }
        if return_trace:
            return data, {"provider": "fake", "raw_shape": (1, 5)}
        return data

    def get_dividends(self, ticker):
        return pd.Series(dtype=float)

    def get_news(self, ticker):
        return []

    def get_filings(self, ticker):
        return []

    def get_market_summary(self, market):
        return {"market": market}


@pytest.fixture(autouse=True)
def _isolate_provider():
    from investormate import reset_data_provider

    reset_data_provider()
    get_data_cache().clear()
    yield
    reset_data_provider()
    get_data_cache().clear()


@pytest.fixture
def rich_info(sample_stock_info):
    """Extend the shared fixture with fields the CLI quote/analyze paths need."""
    info = dict(sample_stock_info)
    info.update(
        {
            "previousClose": 148.0,
            "dayHigh": 152.0,
            "dayLow": 147.5,
            "volume": 55_000_000,
            "industry": "Consumer Electronics",
            "returnOnAssets": 0.20,
            "profitMargins": 0.25,
            "priceToSalesTrailing12Months": 7.5,
            "currentRatio": 1.1,
            "dividendYield": 0.005,
        }
    )
    return info


def test_bare_invocation_prints_welcome(capsys):
    code = main([])
    out = capsys.readouterr().out
    assert code == EXIT_OK
    assert "InvestorMate" in out
    assert "quote TICKER" in out
    assert "analyze TICKER" in out
    assert "Educational/research" in out


def test_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "quote" in out
    assert "analyze" in out


def test_version_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert __version__ in out
    assert "0.6.0" in out


def test_quote_human_output(capsys, rich_info):
    set_data_provider(CLIFakeProvider(rich_info))
    code = main(["quote", "aapl"])
    captured = capsys.readouterr()
    assert code == EXIT_OK
    assert "AAPL" in captured.out
    assert "Apple Inc." in captured.out
    assert "$150.00" in captured.out
    assert captured.err == ""


def test_quote_json_output(capsys, rich_info):
    set_data_provider(CLIFakeProvider(rich_info))
    code = main(["quote", "AAPL", "--json"])
    captured = capsys.readouterr()
    assert code == EXIT_OK
    assert captured.err == ""
    payload = json.loads(captured.out)
    assert payload["ticker"] == "AAPL"
    assert payload["name"] == "Apple Inc."
    assert payload["price"] == 150.0
    assert payload["previous_close"] == 148.0
    assert payload["change"] == pytest.approx(2.0)
    assert payload["change_pct"] == pytest.approx(2.0 / 148.0)
    assert payload["day_high"] == 152.0
    assert payload["day_low"] == 147.5
    assert payload["volume"] == 55_000_000
    assert payload["market_cap"] == 2_500_000_000_000
    assert "Educational" not in captured.out


def test_analyze_human_includes_disclaimer(capsys, rich_info):
    set_data_provider(CLIFakeProvider(rich_info))
    code = main(["analyze", "AAPL"])
    captured = capsys.readouterr()
    assert code == EXIT_OK
    assert "Key ratios" in captured.out
    assert "P/E" in captured.out
    assert "Technology" in captured.out
    assert "Educational/research" in captured.out


def test_analyze_json_stable_keys(capsys, rich_info):
    set_data_provider(CLIFakeProvider(rich_info))
    code = main(["analyze", "AAPL", "--json"])
    captured = capsys.readouterr()
    assert code == EXIT_OK
    payload = json.loads(captured.out)
    for key in (
        "ticker",
        "name",
        "sector",
        "industry",
        "price",
        "pe",
        "pb",
        "roe",
        "debt_to_equity",
        "ps",
        "profit_margin",
        "current_ratio",
        "dividend_yield",
    ):
        assert key in payload
    assert payload["pe"] == 25.0
    assert payload["roe"] == 0.45
    assert "Educational" not in captured.out


def test_quote_missing_fields_render_na(capsys):
    set_data_provider(
        CLIFakeProvider({"symbol": "ZZZ", "shortName": "Sparse Co"})
    )
    code = main(["quote", "ZZZ"])
    captured = capsys.readouterr()
    assert code == EXIT_OK
    assert "N/A" in captured.out
    assert "Sparse Co" in captured.out


def test_invalid_ticker_exit_usage(capsys):
    code = main(["quote", "BAD TICKER!!"])
    captured = capsys.readouterr()
    assert code == EXIT_USAGE
    assert "Error:" in captured.err
    assert "Cause:" in captured.err
    assert "Fix:" in captured.err
    assert captured.out == ""


def test_empty_ticker_exit_usage(capsys):
    code = main(["quote", "   "])
    captured = capsys.readouterr()
    assert code == EXIT_USAGE
    assert "Error:" in captured.err


def test_provider_failure_exit_data(capsys):
    set_data_provider(CLIFakeProvider(fail=True))
    code = main(["quote", "AAPL"])
    captured = capsys.readouterr()
    assert code == EXIT_DATA
    assert "Error:" in captured.err
    assert "network" in captured.err.lower() or "Failed" in captured.err
    assert "Fix:" in captured.err
    assert captured.out == ""


def test_data_fetch_error_message(capsys):
    class BoomProvider(CLIFakeProvider):
        def get_info(self, ticker):
            raise DataFetchError("Failed to fetch stock info: timeout")

    set_data_provider(BoomProvider())
    code = main(["analyze", "AAPL", "--json"])
    captured = capsys.readouterr()
    assert code == EXIT_DATA
    assert "timeout" in captured.err or "Failed to fetch" in captured.err
    # JSON path must not leak decorative text onto stdout on failure
    assert captured.out == ""


def test_lowercase_ticker_normalized(capsys, rich_info):
    provider = CLIFakeProvider(rich_info)
    set_data_provider(provider)
    code = main(["quote", "msft", "--json"])
    assert code == EXIT_OK
    payload = json.loads(capsys.readouterr().out)
    assert payload["ticker"] == "MSFT"
    assert ("get_info", "MSFT") in provider.calls


def test_module_entry_point(capsys, rich_info, monkeypatch):
    set_data_provider(CLIFakeProvider(rich_info))
    monkeypatch.setattr(sys, "argv", ["investormate", "quote", "AAPL", "--json"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("investormate", run_name="__main__")
    assert exc.value.code == EXIT_OK
    payload = json.loads(capsys.readouterr().out)
    assert payload["ticker"] == "AAPL"


def test_library_exceptions_unchanged():
    """CLI error wrapping must not alter Stock exception types for library users."""
    from investormate import Stock
    from investormate.utils.exceptions import InvalidTickerError

    with pytest.raises(InvalidTickerError):
        Stock("BAD!!")

    set_data_provider(CLIFakeProvider(fail=True))
    stock = Stock("AAPL")
    with pytest.raises(DataFetchError):
        _ = stock.info
