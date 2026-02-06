"""
Valuation example: DCF, comparable companies, and fair value summary.

Run: python examples/valuation.py
"""

from investormate import Stock


def main():
    stock = Stock("AAPL")

    # DCF (Discounted Cash Flow) with terminal value
    print("=== DCF Valuation ===")
    dcf = stock.valuation.dcf(growth_rate=0.05, terminal_growth=0.02, years=5)
    if dcf.get("fair_value_per_share"):
        print(f"Fair value per share: ${dcf['fair_value_per_share']:.2f}")
        print(f"Enterprise value: ${dcf['enterprise_value']:,.0f}")
        print(f"WACC used: {dcf['wacc_used']*100:.1f}%")
        print(f"FCF projection (next 5 years): {dcf['fcf_series']}")
    else:
        print("DCF not available (missing FCF or shares data).")

    # Comparable companies (peer multiples)
    print("\n=== Comparable Companies ===")
    peers = ["MSFT", "GOOGL", "META"]
    comps = stock.valuation.comps(peers=peers)
    if comps.get("median_pe") is not None:
        print(f"Peers: {peers}")
        print(f"Median P/E: {comps['median_pe']:.1f}")
        print(f"Median EV/EBITDA: {comps['median_ev_ebitda']}")
        print(f"Median P/S: {comps['median_ps']}")
        print(f"Implied value (P/E): ${comps.get('implied_value_pe')}")
        print(f"Implied value (EV/EBITDA): ${comps.get('implied_value_ev_ebitda')}")
        print(f"Implied value (P/S): ${comps.get('implied_value_ps')}")
        print(f"Current price: ${comps.get('current_price')}")
    else:
        print("Comps: provide peers, e.g. comps(peers=['MSFT','GOOGL'])")

    # Fair value summary (DCF + comps)
    print("\n=== Fair Value Summary ===")
    summary = stock.valuation.summary(peers=peers)
    print(f"Current price: ${summary.get('current_price')}")
    print(f"Fair value range: ${summary.get('fair_value_low')} - ${summary.get('fair_value_high')}")
    print(f"Recommendation: {summary.get('recommendation')}")

    # Sensitivity table (growth vs WACC)
    print("\n=== DCF Sensitivity (growth vs WACC) ===")
    sens = stock.valuation.sensitivity(
        growth_rates=[0.03, 0.05, 0.07],
        wacc_rates=[0.08, 0.10, 0.12],
    )
    for g, row in sens["table"].items():
        print(f"  Growth {g*100:.0f}%: {row}")
    print(f"  Current price: ${sens.get('current_price')}")
    print(f"  Min/Max from table: ${sens.get('min_value')} / ${sens.get('max_value')}")


if __name__ == "__main__":
    main()
