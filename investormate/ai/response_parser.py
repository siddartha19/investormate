"""
Response parsing and sanitization for AI providers in InvestorMate.
"""

import json
import re
from typing import Dict, Any, Optional

from ..utils.exceptions import AIProviderError


def sanitize_and_parse_response(response_text: str) -> Dict:
    """
    Sanitize and parse AI response to structured format.
    
    Args:
        response_text: Raw response text from AI
        
    Returns:
        Structured response dictionary
    """
    if not response_text:
        return {"answer": "Failed to generate response", "graph_data": None}
    
    # Try to parse as JSON
    try:
        # Try direct JSON parse
        parsed = json.loads(response_text)
        if isinstance(parsed, dict):
            return normalize_response(parsed)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if isinstance(parsed, dict):
                return normalize_response(parsed)
        except json.JSONDecodeError:
            pass
    
    # Try to find any JSON object in the text
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            if isinstance(parsed, dict):
                return normalize_response(parsed)
        except json.JSONDecodeError:
            pass
    
    # If no JSON found, return the text as answer
    return {
        "answer": response_text,
        "graph_data": None
    }


def normalize_response(response: Dict) -> Dict:
    """
    Normalize response to standard format.
    
    Args:
        response: Parsed response dictionary
        
    Returns:
        Normalized response
    """
    normalized = {
        "answer": response.get("answer", ""),
        "graph_data": response.get("graph_data"),
    }
    
    # Add any extra fields that might be useful
    if "comparison_table" in response:
        normalized["comparison_table"] = response["comparison_table"]
    
    if "recommendation" in response:
        normalized["recommendation"] = response["recommendation"]
    
    return normalized


def extract_answer(response: Dict) -> str:
    """
    Extract answer text from response.
    
    Args:
        response: Response dictionary
        
    Returns:
        Answer text
    """
    return response.get("answer", "No answer provided")


def extract_chart_data(response: Dict) -> Optional[Dict]:
    """
    Extract chart data from response.
    
    Args:
        response: Response dictionary
        
    Returns:
        Chart data or None
    """
    return response.get("graph_data")


def validate_chart_data(chart_data: Any) -> bool:
    """
    Validate chart data structure.
    
    Args:
        chart_data: Chart data to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not chart_data or not isinstance(chart_data, dict):
        return False
    
    # Check for at least one chart type
    valid_charts = ["bar_chart", "pie_chart", "line_chart"]
    has_chart = any(chart in chart_data for chart in valid_charts)
    
    return has_chart


def format_error_response(error_message: str) -> Dict:
    """
    Format error as response.
    
    Args:
        error_message: Error message
        
    Returns:
        Error response dictionary
    """
    return {
        "answer": f"Error: {error_message}",
        "graph_data": None,
        "error": True
    }
