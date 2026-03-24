"""
Magic Formula screen (Joel Greenblatt): high ROIC + high earnings yield (EBIT/EV).

Uses a custom universe for a quick demo; widen the list for real use.
"""

from investormate import Screener


def main():
    universe = ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "JPM", "XOM", "KO", "PFE", "WMT"]
    screener = Screener(universe=universe)
    picks = screener.magic_formula(top_n=5, min_market_cap=50_000_000_000)
    print("Magic Formula top picks (demo universe):")
    for i, t in enumerate(picks, 1):
        print(f"  {i}. {t}")


if __name__ == "__main__":
    main()
