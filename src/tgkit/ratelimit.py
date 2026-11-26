"""Per-key token buckets for application-level rate limiting.

A token bucket allows a burst up to ``capacity`` and then refills at a steady rate.
This is a **local** limiter: it protects one process. If you run several workers, back
the limit with Redis or another shared store, otherwise each worker gets its own budget.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable, Hashable
from dataclasses import dataclass

EPSILON = 1e-9


@dataclass(slots=True)
class _Bucket:
    tokens: float
    updated: float


class TokenBucket:
    """A thread-safe token bucket with one independent bucket per key.

    Args:
        capacity: Maximum burst size, in tokens.
        refill_per_second: Tokens added per second.
        clock: Injectable clock for tests; defaults to ``time.monotonic``.

    Example:
        >>> limiter = TokenBucket(capacity=5, refill_per_second=0.5)
        >>> limiter.allow(42)
        True
    """

    def __init__(
        self,
        capacity: int,
        refill_per_second: float,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_per_second <= 0:
            raise ValueError("refill_per_second must be positive")
        self.capacity = float(capacity)
        self.refill_per_second = float(refill_per_second)
        self._clock = clock
        self._buckets: dict[Hashable, _Bucket] = {}
        self._lock = threading.Lock()

    def allow(self, key: Hashable, cost: float = 1.0) -> bool:
        """Consume ``cost`` tokens for ``key`` and return whether it was allowed."""
        self._validate_cost(cost)
        with self._lock:
            bucket = self._refill(key, self._clock())
            if bucket.tokens + EPSILON >= cost:
                bucket.tokens = max(0.0, bucket.tokens - cost)
                return True
            return False

    def retry_after(self, key: Hashable, cost: float = 1.0) -> float:
        """Return seconds until ``cost`` tokens are available for ``key``.

        Returns ``0.0`` when the request would be allowed now. Probing does not consume
        tokens and does not create a bucket for an unknown key.
        """
        self._validate_cost(cost)
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                return 0.0
            available = self._available(bucket, self._clock())
            if available + EPSILON >= cost:
                return 0.0
            return (cost - available) / self.refill_per_second

    def forget(self, key: Hashable) -> None:
        """Drop the bucket for ``key``, for example after a user is banned."""
        with self._lock:
            self._buckets.pop(key, None)

    def __len__(self) -> int:
        with self._lock:
            return len(self._buckets)

    def _refill(self, key: Hashable, now: float) -> _Bucket:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = _Bucket(self.capacity, now)
            self._buckets[key] = bucket
            return bucket
        bucket.tokens = self._available(bucket, now)
        bucket.updated = now
        return bucket

    def _available(self, bucket: _Bucket, now: float) -> float:
        elapsed = max(0.0, now - bucket.updated)
        return min(self.capacity, bucket.tokens + elapsed * self.refill_per_second)

    def _validate_cost(self, cost: float) -> None:
        if cost <= 0:
            raise ValueError("cost must be positive")
        if cost > self.capacity:
            raise ValueError("cost must not exceed capacity")
