"""
Tests for sentiment analysis module.
"""

import pytest
from unittest.mock import Mock, patch
from investormate.analysis.sentiment import SentimentAnalyzer, SENTIMENT_ANALYSIS_PROMPT
from investormate.utils.exceptions import AIProviderError


class TestSentimentAnalyzer:
    """Test cases for SentimentAnalyzer class."""

    def test_initialization(self):
        """Test valid initialization."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        assert analyzer.ticker == "AAPL"
        assert analyzer._news_fetcher == mock_news

    def test_initialization_with_ai_provider(self):
        """Test initialization with custom AI provider."""
        mock_news = Mock(return_value=[])
        mock_provider = Mock()
        analyzer = SentimentAnalyzer("AAPL", mock_news, ai_provider=mock_provider)
        assert analyzer._ai_provider == mock_provider

    def test_format_news_for_analysis_empty(self):
        """Test formatting empty news list."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        result = analyzer._format_news_for_analysis([])
        assert "No recent news" in result

    def test_format_news_for_analysis_with_articles(self):
        """Test formatting news articles."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        articles = [
            {"title": "Apple reports strong earnings", "summary": "Q4 beat", "publisher": "Reuters"},
            {"title": "AAPL stock rises", "summary": "", "publisher": "Bloomberg"},
        ]
        result = analyzer._format_news_for_analysis(articles)
        assert "Apple reports strong earnings" in result
        assert "Reuters" in result
        assert "Bloomberg" in result

    def test_parse_ai_response_valid_json(self):
        """Test parsing valid JSON response."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        response = '''
        Here is the analysis:
        {
            "overall_score": 0.75,
            "sentiment_distribution": {"bullish": 70, "bearish": 15, "neutral": 15},
            "bullish_signals": ["growth", "innovation"],
            "bearish_signals": ["concern"],
            "summary": "Overall positive sentiment"
        }
        '''
        result = analyzer._parse_ai_response(response)
        assert result["score"] == 0.75
        assert result["bullish_percent"] == 70
        assert result["bearish_percent"] == 15
        assert result["neutral_percent"] == 15
        assert "growth" in result["bullish_signals"]
        assert result["summary"] == "Overall positive sentiment"

    def test_parse_ai_response_fallback(self):
        """Test fallback parsing when JSON fails."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        response = "The sentiment is bullish and positive with strong growth signals."
        result = analyzer._parse_ai_response(response)
        assert "score" in result
        assert "bullish_percent" in result
        assert "summary" in result

    def test_get_sentiment_label(self):
        """Test sentiment label conversion."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        assert analyzer.get_sentiment_label(0.8) == "Very Bullish"
        assert analyzer.get_sentiment_label(0.3) == "Bullish"
        assert analyzer.get_sentiment_label(0.0) == "Neutral"
        assert analyzer.get_sentiment_label(-0.3) == "Bearish"
        assert analyzer.get_sentiment_label(-0.8) == "Very Bearish"

    @patch.object(SentimentAnalyzer, "_get_ai_provider")
    def test_news_empty_articles(self, mock_get_provider):
        """Test news() with no articles returns default structure."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        result = analyzer.news(days=7)
        assert result["score"] == 0.0
        assert result["article_count"] == 0
        assert "No recent news" in result["summary"]
        mock_get_provider.assert_not_called()

    @patch.object(SentimentAnalyzer, "_get_ai_provider")
    def test_news_with_articles(self, mock_get_provider):
        """Test news() with articles calls AI provider."""
        mock_news = Mock(return_value=[
            {"title": "Test", "summary": "Test", "publisher": "Test"}
        ])
        mock_provider = Mock()
        mock_provider.analyze.return_value = {
            "answer": '{"overall_score": 0.5, "sentiment_distribution": {"bullish": 50, "bearish": 25, "neutral": 25}, "bullish_signals": [], "bearish_signals": [], "summary": "Mixed"}'
        }
        mock_get_provider.return_value = mock_provider

        analyzer = SentimentAnalyzer("AAPL", mock_news, ai_provider=mock_provider)
        result = analyzer.news(days=7)

        assert result["score"] == 0.5
        assert result["article_count"] == 1
        mock_provider.analyze.assert_called_once()

    def test_compare_sentiment(self):
        """Test compare_sentiment across timeframes."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        with patch.object(analyzer, "news", return_value={"score": 0.5, "article_count": 5}):
            results = analyzer.compare_sentiment([1, 7, 30])
            assert 1 in results
            assert 7 in results
            assert 30 in results
            assert results[7]["score"] == 0.5

    def test_repr(self):
        """Test string representation."""
        mock_news = Mock(return_value=[])
        analyzer = SentimentAnalyzer("AAPL", mock_news)
        repr_str = repr(analyzer)
        assert "SentimentAnalyzer" in repr_str
        assert "AAPL" in repr_str
