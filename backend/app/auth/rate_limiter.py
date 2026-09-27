"""
auth/rate_limiter.py — In-memory sliding window rate limiter.

Zero external dependencies (no Redis required for single-node deployment).
Tracks client IP / User ID request timestamps within a sliding time window.
"""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from typing import Callable

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    """

    def __init__(self) -> None:
        # key -> list of timestamps (float)
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> tuple[bool, int]:
        """
        Check if request is allowed for `key` within `window_seconds`.
        Returns (is_allowed, retry_after_seconds).
        """
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            # Filter out timestamps older than the sliding window
            timestamps = [ts for ts in self._requests[key] if ts > cutoff]
            self._requests[key] = timestamps

            if len(timestamps) >= max_requests:
                # Calculate remaining time until oldest request expires
                oldest_in_window = timestamps[0]
                retry_after = int(max(1, oldest_in_window + window_seconds - now))
                return False, retry_after

            # Record current request
            self._requests[key].append(now)
            return True, 0

    def reset(self) -> None:
        """Reset all rate limit counters (useful for unit tests)."""
        with self._lock:
            self._requests.clear()


# Global rate limiter instance
limiter = SlidingWindowRateLimiter()


def rate_limit(max_requests: int, window_seconds: int = 60, key_prefix: str = "global") -> Callable:
    """
    FastAPI dependency factory for endpoint rate limiting.
    Usage:
        @router.post("/analyze", dependencies=[Depends(rate_limit(max_requests=20, window_seconds=60, key_prefix="analyze"))])
    """
    async def dependency(request: Request) -> None:
        # Identify client by X-Forwarded-For or client IP
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client and request.client.host:
            client_ip = request.client.host
        else:
            client_ip = "127.0.0.1"

        rate_key = f"{key_prefix}:{client_ip}"

        allowed, retry_after = limiter.is_allowed(rate_key, max_requests=max_requests, window_seconds=window_seconds)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds}s allowed.",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency
