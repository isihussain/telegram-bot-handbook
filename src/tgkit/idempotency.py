"""Update de-duplication.

Telegram may deliver the same update more than once (webhook retries after a timeout,
re-delivery after a restart). For anything that spends money or changes state, process an
update at most once.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path


class MemoryUpdateStore:
    """Bounded in-memory store. Good for a single process, lost on restart."""

    def __init__(self, max_items: int = 10_000, ttl_seconds: float = 24 * 3600) -> None:
        if max_items < 1:
            raise ValueError("max_items must be >= 1")
        self._max_items = max_items
        self._ttl = ttl_seconds
        self._seen: dict[int, float] = {}

    def _evict(self, now: float) -> None:
        expired = [key for key, ts in self._seen.items() if now - ts > self._ttl]
        for key in expired:
            del self._seen[key]
        while len(self._seen) >= self._max_items:
            oldest = min(self._seen, key=self._seen.__getitem__)
            del self._seen[oldest]

    def claim(self, update_id: int, *, now: float | None = None) -> bool:
        """Return True the first time an update id is seen."""
        current = time.monotonic() if now is None else now
        if update_id in self._seen and current - self._seen[update_id] <= self._ttl:
            return False
        self._evict(current)
        self._seen[update_id] = current
        return True


class SQLiteUpdateStore:
    """Durable store shared by several workers.

    ``claim`` uses ``INSERT OR IGNORE`` and checks ``rowcount``, so exactly one worker wins
    the race for a given update id.
    """

    def __init__(self, path: str | Path, ttl_seconds: float = 7 * 24 * 3600) -> None:
        self._path = str(path)
        self._ttl = ttl_seconds
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS processed_updates ("
                " update_id INTEGER PRIMARY KEY,"
                " processed_at REAL NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def claim(self, update_id: int, *, now: float | None = None) -> bool:
        current = time.time() if now is None else now
        with self._connect() as conn:
            # A stale row must not block a re-delivered update, so drop it first.
            conn.execute(
                "DELETE FROM processed_updates WHERE update_id = ? AND processed_at < ?",
                (update_id, current - self._ttl),
            )
            cursor = conn.execute(
                "INSERT OR IGNORE INTO processed_updates (update_id, processed_at) VALUES (?, ?)",
                (update_id, current),
            )
            return cursor.rowcount == 1

    def prune(self, *, now: float | None = None) -> int:
        current = time.time() if now is None else now
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM processed_updates WHERE processed_at < ?", (current - self._ttl,)
            )
            return cursor.rowcount
