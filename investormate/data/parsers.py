"""
Data parsing and normalization utilities for InvestorMate.
Ensures all data is JSON-serializable and handles edge cases.
"""

from typing import Any, Dict, Optional
import pandas as pd
from datetime import datetime


def normalize_value(value: Any) -> Optional[Any]:
    """
    Normalize a single value to be JSON-serializable.
    
    Args:
        value: Any value from yfinance
        
    Returns:
        JSON-serializable value or None
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
    if isinstance(value, (int, float, str, bool)):
        # Handle NaN and infinity
        if isinstance(value, float):
            if pd.isna(value):
                return None
            if value == float('inf') or value == float('-inf'):
                return None
        return value
    
    if isinstance(value, dict):
        return normalize_dict(value)
    
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    
    # Convert other types to string
    return str(value)


def normalize_dict(data: Dict) -> Dict:
    """
    Normalize a dictionary to be JSON-serializable.
    
    Args:
        data: Dictionary with potentially non-serializable values
        
    Returns:
        JSON-serializable dictionary
    """
    result = {}
    for key, value in data.items():
        # Ensure key is a string
        str_key = str(key)
        result[str_key] = normalize_value(value)
    return result


def safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """
    Safely convert value to int.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Int value or default
    """
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    Safely convert value to string.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        String value or default
    """
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        return str(value)
    except (ValueError, TypeError):
        return default


def parse_financial_statement(df: pd.DataFrame) -> Dict:
    """
    Parse a financial statement DataFrame to JSON-serializable dict.
    
    Args:
        df: Financial statement DataFrame from yfinance
        
    Returns:
        Dictionary with period -> metrics mapping
    """
    result = {}
    for col in df.columns:
        # Convert column name to string (usually a date)
        if isinstance(col, pd.Timestamp):
            col_str = col.strftime('%Y-%m-%d')
        else:
            col_str = str(col)
        
        # Convert each row's index to string and store values
        result[col_str] = {
            str(idx): safe_float(val) 
            for idx, val in df[col].items()
        }
    return result


def extract_price_data(info: Dict) -> Dict:
    """
    Extract key price information from stock info dict.
    
    Args:
        info: Stock info dictionary from yfinance
        
    Returns:
        Dictionary with normalized price data
    """
    return {
        'current_price': safe_float(info.get('currentPrice') or info.get('regularMarketPrice')),
        'previous_close': safe_float(info.get('previousClose')),
        'open': safe_float(info.get('open') or info.get('regularMarketOpen')),
        'day_high': safe_float(info.get('dayHigh') or info.get('regularMarketDayHigh')),
        'day_low': safe_float(info.get('dayLow') or info.get('regularMarketDayLow')),
        'volume': safe_int(info.get('volume') or info.get('regularMarketVolume')),
        'market_cap': safe_float(info.get('marketCap')),
    }


def extract_company_info(info: Dict) -> Dict:
    """
    Extract company information from stock info dict.
    
    Args:
        info: Stock info dictionary from yfinance
        
    Returns:
        Dictionary with company information
    """
    return {
        'name': safe_str(info.get('shortName') or info.get('longName')),
        'sector': safe_str(info.get('sector')),
        'industry': safe_str(info.get('industry')),
        'country': safe_str(info.get('country')),
        'website': safe_str(info.get('website')),
        'description': safe_str(info.get('longBusinessSummary')),
        'employees': safe_int(info.get('fullTimeEmployees')),
    }
