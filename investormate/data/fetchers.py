"""
Data fetching utilities for InvestorMate.
Wrappers around yfinance for JSON-serializable stock data.
"""

from typing import Dict, Optional, Tuple, Union

import pandas as pd
import yfinance as yf

from .cache import (
    TTL_EARNINGS,
    TTL_FILINGS,
    TTL_FINANCIALS,
    TTL_HISTORY,
    TTL_INFO,
    TTL_MARKET,
    TTL_NEWS,
    cached_yfinance_call,
)
from .constants import get_ticker_format, get_ticker_country


def get_yfinance_data(ticker_name: str) -> Dict:
    """
    Get basic stock information.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with stock info (JSON-serializable). Empty dict if no data.
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:info"

    def _fetch() -> Dict:
        ticker = yf.Ticker(fmt)
        info = ticker.info
        if info is None or not isinstance(info, dict):
            return {}
        result = dict(info)
        for k, value in result.items():
            if isinstance(value, pd.Timestamp):
                result[k] = value.strftime("%Y-%m-%d %H:%M:%S")
        return result

    return cached_yfinance_call(key, TTL_INFO, _fetch)


def get_yfinance_balance_sheet_data(ticker_name: str) -> Dict:
    """
    Get balance sheet data.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with balance sheet data (JSON-serializable). Empty dict if no data.
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:balance_sheet"

    def _fetch() -> Dict:
        ticker = yf.Ticker(fmt)
        df = ticker.balance_sheet
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return {}
        result = {}
        for col in df.columns:
            if isinstance(col, pd.Timestamp):
                col_str = col.strftime("%Y-%m-%d")
            else:
                col_str = str(col)
            result[col_str] = {
                str(idx): float(val) if pd.notnull(val) else None
                for idx, val in df[col].items()
            }
        return result

    return cached_yfinance_call(key, TTL_FINANCIALS, _fetch)


def get_yfinance_income_statement_data(ticker_name: str) -> Dict:
    """
    Get income statement data.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with income statement data (JSON-serializable). Empty dict if no data.
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:income_statement"

    def _fetch() -> Dict:
        ticker = yf.Ticker(fmt)
        df = ticker.incomestmt
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return {}
        result = {}
        for col in df.columns:
            if isinstance(col, pd.Timestamp):
                col_str = col.strftime("%Y-%m-%d")
            else:
                col_str = str(col)
            result[col_str] = {
                str(idx): float(val) if pd.notnull(val) else None
                for idx, val in df[col].items()
            }
        return result

    return cached_yfinance_call(key, TTL_FINANCIALS, _fetch)


def get_yfinance_cash_flow_statement_data(ticker_name: str) -> Dict:
    """
    Get cash flow statement data.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with cash flow data (JSON-serializable). Empty dict if no data.
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:cash_flow"

    def _fetch() -> Dict:
        ticker = yf.Ticker(fmt)
        df = ticker.cash_flow
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return {}
        result = {}
        for col in df.columns:
            if isinstance(col, pd.Timestamp):
                col_str = col.strftime("%Y-%m-%d")
            else:
                col_str = str(col)
            result[col_str] = {
                str(idx): float(val) if pd.notnull(val) else None
                for idx, val in df[col].items()
            }
        return result

    return cached_yfinance_call(key, TTL_FINANCIALS, _fetch)


def get_yfinance_calendar_data(ticker_name: str) -> Dict:
    """
    Get earnings / ex-dividend calendar-style data from yfinance (DataFrame or dict).

    Returns:
        JSON-friendly dict (may be empty).
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:calendar"

    def _fetch() -> Dict:
        ticker = yf.Ticker(fmt)
        cal = getattr(ticker, "calendar", None)
        if cal is None:
            return {}
        if isinstance(cal, pd.DataFrame):
            if cal.empty:
                return {}
            # orient='index' with string index
            out = {}
            for idx, row in cal.iterrows():
                k = str(idx)
                out[k] = {
                    str(c): float(v) if pd.notnull(v) and isinstance(v, (int, float)) else str(v) if pd.notnull(v) else None
                    for c, v in row.items()
                }
            return out
        if isinstance(cal, dict):
            return dict(cal)
        return {}

    return cached_yfinance_call(key, TTL_EARNINGS, _fetch)


def get_yfinance_earnings_estimate(ticker_name: str) -> Optional[Dict]:
    """
    Get earnings estimates.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with earnings estimates or None
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:earnings_estimate"

    def _fetch() -> Optional[Dict]:
        ticker = yf.Ticker(fmt)
        df = ticker.earnings_estimate
        if df is not None:
            return {
                str(idx): {
                    str(col): float(val) if pd.notnull(val) else None
                    for col, val in row.items()
                }
                for idx, row in df.iterrows()
            }
        return None

    return cached_yfinance_call(key, TTL_EARNINGS, _fetch)


def get_yfinance_earnings_history(ticker_name: str) -> Optional[Dict]:
    """
    Get earnings history.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with earnings history or None
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:earnings_history"

    def _fetch() -> Optional[Dict]:
        ticker = yf.Ticker(fmt)
        df = ticker.earnings_history
        if df is not None:
            return {
                str(idx): {
                    str(col): float(val) if pd.notnull(val) else None
                    for col, val in row.items()
                }
                for idx, row in df.iterrows()
            }
        return None

    return cached_yfinance_call(key, TTL_EARNINGS, _fetch)


def get_yfinance_revenue_estimate(ticker_name: str) -> Optional[Dict]:
    """
    Get revenue estimates.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with revenue estimates or None
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:revenue_estimate"

    def _fetch() -> Optional[Dict]:
        ticker = yf.Ticker(fmt)
        df = ticker.revenue_estimate
        if df is not None:
            return {
                str(idx): {
                    str(col): float(val) if pd.notnull(val) else None
                    for col, val in row.items()
                }
                for idx, row in df.iterrows()
            }
        return None

    return cached_yfinance_call(key, TTL_EARNINGS, _fetch)


def get_yfinance_eps_trend(ticker_name: str) -> Optional[Dict]:
    """
    Get EPS trend data.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with EPS trend or None
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:eps_trend"

    def _fetch() -> Optional[Dict]:
        ticker = yf.Ticker(fmt)
        df = ticker.eps_trend
        if df is not None:
            return {
                str(idx): {
                    str(col): float(val) if pd.notnull(val) else None
                    for col, val in row.items()
                }
                for idx, row in df.iterrows()
            }
        return None

    return cached_yfinance_call(key, TTL_EARNINGS, _fetch)


def get_yfinance_eps_revisions(ticker_name: str) -> Optional[Dict]:
    """
    Get EPS revisions.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with EPS revisions or None
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:eps_revisions"

    def _fetch() -> Optional[Dict]:
        ticker = yf.Ticker(fmt)
        df = ticker.eps_revisions
        if df is not None:
            return {
                str(idx): {
                    str(col): float(val) if pd.notnull(val) else None
                    for col, val in row.items()
                }
                for idx, row in df.iterrows()
            }
        return None

    return cached_yfinance_call(key, TTL_EARNINGS, _fetch)


def get_yfinance_growth_estimates(ticker_name: str) -> Optional[Dict]:
    """
    Get growth estimates.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        Dictionary with growth estimates or None
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:growth_estimates"

    def _fetch() -> Optional[Dict]:
        ticker = yf.Ticker(fmt)
        df = ticker.growth_estimates
        if df is not None:
            return {
                str(idx): {
                    str(col): float(val) if pd.notnull(val) else None
                    for col, val in row.items()
                }
                for idx, row in df.iterrows()
            }
        return None

    return cached_yfinance_call(key, TTL_EARNINGS, _fetch)


def get_yfinance_stock_history(
    ticker_name: str,
    period: str = "1y",
    interval: str = "1d",
    auto_adjust: bool = True,
    return_trace: bool = False,
) -> Union[Dict, Tuple[Dict, Dict]]:
    """
    Get historical stock price data (OHLCV).

    Args:
        ticker_name: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        auto_adjust: If True (default), prices are dividend- and split-adjusted. If False, raw prices.
        return_trace: If True, return (result_dict, trace_dict) for data provenance; else result_dict only.

    Returns:
        Dictionary with historical OHLCV data (empty dict if no data), or when return_trace=True
        a tuple (result_dict, trace_dict) with trace containing provider and raw_shape.
    """
    fmt = get_ticker_format(ticker_name)
    trace_flag = "1" if return_trace else "0"
    key = f"{fmt}:history:{period}:{interval}:{int(auto_adjust)}:{trace_flag}"

    def _fetch() -> Union[Dict, Tuple[Dict, Dict]]:
        ticker = yf.Ticker(fmt)
        df = ticker.history(period=period, interval=interval, auto_adjust=auto_adjust)

        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            if return_trace:
                return {}, {"provider": "yfinance", "raw_shape": (0, 0)}
            return {}

        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            if return_trace:
                return {}, {"provider": "yfinance", "raw_shape": (0, 0)}
            return {}

        df_selected = df[required_columns]
        result = {}
        for idx, row in df_selected.iterrows():
            date_str = str(idx)
            result[date_str] = {
                "Open": float(row["Open"]) if pd.notnull(row["Open"]) else None,
                "High": float(row["High"]) if pd.notnull(row["High"]) else None,
                "Low": float(row["Low"]) if pd.notnull(row["Low"]) else None,
                "Close": float(row["Close"]) if pd.notnull(row["Close"]) else None,
                "Volume": float(row["Volume"]) if pd.notnull(row["Volume"]) else None,
            }
        if return_trace:
            trace = {"provider": "yfinance", "raw_shape": (len(result), 5)}
            return result, trace
        return result

    return cached_yfinance_call(key, TTL_HISTORY, _fetch)


def get_yfinance_dividends(ticker_name: str) -> pd.Series:
    """
    Dividend payment history (date index, amount per share).

    Returns:
        Empty Series if none.
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:dividends"

    def _fetch() -> pd.Series:
        ticker = yf.Ticker(fmt)
        d = ticker.dividends
        if d is None or (isinstance(d, pd.Series) and d.empty):
            return pd.Series(dtype=float)
        return d

    return cached_yfinance_call(key, TTL_FINANCIALS, _fetch)


def get_yfinance_ticker_news(ticker_name: str) -> list:
    """
    Get latest news for a stock.

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        List of news items. Empty list if no data.
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:news"

    def _fetch() -> list:
        ticker = yf.Ticker(fmt)
        news = ticker.news
        return list(news) if news else []

    return cached_yfinance_call(key, TTL_NEWS, _fetch)


def get_yfinance_ticker_filings(ticker_name: str) -> list:
    """
    Get SEC filings for a stock (US stocks only).

    Args:
        ticker_name: Stock ticker symbol

    Returns:
        List of SEC filings or empty list for non-US stocks
    """
    fmt = get_ticker_format(ticker_name)
    key = f"{fmt}:filings"

    def _fetch() -> list:
        if get_ticker_country(ticker_name) == "US":
            ticker = yf.Ticker(fmt)
            filings = getattr(ticker, "sec_filings", None)
            return list(filings) if filings else []
        return []

    return cached_yfinance_call(key, TTL_FILINGS, _fetch)


def get_yfinance_market_summary_crypto() -> Dict:
    """
    Get cryptocurrency market summary.

    Returns:
        Dictionary with crypto market data
    """
    key = "market:crypto"

    def _fetch() -> Dict:
        summary_url = "https://query1.finance.yahoo.com/v7/finance/quote?"
        summary_fields = [
            "shortName",
            "regularMarketPrice",
            "regularMarketChange",
            "regularMarketChangePercent",
            "currency",
            "fromCurrency",
            "toCurrency",
            "exchangeTimezoneName",
            "exchangeTimezoneShortName",
            "gmtOffSetMilliseconds",
            "regularMarketTime",
            "preMarketTime",
            "postMarketTime",
            "extendedMarketTime",
            "overnightMarketTime",
        ]
        symbols = [
            "BNB-USD",
            "BTC-USD",
            "DOGE-USD",
            "ETH-USD",
            "SOL-USD",
            "USDC-USD",
            "USDT-USD",
            "XRP-USD",
        ]
        summary_params = {
            "fields": ",".join(summary_fields),
            "formatted": False,
            "lang": "en-US",
            "market": "CRYPTOCURRENCIES",
            "symbols": ",".join(symbols),
        }

        summary = yf.Market("CRYPTOCURRENCIES")._fetch_json(
            summary_url, summary_params
        )
        return summary if summary is not None else {}

    return cached_yfinance_call(key, TTL_MARKET, _fetch)


def get_yfinance_market_summary_us() -> Dict:
    """
    Get US market summary.

    Returns:
        Dictionary with US market data. Empty dict if no data.
    """
    key = "market:us"

    def _fetch() -> Dict:
        markets = yf.Market("US")
        summary = getattr(markets, "summary", None)
        return summary if summary is not None else {}

    return cached_yfinance_call(key, TTL_MARKET, _fetch)


def get_yfinance_market_summary_asia() -> Dict:
    """
    Get Asian market summary.

    Returns:
        Dictionary with Asian market data. Empty dict if no data.
    """
    key = "market:asia"

    def _fetch() -> Dict:
        markets = yf.Market("ASIA")
        summary = getattr(markets, "summary", None)
        return summary if summary is not None else {}

    return cached_yfinance_call(key, TTL_MARKET, _fetch)


def get_yfinance_market_summary_europe() -> Dict:
    """
    Get European market summary.

    Returns:
        Dictionary with European market data. Empty dict if no data.
    """
    key = "market:europe"

    def _fetch() -> Dict:
        markets = yf.Market("EUROPE")
        summary = getattr(markets, "summary", None)
        return summary if summary is not None else {}

    return cached_yfinance_call(key, TTL_MARKET, _fetch)


def get_yfinance_market_summary_currency() -> Dict:
    """
    Get currency market summary.

    Returns:
        Dictionary with currency market data. Empty dict if no data.
    """
    key = "market:currency"

    def _fetch() -> Dict:
        markets = yf.Market("CURRENCIES")
        summary = getattr(markets, "summary", None)
        return summary if summary is not None else {}

    return cached_yfinance_call(key, TTL_MARKET, _fetch)


def get_yfinance_market_summary_commodities() -> Dict:
    """
    Get commodities market summary.

    Returns:
        Dictionary with commodities market data. Empty dict if no data.
    """
    key = "market:commodities"

    def _fetch() -> Dict:
        markets = yf.Market("COMMODITIES")
        summary = getattr(markets, "summary", None)
        return summary if summary is not None else {}

    return cached_yfinance_call(key, TTL_MARKET, _fetch)
