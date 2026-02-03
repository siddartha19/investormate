"""
Document extraction utilities for InvestorMate.
Support for PDF, CSV, TXT, JSON, and web content extraction.
"""

import base64
import io
import os
from typing import Tuple, Optional
import pandas as pd
import pypdf
import requests
from bs4 import BeautifulSoup

from ..utils.exceptions import DocumentProcessingError


def extract_data_from_file(file_extension: str, data: bytes) -> str:
    """
    Extract text data from various file formats.
    
    Args:
        file_extension: File extension (.pdf, .txt, .csv, .json)
        data: File data as bytes
        
    Returns:
        Extracted text content
        
    Raises:
        DocumentProcessingError: If extraction fails
    """
    try:
        text = ""
        
        if file_extension in [".pdf", "pdf"]:
            file_data_bytes = io.BytesIO(data)
            pdf_file = pypdf.PdfReader(file_data_bytes)
            text = ""
            for page_num in range(len(pdf_file.pages)):
                page = pdf_file.pages[page_num]
                text += page.extract_text()
                
        elif file_extension in [".txt", ".plain", "txt", "plain"]:
            text = data.decode('utf-8', errors='ignore')
            
        elif file_extension in [".json", "json"]:
            if isinstance(data, bytes):
                text = data.decode('utf-8', errors='ignore')
            else:
                text = str(data)
                
        elif file_extension in [".csv", "csv"]:
            data_str = data.decode("utf-8", errors='ignore')
            df = pd.read_csv(io.StringIO(data_str))
            # Limit to first 100 rows to avoid huge payloads
            text = df.head(100).to_json()
        else:
            raise DocumentProcessingError(f"Unsupported file extension: {file_extension}")
        
        return text
        
    except Exception as e:
        raise DocumentProcessingError(f"Failed to extract data from file: {str(e)}")


def extract_article_content(url: str, max_length: int = 10000) -> Tuple[str, str]:
    """
    Extract article content from a web URL.
    
    Args:
        url: URL to extract content from
        max_length: Maximum content length to return
        
    Returns:
        Tuple of (title, content)
        
    Raises:
        DocumentProcessingError: If extraction fails
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the title of the article
        title_tag = soup.find("title")
        title = title_tag.get_text() if title_tag else "No Title"

        # Find the main content of the article
        # Try article tag first
        article_content = soup.find("article")
        if article_content:
            article_text = article_content.get_text(separator="\n")
            return title.strip(), article_text.strip()[:max_length]
        
        # Fall back to body
        body_content = soup.find("body")
        if body_content:
            body_text = body_content.get_text(separator="\n")
            return title.strip(), body_text.strip()[:max_length]
        
        return title.strip(), "Main content not found."
        
    except requests.RequestException as e:
        raise DocumentProcessingError(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise DocumentProcessingError(f"Failed to extract article content: {str(e)}")


def get_file_data_from_url(file_url: str, max_length: int = 5000) -> Tuple[str, str]:
    """
    Download file from URL and extract its content.
    
    Args:
        file_url: URL of the file
        max_length: Maximum content length to return
        
    Returns:
        Tuple of (extracted_text, file_extension)
        
    Raises:
        DocumentProcessingError: If download or extraction fails
    """
    try:
        file_extension = get_file_extension(file_url)
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()
        
        text = extract_data_from_file(file_extension, response.content)
        return text[:max_length], file_extension
        
    except requests.RequestException as e:
        raise DocumentProcessingError(f"Failed to download file: {str(e)}")
    except Exception as e:
        raise DocumentProcessingError(f"Failed to extract file data: {str(e)}")


def get_file_extension(url: str) -> str:
    """
    Get file extension from URL.
    
    Args:
        url: URL or file path
        
    Returns:
        File extension (e.g., '.pdf', '.csv')
    """
    _, file_extension = os.path.splitext(url.split('?')[0])  # Remove query params
    return file_extension.lower()


def sanitize_base64_document(base64_document: bytes) -> str:
    """
    Sanitize base64-encoded document.
    
    Args:
        base64_document: Base64-encoded document bytes
        
    Returns:
        Sanitized base64 string
    """
    try:
        base64_encoded_str = base64.encodebytes(base64_document).decode()
        
        # Remove data URI prefix if present
        if "," in base64_encoded_str:
            # Format: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD"
            return base64_encoded_str.split(",")[1]
        
        return base64_encoded_str
        
    except Exception as e:
        raise DocumentProcessingError(f"Failed to sanitize base64 document: {str(e)}")


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: String to check
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        import validators
        return validators.url(url) is True
    except Exception:
        # Fallback to simple check
        return url.startswith('http://') or url.startswith('https://')
