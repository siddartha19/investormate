"""Educational layer example. Run: python examples/explain_ratios.py"""

from investormate import Stock, practice_generate


def main():
    stock = Stock("AAPL")

    print(stock.ratios.explain("roe"))
    print("\n--- show_work ---")
    print(stock.ratios.show_work("current_ratio"))

    print("\n--- red flags ---")
    for flag in stock.ratios.red_flags():
        print(f"  - {flag}")

    print("\n--- practice problem ---")
    p = practice_generate("tvm", "easy", seed=7)
    print(p["question"])
    print(f"Answer: {p['answer']}")


if __name__ == "__main__":
    main()
