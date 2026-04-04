"""
Earnings calendar, consensus estimates, and EPS surprise history.

Requires network access (yfinance).
"""

from investormate import Stock


def main():
    stock = Stock("AAPL")
    ear = stock.earnings

    print("Calendar / next earnings fields:")
    print(ear.calendar())

    print("\nConsensus estimate tables (earnings + revenue):")
    print(ear.estimates())

    print("\nHistorical EPS vs estimate (sample):")
    for row in ear.surprise_history()[-5:]:
        print(row)

    t = ear.eps_trend()
    if t:
        print("\nEPS trend:", t)


if __name__ == "__main__":
    main()
