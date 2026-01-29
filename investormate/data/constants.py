"""
Constants and ticker utilities for InvestorMate.

For v0.1.0, we support major Indian stocks (NSE-listed) and US stocks.
Indian tickers get the .NS suffix, US tickers are used as-is.
"""

# Sample of major Indian stocks (NSE)
# Users can use any ticker - this list is for reference/validation
MAJOR_INDIAN_TICKERS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HDFC", "ITC",
    "SBIN", "BHARTIARTL", "KOTAKBANK", "LT", "HINDUNILVR", "AXISBANK",
    "ASIANPAINT", "MARUTI", "BAJFINANCE", "TITAN", "WIPRO", "ULTRACEMCO",
    "NESTLEIND", "HCLTECH", "POWERGRID", "NTPC", "BAJAJFINSV", "ADANIPORTS",
    "ONGC", "COALINDIA", "SUNPHARMA", "M&M", "TECHM", "TATASTEEL", "INDUSINDBK",
    "GRASIM", "JSWSTEEL", "HINDALCO", "SHREECEM", "BRITANNIA", "DRREDDY",
    "ADANIENT", "DIVISLAB", "EICHERMOT", "CIPLA", "APOLLOHOSP", "HEROMOTOCO",
    "BAJAJ-AUTO", "TATAMOTORS", "UPL", "ADANIGREEN", "ADANITRANS"
]

# Sample of major US stocks
MAJOR_US_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "UNH", "JNJ", "V", "WMT", "JPM", "MA", "PG", "XOM", "HD", "CVX",
    "ABBV", "MRK", "KO", "PEP", "COST", "AVGO", "LLY", "TMO", "MCD",
    "CSCO", "ACN", "ABT", "DHR", "NKE", "VZ", "ADBE", "TXN", "NEE",
    "CRM", "ORCL", "PM", "DIS", "INTC", "NFLX", "AMD", "QCOM", "CMCSA",
    "UPS", "HON", "T", "IBM", "AMGN", "RTX"
]


def get_ticker_format(ticker: str) -> str:
    """
    Format ticker symbol for yfinance.
    
    Indian (NSE) stocks get .NS suffix, US stocks remain as-is.
    If ticker is in MAJOR_INDIAN_TICKERS list, it's treated as Indian.
    Otherwise, it's treated as US ticker.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Formatted ticker for yfinance (e.g., "RELIANCE" -> "RELIANCE.NS", "AAPL" -> "AAPL")
    """
    # Check if it's a known Indian ticker
    if ticker.upper() in MAJOR_INDIAN_TICKERS:
        return f"{ticker}.NS"
    
    # Check if ticker already has a suffix (.NS, .BO, etc.)
    if "." in ticker:
        return ticker
    
    # Default to US ticker (no suffix)
    return ticker


def get_ticker_country(ticker: str) -> str:
    """
    Determine the country/market for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Country code ("IN" for India, "US" for United States)
    """
    # Check if it's a known Indian ticker
    if ticker.upper() in MAJOR_INDIAN_TICKERS:
        return "IN"
    
    # Check if ticker has .NS or .BO suffix
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        return "IN"
    
    # Default to US
    return "US"


def is_valid_ticker(ticker: str) -> bool:
    """
    Basic ticker validation.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if ticker appears valid, False otherwise
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Basic checks
    ticker = ticker.strip()
    if len(ticker) < 1 or len(ticker) > 10:
        return False
    
    # Should be alphanumeric with possible dash, dot, or ampersand
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._&")
    return all(c.upper() in allowed_chars for c in ticker)
