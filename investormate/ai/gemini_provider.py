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


def _build_gemini_retryable() -> tuple:
    """
    Build the tuple of transient exceptions worth retrying.

    Server (5xx) errors are retried when the ``google.genai`` errors module is
    available; built-in network errors are always included. Auth/quota errors
    are intentionally excluded so they surface immediately.
    """
    retryable: list = [ConnectionError, TimeoutError]
    try:
        from google.genai import errors as genai_errors

        server_error = getattr(genai_errors, "ServerError", None)
        if server_error is not None:
            retryable.append(server_error)
    except Exception:  # pragma: no cover - defensive across SDK versions
        pass
    return tuple(retryable)


_GEMINI_RETRYABLE = _build_gemini_retryable()


class GeminiProvider(AIProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: str, model: Optional[str] = None, **kwargs):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google API key
            model: Model name (default: gemini-1.5-pro)
            **kwargs: Generation/retry options forwarded to
                :class:`~investormate.ai.base_provider.AIProvider`
                (``temperature``, ``max_tokens``, ``timeout``, ``max_retries``,
                ``retry_backoff``).
        """
        api_key = validate_api_key(api_key, "Google Gemini")
        super().__init__(api_key, model or "gemini-1.5-pro", **kwargs)
        self.client = genai.Client(api_key=self.api_key)

    def analyze(
        self, data: str, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict:
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

            # Apply generation config only when overrides are provided
            config = None
            config_kwargs = {}
            if self.temperature is not None:
                config_kwargs["temperature"] = self.temperature
            if self.max_tokens is not None:
                config_kwargs["max_output_tokens"] = self.max_tokens
            if config_kwargs:
                config = types.GenerateContentConfig(**config_kwargs)

            # Call Gemini API with retry on transient errors
            response = self._retry_call(
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=config,
                ),
                retryable=_GEMINI_RETRYABLE,
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
            self.client.models.generate_content(model=self.model, contents="Hi")
            return True
        except Exception:
            return False

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "Google Gemini"
