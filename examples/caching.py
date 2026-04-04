"""
TTL cache and rate limiting for yfinance fetchers.

Repeated calls for the same ticker/data reuse cached results until TTL expires.
Use ``Stock.refresh()`` to force a refetch for one symbol.

Requires network access for live demo.
"""

import time

from investormate import Stock
from investormate.data.cache import configure_data_cache


def main():
    configure_data_cache(calls_per_second=5.0)
    stock = Stock("AAPL")

    t0 = time.perf_counter()
    _ = stock.info
    t1 = time.perf_counter()
    _ = stock.info  # cache hit (same process, within TTL)
    t2 = time.perf_counter()

    print(f"First info fetch:  {(t1 - t0) * 1000:.1f} ms")
    print(f"Second info fetch: {(t2 - t1) * 1000:.1f} ms (usually faster — cache)")

    stock.refresh()
    print("Called stock.refresh() — next access refetches from Yahoo.")


if __name__ == "__main__":
    main()
