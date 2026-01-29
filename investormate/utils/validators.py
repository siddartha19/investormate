"""
Input validation utilities for InvestorMate.
"""

from typing import Optional
from .exceptions import InvalidTickerError, APIKeyError, ValidationError


def validate_ticker(ticker: str) -> str:
    """
    Validate ticker symbol.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Uppercase ticker symbol
        
    Raises:
        InvalidTickerError: If ticker is invalid
    """
    if not ticker or not isinstance(ticker, str):
        raise InvalidTickerError("Ticker must be a non-empty string")
    
    ticker = ticker.strip().upper()
    
    if len(ticker) < 1 or len(ticker) > 10:
        raise InvalidTickerError(f"Invalid ticker length: {ticker}")
    
    # Should be alphanumeric with possible dash, dot, or ampersand
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._&")
    if not all(c in allowed_chars for c in ticker):
        raise InvalidTickerError(f"Invalid characters in ticker: {ticker}")
    
    return ticker


def validate_api_key(api_key: Optional[str], provider_name: str = "API") -> str:
    """
    Validate API key.
    
    Args:
        api_key: API key string
        provider_name: Name of the provider (for error messages)
        
    Returns:
        API key
        
    Raises:
        APIKeyError: If API key is missing or invalid
    """
    if not api_key or not isinstance(api_key, str):
        raise APIKeyError(f"{provider_name} API key is required")
    
    api_key = api_key.strip()
    
    if len(api_key) < 10:
        raise APIKeyError(f"Invalid {provider_name} API key format")
    
    return api_key


def validate_period(period: str) -> str:
    """
    Validate period parameter for historical data.
    
    Args:
        period: Time period string
        
    Returns:
        Valid period string
        
    Raises:
        ValidationError: If period is invalid
    """
    valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    
    if period not in valid_periods:
        raise ValidationError(f"Invalid period: {period}. Must be one of {valid_periods}")
    
    return period


def validate_interval(interval: str) -> str:
    """
    Validate interval parameter for historical data.
    
    Args:
        interval: Data interval string
        
    Returns:
        Valid interval string
        
    Raises:
        ValidationError: If interval is invalid
    """
    valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
    
    if interval not in valid_intervals:
        raise ValidationError(f"Invalid interval: {interval}. Must be one of {valid_intervals}")
    
    return interval


def validate_positive_number(value: float, param_name: str = "value") -> float:
    """
    Validate that a number is positive.
    
    Args:
        value: Number to validate
        param_name: Parameter name for error messages
        
    Returns:
        The validated number
        
    Raises:
        ValidationError: If number is not positive
    """
    try:
        value = float(value)
        if value <= 0:
            raise ValidationError(f"{param_name} must be positive, got {value}")
        return value
    except (ValueError, TypeError):
        raise ValidationError(f"{param_name} must be a number, got {type(value)}")
