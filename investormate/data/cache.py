"""
In-memory TTL cache and rate limiting for yfinance-backed fetchers.

Reduces duplicate API calls and spaces requests to avoid hammering Yahoo Finance.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")

# Default TTLs (seconds) per data category
TTL_INFO = 60
TTL_HISTORY = 60
TTL_FINANCIALS = 3600
TTL_NEWS = 300
TTL_FILINGS = 3600
TTL_EARNINGS = 3600
TTL_MARKET = 300

# Default maximum number of entries before LRU eviction kicks in. Bounds memory
# growth for long-running processes (e.g. screening thousands of tickers).
DEFAULT_MAX_SIZE = 2048


class TTLCache:
    """
    Thread-safe TTL cache with bounded size and LRU eviction.

    Entries expire after their TTL. When the number of live entries exceeds
    ``maxsize``, the least-recently-used entries are evicted. A ``maxsize`` of
    ``0`` (or negative) disables the size bound entirely.
    """

    def __init__(self, default_ttl: int = 300, maxsize: int = DEFAULT_MAX_SIZE):
        self.default_ttl = default_ttl
        self.maxsize = maxsize
        self._store: "OrderedDict[str, tuple[float, Any]]" = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        now = time.monotonic()
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            expires_at, value = item
            if now >= expires_at:
                del self._store[key]
                return None
            # Mark as most-recently-used.
            self._store.move_to_end(key)
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        seconds = ttl if ttl is not None else self.default_ttl
        expires_at = time.monotonic() + max(0.0, float(seconds))
        with self._lock:
            self._store[key] = (expires_at, value)
            self._store.move_to_end(key)
            self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        """Evict least-recently-used entries while over capacity. Caller holds lock."""
        if self.maxsize and self.maxsize > 0:
            while len(self._store) > self.maxsize:
                self._store.popitem(last=False)

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        """Remove all keys that start with ``prefix + ':'`` or equal ``prefix``."""
        with self._lock:
            to_del = [
                k for k in self._store if k == prefix or k.startswith(prefix + ":")
            ]
            for k in to_del:
                del self._store[k]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)


class RateLimiter:
    """
    Token-bucket rate limiter: ``rate`` tokens replenished per second (default 2/sec).
    Set ``rate`` to 0 or a very large number to effectively disable spacing.
    """

    def __init__(self, rate: float = 2.0, capacity: float = 1.0):
        self.rate = max(0.0, float(rate))
        self.capacity = max(0.0, float(capacity))
        self._tokens = self.capacity
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, cost: float = 1.0) -> None:
        if self.rate <= 0:
            return
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            self._last = now
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            if self._tokens < cost:
                need = cost - self._tokens
                sleep_s = need / self.rate if self.rate > 0 else 0.0
                if sleep_s > 0:
                    time.sleep(sleep_s)
                self._tokens = 0.0
                self._last = time.monotonic()
            else:
                self._tokens -= cost


# Module-level singletons (configurable)
_data_cache = TTLCache(default_ttl=300)
_rate_limiter = RateLimiter(rate=2.0, capacity=1.0)
_cache_enabled = True


def get_data_cache() -> TTLCache:
    """Return the process-wide data cache (for tests and ``Stock.refresh``)."""
    return _data_cache


def get_rate_limiter() -> RateLimiter:
    return _rate_limiter


def configure_data_cache(
    *,
    enabled: Optional[bool] = None,
    default_ttl: Optional[int] = None,
    calls_per_second: Optional[float] = None,
    maxsize: Optional[int] = None,
) -> None:
    """
    Configure global fetch cache and rate limiter.

    Args:
        enabled: If False, ``cached_yfinance_call`` skips cache read/write (still rate-limits).
        default_ttl: Default TTL for :class:`TTLCache` (new entries only).
        calls_per_second: Token bucket refill rate; use 0 or a huge value to disable spacing.
        maxsize: Maximum number of cached entries before LRU eviction. Use 0 to
            disable the size bound.
    """
    global _cache_enabled, _data_cache, _rate_limiter
    if enabled is not None:
        _cache_enabled = bool(enabled)
    if default_ttl is not None:
        _data_cache.default_ttl = int(default_ttl)
    if maxsize is not None:
        _data_cache.maxsize = int(maxsize)
        with _data_cache._lock:
            _data_cache._evict_if_needed()
    if calls_per_second is not None:
        r = float(calls_per_second)
        _rate_limiter = RateLimiter(rate=r, capacity=1.0)


def cached_yfinance_call(key: str, ttl: int, fetcher: Callable[[], T]) -> T:
    """
    Rate-limit, then return cached value for ``key`` if valid, else ``fetcher()`` result.
    """
    _rate_limiter.acquire(1.0)
    if _cache_enabled:
        hit = _data_cache.get(key)
        if hit is not None:
            return hit
    value = fetcher()
    if _cache_enabled:
        _data_cache.set(key, value, ttl=ttl)
    return value


def invalidate_ticker_cache(fmt_ticker: str) -> None:
    """Drop all cached entries whose key is ``fmt_ticker`` or starts with ``fmt_ticker:``."""
    _data_cache.invalidate_prefix(fmt_ticker)
