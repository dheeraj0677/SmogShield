"""Tests for TTLCache expiration, LRU eviction, clear, and stats."""

import time

from services.cache_service import TTLCache


def test_ttl_cache_expiry_and_stats(monkeypatch):
    now = [100.0]
    monkeypatch.setattr(time, "monotonic", lambda: now[0])

    cache = TTLCache(ttl_seconds=10, max_entries=2)
    cache.set("k1", "v1")
    assert cache.get("k1") == "v1"
    assert cache.size == 1

    now[0] += 15.0
    assert cache.get("k1") is None
    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate_pct"] == 50.0


def test_ttl_cache_eviction_and_clear():
    cache = TTLCache(ttl_seconds=60, max_entries=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("a", 10)  # promote "a"
    cache.set("c", 3)   # evicts "b"

    assert cache.get("b") is None
    assert cache.get("a") == 10
    assert cache.get("c") == 3

    cache.clear()
    assert cache.size == 0
    assert cache.stats()["hits"] == 0
