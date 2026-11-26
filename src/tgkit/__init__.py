"""Small, tested helpers used by the handbook examples.

Everything here is deliberately dependency-light so it can be copied into a real bot.
"""

from __future__ import annotations

from .callback_data import CallbackDataTooLong, pack_callback, unpack_callback
from .idempotency import MemoryUpdateStore, SQLiteUpdateStore
from .initdata import InitDataError, validate_init_data, validate_init_data_ed25519
from .retry import call_with_retry
from .text import split_message

__all__ = [
    "CallbackDataTooLong",
    "InitDataError",
    "MemoryUpdateStore",
    "SQLiteUpdateStore",
    "call_with_retry",
    "pack_callback",
    "split_message",
    "unpack_callback",
    "validate_init_data",
    "validate_init_data_ed25519",
]
