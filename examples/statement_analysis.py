"""Financial statement analysis example. Run: python examples/statement_analysis.py"""

from investormate import Stock


def main():
    stock = Stock("AAPL")
    cs = stock.financials.common_size("income")
    if cs:
        latest = list(cs.keys())[0]
        print(f"Common-size income ({latest}):")
        for k, v in list(cs[latest].items())[:5]:
            print(f"  {k}: {v*100:.1f}%")

    quality = stock.financials.cash_flow_quality()
    print(f"\nCash flow quality: {quality.get('assessment')}")

    dupont = stock.ratios.dupont_breakdown()
    print(f"\nDuPont: {dupont.get('tree')}")


if __name__ == "__main__":
    main()
