"""Retry helper for Telegram API calls.

Telegram signals rate limiting with HTTP 429 and ``parameters.retry_after``. python-telegram-bot
raises :class:`telegram.error.RetryAfter` for it. Honour the value instead of guessing, and do not
retry errors that will never succeed (bad request, forbidden, invalid token).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import TypeVar

from telegram.error import BadRequest, Forbidden, InvalidToken, NetworkError, RetryAfter, TimedOut

T = TypeVar("T")

NON_RETRYABLE = (BadRequest, Forbidden, InvalidToken)
RETRYABLE = (RetryAfter, TimedOut, NetworkError)


def retry_after_seconds(value: int | float | timedelta) -> float:
    """Return ``RetryAfter.retry_after`` in seconds.

    python-telegram-bot returns an ``int`` today and a ``datetime.timedelta`` when
    ``PTB_TIMEDELTA=1`` is set (and in a future major version), so handle both.
    """
    total_seconds = getattr(value, "total_seconds", None)
    return float(total_seconds()) if total_seconds is not None else float(value)


async def call_with_retry(
    func: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Call ``func`` until it succeeds, backing off exponentially.

    ``RetryAfter.retry_after`` always wins over the computed backoff. A non-retryable
    :class:`telegram.error.TelegramError` is re-raised immediately.

    Warning: retrying a *send* after a timeout can duplicate the message. Use this for idempotent
    calls (edits, getters) or de-duplicate with :mod:`tgkit.idempotency`.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except NON_RETRYABLE:
            raise
        except RetryAfter as exc:
            last_error = exc
            delay = retry_after_seconds(exc.retry_after) + 0.5
        except RETRYABLE as exc:
            last_error = exc
            delay = min(max_delay, base_delay * 2 ** (attempt - 1))
        if attempt == max_attempts:
            break
        await sleep(delay)

    assert last_error is not None
    raise last_error
