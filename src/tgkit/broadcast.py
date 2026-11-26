"""Broadcast helper that respects Telegram's flood limits.

Rules of thumb from https://core.telegram.org/bots/faq#broadcasting-to-users:
about 30 messages per second overall, and avoid more than one message per second in a single chat.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field

from telegram.error import Forbidden, RetryAfter

from .retry import retry_after_seconds


@dataclass
class BroadcastResult:
    sent: int = 0
    blocked: list[int] = field(default_factory=list)
    failed: dict[int, str] = field(default_factory=dict)


async def broadcast(
    chat_ids: Iterable[int],
    send: Callable[[int], Awaitable[object]],
    *,
    rate_per_second: float = 25.0,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> BroadcastResult:
    """Send to each chat, pacing calls and honouring ``RetryAfter``.

    ``Forbidden`` (the user blocked the bot or deleted the chat) is recorded, not retried, so the
    caller can prune the list. Keep ``rate_per_second`` below 30.
    """
    if not 0 < rate_per_second <= 30:
        raise ValueError("rate_per_second must be in (0, 30]")

    interval = 1.0 / rate_per_second
    result = BroadcastResult()
    for chat_id in chat_ids:
        try:
            await send(chat_id)
            result.sent += 1
        except Forbidden as exc:
            result.blocked.append(chat_id)
            result.failed[chat_id] = str(exc)
        except RetryAfter as exc:
            await sleep(retry_after_seconds(exc.retry_after) + 0.5)
            try:
                await send(chat_id)
                result.sent += 1
            except Exception as exc2:  # noqa: BLE001 - recorded for the caller
                result.failed[chat_id] = str(exc2)
        except Exception as exc:  # noqa: BLE001 - recorded for the caller
            result.failed[chat_id] = str(exc)
        await sleep(interval)
    return result
