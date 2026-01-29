"""
Document processing utilities for InvestorMate.
Text cleaning, normalization, and formatting.
"""

import re
from typing import Optional


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


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Trim
    text = text.strip()
    
    return text


def extract_numbers(text: str) -> list:
    """
    Extract numbers from text.
    
    Args:
        text: Text to extract from
        
    Returns:
        List of numbers found
    """
    # Match integers and floats
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    
    return [float(m) for m in matches if m]


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Text to process
        
    Returns:
        Text with URLs removed
    """
    # Remove URLs
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    text = re.sub(pattern, '', text)
    
    return text


def extract_sentences(text: str, max_sentences: Optional[int] = None) -> list:
    """
    Extract sentences from text.
    
    Args:
        text: Text to extract from
        max_sentences: Maximum number of sentences to return
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting (can be improved)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if max_sentences:
        sentences = sentences[:max_sentences]
    
    return sentences


def summarize_text(text: str, max_length: int = 500) -> str:
    """
    Create a simple summary by taking first N characters.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        
    Returns:
        Summarized text
    """
    text = clean_text(text)
    
    if len(text) <= max_length:
        return text
    
    # Try to break at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    
    if last_period > max_length * 0.8:  # If we're close to the end
        return truncated[:last_period + 1]
    
    return truncated + "..."


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    
    return text.strip()


def format_for_ai(text: str, max_length: int = 10000) -> str:
    """
    Format text for AI consumption.
    
    Args:
        text: Text to format
        max_length: Maximum length
        
    Returns:
        Formatted text
    """
    # Clean the text
    text = clean_text(text)
    
    # Normalize whitespace
    text = normalize_whitespace(text)
    
    # Truncate if needed
    text = truncate_text(text, max_length)
    
    return text
