from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tgkit.idempotency import MemoryUpdateStore, SQLiteUpdateStore


def test_memory_store_claims_once() -> None:
    store = MemoryUpdateStore()
    assert store.claim(1) is True
    assert store.claim(1) is False
    assert store.claim(2) is True


def test_memory_store_evicts_when_full() -> None:
    store = MemoryUpdateStore(max_items=2, ttl_seconds=10_000)
    assert store.claim(1, now=0) is True
    assert store.claim(2, now=1) is True
    assert store.claim(3, now=2) is True
    # 1 was the oldest and is gone, so it can be claimed again
    assert store.claim(1, now=3) is True


def test_memory_store_expires_entries() -> None:
    store = MemoryUpdateStore(ttl_seconds=10)
    assert store.claim(7, now=100) is True
    assert store.claim(7, now=105) is False
    assert store.claim(7, now=111) is True


def test_sqlite_store_claims_once(tmp_path: Path) -> None:
    store = SQLiteUpdateStore(tmp_path / "updates.db")
    assert store.claim(10) is True
    assert store.claim(10) is False


def test_sqlite_store_survives_restart(tmp_path: Path) -> None:
    path = tmp_path / "updates.db"
    assert SQLiteUpdateStore(path).claim(11) is True
    assert SQLiteUpdateStore(path).claim(11) is False


def test_sqlite_prune_removes_old_rows(tmp_path: Path) -> None:
    store = SQLiteUpdateStore(tmp_path / "updates.db", ttl_seconds=10)
    store.claim(1, now=100)
    store.claim(2, now=200)
    # ttl=10: at t=205 row 1 (t=100) is stale, row 2 (t=200) is still fresh.
    assert store.prune(now=205) == 1
    assert store.claim(1, now=205) is True


def test_sqlite_concurrent_claim_has_one_winner(tmp_path: Path) -> None:
    path = tmp_path / "updates.db"
    first = SQLiteUpdateStore(path)
    second = SQLiteUpdateStore(path)
    assert first.claim(99) is True
    assert second.claim(99) is False
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM processed_updates").fetchone()[0] == 1


def test_memory_store_rejects_bad_size() -> None:
    with pytest.raises(ValueError):
        MemoryUpdateStore(max_items=0)
