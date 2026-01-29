"""
OpenAI provider implementation for InvestorMate.
"""

from typing import Dict, Optional
import openai

from .base_provider import AIProvider
from .response_parser import sanitize_and_parse_response, format_error_response
from ..utils.exceptions import AIProviderError
from ..utils.validators import validate_api_key


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o)
        """
        api_key = validate_api_key(api_key, "OpenAI")
        super().__init__(api_key, model or "gpt-4o")
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def analyze(self, data: str, prompt: str, system_prompt: Optional[str] = None) -> Dict:
        """
        Analyze data with OpenAI GPT.
        
        Args:
            data: Data to analyze
            prompt: User prompt/question
            system_prompt: System prompt (optional)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add data and user query
            content = f"{data}\n\n{prompt}"
            messages.append({"role": "user", "content": content})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            # Parse and return
            return sanitize_and_parse_response(response_text)
            
        except openai.AuthenticationError:
            raise AIProviderError("Invalid OpenAI API key")
        except openai.RateLimitError:
            raise AIProviderError("OpenAI rate limit exceeded")
        except openai.APIError as e:
            raise AIProviderError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            return format_error_response(f"OpenAI request failed: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """
        Validate OpenAI API key.
        
        Returns:
            True if API key is valid
        """
        try:
            # Try a minimal API call
            self.client.models.list()
            return True
        except:
            return False
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "OpenAI"
