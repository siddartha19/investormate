"""
InvestorMate command-line interface.

Keyless terminal utility for stock quotes and fundamental snapshots.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional, Sequence

from .analysis.ratios import RatiosCalculator
from .core.stock import Stock
from .data.parsers import extract_price_data
from .utils.exceptions import DataFetchError, InvalidTickerError, InvestorMateError
from .utils.formatters import (
    format_currency,
    format_large_number,
    format_number,
    format_percentage,
)
from .utils.validators import validate_ticker
from .version import __version__

EXIT_OK = 0
EXIT_DATA = 1
EXIT_USAGE = 2

_DISCLAIMER = (
    "Educational/research use only. Not financial advice. "
    "Always verify data before making investment decisions."
)

_WELCOME = """\
InvestorMate {version} — keyless stock analysis in your terminal

Usage:
  investormate quote TICKER      Current price and market snapshot
  investormate analyze TICKER    Fundamentals + key ratios
  investormate --help            Full help

Examples:
  investormate quote AAPL
  investormate analyze MSFT --json

Python API:
  from investormate import Stock
  print(Stock("AAPL").price)

{_disclaimer}
""".format(
    version=__version__, _disclaimer=_DISCLAIMER
)


def _change_fields(
    price: Optional[float], previous_close: Optional[float]
) -> Dict[str, Optional[float]]:
    if price is None or previous_close is None:
        return {"change": None, "change_pct": None}
    change = price - previous_close
    change_pct = None
    if previous_close != 0:
        change_pct = change / previous_close
    return {"change": change, "change_pct": change_pct}


def _build_quote_payload(stock: Stock) -> Dict[str, Any]:
    """Assemble a JSON-serializable quote snapshot from Stock public data."""
    price_data = extract_price_data(stock.info)
    price = price_data.get("current_price")
    previous_close = price_data.get("previous_close")
    changes = _change_fields(price, previous_close)
    return {
        "ticker": stock.ticker,
        "name": stock.name,
        "price": price,
        "previous_close": previous_close,
        "change": changes["change"],
        "change_pct": changes["change_pct"],
        "day_high": price_data.get("day_high"),
        "day_low": price_data.get("day_low"),
        "volume": price_data.get("volume"),
        "market_cap": price_data.get("market_cap"),
    }


def _build_analyze_payload(stock: Stock) -> Dict[str, Any]:
    """
    Fundamentals snapshot using quote + info-only ratios.

    Uses ``RatiosCalculator(stock.info)`` so we do not fetch financial
    statements for the default analyze path (keeps the command fast).
    """
    payload = _build_quote_payload(stock)
    ratios = RatiosCalculator(stock.info)
    payload.update(
        {
            "sector": stock.sector,
            "industry": stock.industry,
            "pe": ratios.pe,
            "pb": ratios.pb,
            "ps": ratios.ps,
            "roe": ratios.roe,
            "roa": ratios.roa,
            "debt_to_equity": ratios.debt_to_equity,
            "profit_margin": ratios.profit_margin,
            "current_ratio": ratios.current_ratio,
            "dividend_yield": ratios.dividend_yield,
        }
    )
    return payload


def _fmt_change(change: Optional[float], change_pct: Optional[float]) -> str:
    if change is None:
        return "N/A"
    sign = "+" if change >= 0 else ""
    pct = format_percentage(change_pct) if change_pct is not None else "N/A"
    return f"{sign}{format_currency(change)} ({sign}{pct})" if change_pct is not None else (
        f"{sign}{format_currency(change)}"
    )


def _print_quote_human(payload: Dict[str, Any]) -> None:
    ticker = payload["ticker"]
    name = payload.get("name") or ticker
    print(f"{ticker} — {name}")
    print(f"  Price:          {format_currency(payload.get('price'))}")
    print(f"  Previous close: {format_currency(payload.get('previous_close'))}")
    print(
        f"  Change:         {_fmt_change(payload.get('change'), payload.get('change_pct'))}"
    )
    day_low = format_currency(payload.get("day_low"))
    day_high = format_currency(payload.get("day_high"))
    print(f"  Day range:      {day_low} – {day_high}")
    volume = payload.get("volume")
    print(
        f"  Volume:         {format_large_number(volume) if volume is not None else 'N/A'}"
    )
    print(f"  Market cap:     {format_large_number(payload.get('market_cap'))}")


def _print_analyze_human(payload: Dict[str, Any]) -> None:
    _print_quote_human(payload)
    print()
    print("Company")
    print(f"  Sector:         {payload.get('sector') or 'N/A'}")
    print(f"  Industry:       {payload.get('industry') or 'N/A'}")
    print()
    print("Key ratios")
    print(f"  P/E:            {format_number(payload.get('pe'))}")
    print(f"  P/B:            {format_number(payload.get('pb'))}")
    print(f"  P/S:            {format_number(payload.get('ps'))}")
    print(f"  ROE:            {format_percentage(payload.get('roe'))}")
    print(f"  ROA:            {format_percentage(payload.get('roa'))}")
    print(f"  Debt/Equity:    {format_number(payload.get('debt_to_equity'))}")
    print(f"  Profit margin:  {format_percentage(payload.get('profit_margin'))}")
    print(f"  Current ratio:  {format_number(payload.get('current_ratio'))}")
    print(f"  Dividend yield: {format_percentage(payload.get('dividend_yield'))}")
    print()
    print(f"Note: {_DISCLAIMER}")


def _emit_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, default=str))


def _error(message: str, cause: str, fix: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    print(f"Cause: {cause}", file=sys.stderr)
    print(f"Fix:   {fix}", file=sys.stderr)


def _run_quote(ticker: str, as_json: bool) -> int:
    stock = Stock(ticker)
    # Touch info once so DataFetchError surfaces before formatting.
    _ = stock.info
    payload = _build_quote_payload(stock)
    if as_json:
        _emit_json(payload)
    else:
        _print_quote_human(payload)
    return EXIT_OK


def _run_analyze(ticker: str, as_json: bool) -> int:
    stock = Stock(ticker)
    _ = stock.info
    payload = _build_analyze_payload(stock)
    if as_json:
        _emit_json(payload)
    else:
        _print_analyze_human(payload)
    return EXIT_OK


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="investormate",
        description=(
            "InvestorMate CLI — keyless stock quotes and fundamental snapshots. "
            f"{_DISCLAIMER}"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  investormate quote AAPL\n"
            "  investormate analyze MSFT --json\n"
            "  python -m investormate quote AAPL\n"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    quote_parser = subparsers.add_parser(
        "quote",
        help="Show current price and market snapshot for a ticker",
    )
    quote_parser.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    quote_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a single JSON object on stdout",
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Show fundamentals and key ratios for a ticker",
    )
    analyze_parser.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a single JSON object on stdout",
    )

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    CLI entry point.

    Args:
        argv: Optional argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code (0 success, 2 usage/input, 1 data/provider failure).
    """
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.command:
        print(_WELCOME, end="")
        return EXIT_OK

    try:
        ticker = validate_ticker(args.ticker)
    except InvalidTickerError as exc:
        _error(
            str(exc),
            "The ticker argument failed validation.",
            "Pass a symbol like AAPL, MSFT, or RELIANCE.NS (1–10 allowed chars).",
        )
        return EXIT_USAGE

    as_json = bool(getattr(args, "json", False))

    try:
        if args.command == "quote":
            return _run_quote(ticker, as_json)
        if args.command == "analyze":
            return _run_analyze(ticker, as_json)
        parser.error(f"Unknown command: {args.command}")
        return EXIT_USAGE
    except InvalidTickerError as exc:
        _error(
            str(exc),
            "The ticker argument failed validation.",
            "Pass a symbol like AAPL, MSFT, or RELIANCE.NS.",
        )
        return EXIT_USAGE
    except DataFetchError as exc:
        _error(
            str(exc),
            "The data provider could not return market data for this ticker.",
            "Check your network connection and ticker spelling, then retry.",
        )
        return EXIT_DATA
    except InvestorMateError as exc:
        _error(
            str(exc),
            "InvestorMate rejected this request.",
            "See the message above and retry with a valid ticker.",
        )
        return EXIT_DATA
    except Exception as exc:  # noqa: BLE001 — CLI must never dump a traceback by default
        _error(
            f"Unexpected failure: {exc}",
            "An internal error occurred while fetching or formatting data.",
            "Retry later. If it persists, open an issue with the ticker and command.",
        )
        return EXIT_DATA


if __name__ == "__main__":
    sys.exit(main())
