"""Tests for TTLCache size bounding and LRU eviction."""

import time

from investormate.data.cache import TTLCache, configure_data_cache, get_data_cache


def test_maxsize_evicts_oldest():
    cache = TTLCache(default_ttl=60, maxsize=3)
    for i in range(5):
        cache.set(f"k{i}", i)
    # Only the 3 most-recent keys survive
    assert len(cache) == 3
    assert cache.get("k0") is None
    assert cache.get("k1") is None
    assert cache.get("k2") == 2
    assert cache.get("k4") == 4


def test_lru_get_refreshes_recency():
    cache = TTLCache(default_ttl=60, maxsize=3)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    # Touch "a" so it becomes most-recently-used
    assert cache.get("a") == 1
    # Inserting a 4th key should now evict "b" (the LRU), not "a"
    cache.set("d", 4)
    assert cache.get("a") == 1
    assert cache.get("b") is None
    assert cache.get("d") == 4


def test_maxsize_zero_disables_bound():
    cache = TTLCache(default_ttl=60, maxsize=0)
    for i in range(50):
        cache.set(f"k{i}", i)
    assert len(cache) == 50


def test_ttl_expiry_still_works():
    cache = TTLCache(default_ttl=60, maxsize=10)
    cache.set("x", 1, ttl=0)
    time.sleep(0.01)
    assert cache.get("x") is None


def test_configure_shrinks_existing_cache():
    cache = get_data_cache()
    cache.clear()
    original = cache.maxsize
    try:
        for i in range(10):
            cache.set(f"m{i}", i)
        configure_data_cache(maxsize=4)
        assert len(cache) == 4
    finally:
        configure_data_cache(maxsize=original)
        cache.clear()
