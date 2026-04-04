"""Tests for TTL cache, rate limiter, and cached_yfinance_call."""

from unittest.mock import patch

from investormate.data import cache as cache_mod


def test_ttl_cache_get_set():
    c = cache_mod.TTLCache(default_ttl=60)
    assert c.get("a") is None
    c.set("a", 1, ttl=3600)
    assert c.get("a") == 1


def test_ttl_cache_expiry():
    c = cache_mod.TTLCache(default_ttl=1)
    c.set("x", 42, ttl=0)
    # zero ttl: expires immediately on next get
    assert c.get("x") is None


def test_ttl_cache_invalidate_prefix():
    c = cache_mod.TTLCache()
    c.set("AAPL:info", {"k": 1}, ttl=60)
    c.set("AAPL:news", [], ttl=60)
    c.set("MSFT:info", {"k": 2}, ttl=60)
    c.invalidate_prefix("AAPL")
    assert c.get("AAPL:info") is None
    assert c.get("AAPL:news") is None
    assert c.get("MSFT:info") == {"k": 2}


def test_cached_yfinance_call_uses_cache():
    calls = {"n": 0}

    def fetcher():
        calls["n"] += 1
        return {"ok": True}

    cache_mod.configure_data_cache(enabled=True, calls_per_second=1_000_000)
    cache_mod.get_data_cache().clear()

    k = "TEST:info"
    v1 = cache_mod.cached_yfinance_call(k, 300, fetcher)
    v2 = cache_mod.cached_yfinance_call(k, 300, fetcher)
    assert v1 == v2
    assert calls["n"] == 1


def test_cached_yfinance_call_disabled():
    calls = {"n": 0}

    def fetcher():
        calls["n"] += 1
        return 1

    cache_mod.configure_data_cache(enabled=False, calls_per_second=1_000_000)
    cache_mod.get_data_cache().clear()

    k = "TEST:disabled"
    cache_mod.cached_yfinance_call(k, 300, fetcher)
    cache_mod.cached_yfinance_call(k, 300, fetcher)
    assert calls["n"] == 2
    cache_mod.configure_data_cache(enabled=True)


@patch("time.sleep")
def test_rate_limiter_spacing(mock_sleep):
    rl = cache_mod.RateLimiter(rate=10.0, capacity=0.0)
    rl.acquire(1.0)
    rl.acquire(1.0)
    assert mock_sleep.called
