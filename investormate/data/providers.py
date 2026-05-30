"""
Pluggable data-source layer for InvestorMate.

All market/fundamental data flows through a :class:`DataProvider`. The default
:class:`YFinanceProvider` delegates to the cached ``get_yfinance_*`` fetchers, so
caching, rate limiting, and existing behavior are unchanged. Swap the active
source process-wide with :func:`set_data_provider` to point InvestorMate at an
alternate API, a recorded fixture set, or a test double::

    from investormate import set_data_provider, DataProvider

    class MyProvider(DataProvider):
        def get_info(self, ticker): ...
        # ... implement the rest, or subclass YFinanceProvider to override a few

    set_data_provider(MyProvider())

Providers receive ticker symbols exactly as the caller supplies them (the
``YFinanceProvider`` applies yfinance-specific formatting internally, mirroring
the legacy fetchers).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd

from . import fetchers

# Market keys accepted by ``get_market_summary`` (mirrors ``core.market``).
MARKET_US = "US"
MARKET_ASIA = "ASIA"
MARKET_EUROPE = "EUROPE"
MARKET_CRYPTO = "CRYPTO"
MARKET_CURRENCIES = "CURRENCIES"
MARKET_COMMODITIES = "COMMODITIES"


class DataProvider(ABC):
    """
    Abstract interface every InvestorMate data source must implement.

    Methods return JSON-serializable structures (dicts/lists) or, for prices and
    dividends, the same pandas objects the legacy fetchers returned. Subclass
    :class:`YFinanceProvider` to reuse the default yfinance behavior and override
    only the methods you need.
    """

    @property
    def name(self) -> str:
        """Human-readable provider name (defaults to the class name)."""
        return type(self).__name__

    @abstractmethod
    def get_info(self, ticker: str) -> Dict:
        """Company/quote info dictionary (empty dict if unavailable)."""

    @abstractmethod
    def get_balance_sheet(self, ticker: str) -> Dict:
        """Balance sheet as ``{period: {line_item: value}}``."""

    @abstractmethod
    def get_income_statement(self, ticker: str) -> Dict:
        """Income statement as ``{period: {line_item: value}}``."""

    @abstractmethod
    def get_cash_flow(self, ticker: str) -> Dict:
        """Cash flow statement as ``{period: {line_item: value}}``."""

    @abstractmethod
    def get_calendar(self, ticker: str) -> Dict:
        """Earnings/ex-dividend calendar data."""

    @abstractmethod
    def get_earnings_estimate(self, ticker: str) -> Optional[Dict]:
        """Analyst earnings estimates, or ``None``."""

    @abstractmethod
    def get_earnings_history(self, ticker: str) -> Optional[Dict]:
        """Historical earnings/EPS surprise data, or ``None``."""

    @abstractmethod
    def get_revenue_estimate(self, ticker: str) -> Optional[Dict]:
        """Analyst revenue estimates, or ``None``."""

    @abstractmethod
    def get_eps_trend(self, ticker: str) -> Optional[Dict]:
        """EPS estimate trend, or ``None``."""

    @abstractmethod
    def get_eps_revisions(self, ticker: str) -> Optional[Dict]:
        """EPS estimate revisions, or ``None``."""

    @abstractmethod
    def get_growth_estimates(self, ticker: str) -> Optional[Dict]:
        """Forward growth estimates, or ``None``."""

    @abstractmethod
    def get_history(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        auto_adjust: bool = True,
        return_trace: bool = False,
    ) -> Union[Dict, Tuple[Dict, Dict]]:
        """Historical OHLCV data; returns ``(data, trace)`` when ``return_trace``."""

    @abstractmethod
    def get_dividends(self, ticker: str) -> pd.Series:
        """Dividend history as a pandas Series (empty Series if none)."""

    @abstractmethod
    def get_news(self, ticker: str) -> List:
        """Recent news items (empty list if none)."""

    @abstractmethod
    def get_filings(self, ticker: str) -> List:
        """Regulatory filings (empty list if none / unsupported)."""

    @abstractmethod
    def get_market_summary(self, market: str) -> Dict:
        """Market summary for one of the ``MARKET_*`` keys."""


class YFinanceProvider(DataProvider):
    """
    Default provider backed by yfinance via the cached ``get_yfinance_*`` fetchers.

    Delegates to :mod:`investormate.data.fetchers`, preserving the in-memory TTL
    cache and rate limiting. Subclass and override individual methods to blend
    yfinance with another source.
    """

    _MARKET_DISPATCH = {
        MARKET_US: fetchers.get_yfinance_market_summary_us,
        MARKET_ASIA: fetchers.get_yfinance_market_summary_asia,
        MARKET_EUROPE: fetchers.get_yfinance_market_summary_europe,
        MARKET_CRYPTO: fetchers.get_yfinance_market_summary_crypto,
        MARKET_CURRENCIES: fetchers.get_yfinance_market_summary_currency,
        MARKET_COMMODITIES: fetchers.get_yfinance_market_summary_commodities,
    }

    def get_info(self, ticker: str) -> Dict:
        return fetchers.get_yfinance_data(ticker)

    def get_balance_sheet(self, ticker: str) -> Dict:
        return fetchers.get_yfinance_balance_sheet_data(ticker)

    def get_income_statement(self, ticker: str) -> Dict:
        return fetchers.get_yfinance_income_statement_data(ticker)

    def get_cash_flow(self, ticker: str) -> Dict:
        return fetchers.get_yfinance_cash_flow_statement_data(ticker)

    def get_calendar(self, ticker: str) -> Dict:
        return fetchers.get_yfinance_calendar_data(ticker)

    def get_earnings_estimate(self, ticker: str) -> Optional[Dict]:
        return fetchers.get_yfinance_earnings_estimate(ticker)

    def get_earnings_history(self, ticker: str) -> Optional[Dict]:
        return fetchers.get_yfinance_earnings_history(ticker)

    def get_revenue_estimate(self, ticker: str) -> Optional[Dict]:
        return fetchers.get_yfinance_revenue_estimate(ticker)

    def get_eps_trend(self, ticker: str) -> Optional[Dict]:
        return fetchers.get_yfinance_eps_trend(ticker)

    def get_eps_revisions(self, ticker: str) -> Optional[Dict]:
        return fetchers.get_yfinance_eps_revisions(ticker)

    def get_growth_estimates(self, ticker: str) -> Optional[Dict]:
        return fetchers.get_yfinance_growth_estimates(ticker)

    def get_history(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        auto_adjust: bool = True,
        return_trace: bool = False,
    ) -> Union[Dict, Tuple[Dict, Dict]]:
        return fetchers.get_yfinance_stock_history(
            ticker,
            period,
            interval,
            auto_adjust=auto_adjust,
            return_trace=return_trace,
        )

    def get_dividends(self, ticker: str) -> pd.Series:
        return fetchers.get_yfinance_dividends(ticker)

    def get_news(self, ticker: str) -> List:
        return fetchers.get_yfinance_ticker_news(ticker)

    def get_filings(self, ticker: str) -> List:
        return fetchers.get_yfinance_ticker_filings(ticker)

    def get_market_summary(self, market: str) -> Dict:
        try:
            fetch = self._MARKET_DISPATCH[market]
        except KeyError:
            raise ValueError(f"Unknown market: {market}")
        return fetch()


# Process-wide active provider (defaults to yfinance).
_active_provider: DataProvider = YFinanceProvider()


def get_data_provider() -> DataProvider:
    """Return the currently active :class:`DataProvider`."""
    return _active_provider


def set_data_provider(provider: DataProvider) -> DataProvider:
    """
    Install ``provider`` as the active data source and return it.

    Raises:
        TypeError: If ``provider`` is not a :class:`DataProvider` instance.
    """
    global _active_provider
    if not isinstance(provider, DataProvider):
        raise TypeError(
            f"provider must be a DataProvider instance, got {type(provider).__name__}"
        )
    _active_provider = provider
    return provider


def reset_data_provider() -> DataProvider:
    """Restore the default :class:`YFinanceProvider` and return it."""
    global _active_provider
    _active_provider = YFinanceProvider()
    return _active_provider
