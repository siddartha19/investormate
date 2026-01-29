"""Tests for helpers module."""

from investormate.utils.helpers import (
    format_currency,
    format_percentage,
    safe_divide,
    truncate_text,
)


def test_format_currency():
    """Test currency formatting."""
    assert format_currency(1500000000, "USD") == "$1.50B"
    assert format_currency(5000000, "USD") == "$5.00M"
    assert format_currency(2500, "USD") == "$2.50K"
    assert format_currency(None) == "N/A"


def test_format_percentage():
    """Test percentage formatting."""
    assert format_percentage(0.15) == "15.00%"
    assert format_percentage(0.0234, 1) == "2.3%"
    assert format_percentage(None) == "N/A"


def test_safe_divide():
    """Test safe division."""
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) is None
    assert safe_divide(10, 0, default=0) == 0
    assert safe_divide(None, 5) is None


def test_truncate_text():
    """Test text truncation."""
    text = "This is a long text that needs truncation"
    truncated = truncate_text(text, 20)
    assert len(truncated) <= 20
    assert truncated.endswith("...")
    
    short_text = "Short"
    assert truncate_text(short_text, 20) == short_text
