"""
Data fetching utilities for InvestorMate.
Wrappers around yfinance for JSON-serializable stock data.
"""

from typing import Dict, Optional
import pandas as pd
import yfinance as yf

from .constants import get_ticker_format, get_ticker_country


def get_yfinance_data(ticker_name: str) -> Dict:
    """
    Get basic stock information.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with stock info (JSON-serializable). Empty dict if no data.
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    info = ticker.info
    if info is None or not isinstance(info, dict):
        return {}
    # Convert any Timestamp objects to strings
    result = dict(info)
    for key, value in result.items():
        if isinstance(value, pd.Timestamp):
            result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
    return result


def get_yfinance_balance_sheet_data(ticker_name: str) -> Dict:
    """
    Get balance sheet data.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with balance sheet data (JSON-serializable). Empty dict if no data.
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.balance_sheet
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return {}
    # Create a new dictionary with string keys
    result = {}
    for col in df.columns:
        # Convert column name to string if it's a datetime
        if isinstance(col, pd.Timestamp):
            col_str = col.strftime('%Y-%m-%d')
        else:
            col_str = str(col)
        # Convert each row's index to string and store values
        result[col_str] = {str(idx): float(val) if pd.notnull(val) else None 
                          for idx, val in df[col].items()}
    return result


def get_yfinance_income_statement_data(ticker_name: str) -> Dict:
    """
    Get income statement data.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with income statement data (JSON-serializable). Empty dict if no data.
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.incomestmt
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return {}
    # Create a new dictionary with string keys
    result = {}
    for col in df.columns:
        # Convert column name to string if it's a datetime
        if isinstance(col, pd.Timestamp):
            col_str = col.strftime('%Y-%m-%d')
        else:
            col_str = str(col)
        # Convert each row's index to string and store values
        result[col_str] = {str(idx): float(val) if pd.notnull(val) else None 
                          for idx, val in df[col].items()}
    return result


def get_yfinance_cash_flow_statement_data(ticker_name: str) -> Dict:
    """
    Get cash flow statement data.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with cash flow data (JSON-serializable). Empty dict if no data.
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.cash_flow
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return {}
    # Create a new dictionary with string keys
    result = {}
    for col in df.columns:
        # Convert column name to string if it's a datetime
        if isinstance(col, pd.Timestamp):
            col_str = col.strftime('%Y-%m-%d')
        else:
            col_str = str(col)
        # Convert each row's index to string and store values
        result[col_str] = {str(idx): float(val) if pd.notnull(val) else None 
                          for idx, val in df[col].items()}
    return result


def get_yfinance_earnings_estimate(ticker_name: str) -> Optional[Dict]:
    """
    Get earnings estimates.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with earnings estimates or None
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.earnings_estimate
    if df is not None:
        # Convert DataFrame to dictionary with row indices as keys
        return {str(idx): {str(col): float(val) if pd.notnull(val) else None 
                          for col, val in row.items()}
                for idx, row in df.iterrows()}
    return None


def get_yfinance_earnings_history(ticker_name: str) -> Optional[Dict]:
    """
    Get earnings history.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with earnings history or None
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.earnings_history
    if df is not None:
        # Convert DataFrame to dictionary with row indices as keys
        return {str(idx): {str(col): float(val) if pd.notnull(val) else None 
                          for col, val in row.items()}
                for idx, row in df.iterrows()}
    return None


def get_yfinance_revenue_estimate(ticker_name: str) -> Optional[Dict]:
    """
    Get revenue estimates.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with revenue estimates or None
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.revenue_estimate
    if df is not None:
        # Convert DataFrame to dictionary with row indices as keys
        return {str(idx): {str(col): float(val) if pd.notnull(val) else None 
                          for col, val in row.items()}
                for idx, row in df.iterrows()}
    return None


def get_yfinance_eps_trend(ticker_name: str) -> Optional[Dict]:
    """
    Get EPS trend data.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with EPS trend or None
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.eps_trend
    if df is not None:
        # Convert DataFrame to dictionary with row indices as keys
        return {str(idx): {str(col): float(val) if pd.notnull(val) else None 
                          for col, val in row.items()}
                for idx, row in df.iterrows()}
    return None


def get_yfinance_eps_revisions(ticker_name: str) -> Optional[Dict]:
    """
    Get EPS revisions.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with EPS revisions or None
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.eps_revisions
    if df is not None:
        # Convert DataFrame to dictionary with row indices as keys
        return {str(idx): {str(col): float(val) if pd.notnull(val) else None 
                          for col, val in row.items()}
                for idx, row in df.iterrows()}
    return None


def get_yfinance_growth_estimates(ticker_name: str) -> Optional[Dict]:
    """
    Get growth estimates.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        Dictionary with growth estimates or None
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.growth_estimates
    if df is not None:
        # Convert DataFrame to dictionary with row indices as keys
        return {str(idx): {str(col): float(val) if pd.notnull(val) else None 
                          for col, val in row.items()}
                for idx, row in df.iterrows()}
    return None


def get_yfinance_stock_history(ticker_name: str, period: str = "1y", interval: str = "1d") -> Dict:
    """
    Get historical stock price data (OHLCV).
    
    Args:
        ticker_name: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
    Returns:
        Dictionary with historical OHLCV data. Empty dict if no data.
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    df = ticker.history(period=period, interval=interval)
    
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return {}
    
    # Required columns for OHLCV data
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    # Check if all required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return {}

    # Extract only the required columns
    df_selected = df[required_columns]

    # Convert the data to a dictionary format with dates as keys
    result = {}
    for idx, row in df_selected.iterrows():
        date_str = str(idx)
        result[date_str] = {
            'Open': float(row['Open']) if pd.notnull(row['Open']) else None,
            'High': float(row['High']) if pd.notnull(row['High']) else None,
            'Low': float(row['Low']) if pd.notnull(row['Low']) else None,
            'Close': float(row['Close']) if pd.notnull(row['Close']) else None,
            'Volume': float(row['Volume']) if pd.notnull(row['Volume']) else None
        }
    return result


def get_yfinance_ticker_news(ticker_name: str) -> list:
    """
    Get latest news for a stock.
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        List of news items. Empty list if no data.
    """
    ticker = yf.Ticker(get_ticker_format(ticker_name))
    news = ticker.news
    return list(news) if news else []


def get_yfinance_ticker_filings(ticker_name: str) -> list:
    """
    Get SEC filings for a stock (US stocks only).
    
    Args:
        ticker_name: Stock ticker symbol
        
    Returns:
        List of SEC filings or empty list for non-US stocks
    """
    if get_ticker_country(ticker_name) == "US":
        ticker = yf.Ticker(get_ticker_format(ticker_name))
        filings = getattr(ticker, 'sec_filings', None)
        return list(filings) if filings else []
    else:
        # TODO: Implement this for Indian and other markets
        return []


def get_yfinance_market_summary_crypto() -> Dict:
    """
    Get cryptocurrency market summary.
    
    Returns:
        Dictionary with crypto market data
    """
    summary_url = "https://query1.finance.yahoo.com/v7/finance/quote?"
    summary_fields = [
        "shortName", "regularMarketPrice", "regularMarketChange", 
        "regularMarketChangePercent", "currency", "fromCurrency", "toCurrency",
        "exchangeTimezoneName", "exchangeTimezoneShortName", "gmtOffSetMilliseconds",
        "regularMarketTime", "preMarketTime", "postMarketTime", 
        "extendedMarketTime", "overnightMarketTime"
    ]
    symbols = ["BNB-USD", "BTC-USD", "DOGE-USD", "ETH-USD", "SOL-USD", "USDC-USD", "USDT-USD", "XRP-USD"]
    summary_params = {
        "fields": ",".join(summary_fields),
        "formatted": False,
        "lang": "en-US",
        "market": "CRYPTOCURRENCIES",
        "symbols": ",".join(symbols)
    }
    
    summary = yf.Market("CRYPTOCURRENCIES")._fetch_json(summary_url, summary_params)
    return summary if summary is not None else {}


def get_yfinance_market_summary_us() -> Dict:
    """
    Get US market summary.
    
    Returns:
        Dictionary with US market data. Empty dict if no data.
    """
    markets = yf.Market("US")
    summary = getattr(markets, 'summary', None)
    return summary if summary is not None else {}


def get_yfinance_market_summary_asia() -> Dict:
    """
    Get Asian market summary.
    
    Returns:
        Dictionary with Asian market data. Empty dict if no data.
    """
    markets = yf.Market("ASIA")
    summary = getattr(markets, 'summary', None)
    return summary if summary is not None else {}


def get_yfinance_market_summary_europe() -> Dict:
    """
    Get European market summary.
    
    Returns:
        Dictionary with European market data. Empty dict if no data.
    """
    markets = yf.Market("EUROPE")
    summary = getattr(markets, 'summary', None)
    return summary if summary is not None else {}


def get_yfinance_market_summary_currency() -> Dict:
    """
    Get currency market summary.
    
    Returns:
        Dictionary with currency market data. Empty dict if no data.
    """
    markets = yf.Market("CURRENCIES")
    summary = getattr(markets, 'summary', None)
    return summary if summary is not None else {}


def get_yfinance_market_summary_commodities() -> Dict:
    """
    Get commodities market summary.
    
    Returns:
        Dictionary with commodities market data. Empty dict if no data.
    """
    markets = yf.Market("COMMODITIES")
    summary = getattr(markets, 'summary', None)
    return summary if summary is not None else {}
