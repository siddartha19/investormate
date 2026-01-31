"""
Example: News Sentiment Analysis

This example demonstrates how to use the SentimentAnalyzer to:
1. Analyze news sentiment for individual stocks
2. Track sentiment changes over time
3. Compare sentiment across multiple stocks
4. Make trading decisions based on sentiment

Note: Requires an AI provider API key (OpenAI, Anthropic, or Gemini).
"""

from investormate import Stock


def example_basic_sentiment():
    """Example 1: Basic sentiment analysis."""
    print("=" * 70)
    print("Example 1: Basic News Sentiment Analysis")
    print("=" * 70)
    
    stock = Stock("AAPL")
    
    # Analyze recent news (last 7 days)
    sentiment = stock.sentiment.news(days=7)
    
    print(f"\nSentiment Analysis for {stock.name} ({stock.ticker})")
    print("-" * 70)
    print(f"Overall Score: {sentiment['score']:.2f} (-1 = bearish, +1 = bullish)")
    print(f"Articles Analyzed: {sentiment['article_count']}")
    print(f"\nSentiment Distribution:")
    print(f"  Bullish:  {sentiment['bullish_percent']:.1f}%")
    print(f"  Bearish:  {sentiment['bearish_percent']:.1f}%")
    print(f"  Neutral:  {sentiment['neutral_percent']:.1f}%")
    print(f"\nSummary: {sentiment['summary']}")
    
    if sentiment['bullish_signals']:
        print(f"\nBullish Signals: {', '.join(sentiment['bullish_signals'][:5])}")
    
    if sentiment['bearish_signals']:
        print(f"Bearish Signals: {', '.join(sentiment['bearish_signals'][:5])}")
    
    print()


def example_sentiment_label():
    """Example 2: Get human-readable sentiment label."""
    print("=" * 70)
    print("Example 2: Sentiment Labels")
    print("=" * 70)
    
    stock = Stock("TSLA")
    sentiment = stock.sentiment.news(days=7)
    
    label = stock.sentiment.get_sentiment_label(sentiment['score'])
    
    print(f"\n{stock.name} Sentiment:")
    print(f"  Score: {sentiment['score']:.2f}")
    print(f"  Label: {label}")
    print()


def example_compare_timeframes():
    """Example 3: Compare sentiment across different timeframes."""
    print("=" * 70)
    print("Example 3: Sentiment Over Different Timeframes")
    print("=" * 70)
    
    stock = Stock("GOOGL")
    
    # Compare 1-day, 7-day, and 30-day sentiment
    timeframes = stock.sentiment.compare_sentiment([1, 7, 30])
    
    print(f"\n{stock.name} Sentiment Comparison:")
    print("-" * 70)
    
    for days, data in sorted(timeframes.items()):
        label = stock.sentiment.get_sentiment_label(data['score'])
        print(f"\n{days}-day sentiment:")
        print(f"  Score: {data['score']:6.2f} ({label})")
        print(f"  Articles: {data['article_count']}")
        print(f"  Bullish: {data['bullish_percent']:.1f}%")
    
    print()


def example_compare_stocks():
    """Example 4: Compare sentiment across multiple stocks."""
    print("=" * 70)
    print("Example 4: Compare Sentiment Across Stocks")
    print("=" * 70)
    
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    print("\nSentiment Comparison (7-day):")
    print("-" * 70)
    print(f"{'Ticker':<10} {'Score':>8} {'Label':<15} {'Bullish%':>10} {'Articles':>10}")
    print("-" * 70)
    
    for ticker in tickers:
        try:
            stock = Stock(ticker)
            sentiment = stock.sentiment.news(days=7)
            label = stock.sentiment.get_sentiment_label(sentiment['score'])
            
            print(f"{ticker:<10} {sentiment['score']:>8.2f} {label:<15} "
                  f"{sentiment['bullish_percent']:>10.1f} {sentiment['article_count']:>10}")
        except Exception as e:
            print(f"{ticker:<10} Error: {e}")
    
    print()


def example_trading_signal():
    """Example 5: Use sentiment for trading signals."""
    print("=" * 70)
    print("Example 5: Trading Signals Based on Sentiment")
    print("=" * 70)
    
    stock = Stock("NVDA")
    sentiment = stock.sentiment.news(days=7)
    
    print(f"\n{stock.name} ({stock.ticker})")
    print(f"Current Price: ${stock.price:.2f}")
    print(f"Sentiment Score: {sentiment['score']:.2f}")
    
    # Simple trading signal logic
    if sentiment['score'] > 0.5:
        signal = "STRONG BUY"
        reason = "Very positive sentiment"
    elif sentiment['score'] > 0.2:
        signal = "BUY"
        reason = "Positive sentiment"
    elif sentiment['score'] < -0.5:
        signal = "STRONG SELL"
        reason = "Very negative sentiment"
    elif sentiment['score'] < -0.2:
        signal = "SELL"
        reason = "Negative sentiment"
    else:
        signal = "HOLD"
        reason = "Neutral sentiment"
    
    print(f"\nTrading Signal: {signal}")
    print(f"Reason: {reason}")
    print(f"Confidence: {sentiment['bullish_percent']:.1f}% bullish, "
          f"{sentiment['bearish_percent']:.1f}% bearish")
    print()


def example_sentiment_filtering():
    """Example 6: Filter stocks by positive sentiment."""
    print("=" * 70)
    print("Example 6: Filter Stocks by Positive Sentiment")
    print("=" * 70)
    
    universe = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]
    positive_stocks = []
    
    print("\nFinding stocks with positive sentiment...")
    print("-" * 70)
    
    for ticker in universe:
        try:
            stock = Stock(ticker)
            sentiment = stock.sentiment.news(days=7)
            
            if sentiment['score'] > 0.3:  # Filter for positive sentiment
                positive_stocks.append({
                    'ticker': ticker,
                    'score': sentiment['score'],
                    'bullish_pct': sentiment['bullish_percent']
                })
                print(f"✓ {ticker}: {sentiment['score']:.2f} ({sentiment['bullish_percent']:.1f}% bullish)")
            else:
                print(f"  {ticker}: {sentiment['score']:.2f} (excluded)")
        
        except Exception as e:
            print(f"  {ticker}: Error - {e}")
    
    print(f"\n{len(positive_stocks)} stocks with positive sentiment found")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("INVESTORMATE - SENTIMENT ANALYSIS EXAMPLES")
    print("=" * 70)
    print()
    
    try:
        example_basic_sentiment()
        example_sentiment_label()
        example_compare_timeframes()
        example_compare_stocks()
        example_trading_signal()
        example_sentiment_filtering()
        
        print("=" * 70)
        print("All examples completed!")
        print("=" * 70)
        print("\nKey Takeaways:")
        print("  1. Sentiment analysis helps gauge market mood")
        print("  2. Compare sentiment across timeframes for trends")
        print("  3. Use sentiment as one factor in trading decisions")
        print("  4. Combine with technical/fundamental analysis")
        print("  5. Sentiment can change quickly - monitor regularly")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Sentiment analysis requires an AI provider API key.")
        print("Set one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY")
        print()


if __name__ == "__main__":
    main()
