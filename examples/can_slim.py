"""
Simplified CAN SLIM-style screen (growth, 52-week strength, volume, 52-week change).

Uses a small demo universe; widen for production use. Requires network (yfinance).
"""

from investormate import Screener


def main():
    universe = ["AAPL", "MSFT", "NVDA", "META", "GOOGL", "AMZN", "TSLA", "NFLX"]
    screener = Screener(universe=universe)
    picks = screener.can_slim(top_n=5, min_score=3)
    print("CAN SLIM-style picks (demo universe):")
    for i, t in enumerate(picks, 1):
        print(f"  {i}. {t}")


if __name__ == "__main__":
    main()
