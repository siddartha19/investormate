"""TVM basics example. Run: python examples/tvm_basics.py"""

from investormate import (
    present_value,
    future_value,
    annuity_pv,
    npv,
    irr,
    amortization_schedule,
    ear,
)


def main():
    print("=== Present / Future Value ===")
    print(f"PV of $1,000 in 10y @ 5%: ${present_value(1000, 0.05, 10):,.2f}")
    print(f"FV of $500 in 5y @ 8%: ${future_value(500, 0.08, 5):,.2f}")

    print("\n=== Annuity ===")
    print(f"PV of $100/yr for 20y @ 8%: ${annuity_pv(100, 0.08, 20):,.2f}")

    print("\n=== NPV / IRR ===")
    cfs = [-1000, 300, 400, 500]
    print(f"NPV @ 10%: ${npv(0.10, cfs):,.2f}")
    print(f"IRR: {irr(cfs)*100:.2f}%")

    print("\n=== Amortization (first 3 rows) ===")
    print(amortization_schedule(100000, 0.04, 30).head(3))

    print(f"\nEAR of 8% compounded monthly: {ear(0.08, 12)*100:.2f}%")


if __name__ == "__main__":
    main()
