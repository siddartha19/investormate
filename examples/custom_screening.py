"""
Example: Custom Stock Screening Strategies

This example demonstrates how to create custom screening strategies using:
1. Function-based filtering and ranking
2. Builder pattern for common criteria
3. Combining multiple filters
"""

from investormate import CustomStrategy, Stock


def example_function_based():
    """Example 1: Function-based custom strategy."""
    print("=" * 70)
    print("Example 1: Function-Based Custom Strategy")
    print("=" * 70)
    
    # Define custom filter function
    def value_filter(stock):
        """Filter for value stocks."""
        try:
            return (
                10 < stock.ratios.pe < 25 and  # Reasonable P/E
                stock.ratios.roe > 0.15 and     # Strong ROE (15%+)
                stock.price > 10                 # Minimum price
            )
        except:
            return False
    
    # Define custom ranking function
    def value_rank(stock):
        """Rank by value metrics."""
        try:
            # Higher score = better value
            return stock.ratios.roe / stock.ratios.pe if stock.ratios.pe > 0 else 0
        except:
            return 0
    
    # Create strategy
    universe = ["AAPL", "GOOGL", "MSFT", "JPM", "BAC", "WFC"]
    
    strategy = CustomStrategy(
        filter_func=value_filter,
        rank_func=value_rank,
        universe=universe
    )
    
    print(f"\nScreening {len(universe)} stocks for value opportunities...")
    print()
    
    # Run strategy
    results = strategy.run(limit=5)
    
    print(f"{'Rank':<6} {'Ticker':<10} {'Company':<30} {'Price':>10} {'Score':>10}")
    print("-" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"{i:<6} {result['ticker']:<10} {result['name'][:28]:<30} "
              f"${result['price']:>9.2f} {result['rank']:>10.4f}")
    
    print()


def example_builder_pattern():
    """Example 2: Builder pattern for common criteria."""
    print("=" * 70)
    print("Example 2: Builder Pattern Strategy")
    print("=" * 70)
    
    # Create strategy using builder pattern
    universe = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA"]
    
    strategy = (
        CustomStrategy()
        .add_filter("ratios.pe", min=10, max=30)    # P/E between 10-30
        .add_filter("ratios.roe", min=0.15)         # ROE > 15%
        .add_filter("price", min=50)                # Price > $50
        .rank_by("ratios.roe")                      # Rank by ROE
        .apply(universe=universe)
    )
    
    print(f"\nFilters:")
    print("  - P/E Ratio: 10 to 30")
    print("  - ROE: > 15%")
    print("  - Price: > $50")
    print("  - Ranked by: ROE (highest first)")
    print()
    
    results = strategy.run()
    
    if results:
        print(f"{'Rank':<6} {'Ticker':<10} {'Price':>10} {'ROE Score':>12}")
        print("-" * 40)
        
        for i, result in enumerate(results, 1):
            print(f"{i:<6} {result['ticker']:<10} ${result['price']:>9.2f} {result['rank']:>12.4f}")
    else:
        print("No stocks passed the filters.")
    
    print()


def example_growth_screening():
    """Example 3: Growth stock screening."""
    print("=" * 70)
    print("Example 3: Growth Stock Screening")
    print("=" * 70)
    
    def growth_filter(stock):
        """Filter for growth stocks."""
        try:
            return (
                stock.ratios.revenue_growth > 0.15 and  # 15%+ revenue growth
                stock.ratios.roe > 0.20 and              # 20%+ ROE
                stock.market_cap > 10_000_000_000        # $10B+ market cap
            )
        except:
            return False
    
    def growth_rank(stock):
        """Rank by growth potential."""
        try:
            # Combine revenue growth and ROE
            return stock.ratios.revenue_growth * stock.ratios.roe
        except:
            return 0
    
    universe = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    
    strategy = CustomStrategy(
        filter_func=growth_filter,
        rank_func=growth_rank,
        universe=universe
    )
    
    print(f"\nCriteria:")
    print("  - Revenue Growth > 15%")
    print("  - ROE > 20%")
    print("  - Market Cap > $10B")
    print()
    
    results = strategy.run(limit=5)
    
    if results:
        print(f"{'Rank':<6} {'Ticker':<10} {'Company':<25} {'Growth Score':>15}")
        print("-" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"{i:<6} {result['ticker']:<10} {result['name'][:23]:<25} {result['rank']:>15.4f}")
    else:
        print("No stocks passed the growth filters.")
    
    print()


def example_dividend_screening():
    """Example 4: Dividend stock screening."""
    print("=" * 70)
    print("Example 4: Dividend Stock Screening")
    print("=" * 70)
    
    def dividend_filter(stock):
        """Filter for dividend stocks."""
        try:
            return (
                stock.ratios.dividend_yield > 0.03 and  # 3%+ dividend yield
                stock.ratios.payout_ratio < 0.70 and    # < 70% payout ratio (sustainable)
                stock.ratios.pe < 25                     # Reasonable valuation
            )
        except:
            return False
    
    def dividend_rank(stock):
        """Rank by dividend attractiveness."""
        try:
            # Higher yield with lower payout ratio = better
            return stock.ratios.dividend_yield / stock.ratios.payout_ratio if stock.ratios.payout_ratio > 0 else 0
        except:
            return 0
    
    universe = ["JPM", "JNJ", "PG", "KO", "PEP", "VZ", "T", "XOM"]
    
    strategy = CustomStrategy(
        filter_func=dividend_filter,
        rank_func=dividend_rank,
        universe=universe
    )
    
    print(f"\nCriteria:")
    print("  - Dividend Yield > 3%")
    print("  - Payout Ratio < 70%")
    print("  - P/E < 25")
    print()
    
    results = strategy.run()
    
    if results:
        print(f"{'Rank':<6} {'Ticker':<10} {'Company':<25} {'Div Score':>12}")
        print("-" * 55)
        
        for i, result in enumerate(results, 1):
            print(f"{i:<6} {result['ticker']:<10} {result['name'][:23]:<25} {result['rank']:>12.4f}")
    else:
        print("No stocks passed the dividend filters.")
    
    print()


def example_multi_criteria():
    """Example 5: Multiple criteria ranking."""
    print("=" * 70)
    print("Example 5: Quality Stocks (Multiple Criteria)")
    print("=" * 70)
    
    def quality_filter(stock):
        """Filter for quality stocks."""
        try:
            return (
                stock.ratios.roe > 0.15 and           # Strong ROE
                stock.ratios.current_ratio > 1.5 and  # Good liquidity
                stock.ratios.debt_to_equity < 0.5     # Low debt
            )
        except:
            return False
    
    def quality_rank(stock):
        """Rank by overall quality."""
        try:
            # Composite score: ROE + current ratio - debt ratio
            return (
                stock.ratios.roe + 
                (stock.ratios.current_ratio / 10) -  # Normalize
                (stock.ratios.debt_to_equity / 2)    # Penalize debt
            )
        except:
            return 0
    
    universe = ["AAPL", "MSFT", "GOOGL", "JPM", "JNJ", "PG", "V", "MA"]
    
    strategy = CustomStrategy(
        filter_func=quality_filter,
        rank_func=quality_rank,
        universe=universe
    )
    
    print(f"\nQuality Criteria:")
    print("  - ROE > 15%")
    print("  - Current Ratio > 1.5")
    print("  - Debt-to-Equity < 0.5")
    print()
    
    results = strategy.run(limit=5)
    
    if results:
        print(f"{'Rank':<6} {'Ticker':<10} {'Company':<30} {'Quality Score':>15}")
        print("-" * 65)
        
        for i, result in enumerate(results, 1):
            print(f"{i:<6} {result['ticker']:<10} {result['name'][:28]:<30} {result['rank']:>15.4f}")
    else:
        print("No stocks passed the quality filters.")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("INVESTORMATE - CUSTOM SCREENING EXAMPLES")
    print("=" * 70)
    print()
    
    try:
        example_function_based()
        example_builder_pattern()
        example_growth_screening()
        example_dividend_screening()
        example_multi_criteria()
        
        print("=" * 70)
        print("All examples completed!")
        print("=" * 70)
        print("\nKey Takeaways:")
        print("  1. Function-based: Maximum flexibility for complex logic")
        print("  2. Builder pattern: Quick setup for common criteria")
        print("  3. Custom filters: Define your own investment criteria")
        print("  4. Custom ranking: Prioritize stocks by your metrics")
        print("  5. Combine multiple factors for robust screening")
        print()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Custom screening requires stock data access.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
