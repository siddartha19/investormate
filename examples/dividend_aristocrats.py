"""
Dividend growth streak screen (approximation — not official S&P Aristocrats index).

Requires network (yfinance). Uses a small universe for demo.
"""

from investormate import Screener


def main():
    universe = ["JNJ", "KO", "PG", "WMT", "PEP", "MCD", "ABBV", "T", "VZ", "XOM"]
    screener = Screener(universe=universe)
    picks = screener.dividend_aristocrats(min_years=10, min_yield=2.0, top_n=10)
    print("Names with long dividend-growth streaks (demo, min 10y, yield >= 2%):")
    for i, t in enumerate(picks, 1):
        print(f"  {i}. {t}")


if __name__ == "__main__":
    main()
