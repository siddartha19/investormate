"""
Pytest configuration and fixtures for InvestorMate tests.
"""

import pytest


@pytest.fixture
def sample_ticker():
    """Sample ticker for testing."""
    return "AAPL"


@pytest.fixture
def sample_stock_info():
    """Sample stock info data."""
    return {
        'symbol': 'AAPL',
        'shortName': 'Apple Inc.',
        'currentPrice': 150.0,
        'marketCap': 2500000000000,
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'trailingPE': 25.0,
        'priceToBook': 40.0,
        'returnOnEquity': 0.45,
        'debtToEquity': 150.0,
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "answer": "Test analysis answer",
        "graph_data": None
    }
