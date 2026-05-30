"""
OpenRouter provider implementation for InvestorMate.

OpenRouter (https://openrouter.ai) is an OpenAI-compatible gateway that routes
requests to many underlying models (OpenAI, Anthropic, Google, Meta, Mistral,
and more) behind a single API key. Because the wire format matches OpenAI, this
provider reuses :class:`~investormate.ai.openai_provider.OpenAIProvider` for the
request/response handling and only swaps the base URL, default model, and the
optional OpenRouter ranking headers.
"""

from typing import Optional

import openai

from .base_provider import AIProvider
from .openai_provider import OpenAIProvider
from ..utils.validators import validate_api_key

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o"


class OpenRouterProvider(OpenAIProvider):
    """
    OpenRouter provider (OpenAI-compatible access to many models).

    Models use OpenRouter's ``vendor/model`` slug format, e.g. ``openai/gpt-4o``,
    ``anthropic/claude-3.5-sonnet``, ``google/gemini-pro-1.5``,
    ``meta-llama/llama-3.1-70b-instruct``.
    """

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        *,
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
        base_url: str = OPENROUTER_BASE_URL,
        **kwargs,
    ):
        """
        Initialize the OpenRouter provider.

        Args:
            api_key: OpenRouter API key (starts with ``sk-or-``).
            model: OpenRouter model slug (default: ``openai/gpt-4o``).
            site_url: Optional site URL sent as the ``HTTP-Referer`` header for
                OpenRouter app rankings/leaderboards.
            site_name: Optional site name sent as the ``X-Title`` header.
            base_url: Override the OpenRouter API base URL.
            **kwargs: Generation/retry options forwarded to
                :class:`~investormate.ai.base_provider.AIProvider`
                (``temperature``, ``max_tokens``, ``timeout``, ``max_retries``,
                ``retry_backoff``).
        """
        api_key = validate_api_key(api_key, "OpenRouter")
        # Initialize the shared base directly; we intentionally skip
        # OpenAIProvider.__init__ because it hardwires the OpenAI base URL.
        AIProvider.__init__(self, api_key, model or DEFAULT_OPENROUTER_MODEL, **kwargs)

        default_headers = {}
        if site_url:
            default_headers["HTTP-Referer"] = site_url
        if site_name:
            default_headers["X-Title"] = site_name

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=base_url,
            timeout=self.timeout,
            default_headers=default_headers or None,
        )

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "OpenRouter"
