"""
Example: Multi-Stock Correlation Analysis

This example demonstrates how to use the Correlation class to:
1. Calculate correlation matrices for portfolio diversification
2. Find highly correlated stock pairs
3. Identify diversification candidates
4. Analyze portfolio risk through correlation

Perfect for building diversified portfolios and understanding stock relationships.
"""

from investormate import Correlation


def example_basic_correlation():
    """Example 1: Basic correlation matrix."""
    print("=" * 60)
    print("Example 1: Basic Correlation Matrix")
    print("=" * 60)
    
    # Analyze correlation between tech giants
    corr = Correlation(["AAPL", "GOOGL", "MSFT", "AMZN"], period="1y")
    
    # Get correlation matrix
    matrix = corr.matrix()
    print("\nCorrelation Matrix (Pearson):")
    print(matrix)
    print("\nNote: Values range from -1 (perfect negative) to 1 (perfect positive)")
    print()


def example_find_correlated_pairs():
    """Example 2: Find highly correlated pairs."""
    print("=" * 60)
    print("Example 2: Find Highly Correlated Stock Pairs")
    print("=" * 60)
    
    # Analyze a diverse set of stocks
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "JPM", "GLD", "TLT"]
    corr = Correlation(tickers, period="1y")
    
    # Find pairs with correlation > 0.7
    pairs = corr.find_pairs(threshold=0.7)
    
    print(f"\nAnalyzing {len(tickers)} stocks: {', '.join(tickers)}")
    print(f"\nHighly correlated pairs (>0.7):")
    
    if pairs:
        for ticker1, ticker2, correlation in pairs:
            print(f"  {ticker1} <-> {ticker2}: {correlation:.3f}")
    else:
        print("  No pairs found with correlation > 0.7")
    
    print("\nInterpretation:")
    print("  - High correlation (>0.7): Stocks move together")
    print("  - These pairs offer limited diversification benefits")
    print()


def example_diversification_candidates():
    """Example 3: Find diversification candidates."""
    print("=" * 60)
    print("Example 3: Find Diversification Candidates")
    print("=" * 60)
    
    # Current portfolio: Tech stocks
    portfolio = ["AAPL", "GOOGL", "MSFT"]
    
    # Potential additions: Mix of assets
    universe = ["GLD", "TLT", "VNQ", "BTC-USD", "JPM", "XOM"]
    
    # Combine for analysis
    all_tickers = portfolio + universe
    corr = Correlation(all_tickers, period="1y")
    
    print(f"\nCurrent Portfolio: {', '.join(portfolio)}")
    print(f"Evaluating: {', '.join(universe)}")
    
    # Find low-correlation assets (good for diversification)
    candidates = corr.find_diversification_candidates(
        portfolio=portfolio,
        universe=universe,
        max_correlation=0.4  # Want correlation < 0.4
    )
    
    print(f"\nDiversification Candidates (correlation < 0.4):")
    
    if candidates:
        for ticker, avg_corr in candidates:
            correlation_type = "negative" if avg_corr < 0 else "low positive"
            print(f"  {ticker:10} | Avg correlation: {avg_corr:6.3f} ({correlation_type})")
    else:
        print("  No candidates found with correlation < 0.4")
    
    print("\nInterpretation:")
    print("  - Lower correlation = better diversification")
    print("  - Negative correlation = moves opposite to portfolio")
    print("  - Consider adding top candidates to reduce portfolio risk")
    print()


def example_sector_correlation():
    """Example 4: Analyze sector correlations."""
    print("=" * 60)
    print("Example 4: Sector Correlation Analysis")
    print("=" * 60)
    
    # Representatives from different sectors
    sectors = {
        "Technology": ["AAPL", "GOOGL"],
        "Finance": ["JPM", "BAC"],
        "Healthcare": ["JNJ", "PFE"],
        "Energy": ["XOM", "CVX"],
    }
    
    all_tickers = [ticker for sector_tickers in sectors.values() for ticker in sector_tickers]
    corr = Correlation(all_tickers, period="1y")
    
    matrix = corr.matrix()
    
    print("\nInter-sector Correlations:")
    print("\nTech vs Finance:")
    print(f"  AAPL vs JPM: {matrix.loc['AAPL', 'JPM']:.3f}")
    print(f"  GOOGL vs BAC: {matrix.loc['GOOGL', 'BAC']:.3f}")
    
    print("\nTech vs Healthcare:")
    print(f"  AAPL vs JNJ: {matrix.loc['AAPL', 'JNJ']:.3f}")
    print(f"  GOOGL vs PFE: {matrix.loc['GOOGL', 'PFE']:.3f}")
    
    print("\nTech vs Energy:")
    print(f"  AAPL vs XOM: {matrix.loc['AAPL', 'XOM']:.3f}")
    print(f"  GOOGL vs CVX: {matrix.loc['GOOGL', 'CVX']:.3f}")
    
    print("\nInterpretation:")
    print("  - Different sectors often have lower correlation")
    print("  - Sector diversification reduces overall portfolio risk")
    print()


def example_correlation_methods():
    """Example 5: Compare correlation methods."""
    print("=" * 60)
    print("Example 5: Different Correlation Methods")
    print("=" * 60)
    
    tickers = ["AAPL", "GOOGL", "MSFT"]
    corr = Correlation(tickers, period="6mo")
    
    print("\nComparing Pearson vs Spearman correlation:")
    
    # Pearson (linear correlation)
    pearson = corr.matrix(method='pearson')
    print("\nPearson (linear relationships):")
    print(pearson)
    
    # Spearman (rank-based correlation)
    spearman = corr.matrix(method='spearman')
    print("\nSpearman (monotonic relationships):")
    print(spearman)
    
    print("\nWhen to use each:")
    print("  - Pearson: Most common, measures linear relationships")
    print("  - Spearman: Robust to outliers, measures monotonic relationships")
    print("  - Kendall: Good for small samples, measures ordinal relationships")
    print()


def example_statistics():
    """Example 6: Get correlation statistics."""
    print("=" * 60)
    print("Example 6: Correlation Statistics")
    print("=" * 60)
    
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA"]
    corr = Correlation(tickers, period="1y")
    
    stats = corr.get_statistics()
    
    print(f"\nAnalysis Summary:")
    print(f"  Tickers analyzed: {stats['ticker_count']}")
    print(f"  Tickers: {', '.join(stats['tickers'])}")
    print(f"  Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    print(f"  Data points: {stats['data_points']} days")
    
    print(f"\nCorrelation Metrics:")
    print(f"  Average correlation: {stats['avg_correlation']:.3f}")
    
    if stats['max_correlation']:
        t1, t2, corr_val = stats['max_correlation']
        print(f"  Highest correlation: {t1} <-> {t2} = {corr_val:.3f}")
    
    if stats['min_correlation']:
        t1, t2, corr_val = stats['min_correlation']
        print(f"  Lowest correlation: {t1} <-> {t2} = {corr_val:.3f}")
    
    print()


def example_portfolio_risk_assessment():
    """Example 7: Assess portfolio diversification."""
    print("=" * 60)
    print("Example 7: Portfolio Risk Assessment")
    print("=" * 60)
    
    # Portfolio A: All tech stocks (high correlation expected)
    portfolio_a = ["AAPL", "GOOGL", "MSFT", "AMZN"]
    corr_a = Correlation(portfolio_a, period="1y")
    
    # Portfolio B: Diversified across asset classes
    portfolio_b = ["AAPL", "GLD", "TLT", "VNQ"]
    corr_b = Correlation(portfolio_b, period="1y")
    
    stats_a = corr_a.get_statistics()
    stats_b = corr_b.get_statistics()
    
    print("\nPortfolio A (All Tech):")
    print(f"  Stocks: {', '.join(portfolio_a)}")
    print(f"  Average correlation: {stats_a['avg_correlation']:.3f}")
    
    print("\nPortfolio B (Diversified):")
    print(f"  Assets: {', '.join(portfolio_b)}")
    print(f"  Average correlation: {stats_b['avg_correlation']:.3f}")
    
    print("\nRisk Assessment:")
    if stats_a['avg_correlation'] > stats_b['avg_correlation']:
        print(f"  ⚠️  Portfolio A has higher correlation ({stats_a['avg_correlation']:.3f})")
        print("     → Higher risk: stocks move together")
        print(f"  ✓  Portfolio B has lower correlation ({stats_b['avg_correlation']:.3f})")
        print("     → Better diversification: more independent movements")
    else:
        print("  Correlation levels are similar")
    
    print("\nRecommendation:")
    print("  - Target average correlation < 0.5 for good diversification")
    print("  - Mix different sectors and asset classes")
    print("  - Include negatively correlated assets for hedging")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("INVESTORMATE - CORRELATION ANALYSIS EXAMPLES")
    print("=" * 60)
    print()
    
    try:
        example_basic_correlation()
        example_find_correlated_pairs()
        example_diversification_candidates()
        example_sector_correlation()
        example_correlation_methods()
        example_statistics()
        example_portfolio_risk_assessment()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print("\nKey Takeaways:")
        print("  1. Use correlation to identify diversification opportunities")
        print("  2. Target low correlation (<0.5) between portfolio holdings")
        print("  3. Different sectors typically have lower correlation")
        print("  4. Alternative assets (gold, bonds) often hedge equity risk")
        print("  5. Monitor correlation over time - it changes!")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Note: Make sure you have internet connection for live data")
        print()


if __name__ == "__main__":
    main()
