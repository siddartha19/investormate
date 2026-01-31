# Sentiment Analysis

AI-powered news sentiment analysis for stocks using OpenAI, Anthropic Claude, or Google Gemini.

## Overview

The Sentiment Analyzer analyzes news articles about a stock and extracts:
- **Sentiment score** (-1 to 1, bearish to bullish)
- **Bullish/bearish percentages**
- **Key signals** (positive and negative themes)
- **Summary** of overall sentiment

## Quick Start

```python
from investormate import Stock

stock = Stock("AAPL")
sentiment = stock.sentiment.news(days=7)

print(f"Score: {sentiment['score']}")
print(f"Bullish: {sentiment['bullish_percent']}%")
print(f"Summary: {sentiment['summary']}")
```

## Requirements

- **AI Provider API Key**: Set one of `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY`
- Internet connection for news data

## API Reference

### Stock.sentiment

Property that returns a `SentimentAnalyzer` instance.

### SentimentAnalyzer.news(days=7, use_cache=True)

Analyze news sentiment.

**Returns:**
- `score` - Overall sentiment (-1 to 1)
- `bullish_percent` - % of bullish articles
- `bearish_percent` - % of bearish articles
- `neutral_percent` - % of neutral articles
- `article_count` - Number of articles analyzed
- `bullish_signals` - List of positive themes
- `bearish_signals` - List of negative themes
- `summary` - Brief sentiment summary

### SentimentAnalyzer.get_sentiment_label(score)

Convert score to label: "Very Bullish", "Bullish", "Neutral", "Bearish", "Very Bearish"

### SentimentAnalyzer.compare_sentiment(days_list)

Compare sentiment across timeframes (e.g., [1, 7, 30] days).

## Examples

See `examples/sentiment_tracking.py` for comprehensive examples.
