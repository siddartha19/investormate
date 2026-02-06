"""
Stock class for InvestorMate.
Main interface for accessing stock data, ratios, and indicators.
"""

from typing import Dict, Optional
import pandas as pd

from ..data.fetchers import (
    get_yfinance_data,
    get_yfinance_balance_sheet_data,
    get_yfinance_income_statement_data,
    get_yfinance_cash_flow_statement_data,
    get_yfinance_stock_history,
    get_yfinance_ticker_news,
    get_yfinance_ticker_filings,
)
from ..data.constants import get_ticker_format
from ..data.parsers import extract_price_data, extract_company_info
from ..data.earnings_transcripts import EarningsCallTranscripts
from ..analysis.ratios import RatiosCalculator
from ..analysis.indicators import IndicatorsHelper
from ..analysis.scores import FinancialScores
from ..analysis.valuation import Valuation
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
        
    # Core Data Properties
    
    @property
    def info(self) -> Dict:
        """Get stock info (fetched once and cached)."""
        if self._info is None:
            try:
                self._info = get_yfinance_data(self.ticker)
            except Exception as e:
                raise DataFetchError(f"Failed to fetch stock info: {str(e)}")
        return self._info
    
    @property
    def price(self) -> Optional[float]:
        """Get current stock price."""
        price_data = extract_price_data(self.info)
        return price_data.get('current_price')
    
    @property
    def previous_close(self) -> Optional[float]:
        """Get previous close price."""
        return extract_price_data(self.info).get('previous_close')
    
    @property
    def market_cap(self) -> Optional[float]:
        """Get market capitalization."""
        return self.info.get('marketCap')
    
    @property
    def volume(self) -> Optional[int]:
        """Get trading volume."""
        price_data = extract_price_data(self.info)
        return price_data.get('volume')
    
    # Company Info
    
    @property
    def name(self) -> str:
        """Get company name."""
        company_info = extract_company_info(self.info)
        return company_info.get('name', self.ticker)
    
    @property
    def sector(self) -> Optional[str]:
        """Get company sector."""
        return extract_company_info(self.info).get('sector')
    
    @property
    def industry(self) -> Optional[str]:
        """Get company industry."""
        return extract_company_info(self.info).get('industry')
    
    @property
    def description(self) -> Optional[str]:
        """Get company description."""
        return extract_company_info(self.info).get('description')
    
    # Financial Statements
    
    @property
    def balance_sheet(self) -> Dict:
        """Get balance sheet data."""
        if self._balance_sheet is None:
            try:
                self._balance_sheet = get_yfinance_balance_sheet_data(self.ticker)
            except Exception as e:
                raise DataFetchError(f"Failed to fetch balance sheet: {str(e)}")
        return self._balance_sheet
    
    @property
    def income_statement(self) -> Dict:
        """Get income statement data."""
        if self._income_stmt is None:
            try:
                self._income_stmt = get_yfinance_income_statement_data(self.ticker)
            except Exception as e:
                raise DataFetchError(f"Failed to fetch income statement: {str(e)}")
        return self._income_stmt
    
    @property
    def cash_flow(self) -> Dict:
        """Get cash flow statement data."""
        if self._cash_flow is None:
            try:
                self._cash_flow = get_yfinance_cash_flow_statement_data(self.ticker)
            except Exception as e:
                raise DataFetchError(f"Failed to fetch cash flow: {str(e)}")
        return self._cash_flow
    
    # Analysis Properties
    
    @property
    def ratios(self) -> RatiosCalculator:
        """Get financial ratios calculator."""
        return RatiosCalculator(
            self.info,
            self.balance_sheet,
            self.income_statement,
            self.cash_flow
        )
    
    @property
    def scores(self) -> FinancialScores:
        """Get financial scores calculator."""
        return FinancialScores(
            self.info,
            self.balance_sheet,
            self.income_statement,
            self.cash_flow
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
    
    def history(self, period: str = "1y", interval: str = "1d", 
                start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """
        Get historical price data.
        
        Args:
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            start: Start date (YYYY-MM-DD) - alternative to period
            end: End date (YYYY-MM-DD) - alternative to period
            
        Returns:
            DataFrame with OHLCV data
        """
        # Validate period/interval at entry (Phase 1.1 input validation)
        period = validate_period(period)
        interval = validate_interval(interval)

        cache_key = f"{period}_{interval}_{start}_{end}"
        
        if cache_key not in self._history_cache:
            
            try:
                data_dict = get_yfinance_stock_history(self.ticker, period, interval)
                
                # Convert dict to DataFrame
                df = pd.DataFrame.from_dict(data_dict, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                
                self._history_cache[cache_key] = df
            except Exception as e:
                raise DataFetchError(f"Failed to fetch historical data: {str(e)}")
        
        return self._history_cache[cache_key]
    
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
            if hasattr(ticker, 'financials'):
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
            return get_yfinance_ticker_news(self.ticker)
        except Exception as e:
            raise DataFetchError(f"Failed to fetch news: {str(e)}")
    
    @property
    def filings(self) -> list:
        """Get SEC filings (US stocks only)."""
        try:
            return get_yfinance_ticker_filings(self.ticker)
        except Exception as e:
            raise DataFetchError(f"Failed to fetch filings: {str(e)}")
    
    # Earnings Call Transcripts
    
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
        """Clear cached data to force refresh on next access."""
        self._info = None
        self._balance_sheet = None
        self._income_stmt = None
        self._cash_flow = None
        self._history_cache = {}
        self._earnings_transcripts = None
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Stock(ticker='{self.ticker}', name='{self.name}')"
