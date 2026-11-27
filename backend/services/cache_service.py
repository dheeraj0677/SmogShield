"""Lightweight thread-safe in-memory LRU + TTL cache with SHA-256 key hashing."""

import hashlib
import json
import threading
import time
from collections import OrderedDict
from typing import Any


class TTLCache:
    """Bounded LRU + TTL cache with optional SHA-256 key hashing for PII-free lookups."""

    def __init__(self, ttl_seconds: int = 900, max_entries: int = 256) -> None:
        self._ttl_seconds = max(1, ttl_seconds)
        self._max_entries = max(1, max_entries)
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    @staticmethod
    def hash_key(namespace: str, payload: Any) -> str:
        """Return a deterministic SHA-256 key avoiding raw user text in cache maps."""
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(f"{namespace}:{serialized}".encode("utf-8")).hexdigest()
        return f"{namespace}:{digest}"

    def get(self, key: str) -> Any | None:
        """Return cached value if present and unexpired, else None."""
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self.misses += 1
                return None

            expires_at, value = entry
            if now >= expires_at:
                del self._store[key]
                self.misses += 1
                return None

            self._store.move_to_end(key)
            self.hits += 1
            return value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Store a value with expiration and evict oldest entry if at capacity."""
        ttl = self._ttl_seconds if ttl_seconds is None else max(1, ttl_seconds)
        expires_at = time.monotonic() + ttl
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (expires_at, value)
            while len(self._store) > self._max_entries:
                self._store.popitem(last=False)

    def clear(self) -> None:
        """Clear all entries and reset hit/miss counters."""
        with self._lock:
            self._store.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> dict[str, float | int]:
        """Return current entry count and hit ratio metrics."""
        with self._lock:
            total = self.hits + self.misses
            hit_rate = round((self.hits / total) * 100, 1) if total > 0 else 0.0
            return {
                "size": len(self._store),
                "max_entries": self._max_entries,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate_pct": hit_rate,
            }

    @property
    def size(self) -> int:
        """Current number of cached items (including unexpired entries)."""
        with self._lock:
            return len(self._store)
