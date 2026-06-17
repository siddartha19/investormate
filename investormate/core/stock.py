"""
Stock class for InvestorMate.
Main interface for accessing stock data, ratios, and indicators.
"""

import warnings
from typing import Any, Dict, List, Optional

import pandas as pd

from ..data.providers import get_data_provider
from ..data.cache import invalidate_ticker_cache
from ..data.constants import MAJOR_US_TICKERS, get_ticker_format
from ..data.parsers import extract_price_data, extract_company_info
from ..data.earnings_transcripts import EarningsCallTranscripts
from ..analysis.ratios import RatiosCalculator
from ..analysis.indicators import IndicatorsHelper
from ..analysis.scores import FinancialScores
from ..analysis.valuation import Valuation
from ..analysis.earnings import EarningsAnalyzer
from ..analysis.financials import FinancialStatements
from ..analysis.capm import CAPMAnalyzer
from ..utils.validators import validate_ticker, validate_period, validate_interval
from ..utils.exceptions import DataFetchError


class Stock:
    """
    Main Stock class for accessing stock data and analysis.

    Example:
        >>> stock = Stock("AAPL")
        >>> print(stock.price)
        >>> print(stock.ratios.pe)
        >>> print(stock.indicators.rsi())
    """

    @classmethod
    def batch(
        cls,
        tickers: List[str],
        *,
        skip_invalid: bool = True,
    ) -> List["Stock"]:
        """
        Build multiple ``Stock`` instances from tickers.

        Args:
            tickers: Ticker symbols.
            skip_invalid: If True, skip tickers that fail validation or init;
                emits a ``UserWarning`` per skipped symbol. If False, the first
                error is raised.

        Returns:
            List of successfully constructed ``Stock`` objects (may be shorter
            than ``tickers`` when ``skip_invalid`` is True).
        """
        stocks: List[Stock] = []
        for raw in tickers:
            try:
                stocks.append(cls(raw))
            except Exception as exc:
                if not skip_invalid:
                    raise
                warnings.warn(
                    f"Skipping ticker {raw!r}: {exc}",
                    UserWarning,
                    stacklevel=2,
                )
        return stocks

    def __init__(self, ticker: str):
        """
        Initialize Stock instance.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "GOOGL", "RELIANCE")
        """
        self.ticker = validate_ticker(ticker)
        self._info = None
        self._balance_sheet = None
        self._income_stmt = None
        self._cash_flow = None
        self._history_cache = {}
        self._earnings_transcripts = None
        self._earnings_analyzer = None
        self._financials_analyzer = None
        self._capm_analyzer = None

    # Core Data Properties

    @property
    def info(self) -> Dict:
        """Get stock info (fetched once and cached)."""
        if self._info is None:
            try:
                self._info = get_data_provider().get_info(self.ticker)
            except Exception as e:
                raise DataFetchError(f"Failed to fetch stock info: {str(e)}")
        return self._info

    @property
    def price(self) -> Optional[float]:
        """Get current stock price."""
        price_data = extract_price_data(self.info)
        return price_data.get("current_price")

    @property
    def previous_close(self) -> Optional[float]:
        """Get previous close price."""
        return extract_price_data(self.info).get("previous_close")

    @property
    def market_cap(self) -> Optional[float]:
        """Get market capitalization."""
        return self.info.get("marketCap")

    @property
    def volume(self) -> Optional[int]:
        """Get trading volume."""
        price_data = extract_price_data(self.info)
        return price_data.get("volume")

    # Company Info

    @property
    def name(self) -> str:
        """Get company name."""
        company_info = extract_company_info(self.info)
        return company_info.get("name", self.ticker)

    @property
    def sector(self) -> Optional[str]:
        """Get company sector."""
        return extract_company_info(self.info).get("sector")

    @property
    def industry(self) -> Optional[str]:
        """Get company industry."""
        return extract_company_info(self.info).get("industry")

    @property
    def peers(self) -> List[str]:
        """
        Auto-detect peer tickers in the same sector (from ``MAJOR_US_TICKERS``).

        Fetches brief info for candidates; may be slow. Returns up to 12 peers
        excluding this ticker. Empty if sector is unknown or no matches.
        """
        my_sector = self.sector
        if not my_sector:
            return []

        peers: List[str] = []
        for candidate in MAJOR_US_TICKERS:
            if candidate.upper() == self.ticker.upper():
                continue
            try:
                info = get_data_provider().get_info(candidate)
                if info.get("sector") == my_sector:
                    peers.append(candidate)
            except Exception:
                continue
            if len(peers) >= 12:
                break
        return peers

    def compare_with(self, peers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare key valuation and quality metrics vs peers.

        Args:
            peers: Explicit peer list; if omitted, uses :py:attr:`peers`.

        Returns:
            Dict with ``subject``, ``peers_compared``, and ``metrics`` (per ticker).
        """
        peer_list = list(peers) if peers is not None else self.peers
        ordered: List[str] = [self.ticker]
        seen = {self.ticker.upper()}
        for p in peer_list:
            u = p.upper()
            if u in seen:
                continue
            seen.add(u)
            ordered.append(p)
            if len(ordered) >= 16:
                break

        def _metrics_row(st: "Stock") -> Dict[str, Any]:
            inf = st.info
            return {
                "name": st.name,
                "sector": st.sector,
                "pe": inf.get("trailingPE") or inf.get("forwardPE"),
                "pb": inf.get("priceToBook"),
                "ps": inf.get("priceToSalesTrailing12Months"),
                "roe": inf.get("returnOnEquity"),
                "roa": inf.get("returnOnAssets"),
                "profit_margin": inf.get("profitMargins"),
                "gross_margin": inf.get("grossMargins"),
                "revenue_growth": inf.get("revenueGrowth"),
                "earnings_growth": inf.get("earningsGrowth"),
                "market_cap": inf.get("marketCap"),
            }

        metrics: Dict[str, Dict[str, Any]] = {self.ticker: _metrics_row(self)}
        for sym in ordered[1:]:
            try:
                metrics[sym] = _metrics_row(Stock(sym))
            except Exception:
                continue

        return {
            "subject": self.ticker,
            "peers_compared": list(metrics.keys()),
            "metrics": metrics,
        }

    @property
    def description(self) -> Optional[str]:
        """Get company description."""
        return extract_company_info(self.info).get("description")

    # Financial Statements

    @property
    def balance_sheet(self) -> Dict:
        """Get balance sheet data."""
        if self._balance_sheet is None:
            try:
                self._balance_sheet = get_data_provider().get_balance_sheet(self.ticker)
            except Exception as e:
                raise DataFetchError(f"Failed to fetch balance sheet: {str(e)}")
        return self._balance_sheet

    @property
    def income_statement(self) -> Dict:
        """Get income statement data."""
        if self._income_stmt is None:
            try:
                self._income_stmt = get_data_provider().get_income_statement(
                    self.ticker
                )
            except Exception as e:
                raise DataFetchError(f"Failed to fetch income statement: {str(e)}")
        return self._income_stmt

    @property
    def cash_flow(self) -> Dict:
        """Get cash flow statement data."""
        if self._cash_flow is None:
            try:
                self._cash_flow = get_data_provider().get_cash_flow(self.ticker)
            except Exception as e:
                raise DataFetchError(f"Failed to fetch cash flow: {str(e)}")
        return self._cash_flow

    # Analysis Properties

    @property
    def ratios(self) -> RatiosCalculator:
        """Get financial ratios calculator."""
        return RatiosCalculator(
            self.info, self.balance_sheet, self.income_statement, self.cash_flow
        )

    @property
    def scores(self) -> FinancialScores:
        """Get financial scores calculator."""
        return FinancialScores(
            self.info, self.balance_sheet, self.income_statement, self.cash_flow
        )

    @property
    def indicators(self) -> IndicatorsHelper:
        """Get technical indicators helper (uses 1y daily data by default)."""
        df = self.history(period="1y", interval="1d")
        return IndicatorsHelper(df)

    @property
    def sentiment(self):
        """Get sentiment analyzer for news sentiment analysis."""
        from ..analysis.sentiment import SentimentAnalyzer

        return SentimentAnalyzer(self.ticker, lambda: self.news)

    # Historical Data

    def history(
        self,
        period: str = "1y",
        interval: str = "1d",
        start: Optional[str] = None,
        end: Optional[str] = None,
        adjusted: bool = True,
        source_trace: bool = False,
    ):
        """
        Get historical price data.

        Args:
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            start: Start date (YYYY-MM-DD) - alternative to period
            end: End date (YYYY-MM-DD) - alternative to period
            adjusted: If True (default), dividend- and split-adjusted prices. If False, raw prices.
            source_trace: If True, return a result object with .data and .trace instead of a DataFrame.

        Returns:
            DataFrame with OHLCV data, or when source_trace=True a HistoryResult with .data and .trace.
        """
        # Validate period/interval at entry (Phase 1.1 input validation)
        period = validate_period(period)
        interval = validate_interval(interval)

        cache_key = f"{period}_{interval}_{start}_{end}_{adjusted}"
        if cache_key not in self._history_cache:
            try:
                out = get_data_provider().get_history(
                    self.ticker,
                    period,
                    interval,
                    auto_adjust=adjusted,
                    return_trace=source_trace,
                )
                if source_trace:
                    data_dict, trace = out
                else:
                    data_dict, trace = out, None
                df = pd.DataFrame.from_dict(data_dict, orient="index")
                df.index = pd.to_datetime(df.index, utc=True)
                df = df.sort_index()
                if source_trace and trace is not None:
                    trace["transform_steps"] = [
                        "normalize_timestamps_utc",
                        "sort_index",
                    ]
                    trace["raw_shape"] = (len(data_dict), 5)
                    self._history_cache[cache_key] = (df, trace)
                else:
                    self._history_cache[cache_key] = (df, None)
            except Exception as e:
                raise DataFetchError(f"Failed to fetch historical data: {str(e)}")

        cached = self._history_cache[cache_key]
        df, trace = cached if isinstance(cached, tuple) else (cached, None)

        if source_trace:
            from .history_result import HistoryResult

            return HistoryResult(
                data=df,
                trace=trace
                or {
                    "provider": "yfinance",
                    "transform_steps": ["normalize_timestamps_utc", "sort_index"],
                },
            )
        return df

    # Revenue Breakdown

    @property
    def revenue_by_segment(self) -> Optional[Dict]:
        """
        Get revenue breakdown by business segment.

        Returns:
            Dictionary with segment revenue data or None if not available
        """
        try:
            import yfinance as yf

            ticker = yf.Ticker(get_ticker_format(self.ticker))

            # Try to get segment data from financials
            if hasattr(ticker, "financials"):
                # This may not be available for all stocks
                # yfinance doesn't directly expose segment data in a standard way
                # Return None for now - would need custom scraping
                pass

            return None
        except Exception:
            return None

    @property
    def revenue_by_geography(self) -> Optional[Dict]:
        """
        Get revenue breakdown by geographic region.

        Returns:
            Dictionary with geographic revenue data or None if not available
        """
        try:
            import yfinance as yf

            ticker = yf.Ticker(get_ticker_format(self.ticker))

            # Try to get geographic data from financials
            # This may not be available for all stocks
            # yfinance doesn't directly expose geographic data in a standard way
            # Return None for now - would need custom scraping

            return None
        except Exception:
            return None

    # News & Filings

    @property
    def news(self) -> list:
        """Get latest news."""
        try:
            return get_data_provider().get_news(self.ticker)
        except Exception as e:
            raise DataFetchError(f"Failed to fetch news: {str(e)}")

    @property
    def filings(self) -> list:
        """Get SEC filings (US stocks only)."""
        try:
            return get_data_provider().get_filings(self.ticker)
        except Exception as e:
            raise DataFetchError(f"Failed to fetch filings: {str(e)}")

    # Earnings Call Transcripts

    @property
    def earnings(self) -> EarningsAnalyzer:
        """
        Earnings calendar, estimates, surprise history, and EPS trends (yfinance).

        Example:
            >>> stock = Stock("AAPL")
            >>> stock.earnings.calendar()
            >>> stock.earnings.surprise_history()
        """
        if self._earnings_analyzer is None:
            self._earnings_analyzer = EarningsAnalyzer(self.ticker)
        return self._earnings_analyzer

    @property
    def financials(self) -> FinancialStatements:
        """
        Financial statement analysis (common-size, horizontal, trend, cash flow quality).

        Example:
            >>> stock.financials.common_size("income")
            >>> stock.financials.horizontal(periods=3)
        """
        if self._financials_analyzer is None:
            self._financials_analyzer = FinancialStatements(
                self.ticker,
                info=self.info,
                balance_sheet=self.balance_sheet,
                income_stmt=self.income_statement,
                cash_flow=self.cash_flow,
            )
        return self._financials_analyzer

    @property
    def capm(self) -> CAPMAnalyzer:
        """
        CAPM and factor model analysis for this stock.

        Example:
            >>> stock.capm.capm(benchmark="SPY")
            >>> stock.capm.jensen_alpha()
        """
        if self._capm_analyzer is None:
            self._capm_analyzer = CAPMAnalyzer(self.ticker)
        return self._capm_analyzer

    def jensen_alpha(self, benchmark: str = "SPY", **kwargs) -> Dict[str, Any]:
        """Shortcut for ``stock.capm.jensen_alpha()``."""
        return self.capm.jensen_alpha(benchmark, **kwargs)

    def report(
        self,
        format: str = "markdown",
        *,
        sections: Optional[List[str]] = None,
    ) -> str:
        """
        Generate a coursework-ready report (markdown; core stdlib only).
        """
        if format != "markdown":
            raise ValidationError(f"Unsupported format: {format}. Use 'markdown'.")
        from ..reporting.export import markdown_report

        return markdown_report(
            self.ticker,
            self.name,
            self.info,
            self.ratios.all(),
            sector=self.sector,
            sections=sections,
        )

    def to_excel(self, path: str) -> str:
        """
        Export analysis workbook (requires ``pip install investormate[export]``).
        """
        from ..reporting.export import export_to_excel

        return export_to_excel(
            path,
            ticker=self.ticker,
            info=self.info,
            ratios=self.ratios.all(),
            income_stmt=self.income_statement,
            balance_sheet=self.balance_sheet,
        )

    @property
    def valuation(self) -> Valuation:
        """
        Get valuation module (DCF, comparable companies, fair value summary).

        Returns:
            Valuation instance

        Example:
            >>> stock = Stock("AAPL")
            >>> dcf = stock.valuation.dcf(growth_rate=0.05)
            >>> comps = stock.valuation.comps(peers=["MSFT", "GOOGL"])
            >>> summary = stock.valuation.summary(peers=["MSFT", "GOOGL"])
        """
        return Valuation(
            self.ticker,
            info=self.info,
            ratios=self.ratios,
            balance_sheet=self.balance_sheet,
            income_stmt=self.income_statement,
            cash_flow=self.cash_flow,
        )

    @property
    def earnings_transcripts(self) -> EarningsCallTranscripts:
        """
        Get earnings call transcripts handler.

        Returns:
            EarningsCallTranscripts object for accessing transcripts

        Example:
            >>> stock = Stock("AAPL")
            >>> transcripts_list = stock.earnings_transcripts.get_transcripts_list()
            >>> q4_transcript = stock.earnings_transcripts.get_transcript(2024, 4)
        """
        if self._earnings_transcripts is None:
            self._earnings_transcripts = EarningsCallTranscripts(self.ticker)
        return self._earnings_transcripts

    # Utility Methods

    def add_indicators(self, df: pd.DataFrame, indicators: list) -> pd.DataFrame:
        """
        Add technical indicators to a DataFrame.

        Args:
            df: DataFrame with OHLCV data
            indicators: List of indicator names

        Returns:
            DataFrame with indicators added
        """
        helper = IndicatorsHelper(df)
        return helper.add_indicators(indicators)

    def refresh(self):
        """
        Clear instance caches and invalidate process-wide fetch cache for this ticker.

        Next access refetches from Yahoo Finance (subject to rate limiting).
        """
        invalidate_ticker_cache(get_ticker_format(self.ticker))
        self._info = None
        self._balance_sheet = None
        self._income_stmt = None
        self._cash_flow = None
        self._history_cache = {}
        self._earnings_transcripts = None
        self._earnings_analyzer = None
        self._financials_analyzer = None
        self._capm_analyzer = None

    def __repr__(self) -> str:
        """String representation."""
        return f"Stock(ticker='{self.ticker}', name='{self.name}')"
