"""
Helper utilities for InvestorMate.
"""

from typing import Any, Dict, List, Optional
import json


def format_currency(value: Optional[float], currency: str = "USD") -> str:
    """
    Format a number as currency.
    
    Args:
        value: Number to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return "N/A"
    
    symbol = "$" if currency == "USD" else currency
    
    if abs(value) >= 1_000_000_000:
        return f"{symbol}{value / 1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"{symbol}{value / 1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{symbol}{value / 1_000:.2f}K"
    else:
        return f"{symbol}{value:.2f}"


def format_percentage(value: Optional[float], decimal_places: int = 2) -> str:
    """
    Format a number as percentage.
    
    Args:
        value: Number to format (0.15 = 15%)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    return f"{value * 100:.{decimal_places}f}%"


def safe_divide(numerator: Optional[float], denominator: Optional[float], 
                default: Optional[float] = None) -> Optional[float]:
    """
    Safely divide two numbers.
    
    Args:
        numerator: Top number
        denominator: Bottom number
        default: Default value if division fails
        
    Returns:
        Result of division or default
    """
    if numerator is None or denominator is None or denominator == 0:
        return default
    
    try:
        return numerator / denominator
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def truncate_text(text: str, max_length: int = 5000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def ensure_list(value: Any) -> List:
    """
    Ensure value is a list.
    
    Args:
        value: Value to convert
        
    Returns:
        List containing the value(s)
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def pretty_print_json(data: Any, indent: int = 2) -> str:
    """
    Pretty print data as JSON.
    
    Args:
        data: Data to print
        indent: Indentation level
        
    Returns:
        Pretty-printed JSON string
    """
    try:
        return json.dumps(data, indent=indent, default=str)
    except (ValueError, TypeError):
        return str(data)


def get_nested_value(data: Dict, keys: List[str], default: Any = None) -> Any:
    """
    Get value from nested dictionary.
    
    Args:
        data: Dictionary to search
        keys: List of keys to traverse
        default: Default value if not found
        
    Returns:
        Value or default
    """
    try:
        result = data
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError, IndexError):
        return default


def batch_items(items: List, batch_size: int = 10) -> List[List]:
    """
    Batch items into groups.
    
    Args:
        items: List of items
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
