"""
Investor class for InvestorMate.
AI-powered stock analysis using multiple providers (OpenAI, Anthropic, Gemini).
"""

from typing import Dict, List, Optional, Union
import json

# Lazy imports to avoid requiring all AI provider dependencies
from ..ai.prompts import (
    STOCK_ANALYSIS_PROMPT,
    DOCUMENT_INSIGHTS_PROMPT,
    COMPARISON_PROMPT,
    get_stock_analysis_prompt,
    get_document_analysis_prompt,
    get_comparison_prompt
)
from ..data.fetchers import get_yfinance_data
from ..documents.extractors import (
    extract_article_content,
    get_file_data_from_url,
    is_valid_url
)
from ..documents.processors import format_for_ai
from ..utils.validators import validate_ticker
from ..utils.exceptions import APIKeyError, AIProviderError


class Investor:
    """
    AI-powered stock analysis assistant.
    
    Supports multiple AI providers: OpenAI, Anthropic Claude, Google Gemini.
    
    Example:
        >>> investor = Investor(openai_api_key="sk-...")
        >>> result = investor.ask("AAPL", "Is Apple undervalued?")
        >>> print(result['answer'])
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None,
                 gemini_api_key: Optional[str] = None,
                 default_provider: str = "openai"):
        """
        Initialize Investor with AI provider(s).
        
        Args:
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
            gemini_api_key: Google Gemini API key
            default_provider: Default provider to use ("openai", "anthropic", "gemini")
        """
        self.providers = {}
        
        # Initialize providers based on available API keys
        # Lazy import to only require dependencies for providers being used
        if openai_api_key:
            from ..ai.openai_provider import OpenAIProvider
            self.providers['openai'] = OpenAIProvider(openai_api_key)
        
        if anthropic_api_key:
            from ..ai.anthropic_provider import AnthropicProvider
            self.providers['anthropic'] = AnthropicProvider(anthropic_api_key)
        
        if gemini_api_key:
            from ..ai.gemini_provider import GeminiProvider
            self.providers['gemini'] = GeminiProvider(gemini_api_key)
        
        # Validate at least one provider is available
        if not self.providers:
            raise APIKeyError(
                "At least one AI provider API key is required. "
                "Provide openai_api_key, anthropic_api_key, or gemini_api_key."
            )
        
        # Set default provider
        if default_provider in self.providers:
            self.default_provider = default_provider
        else:
            # Use first available provider
            self.default_provider = list(self.providers.keys())[0]
    
    def ask(self, ticker: str, question: str, 
            provider: Optional[str] = None) -> Dict:
        """
        Ask a question about a stock using AI.
        
        Args:
            ticker: Stock ticker symbol
            question: Question to ask about the stock
            provider: AI provider to use (default: self.default_provider)
            
        Returns:
            Dictionary with answer and optional chart data
        """
        ticker = validate_ticker(ticker)
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            raise AIProviderError(f"Provider '{provider}' not initialized")
        
        # Fetch stock data
        try:
            stock_data = get_yfinance_data(ticker)
            stock_data_str = json.dumps(stock_data, indent=2, default=str)
        except Exception as e:
            raise AIProviderError(f"Failed to fetch stock data: {str(e)}")
        
        # Prepare prompt
        user_prompt = get_stock_analysis_prompt(stock_data_str, question)
        
        # Get AI provider
        ai_provider = self.providers[provider]
        
        # Analyze
        result = ai_provider.analyze(
            data=stock_data_str,
            prompt=question,
            system_prompt=STOCK_ANALYSIS_PROMPT
        )
        
        return result
    
    def analyze_document(self, ticker: str, document_url: str, 
                        question: str, provider: Optional[str] = None) -> Dict:
        """
        Analyze a document (PDF, article, etc.) about a stock.
        
        Args:
            ticker: Stock ticker symbol
            document_url: URL of the document to analyze
            question: Question to ask about the document
            provider: AI provider to use (default: self.default_provider)
            
        Returns:
            Dictionary with answer and optional chart data
        """
        ticker = validate_ticker(ticker)
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            raise AIProviderError(f"Provider '{provider}' not initialized")
        
        # Extract document content
        try:
            if is_valid_url(document_url):
                # Check if it's a file URL or article
                if any(ext in document_url.lower() for ext in ['.pdf', '.csv', '.json', '.txt']):
                    content, _ = get_file_data_from_url(document_url)
                else:
                    # Assume it's an article
                    _, content = extract_article_content(document_url)
            else:
                raise ValueError("Invalid document URL")
            
            # Format for AI
            content = format_for_ai(content)
            
        except Exception as e:
            raise AIProviderError(f"Failed to extract document content: {str(e)}")
        
        # Prepare prompt
        user_prompt = get_document_analysis_prompt(content, question)
        
        # Get AI provider
        ai_provider = self.providers[provider]
        
        # Analyze
        result = ai_provider.analyze(
            data=content,
            prompt=question,
            system_prompt=DOCUMENT_INSIGHTS_PROMPT
        )
        
        return result
    
    def compare(self, tickers: List[str], question: str,
                provider: Optional[str] = None) -> Dict:
        """
        Compare multiple stocks using AI.
        
        Args:
            tickers: List of stock ticker symbols
            question: Question about the comparison
            provider: AI provider to use (default: self.default_provider)
            
        Returns:
            Dictionary with comparative analysis
        """
        tickers = [validate_ticker(t) for t in tickers]
        provider = provider or self.default_provider
        
        if provider not in self.providers:
            raise AIProviderError(f"Provider '{provider}' not initialized")
        
        # Fetch data for all stocks
        stocks_data = {}
        for ticker in tickers:
            try:
                stocks_data[ticker] = get_yfinance_data(ticker)
            except Exception as e:
                print(f"Warning: Failed to fetch data for {ticker}: {e}")
        
        if not stocks_data:
            raise AIProviderError("Failed to fetch data for any stocks")
        
        # Convert to JSON strings
        stocks_data_json = {
            ticker: json.dumps(data, indent=2, default=str)
            for ticker, data in stocks_data.items()
        }
        
        # Prepare prompt
        comparison_data = "\n\n".join([
            f"--- {ticker} ---\n{data}"
            for ticker, data in stocks_data_json.items()
        ])
        
        # Get AI provider
        ai_provider = self.providers[provider]
        
        # Analyze
        result = ai_provider.analyze(
            data=comparison_data,
            prompt=question,
            system_prompt=COMPARISON_PROMPT
        )
        
        return result
    
    def batch_analyze(self, queries: List[tuple],
                     provider: Optional[str] = None) -> List[Dict]:
        """
        Analyze multiple stocks with different questions.
        
        Args:
            queries: List of (ticker, question) tuples
            provider: AI provider to use (default: self.default_provider)
            
        Returns:
            List of analysis results
        """
        results = []
        for ticker, question in queries:
            try:
                result = self.ask(ticker, question, provider)
                results.append({
                    'ticker': ticker,
                    'question': question,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'ticker': ticker,
                    'question': question,
                    'error': str(e)
                })
        
        return results
    
    @property
    def available_providers(self) -> List[str]:
        """Get list of available AI providers."""
        return list(self.providers.keys())
    
    def __repr__(self) -> str:
        """String representation."""
        providers_str = ", ".join(self.available_providers)
        return f"Investor(providers=[{providers_str}], default='{self.default_provider}')"
