"""
Peer comparison: auto-detect sector peers and compare key metrics.

Uses MAJOR_US_TICKERS for peer discovery; requires network (yfinance).
"""

from investormate import Stock


def main():
    stock = Stock("AAPL")
    print(f"Analyzing {stock.ticker} ({stock.name}) — sector: {stock.sector}")
    peers = stock.peers
    print(f"Detected peers (sample universe): {peers[:8]}")

    comparison = stock.compare_with(peers=peers[:5] if peers else [])
    print("\nMetrics snapshot:")
    for ticker, row in comparison["metrics"].items():
        print(
            f"  {ticker}: P/E={row.get('pe')}, P/B={row.get('pb')}, "
            f"ROE={row.get('roe')}, rev growth={row.get('revenue_growth')}"
        )


if __name__ == "__main__":
    main()
