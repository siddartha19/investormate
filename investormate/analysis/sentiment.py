"""
Sentiment analysis for stock news using AI providers.
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta

from ..ai.base_provider import AIProvider
from ..utils.exceptions import AIProviderError


# Sentiment analysis prompt template
SENTIMENT_ANALYSIS_PROMPT = """Analyze the sentiment of the following news articles about {ticker}.

For each article, determine if it's BULLISH (positive), BEARISH (negative), or NEUTRAL.

News Articles:
{news_data}

Return a JSON object with the following structure:
{{
  "overall_score": <float between -1.0 (very bearish) and 1.0 (very bullish)>,
  "sentiment_distribution": {{
    "bullish": <percentage of bullish articles>,
    "bearish": <percentage of bearish articles>,
    "neutral": <percentage of neutral articles>
  }},
  "bullish_signals": [<list of positive keywords/themes found>],
  "bearish_signals": [<list of negative keywords/themes found>],
  "summary": "<brief 1-2 sentence summary of overall sentiment>"
}}

Focus on: earnings, revenue, growth, partnerships, competition, market conditions, regulatory issues.
"""


class SentimentAnalyzer:
    """
    Analyze news sentiment for stocks using AI providers.
    
    The SentimentAnalyzer uses AI to analyze news articles and extract
    sentiment scores, identify bullish/bearish signals, and provide
    sentiment summaries.
    
    Example:
        >>> from investormate import Stock
        >>> stock = Stock("AAPL")
        >>> sentiment = stock.sentiment.news(days=7)
        >>> print(f"Sentiment Score: {sentiment['score']}")
        >>> print(f"Bullish: {sentiment['bullish_percent']}%")
    """
    
    def __init__(self, ticker: str, news_fetcher: callable, ai_provider: Optional[AIProvider] = None):
        """
        Initialize SentimentAnalyzer.
        
        Args:
            ticker: Stock ticker symbol
            news_fetcher: Callable that returns news articles
            ai_provider: AI provider instance (optional, will use default if not provided)
        """
        self.ticker = ticker
        self._news_fetcher = news_fetcher
        self._ai_provider = ai_provider
        self._cache = {}
    
    def _get_ai_provider(self) -> AIProvider:
        """Get AI provider instance."""
        if self._ai_provider:
            return self._ai_provider
        
        # Try to create a default provider
        try:
            from ..ai.openai_provider import OpenAIProvider
            return OpenAIProvider()
        except Exception:
            pass
        
        try:
            from ..ai.anthropic_provider import AnthropicProvider
            return AnthropicProvider()
        except Exception:
            pass
        
        try:
            from ..ai.gemini_provider import GeminiProvider
            return GeminiProvider()
        except Exception:
            pass
        
        raise AIProviderError(
            "No AI provider available. Please provide an API key for OpenAI, Anthropic, or Gemini."
        )
    
    def _fetch_news(self, days: int = 7) -> List[Dict]:
        """
        Fetch news articles.
        
        Args:
            days: Number of days to look back (not used with yfinance, returns latest)
        
        Returns:
            List of news articles
        """
        try:
            news = self._news_fetcher()
            if not news:
                return []
            
            # Filter by date if possible
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_news = []
            
            for article in news:
                # Check if article has a timestamp
                if 'providerPublishTime' in article:
                    article_date = datetime.fromtimestamp(article['providerPublishTime'])
                    if article_date >= cutoff_date:
                        filtered_news.append(article)
                else:
                    # If no timestamp, include it
                    filtered_news.append(article)
            
            return filtered_news if filtered_news else news[:20]  # Limit to 20 articles
        except Exception as e:
            raise AIProviderError(f"Failed to fetch news: {str(e)}")
    
    def _format_news_for_analysis(self, news: List[Dict]) -> str:
        """
        Format news articles for AI analysis.
        
        Args:
            news: List of news articles
        
        Returns:
            Formatted string for analysis
        """
        if not news:
            return "No recent news articles found."
        
        formatted = []
        for i, article in enumerate(news[:15], 1):  # Limit to 15 articles to avoid token limits
            title = article.get('title', 'No title')
            summary = article.get('summary', '')
            publisher = article.get('publisher', 'Unknown')
            
            formatted.append(f"{i}. [{publisher}] {title}")
            if summary:
                # Truncate long summaries
                summary = summary[:200] + "..." if len(summary) > 200 else summary
                formatted.append(f"   Summary: {summary}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _parse_ai_response(self, response: str) -> Dict:
        """
        Parse AI response into structured sentiment data.
        
        Args:
            response: AI response string
        
        Returns:
            Parsed sentiment dictionary
        """
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                
                return {
                    'score': data.get('overall_score', 0.0),
                    'bullish_percent': data.get('sentiment_distribution', {}).get('bullish', 0.0),
                    'bearish_percent': data.get('sentiment_distribution', {}).get('bearish', 0.0),
                    'neutral_percent': data.get('sentiment_distribution', {}).get('neutral', 0.0),
                    'bullish_signals': data.get('bullish_signals', []),
                    'bearish_signals': data.get('bearish_signals', []),
                    'summary': data.get('summary', '')
                }
            else:
                # Fallback parsing
                return self._fallback_parse(response)
        
        except json.JSONDecodeError:
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict:
        """
        Fallback parser when JSON extraction fails.
        
        Args:
            response: AI response string
        
        Returns:
            Basic sentiment dictionary
        """
        # Simple keyword-based sentiment
        response_lower = response.lower()
        
        bullish_keywords = ['bullish', 'positive', 'strong', 'growth', 'up', 'gain', 'optimistic']
        bearish_keywords = ['bearish', 'negative', 'weak', 'decline', 'down', 'loss', 'pessimistic']
        
        bullish_count = sum(1 for word in bullish_keywords if word in response_lower)
        bearish_count = sum(1 for word in bearish_keywords if word in response_lower)
        
        total = max(bullish_count + bearish_count, 1)
        score = (bullish_count - bearish_count) / total
        
        return {
            'score': round(score, 2),
            'bullish_percent': round((bullish_count / total) * 100, 1),
            'bearish_percent': round((bearish_count / total) * 100, 1),
            'neutral_percent': 0.0,
            'bullish_signals': [],
            'bearish_signals': [],
            'summary': 'Sentiment analysis completed (fallback mode)'
        }
    
    def news(self, days: int = 7, use_cache: bool = True) -> Dict:
        """
        Analyze news sentiment for the stock.
        
        Args:
            days: Number of days of news to analyze
            use_cache: Whether to use cached results
        
        Returns:
            Dictionary with sentiment analysis:
            - score: Overall sentiment (-1 to 1, negative to positive)
            - bullish_percent: Percentage of bullish articles
            - bearish_percent: Percentage of bearish articles
            - neutral_percent: Percentage of neutral articles
            - article_count: Number of articles analyzed
            - bullish_signals: List of positive themes
            - bearish_signals: List of negative themes
            - summary: Brief sentiment summary
        
        Example:
            >>> analyzer = SentimentAnalyzer("AAPL", stock.news)
            >>> sentiment = analyzer.news(days=7)
            >>> print(f"Score: {sentiment['score']}")
            >>> print(f"Summary: {sentiment['summary']}")
        """
        cache_key = f"news_{days}"
        
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Fetch news
        news_articles = self._fetch_news(days)
        
        if not news_articles:
            return {
                'score': 0.0,
                'bullish_percent': 0.0,
                'bearish_percent': 0.0,
                'neutral_percent': 0.0,
                'article_count': 0,
                'bullish_signals': [],
                'bearish_signals': [],
                'summary': 'No recent news articles available for analysis'
            }
        
        # Format news for AI
        news_text = self._format_news_for_analysis(news_articles)
        
        # Create prompt
        prompt = SENTIMENT_ANALYSIS_PROMPT.format(
            ticker=self.ticker,
            news_data=news_text
        )
        
        # Get AI analysis
        try:
            ai_provider = self._get_ai_provider()
            response_dict = ai_provider.analyze(
                data="",  # No additional data needed
                prompt=prompt,
                system_prompt=None
            )
            # Extract the answer from the response
            response = response_dict.get('answer', str(response_dict))
            result = self._parse_ai_response(response)
        except Exception as e:
            raise AIProviderError(f"Sentiment analysis failed: {str(e)}")
        
        # Add article count
        result['article_count'] = len(news_articles)
        
        # Cache result
        if use_cache:
            self._cache[cache_key] = result
        
        return result
    
    def get_sentiment_label(self, score: float) -> str:
        """
        Convert sentiment score to human-readable label.
        
        Args:
            score: Sentiment score (-1 to 1)
        
        Returns:
            Sentiment label string
        """
        if score >= 0.5:
            return "Very Bullish"
        elif score >= 0.2:
            return "Bullish"
        elif score >= -0.2:
            return "Neutral"
        elif score >= -0.5:
            return "Bearish"
        else:
            return "Very Bearish"
    
    def compare_sentiment(self, days_list: List[int]) -> Dict[int, Dict]:
        """
        Compare sentiment across different time periods.
        
        Args:
            days_list: List of day periods to compare (e.g., [1, 7, 30])
        
        Returns:
            Dictionary mapping days to sentiment results
        
        Example:
            >>> comparison = analyzer.compare_sentiment([1, 7, 30])
            >>> print(comparison[7]['score'])  # 7-day sentiment
        """
        results = {}
        
        for days in days_list:
            results[days] = self.news(days=days)
        
        return results
    
    def __repr__(self) -> str:
        """String representation."""
        return f"SentimentAnalyzer(ticker='{self.ticker}')"
