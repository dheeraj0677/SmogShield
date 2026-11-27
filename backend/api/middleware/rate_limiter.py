"""Sliding-window in-memory rate limiting middleware for API endpoints."""

import threading
import time
from collections import defaultdict, deque

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class SlidingWindowRateLimiter:
    """Thread-safe per-client sliding-window request limiter."""

    def __init__(self, window_seconds: int = 60) -> None:
        self._window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, max_requests: int) -> tuple[bool, int, int]:
        """Check whether a request is allowed; returns (allowed, remaining, retry_after_s)."""
        now = time.monotonic()
        cutoff = now - self._window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= max_requests:
                retry_after = max(1, int(round(self._window_seconds - (now - bucket[0]))))
                return False, 0, retry_after

            bucket.append(now)
            remaining = max(0, max_requests - len(bucket))
            return True, remaining, 0

    def reset(self) -> None:
        """Clear all recorded request timestamps (useful in test isolation)."""
        with self._lock:
            self._hits.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforce per-route sliding-window rate limits per client IP."""

    def __init__(
        self,
        app,
        chat_limit_per_min: int = 30,
        aqi_limit_per_min: int = 60,
        limiter: SlidingWindowRateLimiter | None = None,
    ) -> None:
        super().__init__(app)
        self.chat_limit = chat_limit_per_min
        self.aqi_limit = aqi_limit_per_min
        self.limiter = limiter or SlidingWindowRateLimiter(window_seconds=60)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path
        if not path.startswith("/api/") or path == "/api/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        if path.startswith("/api/chat"):
            limit = self.chat_limit
            bucket_key = f"chat:{client_ip}"
        else:
            limit = self.aqi_limit
            bucket_key = f"aqi:{client_ip}"

        allowed, remaining, retry_after = self.limiter.allow(bucket_key, limit)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"Rate limit exceeded. Please retry after {retry_after} seconds."
                    )
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
