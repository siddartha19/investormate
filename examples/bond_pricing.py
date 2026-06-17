"""Bond pricing example. Run: python examples/bond_pricing.py"""

from investormate import Bond, bond_ladder


def main():
    b = Bond(face=1000, coupon=0.06, ytm=0.05, n=10, frequency=2)
    price = b.price()
    print(f"Price: ${price:.2f}")
    print(f"Modified duration: {b.modified_duration():.2f}")
    print(f"Convexity: {b.convexity():.2f}")

    solved = Bond(face=1000, coupon=0.06, n=10, frequency=2, price=price).solve_ytm()
    print(f"Solved YTM: {solved*100:.2f}%")

    print("\n=== Bond Ladder ===")
    for row in bond_ladder([1, 3, 5, 7, 10]):
        print(row)


if __name__ == "__main__":
    main()
