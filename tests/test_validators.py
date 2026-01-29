"""Tests for validators module."""

import pytest
from investormate.utils.validators import (
    validate_ticker,
    validate_api_key,
    validate_period,
    validate_interval,
)
from investormate.utils.exceptions import InvalidTickerError, APIKeyError, ValidationError


def test_validate_ticker_valid():
    """Test valid ticker validation."""
    assert validate_ticker("AAPL") == "AAPL"
    assert validate_ticker("aapl") == "AAPL"
    assert validate_ticker("BRK-B") == "BRK-B"


def test_validate_ticker_invalid():
    """Test invalid ticker validation."""
    with pytest.raises(InvalidTickerError):
        validate_ticker("")
    
    with pytest.raises(InvalidTickerError):
        validate_ticker("TOOLONGTICKER")


def test_validate_api_key_valid():
    """Test valid API key."""
    key = validate_api_key("sk-1234567890", "Test")
    assert key == "sk-1234567890"


def test_validate_api_key_invalid():
    """Test invalid API key."""
    with pytest.raises(APIKeyError):
        validate_api_key("", "Test")
    
    with pytest.raises(APIKeyError):
        validate_api_key("short", "Test")


def test_validate_period():
    """Test period validation."""
    assert validate_period("1y") == "1y"
    
    with pytest.raises(ValidationError):
        validate_period("invalid")


def test_validate_interval():
    """Test interval validation."""
    assert validate_interval("1d") == "1d"
    
    with pytest.raises(ValidationError):
        validate_interval("invalid")
