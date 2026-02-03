"""
Anthropic Claude provider implementation for InvestorMate.
"""

from typing import Dict, Optional
import anthropic

from .base_provider import AIProvider
from .response_parser import sanitize_and_parse_response, format_error_response
from ..utils.exceptions import AIProviderError
from ..utils.validators import validate_api_key


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model name (default: claude-3-5-sonnet-20241022)
        """
        api_key = validate_api_key(api_key, "Anthropic")
        super().__init__(api_key, model or "claude-3-5-sonnet-20241022")
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def analyze(self, data: str, prompt: str, system_prompt: Optional[str] = None) -> Dict:
        """
        Analyze data with Anthropic Claude.
        
        Args:
            data: Data to analyze
            prompt: User prompt/question
            system_prompt: System prompt (optional)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Combine data and user query
            user_message = f"{data}\n\n{prompt}"
            
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt if system_prompt else "You are a helpful financial analyst assistant.",
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extract response text
            response_text = response.content[0].text
            
            # Parse and return
            return sanitize_and_parse_response(response_text)
            
        except anthropic.AuthenticationError:
            raise AIProviderError("Invalid Anthropic API key")
        except anthropic.RateLimitError:
            raise AIProviderError("Anthropic rate limit exceeded")
        except anthropic.APIError as e:
            raise AIProviderError(f"Anthropic API error: {str(e)}")
        except Exception as e:
            return format_error_response(f"Anthropic request failed: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """
        Validate Anthropic API key.
        
        Returns:
            True if API key is valid
        """
        try:
            # Try a minimal API call
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "Anthropic"
