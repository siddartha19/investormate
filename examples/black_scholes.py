"""Black-Scholes example. Run: python examples/black_scholes.py"""

from investormate.finance import options


def main():
    S, K, T, r, sigma = 150, 155, 0.5, 0.05, 0.25
    call = options.black_scholes(S, K, T, r, sigma, "call")
    put = options.black_scholes(S, K, T, r, sigma, "put")
    print(f"Call: ${call:.2f}, Put: ${put:.2f}")

    g = options.greeks(S, K, T, r, sigma, "call")
    print(f"Delta: {g['delta']:.4f}, Gamma: {g['gamma']:.4f}")

    parity = options.put_call_parity(call, put, S, K, r, T)
    print(f"Put-call parity holds: {parity['holds']}")


if __name__ == "__main__":
    main()
