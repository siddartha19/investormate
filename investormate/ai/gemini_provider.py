"""
Google Gemini provider implementation for InvestorMate.
"""

from typing import Dict, Optional
from google import genai
from google.genai import types

from .base_provider import AIProvider
from .response_parser import sanitize_and_parse_response, format_error_response
from ..utils.exceptions import AIProviderError
from ..utils.validators import validate_api_key


class GeminiProvider(AIProvider):
    """Google Gemini provider."""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key
            model: Model name (default: gemini-1.5-pro)
        """
        api_key = validate_api_key(api_key, "Google Gemini")
        super().__init__(api_key, model or "gemini-1.5-pro")
        self.client = genai.Client(api_key=self.api_key)
    
    def analyze(self, data: str, prompt: str, system_prompt: Optional[str] = None) -> Dict:
        """
        Analyze data with Google Gemini.
        
        Args:
            data: Data to analyze
            prompt: User prompt/question
            system_prompt: System prompt (optional)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Combine system prompt, data, and user query
            full_prompt = ""
            if system_prompt:
                full_prompt += f"{system_prompt}\n\n"
            full_prompt += f"{data}\n\n{prompt}"
            
            # Call Gemini API
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            
            # Extract response text
            response_text = response.text
            
            # Parse and return
            return sanitize_and_parse_response(response_text)
            
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "authentication" in error_msg.lower():
                raise AIProviderError("Invalid Google Gemini API key")
            elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
                raise AIProviderError("Google Gemini rate limit exceeded")
            else:
                return format_error_response(f"Gemini request failed: {error_msg}")
    
    def validate_api_key(self) -> bool:
        """
        Validate Google Gemini API key.
        
        Returns:
            True if API key is valid
        """
        try:
            # Try a minimal API call
            self.client.models.generate_content(
                model=self.model,
                contents="Hi"
            )
            return True
        except:
            return False
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "Google Gemini"
