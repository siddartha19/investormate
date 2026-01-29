"""
Base class for AI providers in InvestorMate.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize AI provider.
        
        Args:
            api_key: API key for the provider
            model: Model name to use (provider-specific)
        """
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    def analyze(self, data: str, prompt: str, system_prompt: Optional[str] = None) -> Dict:
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
