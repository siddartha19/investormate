"""
Base class for AI providers in InvestorMate.
"""

import time
from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional, Tuple, Type, TypeVar

from ..utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: float = 60.0,
        max_retries: int = 2,
        retry_backoff: float = 0.5,
    ):
        """
        Initialize AI provider.

        Args:
            api_key: API key for the provider
            model: Model name to use (provider-specific)
            temperature: Sampling temperature; ``None`` uses the provider default.
            max_tokens: Max tokens to generate; ``None`` uses the provider default.
            timeout: Per-request timeout in seconds.
            max_retries: Number of retries on transient errors (rate limits,
                timeouts, connection errors). ``0`` disables retries.
            retry_backoff: Base seconds for exponential backoff between retries.
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max(0, int(max_retries))
        self.retry_backoff = max(0.0, float(retry_backoff))

    def _retry_call(
        self,
        func: Callable[[], T],
        retryable: Tuple[Type[BaseException], ...],
    ) -> T:
        """
        Invoke ``func`` with exponential backoff on ``retryable`` exceptions.

        The final attempt re-raises the original exception so provider-specific
        handlers can translate it into an :class:`AIProviderError`.
        """
        attempt = 0
        while True:
            try:
                return func()
            except retryable as exc:
                if attempt >= self.max_retries:
                    raise
                sleep_s = self.retry_backoff * (2**attempt)
                logger.warning(
                    "%s transient error (attempt %d/%d), retrying in %.2fs: %s",
                    self.provider_name,
                    attempt + 1,
                    self.max_retries,
                    sleep_s,
                    exc,
                )
                if sleep_s > 0:
                    time.sleep(sleep_s)
                attempt += 1

    @abstractmethod
    def analyze(
        self, data: str, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict:
        """
        Analyze data with AI.

        Args:
            data: Data to analyze
            prompt: User prompt/question
            system_prompt: System prompt (optional)

        Returns:
            Dictionary with analysis results
        """
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate API key.

        Returns:
            True if API key is valid
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Get provider name.

        Returns:
            Provider name (e.g., "OpenAI", "Anthropic", "Gemini")
        """
        pass
