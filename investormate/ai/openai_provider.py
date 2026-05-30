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

    def __init__(self, api_key: str, model: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o)
            **kwargs: Generation/retry options forwarded to
                :class:`~investormate.ai.base_provider.AIProvider`
                (``temperature``, ``max_tokens``, ``timeout``, ``max_retries``,
                ``retry_backoff``).
        """
        api_key = validate_api_key(api_key, "OpenAI")
        super().__init__(api_key, model or "gpt-4o", **kwargs)
        self.client = openai.OpenAI(api_key=self.api_key, timeout=self.timeout)

    def analyze(
        self, data: str, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict:
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

            # Build request kwargs, only including optional params when set
            request_kwargs = {"model": self.model, "messages": messages}
            if self.temperature is not None:
                request_kwargs["temperature"] = self.temperature
            if self.max_tokens is not None:
                request_kwargs["max_tokens"] = self.max_tokens

            # Call OpenAI API with retry on transient errors
            response = self._retry_call(
                lambda: self.client.chat.completions.create(**request_kwargs),
                retryable=(
                    openai.RateLimitError,
                    openai.APITimeoutError,
                    openai.APIConnectionError,
                ),
            )

            # Extract response text
            response_text = response.choices[0].message.content

            # Parse and return
            return sanitize_and_parse_response(response_text)

        except openai.AuthenticationError:
            raise AIProviderError(f"Invalid {self.provider_name} API key")
        except openai.RateLimitError:
            raise AIProviderError(f"{self.provider_name} rate limit exceeded")
        except openai.APIError as e:
            raise AIProviderError(f"{self.provider_name} API error: {str(e)}")
        except Exception as e:
            return format_error_response(
                f"{self.provider_name} request failed: {str(e)}"
            )

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
        except Exception:
            return False

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "OpenAI"
