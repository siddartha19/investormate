"""
Custom exceptions for InvestorMate.
"""


class InvestorMateError(Exception):
    """Base exception for InvestorMate."""
    pass


class InvalidTickerError(InvestorMateError):
    """Raised when an invalid ticker symbol is provided."""
    pass


class APIKeyError(InvestorMateError):
    """Raised when API key is missing or invalid."""
    pass


class DataFetchError(InvestorMateError):
    """Raised when data fetching fails."""
    pass


class AIProviderError(InvestorMateError):
    """Raised when AI provider encounters an error."""
    pass


class ValidationError(InvestorMateError):
    """Raised when input validation fails."""
    pass


class DocumentProcessingError(InvestorMateError):
    """Raised when document processing fails."""
    pass
