"""Lightweight thread-safe in-memory TTL cache with bounded capacity."""

import threading
import time
from collections import OrderedDict
from typing import Any


class TTLCache:
    """Bounded LRU + TTL cache to avoid repeated external AQI and weather calls."""

    def __init__(self, ttl_seconds: int = 900, max_entries: int = 256) -> None:
        self._ttl_seconds = max(1, ttl_seconds)
        self._max_entries = max(1, max_entries)
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

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

    @property
    def size(self) -> int:
        """Current number of cached items (including unexpired entries)."""
        with self._lock:
            return len(self._store)
